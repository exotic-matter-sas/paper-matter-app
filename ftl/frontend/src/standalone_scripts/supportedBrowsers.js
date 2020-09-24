const Bowser = require("bowser");

const browser = Bowser.getParser(window.navigator.userAgent);
// /!\ Keep in sync with packages.json > browserslist
const isValidBrowser = browser.satisfies({
  chrome: ">=80",
  chromium: ">=80",
  firefox: ">=78",
  safari: ">=12",
  opera: ">=70",
  edge: ">=80",
});

window.addEventListener("DOMContentLoaded", (event) => {
  // If user doesn't already set the cookie to ignore the warning
  if (
    !document.cookie
      .split(";")
      .some((item) => item.trim().startsWith("ignore_browser_warning="))
  ) {
    if (isValidBrowser === false) {
      document
        .querySelector("#unsupported-browser-version-warning")
        .classList.remove("d-none");
    } else if (isValidBrowser === undefined) {
      document
        .querySelector("#unsupported-browser-warning")
        .classList.remove("d-none");
    }
  }
});
