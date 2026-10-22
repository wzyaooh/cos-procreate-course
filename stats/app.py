#!/usr/bin/env python3
"""张宇涵的cos后期Procreate 自学站：轻量统计服务。

- POST /api/e            接收前端上报（匿名设备编号 + 事件）
- /stats/                看板（需要登录）
- /stats/api/...         看板数据
只用 Python 标准库，数据存在 SQLite（默认 /data/stats.db）。

环境变量：
  STATS_PASSWORD_HASH   看板密码的哈希，用 tools/stats_password.py 生成（必填，否则看板无法登录）
  STATS_SECRET          登录 Cookie 的签名密钥（建议填，tools/stats_password.py 会一起生成）
  STATS_RETENTION_DAYS  按设备的原始记录保留几天，默认 2；每日汇总一直保留
  STATS_UTC_OFFSET      统计按哪个时区分天，默认 8（北京时间）
  STATS_DB              数据库路径，默认 /data/stats.db
  STATS_PORT            监听端口，默认 8000
"""
import csv
import hashlib
import hmac
import io
import json
import os
import re
import secrets
import sqlite3
import sys
import threading
import time
import traceback
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hll import HLL, merged_count  # noqa: E402
from uaparse import is_bot, parse as parse_ua  # noqa: E402

HERE = Path(__file__).resolve().parent
STATIC = HERE / "static"
DB_PATH = os.environ.get("STATS_DB", "/data/stats.db")
RETENTION_DAYS = max(1, int(os.environ.get("STATS_RETENTION_DAYS", "2") or 2))
TZ = timezone(timedelta(hours=float(os.environ.get("STATS_UTC_OFFSET", "8") or 8)))
PASSWORD_HASH = os.environ.get("STATS_PASSWORD_HASH", "").strip()
SECRET = (os.environ.get("STATS_SECRET", "").strip() or secrets.token_hex(32)).encode()
COOKIE = "zstats"
COOKIE_DAYS = 30
ROLLUP_EVERY = 300  # 秒

ID_RE = re.compile(r"^[0-9a-f]{32}$")
SID_RE = re.compile(r"^[0-9a-f]{16}$")
PATH_RE = re.compile(r"^/[\w\-./%]*$")
EVENT_TYPES = {"view", "time", "read", "act", "search", "link", "progress"}
MODULE_ORDER = ["m0", "m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8"]

# ---------------------------------------------------------------- 数据库
SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS devices(
  id TEXT PRIMARY KEY, first_seen INT, last_seen INT, dtype TEXT, os TEXT, browser TEXT,
  screen TEXT, standalone INT DEFAULT 0, lang TEXT, tz TEXT, done_json TEXT, hw INT DEFAULT 0, last_path TEXT);
CREATE TABLE IF NOT EXISTS sessions(
  id TEXT PRIMARY KEY, device_id TEXT, start INT, last INT, entry TEXT);
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT, session_id TEXT, ts INT, type TEXT,
  path TEXT, name TEXT, value TEXT, num REAL);
CREATE INDEX IF NOT EXISTS ev_ts ON events(ts);
CREATE INDEX IF NOT EXISTS ev_dev ON events(device_id, ts);
CREATE INDEX IF NOT EXISTS ev_type ON events(type, ts);
CREATE TABLE IF NOT EXISTS agg_day(day TEXT PRIMARY KEY, hll BLOB, devices INT, new_devices INT, sessions INT,
  views INT, seconds INT, standalone INT);
CREATE TABLE IF NOT EXISTS agg_page(day TEXT, path TEXT, views INT, seconds INT, hll BLOB, PRIMARY KEY(day, path));
CREATE TABLE IF NOT EXISTS agg_section(day TEXT, path TEXT, section TEXT, title TEXT, hll BLOB, PRIMARY KEY(day, path, section));
CREATE TABLE IF NOT EXISTS agg_feature(day TEXT, name TEXT, count INT, hll BLOB, PRIMARY KEY(day, name));
CREATE TABLE IF NOT EXISTS agg_search(day TEXT, q TEXT, count INT, zero INT, hll BLOB, PRIMARY KEY(day, q));
CREATE TABLE IF NOT EXISTS agg_link(day TEXT, url TEXT, count INT, hll BLOB, PRIMARY KEY(day, url));
CREATE TABLE IF NOT EXISTS agg_dim(day TEXT, dim TEXT, key TEXT, hll BLOB, PRIMARY KEY(day, dim, key));
CREATE TABLE IF NOT EXISTS agg_progress(day TEXT, bucket TEXT, devices INT, PRIMARY KEY(day, bucket));
CREATE TABLE IF NOT EXISTS agg_done(day TEXT, lesson TEXT, count INT, PRIMARY KEY(day, lesson));
CREATE TABLE IF NOT EXISTS meta(k TEXT PRIMARY KEY, v TEXT);
"""


class DB:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        with self.lock:
            self.conn.executescript(SCHEMA)

    def q(self, sql, args=()):
        with self.lock:
            return self.conn.execute(sql, args).fetchall()

    def one(self, sql, args=()):
        r = self.q(sql, args)
        return r[0] if r else None

    def tx(self, fn):
        with self.lock:
            self.conn.execute("BEGIN")
            try:
                out = fn(self.conn)
                self.conn.execute("COMMIT")
                return out
            except Exception:
                self.conn.execute("ROLLBACK")
                raise


db = None


# ---------------------------------------------------------------- 时间
def now_ms():
    return int(time.time() * 1000)


def day_of(ms):
    return datetime.fromtimestamp(ms / 1000, TZ).strftime("%Y-%m-%d")


def day_start_ms(day):
    d = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=TZ)
    return int(d.timestamp() * 1000)


def today():
    return day_of(now_ms())


def days_back(n):
    """最近 n 天（含今天），从早到晚"""
    t = datetime.fromtimestamp(time.time(), TZ).date()
    return [(t - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(n - 1, -1, -1)]


# ---------------------------------------------------------------- 接收
def clip(v, n):
    if v is None:
        return None
    return str(v)[:n]


def clean_path(p):
    p = clip(p, 200) or "/"
    p = p.split("?")[0].split("#")[0]
    return p if PATH_RE.match(p) else "/"


def bucket_of(done):
    """学习进度：完成课里最靠后的模块"""
    mods = [x.split("-")[0] for x in done if isinstance(x, str) and re.match(r"^m\d-\d\d$", x)]
    if not mods:
        return "未开始"
    return max(mods, key=lambda m: MODULE_ORDER.index(m) if m in MODULE_ORDER else -1).upper()


_rate = {}
_rate_lock = threading.Lock()


def rate_ok(key, limit, window=60):
    t = time.time()
    with _rate_lock:
        arr = [x for x in _rate.get(key, []) if t - x < window]
        if len(arr) >= limit:
            _rate[key] = arr
            return False
        arr.append(t)
        _rate[key] = arr
        if len(_rate) > 20000:
            for k in list(_rate)[:5000]:
                _rate.pop(k, None)
        return True


def ingest(payload, ua):
    if not isinstance(payload, dict) or payload.get("v") != 1:
        return False
    did, sid = payload.get("d"), payload.get("s")
    if not (isinstance(did, str) and ID_RE.match(did) and isinstance(sid, str) and SID_RE.match(sid)):
        return False
    if is_bot(ua) or not rate_ok("d:" + did, 120):
        return False
    evs = payload.get("e")
    if not isinstance(evs, list) or not evs:
        return False
    c = payload.get("c") if isinstance(payload.get("c"), dict) else {}
    try:
        touch = int(c.get("tp") or 0)
    except (TypeError, ValueError):
        touch = 0
    dtype, os_, browser = parse_ua(ua, touch)
    screen = f"{int(c.get('sw') or 0)}×{int(c.get('sh') or 0)}" if str(c.get("sw", "")).isdigit() else ""
    standalone = 1 if c.get("sa") in (1, True, "1") else 0
    lang, tz = clip(c.get("lg"), 20) or "", clip(c.get("tz"), 40) or ""
    server_now = now_ms()

    rows, progress, last_path = [], None, None
    for e in evs[:100]:
        if not isinstance(e, dict) or e.get("t") not in EVENT_TYPES:
            continue
        try:
            ts = int(e.get("ts") or server_now)
        except (TypeError, ValueError):
            ts = server_now
        if abs(ts - server_now) > 86400_000:  # 设备时间不准时用服务器时间
            ts = server_now
        t, p = e["t"], clean_path(e.get("p"))
        name = value = None
        num = None
        if t == "view":
            value = clip(e.get("r"), 120)
            last_path = p
        elif t == "time":
            try:
                num = max(0, min(int(e.get("sec") or 0), 3600))
            except (TypeError, ValueError):
                continue
            if not num:
                continue
        elif t == "read":
            name, value = clip(e.get("id"), 80), clip(e.get("tt"), 80)
            if not name:
                continue
        elif t == "act":
            name, value = clip(e.get("n"), 40), clip(e.get("v"), 120)
            if not name:
                continue
            num = 1 if e.get("on") in (None, 1, True) else 0
        elif t == "search":
            value = (clip(e.get("q"), 60) or "").strip()
            if not value:
                continue
            try:
                num = int(e.get("hits") or 0)
            except (TypeError, ValueError):
                num = 0
        elif t == "link":
            value = clip(e.get("u"), 300)
            if not value or not value.startswith(("http://", "https://")):
                continue
        elif t == "progress":
            done = e.get("done") if isinstance(e.get("done"), list) else []
            done = [clip(x, 10) for x in done if isinstance(x, str) and re.match(r"^m\d-\d\d$", x)][:60]
            try:
                hw = int(e.get("hw") or 0)
            except (TypeError, ValueError):
                hw = 0
            progress = (done, hw)
            name, value, num = bucket_of(done), json.dumps(done), len(done)
        rows.append((did, sid, ts, t, p, name, value, num))
    if not rows:
        return False

    def write(conn):
        first_ts = min(r[2] for r in rows)
        last_ts = max(r[2] for r in rows)
        conn.execute(
            "INSERT INTO devices(id, first_seen, last_seen, dtype, os, browser, screen, standalone, lang, tz) "
            "VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET last_seen=max(last_seen, excluded.last_seen), "
            "dtype=excluded.dtype, os=excluded.os, browser=excluded.browser, screen=excluded.screen, "
            "standalone=max(standalone, excluded.standalone), lang=excluded.lang, tz=excluded.tz",
            (did, first_ts, last_ts, dtype, os_, browser, screen, standalone, lang, tz))
        if progress:
            conn.execute("UPDATE devices SET done_json=?, hw=? WHERE id=?", (json.dumps(progress[0]), progress[1], did))
        if last_path:
            conn.execute("UPDATE devices SET last_path=? WHERE id=?", (last_path, did))
        entry = next((r[4] for r in rows if r[3] == "view"), rows[0][4])
        conn.execute(
            "INSERT INTO sessions(id, device_id, start, last, entry) VALUES(?,?,?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET last=max(last, excluded.last), start=min(start, excluded.start)",
            (sid, did, first_ts, last_ts, entry))
        conn.executemany("INSERT INTO events(device_id, session_id, ts, type, path, name, value, num) VALUES(?,?,?,?,?,?,?,?)", rows)

    db.tx(write)
    return True


# ---------------------------------------------------------------- 汇总和清理
def collect(s, e):
    """把 [s, e) 之间的原始记录按页面、小节、功能……分组，每组带上精确的设备集合。"""
    ev = db.q("SELECT device_id, session_id, ts, type, path, name, value, num FROM events WHERE ts>=? AND ts<?", (s, e))
    devs_active = {r["device_id"] for r in ev}
    dev_info = {}
    if devs_active:
        qs = ",".join("?" * len(devs_active))
        for r in db.q(f"SELECT * FROM devices WHERE id IN ({qs})", tuple(devs_active)):
            dev_info[r["id"]] = r

    new_dev = db.one("SELECT count(*) c FROM devices WHERE first_seen>=? AND first_seen<?", (s, e))["c"]
    n_sess = len({r["session_id"] for r in ev})
    views = sum(1 for r in ev if r["type"] == "view")
    secs = int(sum(r["num"] or 0 for r in ev if r["type"] == "time"))
    standalone = sum(1 for d in devs_active if d in dev_info and dev_info[d]["standalone"])

    pages, sections, feats, searches, links, done = {}, {}, {}, {}, {}, {}
    last_prog = {}
    for r in ev:
        t, p, d = r["type"], r["path"], r["device_id"]
        if t in ("view", "time"):
            pg = pages.setdefault(p, [0, 0, set()])
            pg[2].add(d)
            if t == "view":
                pg[0] += 1
            else:
                pg[1] += int(r["num"] or 0)
        elif t == "read":
            sc = sections.setdefault((p, r["name"]), [r["value"] or "", set()])
            sc[1].add(d)
        elif t == "act":
            if r["num"] == 0:
                continue
            f = feats.setdefault(r["name"], [0, set()])
            f[0] += 1
            f[1].add(d)
            if r["name"] == "lesson_done" and r["value"]:
                done[r["value"]] = done.get(r["value"], 0) + 1
        elif t == "search":
            k = r["value"].lower()
            sr = searches.setdefault(k, [0, 0, set()])
            sr[0] += 1
            sr[1] = 1 if (r["num"] or 0) == 0 else 0  # 同一个词结果数是固定的，取最后一次
            sr[2].add(d)
        elif t == "link":
            lk = links.setdefault(r["value"], [0, set()])
            lk[0] += 1
            lk[1].add(d)
        elif t == "progress":
            if d not in last_prog or r["ts"] >= last_prog[d][0]:
                last_prog[d] = (r["ts"], r["name"])
    prog = {}
    for d in devs_active:
        b = last_prog[d][1] if d in last_prog else (bucket_of(json.loads(dev_info[d]["done_json"] or "[]")) if d in dev_info and dev_info[d]["done_json"] else "未开始")
        prog[b] = prog.get(b, 0) + 1
    dims = {}
    for d in devs_active:
        if d not in dev_info:
            continue
        for dim in ("dtype", "os", "browser"):
            dims.setdefault((dim, dev_info[d][dim] or "其他"), set()).add(d)
    return {"ev": ev, "devs": devs_active, "new": new_dev, "sessions": n_sess, "views": views, "secs": secs,
            "standalone": standalone, "pages": pages, "sections": sections, "feats": feats, "searches": searches,
            "links": links, "dims": dims, "prog": prog, "done": done}


def hll_of(ids, p=10):
    h = HLL(p)
    for i in ids:
        h.add(i)
    return h.dump()


def rollup_day(day):
    c = collect(day_start_ms(day), day_start_ms(day) + 86400_000)
    ev, pages, sections, feats, searches, links, dims = c["ev"], c["pages"], c["sections"], c["feats"], c["searches"], c["links"], c["dims"]

    def write(conn):
        for t in ("agg_day", "agg_page", "agg_section", "agg_feature", "agg_search", "agg_link", "agg_dim", "agg_progress", "agg_done"):
            conn.execute(f"DELETE FROM {t} WHERE day=?", (day,))
        if not ev:
            return
        conn.execute("INSERT INTO agg_day VALUES(?,?,?,?,?,?,?,?)", (day, hll_of(c["devs"]), len(c["devs"]), c["new"], c["sessions"], c["views"], c["secs"], c["standalone"]))
        conn.executemany("INSERT INTO agg_page VALUES(?,?,?,?,?)", [(day, p, v[0], v[1], hll_of(v[2], 8)) for p, v in pages.items()])
        conn.executemany("INSERT INTO agg_section VALUES(?,?,?,?,?)", [(day, k[0], k[1], v[0], hll_of(v[1], 8)) for k, v in sections.items()])
        conn.executemany("INSERT INTO agg_feature VALUES(?,?,?,?)", [(day, k, v[0], hll_of(v[1], 8)) for k, v in feats.items()])
        conn.executemany("INSERT INTO agg_search VALUES(?,?,?,?,?)", [(day, k, v[0], v[1], hll_of(v[2], 8)) for k, v in searches.items()])
        conn.executemany("INSERT INTO agg_link VALUES(?,?,?,?)", [(day, k, v[0], hll_of(v[1], 8)) for k, v in links.items()])
        conn.executemany("INSERT INTO agg_dim VALUES(?,?,?,?)", [(day, k[0], k[1], hll_of(v, 8)) for k, v in dims.items()])
        conn.executemany("INSERT INTO agg_progress VALUES(?,?,?)", [(day, k, v) for k, v in c["prog"].items()])
        conn.executemany("INSERT INTO agg_done VALUES(?,?,?)", [(day, k, v) for k, v in c["done"].items()])

    db.tx(write)


_rollup_lock = threading.Lock()


def rollup_and_purge():
    """重算原始记录还完整的那几天的汇总，再删掉超过保留期的原始记录。"""
    with _rollup_lock:
        cutoff = now_ms() - RETENTION_DAYS * 86400_000
        for day in days_back(RETENTION_DAYS + 2):
            if day_start_ms(day) >= cutoff:
                rollup_day(day)

        def purge(conn):
            conn.execute("DELETE FROM events WHERE ts<?", (cutoff,))
            conn.execute("DELETE FROM sessions WHERE last<?", (cutoff,))
            conn.execute("DELETE FROM devices WHERE last_seen<?", (cutoff,))
            conn.execute("INSERT OR REPLACE INTO meta VALUES('last_rollup', ?)", (str(now_ms()),))

        db.tx(purge)


def rollup_loop():
    while True:
        try:
            rollup_and_purge()
        except Exception:
            traceback.print_exc()
        time.sleep(ROLLUP_EVERY)


# ---------------------------------------------------------------- 看板数据
def range_days(qs):
    r = (qs.get("range") or ["7"])[0]
    if r == "all":
        first = db.one("SELECT min(day) d FROM agg_day")["d"] or today()
        n = (datetime.strptime(today(), "%Y-%m-%d") - datetime.strptime(first, "%Y-%m-%d")).days + 1
        return days_back(max(1, min(n, 3650)))
    try:
        n = int(r)
    except ValueError:
        n = 7
    return days_back(max(1, min(n, 3650)))


def exact(days):
    """所选的几天原始记录都还在（没超过保留期）时，直接从原始记录数设备，结果是精确的；否则返回 None，用汇总里的估算值。"""
    if day_start_ms(days[0]) < now_ms() - RETENTION_DAYS * 86400_000:
        return None
    return collect(day_start_ms(days[0]), day_start_ms(days[-1]) + 86400_000)


def in_days(days):
    return ",".join("?" * len(days)), tuple(days)


def api_overview(qs):
    rollup_day(today())
    days = range_days(qs)
    ph, args = in_days(days)
    rows = {r["day"]: r for r in db.q(f"SELECT * FROM agg_day WHERE day IN ({ph})", args)}
    series = [{"day": d, "devices": rows[d]["devices"] if d in rows else 0,
               "minutes": round((rows[d]["seconds"] if d in rows else 0) / 60, 1),
               "views": rows[d]["views"] if d in rows else 0,
               "new": rows[d]["new_devices"] if d in rows else 0} for d in days]
    ex = exact(days)
    devices = len(ex["devs"]) if ex else merged_count([r["hll"] for r in rows.values()])
    secs = sum(r["seconds"] for r in rows.values())
    dims = {}
    for r in db.q(f"SELECT dim, key, hll FROM agg_dim WHERE day IN ({ph})", args):
        dims.setdefault(r["dim"], {}).setdefault(r["key"], []).append(r["hll"])
    if ex:
        dims = {}
        for (dim, k), ids in ex["dims"].items():
            dims.setdefault(dim, []).append({"key": k, "devices": len(ids)})
        dims = {dim: sorted(v, key=lambda x: -x["devices"]) for dim, v in dims.items()}
    else:
        dims = {dim: sorted(({"key": k, "devices": merged_count(v, 8)} for k, v in kv.items()), key=lambda x: -x["devices"]) for dim, kv in dims.items()}
    online = db.one("SELECT count(DISTINCT device_id) c FROM events WHERE ts>?", (now_ms() - 3 * 60_000,))["c"]
    sa = sum(r["standalone"] for r in rows.values())
    dev_days = sum(r["devices"] for r in rows.values())
    return {
        "days": days, "series": series, "online": online,
        "cards": {"devices": devices, "new_devices": sum(r["new_devices"] for r in rows.values()),
                  "sessions": sum(r["sessions"] for r in rows.values()), "views": sum(r["views"] for r in rows.values()),
                  "seconds": secs, "avg_seconds_per_device": round(secs / devices) if devices else 0,
                  "standalone_ratio": round(sa / dev_days, 3) if dev_days else 0},
        "dims": dims, "retention_days": RETENTION_DAYS, "approx": ex is None and len(days) > 1,
    }


def api_pages(qs):
    rollup_day(today())
    days = range_days(qs)
    ph, args = in_days(days)
    acc = {}
    for r in db.q(f"SELECT path, views, seconds, hll FROM agg_page WHERE day IN ({ph})", args):
        a = acc.setdefault(r["path"], [0, 0, []])
        a[0] += r["views"]
        a[1] += r["seconds"]
        a[2].append(r["hll"])
    ex = exact(days)
    done = {r["lesson"]: r["c"] for r in db.q(f"SELECT lesson, sum(count) c FROM agg_done WHERE day IN ({ph}) GROUP BY lesson", args)}
    pages = []
    for p, (v, s, hl) in acc.items():
        n = len(ex["pages"][p][2]) if ex and p in ex["pages"] else merged_count(hl, 8)
        pages.append({"path": p, "views": v, "seconds": s, "devices": n, "avg_seconds": round(s / n) if n else 0})
    pages.sort(key=lambda x: -x["seconds"])
    prog_rows = db.q(f"SELECT day, bucket, devices FROM agg_progress WHERE day IN ({ph})", args)
    latest = {}
    for r in db.q("SELECT done_json FROM devices"):
        b = bucket_of(json.loads(r["done_json"] or "[]")) if r["done_json"] else "未开始"
        latest[b] = latest.get(b, 0) + 1
    return {"pages": pages, "done": done, "progress_daily": [dict(r) for r in prog_rows], "progress_now": latest,
            "retention_days": RETENTION_DAYS}


def api_sections(qs):
    days = range_days(qs)
    path = clean_path((qs.get("path") or ["/"])[0])
    ph, args = in_days(days)
    page_hll = [r["hll"] for r in db.q(f"SELECT hll FROM agg_page WHERE day IN ({ph}) AND path=?", args + (path,))]
    ex = exact(days)
    base = len(ex["pages"][path][2]) if ex and path in ex["pages"] else merged_count(page_hll, 8)
    acc = {}
    for r in db.q(f"SELECT section, title, hll FROM agg_section WHERE day IN ({ph}) AND path=?", args + (path,)):
        a = acc.setdefault(r["section"], [r["title"], []])
        a[1].append(r["hll"])
    def n_sec(k, blobs):
        if ex and (path, k) in ex["sections"]:
            return len(ex["sections"][(path, k)][1])
        return merged_count(blobs, 8)
    secs = [{"id": k, "title": v[0], "devices": n_sec(k, v[1])} for k, v in acc.items()]
    return {"path": path, "page_devices": base, "sections": secs}


def api_features(qs):
    rollup_day(today())
    days = range_days(qs)
    ph, args = in_days(days)
    ex = exact(days)
    exsets = {"agg_feature": (ex["feats"], 1), "agg_search": (ex["searches"], 2), "agg_link": (ex["links"], 1)} if ex else {}

    def merge(table, key, extra=""):
        acc = {}
        for r in db.q(f"SELECT * FROM {table} WHERE day IN ({ph})", args):
            a = acc.setdefault(r[key], {"count": 0, "hll": [], "zero": 0})
            a["count"] += r["count"]
            a["hll"].append(r["hll"])
            if extra:
                a["zero"] = max(a["zero"], r[extra])
        def ndev(k, blobs):
            if table in exsets and k in exsets[table][0]:
                return len(exsets[table][0][k][exsets[table][1]])
            return merged_count(blobs, 8)
        out = [{"key": k, "count": v["count"], "devices": ndev(k, v["hll"]), **({"zero": v["zero"]} if extra else {})} for k, v in acc.items()]
        return sorted(out, key=lambda x: -x["count"])

    return {"features": merge("agg_feature", "name"), "search": merge("agg_search", "q", "zero")[:200],
            "links": merge("agg_link", "url")[:200]}


def api_devices(qs):
    rows = db.q("SELECT * FROM devices ORDER BY last_seen DESC LIMIT 2000")
    agg = {r["device_id"]: r for r in db.q(
        "SELECT device_id, sum(CASE WHEN type='time' THEN num ELSE 0 END) secs, sum(CASE WHEN type='view' THEN 1 ELSE 0 END) views, "
        "count(DISTINCT session_id) sessions FROM events GROUP BY device_id")}
    out = []
    for r in rows:
        a = agg.get(r["id"])
        done = json.loads(r["done_json"] or "[]") if r["done_json"] else []
        out.append({"id": r["id"], "first_seen": r["first_seen"], "last_seen": r["last_seen"], "dtype": r["dtype"], "os": r["os"],
                    "browser": r["browser"], "screen": r["screen"], "standalone": r["standalone"], "lang": r["lang"],
                    "seconds": int(a["secs"] or 0) if a else 0, "views": a["views"] if a else 0, "sessions": a["sessions"] if a else 0,
                    "done": len(done), "progress": bucket_of(done), "hw": r["hw"], "last_path": r["last_path"]})
    return {"devices": out, "retention_days": RETENTION_DAYS}


def api_device(qs):
    did = (qs.get("id") or [""])[0]
    if not ID_RE.match(did):
        return {"error": "设备编号不对"}
    dev = db.one("SELECT * FROM devices WHERE id=?", (did,))
    if not dev:
        return {"error": "没有这台设备的记录（可能已超过保留期被删除）"}
    sessions = []
    for s in db.q("SELECT * FROM sessions WHERE device_id=? ORDER BY start DESC", (did,)):
        evs = db.q("SELECT ts, type, path, name, value, num FROM events WHERE session_id=? ORDER BY ts, id", (s["id"],))
        pages = {}
        for e in evs:
            if e["type"] in ("view", "time"):
                pg = pages.setdefault(e["path"], {"path": e["path"], "views": 0, "seconds": 0, "first": e["ts"]})
                pg["views"] += 1 if e["type"] == "view" else 0
                pg["seconds"] += int(e["num"] or 0) if e["type"] == "time" else 0
        timeline = [dict(e) for e in evs if e["type"] != "time"]
        sessions.append({"id": s["id"], "start": s["start"], "last": s["last"], "entry": s["entry"],
                         "seconds": sum(p["seconds"] for p in pages.values()),
                         "pages": sorted(pages.values(), key=lambda x: x["first"]), "timeline": timeline})
    d = dict(dev)
    d["done"] = json.loads(d.pop("done_json") or "[]") if d.get("done_json") else []
    d.pop("done_json", None)
    return {"device": d, "sessions": sessions, "retention_days": RETENTION_DAYS}


def csv_export(qs):
    which = (qs.get("t") or ["daily"])[0]
    out = io.StringIO()
    w = csv.writer(out)
    if which == "daily":
        w.writerow(["日期", "设备数", "新设备", "访问次数", "页面浏览", "总时长（分钟）", "主屏幕打开的设备"])
        for r in db.q("SELECT * FROM agg_day ORDER BY day"):
            w.writerow([r["day"], r["devices"], r["new_devices"], r["sessions"], r["views"], round(r["seconds"] / 60, 1), r["standalone"]])
    elif which == "pages":
        w.writerow(["日期", "页面", "浏览次数", "停留（分钟）"])
        for r in db.q("SELECT * FROM agg_page ORDER BY day, path"):
            w.writerow([r["day"], r["path"], r["views"], round(r["seconds"] / 60, 1)])
    elif which == "search":
        w.writerow(["日期", "搜索词", "次数", "没有结果"])
        for r in db.q("SELECT * FROM agg_search ORDER BY day, count DESC"):
            w.writerow([r["day"], r["q"], r["count"], "是" if r["zero"] else ""])
    elif which == "events":
        w.writerow(["时间", "设备", "访问", "类型", "页面", "名称", "值", "数值"])
        for r in db.q("SELECT * FROM events ORDER BY ts"):
            w.writerow([datetime.fromtimestamp(r["ts"] / 1000, TZ).strftime("%Y-%m-%d %H:%M:%S"), r["device_id"][:8], r["session_id"][:6],
                        r["type"], r["path"], r["name"] or "", r["value"] or "", "" if r["num"] is None else r["num"]])
    else:
        return None
    return ("﻿" + out.getvalue()).encode("utf-8"), f"stats-{which}-{today()}.csv"


API = {"overview": api_overview, "pages": api_pages, "sections": api_sections, "features": api_features,
       "devices": api_devices, "device": api_device}


# ---------------------------------------------------------------- 登录
def verify_password(pw: str) -> bool:
    """STATS_PASSWORD_HASH 格式：pbkdf2:sha256:迭代次数:盐(hex):哈希(hex)"""
    try:
        kind, algo, it, salt, want = PASSWORD_HASH.split(":")
        assert kind == "pbkdf2"
        got = hashlib.pbkdf2_hmac(algo, pw.encode(), bytes.fromhex(salt), int(it)).hex()
        return hmac.compare_digest(got, want)
    except Exception:
        return False


def make_cookie():
    exp = str(int(time.time()) + COOKIE_DAYS * 86400)
    sig = hmac.new(SECRET, exp.encode(), hashlib.sha256).hexdigest()
    return f"{exp}.{sig}"


def cookie_ok(header):
    for part in (header or "").split(";"):
        k, _, v = part.strip().partition("=")
        if k == COOKIE and "." in v:
            exp, sig = v.split(".", 1)
            good = hmac.new(SECRET, exp.encode(), hashlib.sha256).hexdigest()
            if hmac.compare_digest(sig, good) and exp.isdigit() and int(exp) > time.time():
                return True
    return False


LOGIN_HTML = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>登录 - 学习统计</title><style>
:root{{color-scheme:light}}body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#FFFDF5;color:#1E293B;
font-family:system-ui,-apple-system,"PingFang SC","Microsoft YaHei",sans-serif}}form{{width:min(360px,90vw);background:#fff;border:2px solid #1E293B;
border-radius:18px;box-shadow:6px 6px 0 #7C3AED;padding:28px 24px}}h1{{font-size:22px;margin:0 0 6px}}p{{margin:0 0 18px;color:#475569;font-size:15px}}
input{{width:100%;box-sizing:border-box;font:inherit;font-size:17px;padding:10px 14px;border:2px solid #1E293B;border-radius:12px;margin-bottom:14px}}
button{{width:100%;font:inherit;font-size:17px;font-weight:800;padding:10px;color:#fff;background:#7C3AED;border:2px solid #1E293B;border-radius:999px;
box-shadow:4px 4px 0 #1E293B;cursor:pointer}}.err{{color:#B91C1C;font-weight:700}}</style></head><body>
<form method="post" action="/stats/login"><h1>学习统计</h1><p>张宇涵的cos后期Procreate 自学站</p>{msg}
<input type="password" name="password" placeholder="看板密码" autocomplete="current-password" required autofocus>
<button type="submit">登录</button></form></body></html>"""


_login_fail = []
_login_lock = threading.Lock()


# ---------------------------------------------------------------- HTTP
class Handler(BaseHTTPRequestHandler):
    server_version = "stats"
    sys_version = ""

    def log_message(self, fmt, *args):  # 不记录访问日志（里面有 IP）
        pass

    def send(self, code, body=b"", ctype="text/plain; charset=utf-8", headers=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Robots-Tag", "noindex, nofollow")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def json(self, obj, code=200):
        self.send(code, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

    def authed(self):
        return cookie_ok(self.headers.get("Cookie"))

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        u = urlparse(self.path)
        path, qs = u.path, parse_qs(u.query)
        if path == "/healthz":
            return self.send(200, "ok")
        if path in ("/stats", "/stats/login") and not self.authed():
            return self.send(200, LOGIN_HTML.format(msg=""), "text/html; charset=utf-8") if path == "/stats/login" else \
                self.send(302, "", headers={"Location": "/stats/login"})
        if not path.startswith("/stats"):
            return self.send(404, "not found")
        if not self.authed():
            if path.startswith("/stats/api/"):
                return self.json({"error": "请先登录"}, 401)
            return self.send(302, "", headers={"Location": "/stats/login"})
        if path in ("/stats", "/stats/login"):
            return self.send(302, "", headers={"Location": "/stats/"})
        if path == "/stats/":
            return self.static("index.html")
        if path.startswith("/stats/static/"):
            return self.static(path[len("/stats/static/"):])
        if path.startswith("/stats/api/"):
            name = path[len("/stats/api/"):].strip("/")
            if name == "export.csv":
                r = csv_export(qs)
                if not r:
                    return self.send(404, "not found")
                return self.send(200, r[0], "text/csv; charset=utf-8", {"Content-Disposition": f"attachment; filename={r[1]}"})
            fn = API.get(name)
            if not fn:
                return self.json({"error": "没有这个接口"}, 404)
            try:
                return self.json(fn(qs))
            except Exception as e:
                traceback.print_exc()
                return self.json({"error": str(e)}, 500)
        return self.send(404, "not found")

    def static(self, rel):
        f = (STATIC / rel).resolve()
        if STATIC.resolve() not in f.parents or not f.is_file():
            return self.send(404, "not found")
        ctype = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
                 ".svg": "image/svg+xml"}.get(f.suffix, "application/octet-stream")
        return self.send(200, f.read_bytes(), ctype)

    def read_body(self, limit):
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > limit:
            return None
        return self.rfile.read(n)

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/e":
            origin = self.headers.get("Origin")
            host = self.headers.get("X-Forwarded-Host") or self.headers.get("Host") or ""
            if origin and urlparse(origin).netloc != host:
                return self.send(204)
            body = self.read_body(64 * 1024)
            try:
                ingest(json.loads(body or b"null"), self.headers.get("User-Agent", ""))
            except Exception:
                traceback.print_exc()
            return self.send(204)
        if path == "/stats/login":
            with _login_lock:
                t = time.time()
                _login_fail[:] = [x for x in _login_fail if t - x < 900]
                if len(_login_fail) >= 10:
                    return self.send(429, LOGIN_HTML.format(msg='<p class="err">试错次数太多，15 分钟后再试。</p>'), "text/html; charset=utf-8")
            body = self.read_body(4096) or b""
            pw = (parse_qs(body.decode("utf-8", "replace")).get("password") or [""])[0]
            if PASSWORD_HASH and verify_password(pw):
                return self.send(303, "", headers={"Location": "/stats/",
                                                   "Set-Cookie": f"{COOKIE}={make_cookie()}; Max-Age={COOKIE_DAYS * 86400}; Path=/stats; HttpOnly; Secure; SameSite=Strict"})
            with _login_lock:
                _login_fail.append(time.time())
            msg = "密码不对。" if PASSWORD_HASH else "服务器还没有设置看板密码（STATS_PASSWORD_HASH）。"
            return self.send(401, LOGIN_HTML.format(msg=f'<p class="err">{msg}</p>'), "text/html; charset=utf-8")
        if path == "/stats/logout":
            return self.send(303, "", headers={"Location": "/stats/login", "Set-Cookie": f"{COOKIE}=; Max-Age=0; Path=/stats; HttpOnly; Secure; SameSite=Strict"})
        return self.send(404, "not found")


def main():
    global db
    db = DB(DB_PATH)
    if not PASSWORD_HASH:
        print("提示：没有设置 STATS_PASSWORD_HASH，看板无法登录。用 tools/stats_password.py 生成。", flush=True)
    threading.Thread(target=rollup_loop, daemon=True).start()
    port = int(os.environ.get("STATS_PORT", "8000"))
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    srv.daemon_threads = True
    print(f"stats 服务已启动：端口 {port}，数据库 {DB_PATH}，原始记录保留 {RETENTION_DAYS} 天", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
