class DevTopBar extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <header class = "topbar">
          <div class = "project-display"></div> <!-- project logo/name -->
          <div class = "git-status-display"></div> <!-- what git commit is this, and possibly run a command -->
          <div class = "global-search"></div> <!-- like ctrl + f, but searches every page -->
          <div class = "hyper-links"></div> <!-- for example to the git repo -->
      </header>
      `;
  }
}
class DevSideBar extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <aside class = "sidebar">
          <div class = "page-browser"></div> <!-- like, file system looking thingy -->
          <div class = "theme-mode">
          </div> <!--light/dark mode-->
      </aside>
      `;
  }
}
class DevLayoutCSS extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <link rel="stylesheet" href = "css/sidebar.css">
      <link rel="stylesheet" href = "css/topbar.css">
      <link rel="stylesheet" href = "css/contentbody.css">
      `;
  }
}
class DevTitle extends HTMLElement {
  connectedCallback() {
    setTimeout(() => {
      const customPageName = this.innerHTML.trim() || "documentation"
      document.title = `documentation title, page: ${customPageName}`;
      this.innerHTML = ``;
    }, 0);
  }
}
customElements.define('dev-topbar', DevTopBar)
customElements.define('dev-sidebar', DevSideBar)
customElements.define('dev-layout-css', DevLayoutCSS)
customElements.define('dev-title', DevTitle)
