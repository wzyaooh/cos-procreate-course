#!/usr/bin/env bash
# 1Panel（v2）+ OpenResty 环境下的「等解析生效 → 自动申请证书 → 开启 HTTPS」脚本。
#
# 用法（在服务器上、项目根目录里，用 root 运行）：
#   setsid nohup bash deploy/1panel/ssl-auto.sh > /dev/null 2>&1 &
#   tail -f /var/log/cos-ssl-auto.log        # 看进度
#
# 前提：
#   1. 已在 1Panel「应用商店」装好 OpenResty；
#   2. 已在 1Panel 建好反向代理网站：主域名 = .env 里的 SITE_DOMAIN，代理地址 = http://127.0.0.1:${LOCAL_PORT:-8080}
#      （脚本会检查；没建好会直接退出）；
#   3. 1Panel 里有一个 ACME 账户（新装的 1Panel 自带一个，id 一般是 1；可用 ACME_ACCOUNT_ID 指定）。
#
# 原理：脚本通过 1Panel 在本机的接口 /etc/1panel/agent.sock 调用面板功能，效果和在面板里点按钮一样，
#       建好的证书和 HTTPS 设置在面板里都能看到、能改。只在 1Panel v2.3.x 上测试过。
set -u
cd "$(dirname "$0")/../.."
env_get() { grep -E "^$1=" .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"'"'"' '; }
DOMAIN=${SITE_DOMAIN:-$(env_get SITE_DOMAIN)}
IP=${SERVER_IP:-$(curl -s -4 --max-time 8 https://ifconfig.me || curl -s -4 --max-time 8 https://api.ipify.org)}
ACME=${ACME_ACCOUNT_ID:-1}
WAIT_MIN=${WAIT_MINUTES:-360}
S=/etc/1panel/agent.sock
LOG=${LOG_FILE:-/var/log/cos-ssl-auto.log}

api() { curl -s --unix-socket $S -X "$1" "http://localhost/api/v2$2" -H "Content-Type: application/json" ${3:+-d "$3"}; }
# 只取接口返回的状态码和提示，不记录 data（证书接口的 data 里有私钥）
brief() { python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print("code=%s %s" % (d.get("code"), d.get("message","")))
except Exception: print("返回内容无法解析")'; }
touch "$LOG" && chmod 600 "$LOG"
log() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; }

[ -n "$DOMAIN" ] && [ "$DOMAIN" != "example.com" ] || { log "先在 .env 里把 SITE_DOMAIN 改成你的域名"; exit 1; }
[ -S "$S" ] || { log "找不到 $S：这台机器没有装 1Panel v2，或者不是用 root 运行"; exit 1; }
[ -n "$IP" ] || { log "查不到本机公网 IP，用 SERVER_IP=x.x.x.x 指定"; exit 1; }

WID=$(api POST /websites/search '{"page":1,"pageSize":100,"name":"","orderBy":"created_at","order":"descending","websiteGroupId":0}' \
  | python3 -c "import json,sys;d=json.load(sys.stdin)['data']['items'] or [];print(next((w['id'] for w in d if w['primaryDomain']=='$DOMAIN'),''))")
[ -n "$WID" ] || { log "1Panel 里没有主域名为 $DOMAIN 的网站，先在「网站 › 创建网站 › 反向代理」里建好"; exit 1; }

log "开始等待解析：$DOMAIN -> $IP（最多 $WAIT_MIN 分钟）"
A=""
for i in $(seq 1 "$WAIT_MIN"); do
  A=$(curl -s -m 10 "https://dns.google/resolve?name=$DOMAIN&type=A" \
    | python3 -c 'import json,sys;d=json.load(sys.stdin);print(" ".join(a["data"] for a in d.get("Answer",[]) if a.get("type")==1))' 2>/dev/null)
  if echo " $A " | grep -q " $IP "; then log "解析已生效：$A"; break; fi
  [ $((i % 10)) = 1 ] && log "还没生效（第 $i 次检查，当前：${A:-无记录}）"
  sleep 60
done
echo " $A " | grep -q " $IP " || { log "等了 $WAIT_MIN 分钟解析还没生效，退出。加好解析后重新运行本脚本。"; exit 1; }
sleep 30

find_ssl() { api POST /websites/ssl/search '{"page":1,"pageSize":100}' \
  | python3 -c "import json,sys;d=json.load(sys.stdin)['data']['items'] or [];print(next((s['id'] for s in d if s['primaryDomain']=='$DOMAIN'),''))"; }
SID=$(find_ssl)
if [ -z "$SID" ]; then
  log "申请证书：$(api POST /websites/ssl "{\"primaryDomain\":\"$DOMAIN\",\"otherDomains\":\"\",\"provider\":\"http\",\"acmeAccountId\":$ACME,\"autoRenew\":true,\"keyType\":\"EC256\",\"apply\":true,\"description\":\"$DOMAIN\"}" | brief)"
  sleep 5; SID=$(find_ssl)
else
  log "重新申请已有证书：$(api POST /websites/ssl/obtain "{\"ID\":$SID,\"skipDNSCheck\":false}" | brief)"
fi
[ -n "$SID" ] || { log "证书条目没建出来，到 1Panel「网站 › 证书」里看报错"; exit 1; }
for i in $(seq 1 40); do
  ST=$(api GET /websites/ssl/$SID | python3 -c "import json,sys;d=json.load(sys.stdin)['data'];print(d.get('status',''), '|', d.get('message',''))")
  case "$ST" in ready*) log "证书已签发"; break;; *rror*) log "证书申请失败：$ST"; exit 1;; esac
  sleep 15
done
case "$ST" in ready*) ;; *) log "等了 10 分钟证书还没签好（状态：$ST），到 1Panel「网站 › 证书」里看"; exit 1;; esac

ALGO='ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:!aNULL:!eNULL:!EXPORT:!DSS:!DES:!RC4:!3DES:!MD5:!PSK:!KRB5:!SRP:!CAMELLIA:!SEED'
# hsts 关掉：网站容器里的 Caddy 已经发了 HSTS 头，避免重复
log "开启 HTTPS：$(api POST /websites/$WID/https "{\"websiteId\":$WID,\"enable\":true,\"websiteSSLId\":$SID,\"type\":\"existed\",\"httpConfig\":\"HTTPToHTTPS\",\"SSLProtocol\":[\"TLSv1.3\",\"TLSv1.2\"],\"algorithm\":\"$ALGO\",\"hsts\":false,\"hstsIncludeSubDomains\":false,\"httpsPorts\":[443],\"http3\":false}" | brief)"
sleep 5
bash tools/deploy_check.sh | tee -a "$LOG"
log "完成"
