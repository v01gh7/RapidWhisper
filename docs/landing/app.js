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

  const controlsSection = document.getElementById("controls");
  const licensesSection = document.getElementById("licenses");

  let recording = true;
  let seconds = 11;

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
    });
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

  setInterval(function () {
    if (recording) {
      seconds += 1;
    }
    syncHeroState();
  }, 1000);
})();
