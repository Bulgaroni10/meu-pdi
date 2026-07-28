(() => {
  const root = document.documentElement;
  const shell = document.getElementById("appShell");
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebarBackdrop");
  const mobileMenu = document.getElementById("mobileMenu");
  const collapse = document.getElementById("sidebarCollapse");
  const themeToggle = document.getElementById("themeToggle");
  const globalSearchInput = document.getElementById("globalSearchInput");
  const timerLauncher = document.getElementById("studyTimerLauncher");
  const timerPanel = document.getElementById("studyTimerPanel");
  const timerClose = document.getElementById("studyTimerClose");
  const timerDisplay = document.getElementById("studyTimerDisplay");
  const timerToggle = document.getElementById("studyTimerToggle");
  const timerReset = document.getElementById("studyTimerReset");

  const updateThemeIcon = () => {
    if (!themeToggle) return;
    const dark = root.dataset.bsTheme === "dark";
    themeToggle.innerHTML = `<i class="bi ${dark ? "bi-sun" : "bi-moon-stars"}" aria-hidden="true"></i>`;
    themeToggle.setAttribute("aria-label", dark ? "Ativar tema claro" : "Ativar tema escuro");
  };

  themeToggle?.addEventListener("click", () => {
    const next = root.dataset.bsTheme === "dark" ? "light" : "dark";
    root.dataset.bsTheme = next;
    localStorage.setItem("meu-pdi-theme", next);
    updateThemeIcon();
  });

  const closeMobileMenu = () => {
    sidebar?.classList.remove("mobile-open");
    backdrop?.classList.remove("show");
    mobileMenu?.setAttribute("aria-expanded", "false");
    document.body.classList.remove("nav-open");
  };

  mobileMenu?.addEventListener("click", () => {
    const open = !sidebar?.classList.contains("mobile-open");
    sidebar?.classList.toggle("mobile-open", open);
    backdrop?.classList.toggle("show", open);
    mobileMenu.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("nav-open", open);
  });
  backdrop?.addEventListener("click", closeMobileMenu);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMobileMenu();
    const editing =
      event.target instanceof HTMLInputElement ||
      event.target instanceof HTMLTextAreaElement ||
      event.target instanceof HTMLSelectElement ||
      event.target?.isContentEditable;
    if (event.key === "/" && !editing && globalSearchInput) {
      event.preventDefault();
      globalSearchInput.focus();
      globalSearchInput.select();
    }
  });

  const collapsed = localStorage.getItem("meu-pdi-sidebar") === "collapsed";
  shell?.classList.toggle("sidebar-collapsed", collapsed);
  collapse?.setAttribute("aria-expanded", String(!collapsed));

  collapse?.addEventListener("click", () => {
    const next = !shell.classList.contains("sidebar-collapsed");
    shell.classList.toggle("sidebar-collapsed", next);
    collapse.setAttribute("aria-expanded", String(!next));
    collapse.setAttribute("aria-label", next ? "Expandir menu" : "Recolher menu");
    localStorage.setItem("meu-pdi-sidebar", next ? "collapsed" : "expanded");
  });

  updateThemeIcon();

  const TIMER_KEY = "meu-pdi-study-timer";
  let timerState = { elapsed: 0, startedAt: null };
  try {
    timerState = { ...timerState, ...JSON.parse(localStorage.getItem(TIMER_KEY) || "{}") };
  } catch {
    localStorage.removeItem(TIMER_KEY);
  }

  const elapsedSeconds = () => {
    const running = timerState.startedAt
      ? Math.max(0, Math.floor((Date.now() - timerState.startedAt) / 1000))
      : 0;
    return Math.max(0, Number(timerState.elapsed) || 0) + running;
  };

  const formatTimer = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remaining = seconds % 60;
    return [hours, minutes, remaining].map((value) => String(value).padStart(2, "0")).join(":");
  };

  const saveTimer = () => localStorage.setItem(TIMER_KEY, JSON.stringify(timerState));
  const renderTimer = () => {
    if (!timerDisplay || !timerToggle) return;
    timerDisplay.textContent = formatTimer(elapsedSeconds());
    const running = Boolean(timerState.startedAt);
    timerToggle.innerHTML = running
      ? '<i class="bi bi-pause-fill"></i><span>Pausar</span>'
      : '<i class="bi bi-play-fill"></i><span>Iniciar</span>';
    timerLauncher?.classList.toggle("running", running);
  };

  const setTimerPanel = (open) => {
    if (!timerPanel || !timerLauncher) return;
    timerPanel.hidden = !open;
    timerLauncher.setAttribute("aria-expanded", String(open));
  };

  timerLauncher?.addEventListener("click", () => setTimerPanel(timerPanel.hidden));
  timerClose?.addEventListener("click", () => setTimerPanel(false));
  timerToggle?.addEventListener("click", () => {
    if (timerState.startedAt) {
      timerState.elapsed = elapsedSeconds();
      timerState.startedAt = null;
    } else {
      timerState.startedAt = Date.now();
    }
    saveTimer();
    renderTimer();
  });
  timerReset?.addEventListener("click", () => {
    if (!window.confirm("Zerar o cronômetro desta sessão?")) return;
    timerState = { elapsed: 0, startedAt: null };
    saveTimer();
    renderTimer();
  });
  window.setInterval(renderTimer, 1000);
  renderTimer();
})();
