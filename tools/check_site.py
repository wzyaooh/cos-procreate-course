#!/usr/bin/env python3
"""检查构建结果：站内链接、页内锚点、搜索索引地址、残留的未解析标记。

用法：python tools/check_site.py site      （site 是 build.py --out 的目录）
有问题时退出码为 1。
"""
import glob
import json
import os
import re
import sys

root = sys.argv[1] if len(sys.argv) > 1 else "site"
os.chdir(root)
ids, bad, n = {}, [], 0
pages = glob.glob("**/*.html", recursive=True)
for f in pages:
    ids[f] = set(re.findall(r'id="([^"]+)"', open(f, encoding="utf-8").read()))


def target(path):
    t = path.split("?")[0].lstrip("/")
    return (t + "index.html") if (t == "" or t.endswith("/")) else t


for f in pages:
    s = open(f, encoding="utf-8").read()
    for h in re.findall(r'(?:href|src)="(/[^"]*)"', s):
        n += 1
        path, _, frag = h.partition("#")
        t = target(path)
        if not os.path.exists(t):
            bad.append(f"{f}: 链接到不存在的文件 {h}")
        elif frag and t.endswith(".html") and frag not in ids.get(t, set()):
            bad.append(f"{f}: 锚点不存在 {h}")
    for h in re.findall(r'href="#([^"]+)"', s):
        if h not in ids[f]:
            bad.append(f"{f}: 页内锚点不存在 #{h}")
    if re.search(r"\[\[|^:::|(href|src)=\"(lesson|problem|page|static):", s, re.M):
        bad.append(f"{f}: 有没解析的标记（[[、:::、lesson: 等）")

idx = open("search-index.js", encoding="utf-8").read()
entries = json.loads(idx[idx.index("=") + 1:].rstrip(";\n"))
for x in entries:
    p, _, fr = x["u"].partition("#")
    t = target(p)
    if not os.path.exists(t) or (fr and fr not in ids.get(t, set())):
        bad.append(f"搜索索引指向不存在的位置：{x['u']}")

for b in bad:
    print("问题", b)
print(f"\n{len(pages)} 个页面，{n} 个站内链接，{len(entries)} 条搜索索引；问题 {len(bad)} 处")
sys.exit(1 if bad else 0)
