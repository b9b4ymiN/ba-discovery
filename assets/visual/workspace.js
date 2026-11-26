(() => {
  "use strict";
  const data = JSON.parse(document.getElementById("ba-data").textContent);
  const el = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  document.getElementById("title").textContent = data.title;
  document.getElementById("summary").textContent = data.summary;
  document.getElementById("meta").textContent = "Phase: " + data.phase + " | Pele " + data.pele_version;
  const sources = document.getElementById("sources");
  for (const source of data.sources) sources.append(el("li", source.path + " — SHA-256 " + source.sha256));
  if (!data.sources.length) sources.append(el("li", "No project sources declared. Illustrative draft only."));
  const section = document.getElementById("diagrams");
  for (const diagram of data.diagrams) {
    const card = el("article", undefined, "card");
    card.append(el("h2", diagram.title), el("p", diagram.description));
    card.append(el("p", "References: " + (diagram.references.join(", ") || "none / illustrative"), "meta"));
    try {
      const result = window.pele.render(diagram.source);
      if (typeof result.svg !== "string" || !result.svg.trim()) throw new Error("Renderer returned no SVG");
      // SVG is an inert image rather than injected DOM. Never interpret input as HTML.
      const img = el("img");
      img.alt = diagram.title;
      img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(result.svg);
      img.addEventListener("error", () => {
        img.remove();
        card.prepend(el("p", "SVG could not be displayed; see source below.", "error"));
      });
      card.append(img);
    } catch (error) {
      card.append(el("p", "Diagram render failed: " + String(error.message || error), "error"));
    }
    const details = el("details");
    details.append(el("summary", "Diagram source"), el("pre", diagram.source));
    card.append(details);
    section.append(card);
  }
})();
