#!/usr/bin/env python3
"""统计服务自测：用临时数据库模拟几台设备的上报，检查汇总和保留期清理。CI 里会运行。"""
import json
import os
import sys
import tempfile
import time

tmp = tempfile.mkdtemp()
os.environ["STATS_DB"] = os.path.join(tmp, "t.db")
os.environ["STATS_RETENTION_DAYS"] = "2"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app  # noqa: E402
from hll import HLL  # noqa: E402

app.db = app.DB(os.environ["STATS_DB"])
IPAD = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
PHONE = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0"
now = app.now_ms()


def send(did, sid, ua, evs, touch=5):
    return app.ingest({"v": 1, "d": did, "s": sid, "c": {"sw": 1180, "sh": 820, "tp": touch, "sa": 1}, "e": evs}, ua)


ok = True


def check(name, cond):
    global ok
    print(("通过 " if cond else "失败 ") + name)
    ok = ok and cond


d1, d2 = "a" * 32, "b" * 32
check("接收 iPad 上报", send(d1, "1" * 16, IPAD, [
    {"t": "view", "p": "/m5/04/", "ts": now}, {"t": "time", "p": "/m5/04/", "ts": now + 1000, "sec": 120},
    {"t": "read", "p": "/m5/04/", "id": "legs", "tt": "第 3 步：拉长腿", "ts": now},
    {"t": "act", "p": "/m5/04/", "n": "lesson_done", "v": "m5-04", "on": 1, "ts": now},
    {"t": "search", "p": "/search/", "q": "双立体", "hits": 7, "ts": now},
    {"t": "search", "p": "/search/", "q": "不存在的词", "hits": 0, "ts": now},
    {"t": "progress", "done": ["m0-01", "m5-04"], "hw": 2, "ts": now}]))
check("接收手机上报", send(d2, "2" * 16, PHONE, [{"t": "view", "p": "/", "ts": now}, {"t": "time", "p": "/", "ts": now, "sec": 30}], touch=5))
check("拒绝爬虫", not send("c" * 32, "3" * 16, "Googlebot/2.1", [{"t": "view", "p": "/", "ts": now}]))
check("拒绝格式不对的设备编号", not send("xyz", "3" * 16, IPAD, [{"t": "view", "p": "/", "ts": now}]))
check("单条时长封顶 3600 秒", send(d2, "2" * 16, PHONE, [{"t": "time", "p": "/", "ts": now, "sec": 99999}]) and
      app.db.one("SELECT max(num) m FROM events")["m"] == 3600)

app.rollup_and_purge()
ov = app.api_overview({"range": ["7"]})
check("今天 2 台设备", ov["cards"]["devices"] == 2)
check("总时长 120+30+3600 秒", ov["cards"]["seconds"] == 3750)
dims = {d["key"]: d["devices"] for d in ov["dims"]["dtype"]}
check("设备类型识别 iPad / 手机", dims.get("iPad") == 1 and dims.get("手机") == 1)
br = {d["key"] for d in ov["dims"]["browser"]}
check("浏览器识别 Safari / 微信", {"Safari", "微信"} <= br)
pg = {p["path"]: p for p in app.api_pages({"range": ["7"]})["pages"]}
check("5.4 课停留 120 秒", pg["/m5/04/"]["seconds"] == 120)
check("学完 5.4 记 1 次", app.api_pages({"range": ["7"]})["done"].get("m5-04") == 1)
check("进度分布：M5", app.api_pages({"range": ["7"]})["progress_now"].get("M5") == 1)
ft = app.api_features({"range": ["7"]})
sq = {s["key"]: s for s in ft["search"]}
check("搜索词和无结果标记", sq["双立体"]["zero"] == 0 and sq["不存在的词"]["zero"] == 1)
sc = app.api_sections({"range": ["7"], "path": ["/m5/04/"]})
check("小节阅读", sc["sections"][0]["id"] == "legs" and sc["page_devices"] == 1)
dv = app.api_device({"id": [d1]})
check("设备详情时间线", dv["sessions"][0]["seconds"] == 120 and len(dv["sessions"][0]["timeline"]) >= 5)

# 保留期：把数据挪到 3 天前，清理后原始记录没了，但那天的汇总还在
old = now - 3 * 86400_000
old_day = app.day_of(old)
app.rollup_day(old_day)  # 先确认空的那天不会出错
app.db.q("UPDATE events SET ts=ts-?", (3 * 86400_000,))
app.db.q("UPDATE devices SET first_seen=first_seen-?, last_seen=last_seen-?", (3 * 86400_000, 3 * 86400_000))
app.db.q("UPDATE sessions SET start=start-?, last=last-?", (3 * 86400_000, 3 * 86400_000))
app.rollup_day(old_day)  # 模拟当时（数据完整时）已经汇总过
app.rollup_and_purge()
check("超过 2 天的原始记录被删除", app.db.one("SELECT count(*) c FROM events")["c"] == 0 and app.db.one("SELECT count(*) c FROM devices")["c"] == 0)
check("超过 2 天的每日汇总保留", app.db.one("SELECT devices FROM agg_day WHERE day=?", (old_day,))["devices"] == 2)
ov7 = app.api_overview({"range": ["7"]})
check("7 天设备数仍然是 2（来自汇总）", ov7["cards"]["devices"] == 2)

# 这两个设备编号在 HLL 里落在同一个寄存器，估算会少算一台；原始记录还在时必须精确
x1, x2 = "69f993f764d65e59f5f654e8b9bbe598", "d5cf2bed4fe79bb042ff1509e44f10ba"
for x in (x1, x2):
    send(x, x[:16], IPAD, [{"t": "view", "p": "/m1/01/", "ts": now}, {"t": "act", "p": "/m1/01/", "n": "toc_open", "ts": now}])
app.rollup_and_purge()
check("保留期内设备数精确（HLL 冲突的两台也算 2）", app.api_overview({"range": ["1"]})["cards"]["devices"] == 2
      and app.db.one("SELECT devices FROM agg_day WHERE day=?", (app.today(),))["devices"] == 2)
pg1 = {p["path"]: p for p in app.api_pages({"range": ["1"]})["pages"]}
fe1 = {f["key"]: f for f in app.api_features({"range": ["1"]})["features"]}
check("保留期内页面、功能的设备数精确", pg1["/m1/01/"]["devices"] == 2 and fe1["toc_open"]["devices"] == 2)

h = HLL(10)
for i in range(5000):
    h.add(f"dev{i}")
check(f"HLL 估算误差小于 5%（5000 → {h.count()}）", abs(h.count() - 5000) / 5000 < 0.05)

app.PASSWORD_HASH = "pbkdf2:sha256:1000:" + "00" * 16 + ":" + __import__("hashlib").pbkdf2_hmac("sha256", b"pw123456", b"\0" * 16, 1000).hex()
check("密码校验", app.verify_password("pw123456") and not app.verify_password("wrong"))
c = app.make_cookie()
check("登录 Cookie 校验", app.cookie_ok(f"zstats={c}") and not app.cookie_ok("zstats=1.abc"))
print("\n全部通过" if ok else "\n有失败项")
sys.exit(0 if ok else 1)
