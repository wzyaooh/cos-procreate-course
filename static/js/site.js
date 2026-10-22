/* 张宇涵的cos后期Procreate 自学站：进度、清单、搜索、对比滑块、资料筛选 */
(function () {
  "use strict";
  var KEY = "zyh-cos-progress-v1";
  var EMPTY = { lessons: {}, homework: {}, checks: {}, last: null };

  function load() {
    try {
      var d = JSON.parse(localStorage.getItem(KEY) || "null");
      if (d && typeof d === "object") return Object.assign({}, EMPTY, d);
    } catch (e) {}
    return JSON.parse(JSON.stringify(EMPTY));
  }
  function save(d) {
    try { localStorage.setItem(KEY, JSON.stringify(d)); return true; } catch (e) { return false; }
  }
  var state = load();
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  /* 给统计脚本（track.js）发通知；没开统计时没人监听，不影响任何功能 */
  function emit(name, detail) {
    /* 统计脚本可能比这里晚加载（比如打开带 ?q= 的搜索页），先留一份最后的通知 */
    try { (window.__zyhEmitted = window.__zyhEmitted || {})[name] = detail; } catch (e) {}
    try { document.dispatchEvent(new CustomEvent("zyh:" + name, { detail: detail })); } catch (e) {}
  }
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* 课程列表里的完成状态 */
  function paintLessons() {
    $$("[data-lesson-row]").forEach(function (el) {
      var done = !!state.lessons[el.getAttribute("data-lesson-row")];
      el.classList.toggle("is-done", done);
      var sr = $("[data-done-label]", el);
      if (sr) sr.textContent = done ? "，已完成" : "";
    });
  }

  /* 首页：通关地图进度、继续学习 */
  function paintHome() {
    $$("[data-module]").forEach(function (card) {
      var ids = card.getAttribute("data-lessons").split(",");
      var n = ids.filter(function (id) { return state.lessons[id]; }).length;
      var bar = $(".quest-bar i", card);
      if (bar) bar.style.width = Math.round((n / ids.length) * 100) + "%";
      var c = $("[data-count]", card);
      if (c) c.textContent = n === 0 ? "还没开始" : n === ids.length ? "全部完成" : "已完成 " + n + " / " + ids.length;
      card.classList.toggle("is-done", n === ids.length);
    });
    var btn = $("[data-continue]");
    var note = $("[data-continue-note]");
    if (btn && state.last && state.last.url) {
      btn.textContent = "继续学习";
      btn.setAttribute("href", resolveUrl(state.last.url));
      if (note) { note.hidden = false; note.textContent = "上次学到：" + state.last.title; }
    }
  }

  /* 预览版是相对路径，这里把保存的绝对路径换成相对路径 */
  function resolveUrl(u) {
    if (location.protocol !== "file:") return u;
    var depth = (document.body.getAttribute("data-depth") || "0") | 0;
    var p = "";
    for (var i = 0; i < depth; i++) p += "../";
    var hash = "", k = u.indexOf("#");
    if (k >= 0) { hash = u.slice(k); u = u.slice(0, k); }
    return p + u.replace(/^\//, "") + (u.slice(-1) === "/" ? "index.html" : "") + hash;
  }

  /* 课程页：完成按钮、记住上次学到哪 */
  function initLesson() {
    var art = $("[data-lesson]");
    if (!art) return;
    var id = art.getAttribute("data-lesson");
    var h1 = $("h1", art);
    var url = document.body.getAttribute("data-url");
    if (url) {
      state.last = { id: id, url: url, title: h1 ? h1.textContent.replace(/\s+/g, " ").trim() : id };
      save(state);
    }
    var btn = $("[data-done]");
    if (!btn) return;
    function paint() {
      var done = !!state.lessons[id];
      btn.setAttribute("aria-pressed", done ? "true" : "false");
      btn.textContent = done ? "本课已完成（点击取消）" : "标记本课已完成";
    }
    btn.addEventListener("click", function () {
      if (state.lessons[id]) delete state.lessons[id]; else state.lessons[id] = Date.now();
      save(state); paint(); paintLessons();
    });
    paint();
  }

  /* 作业勾选（课程页、作业中心、模块页共用） */
  function initHomework() {
    var boxes = $$("[data-hw]");
    boxes.forEach(function (b) {
      var id = b.getAttribute("data-hw");
      b.checked = !!state.homework[id];
      var item = b.closest(".hw-item");
      if (item) item.classList.toggle("is-done", b.checked);
      b.addEventListener("change", function () {
        if (b.checked) state.homework[id] = Date.now(); else delete state.homework[id];
        save(state);
        if (item) item.classList.toggle("is-done", b.checked);
        paintHwTotal();
      });
    });
    paintHwTotal();
  }
  function paintHwTotal() {
    var el = $("[data-hw-total]");
    if (!el) return;
    var boxes = $$("[data-hw]");
    var n = boxes.filter(function (b) { return b.checked; }).length;
    el.textContent = "已完成 " + n + " / " + boxes.length;
  }

  /* 自检清单 */
  function initChecklists() {
    $$("[data-checklist]").forEach(function (box) {
      var id = box.getAttribute("data-checklist");
      var saved = state.checks[id] || [];
      $$("input[data-check-index]", box).forEach(function (inp) {
        var i = +inp.getAttribute("data-check-index");
        inp.checked = saved.indexOf(i) >= 0;
        inp.addEventListener("change", function () {
          var arr = $$("input[data-check-index]", box).filter(function (x) { return x.checked; })
            .map(function (x) { return +x.getAttribute("data-check-index"); });
          if (arr.length) state.checks[id] = arr; else delete state.checks[id];
          save(state);
        });
      });
    });
  }

  /* 修图前后对比滑块 */
  function initCompare() {
    $$("[data-compare]").forEach(function (fig) {
      var stage = $(".compare-stage", fig), range = $(".compare-range", fig);
      function set(v) { stage.style.setProperty("--pos", v + "%"); }
      range.addEventListener("input", function () { set(range.value); });
      set(range.value);
      var dragging = false;
      function fromEvent(e) {
        var r = stage.getBoundingClientRect();
        var v = Math.max(0, Math.min(100, ((e.clientX - r.left) / r.width) * 100));
        range.value = v; set(v);
      }
      stage.addEventListener("pointerdown", function (e) { dragging = true; stage.setPointerCapture(e.pointerId); fromEvent(e); });
      stage.addEventListener("pointermove", function (e) { if (dragging) fromEvent(e); });
      stage.addEventListener("pointerup", function () { dragging = false; });
      stage.style.touchAction = "pan-y";
    });
  }

  /* 资料库筛选 */
  function initFilters() {
    var box = $("[data-filters]");
    if (!box) return;
    var sel = { type: "", platform: "", paid: "" };
    var cards = $$(".res-card");
    var count = $("[data-filter-count]");
    function apply() {
      var n = 0;
      cards.forEach(function (c) {
        var ok = (!sel.type || c.dataset.type === sel.type) && (!sel.platform || c.dataset.platform === sel.platform) && (!sel.paid || c.dataset.paid === sel.paid);
        c.hidden = !ok; if (ok) n++;
      });
      count.textContent = "显示 " + n + " 条";
      try { localStorage.setItem("zyh-res-filter", JSON.stringify(sel)); } catch (e) {}
    }
    try { Object.assign(sel, JSON.parse(localStorage.getItem("zyh-res-filter") || "{}")); } catch (e) {}
    $$(".fchip", box).forEach(function (b) {
      var f = b.dataset.f, v = b.dataset.v;
      b.classList.toggle("is-on", sel[f] === v);
      b.setAttribute("aria-pressed", sel[f] === v ? "true" : "false");
      b.addEventListener("click", function () {
        sel[f] = v;
        $$('.fchip[data-f="' + f + '"]', box).forEach(function (x) {
          var on = x === b; x.classList.toggle("is-on", on); x.setAttribute("aria-pressed", on ? "true" : "false");
        });
        apply();
      });
    });
    apply();
  }

  /* 搜索：索引按小节收录，结果显示「课 › 小节」，同一页最多 3 条 */
  function initSearch() {
    var form = $("[data-search-form]");
    if (!form || !window.SEARCH_INDEX) return;
    var input = $("[data-search-input]"), list = $("[data-search-results]"), count = $("[data-search-count]");
    function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
    function hl(s, terms) {
      var out = esc(s);
      terms.forEach(function (t) { if (t) out = out.split(esc(t)).join("<mark>" + esc(t) + "</mark>"); });
      return out;
    }
    function snippet(x, t) {
      var i = x.indexOf(t);
      if (i < 0) return x.slice(0, 90) + (x.length > 90 ? "…" : "");
      var a = Math.max(0, i - 36), b = Math.min(x.length, i + 64);
      return (a > 0 ? "…" : "") + x.slice(a, b) + (b < x.length ? "…" : "");
    }
    function run() {
      var q = input.value.trim();
      list.innerHTML = "";
      if (!q) { count.textContent = ""; return; }
      var terms = q.split(/\s+/).filter(Boolean);
      var scored = [];
      window.SEARCH_INDEX.forEach(function (d) {
        var head = d.t + " " + (d.s || ""), score = 0, ok = true;
        terms.forEach(function (t) {
          var inHead = head.indexOf(t) >= 0, inBody = d.x.indexOf(t) >= 0;
          if (!inHead && !inBody) ok = false;
          if (d.s && d.s.indexOf(t) >= 0) score += 20;
          else if (inHead) score += 12;
          if (inBody) score += Math.min(6, d.x.split(t).length - 1);
        });
        if (ok) scored.push({ d: d, s: score });
      });
      scored.sort(function (a, b) { return b.s - a.s; });
      var perPage = {}, hits = [];
      scored.forEach(function (h) {
        var page = h.d.u.split("#")[0];
        perPage[page] = (perPage[page] || 0) + 1;
        if (perPage[page] <= 3 && hits.length < 60) hits.push(h);
      });
      var pages = Object.keys(perPage).length;
      count.textContent = hits.length ? "在 " + pages + " 个页面里找到 " + scored.length + " 处，显示 " + hits.length + " 条" :
        "没有找到「" + q + "」。换个说法试试，比如「比例」「肤色」「抠图」。";
      hits.forEach(function (h) {
        var li = document.createElement("li");
        var title = hl(h.d.t, terms) + (h.d.s ? ' <span class="sr-sep">›</span> ' + hl(h.d.s, terms) : "");
        li.innerHTML = '<span class="pill">' + esc(h.d.k) + '</span> <a href="' + esc(resolveUrl(h.d.u)) + '">' + title + "</a><p>" + hl(snippet(h.d.x, terms[0]), terms) + "</p>";
        list.appendChild(li);
      });
      try { history.replaceState(null, "", "?q=" + encodeURIComponent(q)); } catch (e) {}
      emit("search", { q: q, hits: scored.length, submit: !!run.submit });
      run.submit = false;
    }
    var timer;
    form.addEventListener("submit", function (e) { e.preventDefault(); run.submit = true; run(); });
    input.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(run, 150); });
    var m = location.search.match(/[?&]q=([^&]+)/);
    if (m) { input.value = decodeURIComponent(m[1].replace(/\+/g, " ")); run(); }
  }

  /* 进度备份 */
  function initBackup() {
    var msg = $("[data-backup-msg]");
    function paintLast() {
      var el = $("[data-backup-last]"); if (!el) return;
      el.textContent = state.lastExport ? "上次导出：" + new Date(state.lastExport).toLocaleDateString("zh-CN") : "还没有导出过进度。";
    }
    paintLast();
    var ex = $("[data-export]"), im = $("[data-import]"), rs = $("[data-reset]");
    if (!ex) return;
    ex.addEventListener("click", function () {
      var blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "cos后期自学进度-" + new Date().toISOString().slice(0, 10) + ".json";
      document.body.appendChild(a); a.click(); a.remove();
      state.lastExport = Date.now(); save(state); paintLast();
      msg.textContent = "已导出。文件保存在「下载」或「文件」App 里。";
    });
    im.addEventListener("change", function () {
      var f = im.files[0]; if (!f) return;
      var r = new FileReader();
      r.onload = function () {
        try {
          var d = JSON.parse(r.result);
          if (!d || typeof d.lessons !== "object") throw new Error();
          state = Object.assign({}, EMPTY, d); save(state);
          msg.textContent = "已导入：" + Object.keys(state.lessons).length + " 节课、" + Object.keys(state.homework).length + " 个作业。";
        } catch (e) { msg.textContent = "导入失败：这不是本站导出的进度文件。"; }
      };
      r.readAsText(f);
    });
    rs.addEventListener("click", function () {
      if (!confirm("清空后无法恢复。确定清空全部学习进度吗？")) return;
      state = JSON.parse(JSON.stringify(EMPTY)); save(state);
      msg.textContent = "进度已清空。";
    });
  }

  /* 阅读进度、当前小节、目录抽屉、回到顶部 */
  function initReading() {
    var bar = $("[data-progress]"), top = $("[data-to-top]"), cur = $("[data-cur-sec]");
    var sheet = $("[data-toc-sheet]"), openBtn = $("[data-toc-open]");
    var heads = $$(".prose h2[id], .prose h3[id]");
    var links = $$("[data-toc-link]");
    var ticking = false;
    function update() {
      ticking = false;
      var h = document.documentElement, max = h.scrollHeight - h.clientHeight;
      if (bar) bar.style.width = (max > 0 ? Math.min(100, (h.scrollTop / max) * 100) : 0) + "%";
      if (top) top.hidden = h.scrollTop < 900;
      if (!heads.length) return;
      var y = 120, active = null;
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].getBoundingClientRect().top - y <= 0) active = heads[i]; else break;
      }
      var id = active ? active.id : "";
      if (cur) cur.textContent = active ? active.textContent.replace(/\s+/g, " ").trim() : "";
      links.forEach(function (a) { a.classList.toggle("is-current", a.getAttribute("href") === "#" + id); });
    }
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    window.addEventListener("resize", update);
    update();
    if (top) top.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
    if (!sheet || !openBtn) return;
    var lastFocus = null;
    function open() {
      lastFocus = document.activeElement; sheet.hidden = false; document.body.style.overflow = "hidden";
      var c = $("a.is-current", sheet) || $("a", sheet); if (c) { c.focus(); c.scrollIntoView({ block: "center" }); }
    }
    function close() { sheet.hidden = true; document.body.style.overflow = ""; if (lastFocus) lastFocus.focus(); }
    openBtn.addEventListener("click", open);
    $("[data-toc-close]", sheet).addEventListener("click", close);
    sheet.addEventListener("click", function (e) { if (e.target === sheet) close(); if (e.target.closest("a")) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !sheet.hidden) close(); });
  }

  /* 窄屏时课程目录默认收起 */
  function initSideToc() {
    var d = $(".side-toc");
    if (d && window.matchMedia && window.matchMedia("(max-width: 1000px)").matches) d.removeAttribute("open");
  }

  /* 首页备份提醒：学完 5 课以后，超过 14 天没导出就提醒一次 */
  function initBackupNotice() {
    var box = $("[data-backup-notice]"); if (!box) return;
    var done = Object.keys(state.lessons).length, now = Date.now(), DAY = 864e5;
    var last = Math.max(state.lastExport || 0, state.noticeSnooze || 0);
    if (done >= 5 && now - last > 14 * DAY) {
      $("[data-done-count]", box).textContent = done; box.hidden = false;
      $("[data-backup-dismiss]", box).addEventListener("click", function () { state.noticeSnooze = now; save(state); box.hidden = true; });
    }
  }

  function boot() {
    initSideToc(); initReading(); initBackupNotice();
    paintLessons(); paintHome(); initLesson(); initHomework(); initChecklists();
    initCompare(); initFilters(); initSearch(); initBackup();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
