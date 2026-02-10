(function () {
  const SUPPORTED_LANGS = ["en", "fr", "ru"];
  const translationsByLang = {};

  const FALLBACK_THEME_NOTES = {
    default: "Default: universal theme for daily work.",
    ocean: "Ocean: cool palette for calm focus.",
    dusk: "Dusk: evening contrast with soft accents.",
    retro: "Retro: warm retro gradient and analog atmosphere.",
    neo: "Neo: neon style with vivid contrast.",
    lime: "Lime: energetic green accent and high visual tone.",
    terminal: "Terminal Theme: modern CLI aesthetics with green terminal glow.",
  };

  const FALLBACK_THEME_APPS = {
    default: "VS Code",
    ocean: "Google Docs",
    dusk: "Notion",
    retro: "Obsidian",
    neo: "Telegram Desktop",
    lime: "LibreOffice Writer",
    terminal: "Windows Terminal",
  };

  const FALLBACK_DOWNLOAD_HINT = "Windows downloads directly; for macOS/Linux the Releases page opens.";
  const FALLBACK_SELECTED_HINTS = {
    windows: "Selected: Windows (.exe).",
    macos: "Selected: macOS (.dmg).",
    linux: "Selected: Linux (.AppImage).",
  };
  const FALLBACK_DOWNLOAD_TITLES = {
    windows: "Download for Windows",
    macos: "Download for macOS",
    linux: "Open downloads",
  };
  const FALLBACK_LANG_MENU = {
    en: "English",
    fr: "French",
    ru: "Russian",
  };

  const heroWave = document.getElementById("hero-wave");
  const heroPreview = document.getElementById("hero-preview");
  const topbar = document.querySelector(".topbar");
  const heroAppName = document.getElementById("hero-app-name");
  const themeNote = document.getElementById("theme-note");
  const themeButtons = document.querySelectorAll(".theme-btn[data-theme-id]");

  const heroState = document.getElementById("hero-state");
  const heroTime = document.getElementById("hero-time");
  const heroRecordBtn = document.getElementById("hero-record-btn");
  const heroCancelBtn = document.getElementById("hero-cancel-btn");
  const heroRecordToggle = document.getElementById("hero-record-toggle");
  const headerThemeDropdown = document.getElementById("header-theme-dropdown");
  const headerThemeTrigger = document.getElementById("header-theme-trigger");
  const topDownloadBtn = document.getElementById("top-download-btn");
  const topLangDropdown = document.getElementById("top-lang-dropdown");
  const topLangToggle = document.getElementById("top-lang-toggle");
  const langButtons = document.querySelectorAll(".lang-btn[data-lang-id]");

  const licensesSection = document.getElementById("licenses");
  const downloadHint = document.getElementById("download-hint");
  const downloadCards = document.querySelectorAll(".platform-icon-card[data-download-os]");
  const metaDescription = document.querySelector('meta[name="description"]');

  let currentLang = "en";
  let currentTranslation = null;
  let recording = true;
  let seconds = 11;
  let selectedDownloadOs = "";
  let topDownloadTargetOs = "windows";

  const DOWNLOAD_LINKS = {
    windows: "https://github.com/v01gh7/RapidWhisper/releases/latest/download/RapidWhisper.exe",
    macos: "https://github.com/v01gh7/RapidWhisper/releases/latest",
    linux: "https://github.com/v01gh7/RapidWhisper/releases/latest",
  };

  function getByPath(source, path, fallbackValue) {
    if (!source || !path) return fallbackValue;
    const value = path.split(".").reduce(function (acc, key) {
      if (acc && typeof acc === "object") {
        return acc[key];
      }
      return undefined;
    }, source);
    return value === undefined || value === null ? fallbackValue : value;
  }

  function setText(selector, value) {
    if (typeof value !== "string") return;
    const node = document.querySelector(selector);
    if (node) {
      node.textContent = value;
    }
  }

  function setHTML(selector, value) {
    if (typeof value !== "string") return;
    const node = document.querySelector(selector);
    if (node) {
      node.innerHTML = value;
    }
  }

  function setAttr(selector, attrName, value) {
    if (typeof value !== "string") return;
    const node = document.querySelector(selector);
    if (node) {
      node.setAttribute(attrName, value);
    }
  }

  function setListText(selector, values) {
    if (!Array.isArray(values)) return;
    const nodes = document.querySelectorAll(selector);
    nodes.forEach(function (node, index) {
      if (typeof values[index] === "string") {
        node.textContent = values[index];
      }
    });
  }

  function setTagList(selector, values, className) {
    if (!Array.isArray(values)) return;
    const node = document.querySelector(selector);
    if (!node) return;
    node.innerHTML = "";
    values.forEach(function (value) {
      if (typeof value !== "string") return;
      const trimmed = value.trim();
      if (!trimmed) return;
      const item = document.createElement("span");
      if (typeof className === "string" && className) {
        item.className = className;
      }
      item.textContent = trimmed;
      node.appendChild(item);
    });
  }

  function setPipelineSteps(steps) {
    if (!Array.isArray(steps)) return;
    const nodes = document.querySelectorAll("#pipeline .steps li");
    nodes.forEach(function (node, index) {
      if (typeof steps[index] !== "string") return;
      const order = String(index + 1).padStart(2, "0");
      node.innerHTML = "<span>" + order + "</span> " + steps[index];
    });
  }

  function setThemeButtonLabels(themeButtonsMap) {
    if (!themeButtonsMap || typeof themeButtonsMap !== "object") return;
    themeButtons.forEach(function (button) {
      const themeId = button.dataset.themeId || "";
      const label = themeButtonsMap[themeId];
      if (typeof label === "string") {
        button.textContent = label;
      }
    });
  }

  function scrollToTargetWithOffset(targetElement) {
    if (!targetElement) return;
    const headerOffset = (topbar ? Math.ceil(topbar.getBoundingClientRect().height) : 0) + 20;
    const targetTop = targetElement.getBoundingClientRect().top + window.scrollY - headerOffset;
    window.scrollTo({
      top: Math.max(0, targetTop),
      behavior: "smooth",
    });
  }

  function scrollByHash(hashValue) {
    const hash = typeof hashValue === "string" ? hashValue.trim() : "";
    if (!hash || hash === "#") return false;
    const id = hash.startsWith("#") ? hash.slice(1) : hash;
    if (!id) return false;
    const target = document.getElementById(id);
    if (!target) return false;
    scrollToTargetWithOffset(target);
    return true;
  }

  function setLangButtonLabels(langMenuMap) {
    const labels = langMenuMap && typeof langMenuMap === "object" ? langMenuMap : FALLBACK_LANG_MENU;
    langButtons.forEach(function (button) {
      const langId = button.dataset.langId || "";
      const label = labels[langId];
      if (typeof label === "string") {
        button.textContent = label;
      }
    });
  }

  function setLangButtonsActive(langCode) {
    langButtons.forEach(function (button) {
      button.classList.toggle("is-active", button.dataset.langId === langCode);
    });
  }

  function setPurposeCards(cards) {
    if (!Array.isArray(cards)) return;
    const nodes = document.querySelectorAll("#purpose .tile");
    nodes.forEach(function (cardNode, index) {
      const payload = cards[index];
      if (!payload || typeof payload !== "object") return;
      const titleNode = cardNode.querySelector("h3");
      const bodyNode = cardNode.querySelector("p");
      if (titleNode && typeof payload.title === "string") titleNode.textContent = payload.title;
      if (bodyNode && typeof payload.desc === "string") bodyNode.textContent = payload.desc;
    });
  }

  function setFeatureCards(cards) {
    if (!Array.isArray(cards)) return;
    const nodes = document.querySelectorAll("#features .feature-card");
    nodes.forEach(function (cardNode, index) {
      const payload = cards[index];
      if (!payload || typeof payload !== "object") return;
      const titleNode = cardNode.querySelector("h3");
      const bodyNode = cardNode.querySelector("p");
      if (titleNode && typeof payload.title === "string") titleNode.textContent = payload.title;
      if (bodyNode && typeof payload.desc === "string") bodyNode.textContent = payload.desc;
    });
  }

  function setProviderCards(cards) {
    if (!Array.isArray(cards)) return;
    const nodes = document.querySelectorAll("#providers .provider-card");
    nodes.forEach(function (cardNode, index) {
      const payload = cards[index];
      if (!payload || typeof payload !== "object") return;
      const titleNode = cardNode.querySelector("h3");
      const bodyNode = cardNode.querySelector("p");
      if (titleNode && typeof payload.title === "string") titleNode.textContent = payload.title;
      if (bodyNode && typeof payload.desc === "string") bodyNode.textContent = payload.desc;
    });
  }

  function setFooterText(footer) {
    if (!footer || typeof footer !== "object") return;
    const spans = document.querySelectorAll(".footer span");
    if (spans[0] && typeof footer.left === "string") spans[0].textContent = footer.left;
    if (spans[1] && typeof footer.center === "string") spans[1].textContent = footer.center;
    if (spans[2] && typeof footer.right === "string") spans[2].textContent = footer.right;
  }

  function applyMeta(translation) {
    const htmlLang = getByPath(translation, "meta.lang", currentLang);
    if (typeof htmlLang === "string") {
      document.documentElement.lang = htmlLang;
    }
    const pageTitle = getByPath(translation, "meta.title", "");
    if (typeof pageTitle === "string" && pageTitle) {
      document.title = pageTitle;
    }
    const pageDescription = getByPath(translation, "meta.description", "");
    if (metaDescription && typeof pageDescription === "string" && pageDescription) {
      metaDescription.setAttribute("content", pageDescription);
    }
  }

  function applyStaticText(translation) {
    setAttr(".brand", "aria-label", getByPath(translation, "header.brand_aria", "RapidWhisper Home"));
    setText('.nav a[href="#purpose"]', getByPath(translation, "header.nav.purpose", ""));
    setText('.nav a[href="#controls"]', getByPath(translation, "header.nav.hotkeys", ""));
    setText('.nav a[href="#features"]', getByPath(translation, "header.nav.features", ""));
    setText('.nav a[href="#providers"]', getByPath(translation, "header.nav.providers", ""));
    setText('.nav a[href="#pipeline"]', getByPath(translation, "header.nav.pipeline", ""));

    setAttr("#header-theme-trigger", "aria-label", getByPath(translation, "header.theme_aria", ""));
    setAttr("#header-theme-menu", "aria-label", getByPath(translation, "header.theme_aria", ""));
    setText("#top-download-btn", getByPath(translation, "header.download_button", ""));
    setAttr("#top-lang-menu", "aria-label", getByPath(translation, "header.lang_menu_aria", "Language list"));
    setLangButtonLabels(getByPath(translation, "header.lang_menu", FALLBACK_LANG_MENU));
    setThemeButtonLabels(getByPath(translation, "hero.theme_buttons", {}));

    setText(".kicker", getByPath(translation, "hero.kicker", ""));
    setText(".hero-copy h1", getByPath(translation, "hero.title", ""));
    setText(".lead", getByPath(translation, "hero.lead", ""));
    setText('[data-action="scroll-controls"]', getByPath(translation, "hero.open_hotkeys", ""));

    setAttr(".discord-news-block", "aria-label", getByPath(translation, "hero.discord.aria", ""));
    setText(".discord-news-copy span", getByPath(translation, "hero.discord.description", ""));
    setText(".discord-news-link", getByPath(translation, "hero.discord.open_button", ""));

    setAttr(".support-block", "aria-label", getByPath(translation, "hero.support.aria", ""));
    setText(".support-head h3", getByPath(translation, "hero.support.title", ""));
    setText(".support-head p", getByPath(translation, "hero.support.subtitle", ""));
    setText(".support-grid .support-card:nth-child(1) .support-desc", getByPath(translation, "hero.support.cards.streamlabs_desc", ""));
    setText(".support-grid .support-card:nth-child(2) .support-desc", getByPath(translation, "hero.support.cards.donatex_desc", ""));
    setText(".support-grid .support-card:nth-child(3) .support-desc", getByPath(translation, "hero.support.cards.kofi_desc", ""));

    setAttr("aside.demo", "aria-label", getByPath(translation, "hero.demo_aria", ""));
    setText(".theme-panel-title", getByPath(translation, "hero.theme_panel_title", ""));
    setAttr(".theme-switcher", "aria-label", getByPath(translation, "hero.theme_switcher_aria", ""));
    setText(".demo-app div span", getByPath(translation, "hero.active_app", ""));
    setText("#hero-cancel-btn", getByPath(translation, "hero.buttons.cancel", ""));

    setAttr(".download-block", "aria-label", getByPath(translation, "hero.download.aria", ""));
    setText(".download-head h3", getByPath(translation, "hero.download.title", ""));
    setText(".download-head p", getByPath(translation, "hero.download.subtitle", ""));
    setAttr(".platform-strip", "aria-label", getByPath(translation, "hero.download.platform_strip_aria", ""));
    setAttr(".smart-format-block", "aria-label", getByPath(translation, "hero.smart_format.aria", ""));
    setText(".smart-format-title", getByPath(translation, "hero.smart_format.title", ""));
    setText(".smart-format-count", getByPath(translation, "hero.smart_format.count", ""));
    setText(".smart-format-lead", getByPath(translation, "hero.smart_format.lead", ""));
    setAttr(".smart-format-modes", "aria-label", getByPath(translation, "hero.smart_format.modes_aria", ""));
    setTagList(".smart-format-modes", getByPath(translation, "hero.smart_format.modes", []), "smart-chip");
    setText(".smart-format-apps-title", getByPath(translation, "hero.smart_format.standard_apps_title", ""));
    setAttr(".smart-format-apps", "aria-label", getByPath(translation, "hero.smart_format.standard_apps_aria", ""));
    setTagList(".smart-format-apps", getByPath(translation, "hero.smart_format.standard_apps", []), "smart-chip");
    setText(".demo-free-note", getByPath(translation, "hero.download.free", ""));

    const platformNames = getByPath(translation, "hero.download.platform_names", {});
    const platformIconAlt = getByPath(translation, "hero.download.platform_icon_alt", {});
    document.querySelectorAll(".platform-icon-card[data-download-os]").forEach(function (card) {
      const osId = card.dataset.downloadOs || "";
      const nameNode = card.querySelector("span");
      const iconNode = card.querySelector("img");
      if (nameNode && typeof platformNames[osId] === "string") {
        nameNode.textContent = platformNames[osId];
      }
      if (iconNode && typeof platformIconAlt[osId] === "string") {
        iconNode.setAttribute("alt", platformIconAlt[osId]);
      }
    });

    setAttr("#free-use", "aria-label", getByPath(translation, "free_use.aria", ""));
    setText(".free-use-head h2", getByPath(translation, "free_use.title", ""));
    setText(".free-use-badge", getByPath(translation, "free_use.badge", ""));
    setText(".free-use-lead", getByPath(translation, "free_use.lead", ""));
    setText(".free-local-title", getByPath(translation, "free_use.local_stats_title", ""));
    setAttr(".free-local-tags", "aria-label", getByPath(translation, "free_use.local_stats_aria", ""));
    setTagList(".free-local-tags", getByPath(translation, "free_use.local_stats", []), "free-stat-chip");
    setText(".free-local-note", getByPath(translation, "free_use.local_stats_note", ""));
    setText(".free-card-start h3", getByPath(translation, "free_use.start_title", ""));
    setText(".free-start-text", getByPath(translation, "free_use.start_text", ""));
    setText("#free-groq-link", getByPath(translation, "free_use.groq_link_label", ""));
    setAttr("#free-groq-link", "aria-label", getByPath(translation, "free_use.groq_link_aria", ""));
    setAttr("#free-groq-link", "title", getByPath(translation, "free_use.groq_link_title", ""));
    setListText(".free-steps li span", getByPath(translation, "free_use.steps", []));
    setText(".free-card-providers h3", getByPath(translation, "free_use.providers_title", ""));
    setText(".free-providers-text", getByPath(translation, "free_use.providers_text", ""));
    setAttr(".free-provider-tags", "aria-label", getByPath(translation, "free_use.providers_aria", ""));
    setTagList(".free-provider-tags", getByPath(translation, "free_use.providers", []), "free-provider-chip");
    setText(".free-llm-note", getByPath(translation, "free_use.llm_note", ""));
    setText(".free-model-note", getByPath(translation, "free_use.model_note", ""));

    setText("#controls > h2", getByPath(translation, "controls.title", ""));
    setText("#controls .control-card:first-child > h3", getByPath(translation, "controls.hotkeys_title", ""));
    setListText(".hotkey-list .hotkey-name", getByPath(translation, "controls.hotkey_names", []));
    setText(".control-section-title", getByPath(translation, "controls.quick_window_title", ""));

    const windowSettings = getByPath(translation, "controls.window_settings", []);
    if (Array.isArray(windowSettings)) {
      const rows = document.querySelectorAll(".control-setting-list li");
      rows.forEach(function (row, index) {
        const payload = windowSettings[index];
        if (!payload || typeof payload !== "object") return;
        const nameNode = row.querySelector("span");
        const valueNode = row.querySelector("strong");
        if (nameNode && typeof payload.name === "string") nameNode.textContent = payload.name;
        if (valueNode && typeof payload.value === "string") valueNode.textContent = payload.value;
      });
    }

    setText(".hooks-card > h3", getByPath(translation, "controls.hooks_title", ""));
    setText(".hooks-events-head span", getByPath(translation, "controls.pipeline_events_title", ""));
    setText(".hooks-events-head strong", getByPath(translation, "controls.pipeline_events_count", ""));
    setListText(".hooks-events-block .hooks-event-tags code", getByPath(translation, "controls.pipeline_events", []));
    setText(".hooks-intro", getByPath(translation, "controls.hooks_intro", ""));
    setListText(".hooks-list li > span", getByPath(translation, "controls.hooks_sections", []));
    setListText(".hooks-list li:nth-child(1) .hooks-meta-tags code", getByPath(translation, "controls.hooks_connect_tags", []));
    setListText(".hooks-list li:nth-child(2) .hooks-meta-tags code", getByPath(translation, "controls.hooks_ui_tags", []));
    setListText(".hooks-list li:nth-child(3) .hooks-meta-tags code", getByPath(translation, "controls.hooks_contract_tags", []));
    setHTML(".hooks-example", getByPath(translation, "controls.hooks_example_html", ""));

    setText("#purpose > h2", getByPath(translation, "purpose.title", ""));
    setPurposeCards(getByPath(translation, "purpose.cards", []));

    setText("#features > h2", getByPath(translation, "features.title", ""));
    setFeatureCards(getByPath(translation, "features.cards", []));

    setText("#providers > h2", getByPath(translation, "providers.title", ""));
    setProviderCards(getByPath(translation, "providers.cards", []));

    setText("#pipeline > h2", getByPath(translation, "pipeline.title", ""));
    setPipelineSteps(getByPath(translation, "pipeline.steps", []));

    setText("#licenses > h2", getByPath(translation, "licenses.title", ""));
    setText("#licenses > p", getByPath(translation, "licenses.description", ""));
    setListText("#licenses .license-list li", getByPath(translation, "licenses.items", []));
    setText('#licenses [data-action="hide-license"]', getByPath(translation, "licenses.hide_button", ""));

    setFooterText(getByPath(translation, "footer", {}));
  }

  function createWave(container) {
    if (!container || container.dataset.waveReady === "1") return;
    container.dataset.waveReady = "1";
    const fragment = document.createDocumentFragment();
    for (let i = 0; i < 44; i += 1) {
      const bar = document.createElement("span");
      bar.className = "bar";
      bar.style.setProperty("--i", String(i));
      bar.style.height = (9 + Math.round(Math.random() * 26)) + "px";
      fragment.appendChild(bar);
    }
    container.appendChild(fragment);
  }

  function animateWave(container, isRecording) {
    if (!container) return;
    const bars = container.querySelectorAll(".bar");
    bars.forEach(function (bar, idx) {
      const min = isRecording ? 10 : 6;
      const max = isRecording ? 38 : 12;
      const emphasis = isRecording && idx > 16 && idx < 30 ? 9 : 0;
      const next = min + Math.round(Math.random() * (max - min + emphasis));
      bar.style.height = next + "px";
    });
  }

  function formatTime(totalSeconds) {
    const mm = Math.floor(totalSeconds / 60).toString().padStart(2, "0");
    const ss = (totalSeconds % 60).toString().padStart(2, "0");
    return mm + ":" + ss;
  }

  function syncHeroState() {
    if (!heroState || !heroTime) return;
    if (recording) {
      heroState.textContent = getByPath(currentTranslation, "hero.state.recording", "Recording...");
      heroTime.textContent = formatTime(seconds);
      if (heroRecordBtn) heroRecordBtn.textContent = getByPath(currentTranslation, "hero.buttons.pause", "Pause");
      if (heroRecordToggle) heroRecordToggle.textContent = getByPath(currentTranslation, "hero.buttons.pause_recording", "Pause recording");
    } else {
      heroState.textContent = getByPath(currentTranslation, "hero.state.idle", "Standby");
      heroTime.textContent = "00:00";
      if (heroRecordBtn) heroRecordBtn.textContent = getByPath(currentTranslation, "hero.buttons.record", "Record");
      if (heroRecordToggle) heroRecordToggle.textContent = getByPath(currentTranslation, "hero.buttons.start_recording", "Start recording");
    }
    animateWave(heroWave, recording);
  }

  function setRecording(nextValue) {
    recording = Boolean(nextValue);
    if (recording && seconds === 0) {
      seconds = 1;
    }
    syncHeroState();
  }

  function detectCurrentOS() {
    const uaDataPlatform = navigator.userAgentData && navigator.userAgentData.platform
      ? navigator.userAgentData.platform
      : "";
    const platform = (uaDataPlatform + " " + (navigator.platform || "")).toLowerCase();
    const userAgent = (navigator.userAgent || "").toLowerCase();

    if (platform.includes("mac") || userAgent.includes("macintosh") || userAgent.includes("mac os")) {
      return "macos";
    }
    if (platform.includes("win") || userAgent.includes("windows")) {
      return "windows";
    }
    if (platform.includes("linux") || userAgent.includes("linux")) {
      return "linux";
    }
    return "windows";
  }

  function setDownloadHint(osId) {
    if (!downloadHint) return;
    const selectedMap = getByPath(currentTranslation, "hero.download.selected", FALLBACK_SELECTED_HINTS);
    const defaultHint = getByPath(currentTranslation, "hero.download.hint_default", FALLBACK_DOWNLOAD_HINT);
    if (osId && selectedMap && typeof selectedMap[osId] === "string") {
      downloadHint.textContent = selectedMap[osId];
      return;
    }
    downloadHint.textContent = defaultHint;
  }

  function markDownloadCard(osId) {
    const nextId = DOWNLOAD_LINKS[osId] ? osId : "";
    selectedDownloadOs = nextId;
    downloadCards.forEach(function (card) {
      card.classList.toggle("is-active", nextId !== "" && card.dataset.downloadOs === nextId);
    });
  }

  function setTopDownloadTitle(osId) {
    if (!topDownloadBtn) return;
    const titleMap = getByPath(currentTranslation, "hero.download.top_button_title", FALLBACK_DOWNLOAD_TITLES);
    const titleValue = titleMap && typeof titleMap[osId] === "string"
      ? titleMap[osId]
      : FALLBACK_DOWNLOAD_TITLES[osId] || FALLBACK_DOWNLOAD_TITLES.windows;
    topDownloadBtn.title = titleValue;
  }

  function downloadByOS(osId) {
    const id = DOWNLOAD_LINKS[osId] ? osId : "windows";
    const href = DOWNLOAD_LINKS[id];
    if (!href) return;

    markDownloadCard(id);
    setDownloadHint(id);

    if (id === "windows") {
      const a = document.createElement("a");
      a.href = href;
      a.download = "RapidWhisper.exe";
      a.rel = "noopener";
      document.body.appendChild(a);
      a.click();
      a.remove();
      return;
    }

    window.open(href, "_blank", "noopener");
  }

  function setThemeDropdownOpen(open) {
    if (!headerThemeDropdown || !headerThemeTrigger) return;
    const isOpen = Boolean(open);
    headerThemeDropdown.classList.toggle("is-open", isOpen);
    headerThemeTrigger.setAttribute("aria-expanded", isOpen ? "true" : "false");
  }

  function setLangDropdownOpen(open) {
    if (!topLangDropdown || !topLangToggle) return;
    const isOpen = Boolean(open);
    topLangDropdown.classList.toggle("is-open", isOpen);
    topLangToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  }

  function applyTheme(themeId) {
    const id = themeId || "default";
    document.body.dataset.pageTheme = id;
    if (heroPreview) {
      heroPreview.dataset.themeId = id;
    }
    if (heroAppName) {
      const appMap = getByPath(currentTranslation, "hero.theme_apps", FALLBACK_THEME_APPS);
      if (typeof appMap[id] === "string") {
        heroAppName.textContent = appMap[id];
      }
    }
    if (themeNote) {
      const noteMap = getByPath(currentTranslation, "hero.theme_notes", FALLBACK_THEME_NOTES);
      if (typeof noteMap[id] === "string") {
        themeNote.textContent = noteMap[id];
      }
    }
    themeButtons.forEach(function (button) {
      button.classList.toggle("is-active", button.dataset.themeId === id);
    });
  }

  function setLicensesVisible(visible) {
    if (!licensesSection) return;
    const isVisible = Boolean(visible);
    licensesSection.classList.toggle("is-collapsed", !isVisible);
    licensesSection.setAttribute("aria-hidden", isVisible ? "false" : "true");
    if (isVisible) {
      licensesSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function applyLanguage(langCode) {
    const normalized = SUPPORTED_LANGS.includes(langCode) ? langCode : "en";
    const translation = translationsByLang[normalized] || translationsByLang.en;
    if (!translation) return;

    currentLang = normalized;
    currentTranslation = translation;

    applyMeta(translation);
    applyStaticText(translation);

    if (topLangToggle) {
      topLangToggle.textContent = getByPath(translation, "header.lang_button_label", normalized.toUpperCase());
      const langAria = getByPath(translation, "header.lang_toggle_aria", "Switch language");
      topLangToggle.setAttribute("aria-label", langAria);
      topLangToggle.title = getByPath(translation, "header.lang_toggle_title", langAria);
    }
    setLangButtonsActive(normalized);

    applyTheme(heroPreview && heroPreview.dataset.themeId ? heroPreview.dataset.themeId : "default");
    syncHeroState();
    setDownloadHint(selectedDownloadOs);
    setTopDownloadTitle(topDownloadTargetOs);
  }

  async function preloadTranslations() {
    await Promise.all(SUPPORTED_LANGS.map(async function (langCode) {
      const response = await fetch("i18n/" + langCode + ".json", { cache: "no-store" });
      if (!response.ok) {
        throw new Error("Failed to load i18n/" + langCode + ".json");
      }
      translationsByLang[langCode] = await response.json();
    }));
  }

  createWave(heroWave);
  setLicensesVisible(false);

  themeButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      applyTheme(button.dataset.themeId);
      setThemeDropdownOpen(false);
    });
  });

  if (headerThemeTrigger) {
    headerThemeTrigger.addEventListener("click", function () {
      const shouldOpen = !headerThemeDropdown || !headerThemeDropdown.classList.contains("is-open");
      setThemeDropdownOpen(shouldOpen);
    });
  }

  document.addEventListener("click", function (event) {
    if (headerThemeDropdown && !headerThemeDropdown.contains(event.target)) {
      setThemeDropdownOpen(false);
    }
    if (topLangDropdown && !topLangDropdown.contains(event.target)) {
      setLangDropdownOpen(false);
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      setThemeDropdownOpen(false);
      setLangDropdownOpen(false);
    }
  });

  if (heroRecordBtn) {
    heroRecordBtn.addEventListener("click", function () {
      setRecording(!recording);
    });
  }

  if (heroRecordToggle) {
    heroRecordToggle.addEventListener("click", function () {
      setRecording(!recording);
    });
  }

  if (heroCancelBtn) {
    heroCancelBtn.addEventListener("click", function () {
      seconds = 0;
      setRecording(false);
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (event) {
      const hash = link.getAttribute("href") || "";
      if (!hash || hash === "#") return;
      const navigated = scrollByHash(hash);
      if (!navigated) return;
      event.preventDefault();
      if (window.location.hash !== hash) {
        history.pushState(null, "", hash);
      }
    });
  });

  document.querySelectorAll('[data-action="scroll-controls"]').forEach(function (button) {
    button.addEventListener("click", function () {
      scrollByHash("#controls");
    });
  });

  document.querySelectorAll('[data-action="toggle-license"]').forEach(function (button) {
    button.addEventListener("click", function () {
      const currentlyHidden = licensesSection && licensesSection.classList.contains("is-collapsed");
      setLicensesVisible(currentlyHidden);
    });
  });

  document.querySelectorAll('[data-action="hide-license"]').forEach(function (button) {
    button.addEventListener("click", function () {
      setLicensesVisible(false);
    });
  });

  downloadCards.forEach(function (card) {
    card.addEventListener("click", function () {
      const osId = card.dataset.downloadOs || "";
      markDownloadCard(osId);
      setDownloadHint(osId);
    });
  });

  if (topDownloadBtn) {
    const currentOS = detectCurrentOS();
    topDownloadTargetOs = currentOS === "macos" || currentOS === "windows" ? currentOS : "linux";
    topDownloadBtn.addEventListener("click", function () {
      downloadByOS(topDownloadTargetOs);
    });
  }

  if (topLangDropdown) {
    topLangDropdown.addEventListener("mouseenter", function () {
      setLangDropdownOpen(true);
    });
    topLangDropdown.addEventListener("mouseleave", function () {
      setLangDropdownOpen(false);
    });
  }

  if (topLangToggle) {
    topLangToggle.addEventListener("click", function () {
      const shouldOpen = !topLangDropdown || !topLangDropdown.classList.contains("is-open");
      setLangDropdownOpen(shouldOpen);
    });
  }

  langButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const langId = button.dataset.langId || "en";
      applyLanguage(langId);
      setLangDropdownOpen(false);
    });
  });

  preloadTranslations()
    .then(function () {
      applyLanguage("en");
      if (window.location.hash) {
        setTimeout(function () {
          scrollByHash(window.location.hash);
        }, 0);
      }
    })
    .catch(function (error) {
      console.error("Landing i18n load failed:", error);
      currentTranslation = null;
      applyTheme("default");
      syncHeroState();
      setDownloadHint("");
      setTopDownloadTitle(topDownloadTargetOs);
    });

  setInterval(function () {
    if (recording) {
      seconds += 1;
    }
    syncHeroState();
  }, 1000);
})();
