#!/usr/bin/env python3
"""检查 content/resources.yaml 里的链接还能不能打开。

用法：python tools/check_links.py
B 站、知乎等网站会拦截脚本访问，返回 403/412 不一定是链接失效，需要用浏览器手动打开确认。
"""
import concurrent.futures as cf
import urllib.error
import urllib.request
from pathlib import Path

import yaml

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
BLOCKERS = ("bilibili.com", "zhihu.com", "csdn.net", "smzdm.com", "zcool.com.cn", "baike.baidu.com")


def check(r):
    req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return r, resp.status, ""
    except urllib.error.HTTPError as e:
        return r, e.code, ""
    except Exception as e:  # 超时、DNS 等
        return r, 0, type(e).__name__


def main():
    rs = yaml.safe_load(open(Path(__file__).resolve().parent.parent / "content" / "resources.yaml", encoding="utf-8"))
    bad = manual = 0
    with cf.ThreadPoolExecutor(8) as ex:
        for r, code, err in ex.map(check, rs):
            if 200 <= code < 400:
                mark = "正常"
            elif any(b in r["url"] for b in BLOCKERS):
                mark = "需手动确认"; manual += 1
            else:
                mark = "可能失效"; bad += 1
            print(f"{mark:6} {code or err:>4}  {r['id']:28} {r['url']}")
    print(f"\n共 {len(rs)} 条：可能失效 {bad} 条，需手动确认 {manual} 条")


if __name__ == "__main__":
    main()
