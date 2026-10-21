# 参与改进

谢谢你愿意帮忙！这个项目最需要的是：**和真机界面不一致的地方、写错的数字、失效的链接、讲得不清楚的步骤**。

## 只想报告问题

到 [Issues](https://github.com/wzyaooh/cos-procreate-course/issues/new/choose) 选一个模板填写。最有用的信息是：

- 哪一课、哪一步（直接贴网页地址，比如 `https://cos.llmunify.com/m5/04/#legs`）
- 你的 Procreate 版本（「操作 › 帮助 › 关于 Procreate」）和 iPadOS 版本
- 实际界面是什么样，最好附一张截图

## 想直接改

1. Fork 本仓库，改 `content/` 下的文件。
2. 本地检查（需要 Python 3.9 以上）：

   ```bash
   pip install -r requirements.txt
   python tools/lint.py --numbers          # 用词、步骤卡、数字写法
   python tools/build.py --out site        # 构建
   python tools/check_site.py site         # 站内链接和锚点
   python tools/build.py --out preview --preview   # 生成预览，打开 preview/index.html 看效果
   ```

3. 提交 Pull Request。GitHub 会自动跑一遍上面的检查。

课程的文件格式、可用写法（步骤卡、提示框、对比滑块、菜单路径贴纸）见 [docs/authoring.md](docs/authoring.md)。

## 写法约定

这几条是整个课程保持一致的关键，`tools/lint.py` 会检查其中一部分。

**用词以 Procreate 官方中文手册为准**（<https://help.procreate.com/cn/procreate/handbook>）。常见的：

| 写 | 不写 |
|---|---|
| 克隆 | 仿制 |
| 双立体（插值） | 双立方 |
| 阿尔法锁定 | Alpha 锁定 |
| 颜色平衡 | 色彩平衡 |
| 覆盖（混合模式） | 叠加（这是 PS 的叫法，提到 PS 时要说明） |

**每张步骤卡都要有「看到：」**：最后一行写做完这一步，画面或界面应该是什么样，让读者能判断自己做对了没有。

**数字分三类写**：

| 类型 | 例子 | 怎么写 |
|---|---|---|
| 有出处的 | 打印 300 DPI、软件默认值、平台规定 | 写明出处，能链接就链接 |
| 算出来的 | 放大倍数、HSB 换 RGB、头身比 | 写出怎么算的 |
| 经验起点值 | 模糊、液化、不透明度、笔刷尺寸的百分比 | 写成「从 X 左右开始，看到 Y 就停」，不要只给一个数 |

**不凑字**：不写开场白，不重复讲前面课讲过的内容，直接链接过去（`[3.4 课](lesson:m3-04#measure)`）。

**不放练习照片和别人的作品**：示意图用 `tools/diagrams/` 里的脚本画。资料只收作者本人或官方发布的内容，不收转卖课程的网站。新增资料的链接要确认能打开。

## 许可

提交到本仓库的课程内容按 [CC BY-NC-SA 4.0](LICENSE-CONTENT) 授权，代码按 [MIT](LICENSE) 授权。提交 Pull Request 即表示你同意以这两个协议授权你的修改。
