#!/usr/bin/env python3
"""把 content/ 里的 Markdown 和 YAML 生成静态网站。

用法：
  python tools/build.py --out site            # 正式构建（部署用）
  python tools/build.py --out preview --preview  # 本地预览：相对路径、内联样式，可直接双击打开
"""
import argparse, base64, hashlib, html, json, os, re, shutil
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
SITE_NAME = "张宇涵的cos后期Procreate 自学站"
REPO_URL = "https://github.com/wzyaooh/cos-procreate-course"
# 匿名使用统计：设成 1 才在页面里加载 static/js/track.js（需要同时运行 stats 服务，见 docs/stats.md）
STATS_ENABLED = os.environ.get("STATS_ENABLED", "").strip().lower() in ("1", "true", "yes", "on")
STATS_RETENTION_DAYS = int(os.environ.get("STATS_RETENTION_DAYS", "2") or 2)  # 写进隐私说明，要和 stats 服务的设置一致
# 正式网址（分享卡片、sitemap 用）。Docker 构建时从 .env 的 SITE_DOMAIN 传进来；不设就不生成这两项
SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "").strip().strip("/")
SITE_URL = "" if (not SITE_DOMAIN or SITE_DOMAIN.startswith(":")) else "https://" + SITE_DOMAIN.replace("https://", "").replace("http://", "")


# ---------- 读取内容 ----------
def load_yaml(name):
    with open(CONTENT / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def split_front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("缺少 front matter")
    return yaml.safe_load(m.group(1)), m.group(2)


# ---------- Markdown 扩展语法 ----------
CALLOUTS = {"warn": "易错", "tip": "小技巧", "danger": "千万别", "why": "为什么", "check": "怎么判断做对了"}


def preprocess(md_text):
    """处理自定义语法：
    :::warn 标题 ... :::      提示框（warn/tip/danger/why/check）
    :::compare ... :::        修图前后对比滑块
    [[操作 > 画布 > 参考]]     菜单路径按键贴纸
    """
    out, lines, i = [], md_text.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^:::(\w+)\s*(.*)$", line)
        if m:
            kind, title = m.group(1), m.group(2).strip()
            body = []
            i += 1
            while i < len(lines) and lines[i].strip() != ":::":
                body.append(lines[i])
                i += 1
            i += 1
            if kind == "compare":
                items = {}
                for b in body:
                    k, _, v = b.partition(":")
                    src, _, cap = v.partition("|")
                    items[k.strip()] = (src.strip(), cap.strip())
                (bs, bc), (as_, ac) = items["before"], items["after"]
                out.append(
                    f'<figure class="compare" data-compare>'
                    f'<div class="compare-stage">'
                    f'<img class="compare-before" src="{bs}" alt="{html.escape(bc)}">'
                    f'<img class="compare-after" src="{as_}" alt="{html.escape(ac)}">'
                    f'<div class="compare-handle" aria-hidden="true"></div></div>'
                    f'<input class="compare-range" type="range" min="0" max="100" value="50" '
                    f'aria-label="拖动对比修图前后">'
                    f'<figcaption><span>左：{html.escape(bc)}</span><span>右：{html.escape(ac)}</span></figcaption>'
                    f"</figure>"
                )
            elif kind == "step":
                out.append('<div class="step" markdown="1">')
                out.append(f'<p class="step-title">{html.escape(title)}</p>')
                out.append("")
                out.extend(body)
                out.append("")
                out.append("</div>")
            else:
                label = title or CALLOUTS.get(kind, "")
                out.append(f'<div class="callout callout-{kind}" markdown="1">')
                if label:
                    out.append(f'<p class="callout-title">{html.escape(label)}</p>')
                out.append("")
                out.extend(body)
                out.append("")
                out.append("</div>")
            continue
        out.append(line)
        i += 1
    text = "\n".join(out)

    def path_repl(mo):
        parts = [p.strip() for p in mo.group(1).split(">")]
        keys = '<i aria-hidden="true">›</i>'.join(f"<kbd>{html.escape(p)}</kbd>" for p in parts)
        return f'<span class="path">{keys}</span>'

    return re.sub(r"\[\[(.+?)\]\]", path_repl, text)


def render_md(text):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "attr_list", "md_in_html", "sane_lists", "toc"],
                           extension_configs={"toc": {"slugify": lambda v, s: "s-" + hashlib.md5(v.encode()).hexdigest()[:8]}})
    body = md.convert(preprocess(text))
    # 带标题的单图转成 figure
    body = re.sub(r'<p><img alt="([^"]*)" src="([^"]+)" title="([^"]+)" ?/?></p>',
                  r'<figure class="fig"><img alt="\1" src="\2"><figcaption>\3</figcaption></figure>', body)
    # 步骤卡里的"看到："一行，显示成结果提示
    body = re.sub(r"<p>看到：(.*?)</p>", r'<p class="step-see"><b>做完应该看到：</b>\1</p>', body, flags=re.S)
    # 表格外包一层，窄屏可横向滚动
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return body, md.toc_tokens


def sections(body_html):
    """按 h2/h3 把正文切成小节：[(锚点, 小节标题, 纯文本)]，第一段（标题前）锚点为空。"""
    parts = re.split(r'(<h[23][^>]*id="[^"]+"[^>]*>.*?</h[23]>)', body_html, flags=re.S)
    out, cur_id, cur_title = [], "", ""
    for part in parts:
        m = re.match(r'<h[23][^>]*id="([^"]+)"[^>]*>(.*?)</h[23]>', part, re.S)
        if m:
            cur_id, cur_title = m.group(1), plain(m.group(2))
        else:
            txt = plain(part)
            if txt:
                out.append((cur_id, cur_title, txt))
    return out


def plain(html_text):
    t = re.sub(r"<[^>]+>", " ", html_text)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


# ---------- 构建 ----------
class Site:
    def __init__(self, out, preview):
        self.out, self.preview = Path(out), preview
        self.modules = load_yaml("modules.yaml")
        # 资料库：resources.yaml 加上各模块追加的 resources_*.yaml
        self.resources = {}
        for f in ["resources.yaml"] + sorted(p.name for p in CONTENT.glob("resources_*.yaml")):
            for r in load_yaml(f) or []:
                if r["id"] in self.resources:
                    raise SystemExit(f"资料 id 重复：{r['id']}（{f}）")
                self.resources[r["id"]] = r
        # 同一个网址被多个模块收录时，只保留第一条，其余 id 作为别名指向它
        self.alias, by_url = {}, {}
        for rid, r in list(self.resources.items()):
            key = r["url"].rstrip("/")
            if key in by_url:
                keep = by_url[key]
                self.alias[rid] = keep
                self.resources[keep].setdefault("lessons", [])
                self.resources[keep]["lessons"] += [l for l in r.get("lessons", []) if l not in self.resources[keep]["lessons"]]
                del self.resources[rid]
            else:
                by_url[key] = rid
                self.alias[rid] = rid
        self.problems = load_yaml("problems.yaml")
        self.photo_list = load_yaml("photo_list.yaml")
        self.lessons, self.order = {}, []
        for mod in self.modules:
            for les in mod["lessons"]:
                les["module"] = mod
                les["written"] = False
                self.lessons[les["id"]] = les
                self.order.append(les["id"])
        for f in sorted((CONTENT / "lessons").glob("*.md")):
            meta, body = split_front_matter(f.read_text(encoding="utf-8"))
            les = self.lessons[meta["id"]]
            # 作业、找图里写的本课锚点 (#xxx)，在作业中心等别的页面也要能跳回本课
            def fix_local(v, lid=meta["id"]):
                if isinstance(v, str):
                    return v.replace("](#", f"](lesson:{lid}#")
                if isinstance(v, list):
                    return [fix_local(x) for x in v]
                if isinstance(v, dict):
                    return {k: fix_local(x) for k, x in v.items()}
                return v
            for key in ("homework", "find"):
                if key in meta:
                    meta[key] = fix_local(meta[key])
            les.update(meta)
            les["written"] = True
            les["body_md"] = body
        # 还没写正文的课：资料从 resources.yaml 的 lessons 字段反查
        for les in self.lessons.values():
            if not les["written"]:
                les["resources"] = [r["id"] for r in self.resources.values() if les["id"] in r.get("lessons", [])]
        for p in self.problems:
            if p.get("file"):
                meta, body = split_front_matter((CONTENT / "problems" / p["file"]).read_text(encoding="utf-8"))
                p.update(meta)
                p["body_md"] = body
        self.env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html"]),
                               trim_blocks=True, lstrip_blocks=True)
        def md_short(t):
            # 短文本（作业、找图）里列表前常常没空行，补上，否则会渲染成一段
            lines, out = (t or "").split("\n"), []
            for ln in lines:
                if re.match(r"^\s*(\d+\.|[-*]) ", ln) and out and out[-1].strip() and not re.match(r"^\s*(\d+\.|[-*]) ", out[-1]):
                    out.append("")
                out.append(ln)
            return markdown.markdown(preprocess("\n".join(out)), extensions=["md_in_html", "sane_lists"])
        self.env.filters["md"] = md_short
        self.env.filters["mdi"] = lambda t: re.sub(r"^<p>|</p>$", "", markdown.markdown(preprocess(t or "")))
        self.search = []
        self.css = (STATIC / "css" / "site.css").read_text(encoding="utf-8")
        self.js = (STATIC / "js" / "site.js").read_text(encoding="utf-8")
        self.track_js = (STATIC / "js" / "track.js").read_text(encoding="utf-8")
        # 静态文件加版本号：内容变了地址就变，浏览器缓存不会拿到旧样式
        self.ver = hashlib.md5((self.css + self.js + self.track_js).encode()).hexdigest()[:8]

    # 地址：正式版用 /m0/01/，预览版用相对路径 + index.html
    def url(self, target, here):
        if not self.preview:
            return target
        parts = [p for p in here.strip("/").split("/") if p]
        depth = len(parts) - (1 if here.endswith(".html") else 0)
        prefix = "../" * depth
        path, _, frag = target.partition("#")
        path = path.lstrip("/")
        if path.startswith("static/"):
            res = prefix + path
        elif path == "" or path.endswith("/"):
            res = prefix + path + "index.html"
        else:
            res = prefix + path
        return res + ("#" + frag if frag else "")

    def lesson_url(self, lid):
        m, n = lid.split("-")
        return f"/{m}/{n}/"

    def resolve_links(self, body, here):
        def repl(mo):
            attr, kind, ref = mo.group(1), mo.group(2), mo.group(3)
            if kind == "lesson":
                t = self.lesson_url(ref.split("#")[0]) + ("#" + ref.split("#")[1] if "#" in ref else "")
            elif kind == "problem":
                t = f"/problems/{ref}/"
            elif kind == "page":
                t = "/" + ref.lstrip("/")
            else:
                t = "/static/" + ref
            return f'{attr}="{self.url(t, here)}"'
        body = re.sub(r'(href|src)="(lesson|problem|page|static):([^"]+)"', repl, body)
        def img_attr(mo):
            rel = mo.group(1)
            extra = ""
            if rel.endswith(".svg"):
                head = (STATIC / rel).read_text(encoding="utf-8")[:400]
                w = re.search(r'\bwidth="(\d+)"', head); h = re.search(r'\bheight="(\d+)"', head)
                if w and h:
                    extra = f' width="{w.group(1)}" height="{h.group(1)}"'
            return f'src="{self.asset(rel, here)}"{extra} loading="lazy" decoding="async"'
        body = re.sub(r'src="(diagrams/[^"]+)"', img_attr, body)
        return body

    def asset(self, rel, here):
        data = (STATIC / rel).read_bytes()
        if self.preview and rel.endswith(".svg"):
            return "data:image/svg+xml;base64," + base64.b64encode(data).decode()
        return self.url("/static/" + rel, here) + "?v=" + hashlib.md5(data).hexdigest()[:8]

    def render(self, template, here, title, **ctx):
        tpl = self.env.get_template(template)
        parts = [x for x in here.strip("/").split("/") if x]
        depth = len(parts) - (1 if here.endswith(".html") else 0)
        ctx.update(site_name=SITE_NAME, title=title, here=here, preview=self.preview, depth=depth,
                   u=lambda t: self.url(t, here), lu=lambda lid: self.url(self.lesson_url(lid), here),
                   modules=self.modules, lessons=self.lessons, ver=self.ver, repo_url=REPO_URL,
                   stats_enabled=(STATS_ENABLED and not self.preview), stats_retention=STATS_RETENTION_DAYS, site_url=("" if self.preview else SITE_URL),
                   asset=lambda rel: self.asset(rel, here), inline_css=self.css if self.preview else None,
                   inline_js=self.js if self.preview else None)
        html_out = self.resolve_links(tpl.render(**ctx), here)
        dest = self.out / (here.strip("/") + "/index.html" if here.strip("/") else "index.html")
        if here.endswith(".html"):
            dest = self.out / here.strip("/")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_out, encoding="utf-8")

    def write_extras(self):
        """manifest、sitemap、robots"""
        manifest = {
            "name": SITE_NAME, "short_name": "cos后期自学", "lang": "zh-CN", "start_url": "/", "scope": "/",
            "display": "standalone", "background_color": "#FFFDF5", "theme_color": "#FFFDF5",
            "icons": [
                {"src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                {"src": "/static/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
            ],
        }
        (self.out / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
        pages = sorted("/" + str(p.relative_to(self.out).parent).replace("\\", "/").strip(".") for p in self.out.rglob("index.html"))
        pages = [("/" + p.strip("/") + "/").replace("//", "/") for p in pages]
        if SITE_URL:
            urls = "".join(f"<url><loc>{SITE_URL}{p}</loc></url>" for p in pages)
            (self.out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>'
                                                  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + "</urlset>", encoding="utf-8")
            (self.out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /stats/\nDisallow: /api/\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
        else:
            (self.out / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /stats/\nDisallow: /api/\n", encoding="utf-8")
        # 统计看板用：页面标题、模块和课程列表（都是公开信息）
        titles = {}
        for f in self.out.rglob("index.html"):
            m = re.search(r"<title>(.*?)</title>", f.read_text(encoding="utf-8"), re.S)
            p = "/" + str(f.relative_to(self.out).parent).replace("\\", "/").strip(".")
            p = ("/" + p.strip("/") + "/").replace("//", "/")
            titles[p] = html.unescape(m.group(1)).replace(" - " + SITE_NAME, "").replace(SITE_NAME, "首页").strip() if m else p
        site_map = {"pages": titles, "modules": [
            {"id": m["id"], "no": m["no"], "title": m["title"],
             "lessons": [{"id": l["id"], "no": l["no"], "title": l["title"], "path": self.lesson_url(l["id"]),
                          "sections": l.get("_sections", [])} for l in m["lessons"]]}
            for m in self.modules]}
        (self.out / "site-map.json").write_text(json.dumps(site_map, ensure_ascii=False), encoding="utf-8")

    def neighbors(self, lid):
        i = self.order.index(lid)
        prev = self.lessons[self.order[i - 1]] if i > 0 else None
        nxt = self.lessons[self.order[i + 1]] if i + 1 < len(self.order) else None
        return prev, nxt

    def build(self):
        if self.out.exists():
            shutil.rmtree(self.out)
        self.out.mkdir(parents=True)
        if not self.preview:
            shutil.copytree(STATIC, self.out / "static")

        written = [l for l in self.lessons.values() if l["written"]]
        self.render("home.html", "/", None, written=written, problems=self.problems,
                    total_lessons=len(self.order), total_hours=sum(m["hours"] for m in self.modules))
        self.render("map.html", "/map/", "课程地图")
        for mod in self.modules:
            self.render("module.html", f"/{mod['id']}/", f"M{mod['no']} {mod['title']}", mod=mod)

        for lid in self.order:
            les = self.lessons[lid]
            here = self.lesson_url(lid)
            body_html, toc = ("", [])
            if les["written"]:
                body_html, toc = render_md(les["body_md"])
                body_html = self.resolve_links(body_html, here)
            def pick(ids, seen):
                out = []
                for r in ids:
                    if r not in self.alias:
                        raise SystemExit(f"{lid} 引用了不存在的资料 id：{r}")
                    c = self.alias[r]
                    if c not in seen:
                        seen.add(c); out.append(self.resources[c])
                return out
            seen = set()
            res = pick(les.get("resources", []), seen)
            refs = pick(les.get("references", []), seen)
            prereq = [self.lessons[p] for p in les.get("prerequisites", [])]
            related = [p for p in self.problems if lid in p.get("lessons", [])]
            prev, nxt = self.neighbors(lid)
            les["_sections"] = re.findall(r'<h[23][^>]*\bid="([^"]+)"', body_html)
            self.render("lesson.html", here, f"{les['no']} {les['title']}", les=les, body=body_html, toc=toc,
                        res=res, refs=refs, prereq=prereq, related=related, prev=prev, nxt=nxt)
            title = f"{les['no']} {les['title']}"
            self.search.append(dict(t=title, u=here, k="课程", x=(les.get("summary") or les.get("outline", ""))))
            for aid, stitle, txt in sections(body_html):
                if aid:
                    self.search.append(dict(t=title, s=stitle, u=here + "#" + aid, k="课程", x=txt))

        for p in self.problems:
            if p.get("body_md"):
                here = f"/problems/{p['slug']}/"
                body_html, _ = render_md(p["body_md"])
                body_html = self.resolve_links(body_html, here)
                _, ptoc = render_md(p["body_md"])
                self.render("problem.html", here, p["title"], p=p, body=body_html, toc=ptoc)
                self.search.append(dict(t=p["title"], u=here, k="问题速查", x=p["symptom"]))
                for aid, stitle, txt in sections(body_html):
                    if aid:
                        self.search.append(dict(t=p["title"], s=stitle, u=here + "#" + aid, k="问题速查", x=txt))
            else:
                self.search.append(dict(t=p["title"], u="/problems/#" + p["slug"], k="问题速查", x=p["symptom"]))
        groups = []
        for p in self.problems:
            if not groups or groups[-1][0] != p["group"]:
                groups.append((p["group"], []))
            groups[-1][1].append(p)
        self.render("problems.html", "/problems/", "问题速查", groups=groups)

        res_list = list(self.resources.values())
        main_platforms = ["B站", "YouTube", "知乎", "少数派", "Procreate 官方"]
        for r in res_list:
            r["pgroup"] = r["platform"] if r["platform"] in main_platforms else "其他网站"
            r["used_in"] = [l for l in self.lessons.values()
                            if r["id"] in [self.alias.get(x, x) for x in l.get("resources", []) + l.get("references", [])]
                            or l["id"] in r.get("lessons", [])]
            self.search.append(dict(t=r["title"], u="/resources/#" + r["id"], k="资料", x=r.get("why", "")))
        self.render("resources.html", "/resources/", "资料库", res_list=res_list,
                    platforms=main_platforms + ["其他网站"], types=["视频", "文章", "手册", "课程", "书"])
        self.render("homework.html", "/homework/", "作业中心")
        # 通用页面：content/pages/{slug}.md → /{slug}/
        for f in sorted((CONTENT / "pages").glob("*.md")):
            meta, body = split_front_matter(f.read_text(encoding="utf-8"))
            here = f"/{f.stem}/"
            body_html, toc = render_md(body)
            body_html = self.resolve_links(body_html, here)
            self.render("page.html", here, meta["title"], meta=meta, body=body_html, toc=toc)
            self.search.append(dict(t=meta["title"], u=here, k="页面", x=meta.get("summary", "")))
            for aid, stitle, txt in sections(body_html):
                if aid:
                    self.search.append(dict(t=meta["title"], s=stitle, u=here + "#" + aid, k="页面", x=txt))
        self.render("about.html", "/about/", "使用说明", photo_list=self.photo_list)
        self.render("search.html", "/search/", "搜索")
        self.render("404.html", "/404.html", "页面不存在")

        if not self.preview:
            self.write_extras()
        idx = "window.SEARCH_INDEX=" + json.dumps(self.search, ensure_ascii=False) + ";"
        if self.preview:
            for f in self.out.rglob("*.html"):
                depth = len(f.relative_to(self.out).parts) - 1
                fixed = f.read_text(encoding="utf-8").replace("__SEARCH_INDEX_SRC__", "../" * depth + "search-index.js")
                f.write_text(fixed, encoding="utf-8")
            (self.out / "search-index.js").write_text(idx, encoding="utf-8")
        else:
            (self.out / "search-index.js").write_text(idx, encoding="utf-8")
        print(f"已生成 {len(list(self.out.rglob('*.html')))} 个页面 → {self.out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="site")
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    Site(a.out, a.preview).build()
