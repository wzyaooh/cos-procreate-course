#!/usr/bin/env python3
"""内容检查：用词、步骤卡、数字写法。

用法：
  python tools/lint.py                 # 检查全部
  python tools/lint.py m3-03 m5-06     # 只检查指定的课（按文件名前缀）
  python tools/lint.py --numbers       # 同时列出数字写法问题（较多，按需开）

退出码：有"错误"时为 1。数字写法只作提示，不影响退出码。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

# 错误写法 → 正确写法（按 Procreate 官方中文手册）
TERMS = [
    (r"仿制(?!图章)", "克隆（Procreate 里叫「克隆」）"),
    (r"仿制图章", "克隆（PS 的仿制图章，在 Procreate 里叫「克隆」；只在对照 PS 时可以出现）"),
    (r"双立方", "双立体"),
    (r"Alpha ?锁定", "阿尔法锁定"),
    (r"色彩平衡", "颜色平衡（Procreate 的叫法）"),
    (r"^(?!.*(PS|Photoshop|找不到)).*「叠加」", "覆盖（PS 里叫「叠加」；不提 PS 时应写「覆盖」）"),
    (r"「自由形状」", "自由变换"),
    (r"^(?=.*液化).*扭转", "转动（液化模式）"),
]
# 这些文件允许出现对照用的 PS 叫法
TERM_EXEMPT = {"ps-procreate.md"}  # 对照表本来就要写 PS 的叫法

NUM = re.compile(r"\d+(?:\.\d+)?\s*%")
QUALIFIER = re.compile(r"为准|停|看到|直到|左右|起点|开始|试|大约|约|一般|以内|不超过|参考|默认|上限|下限|最多|最少|至少|出处|官方|手册|计算|算出|=|＝|÷|×")


def iter_files(prefixes):
    files = sorted((CONTENT / "lessons").glob("*.md")) + sorted((CONTENT / "problems").glob("*.md")) + sorted((CONTENT / "pages").glob("*.md"))
    for f in files:
        if prefixes and not any(f.name.startswith(p) for p in prefixes):
            continue
        yield f


def body_of(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def check(f, want_numbers):
    errors, notes = [], []
    text = f.read_text(encoding="utf-8")
    fm, body = body_of(text)
    full = fm + "\n" + body
    # 用词
    if f.name not in TERM_EXEMPT:
        for i, line in enumerate(full.split("\n"), 1):
            for pat, fix in TERMS:
                m = re.search(pat, line)
                if m:
                    errors.append(f"{f.name}:{i} 用词问题 → {fix}：{line.strip()[:60]}")
    # 步骤卡必须有"看到："
    for m in re.finditer(r"^:::step (.+?)\n(.*?)^:::\s*$", body, re.S | re.M):
        if not re.search(r"^看到：", m.group(2), re.M):
            line = body[: m.start()].count("\n") + fm.count("\n") + 3
            errors.append(f"{f.name}:{line} 步骤卡「{m.group(1).strip()}」没有「看到：」一行")
    # 残留的旧写法
    for i, line in enumerate(body.split("\n"), 1):
        if line.startswith("做完应该看到："):
            errors.append(f"{f.name} 第 {i} 行用了「做完应该看到：」，改成「看到：」")
    # 数字写法（提示）
    if want_numbers:
        for i, line in enumerate(body.split("\n"), 1):
            s = line.strip()
            if not NUM.search(s) or s.startswith(("|", "![", "before:", "after:", "<")):
                continue
            if not QUALIFIER.search(s):
                notes.append(f"{f.name}:{i + fm.count(chr(10)) + 2} 数字没有出处或停止标准：{s[:70]}")
    return errors, notes


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    want_numbers = "--numbers" in sys.argv
    all_err, all_note = [], []
    for f in iter_files(args):
        e, n = check(f, want_numbers)
        all_err += e
        all_note += n
    for e in all_err:
        print("错误", e)
    for n in all_note:
        print("提示", n)
    print(f"\n错误 {len(all_err)} 条" + (f"，数字提示 {len(all_note)} 条" if want_numbers else ""))
    sys.exit(1 if all_err else 0)


if __name__ == "__main__":
    main()
