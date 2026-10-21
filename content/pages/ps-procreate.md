---
title: PS 和 Procreate 对照表
summary: 看 Photoshop 教程时，查它说的工具、菜单、快捷键在 Procreate 里叫什么、在哪里，以及本站哪一课讲这一步。
wide: true
---

本站推荐的不少教程是用 Photoshop（下面简称 PS）讲的。看到 PS 的操作，先按类别找到那一行：第一列是 PS 中文版的叫法（括号里是英文版），第二、三列是 Procreate 里叫什么、在哪里，第四列链到本站讲这一步的课。表里找不到的，多半是 Procreate 没有这个功能，看最后一节[「PS 有、Procreate 没有的功能」](#missing)。

Procreate 的叫法以[官方中文使用手册](https://help.procreate.com/cn/procreate/handbook/introduction)为准，PS 的叫法参照 Adobe 官方中文帮助。PS 版本不同，个别菜单名会有出入，以你看的教程里的界面为准。完整翻译一句 PS 教程的示范见 [1.4 课案例三](lesson:m1-04#case-ps)。

:::tip 先记住最重要的一条区别
PS 教程里常说"新建一个调整图层"。Procreate 的调整都直接改像素，没有调整图层，所以凡是这一步，都改成**先复制一层，在副本上调**，事后用副本的不透明度控制强度（[2.1 课](lesson:m2-01#why-pixels)）。
:::

## 图层和混合模式 {#layers}

| PS 里的叫法（英文） | Procreate 里叫什么 | 在哪里找 | 本站哪课讲 |
|---|---|---|---|
| 新建图层（New Layer） | 新增图层 | 图层面板右上角的「+」 | [1.4 第 2 步](lesson:m1-04#basic) |
| 复制图层（Duplicate Layer） | 复制 | 在图层上单指向左轻滑 › 复制 | [1.4 第 2 步](lesson:m1-04#basic) |
| 不透明度、混合模式（Opacity、Blending Mode） | 不透明度、混合模式 | 点图层右边的字母（默认是 N），弹出的菜单里 | [1.4 第 3 步](lesson:m1-04#blend) |
| 叠加（Overlay） | **覆盖** | 混合模式菜单 | [1.4](lesson:m1-04#why-overlay) |
| 正片叠底、滤色、线性减淡（添加）、柔光、颜色、明度（Multiply、Screen、Linear Dodge (Add)、Soft Light、Color、Luminosity） | 正片叠底、滤色、添加、柔光、颜色、明度 | 混合模式菜单 | [1.4 总表](lesson:m1-04#blend-table) |
| 图层编组（Group Layers） | 组合（建成「组」） | 单指向右轻滑多选图层 › 点面板上的「图层」› 组合 | [1.4 第 4 步](lesson:m1-04#group) |
| 向下合并（Merge Down） | 向下合并 | 轻点图层两次打开图层选项 › 向下合并；合并一串：两指按住首尾两层往中间捏 | [1.4 第 4 步](lesson:m1-04#group) |

## 选区和蒙版 {#selection}

| PS 里的叫法（英文） | Procreate 里叫什么 | 在哪里找 | 本站哪课讲 |
|---|---|---|---|
| 图层蒙版（Layer Mask） | 蒙版 | 图层选项 › 蒙版 | [1.5 第 5 步](lesson:m1-05#mask) |
| 剪贴蒙版（Clipping Mask） | 剪辑蒙版 | 图层选项 › 剪辑蒙版 | [1.5 第 4 步](lesson:m1-05#clip) |
| 锁定透明像素（Lock Transparent Pixels） | 阿尔法锁定 | 图层选项 › 阿尔法锁定；或两指在图层上向右轻滑 | [1.5 第 3 步](lesson:m1-05#alpha) |
| 魔棒工具、快速选择工具（Magic Wand、Quick Selection） | 选取 › 自动 | 左上角 S 形的选取图标 › 底部「自动」，点住左右拖调阈值 | [1.6 第 1 步](lesson:m1-06#select)、[2.5](lesson:m2-05#why-threshold) |
| 套索工具、多边形套索工具（Lasso、Polygonal Lasso） | 选取 › 手绘 | 拖着描相当于套索，一下一下轻点相当于多边形套索 | [1.6 第 1 步](lesson:m1-06#select) |
| 反向选择（Inverse） | 反转 | 选取底栏 | [1.6 第 1 步](lesson:m1-06#select) |
| 羽化（Feather） | 羽化 | 选取底栏 | [1.6 第 2 步](lesson:m1-06#feather) |

## 变换和液化 {#transform}

| PS 里的叫法（英文） | Procreate 里叫什么 | 在哪里找 | 本站哪课讲 |
|---|---|---|---|
| 自由变换（Free Transform） | 变换：自由变换、等比 | 左上角箭头图标 › 底部选模式 | [1.6 第 4 步](lesson:m1-06#setup) |
| 扭曲、透视（Distort、Perspective） | 扭曲 | 变换底部 › 扭曲，拖四个角 | [1.6 第 5 步](lesson:m1-06#distort) |
| 变形（Warp） | 弯曲 | 变换底部 › 弯曲 | [1.6 第 5 步](lesson:m1-06#distort) |
| 液化（Liquify）：向前变形、收缩、膨胀、旋转扭曲、重建（Forward Warp、Pucker、Bloat、Twirl、Reconstruct） | 液化：推、捏合、展开、转动、重建 | [[调整 > 液化]]，底部选模式；整体减弱用底部的「调整」 | [2.3 第 1 步](lesson:m2-03#start)、[2.3 第 4 步](lesson:m2-03#undo) |

## 修补 {#retouch}

| PS 里的叫法（英文） | Procreate 里叫什么 | 在哪里找 | 本站哪课讲 |
|---|---|---|---|
| 仿制图章工具（Clone Stamp） | 克隆 | [[调整 > 克隆]]；PS 按 Alt 单击取样，这里拖动取样圆盘，长按圆盘锁定 | [2.2](lesson:m2-02#start) |
| 污点修复画笔工具、修复画笔工具（Spot Healing Brush、Healing Brush） | 没有；用克隆点掉，再用低不透明度软画笔补色 | [[调整 > 克隆]] | [4.3 第 1～2 步](lesson:m4-03#clone) |
| 修补工具（Patch） | 没有；选一块干净的区域复制出来，挪过去，用蒙版融边 | 选取 › 三指下拖 › 复制 | [5.5 第 2 步](lesson:m5-05#patch) |
| 涂抹工具（Smudge） | 涂抹 | 右上角手指形图标 | [1.3 第 4 步](lesson:m1-03#smudge) |
| 减淡工具、加深工具（Dodge、Burn） | 没有专门的工具；在柔光模式的中性灰图层上用白色、黑色软画笔涂 | 新建图层 › 图层选项 › 填充图层 › 改柔光 | [4.4 第 1～4 步](lesson:m4-04#fill) |

## 调整 {#adjust}

| PS 里的叫法（英文） | Procreate 里叫什么 | 在哪里找 | 本站哪课讲 |
|---|---|---|---|
| 曲线（Curves） | 曲线 | [[调整 > 曲线]] | [2.1 第 4 步](lesson:m2-01#curves) |
| 色彩平衡（Color Balance） | **颜色平衡** | [[调整 > 颜色平衡]] | [2.1 第 3 步](lesson:m2-01#balance) |
| 色相/饱和度（Hue/Saturation） | 色相、饱和度、亮度 | [[调整 > 色相、饱和度、亮度]] | [2.1 第 5 步](lesson:m2-01#hsb) |
| 渐变映射（Gradient Map） | 渐变映射 | [[调整 > 渐变映射]] | [2.1 第 6 步](lesson:m2-01#gradmap)、[5.6 第 5 步](lesson:m5-06#gradient-map) |
| 去色、黑白（Desaturate、Black & White） | 没有一键去色；把饱和度拉到最左，或者只是想看明暗时用灰度观察层 | [[调整 > 色相、饱和度、亮度]] | [3.1 第 2 步](lesson:m3-01#gray) |
| 高斯模糊、动感模糊（Gaussian Blur、Motion Blur） | 高斯模糊、动态模糊 | [[调整 > 高斯模糊]]、[[调整 > 动态模糊]] | [2.4 第 1～2 部分](lesson:m2-04#dof) |
| 径向模糊（Radial Blur） | 最接近的是透视模糊 | [[调整 > 透视模糊]] | [2.4 第 3 部分](lesson:m2-04#persp) |
| USM 锐化、智能锐化（Unsharp Mask、Smart Sharpen） | 锐化 | [[调整 > 锐化]] | [2.4 第 5 部分](lesson:m2-04#sharpen) |
| 添加杂色（Add Noise） | 杂色 | [[调整 > 杂色]] | [2.4 第 4 部分](lesson:m2-04#grain) |

## 磨皮和光影 {#skin}

| PS 里的叫法（英文） | Procreate 里叫什么 | 在哪里找 | 本站哪课讲 |
|---|---|---|---|
| 高低频磨皮（Frequency Separation） | 做不了；用克隆、低不透明度补色、杂色补质感三步代替 | — | [4.3](lesson:m4-03#why-fs) |
| 中性灰（填充 50% 灰，模式改柔光或叠加） | 一样能做：填充图层，模式改柔光或覆盖 | 颜色面板「值」里输入十六进制 808080 › 图层选项 › 填充图层 | [4.4 第 1～2 步](lesson:m4-04#fill)、[1.4 案例三](lesson:m1-04#case-ps) |
| 双曲线（一个提亮、一个压暗的曲线调整图层，配蒙版涂） | 没有调整图层，做不了原样；用中性灰图层达到同样的局部提亮、压暗 | — | [4.4](lesson:m4-04#why-neutral) |
| 观察组（黑白观察层） | 灰度观察层 | 新建图层填满黑色，混合模式改「颜色」 | [4.1 第 3 步](lesson:m4-01#gray)、[4.4](lesson:m4-04#why-gray) |

## 画笔和颜色 {#brush}

| PS 里的叫法（英文） | Procreate 里叫什么 | 在哪里找 | 本站哪课讲 |
|---|---|---|---|
| 画笔工具（Brush） | 绘图 | 右上角画笔图标 › 画笔库 | [1.3 第 1 步](lesson:m1-03#pick) |
| 柔边圆、硬边圆画笔，调「硬度」（Hardness） | 没有硬度滑块，换笔：软画笔、硬画笔 | 画笔库 › 气笔修饰 | [1.3 第 1 步](lesson:m1-03#pick) |
| 流量（Flow） | 没有；用低不透明度多叠几笔 | 左侧栏下面的不透明度滑块 | [1.3](lesson:m1-03#why-opacity) |
| 吸管工具（Eyedropper） | 取色 | 手指按住画布 | [1.2 第 1 步](lesson:m1-02#list) |
| 拾色器里的 HSB、十六进制（Color Picker） | 颜色面板 › 值 | 右上角颜色圆点 › 底部「值」 | [3.2 第 2 步](lesson:m3-02#read) |

## 画布和导出 {#canvas}

| PS 里的叫法（英文） | Procreate 里叫什么 | 在哪里找 | 本站哪课讲 |
|---|---|---|---|
| 画布大小（Canvas Size） | 裁剪并调整大小，「画布重新取样」关闭 | [[操作 > 画布 > 裁剪并调整大小]] | [5.5 第 4 步](lesson:m5-05#extend) |
| 图像大小（Image Size） | 裁剪并调整大小，打开「画布重新取样」 | [[操作 > 画布 > 裁剪并调整大小]] | [2.6 第 6 步](lesson:m2-06#resize) |
| 转换为配置文件（Convert to Profile），转 sRGB | 颜色配置文件 | [[操作 > 画布 > 画布信息]] › 颜色配置文件 | [0.2](lesson:m0-02#color-space) |
| 存储为 PSD、导出为 JPEG / PNG（Save As、Export As） | 分享 | [[操作 > 分享]] | [2.6 第 6 步](lesson:m2-06#export) |

## 快捷操作 {#shortcuts}

PS 靠键盘，Procreate 靠手势和按钮。快捷键以 Windows 为准，Mac 把 Ctrl 换成 Command、Alt 换成 Option。

| PS 里的叫法（英文） | Procreate 里叫什么 | 在哪里找 | 本站哪课讲 |
|---|---|---|---|
| Ctrl+Z 还原、Ctrl+Shift+Z 重做（Undo、Redo） | 撤销、重做 | 两指轻点撤销（按住不放连续撤销），三指轻点重做 | [1.2 第 1 步](lesson:m1-02#list) |
| Ctrl+T 自由变换 | 变换 | 点左上角箭头图标 | [1.6 第 4 步](lesson:m1-06#setup) |
| Ctrl+J 通过拷贝的图层（Layer via Copy） | 复制 | 没有选区：图层上向左轻滑 › 复制；有选区：三指下拖 › 复制 | [1.4 第 2 步](lesson:m1-04#basic)、[1.2 第 1 步](lesson:m1-02#list) |
| Ctrl+Alt+Shift+E 盖印（Stamp Visible） | 全部拷贝，再粘贴 | 三指下拖 › 全部拷贝；再三指下拖 › 粘贴 | [2.4 第 5 部分](lesson:m2-04#sharpen) |
| Ctrl+D 取消选择（Deselect） | 退出选取 | 再点一次左上角的选取图标 | [手册：选取的界面与手势](https://help.procreate.com/cn/procreate/handbook/selections/selections-interface) |
| [ 和 ] 调画笔大小 | 尺寸 | 左侧栏上面的滑块 | [1.3 第 2 步](lesson:m1-03#size-opacity) |

## PS 有、Procreate 没有的功能 {#missing}

PS 教程里用到下面这些，在 Procreate 里找不到对应的按钮，按第三列的做法达到同样的目的。

| PS 功能（英文） | Procreate 的情况 | 本站的替代做法 | 本站哪课讲 |
|---|---|---|---|
| 高低频磨皮（Frequency Separation） | 没有高反差保留这类滤镜，也不能把两张图相减，做不出干净的高频层 | 克隆去尖刺、低不透明度软画笔补色块、杂色补质感 | [4.3](lesson:m4-03#why-fs) |
| 内容识别填充（Content-Aware Fill） | 不会按周围的内容自动补齐 | 小件用克隆；大件复制一块相似的背景，挪过去用蒙版融边；地面按透视扭曲 | [5.5](lesson:m5-05#why-choose) |
| 调整图层（Adjustment Layers） | 调整确认后直接写进像素，之后不能再打开改参数 | 先复制一层再调；用副本的不透明度收强度；只想改局部就给副本加蒙版 | [2.1](lesson:m2-01#why-pixels)、[2.1 第 7 步](lesson:m2-01#opacity) |
| 智能对象（Smart Object） | 没有；每确认一次变换，像素就重算一次，反复缩放会越来越糊 | 尽量一次变换到位；缩放前把插值设成双立体（PS 重新采样里的「两次立方」对应这里的双立体）；原图锁在最下面留底 | [1.6](lesson:m1-06#why-interp) |
| 动作（Actions） | 不能录制、回放一串操作 | 做一个模板文件，每次从模板开始；调色存成 Lightroom 预设 | [8.2 第 5 步](lesson:m8-02#template) |
| 选择并遮住、钢笔工具（Select and Mask、Pen Tool） | 没有边缘细化，也没有路径 | 自动加手绘选取抠出大形，再用蒙版和软画笔修发丝 | [2.5](lesson:m2-05#refine) |
| 色阶（Levels） | 没有 | 用曲线 | [2.1 第 4 步](lesson:m2-01#curves) |
| 历史记录面板、快照（History、Snapshot） | 只能一步步撤销，退出作品后撤销记录就没了 | 重要的节点在图库里复制作品，存成版本 | [2.6 第 4 步](lesson:m2-06#version) |
| Camera Raw 滤镜（Camera Raw Filter） | 不能打开 RAW，也没有这一整套调光调色面板 | 先在 Lightroom 手机版调曝光、白平衡，再导入 Procreate | [4.2](lesson:m4-02#why-lr) |
