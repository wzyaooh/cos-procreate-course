# 写课和改课

## 项目结构

```
content/
  modules.yaml        9 个模块和 46 节课的目录、要点、找图要求、作业
  lessons/            已写好正文的课，一课一个 .md 文件（会覆盖 modules.yaml 里同一课的内容）
  problems.yaml       问题速查列表
  problems/           有详细修法的问题，一个问题一个 .md 文件
  pages/              其他页面（PS 对照表、毕业作品），一个文件一个页面，地址是 /文件名/
  resources*.yaml     资料库（所有外部链接都在这里；resources_*.yaml 是按模块追加的，构建时合并、按网址去重）
  photo_list.yaml     找图清单
templates/            页面模板
static/               样式、脚本、示意图
tools/build.py        构建网站
tools/check_links.py  检查资料链接是否还能打开
tools/check_site.py   检查构建结果里的站内链接、锚点、搜索索引
tools/lint.py         内容检查：用词、步骤卡、数字写法
tools/make_icons.py   生成图标和分享卡片（手动运行，生成的 PNG 随项目提交）
tools/deploy_check.sh 部署后在服务器上运行的自检
tools/diagrams/       生成示意图的脚本（kit.py 是公共组件，其余按模块分文件）
docker/               Caddy 配置、nginx 反代配置参考
deploy/1panel/        1Panel 环境下自动申请证书的脚本
docs/                 部署说明、写课说明
Dockerfile
docker-compose.yml
.env.example          域名和运行模式
```


## 本地预览

电脑上装好 Python 3 后：

```bash
pip install -r requirements.txt
python tools/build.py --out preview --preview
```

然后直接双击打开 `preview/index.html`。预览版用相对路径，并把样式内联到每个页面，不需要启动服务器。

## 写一节新课

在 `content/lessons/` 新建一个文件，比如 `m5-01-wig.md`。文件开头的设置区格式如下（`id` 要和 `modules.yaml` 里的课对应）：

```yaml
---
id: m5-01
summary: 一句话说清这节课解决什么问题。
tools: [Procreate]
prerequisites: [m2-02]            # 建议先学的课
goals:
  - 学完能做到的第一件事
resources: [bili-wig]             # 学习资料，填 resources.yaml 里的 id
references: [hb-clone]            # 参考资料
find: 这次作业需要什么样的照片。
homework:
  task: 作业要做什么。
  acceptance:
    - 验收标准一
  deliverables: [要交的东西]
checklist:
  - 自检清单的一条

正文用 Markdown 写。
```

正文里可以用这些写法：

| 写法 | 效果 |
|---|---|
| `[[操作 > 画布 > 参考]]` | 菜单路径按键贴纸 |
| `:::warn 标题` … `:::` | 黄色易错提示框。另有 `tip`、`why`、`check`、`danger` |
| `:::compare` 加 `before:` `after:` 两行 … `:::` | 修图前后对比滑块 |
| `:::step 步骤标题` … `:::` | 带编号的步骤卡，每个二级标题下重新从 1 编号 |
| 步骤卡里以 `看到：` 开头的一段 | 显示成绿色的「做完应该看到」提示 |
| `![说明](diagrams/xxx.svg "图注")` | 带图注的示意图，图片放在 `static/diagrams/` |
| `[链接文字](lesson:m3-04)` | 链接到某一课，可以加 `#小节id` |
| `[链接文字](problem:proportion)` | 链接到问题速查 |
| `## 标题 {#legs}` | 给小节设一个固定的跳转 id |

写作原则：每课写到"照着能做出来"为止，不凑字数；操作写到具体菜单和数值；每个知识点说清做什么、为什么、怎么判断做对了。

## 重新生成示意图

示意图是用 Python 脚本画的 SVG，改了脚本后运行：

```bash
python tools/diagrams/m2.py                                    # 只重画某个模块
for f in tools/diagrams/*.py; do [ "$(basename $f)" = kit.py ] || python "$f"; done   # 全部重画
```

只用 Python 标准库。生成的是 SVG，中文用浏览器里的系统字体显示（苹方、思源黑体等）。

生成的文件在 `static/diagrams/` 里。这些示意图按 Procreate 5 的界面布局绘制，不是真机截图；以后想换成真机截图，直接替换同名文件或改 Markdown 里的图片路径即可。

## 内容检查

改完课程后运行：

```bash
python tools/lint.py              # 用词、步骤卡缺「看到：」
python tools/lint.py --numbers    # 再加上数字写法检查
```

出现「错误」要改；「数字提示」表示这一句的百分比既没有出处、也没有写看到什么就停，按网站「使用说明 › 课程里的数字怎么用」里的三类规则改写。

## 检查资料链接

```bash
python tools/check_links.py
```

B 站、知乎等网站会拦截脚本访问，结果显示「需手动确认」的，用浏览器打开看一眼即可。
