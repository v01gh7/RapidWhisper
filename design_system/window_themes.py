"""
Centralized window theme registry.

All themes are opaque by design and intended for instant runtime switching.
"""

from __future__ import annotations

from typing import Dict, List, TypedDict


class WindowTheme(TypedDict):
    id: str
    name_key: str
    font_family: str
    floating_bg: str
    window_bg: str
    window_border: str
    text_primary: str
    text_secondary: str
    accent: str
    accent_hover: str
    accent_press: str
    input_bg: str
    input_bg_alt: str
    input_border: str
    input_focus: str
    group_bg: str
    group_title_bg: str
    sidebar_bg: str
    sidebar_hover: str
    sidebar_selected: str
    scroll_track: str
    scroll_handle: str
    scroll_handle_hover: str
    link: str
    record_dot: str
    waveform_color: str
    panel_bg: str
    panel_border_top: str
    panel_app_name: str
    panel_app_sub: str
    panel_app_icon_bg: str
    panel_app_icon_border: str
    panel_record_bg: str
    panel_record_border: str
    panel_record_text: str
    panel_record_bg_hover: str
    panel_record_border_hover: str
    panel_record_text_hover: str
    panel_record_bg_active: str
    panel_record_border_active: str
    panel_record_text_active: str
    panel_cancel_bg: str
    panel_cancel_border: str
    panel_cancel_text: str
    panel_cancel_bg_hover: str
    panel_cancel_border_hover: str
    panel_cancel_text_hover: str
    panel_cancel_bg_active: str
    panel_cancel_border_active: str
    panel_cancel_text_active: str
    panel_keycap_bg: str
    panel_keycap_border: str
    panel_keycap_text: str
    panel_divider: str


DEFAULT_WINDOW_THEME_ID = "default"

# Display order in settings.
VISIBLE_WINDOW_THEME_IDS: List[str] = [
    "default",
    "retro",
    "neo",
    "lime",
    "dusk",
    "ocean",
    "terminal_theme",
]


_BASE_THEME: WindowTheme = {
    "id": DEFAULT_WINDOW_THEME_ID,
    "name_key": "settings.ui_customization.theme_default",
    "font_family": "Segoe UI",
    "floating_bg": "#1E2633",
    "window_bg": "#1E2633",
    "window_border": "#3A475E",
    "text_primary": "#ECF2FF",
    "text_secondary": "#C2CEE2",
    "accent": "#4EA1FF",
    "accent_hover": "#67B0FF",
    "accent_press": "#2E8AF0",
    "input_bg": "#222C3B",
    "input_bg_alt": "#1A2230",
    "input_border": "#44556F",
    "input_focus": "#67B0FF",
    "group_bg": "#202A3A",
    "group_title_bg": "#2A3750",
    "sidebar_bg": "#171F2C",
    "sidebar_hover": "#243147",
    "sidebar_selected": "#2E4367",
    "scroll_track": "#1C2533",
    "scroll_handle": "#40516A",
    "scroll_handle_hover": "#5B7295",
    "link": "#79BBFF",
    "record_dot": "#FF6565",
    "waveform_color": "#64AAFF",
    "panel_bg": "#1A2231",
    "panel_border_top": "#33445F",
    "panel_app_name": "#ECF2FF",
    "panel_app_sub": "#A9B6CC",
    "panel_app_icon_bg": "#253248",
    "panel_app_icon_border": "#445672",
    "panel_record_bg": "#274062",
    "panel_record_border": "#4E79AE",
    "panel_record_text": "#B8DEFF",
    "panel_record_bg_hover": "#2F4D75",
    "panel_record_border_hover": "#6794CC",
    "panel_record_text_hover": "#E1F1FF",
    "panel_record_bg_active": "#365987",
    "panel_record_border_active": "#7FB0E8",
    "panel_record_text_active": "#F0F8FF",
    "panel_cancel_bg": "#4B2B36",
    "panel_cancel_border": "#9E5A6D",
    "panel_cancel_text": "#FFA9BB",
    "panel_cancel_bg_hover": "#5C3341",
    "panel_cancel_border_hover": "#BB6E84",
    "panel_cancel_text_hover": "#FFE2E8",
    "panel_cancel_bg_active": "#6A3B4B",
    "panel_cancel_border_active": "#CF8097",
    "panel_cancel_text_active": "#FFF0F4",
    "panel_keycap_bg": "#2A3548",
    "panel_keycap_border": "#4A5D7A",
    "panel_keycap_text": "#E8EDF8",
    "panel_divider": "#43556F",
}


def _build_theme(theme_id: str, name_key: str, **overrides: str) -> WindowTheme:
    theme: WindowTheme = dict(_BASE_THEME)
    theme["id"] = theme_id
    theme["name_key"] = name_key
    theme.update(overrides)
    return theme


_WINDOW_THEMES: Dict[str, WindowTheme] = {
    "default": _build_theme("default", "settings.ui_customization.theme_default"),
    "retro": _build_theme(
        "retro",
        "settings.ui_customization.theme_retro",
        font_family="Consolas",
        floating_bg="#2A2218",
        window_bg="#2A2218",
        window_border="#7B5E37",
        text_primary="#F2D6A2",
        text_secondary="#D8B87C",
        accent="#D9A74B",
        accent_hover="#E7BC67",
        accent_press="#BF8C38",
        input_bg="#312617",
        input_bg_alt="#261E13",
        input_border="#7B5E37",
        input_focus="#E7BC67",
        group_bg="#302516",
        group_title_bg="#3A2B17",
        sidebar_bg="#221A11",
        sidebar_hover="#352715",
        sidebar_selected="#4A341A",
        scroll_track="#271E13",
        scroll_handle="#6B512F",
        scroll_handle_hover="#8B683E",
        link="#F0C27B",
        record_dot="#E07A3A",
        waveform_color="#E3B66E",
        panel_bg="#261E14",
        panel_border_top="#5C472A",
        panel_app_name="#F3D9A8",
        panel_app_sub="#CDAE78",
        panel_app_icon_bg="#332613",
        panel_app_icon_border="#6C5331",
        panel_record_bg="#4A3A1F",
        panel_record_border="#8A6C3B",
        panel_record_text="#F4DDAE",
        panel_record_bg_hover="#5C4624",
        panel_record_border_hover="#A17E45",
        panel_record_text_hover="#FFF0D2",
        panel_record_bg_active="#6B502A",
        panel_record_border_active="#BA9350",
        panel_record_text_active="#FFF5DF",
        panel_cancel_bg="#4A3025",
        panel_cancel_border="#8C5842",
        panel_cancel_text="#E5B193",
        panel_cancel_bg_hover="#5A3A2D",
        panel_cancel_border_hover="#A56A51",
        panel_cancel_text_hover="#F8DDCC",
        panel_cancel_bg_active="#684235",
        panel_cancel_border_active="#BB7C62",
        panel_cancel_text_active="#FEEBDD",
        panel_keycap_bg="#332718",
        panel_keycap_border="#6D5433",
        panel_keycap_text="#ECD5AE",
        panel_divider="#634C30",
    ),
    "neo": _build_theme(
        "neo",
        "settings.ui_customization.theme_neo",
        font_family="Cascadia Code",
        floating_bg="#111625",
        window_bg="#111625",
        window_border="#3C4A78",
        text_primary="#E9F2FF",
        text_secondary="#B0C0E4",
        accent="#31D6FF",
        accent_hover="#63E6FF",
        accent_press="#10B8E4",
        input_bg="#151C2E",
        input_bg_alt="#101627",
        input_border="#3D4E7F",
        input_focus="#63E6FF",
        group_bg="#161E31",
        group_title_bg="#1D2944",
        sidebar_bg="#0E1423",
        sidebar_hover="#1B2740",
        sidebar_selected="#23365A",
        scroll_track="#141C2E",
        scroll_handle="#3B4D78",
        scroll_handle_hover="#5670AC",
        link="#6EE7FF",
        record_dot="#FF4FA8",
        waveform_color="#56D9FF",
        panel_bg="#121A2C",
        panel_border_top="#2D3B60",
        panel_app_name="#E9F2FF",
        panel_app_sub="#A7B8DE",
        panel_app_icon_bg="#1C2742",
        panel_app_icon_border="#3D507F",
        panel_record_bg="#224B68",
        panel_record_border="#3A8DBD",
        panel_record_text="#B5F1FF",
        panel_record_bg_hover="#2A5D81",
        panel_record_border_hover="#4FA7DD",
        panel_record_text_hover="#DEFAFF",
        panel_record_bg_active="#32709A",
        panel_record_border_active="#66BDEB",
        panel_record_text_active="#EAFDFF",
        panel_cancel_bg="#4A2440",
        panel_cancel_border="#944E80",
        panel_cancel_text="#FFA8E3",
        panel_cancel_bg_hover="#5A2B4D",
        panel_cancel_border_hover="#AE5E96",
        panel_cancel_text_hover="#FFDDF4",
        panel_cancel_bg_active="#68335A",
        panel_cancel_border_active="#C16FA8",
        panel_cancel_text_active="#FFEFFC",
        panel_keycap_bg="#1C2842",
        panel_keycap_border="#3E5384",
        panel_keycap_text="#DCE8FF",
        panel_divider="#3A4E79",
    ),
    "lime": _build_theme(
        "lime",
        "settings.ui_customization.theme_lime",
        font_family="Cascadia Code",
        floating_bg="#141E14",
        window_bg="#141E14",
        window_border="#3C653C",
        text_primary="#E8FFE0",
        text_secondary="#B7D9AB",
        accent="#86E85A",
        accent_hover="#9CF06E",
        accent_press="#6FCE48",
        input_bg="#172417",
        input_bg_alt="#111B11",
        input_border="#3D663D",
        input_focus="#9CF06E",
        group_bg="#182718",
        group_title_bg="#203220",
        sidebar_bg="#0E170E",
        sidebar_hover="#1A2B1A",
        sidebar_selected="#244024",
        scroll_track="#152015",
        scroll_handle="#3A613A",
        scroll_handle_hover="#538953",
        link="#A9FF81",
        record_dot="#B3FF6A",
        waveform_color="#88FF52",
        panel_bg="#131F13",
        panel_border_top="#2E4A2E",
        panel_app_name="#E8FFE0",
        panel_app_sub="#A7C99E",
        panel_app_icon_bg="#1C2F1C",
        panel_app_icon_border="#3A623A",
        panel_record_bg="#2C4D2C",
        panel_record_border="#5F9A5F",
        panel_record_text="#CDFFD0",
        panel_record_bg_hover="#346136",
        panel_record_border_hover="#73B873",
        panel_record_text_hover="#E9FFEB",
        panel_record_bg_active="#3E7640",
        panel_record_border_active="#8BCE8D",
        panel_record_text_active="#F3FFF4",
        panel_cancel_bg="#3F3520",
        panel_cancel_border="#7F6B3E",
        panel_cancel_text="#E4D69B",
        panel_cancel_bg_hover="#4D4128",
        panel_cancel_border_hover="#9A8250",
        panel_cancel_text_hover="#F8EEC9",
        panel_cancel_bg_active="#5A4C30",
        panel_cancel_border_active="#B59A60",
        panel_cancel_text_active="#FFF7DF",
        panel_keycap_bg="#223522",
        panel_keycap_border="#456E45",
        panel_keycap_text="#D9F3CF",
        panel_divider="#3D613D",
    ),
    "dusk": _build_theme(
        "dusk",
        "settings.ui_customization.theme_dusk",
        floating_bg="#1A1E2D",
        window_bg="#1A1E2D",
        window_border="#464C6E",
        text_primary="#F0EFFF",
        text_secondary="#C6C3E6",
        accent="#8EA2FF",
        accent_hover="#AAB9FF",
        accent_press="#7A8FEA",
        input_bg="#20263A",
        input_bg_alt="#171C2C",
        input_border="#475379",
        input_focus="#AAB9FF",
        group_bg="#21283D",
        group_title_bg="#2A3350",
        sidebar_bg="#14192A",
        sidebar_hover="#232C44",
        sidebar_selected="#2F3A5E",
        scroll_track="#1A2133",
        scroll_handle="#485271",
        scroll_handle_hover="#63709A",
        link="#B2C3FF",
        record_dot="#FF6E98",
        waveform_color="#9DB0FF",
        panel_bg="#1B2135",
        panel_border_top="#3A4568",
        panel_app_name="#EFEFFF",
        panel_app_sub="#B7BDE0",
        panel_app_icon_bg="#25304B",
        panel_app_icon_border="#4A5C86",
        panel_record_bg="#32496C",
        panel_record_border="#5D81B5",
        panel_record_text="#CDE0FF",
        panel_record_bg_hover="#3D5B86",
        panel_record_border_hover="#739DD8",
        panel_record_text_hover="#E5EEFF",
        panel_record_bg_active="#486AA0",
        panel_record_border_active="#89B3E8",
        panel_record_text_active="#F2F7FF",
        panel_cancel_bg="#4B2A44",
        panel_cancel_border="#9A5B8E",
        panel_cancel_text="#F3B4E7",
        panel_cancel_bg_hover="#5A3353",
        panel_cancel_border_hover="#B56EA7",
        panel_cancel_text_hover="#FFE5FB",
        panel_cancel_bg_active="#693D62",
        panel_cancel_border_active="#CB82BC",
        panel_cancel_text_active="#FFF0FD",
        panel_keycap_bg="#283251",
        panel_keycap_border="#4E5F8A",
        panel_keycap_text="#E1E8FF",
        panel_divider="#4C5B82",
    ),
    "ocean": _build_theme(
        "ocean",
        "settings.ui_customization.theme_ocean",
        floating_bg="#112331",
        window_bg="#112331",
        window_border="#2F5D77",
        text_primary="#E7F7FF",
        text_secondary="#AFCFDD",
        accent="#36B7D9",
        accent_hover="#5BC7E5",
        accent_press="#1F9CBC",
        input_bg="#153043",
        input_bg_alt="#102636",
        input_border="#2F617F",
        input_focus="#66D4F1",
        group_bg="#173447",
        group_title_bg="#1D425A",
        sidebar_bg="#0D1E2B",
        sidebar_hover="#183549",
        sidebar_selected="#1F4762",
        scroll_track="#142A3A",
        scroll_handle="#30607C",
        scroll_handle_hover="#3D7C9F",
        link="#7EE1FF",
        record_dot="#7FD4FF",
        waveform_color="#54C8FF",
        panel_bg="#132B3D",
        panel_border_top="#2E5C77",
        panel_app_name="#E5F8FF",
        panel_app_sub="#A8CAD7",
        panel_app_icon_bg="#1E3C52",
        panel_app_icon_border="#3B6B87",
        panel_record_bg="#1F546D",
        panel_record_border="#3E8EB1",
        panel_record_text="#B6ECFF",
        panel_record_bg_hover="#266883",
        panel_record_border_hover="#52A9CF",
        panel_record_text_hover="#DBF7FF",
        panel_record_bg_active="#2E7B9A",
        panel_record_border_active="#67BEE4",
        panel_record_text_active="#EDFAFF",
        panel_cancel_bg="#4A3A2B",
        panel_cancel_border="#8D6F4F",
        panel_cancel_text="#EACBA2",
        panel_cancel_bg_hover="#584632",
        panel_cancel_border_hover="#A6845E",
        panel_cancel_text_hover="#FAE8CC",
        panel_cancel_bg_active="#665239",
        panel_cancel_border_active="#BD9A70",
        panel_cancel_text_active="#FFF4E3",
        panel_keycap_bg="#214258",
        panel_keycap_border="#437391",
        panel_keycap_text="#D8EFFA",
        panel_divider="#3F6F8B",
    ),
    "terminal_theme": _build_theme(
        "terminal_theme",
        "settings.ui_customization.theme_terminal_theme",
        font_family="Cascadia Mono",
        floating_bg="#0A0F0A",
        window_bg="#0A0F0A",
        window_border="#2A5A2A",
        text_primary="#B6FF9E",
        text_secondary="#7FD26C",
        accent="#39FF14",
        accent_hover="#64FF49",
        accent_press="#2EDD0F",
        input_bg="#0F1A0F",
        input_bg_alt="#0A130A",
        input_border="#2F6A2F",
        input_focus="#64FF49",
        group_bg="#102010",
        group_title_bg="#152915",
        sidebar_bg="#091309",
        sidebar_hover="#163016",
        sidebar_selected="#1F451F",
        scroll_track="#0F1A0F",
        scroll_handle="#2E632E",
        scroll_handle_hover="#438E43",
        link="#82FF70",
        record_dot="#52FF3F",
        waveform_color="#39FF14",
        panel_bg="#0D180D",
        panel_border_top="#265226",
        panel_app_name="#C3FFAE",
        panel_app_sub="#79C96A",
        panel_app_icon_bg="#132413",
        panel_app_icon_border="#2D5C2D",
        panel_record_bg="#1D4021",
        panel_record_border="#3A7F42",
        panel_record_text="#A4FF99",
        panel_record_bg_hover="#25502A",
        panel_record_border_hover="#4A9E53",
        panel_record_text_hover="#D8FFD2",
        panel_record_bg_active="#2E6134",
        panel_record_border_active="#62BC6D",
        panel_record_text_active="#EEFFEC",
        panel_cancel_bg="#3D3520",
        panel_cancel_border="#7D6B3B",
        panel_cancel_text="#E0D087",
        panel_cancel_bg_hover="#4A4128",
        panel_cancel_border_hover="#977F47",
        panel_cancel_text_hover="#F5E9B8",
        panel_cancel_bg_active="#584E30",
        panel_cancel_border_active="#AF9356",
        panel_cancel_text_active="#FFF8D8",
        panel_keycap_bg="#193019",
        panel_keycap_border="#376F37",
        panel_keycap_text="#BDF2AD",
        panel_divider="#2D5B2D",
    ),
}

# Backward-compatible aliases for previously added ids.
_THEME_ALIASES = {
    "tokyo_night": "dusk",
    "catppuccin_mocha": "dusk",
    "dracula": "neo",
    "gruvbox_dark": "retro",
    "nord": "ocean",
    "terminal_green": "terminal_theme",
}


def get_window_theme_ids() -> List[str]:
    return list(VISIBLE_WINDOW_THEME_IDS)


def get_window_theme(theme_id: str | None) -> WindowTheme:
    if theme_id in _WINDOW_THEMES:
        return _WINDOW_THEMES[theme_id]
    mapped = _THEME_ALIASES.get(theme_id or "", DEFAULT_WINDOW_THEME_ID)
    return _WINDOW_THEMES.get(mapped, _WINDOW_THEMES[DEFAULT_WINDOW_THEME_ID])


def get_window_theme_name_key(theme_id: str | None) -> str:
    return get_window_theme(theme_id)["name_key"]
