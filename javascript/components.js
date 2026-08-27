import {
  background_switcher_svg_path,
  sidebar_theme_css,
  topbar_theme_css,
  contentbody_css,
} from "./paths.js"

{
  const savedtheme = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", savedtheme)
}

class DocTopBar extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <header class = "topbar">
          <div class = "project-display">
              <span class="project-name">Project Name</span> <!--add this, remove it, idc -->
          </div> <!-- project logo/name -->
          <div class = "git-status-display"></div> <!-- what git commit is this, and possibly run a command -->
          <div class = "global-search"></div> <!-- like ctrl + f, but searches every page -->
          <div class = "hyper-links">
            <button class="hyper-link-button" onclick="window.open('https://github.com/Predret/generic-doc-thingy', '_blank')"><span class="repo-link">Download docs</span></button>
          </div> <!-- for example to the git repo -->
      </header>
      `;
  }
}
class DocSideBar extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <aside class = "sidebar">
          <div class = "page-browser"></div> <!-- like, file system looking thingy -->
          <div class = "theme-mode">
          <button id = theme_button class=theme_switch_button><img src="${background_switcher_svg_path}" class="theme_switch"></button>
          </div> <!--light/dark mode-->
      </aside>
      `;
    const themeButton = this.querySelector("#theme_button");

    themeButton.addEventListener("click", () => {
      const html = document.documentElement;
      const currentTheme = html.getAttribute("data-theme");

      const newTheme =
        currentTheme === "dark" ? "light" : "dark";

      html.setAttribute("data-theme", newTheme);
      localStorage.setItem("theme", newTheme);
    });
  }
}
class DocLayoutCSS extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <link rel="stylesheet" href = "${sidebar_theme_css}">
      <link rel="stylesheet" href = "${topbar_theme_css}">
      <link rel="stylesheet" href = "${contentbody_css}">
      `;
  }
}
class DocTitle extends HTMLElement {
  connectedCallback() {
    setTimeout(() => {
      const customPageName = this.innerHTML.trim() || "documentation"
      document.title = `documentation title, page: ${customPageName}`;
      this.innerHTML = ``;
    }, 0);
  }
}
class DocHeader extends HTMLElement {
  connectedCallback() {
    const name = this.getAttribute("name") || "";
    if (!name.trim()) { throw new Error("DocHeader requires a name. Use a normal header instead.")}
    let size = Number(this.getAttribute("size") || 1);
    if (!Number.isInteger(size) || size < 1  || size > 6) { throw new Error("DocHeader has an invalid size. (1-6)"); }
    const inputInnerHTML = this.innerHTML
    this.innerHTML = `
      <h${size} id="${name}" class="maintext">${inputInnerHTML}</h${size}>
      `
  }
}

customElements.define('doc-topbar', DocTopBar);
customElements.define('doc-sidebar', DocSideBar);
customElements.define('doc-layout-css', DocLayoutCSS);
customElements.define('doc-title', DocTitle);
customElements.define('doc-header', DocHeader);
