# 部署

以下以 Ubuntu / Debian 服务器为例，全程用 root 或带 sudo 的用户操作。

### 1. 域名解析

下面用 `cos.example.com` 举例，换成你自己的域名。用子域名的话，主域名上原有的服务不受影响。

在你域名的 DNS 管理后台添加一条 **A 记录**：

| 主机记录 | 类型 | 记录值 |
|---|---|---|
| `cos` | A | 这台服务器的公网 IP |

不要改动 `@`、`www` 以及其他已有的记录。

用 Cloudflare 管理 DNS 的话：**第一次部署前先把这条记录的代理关掉（灰色云朵）**，等证书申请成功后再打开，并把 SSL/TLS 模式设为「完全（严格）」。注意 SSL/TLS 模式是整个域名共用的，改之前确认不会影响主域名上的服务；不确定的话就一直保持灰色云朵。

确认解析已经生效（显示的 IP 应该是这台服务器）：

```bash
ping -c 2 cos.example.com
```

以后想换成别的域名，改 `.env` 里的 `SITE_DOMAIN`，再执行 `docker compose up -d --build`。

### 2. 安装 Docker

```bash
curl -fsSL https://get.docker.com | sh
docker compose version   # 能显示版本号就说明装好了
```

### 3. 放行端口

云服务商控制台的「安全组 / 防火墙」和服务器本身的防火墙，都要放行（反代模式下是给 OpenResty 用的）：

- TCP 80（申请证书时验证用，必须对外开放）
- TCP 443
- UDP 443（HTTP/3，可选）

服务器用 ufw 的话：

```bash
ufw allow 80/tcp && ufw allow 443/tcp && ufw allow 443/udp
```

### 4. 下载项目

在服务器上从 GitHub 拉取代码，比如放在 `/opt/cos-procreate-course`：

```bash
cd /opt
git clone https://github.com/wzyaooh/cos-procreate-course.git
cd cos-procreate-course
```

以后更新：`git pull && docker compose up -d --build`。

### 5. 填写设置

```bash
cd /opt/cos-procreate-course
cp .env.example .env
nano .env        # SITE_DOMAIN 改成你的域名；CADDY_SITE 保持 :80
```

网站有两种运行模式，默认是第一种：

| 模式 | `.env` 里的 CADDY_SITE | 谁占 80/443 | 证书谁管 | 适合 |
|---|---|---|---|---|
| **反代模式**（默认） | `:80` | nginx / 1Panel OpenResty | nginx / 1Panel | 一台服务器上要放多个网站 |
| 直连模式 | 你的域名，比如 `cos.example.com` | 本网站的容器 | 容器里的 Caddy 自动申请 | 服务器上只有这一个网站 |

直连模式还要把 `docker-compose.yml` 里 `ports` 的第一行删掉，换成注释里的三行。

### 6. 启动

```bash
docker compose up -d --build
```

反代模式下，容器只在本机 `127.0.0.1:8080` 提供网页，外面还访问不到，接着做下面的「用 1Panel OpenResty 反代」。直连模式下，第一次启动时 Caddy 会自动申请证书，`docker compose logs -f` 里看到 `certificate obtained successfully` 就成功了。

### 6.1 用 1Panel OpenResty 反代（反代模式）

1. **装 OpenResty**：1Panel 面板 ›「应用商店」› 搜「OpenResty」›「安装」。HTTP 端口 80、HTTPS 端口 443 保持默认。
2. **建网站**：「网站」›「网站」›「创建网站」› 选「反向代理」：
    - 主域名：你的域名，比如 `cos.example.com`
    - 代理地址：`http://127.0.0.1:8080`
    - 其他保持默认，点「确认」。
3. **申请证书**（要先做完第 1 步的域名解析）：「网站」›「证书」› 先「添加 ACME 账户」（邮箱可以随便填一个自己的），再「申请证书」：域名填你的域名，验证方式选「HTTP」，勾选「自动续签」。
4. **启用 HTTPS**：回到网站列表，点你的网站 ›「配置」›「HTTPS」› 打开「启用 HTTPS」，证书选刚申请的，「HTTP 选项」选「访问 HTTP 自动跳转到 HTTPS」，保存。

面板上的按钮名称以你的 1Panel 版本为准。

**懒得点证书那几步**：建好网站以后，在服务器上运行 `setsid nohup bash deploy/1panel/ssl-auto.sh > /dev/null 2>&1 &`。脚本会等解析生效，然后自动申请证书、开启 HTTPS 和跳转，进度看 `tail -f /var/log/cos-ssl-auto.log`。说明见脚本开头的注释。手动配系统 nginx 的话，参考 `docker/nginx-site.conf.example`。

浏览器打开 `https://你的域名`，能看到首页、地址栏有锁的图标就部署完成了。

### 7. 运行部署自检

```bash
bash tools/deploy_check.sh
```

脚本会逐项检查：域名解析、容器状态、端口、证书、首页和课程页能不能打开、http 是否跳转到 https。每项显示「通过」或「没通过」以及怎么办。有没通过的，把全部输出复制发给维护者。

---

## 日常维护

| 要做什么 | 命令（在项目目录里执行） |
|---|---|
| 改了内容，更新网站 | `docker compose up -d --build` |
| 查看运行状态 | `docker compose ps` |
| 查看日志 | `docker compose logs -f` |
| 停止网站 | `docker compose down` |
| 重启 | `docker compose restart` |

证书保存在名为 `caddy_data` 的数据卷里，更新网站、重建容器都不会重新申请。**不要执行 `docker compose down -v`**，`-v` 会删除证书，频繁重新申请会触发 Let's Encrypt 的频率限制。

---

## 常见问题

**证书申请失败**

1. `ping -c 2 你的域名`，确认解析到了这台服务器。
2. 确认 80 和 443 端口在安全组和防火墙里都放行了。
3. 用 Cloudflare 的话，确认第一次申请时代理是关着的（灰色云朵）。
4. 反代模式：在 1Panel「网站 › 证书」里重新申请；直连模式：执行 `docker compose restart`，再看日志。

**启动报错 "port is already allocated" 或 "address already in use"**

服务器上已经有别的程序占用了 80 或 443 端口（比如 nginx、Apache、宝塔面板）。查看是谁占用的：

```bash
ss -ltnp | grep -E ':80 |:443 '
```

你在用直连模式，但 80/443 已经被别的程序占用了（比如 nginx、Apache、宝塔、1Panel 的 OpenResty）。改用默认的反代模式：`.env` 里写 `CADDY_SITE=:80`，`docker-compose.yml` 的端口用 `127.0.0.1:8080:80`，再按「用 1Panel OpenResty 反代」或 `docker/nginx-site.conf.example` 配好转发。

**8080 端口也被占用了**

在 `.env` 里加一行 `LOCAL_PORT=8090`（换一个没被占用的端口），执行 `docker compose up -d`，nginx 的代理地址也改成 `http://127.0.0.1:8090`。

**改了内容，浏览器里没变化**

确认执行过 `docker compose up -d --build`。网页本身设置了每次都检查更新；样式和脚本的地址带版本号，内容变了地址就会变，一般不需要清缓存。

**Docker 构建失败**

把 `docker compose up -d --build` 输出的最后 30 行左右发给维护者。

---
