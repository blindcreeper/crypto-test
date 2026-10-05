(() => {
  document.querySelectorAll(".doc-content section[id] > .panel-head h2, .doc-content #sub-heading").forEach(heading => {
    const section = heading.closest("section[id]");
    if (!section || heading.querySelector(".headerlink")) return;
    const anchor = document.createElement("a");
    anchor.className = "headerlink";
    anchor.href = `#${section.id}`;
    anchor.textContent = "¶";
    anchor.setAttribute("aria-label", `链接到“${heading.textContent.trim()}”`);
    heading.append(anchor);
  });
})();
