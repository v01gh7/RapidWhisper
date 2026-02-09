(function () {
  const THEME_NOTES = {
    default: "Default: универсальная тема для повседневной работы.",
    ocean: "Ocean: прохладная палитра для спокойной концентрации.",
    dusk: "Dusk: вечерний контраст с мягкими акцентами.",
    retro: "Retro: теплый ретро-градиент и ламповая атмосфера.",
    neo: "Neo: неоновый стиль с ярким контрастом.",
    lime: "Lime: энергичный зеленый акцент и высокий визуальный тонус.",
    terminal: "Terminal Theme: современная CLI-эстетика с зеленым терминальным свечением.",
  };

  const THEME_APPS = {
    default: "VS Code",
    ocean: "Google Docs",
    dusk: "Notion",
    retro: "Obsidian",
    neo: "Telegram Desktop",
    lime: "LibreOffice Writer",
    terminal: "Windows Terminal",
  };

  const heroWave = document.getElementById("hero-wave");
  const heroPreview = document.getElementById("hero-preview");
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

  const controlsSection = document.getElementById("controls");
  const licensesSection = document.getElementById("licenses");
  const downloadHint = document.getElementById("download-hint");
  const downloadCards = document.querySelectorAll(".platform-icon-card[data-download-os]");

  let recording = true;
  let seconds = 11;
  const DOWNLOAD_LINKS = {
    windows: "../../dist/RapidWhisper.exe",
    macos: "https://github.com/v01gh7/RapidWhisper/releases/latest",
    linux: "https://github.com/v01gh7/RapidWhisper/releases/latest",
  };

  function createWave(container) {
    if (!container || container.dataset.waveReady === "1") return;
    container.dataset.waveReady = "1";
    const fragment = document.createDocumentFragment();
    for (let i = 0; i < 44; i += 1) {
      const bar = document.createElement("span");
      bar.className = "bar";
      bar.style.setProperty("--i", String(i));
      bar.style.height = `${9 + Math.round(Math.random() * 26)}px`;
      fragment.appendChild(bar);
    }
    container.appendChild(fragment);
  }

  function animateWave(container, isRecording) {
    if (!container) return;
    const bars = container.querySelectorAll(".bar");
    bars.forEach((bar, idx) => {
      const min = isRecording ? 10 : 6;
      const max = isRecording ? 38 : 12;
      const emphasis = isRecording && idx > 16 && idx < 30 ? 9 : 0;
      const next = min + Math.round(Math.random() * (max - min + emphasis));
      bar.style.height = `${next}px`;
    });
  }

  function formatTime(totalSeconds) {
    const mm = Math.floor(totalSeconds / 60).toString().padStart(2, "0");
    const ss = (totalSeconds % 60).toString().padStart(2, "0");
    return `${mm}:${ss}`;
  }

  function syncHeroState() {
    if (!heroState || !heroTime) return;
    if (recording) {
      heroState.textContent = "Запись...";
      heroTime.textContent = formatTime(seconds);
      if (heroRecordBtn) heroRecordBtn.textContent = "Пауза";
      if (heroRecordToggle) heroRecordToggle.textContent = "Пауза записи";
    } else {
      heroState.textContent = "Ожидание";
      heroTime.textContent = "00:00";
      if (heroRecordBtn) heroRecordBtn.textContent = "Запись";
      if (heroRecordToggle) heroRecordToggle.textContent = "Старт записи";
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
    const platform = `${uaDataPlatform} ${navigator.platform || ""}`.toLowerCase();
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
    const labels = {
      windows: "Windows (.exe)",
      macos: "macOS (.dmg)",
      linux: "Linux (.AppImage)",
    };
    if (labels[osId]) {
      downloadHint.textContent = `Выбрано: ${labels[osId]}.`;
    }
  }

  function markDownloadCard(osId) {
    downloadCards.forEach((card) => {
      card.classList.toggle("is-active", card.dataset.downloadOs === osId);
    });
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

  function applyTheme(themeId) {
    const id = themeId || "default";
    document.body.dataset.pageTheme = id;
    if (heroPreview) {
      heroPreview.dataset.themeId = id;
    }
    if (heroAppName && THEME_APPS[id]) {
      heroAppName.textContent = THEME_APPS[id];
    }
    if (themeNote && THEME_NOTES[id]) {
      themeNote.textContent = THEME_NOTES[id];
    }
    themeButtons.forEach((button) => {
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

  createWave(heroWave);
  syncHeroState();
  applyTheme("default");
  setLicensesVisible(false);

  themeButtons.forEach((button) => {
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
    if (!headerThemeDropdown) return;
    if (!headerThemeDropdown.contains(event.target)) {
      setThemeDropdownOpen(false);
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      setThemeDropdownOpen(false);
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

  document.querySelectorAll('[data-action="scroll-controls"]').forEach((button) => {
    button.addEventListener("click", function () {
      if (controlsSection) {
        controlsSection.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  document.querySelectorAll('[data-action="toggle-license"]').forEach((button) => {
    button.addEventListener("click", function () {
      const currentlyHidden = licensesSection && licensesSection.classList.contains("is-collapsed");
      setLicensesVisible(currentlyHidden);
    });
  });

  document.querySelectorAll('[data-action="hide-license"]').forEach((button) => {
    button.addEventListener("click", function () {
      setLicensesVisible(false);
    });
  });

  downloadCards.forEach((card) => {
    card.addEventListener("click", function () {
      const osId = card.dataset.downloadOs || "";
      markDownloadCard(osId);
      setDownloadHint(osId);
    });
  });

  if (topDownloadBtn) {
    const currentOS = detectCurrentOS();
    const forTopButton = currentOS === "macos" || currentOS === "windows" ? currentOS : "linux";
    topDownloadBtn.title = forTopButton === "macos"
      ? "Скачать для macOS"
      : forTopButton === "windows"
        ? "Скачать для Windows"
        : "Открыть загрузки";
    topDownloadBtn.addEventListener("click", function () {
      downloadByOS(forTopButton);
    });
  }

  setInterval(function () {
    if (recording) {
      seconds += 1;
    }
    syncHeroState();
  }, 1000);
})();
