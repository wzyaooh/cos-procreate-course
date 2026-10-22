/* 学习统计看板 */
(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var INK = "#1E293B", VIO = "#7C3AED", PINK = "#F472B6", MINT = "#34D399", YEL = "#FBBF24", PALETTE = [VIO, PINK, MINT, YEL, "#60A5FA", "#F97316", "#94A3B8", "#14B8A6", "#E11D48", "#A3E635"];
  var FEATURES = {
    lesson_done: "标记课程完成", homework: "勾选作业", checklist: "勾选自检清单", toc_open: "打开本页目录", toc_jump: "用目录跳到小节",
    to_top: "回到顶部", res_filter: "资料库筛选", progress_export: "导出进度", progress_import: "导入进度", progress_reset_click: "点了清空进度",
    backup_notice_dismiss: "关闭备份提醒", side_toc_toggle: "展开或收起课程目录", compare: "拖动修图前后对比", print: "打印页面"
  };
  var state = { range: localStorage.getItem("zstats-range") || "7", tab: localStorage.getItem("zstats-tab") || "overview", site: null, charts: {}, cache: {} };
  if (window.Chart) { Chart.defaults.font.family = getComputedStyle(document.body).fontFamily; Chart.defaults.color = INK; Chart.defaults.borderColor = "#E2E8F0"; }

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function n(x) { return (x || 0).toLocaleString("zh-CN"); }
  function dur(sec) {
    sec = Math.round(sec || 0);
    if (sec < 60) return sec + " 秒";
    var h = Math.floor(sec / 3600), m = Math.floor((sec % 3600) / 60), s = sec % 60;
    if (h) return h + " 小时 " + m + " 分";
    return m + " 分" + (s && m < 10 ? " " + s + " 秒" : "");
  }
  function when(ms) {
    var d = new Date(ms), p = function (x) { return ("0" + x).slice(-2); };
    var today = new Date(); var same = d.toDateString() === today.toDateString();
    var y = new Date(Date.now() - 864e5).toDateString() === d.toDateString();
    return (same ? "今天" : y ? "昨天" : (d.getMonth() + 1) + "/" + d.getDate()) + " " + p(d.getHours()) + ":" + p(d.getMinutes());
  }
  function title(path) { return (state.site && state.site.pages[path]) || path; }
  function lessonOf(path) {
    if (!state.site) return null;
    for (var i = 0; i < state.site.modules.length; i++) {
      var m = state.site.modules[i];
      for (var j = 0; j < m.lessons.length; j++) if (m.lessons[j].path === path) return m.lessons[j];
    }
    return null;
  }

  function api(name, extra) {
    var url = "/stats/api/" + name + "?range=" + encodeURIComponent(state.range) + (extra || "");
    return fetch(url, { credentials: "same-origin" }).then(function (r) {
      if (r.status === 401) { location.href = "/stats/login"; throw new Error("请先登录"); }
      return r.json();
    }).then(function (d) { if (d.error) throw new Error(d.error); return d; });
  }
  function showErr(e) { var el = $("[data-err]"); el.hidden = false; el.textContent = "读取数据失败：" + (e && e.message || e); }

  function chart(id, cfg) {
    if (state.charts[id]) state.charts[id].destroy();
    cfg.options = Object.assign({ responsive: true, maintainAspectRatio: false, animation: false }, cfg.options || {});
    var cv = document.getElementById(id), none = !(cfg.data.labels || []).length;
    cv.parentNode.classList.toggle("is-empty", none);
    state.charts[id] = new Chart(cv, cfg);
  }

  /* 可排序表格 */
  function table(el, cols, rows, opt) {
    opt = opt || {};
    if (!rows.length) { el.innerHTML = '<p class="empty">' + (opt.empty || "这段时间还没有数据") + "</p>"; return; }
    var sortKey = el._sortKey || opt.sort, dir = el._dir || -1;
    var sorted = rows.slice().sort(function (a, b) {
      var x = a[sortKey], y = b[sortKey];
      if (typeof x === "string" || typeof y === "string") return String(x || "").localeCompare(String(y || ""), "zh") * dir;
      return ((x || 0) - (y || 0)) * dir;
    });
    var limit = opt.limit || 300;
    var h = '<div class="tbl"><table><thead><tr>' + cols.map(function (c) {
      return '<th class="' + (c.num ? "num" : "") + '" data-k="' + c.k + '"' + (c.k === sortKey ? ' aria-sort="' + (dir < 0 ? "descending" : "ascending") + '"' : "") + ">" + c.t + "</th>";
    }).join("") + "</tr></thead><tbody>" + sorted.slice(0, limit).map(function (r, i) {
      return "<tr" + (opt.click ? ' class="click" data-i="' + rows.indexOf(r) + '"' : "") + ">" + cols.map(function (c) {
        return '<td class="' + (c.num ? "num" : "") + '">' + (c.f ? c.f(r) : esc(r[c.k])) + "</td>";
      }).join("") + "</tr>";
    }).join("") + "</tbody></table></div>" + (sorted.length > limit ? '<p class="note">只显示前 ' + limit + " 条，完整数据用导出。</p>" : "");
    el.innerHTML = h;
    $$("th", el).forEach(function (th) {
      th.addEventListener("click", function () {
        var k = th.getAttribute("data-k");
        el._dir = el._sortKey === k ? -(el._dir || -1) : -1; el._sortKey = k;
        table(el, cols, rows, opt);
      });
    });
    if (opt.click) $$("tr.click", el).forEach(function (tr) { tr.addEventListener("click", function () { opt.click(rows[+tr.getAttribute("data-i")]); }); });
  }

  /* ---------- 概览 ---------- */
  function loadOverview() {
    return Promise.all([api("overview"), api("pages")]).then(function (res) {
      var d = res[0], pg = res[1], c = d.cards;
      var cards = [
        ["设备数", n(c.devices), d.approx ? "多天合并为估算值" : "今天打开过的设备", VIO],
        ["新设备", n(c.new_devices), "第一次打开本站", MINT],
        ["访问次数", n(c.sessions), "隔 30 分钟以上算新的一次", INK],
        ["页面浏览", n(c.views), "打开页面的次数", INK],
        ["总学习时长", dur(c.seconds), "页面在前台、有操作的时间", PINK],
        ["人均时长", dur(c.avg_seconds_per_device), "总时长 ÷ 设备数", PINK],
        ["主屏幕打开", Math.round(c.standalone_ratio * 100) + "%", "添加到主屏幕后打开的比例", YEL],
        ["现在在线", n(d.online), "最近 3 分钟有活动", MINT]
      ];
      $("[data-cards]").innerHTML = cards.map(function (x) {
        return '<div class="card" style="--c:' + x[3] + '"><div class="k">' + x[0] + '</div><div class="v">' + x[1] + '</div><div class="h">' + x[2] + "</div></div>";
      }).join("");
      var labels = d.series.map(function (s) { return s.day.slice(5); });
      chart("c-trend", {
        type: "bar", data: { labels: labels, datasets: [
          { type: "line", label: "设备数", data: d.series.map(function (s) { return s.devices; }), borderColor: VIO, backgroundColor: VIO, yAxisID: "y", tension: .25, pointRadius: d.series.length > 40 ? 0 : 3 },
          { type: "bar", label: "学习时长（分钟）", data: d.series.map(function (s) { return s.minutes; }), backgroundColor: "rgba(244,114,182,.55)", borderColor: INK, borderWidth: 1.5, yAxisID: "y1" }
        ] },
        options: { interaction: { mode: "index", intersect: false }, scales: { y: { beginAtZero: true, ticks: { precision: 0 }, title: { display: true, text: "设备" } }, y1: { beginAtZero: true, position: "right", grid: { drawOnChartArea: false }, title: { display: true, text: "分钟" } } } }
      });
      function donut(id, list) {
        list = (list || []).slice(0, 8);
        chart(id, { type: "doughnut", data: { labels: list.map(function (x) { return x.key; }), datasets: [{ data: list.map(function (x) { return x.devices; }), backgroundColor: PALETTE, borderColor: INK, borderWidth: 1.5 }] },
          options: { plugins: { legend: { position: "right" } }, cutout: "55%" } });
      }
      donut("c-dtype", d.dims.dtype); donut("c-browser", d.dims.browser);
      var top = pg.pages.slice(0, 10), max = top.length ? top[0].seconds : 1;
      table($("[data-top-pages]"), [
        { k: "path", t: "页面", f: function (r) { return '<a href="' + esc(r.path) + '" target="_blank" rel="noopener">' + esc(title(r.path)) + "</a>"; } },
        { k: "seconds", t: "总时长", num: 1, f: function (r) { return dur(r.seconds); } },
        { k: "bar", t: "", f: function (r) { return '<div class="bar"><i style="width:' + Math.round(r.seconds / max * 100) + '%"></i></div>'; } },
        { k: "devices", t: "设备", num: 1 }, { k: "avg_seconds", t: "人均", num: 1, f: function (r) { return dur(r.avg_seconds); } }
      ], top, { sort: "seconds" });
      $("[data-ov-note]").textContent = "按设备的详细记录保留 " + d.retention_days + " 天，更早的只有每日汇总。数据每 5 分钟汇总一次，今天的数字是实时的。";
    });
  }

  /* ---------- 课程 ---------- */
  function loadLessons() {
    return api("pages").then(function (d) {
      var mods = state.site ? state.site.modules : [];
      var order = ["未开始"].concat(mods.map(function (m) { return "M" + m.no; }));
      chart("c-progress", { type: "bar", data: { labels: order.map(function (b) { var m = mods.find(function (x) { return "M" + x.no === b; }); return m ? b + " " + m.title : b; }),
        datasets: [{ label: "设备", data: order.map(function (b) { return d.progress_now[b] || 0; }), backgroundColor: MINT, borderColor: INK, borderWidth: 1.5 }] },
        options: { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, ticks: { precision: 0 } } } } });
      $("[data-prog-sub]").textContent = "最近 " + d.retention_days + " 天打开过的设备，按完成的最靠后的一课所在模块统计";
      var doneByMod = mods.map(function (m) { return m.lessons.reduce(function (a, l) { return a + (d.done[l.id] || 0); }, 0); });
      chart("c-done", { type: "bar", data: { labels: mods.map(function (m) { return "M" + m.no; }),
        datasets: [{ label: "完成次数", data: doneByMod, backgroundColor: VIO, borderColor: INK, borderWidth: 1.5 }] },
        options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } } });
      var byPath = {}; d.pages.forEach(function (p) { byPath[p.path] = p; });
      var rows = [];
      mods.forEach(function (m) { m.lessons.forEach(function (l) {
        var p = byPath[l.path] || {};
        rows.push({ no: l.no, ord: m.no * 100 + parseInt(l.id.split("-")[1], 10), title: l.title, path: l.path, devices: p.devices || 0, views: p.views || 0, seconds: p.seconds || 0, avg: p.avg_seconds || 0, done: d.done[l.id] || 0 });
      }); });
      var lt = $("[data-lesson-table]"), only = $("[data-only-visited]");
      if (!lt._sortKey) { lt._sortKey = "ord"; lt._dir = 1; }
      var allRows = rows;
      rows = only && only.checked ? rows.filter(function (r) { return r.devices > 0; }) : rows;
      if (only) only.onchange = function () { loadLessons().catch(showErr); };
      table(lt, [
        { k: "ord", t: "课", f: function (r) { return "<b>" + r.no + "</b>"; } }, { k: "title", t: "标题" },
        { k: "devices", t: "设备", num: 1 }, { k: "views", t: "浏览", num: 1 },
        { k: "seconds", t: "总时长", num: 1, f: function (r) { return dur(r.seconds); } }, { k: "avg", t: "人均", num: 1, f: function (r) { return dur(r.avg); } },
        { k: "done", t: "标记完成", num: 1 }
      ], rows, { sort: "ord", click: showSections, empty: "这段时间没有人打开过课程" });
      $("[data-lesson-sum]").textContent = "46 节课里有 " + allRows.filter(function (r) { return r.devices > 0; }).length + " 节有人打开过";
      var lessonPaths = {}; rows.forEach(function (r) { lessonPaths[r.path] = 1; });
      var others = d.pages.filter(function (p) { return !lessonPaths[p.path]; });
      table($("[data-other-table]"), [
        { k: "path", t: "页面", f: function (r) { return esc(title(r.path)) + ' <span class="mono">' + esc(r.path) + "</span>"; } },
        { k: "devices", t: "设备", num: 1 }, { k: "views", t: "浏览", num: 1 }, { k: "seconds", t: "总时长", num: 1, f: function (r) { return dur(r.seconds); } }
      ], others, { sort: "views" });
    });
  }
  function showSections(r) {
    openDrawer(r.no + " " + r.title + " · 读到哪一步", '<p class="empty">读取中…</p>');
    api("sections", "&path=" + encodeURIComponent(r.path)).then(function (d) {
      if (!d.sections.length) { $("[data-drawer-body]").innerHTML = '<p class="empty">这段时间没有阅读记录</p>'; return; }
      var base = Math.max(d.page_devices, 1), les = lessonOf(r.path), order = (les && les.sections) || [];
      d.sections.sort(function (a, b) {
        var x = order.indexOf(a.id), y = order.indexOf(b.id);
        return (x < 0 ? 999 : x) - (y < 0 ? 999 : y);
      });
      $("[data-drawer-body]").innerHTML = '<p class="sub">共 ' + d.page_devices + " 台设备打开过这节课。百分比 = 读到这一节的设备 ÷ 打开这节课的设备，按页面里的顺序排列。</p>" +
        '<div class="tbl"><table><tbody>' + d.sections.map(function (s) {
          var pct = Math.round(s.devices / base * 100);
          return "<tr><td>" + esc(s.title || s.id) + '</td><td class="num">' + pct + '%</td><td style="width:35%"><div class="bar"><i style="width:' + pct + '%"></i></div></td></tr>';
        }).join("") + "</tbody></table></div>";
    }).catch(showErr);
  }

  /* ---------- 功能和搜索 ---------- */
  function loadFeatures() {
    return api("features").then(function (d) {
      var f = d.features.slice(0, 20);
      chart("c-features", { type: "bar", data: { labels: f.map(function (x) { return FEATURES[x.key] || x.key; }),
        datasets: [{ label: "次数", data: f.map(function (x) { return x.count; }), backgroundColor: YEL, borderColor: INK, borderWidth: 1.5 },
                   { label: "设备", data: f.map(function (x) { return x.devices; }), backgroundColor: VIO, borderColor: INK, borderWidth: 1.5 }] },
        options: { indexAxis: "y", scales: { x: { beginAtZero: true, ticks: { precision: 0 } } } } });
      var zeroOnly = $("[data-zero-only]");
      function paintSearch() {
        var rows = d.search.filter(function (s) { return !zeroOnly.checked || s.zero; });
        table($("[data-search-table]"), [
          { k: "key", t: "搜索词", f: function (r) { return esc(r.key) + (r.zero ? ' <span class="pill zero">没有结果</span>' : ""); } },
          { k: "count", t: "次数", num: 1 }, { k: "devices", t: "设备", num: 1 }
        ], rows, { sort: "count", empty: zeroOnly.checked ? "没有搜不到结果的词" : "这段时间没有人搜索" });
      }
      zeroOnly.onchange = paintSearch; paintSearch();
      table($("[data-link-table]"), [
        { k: "key", t: "链接", f: function (r) { var u; try { u = new URL(r.key); } catch (e) { return esc(r.key); } return '<a href="' + esc(r.key) + '" target="_blank" rel="noopener noreferrer">' + esc(u.host + u.pathname).slice(0, 70) + "</a>"; } },
        { k: "count", t: "点击", num: 1 }, { k: "devices", t: "设备", num: 1 }
      ], d.links, { sort: "count" });
    });
  }

  /* ---------- 设备 ---------- */
  function loadDevices() {
    return api("devices").then(function (d) {
      $("[data-dev-sub]").textContent = "最近 " + d.retention_days + " 天打开过的 " + d.devices.length + " 台设备（设备编号是随机生成的，和身份无关）。点一行看这台设备的时间线。";
      var sel = $("[data-dev-type]"), types = {};
      d.devices.forEach(function (x) { types[x.dtype] = 1; });
      sel.innerHTML = '<option value="">全部</option>' + Object.keys(types).map(function (t) { return '<option value="' + esc(t) + '">' + esc(t) + "</option>"; }).join("");
      var q = $("[data-dev-q]");
      function paint() {
        var rows = d.devices.filter(function (x) {
          return (!sel.value || x.dtype === sel.value) && (!q.value || x.id.indexOf(q.value) >= 0 || (x.last_path || "").indexOf(q.value) >= 0);
        });
        table($("[data-dev-table]"), [
          { k: "id", t: "设备", f: function (r) { return '<span class="mono">' + r.id.slice(0, 8) + "</span>"; } },
          { k: "dtype", t: "类型", f: function (r) { return esc(r.dtype) + ' <span class="pill">' + esc(r.os) + '</span> <span class="pill">' + esc(r.browser) + "</span>" + (r.standalone ? ' <span class="pill sa">主屏幕</span>' : ""); } },
          { k: "last_seen", t: "最近", f: function (r) { return when(r.last_seen); } },
          { k: "seconds", t: "时长", num: 1, f: function (r) { return dur(r.seconds); } },
          { k: "views", t: "浏览", num: 1 }, { k: "sessions", t: "访问", num: 1 },
          { k: "done", t: "学完", num: 1, f: function (r) { return r.done + " 课"; } },
          { k: "last_path", t: "最后看的", f: function (r) { return esc(title(r.last_path || "")); } }
        ], rows, { sort: "last_seen", click: showDevice, empty: "最近 " + d.retention_days + " 天没有设备记录" });
      }
      sel.onchange = paint; q.oninput = paint; paint();
    });
  }
  var EV = {
    view: ["打开", MINT], read: ["读到", "#fff"], search: ["搜索", YEL], link: ["打开外部链接", "#60A5FA"], progress: ["学习进度", VIO], act: ["", PINK]
  };
  function showDevice(r) {
    openDrawer("设备 " + r.id.slice(0, 8), '<p class="empty">读取中…</p>');
    api("device", "&id=" + r.id).then(function (d) {
      var dv = d.device;
      var h = '<div class="chips"><span class="pill">' + esc(dv.dtype) + '</span><span class="pill">' + esc(dv.os) + '</span><span class="pill">' + esc(dv.browser) + '</span><span class="pill">屏幕 ' + esc(dv.screen) + "</span>" +
        (dv.standalone ? '<span class="pill sa">从主屏幕打开</span>' : "") + '<span class="pill">' + esc(dv.lang) + "</span></div>" +
        '<p class="sub">第一次：' + when(dv.first_seen) + "　最近：" + when(dv.last_seen) + "　已学完 " + dv.done.length + " 课、勾了 " + (dv.hw || 0) + " 个作业" +
        (dv.done.length ? "：" + dv.done.map(function (x) { return x.replace(/^m(\d)-0?(\d+)$/, "$1.$2"); }).join("、") : "") + "</p>";
      h += d.sessions.map(function (s) {
        var tl = s.timeline.map(function (e) {
          var k = EV[e.type] || ["", "#fff"], txt;
          if (e.type === "view") txt = "<b>" + esc(title(e.path)) + "</b>" + (e.value ? ' <span class="note">来自 ' + esc(e.value) + "</span>" : "");
          else if (e.type === "read") txt = "读到「" + esc(e.value || e.name) + "」";
          else if (e.type === "search") txt = "搜索「" + esc(e.value) + "」，" + (e.num ? e.num + " 处结果" : "没有结果");
          else if (e.type === "link") txt = "打开外部链接 " + esc(e.value).slice(0, 80);
          else if (e.type === "progress") txt = "学习进度：完成 " + (e.num || 0) + " 课（" + esc(e.name) + "）";
          else txt = (FEATURES[e.name] || e.name) + (e.value ? " " + esc(e.value) : "") + (e.num === 0 ? "（取消）" : "");
          return '<li style="--c:' + k[1] + '"><time>' + when(e.ts).slice(-5) + "</time>" + txt + "</li>";
        }).join("");
        var pages = s.pages.map(function (p) { return esc(title(p.path)) + " " + dur(p.seconds); }).join(" · ");
        return '<div class="sess"><h3>' + when(s.start) + " 开始 · 学习 " + dur(s.seconds) + "</h3><p class=\"sub\">" + pages + '</p><ul class="tl">' + tl + "</ul></div>";
      }).join("");
      $("[data-drawer-body]").innerHTML = h || '<p class="empty">没有记录</p>';
    }).catch(showErr);
  }

  /* ---------- 抽屉、切换 ---------- */
  function openDrawer(t, body) { $("[data-drawer-title]").textContent = t; $("[data-drawer-body]").innerHTML = body; $("[data-drawer]").hidden = false; }
  $("[data-drawer-close]").onclick = function () { $("[data-drawer]").hidden = true; };
  $("[data-drawer]").addEventListener("click", function (e) { if (e.target === e.currentTarget) e.currentTarget.hidden = true; });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") $("[data-drawer]").hidden = true; });

  var LOAD = { overview: loadOverview, lessons: loadLessons, features: loadFeatures, devices: loadDevices };
  function render() {
    $("[data-err]").hidden = true;
    $$("[data-range]").forEach(function (b) { b.classList.toggle("on", b.getAttribute("data-range") === state.range); });
    $$("[data-tab]").forEach(function (b) { var on = b.getAttribute("data-tab") === state.tab; b.classList.toggle("on", on); b.setAttribute("aria-selected", on); });
    $$("[data-panel]").forEach(function (p) { p.hidden = p.getAttribute("data-panel") !== state.tab; });
    LOAD[state.tab]().catch(showErr);
  }
  $$("[data-range]").forEach(function (b) { b.onclick = function () { state.range = b.getAttribute("data-range"); localStorage.setItem("zstats-range", state.range); render(); }; });
  $$("[data-tab]").forEach(function (b) { b.onclick = function () { state.tab = b.getAttribute("data-tab"); localStorage.setItem("zstats-tab", state.tab); render(); }; });
  $("[data-refresh]").onclick = render;
  fetch("/site-map.json").then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; })
    .then(function (s) { state.site = s || { pages: {}, modules: [] }; render(); });
  setInterval(function () { if (!document.hidden && state.tab === "overview") render(); }, 60000);
})();
