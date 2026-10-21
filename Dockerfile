# 第一步：把 content/ 里的 Markdown 构建成网页
FROM python:3.12-slim AS build
WORKDIR /src
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# 网址写进分享卡片和 sitemap；docker-compose 会把 .env 里的 SITE_DOMAIN 传进来
ARG SITE_DOMAIN=
RUN SITE_DOMAIN=${SITE_DOMAIN} python tools/build.py --out /site

# 第二步：用 Caddy 提供网页，并自动申请、续期 HTTPS 证书
FROM caddy:2.10-alpine
COPY docker/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /site /srv
