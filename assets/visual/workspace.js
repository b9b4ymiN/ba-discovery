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
  const v2 = data.schema_version === 2;
  const tabs = document.getElementById("view-tabs");
  const panels = [];
  const selectTab = (tab) => {
    for (const panel of panels) panel.node.hidden = panel.tab !== tab;
    for (const button of tabs.querySelectorAll("button")) button.setAttribute("aria-pressed", String(button.dataset.tab === tab));
  };
  for (const diagram of data.diagrams) {
    const card = el("article", undefined, "card");
    card.append(el("h2", diagram.title), el("p", diagram.description));
    if (v2) {
      card.append(el("p", diagram.status + " · " + diagram.level + " · " + diagram.phase + " · " + diagram.kind, "meta"));
      if (diagram.stale) card.append(el("p", "STALE — previous context; do not rely on this view as current.", "notice"));
      else if (diagram.retained) card.append(el("p", "Retained view — not reviewed in this turn.", "meta"));
      if (diagram.status === "APPROVED") card.append(el("p", "Approved-source label; verify the actual approved scope. This workspace is not approval.", "meta"));
      card.append(el("p", "Question: " + diagram.question));
      card.append(el("p", "Why this visual: " + diagram.selection_reason, "meta"));
      if (diagram.change_summary) card.append(el("p", "Update: " + diagram.change_summary, "meta"));
    }
    card.append(el("p", "References: " + (diagram.references.join(", ") || "none / illustrative"), "meta"));
    if (v2 && diagram.columns) {
      const wrapper = el("div", undefined, "table-wrap");
      const table = el("table");
      const head = el("thead"), tr = el("tr"), body = el("tbody");
      for (const col of diagram.columns) { const th = el("th", col); th.scope = "col"; tr.append(th); }
      head.append(tr); table.append(head);
      for (const row of diagram.rows) { const line = el("tr"); for (const cell of row) line.append(el("td", cell)); body.append(line); }
      table.append(body); wrapper.append(table); card.append(wrapper);
    } else {
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
    }
    if (v2) {
      const questions = el("ul");
      for (const question of diagram.open_questions) questions.append(el("li", question));
      if (questions.childElementCount) card.append(el("h3", "Open questions"), questions);
      const trace = el("details");
      const list = el("ul");
      for (const source of diagram.sources) list.append(el("li", source.path + " — SHA-256 " + source.sha256));
      if (!list.childElementCount) list.append(el("li", "No declared source; illustrative or unverified."));
      trace.append(el("summary", "Evidence fingerprints"), list);
      card.append(trace);
      panels.push({node: card, tab: diagram.tab});
    }
    section.append(card);
  }
  if (v2) {
    document.getElementById("source-section").hidden = true;
    const focus = data.diagrams.find(d => d.visual_id === data.focus_id);
    document.getElementById("focus").textContent = focus ? "Current focus: " + focus.question : "";
    for (const tab of ["Process", "System", "Data", "Rules", "Review"]) {
      if (!panels.some(panel => panel.tab === tab)) continue;
      const button = el("button", tab);
      button.type = "button"; button.dataset.tab = tab;
      button.addEventListener("click", () => selectTab(tab));
      tabs.append(button);
    }
    selectTab(focus ? focus.tab : panels[0]?.tab);
  }
})();
