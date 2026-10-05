(() => {
  const fields = ["long-return", "short-return", "cost-return"].map(id => document.getElementById(id));
  const result = document.getElementById("calc-result");
  const presets = [...document.querySelectorAll(".calc-presets button")];

  function updateCalculator() {
    const [longReturn, shortReturn, cost] = fields.map(field => Number(field.value));
    if (fields.some(field => field.value.trim() === "") ||
        ![longReturn, shortReturn, cost].every(Number.isFinite)) {
      result.innerHTML = "<strong>请输入有效数字</strong><span>请填写两组价格变化和净费用。</span>";
      return;
    }
    const spread = longReturn - shortReturn;
    const longLeg = .45 * longReturn;
    const shortLeg = -.45 * shortReturn;
    const net = longLeg + shortLeg - cost;
    const amount = n => Math.abs(n).toFixed(Math.abs(n) < .1 ? 4 : 2);
    const signed = n => (n >= 0 ? "+" : "−") + amount(n);
    const expense = cost >= 0
      ? `扣净费用 ${amount(cost)} USDT`
      : `加净收入 ${amount(cost)} USDT`;
    result.innerHTML = `<strong>${signed(net)} USDT</strong><span>每 100 USDT 权益：多头持仓 ${signed(longLeg)} USDT，空头持仓 ${signed(shortLeg)} USDT，${expense}。两组币价差（做多币 − 做空币）为 ${signed(spread)} 个百分点。</span>`;
  }

  fields.forEach(field => field.addEventListener("input", () => {
    presets.forEach(button => button.setAttribute("aria-pressed", "false"));
    updateCalculator();
  }));
  presets.forEach((button, index) => {
    button.setAttribute("aria-pressed", index === 0 ? "true" : "false");
    button.addEventListener("click", () => {
      fields[0].value = button.dataset.long;
      fields[1].value = button.dataset.short;
      presets.forEach(preset => preset.setAttribute("aria-pressed", String(preset === button)));
      updateCalculator();
    });
  });
  updateCalculator();

  const toggle = document.getElementById("theme-toggle");
  function updateToggle() {
    const dark = document.documentElement.dataset.theme === "dark";
    toggle.textContent = dark ? "☀" : "◐";
    toggle.setAttribute("aria-pressed", String(dark));
    toggle.setAttribute("aria-label", dark ? "切换为浅色模式" : "切换为深色模式");
  }
  toggle.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("strategy-docs-theme", next); } catch {}
    updateToggle();
  });
  updateToggle();

  const links = [...document.querySelectorAll(".sidebar a[href^='#'], .page-toc a[href^='#'], .mobile-nav a[href^='#']")];
  const targets = [...new Set(links.map(link => link.getAttribute("href")))]
    .map(hash => document.querySelector(hash)).filter(Boolean);
  let scheduled = false;
  function syncNavigation() {
    let current = "thesis";
    let best = -Infinity;
    for (const target of targets) {
      const top = target.getBoundingClientRect().top;
      if (top <= 160 && top > best) {
        best = top;
        current = target.id;
      }
    }
    if (window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2) {
      const last = targets.reduce((latest, target) =>
        !latest || target.getBoundingClientRect().top > latest.getBoundingClientRect().top
          ? target : latest, null);
      if (last) current = last.id;
    }
    links.forEach(link => {
      const active = link.getAttribute("href") === "#" + current;
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
    scheduled = false;
  }
  window.addEventListener("scroll", () => {
    if (!scheduled) { scheduled = true; requestAnimationFrame(syncNavigation); }
  }, { passive: true });
  window.addEventListener("hashchange", syncNavigation);
  syncNavigation();
})();

(() => {
  document.querySelectorAll("pre.code-example, pre.highlight").forEach(pre => {
    if (pre.closest(".code-block")) return;
    const holder = document.createElement("div");
    holder.className = "code-block";
    pre.parentNode.insertBefore(holder, pre);
    holder.append(pre);
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy-btn";
    button.textContent = "复制";
    button.setAttribute("aria-label", "复制代码");
    button.setAttribute("aria-live", "polite");
    let resetTimer;
    button.addEventListener("click", async () => {
      const text = (pre.querySelector("code") || pre).innerText.replace(/\n+$/, "");
      try {
        let copied = false;
        if (navigator.clipboard?.writeText) {
          try { await navigator.clipboard.writeText(text); copied = true; } catch {}
        }
        if (!copied) {
          const field = document.createElement("textarea");
          field.value = text;
          field.style.position = "fixed";
          field.style.opacity = "0";
          document.body.append(field);
          field.select();
          copied = document.execCommand("copy");
          field.remove();
          if (!copied) throw new Error("copy failed");
        }
        button.textContent = "已复制";
        button.classList.add("copied");
      } catch {
        button.textContent = "复制失败";
        button.classList.remove("copied");
      }
      clearTimeout(resetTimer);
      resetTimer = setTimeout(() => {
        button.textContent = "复制";
        button.classList.remove("copied");
      }, 1600);
    });
    holder.append(button);
  });

  const h1 = document.querySelector(".content h1");
  if (h1 && !h1.id) h1.id = "top";
  let headingNumber = 0;
  document.querySelectorAll(".content h2, .content h3").forEach(heading => {
    if (heading.querySelector(".headerlink")) return;
    if (!heading.id) {
      do { headingNumber += 1; } while (document.getElementById(`heading-${headingNumber}`));
      heading.id = `heading-${headingNumber}`;
    }
    const anchor = document.createElement("a");
    anchor.className = "headerlink";
    anchor.href = `#${heading.id}`;
    anchor.textContent = "¶";
    anchor.setAttribute("aria-label", `链接到“${heading.textContent.trim()}”`);
    heading.append(anchor);
  });

  const footer = document.querySelector(".content > footer");
  if (footer && !footer.dataset.enhanced) {
    footer.dataset.enhanced = "1";
    const note = document.createElement("p");
    note.className = "footer-note";
    while (footer.firstChild) note.append(footer.firstChild);
    const nav = document.createElement("nav");
    nav.className = "footer-links";
    nav.setAttribute("aria-label", "页脚");
    nav.innerHTML = '<a href="#top">策略介绍</a><a href="#sources">研究资料</a><a href="#top">返回顶部 ↑</a>';
    footer.append(nav, note);
  }

  const top = document.createElement("button");
  top.type = "button";
  top.className = "to-top";
  top.textContent = "返回顶部";
  top.setAttribute("aria-label", "返回顶部");
  top.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth"
    });
  });
  document.body.append(top);
  let scrollScheduled = false;
  function updateBackToTop() {
    top.classList.toggle("show", window.scrollY > 600);
    scrollScheduled = false;
  }
  window.addEventListener("scroll", () => {
    if (!scrollScheduled) {
      scrollScheduled = true;
      requestAnimationFrame(updateBackToTop);
    }
  }, { passive: true });
  updateBackToTop();
})();
