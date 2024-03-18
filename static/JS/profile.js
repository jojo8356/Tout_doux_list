function toggleHiddenContent(clickableElement, hiddenElement) {
  if (!clickableElement || !hiddenElement) {
    console.error('Les éléments spécifiés ne peuvent pas être trouvés.');
    return;
  }

  clickableElement.addEventListener("click", function() {
    hiddenElement.style.display = (hiddenElement.style.display === "none") ? "block" : "none";
  });
}
var clickableElement = document.querySelector("img.profile");
var hiddenElement = document.querySelector("ul.menu-profile");
hiddenElement.style.display = "none";
toggleHiddenContent(clickableElement, hiddenElement);