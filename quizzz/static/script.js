document.addEventListener("DOMContentLoaded", () => {
  document
    .querySelectorAll(".momentjs-date")
    .forEach(dateEl => jsFuncs.renderMomentDate(dateEl));
});