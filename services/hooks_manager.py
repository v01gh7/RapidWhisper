"""
Hook manager for RapidWhisper processing pipeline.

Discovers hook scripts, executes them by event, and logs results.
"""

from __future__ import annotations

import copy
import logging
import importlib.util
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor

from core.config import get_config_dir
from core.config_loader import get_config_loader
from utils.logger import get_logger, get_hooks_logger, rotate_file_if_too_large
from utils.hooks_log_store import HookLogStore


DEFAULT_EVENTS = [
    "before_recording",
    "after_recording",
    "transcription_received",
    "formatting_step",
    "post_formatting_step",
    "task_completed",
]


@dataclass
class HookMeta:
    name: str
    path: Path
    handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    event: str


def build_hook_options(
    event: str,
    session_id: Optional[str] = None,
    data: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build or extend hook options payload.
    """
    payload = options if isinstance(options, dict) else {}
    payload.setdefault("event", event)
    payload.setdefault("session_id", session_id)
    payload.setdefault("timestamps", {})
    payload["timestamps"]["event_time"] = datetime.utcnow().isoformat()
    payload.setdefault("data", {})
    if data:
        payload["data"].update(data)
    payload.setdefault("hooks", [])
    payload.setdefault("errors", [])
    return payload


class HookManager:
    """
    Discovers and executes hooks by event.
    """

    def __init__(self) -> None:
        self.logger = get_logger()
        self.hooks_logger = get_hooks_logger()
        self.log_store = HookLogStore()
        self.config_loader = get_config_loader()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.hooks: Dict[str, HookMeta] = {}
        self.refresh_hooks()

    @staticmethod
    def normalize_config(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        cfg = raw if isinstance(raw, dict) else {}
        cfg.setdefault("enabled", True)
        cfg.setdefault("paths", ["config/hooks"])
        cfg.setdefault("order", {})
        cfg.setdefault("disabled", {})
        cfg.setdefault("background", {})
        log_cfg = cfg.get("log", {})
        if not isinstance(log_cfg, dict):
            log_cfg = {}
        log_cfg.setdefault("enabled", True)
        log_cfg.setdefault("max_entries", 500)
        cfg["log"] = log_cfg
        for event in DEFAULT_EVENTS:
            cfg["order"].setdefault(event, [])
            cfg["disabled"].setdefault(event, [])
            cfg["background"].setdefault(event, [])
        return cfg

    def _load_config(self) -> Dict[str, Any]:
        raw = self.config_loader.get("hooks", {})
        cfg = self.normalize_config(raw)
        self.log_store.set_max_entries(cfg["log"].get("max_entries", 500))
        self._log_enabled = cfg["log"].get("enabled", True)
        return cfg

    def _resolve_paths(self, paths: List[str]) -> List[Path]:
        resolved: List[Path] = []
        config_dir = get_config_dir()
        for p in paths:
            path = Path(p)
            if not path.is_absolute():
                path = config_dir / path
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.logger.warning(f"Failed to create hooks path {path}: {e}")
            resolved.append(path)
        return resolved

    def refresh_hooks(self) -> None:
        cfg = self._load_config()
        paths = self._resolve_paths(cfg.get("paths", []))
        discovered = self._discover_hooks(paths, max_depth=5)
        self.hooks = discovered
        self.logger.info(f"Hooks discovered: {len(self.hooks)}")

    def get_available_hooks(self, event: Optional[str] = None) -> List[str]:
        if event:
            return sorted([name for name, meta in self.hooks.items() if meta.event == event])
        return sorted(self.hooks.keys())

    def get_available_hooks_by_event(self) -> Dict[str, List[str]]:
        result: Dict[str, List[str]] = {event: [] for event in DEFAULT_EVENTS}
        for name, meta in self.hooks.items():
            if meta.event in result:
                result[meta.event].append(name)
        for event in result:
            result[event].sort()
        return result

    def get_hooks_meta(self) -> Dict[str, HookMeta]:
        return dict(self.hooks)

    def _discover_hooks(self, paths: List[Path], max_depth: int = 5) -> Dict[str, HookMeta]:
        hooks: Dict[str, HookMeta] = {}
        for base in paths:
            if not base.exists():
                continue
            for root, dirs, files in os.walk(base):
                try:
                    depth = len(Path(root).relative_to(base).parts)
                except ValueError:
                    depth = 0
                # Skip cache directories
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                if depth >= max_depth:
                    dirs[:] = []
                for filename in files:
                    if not filename.endswith(".py"):
                        continue
                    if filename.startswith("__"):
                        continue
                    path = Path(root) / filename
                    rel = path.relative_to(base).with_suffix("")
                    name = str(rel).replace("\\", "/")
                    meta = self._load_hook_meta(path, name)
                    if meta:
                        hooks[name] = meta
        return hooks

    def _load_hook_meta(self, path: Path, name: str) -> Optional[HookMeta]:
        try:
            module_name = f"hook_{abs(hash(str(path)))}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            handler = getattr(module, "hookHandler", None)
            if not callable(handler):
                return None
            event = getattr(module, "HOOK_EVENT", None)
            if not isinstance(event, str):
                self.logger.warning(f"Hook {name} missing HOOK_EVENT. Skipping.")
                return None
            event_key = event.strip()
            if event_key not in DEFAULT_EVENTS:
                self.logger.warning(f"Hook {name} has invalid HOOK_EVENT: {event_key}. Skipping.")
                return None
            return HookMeta(name=name, path=path, handler=handler, event=event_key)
        except Exception as e:
            self.logger.error(f"Failed to load hook {path}: {e}")
        return None

    def run_event(self, event: str, options: Dict[str, Any]) -> Dict[str, Any]:
        cfg = self._load_config()
        if not cfg.get("enabled", True):
            return options
        if event not in DEFAULT_EVENTS:
            return options

        available = [name for name, meta in self.hooks.items() if meta.event == event]
        order = [name for name in cfg["order"].get(event, []) if name in available]
        for name in available:
            if name not in order:
                order.append(name)

        disabled = set(cfg["disabled"].get(event, []))
        background = set(cfg["background"].get(event, []))

        for name in order:
            meta = self.hooks.get(name)
            if not meta:
                continue
            if meta.event != event:
                continue
            if name in disabled:
                continue
            if name in background:
                self._run_hook_async(event, meta, options)
                continue
            options = self._run_hook_sync(event, meta, options)
        return options

    def _run_hook_sync(self, event: str, meta: HookMeta, options: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        status = "ok"
        error_message = ""
        result = options
        try:
            result = meta.handler(options)
            if not isinstance(result, dict):
                status = "error"
                error_message = "Hook returned non-dict result"
                result = options
        except Exception as e:
            status = "error"
            error_message = str(e)
            result = options
            options.setdefault("errors", []).append(
                {"hook": meta.name, "event": event, "error": error_message}
            )
            self.logger.error(f"Hook error [{meta.name}]: {e}")
        duration_ms = int((time.time() - start_time) * 1000)
        self._log_hook_event(event, meta.name, status, duration_ms, error_message)
        result.setdefault("hooks", []).append(
            {
                "name": meta.name,
                "event": event,
                "status": status,
                "duration_ms": duration_ms,
                "background": False
            }
        )
        return result

    def _run_hook_async(self, event: str, meta: HookMeta, options: Dict[str, Any]) -> None:
        payload = copy.deepcopy(options)

        def task():
            start_time = time.time()
            status = "ok"
            error_message = ""
            try:
                result = meta.handler(payload)
                if not isinstance(result, dict):
                    status = "error"
                    error_message = "Hook returned non-dict result"
            except Exception as e:
                status = "error"
                error_message = str(e)
                self.logger.error(f"Background hook error [{meta.name}]: {e}")
            duration_ms = int((time.time() - start_time) * 1000)
            self._log_hook_event(event, meta.name, status, duration_ms, error_message, background=True)

        self.executor.submit(task)

    def _log_hook_event(
        self,
        event: str,
        hook_name: str,
        status: str,
        duration_ms: int,
        error_message: str = "",
        background: bool = False
    ) -> None:
        if getattr(self, "_log_enabled", True) is False:
            return
        entry = {
            "time": datetime.utcnow().isoformat(),
            "event": event,
            "hook": hook_name,
            "status": status,
            "duration_ms": duration_ms,
            "error": error_message,
            "background": background,
        }
        self.log_store.add_entry(entry)
        try:
            log_path = getattr(self.hooks_logger, "log_path", None)
            if log_path and Path(log_path).exists() and Path(log_path).stat().st_size > 5 * 1024 * 1024:
                handler = getattr(self.hooks_logger, "file_handler", None)
                formatter = getattr(self.hooks_logger, "file_formatter", None)
                if handler:
                    self.hooks_logger.removeHandler(handler)
                    handler.close()
                rotate_file_if_too_large(Path(log_path))
                try:
                    new_handler = logging.FileHandler(Path(log_path), encoding="utf-8")
                    new_handler.setLevel(logging.INFO)
                    if formatter:
                        new_handler.setFormatter(formatter)
                    self.hooks_logger.addHandler(new_handler)
                    self.hooks_logger.file_handler = new_handler
                except Exception:
                    pass
        except Exception:
            pass
        self.hooks_logger.info(
            f"{event} | {hook_name} | {status} | {duration_ms}ms"
            + (f" | {error_message}" if error_message else "")
        )


_hook_manager_instance: Optional[HookManager] = None


def get_hook_manager() -> HookManager:
    global _hook_manager_instance
    if _hook_manager_instance is None:
        _hook_manager_instance = HookManager()
    return _hook_manager_instance
