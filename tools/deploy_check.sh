#!/usr/bin/env bash
# 部署后自检：在服务器上、项目目录里运行  bash tools/deploy_check.sh
# 每一项打印「通过」或「没通过 + 怎么办」。有没通过的，把全部输出发给维护者。
set -u
cd "$(dirname "$0")/.."
DOMAIN=$(grep -E '^SITE_DOMAIN=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
MODE=$(grep -E '^CADDY_SITE=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"'"'"' ')
LPORT=$(grep -E '^LOCAL_PORT=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d ' ')
LPORT=${LPORT:-8080}
FAIL=0
ok()   { printf '  通过    %s\n' "$1"; }
bad()  { printf '  没通过  %s\n          怎么办：%s\n' "$1" "$2"; FAIL=1; }
echo "== 张宇涵的cos后期Procreate 自学站：部署自检 =="
echo "时间：$(date '+%F %T')"

# 1. .env
if [ -n "${DOMAIN:-}" ]; then ok ".env 里的域名：$DOMAIN"; else bad ".env 里没有 SITE_DOMAIN" "cp .env.example .env，再把 SITE_DOMAIN 改成你的域名"; DOMAIN=example.com; fi

# 2. 解析
PUBIP=$(curl -s -4 --max-time 8 https://ifconfig.me || curl -s -4 --max-time 8 https://api.ipify.org || true)
DNSIP=$( (getent ahostsv4 "$DOMAIN" 2>/dev/null | awk '{print $1; exit}') || true)
[ -z "$DNSIP" ] && command -v dig >/dev/null && DNSIP=$(dig +short A "$DOMAIN" | tail -1)
if [ -z "$DNSIP" ]; then bad "$DOMAIN 解析不到 IP" "在 DNS 后台加 A 记录：主机记录 cos，记录值填本机公网 IP${PUBIP:+（$PUBIP）}；刚加的等几分钟再试"
elif [ -n "$PUBIP" ] && [ "$DNSIP" != "$PUBIP" ]; then bad "$DOMAIN 解析到 $DNSIP，但本机公网 IP 是 $PUBIP" "如果开了 Cloudflare 代理（橙色云朵），第一次部署先关掉；否则把 A 记录改成 $PUBIP"
else ok "$DOMAIN 解析到 $DNSIP"; fi

# 3. Docker 和容器
if ! command -v docker >/dev/null; then bad "没装 Docker" "curl -fsSL https://get.docker.com | sh"
else
  STATE=$(docker inspect -f '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' zhangyuhan-cos-course 2>/dev/null || echo "missing")
  case "$STATE" in
    running\ healthy*|running\ ) ok "容器在运行（$STATE）";;
    running\ starting*) ok "容器在运行，健康检查还在启动中（等半分钟再跑一次本脚本）";;
    missing) bad "找不到容器 zhangyuhan-cos-course" "在项目目录执行：docker compose up -d --build";;
    *) bad "容器状态：$STATE" "执行 docker compose logs --tail 50 看报错";;
  esac
fi

# 4. 端口
if [ "${MODE:-}" = ":80" ]; then
  echo "  （反代模式：容器只在本机 127.0.0.1:$LPORT 提供 HTTP，80/443 由 nginx / OpenResty 负责）"
  C0=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 "http://127.0.0.1:$LPORT/m5/04/")
  [ "$C0" = "200" ] && ok "容器在本机 127.0.0.1:$LPORT 能正常返回页面" || bad "本机 127.0.0.1:$LPORT 返回 ${C0:-无响应}" "docker compose ps 看端口映射；docker compose logs --tail 50 看报错"
  if (ss -ltnp 2>/dev/null) | grep -E "[:.]443\s" | grep -qiE "nginx|openresty"; then ok "nginx / OpenResty 在监听 443"
  else bad "没有 nginx / OpenResty 在监听 443" "在 1Panel 应用商店安装 OpenResty，并按 README「用 1Panel OpenResty 反代」建好网站和证书"; fi
else
  for P in 80 443; do
    if (ss -ltn 2>/dev/null || netstat -ltn 2>/dev/null) | grep -qE "[:.]$P\s"; then ok "本机 $P 端口在监听"
    else bad "本机 $P 端口没有程序在监听" "确认容器在运行；docker compose ps 看端口映射"; fi
  done
fi

# 5. 证书和网页
CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "https://$DOMAIN/")
if [ "$CODE" = "200" ]; then ok "https://$DOMAIN/ 能打开（200）"
else bad "https://$DOMAIN/ 打不开（返回 ${CODE:-无响应}）" "多半是证书还没签下来。反代模式：到 1Panel「网站 › 证书」看申请状态；直连模式：docker compose logs --tail 80 | grep -i -E 'certificate|error'。常见原因是解析没生效、安全组没放行 80/443"; fi
EXP=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
if [ -n "$EXP" ]; then ok "证书有效期到：$EXP（$( [ "${MODE:-}" = ":80" ] && echo "由 nginx / 1Panel 续期，1Panel 里要勾选自动续签" || echo "Caddy 会自动续期" )）"; else bad "读不到证书" "同上"; fi
C2=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "https://$DOMAIN/m5/04/")
[ "$C2" = "200" ] && ok "课程页 /m5/04/ 能打开" || bad "课程页 /m5/04/ 返回 $C2" "执行 docker compose up -d --build 重新构建"
C3=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "http://$DOMAIN/")
case "$C3" in 301|302|307|308) ok "http 会自动跳转到 https（$C3）";; *) bad "http 返回 $C3，没有跳转到 https" "确认 80 端口对外开放";; esac

# 6. 使用统计（只在 .env 里开启时检查）
SEN=$(grep -E '^STATS_ENABLED=' .env 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '"'"'"' ')
case "${SEN:-0}" in 1|true|yes|on)
  grep -qE '^COMPOSE_PROFILES=.*stats' .env || bad "开了 STATS_ENABLED，但没写 COMPOSE_PROFILES=stats" "在 .env 里加一行 COMPOSE_PROFILES=stats，再 docker compose up -d --build"
  grep -qE '^STATS_PASSWORD_HASH=pbkdf2:' .env && ok "看板密码已设置（.env 里只有哈希）" || bad "没设置看板密码" "运行 python3 tools/stats_password.py，把输出的两行贴进 .env"
  SST=$(docker inspect -f '{{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}}' zhangyuhan-cos-stats 2>/dev/null || echo "missing")
  case "$SST" in
    running\ healthy*) ok "统计服务在运行（$SST）";;
    running\ starting*) ok "统计服务在运行，健康检查还在启动中";;
    missing) bad "找不到容器 zhangyuhan-cos-stats" "确认 .env 有 COMPOSE_PROFILES=stats，再 docker compose up -d --build";;
    *) bad "统计服务状态：$SST" "docker compose logs --tail 50 stats 看报错";;
  esac
  C4=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "https://$DOMAIN/stats/login")
  [ "$C4" = "200" ] && ok "统计看板 https://$DOMAIN/stats/ 能打开" || bad "统计看板返回 ${C4:-无响应}" "docker compose logs --tail 50 stats"
  C5=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 -X POST -H "Origin: https://$DOMAIN" -H 'Content-Type: text/plain' --data '{}' "https://$DOMAIN/api/e")
  [ "$C5" = "204" ] && ok "统计数据接口 /api/e 正常（204）" || bad "统计数据接口返回 ${C5:-无响应}" "确认网站容器已重新构建（docker compose up -d --build），Caddy 才会把 /api/e 转给统计服务"
  curl -s --max-time 15 "https://$DOMAIN/" | grep -q 'track.js' && ok "页面里已加载统计脚本" || bad "页面里没有统计脚本" "STATS_ENABLED=1 要在构建时生效：docker compose up -d --build"
;; esac

echo
if [ $FAIL = 0 ]; then echo "全部通过。可以在 iPad 上打开 https://$DOMAIN/ 了。"; else echo "有没通过的项。把上面的全部输出复制发给维护者。"; fi
exit $FAIL
