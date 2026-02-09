(function () {
  const THEME_NOTES = {
    default: "Default: универсальная тема для длительной работы и чистой читаемости.",
    ocean: "Ocean: прохладный сине-бирюзовый стиль для спокойного фокуса.",
    dusk: "Dusk: вечерний контраст с мягкими фиолетово-розовыми акцентами.",
    retro: "Retro: теплый ретро-градиент с ламповым оттенком интерфейса.",
    neo: "Neo: неоновый high-contrast стиль для динамичного рабочего ритма.",
    lime: "Lime: энергичная зелено-лаймовая тема с яркой индикацией.",
    terminal: "Terminal Theme: современная CLI-эстетика с зелёным терминальным светом.",
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
      const emphasis = isRecording && idx > 16 && idx < 30 ? 10 : 0;
      const next = min + Math.round(Math.random() * (max - min + emphasis));
      bar.style.height = `${next}px`;
    });
  }

  const heroWave = document.getElementById("hero-wave");
  const themeWave = document.getElementById("theme-wave");
  createWave(heroWave);
  createWave(themeWave);

  let recording = true;
  let seconds = 11;
  const heroState = document.getElementById("hero-state");
  const heroTime = document.getElementById("hero-time");
  const heroRecordBtn = document.getElementById("hero-record-btn");
  const heroCancelBtn = document.getElementById("hero-cancel-btn");

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
    } else {
      heroState.textContent = "Ожидание";
      heroTime.textContent = "00:00";
      if (heroRecordBtn) heroRecordBtn.textContent = "Запись";
    }
    animateWave(heroWave, recording);
  }

  if (heroRecordBtn) {
    heroRecordBtn.addEventListener("click", function () {
      recording = !recording;
      if (recording && seconds === 0) seconds = 1;
      syncHeroState();
    });
  }

  if (heroCancelBtn) {
    heroCancelBtn.addEventListener("click", function () {
      recording = false;
      seconds = 0;
      syncHeroState();
    });
  }

  setInterval(function () {
    if (recording) {
      seconds += 1;
    }
    syncHeroState();
    animateWave(themeWave, true);
  }, 1000);

  syncHeroState();

  const themePreview = document.getElementById("theme-preview");
  const themeNote = document.getElementById("theme-note");
  const themeAppName = document.getElementById("theme-app-name");
  const heroAppName = document.getElementById("hero-app-name");
  const themeButtons = document.querySelectorAll(".theme-btn");

  function applyTheme(themeId) {
    if (!themePreview) return;
    themePreview.dataset.themeId = themeId;
    document.body.dataset.pageTheme = themeId;

    if (themeNote && THEME_NOTES[themeId]) {
      themeNote.textContent = THEME_NOTES[themeId];
    }
    if (themeAppName && THEME_APPS[themeId]) {
      themeAppName.textContent = THEME_APPS[themeId];
    }
    if (heroAppName && THEME_APPS[themeId]) {
      heroAppName.textContent = THEME_APPS[themeId];
    }

    themeButtons.forEach((btn) => {
      btn.classList.toggle("is-active", btn.dataset.themeId === themeId);
    });
  }

  themeButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const themeId = btn.dataset.themeId || "default";
      applyTheme(themeId);
    });
  });

  const themeActionButtons = document.querySelectorAll(".theme-window .chip");
  themeActionButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const isRecord = btn.classList.contains("chip-record");
      animateWave(themeWave, isRecord);
    });
  });

  applyTheme("default");
})();
