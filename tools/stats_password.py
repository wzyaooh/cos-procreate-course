#!/usr/bin/env python3
"""生成统计看板的密码哈希和 Cookie 密钥，把输出的两行加到服务器的 .env 里。

用法：python tools/stats_password.py          （会提示输入两次密码，输入时不显示）
密码本身不会保存在任何地方，.env 里只有哈希。
"""
import getpass
import hashlib
import secrets
import sys

ITER = 600_000

if sys.stdin.isatty():
    pw = getpass.getpass("看板密码：")
    if getpass.getpass("再输入一次：") != pw:
        sys.exit("两次输入不一样")
else:  # 允许用管道传入：printf '%s' "密码" | python tools/stats_password.py
    pw = sys.stdin.read().rstrip("\n")
if len(pw) < 8:
    sys.exit("密码至少 8 位")
salt = secrets.token_bytes(16)
h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, ITER).hex()
print(f"STATS_PASSWORD_HASH=pbkdf2:sha256:{ITER}:{salt.hex()}:{h}")
print(f"STATS_SECRET={secrets.token_hex(32)}")
