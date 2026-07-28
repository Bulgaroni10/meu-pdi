(() => {
  const root = document.documentElement;
  const shell = document.getElementById("appShell");
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebarBackdrop");
  const mobileMenu = document.getElementById("mobileMenu");
  const collapse = document.getElementById("sidebarCollapse");
  const themeToggle = document.getElementById("themeToggle");
  const globalSearchInput = document.getElementById("globalSearchInput");

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
})();
