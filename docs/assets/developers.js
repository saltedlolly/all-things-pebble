/* Sort and filter the watchfaces and apps on each developer's page.
   document$ fires on every page load, including the theme's instant
   navigation between pages. */
document$.subscribe(function () {
  var controls = document.querySelector(".dev-controls");
  var grid = document.querySelector(".dev-apps");
  if (!controls || !grid) return;
  var cards = Array.prototype.slice.call(grid.querySelectorAll(".app-card"));
  var buttons = controls.querySelectorAll("[data-filter]");
  var select = controls.querySelector("select");
  var filter = "all";

  function byTitle(a, b) {
    return a.dataset.title.localeCompare(b.dataset.title, undefined, { numeric: true, sensitivity: "base" });
  }

  function apply() {
    var key = select.value;
    cards.slice().sort(function (a, b) {
      if (key === "title") return byTitle(a, b);
      // Newest first; apps without a date go last
      var x = a.dataset[key] || "", y = b.dataset[key] || "";
      return x === y ? byTitle(a, b) : (x < y ? 1 : -1);
    }).forEach(function (card) {
      card.hidden = filter !== "all" && card.dataset.type !== filter;
      grid.appendChild(card);
    });
  }

  Array.prototype.forEach.call(buttons, function (button) {
    button.addEventListener("click", function () {
      filter = button.dataset.filter;
      Array.prototype.forEach.call(buttons, function (b) {
        b.setAttribute("aria-pressed", String(b === button));
      });
      apply();
    });
  });
  select.addEventListener("change", apply);
  controls.hidden = false;
});
