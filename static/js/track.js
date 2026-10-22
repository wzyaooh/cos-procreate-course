/* 张宇涵的cos后期Procreate 自学站：匿名使用统计。说明见「使用说明 › 隐私说明」。
   - 设备编号是随机生成的，存在本机浏览器里，和身份无关；不用 Cookie，不做浏览器指纹
   - 发送失败不影响网站使用 */
(function () {
  "use strict";
  var ENDPOINT = "/api/e", KD = "zyh-stats-did", KS = "zyh-stats-sid", KP = "zyh-cos-progress-v1";
  var IDLE = 10 * 60e3, SESSION_GAP = 30 * 60e3;
  if (!window.JSON || !document.addEventListener) return;
  try { localStorage.removeItem("zyh-stats-off"); } catch (e) {} // 旧版本留下的关闭标记，已不再使用

  function rid(n) {
    var a = new Uint8Array(n), c = window.crypto || window.msCrypto;
    if (c && c.getRandomValues) c.getRandomValues(a); else for (var i = 0; i < n; i++) a[i] = Math.floor(Math.random() * 256);
    return Array.prototype.map.call(a, function (b) { return ("0" + b.toString(16)).slice(-2); }).join("");
  }
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  var did = lsGet(KD);
  if (!/^[0-9a-f]{32}$/.test(did || "")) { did = rid(16); lsSet(KD, did); }
  var sess = null;
  try { sess = JSON.parse(lsGet(KS) || "null"); } catch (e) {}
  var t0 = Date.now(), isNew = !sess || !/^[0-9a-f]{16}$/.test(sess.id || "") || t0 - (sess.last || 0) > SESSION_GAP;
  if (isNew) sess = { id: rid(8), last: t0 };
  function touchSession() { sess.last = Date.now(); lsSet(KS, JSON.stringify(sess)); }
  touchSession();

  var path = location.pathname, queue = [];
  function ctx() {
    var sa = 0;
    try { sa = (window.matchMedia && matchMedia("(display-mode: standalone)").matches) || navigator.standalone === true ? 1 : 0; } catch (e) {}
    var tz = "";
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (e) {}
    return { sw: screen.width, sh: screen.height, tp: navigator.maxTouchPoints || 0, sa: sa, lg: navigator.language || "", tz: tz };
  }
  function push(ev) { ev.ts = Date.now(); if (!ev.p) ev.p = path; queue.push(ev); if (queue.length >= 40) flush(false); }

  /* 前台计时：页面在前台、并且 10 分钟内有过操作才算 */
  var visible = document.visibilityState !== "hidden", lastAct = t0, lastTick = t0, acc = 0;
  function tick() {
    var t = Date.now(), dt = t - lastTick;
    if (visible && t - lastAct < IDLE) acc += Math.min(dt, 4000);
    lastTick = t;
  }
  function takeTime() {
    tick();
    var sec = Math.floor(acc / 1000);
    if (sec >= 1) { queue.push({ t: "time", p: path, ts: Date.now(), sec: sec }); acc -= sec * 1000; }
  }
  var lastTouch = 0;
  function activity() {
    var t = Date.now();
    if (t - lastAct >= IDLE) lastTick = t; // 从闲置中回来，闲置那段不算
    lastAct = t;
    if (t - lastTouch > 60e3) { lastTouch = t; touchSession(); }
  }
  ["pointerdown", "keydown", "scroll", "touchstart", "wheel", "input"].forEach(function (n) {
    window.addEventListener(n, activity, { passive: true, capture: true });
  });
  var lastMove = 0;
  window.addEventListener("pointermove", function () { var t = Date.now(); if (t - lastMove > 5000) { lastMove = t; activity(); } }, { passive: true });

  function flush(beacon) {
    takeTime();
    if (!queue.length) return;
    var body = JSON.stringify({ v: 1, d: did, s: sess.id, c: ctx(), e: queue.splice(0, 100) });
    try {
      if (beacon && navigator.sendBeacon && navigator.sendBeacon(ENDPOINT, new Blob([body], { type: "text/plain" }))) return;
      if (window.fetch) fetch(ENDPOINT, { method: "POST", body: body, keepalive: true, credentials: "omit", headers: { "Content-Type": "text/plain" } }).catch(function () {});
    } catch (e) {}
  }
  setInterval(tick, 2000);
  setTimeout(function () { flush(false); }, 4000);            // 打开后很快发一次，短暂停留也能记到
  setInterval(function () { if (visible) flush(false); }, 20000);
  document.addEventListener("visibilitychange", function () {
    tick();
    visible = document.visibilityState !== "hidden";
    if (visible) { lastTick = Date.now(); activity(); } else flush(true);
  });
  window.addEventListener("pagehide", function () { flush(true); });

  /* 打开页面、学习进度 */
  var ref = "";
  try {
    if (document.referrer) {
      var r = new URL(document.referrer);
      ref = r.host === location.host ? r.pathname : r.host;
    }
  } catch (e) {}
  push({ t: "view", r: ref });
  function progress() {
    try {
      var st = JSON.parse(lsGet(KP) || "null") || {};
      push({ t: "progress", done: Object.keys(st.lessons || {}).sort().slice(0, 60), hw: Object.keys(st.homework || {}).length });
    } catch (e) {}
  }
  var lastProg = +lsGet("zyh-stats-prog") || 0;
  if (isNew || t0 - lastProg > 6 * 3600e3) { progress(); lsSet("zyh-stats-prog", String(t0)); }

  /* 课程读到哪一节 */
  var heads = [].slice.call(document.querySelectorAll(".prose h2[id], .prose h3[id]"));
  if (heads.length && window.IntersectionObserver) {
    var seen = {};
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var h = en.target;
        if (en.isIntersecting && !seen[h.id]) {
          seen[h.id] = 1;
          push({ t: "read", id: h.id, tt: (h.textContent || "").replace(/\s+/g, " ").trim().slice(0, 60) });
          io.unobserve(h);
        }
      });
    }, { rootMargin: "0px 0px -55% 0px" });
    heads.forEach(function (h) { io.observe(h); });
  }

  /* 功能使用 */
  function act(n, v, on) { var e = { t: "act", n: n }; if (v != null) e.v = String(v); if (on != null) e.on = on ? 1 : 0; push(e); }
  var lessonId = (document.querySelector("[data-lesson]") || {}).getAttribute ? document.querySelector("[data-lesson]").getAttribute("data-lesson") : null;
  document.addEventListener("click", function (e) {
    var el = e.target.closest ? e.target.closest("a, button, summary, [data-done]") : null;
    if (!el) return;
    if (el.matches("[data-done]")) {
      setTimeout(function () { var on = el.getAttribute("aria-pressed") === "true"; act("lesson_done", el.getAttribute("data-done"), on); if (on) progress(); }, 0);
    } else if (el.matches("[data-toc-open]")) act("toc_open");
    else if (el.matches("[data-to-top]")) act("to_top");
    else if (el.matches(".fchip")) act("res_filter", el.getAttribute("data-f") + ":" + (el.getAttribute("data-v") || "全部"));
    else if (el.matches("[data-export]")) act("progress_export");
    else if (el.matches("[data-reset]")) act("progress_reset_click");
    else if (el.matches("[data-backup-dismiss]")) act("backup_notice_dismiss");
    else if (el.matches(".side-toc summary")) act("side_toc_toggle");
    else if (el.matches("a[href]")) {
      var u;
      try { u = new URL(el.href, location.href); } catch (x) { return; }
      if (u.host && u.host !== location.host && /^https?:$/.test(u.protocol)) { push({ t: "link", u: u.href.slice(0, 300) }); flush(true); }
      else if (u.host === location.host && u.pathname !== path) flush(true); // 站内跳转前先发出去
      else if (u.host === location.host && u.pathname === path && u.hash && el.closest("[data-toc-sheet], .side-sections")) act("toc_jump", u.hash.slice(1));
    }
  }, true);
  document.addEventListener("change", function (e) {
    var el = e.target;
    if (!el || !el.matches) return;
    if (el.matches("[data-hw]")) act("homework", el.getAttribute("data-hw"), el.checked);
    else if (el.matches("[data-check-index]")) act("checklist", (lessonId || path) + "#" + el.getAttribute("data-check-index"), el.checked);
    else if (el.matches("[data-import]")) act("progress_import");
  }, true);
  var cmpSeen = [];
  document.addEventListener("pointerdown", function (e) {
    var fig = e.target.closest && e.target.closest("[data-compare]");
    if (!fig) return;
    var i = [].indexOf.call(document.querySelectorAll("[data-compare]"), fig);
    if (cmpSeen.indexOf(i) < 0) { cmpSeen.push(i); act("compare", i + 1); }
  }, true);
  window.addEventListener("beforeprint", function () { act("print"); });

  /* 站内搜索：停止输入 1.5 秒后记下最后的关键词 */
  var sTimer, sLast = "";
  function onSearch(d) {
    d = d || {};
    clearTimeout(sTimer);
    sTimer = setTimeout(function () {
      var q = (d.q || "").trim();
      if (q && q !== sLast) { sLast = q; push({ t: "search", q: q.slice(0, 60), hits: d.hits || 0 }); }
    }, d.submit ? 0 : 1500);
  }
  document.addEventListener("zyh:search", function (e) { onSearch(e.detail); });
  // site.js 先跑完的话（打开带 ?q= 的搜索页），补上它已经发出的那次搜索
  if (window.__zyhEmitted && window.__zyhEmitted.search) onSearch(window.__zyhEmitted.search);
})();
