"""M0 开课准备 的示意图。运行：python tools/diagrams/m0.py"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'diagrams', 'm0')
os.makedirs(OUT, exist_ok=True)


def save(name, s):
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)


def frame(inner):
    return f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#1F2329"/>' + inner


def thumb(x, y, w, h, kind=0, name='未命名作品'):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#FFF7E6"/>'
    if kind == 0:
        s += f'<path d="M{x + w / 2} {y + h - 8} q-14 -40 0 -70 q14 30 0 70" fill="{PINK}" stroke="{INK}" stroke-width="1.5"/>'
    elif kind == 1:
        s += f'<circle cx="{x + w / 2}" cy="{y + h / 2}" r="{w / 4}" fill="{VIO2}" stroke="{INK}" stroke-width="1.5"/>'
    else:
        s += f'<rect x="{x + 10}" y="{y + h * 0.6}" width="{w - 20}" height="{h * 0.3}" fill="{MINT1}" stroke="{INK}" stroke-width="1.5"/>'
    s += text(x, y + h + 20, name, 13, 600, UITEXT)
    return s


def gallery_top(hl=None):
    s = text(SX + 26, 52, 'Procreate', 22, 800, UITEXT)
    xs = {'选择': 520, '导入': 588, '照片': 656, '+': 730}
    for k, x in xs.items():
        s += text(x, 52, k, 18 if k != '+' else 30, 700, UITEXT, 'middle')
        if hl == k:
            s += ringrect(x - 30, 26, 60, 38) if k != '+' else ring(x, 42, 20)
    return s, xs


def u_gallery():
    top, xs = gallery_top('照片')
    s = top + ringrect(xs['导入'] - 30, 26, 60, 38)
    for i in range(3):
        s += thumb(60 + i * 230, 100, 170, 220, i, ['雷电将军_01', '练习_光影球', '未命名作品'][i])
    s += badge(xs['照片'], 82, 1, YEL) + badge(xs['导入'], 82, 2, YEL)
    s += label(392, 400, '① 照片：从相册选', YEL1, 15) + label(392, 436, '② 导入：从「文件」App 选（网盘、AirDrop 的原图）', YEL1, 15)
    s += label(392, 472, '两种方式都会直接用这张图新建一个画布', WHITE, 15)
    s += note('示意图')
    save('u-gallery', svg(W, H, frame(s), '图库右上角的照片和导入按钮'))


def u_custom_canvas():
    top, xs = gallery_top('+')
    s = top + f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#000" fill-opacity=".45"/>'
    px, py, pw, ph = 130, 80, 540, 420
    s += panel(px, py, pw, ph) + text(px + pw / 2, py + 32, '自定义画布', 18, 800, UITEXT, 'middle')
    s += text(px + pw - 24, py + 32, '创建', 16, 800, UIBLUE, 'end')
    tabs = ['尺寸', '颜色配置', '缩时视频设置', '画布属性']
    for i, t in enumerate(tabs):
        y = py + 70 + i * 44
        s += f'<rect x="{px + 12}" y="{y}" width="150" height="36" rx="8" fill="{UIBLUE if i == 0 else UIBAR}"/>' + text(px + 26, y + 24, t, 15, 700, UITEXT)
    fields = [('宽度', '3000 px'), ('高度', '4000 px'), ('DPI', '300')]
    for i, (k, v) in enumerate(fields):
        y = py + 72 + i * 56
        s += text(px + 190, y + 24, k, 15, 700, UITEXT) + f'<rect x="{px + 270}" y="{y}" width="200" height="38" rx="8" fill="{UIBAR}"/>' + text(px + 286, y + 25, v, 16, 700, WHITE)
    s += text(px + 190, py + 260, '最大图层数', 15, 700, UITEXT) + text(px + 470, py + 260, '（按设备显示）', 15, 800, YEL, 'end')
    s += ringrect(px + 180, py + 236, 300, 36)
    s += badge(xs['+'], 78, 1) + badge(px + 500, py + 110, 2) + badge(px + 500, py + 254, 3) + badge(px + pw - 40, py + 56, 4)
    s += label(px + 190, py + 320, '② 填 3000 × 4000，单位选 px', YEL1, 14)
    s += label(px + 190, py + 352, '③ 这里会显示这个尺寸能建多少层', YEL1, 14)
    s += label(px + 190, py + 384, '④ 点「创建」', YEL1, 14)
    s += note('示意图：图库右上角「+」→ 带加号的长方形图标')
    save('u-custom-canvas', svg(W, H, frame(s), '自定义画布：尺寸和最大图层数'))


def u_canvas_info():
    s = f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>' + topbar('actions')
    px, py, pw, ph = 170, 70, 460, 440
    s += panel(px, py, pw, ph) + text(px + pw / 2, py + 30, '画布信息', 18, 800, UITEXT, 'middle')
    cats = ['关于本作品', '尺寸', '图层', '颜色配置文件', '视频设置', '统计']
    for i, t in enumerate(cats):
        y = py + 56 + i * 42
        s += f'<rect x="{px + 12}" y="{y}" width="140" height="34" rx="8" fill="{UIBLUE if t == "图层" else UIBAR}"/>' + text(px + 24, y + 23, t, 14, 700, UITEXT)
    rows = [('最大图层数', '（你的数字）'), ('使用的图层', '1'), ('可用图层数', '最大 − 已用')]
    for i, (k, v) in enumerate(rows):
        y = py + 60 + i * 46
        s += text(px + 172, y + 22, k, 15, 700, UITEXT) + text(px + pw - 20, y + 22, v, 15, 800, YEL if i == 0 else UITEXT, 'end')
    s += ringrect(px + 162, py + 56, pw - 174, 36)
    s += badge(*icon_pos('actions'), 1) if False else ''
    s += ring(*icon_pos('actions'), 18)
    s += label(px + 172, py + 250, '左边点「图层」，右边第一行就是', YEL1, 14)
    s += label(px + 172, py + 282, '「尺寸」里能看到像素宽度和高度', WHITE, 14)
    s += label(px + 172, py + 314, '「颜色配置文件」里能看到 P3 或 sRGB', WHITE, 14)
    s += note('示意图：操作 › 画布 › 画布信息')
    save('u-canvas-info', svg(W, H, s, '画布信息：图层、尺寸、颜色配置文件'))


def u_gesture():
    s = f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>' + topbar('actions')
    px, py, pw, ph = 110, 66, 580, 450
    s += panel(px, py, pw, ph) + text(px + pw / 2, py + 30, '手势控制', 18, 800, UITEXT, 'middle') + text(px + pw - 20, py + 30, '完成', 16, 800, UIBLUE, 'end')
    cats = ['常规', '涂抹', '擦除', '辅助绘图', '吸管', '速创形状', '速选菜单', '全屏', '清除图层', '拷贝并粘贴', '图层选择']
    for i, t in enumerate(cats):
        y = py + 50 + i * 35
        s += f'<rect x="{px + 10}" y="{y}" width="150" height="30" rx="7" fill="{UIBLUE if i == 0 else UIBAR}"/>' + text(px + 22, y + 21, t, 14, 700, UITEXT)
    s += menu_rows(px + 170, py + 50, pw - 180, ['禁用触摸操作', '禁用撤销并重做', '捏合缩放旋转', '启用 3D 手指绘画'], hl='禁用触摸操作',
                   row_h=44, toggles={'禁用触摸操作': True, '禁用撤销并重做': False, '捏合缩放旋转': True, '启用 3D 手指绘画': False})
    s += ring(*icon_pos('actions'), 18)
    s += badge(px + 85, py + 40, 1) + badge(px + pw - 28, py + 52, 2)
    s += label(px + 180, py + 270, '① 左边选「常规」', YEL1, 14)
    s += label(px + 180, py + 302, '② 打开「禁用触摸操作」', YEL1, 14)
    s += label(px + 180, py + 334, '之后手指只能缩放、撤销，不会画出东西', WHITE, 14)
    s += note('示意图：操作 › 偏好设置 › 手势控制')
    save('u-gesture', svg(W, H, s, '手势控制：常规里的禁用触摸操作'))


def u_pressure():
    s = f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>' + topbar('actions')
    px, py, pw, ph = 150, 66, 500, 450
    s += panel(px, py, pw, ph) + text(px + pw / 2, py + 30, '压力与平滑度', 18, 800, UITEXT, 'middle')
    gx, gy, gw, gh = px + 40, py + 60, 260, 260
    s += f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="{UIBAR}" stroke="#4B5563"/>'
    for i in range(1, 4):
        s += f'<line x1="{gx + gw * i / 4}" y1="{gy}" x2="{gx + gw * i / 4}" y2="{gy + gh}" stroke="#4B5563"/><line x1="{gx}" y1="{gy + gh * i / 4}" x2="{gx + gw}" y2="{gy + gh * i / 4}" stroke="#4B5563"/>'
    s += f'<line x1="{gx}" y1="{gy + gh}" x2="{gx + gw}" y2="{gy}" stroke="{UIDIM}" stroke-width="2" stroke-dasharray="5 4"/>'
    s += f'<path d="M{gx} {gy + gh} Q{gx + gw * 0.2} {gy + gh * 0.25} {gx + gw} {gy}" fill="none" stroke="{UIBLUE}" stroke-width="3.5"/>'
    s += f'<path d="M{gx} {gy + gh} Q{gx + gw * 0.8} {gy + gh * 0.8} {gx + gw} {gy}" fill="none" stroke="{PINK}" stroke-width="3.5"/>'
    s += text(gx + gw / 2, gy + gh + 22, '下笔力度 →', 13, 700, UITEXT, 'middle')
    s += f'<text x="{gx - 14}" y="{gy + gh / 2}" font-size="13" font-weight="700" fill="{UITEXT}" text-anchor="middle" transform="rotate(-90 {gx - 14} {gy + gh / 2})">笔画深浅 →</text>'
    s += label(gx + gw + 20, gy + 40, '蓝线：往左上拉', VIO1, 14) + text(gx + gw + 20, gy + 64, '轻轻画就有效果', 13, 600, UITEXT)
    s += text(gx + gw + 20, gy + 84, '适合下笔轻的人', 13, 600, UITEXT)
    s += label(gx + gw + 20, gy + 140, '粉线：往右下拉', PINK1, 14) + text(gx + gw + 20, gy + 164, '要用力画才有效果', 13, 600, UITEXT)
    s += text(gx + gw + 20, gy + 184, '适合下笔重的人', 13, 600, UITEXT)
    s += text(gx + gw + 20, gy + 240, '灰色虚线：默认', 13, 600, UIDIM)
    s += text(px + 40, py + ph - 26, '曲线上轻点可以加控制点；点「重置」恢复默认', 13, 600, UIDIM)
    s += ring(*icon_pos('actions'), 18)
    s += note('示意图：操作 › 偏好设置 › 压力与平滑度')
    save('u-pressure', svg(W, H, s, '压力曲线：往左上拉更灵敏，往右下拉更迟钝'))


def u_share():
    top, xs = gallery_top()
    s = top
    s += thumb(60, 100, 170, 220, 0, '雷电将军_01')
    # 左滑后的按钮
    for j, (b, col) in enumerate([('分享', '#2563EB'), ('复制', '#4B5563'), ('删除', '#DC2626')]):
        s += f'<rect x="{240 + j * 62}" y="160" width="58" height="100" rx="8" fill="{col}"/>' + text(240 + j * 62 + 29, 216, b, 15, 800, WHITE, 'middle')
    s += ringrect(237, 157, 64, 106)
    s += arrow(200, 372, 120, 372, UITEXT, 3) + text(160, 398, '在缩略图上向左轻滑', 14, 700, UITEXT, 'middle')
    px, py = 470, 90
    fm = ['Procreate', 'PSD', 'PDF', 'JPEG', 'PNG', 'TIFF', '动画 GIF']
    s += panel(px, py, 260, 36 + len(fm) * 38, '导出格式')
    for i, f in enumerate(fm):
        y = py + 44 + i * 38
        s += text(px + 18, y + 22, f, 15, 700, UITEXT)
        if f in ('Procreate', 'JPEG'):
            s += ringrect(px + 8, y - 2, 244, 34)
    s += badge(270, 148, 1) + badge(px + 270, py + 62, 2)
    s += label(px - 10, py + 340, 'Procreate：保留全部图层，用来备份', YEL1, 14)
    s += label(px - 10, py + 372, 'JPEG：最终交付用', YEL1, 14)
    s += note('示意图')
    save('u-share', svg(W, H, frame(s), '图库里向左滑动作品，点分享，选格式'))


# ---------------- 原理图 ----------------
def p_pixels():
    Wd, Hd = 760, 330
    s = [f'<rect x="20" y="10" width="720" height="310" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    # 左：一只眼睛（简化）
    s.append(f'<rect x="50" y="60" width="240" height="200" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<ellipse cx="170" cy="160" rx="80" ry="40" fill="{WHITE}" stroke="{INK}" stroke-width="3"/><circle cx="170" cy="160" r="32" fill="{VIO}"/><circle cx="170" cy="160" r="14" fill="{INK}"/><circle cx="182" cy="148" r="7" fill="{WHITE}"/>')
    s.append(f'<rect x="176" y="136" width="30" height="30" fill="none" stroke="{RED}" stroke-width="3"/>')
    s.append(label(50, 290, '原图：看起来是平滑的', YEL1, 14))
    s.append(arrow(300, 160, 380, 160, INK, 3))
    s.append(text(340, 146, '放大', 14, 800, INK, 'middle'))
    # 右：像素格
    random.seed(3)
    cols = ['#8B5CF6', '#7C3AED', '#A78BFA', '#FFFFFF', '#E9E5FF', '#1E293B', '#6D28D9']
    n = 8; cell = 26; ox, oy = 400, 56
    for i in range(n):
        for j in range(n):
            d = math.hypot(i - 5.2, j - 2.6)
            if d < 1.4: c = '#FFFFFF'
            elif d < 2.2: c = '#E9E5FF'
            elif i + j > 11: c = '#1E293B'
            elif d < 3.4: c = '#A78BFA'
            else: c = random.choice(['#8B5CF6', '#7C3AED'])
            s.append(f'<rect x="{ox + i * cell}" y="{oy + j * cell}" width="{cell}" height="{cell}" fill="{c}" stroke="#94A3B8" stroke-width=".8"/>')
    s.append(label(400, 290, '放大到最后：一个个单色的小方块', YEL1, 14))
    s.append(text(630, 120, '每一格', 14, 700) + text(630, 142, '就是一个像素', 14, 700))
    s.append(text(630, 182, '4032 × 3024', 14, 800, VIO7) + text(630, 204, '≈ 1200 万个', 14, 700, VIO7))
    save('p-pixels', svg(Wd, Hd, ''.join(s), '像素：图片放大到最后是一个个单色小方块'))


def p_bits():
    Wd, Hd = 760, 360
    s = [f'<rect x="20" y="10" width="720" height="340" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    s.append(text(50, 52, '同一段暗部，后期提亮之后：', 16, 800))
    for row, (name, levels, fill) in enumerate([('JPG：只有 256 级', 10, RED1), ('RAW：上千级', 200, MINT1)]):
        y = 90 + row * 120
        s.append(label(50, y, name, fill, 14))
        x0, w, h = 50, 660, 56
        for k in range(levels):
            t = k / (levels - 1)
            v = int(40 + t * 180)
            c = f'#{v:02x}{int(v * 0.85):02x}{int(v * 0.95):02x}'
            s.append(f'<rect x="{x0 + w * k / levels:.2f}" y="{y + 12}" width="{w / levels + 0.6:.2f}" height="{h}" fill="{c}"/>')
        s.append(f'<rect x="{x0}" y="{y + 12}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>')
    s.append(text(50, 336, '暗部原本只占用很少几级亮度，拉亮以后，JPG 能用的级数不够，就断成一条条色带。', 14, 600, MUTED))
    save('p-bits', svg(Wd, Hd, ''.join(s), 'JPG 和 RAW 提亮暗部后的区别：JPG 出现色带'))


def p_gamut():
    Wd, Hd = 760, 340
    s = [f'<rect x="20" y="10" width="720" height="320" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    # 简化色域三角形
    def tri(pts, fill, op, stroke, dash=''):
        d = 'M' + ' L'.join(f'{x} {y}' for x, y in pts) + ' Z'
        return f'<path d="{d}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="3" {dash}/>'
    p3 = [(120, 280), (250, 50), (400, 280)]
    srgb = [(140, 265), (245, 85), (370, 268)]
    s.append(tri(p3, VIO2, .35, VIO7))
    s.append(tri(srgb, MINT, .35, MINT7, 'stroke-dasharray="7 5"'))
    s.append(label(270, 66, 'Display P3', VIO1, 14) + label(196, 210, 'sRGB', MINT1, 14))
    s.append(f'<circle cx="252" cy="62" r="7" fill="{RED}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(440, 80, '外圈：P3 能显示的颜色', 15, 700, VIO7))
    s.append(text(440, 106, '内圈：sRGB 能显示的颜色', 15, 700, MINT7))
    s.append(text(440, 150, '红点：只有 P3 才有的', 15, 700) + text(440, 174, '很饱和的绿、红、橙', 15, 700))
    s.append(text(440, 218, '不支持 P3 的平台和设备', 15, 600, MUTED) + text(440, 242, '会把它挤进 sRGB 里显示，', 15, 600, MUTED))
    s.append(text(440, 266, '颜色就变灰、变淡或偏了。', 15, 600, MUTED))
    save('p-gamut', svg(Wd, Hd, ''.join(s), '色域示意：P3 比 sRGB 能显示更多饱和的颜色'))


def p_compress():
    Wd, Hd = 760, 300
    s = [f'<rect x="20" y="10" width="720" height="280" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    for col, (name, q) in enumerate([('高质量 JPEG', 0), ('低质量 JPEG，放大到 200%', 1)]):
        ox = 50 + col * 350
        s.append(label(ox, 50, name, MINT1 if q == 0 else RED1, 14))
        x0, y0, w, h = ox, 70, 300, 190
        if q == 0:
            s.append(f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7DD3FC"/><stop offset="1" stop-color="#FDE68A"/></linearGradient></defs>')
            s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="url(#sky)"/>')
            s.append(f'<path d="M{x0 + 120} {y0 + h} C{x0 + 110} {y0 + 90} {x0 + 150} {y0 + 40} {x0 + 170} {y0 + 30}" fill="none" stroke="{INK}" stroke-width="3"/>')
        else:
            blk = 24
            for i in range(int(w / blk) + 1):
                for j in range(int(h / blk) + 1):
                    t = min(1, (j * blk) / h)
                    t = round(t * 5) / 5
                    r = int(0x7D + (0xFD - 0x7D) * t); g = int(0xD3 + (0xE6 - 0xD3) * t); b = int(0xFC + (0x8A - 0xFC) * t)
                    bw = min(blk, w - i * blk); bh = min(blk, h - j * blk)
                    if bw > 0 and bh > 0:
                        s.append(f'<rect x="{x0 + i * blk}" y="{y0 + j * blk}" width="{bw}" height="{bh}" fill="#{r:02x}{g:02x}{b:02x}"/>')
            s.append(f'<path d="M{x0 + 120} {y0 + h} C{x0 + 110} {y0 + 90} {x0 + 150} {y0 + 40} {x0 + 170} {y0 + 30}" fill="none" stroke="{INK}" stroke-width="7" stroke-opacity=".25"/>'
                     f'<path d="M{x0 + 120} {y0 + h} C{x0 + 110} {y0 + 90} {x0 + 150} {y0 + 40} {x0 + 170} {y0 + 30}" fill="none" stroke="{INK}" stroke-width="3"/>')
            s.append(label(x0 + 190, y0 + 60, '色块', YEL1, 13) + label(x0 + 150, y0 + 130, '线边发脏', YEL1, 13))
        s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>')
    save('p-compress', svg(Wd, Hd, ''.join(s), 'JPEG 压缩痕迹：色块、渐变断层、边缘发脏'))


def p_hist_zones():
    Wd, Hd = 760, 330
    s = [f'<rect x="20" y="10" width="720" height="310" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    x0, y0, w, h = 60, 50, 640, 170
    zones = [('黑', 0.0, 0.06), ('暗部', 0.06, 0.32), ('中间调', 0.32, 0.68), ('亮部', 0.68, 0.94), ('白', 0.94, 1.0)]
    for i, (n, a, b) in enumerate(zones):
        v = int(30 + (a + b) / 2 * 210)
        s.append(f'<rect x="{x0 + w * a:.1f}" y="{y0 + h + 8}" width="{w * (b - a):.1f}" height="26" fill="#{v:02x}{v:02x}{v:02x}" stroke="{INK}" stroke-width="1.5"/>')
        s.append(text(x0 + w * (a + b) / 2, y0 + h + 58, n, 14, 800, INK, 'middle'))
    pts = []
    for k in range(101):
        t = k / 100
        v = 0.25 * math.exp(-((t - 0.22) / 0.1) ** 2) + 0.9 * math.exp(-((t - 0.58) / 0.08) ** 2) + 0.35 * math.exp(-((t - 0.8) / 0.08) ** 2) + 0.05
        pts.append((x0 + t * w, y0 + h - v * (h - 10)))
    d = f'M{x0} {y0 + h} ' + ' '.join(f'L{a:.1f} {b:.1f}' for a, b in pts) + f' L{x0 + w} {y0 + h} Z'
    s.append(f'<path d="{d}" fill="{VIO2}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>')
    s.append(arrow(x0 + w * 0.58, y0 - 4, x0 + w * 0.58, y0 + 24, INK, 2.5))
    s.append(label(x0 + w * 0.58 + 8, y0 + 14, '这座山多半是脸和皮肤', YEL1, 13))
    s.append(label(x0 + w * 0.2 - 30, y0 + 70, '头发、深色衣服', WHITE, 13))
    s.append(label(x0 + w * 0.8 - 10, y0 + 70, '背景墙', WHITE, 13))
    s.append(text(x0, y0 + h + 92, '人像里，脸一般落在中间调偏亮的位置。脸要是挤在暗部或贴到白，说明曝光有问题。', 14, 600, MUTED))
    save('p-hist-zones', svg(Wd, Hd, ''.join(s), '直方图分区：黑、暗部、中间调、亮部、白'))


def p_flow():
    Wd, Hd = 760, 330
    s = [f'<rect x="20" y="10" width="720" height="310" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    steps = [('选片', '挑表情、动作、对焦', WHITE), ('基础调整', 'Lightroom：曝光、白平衡', MINT1), ('精修', 'Procreate：皮肤、光影、假发、比例', VIO1),
             ('特效和合成', 'Procreate：光效、换背景', VIO1), ('统一调色', 'Lightroom 或渐变映射', MINT1), ('导出交付', 'sRGB、命名、留分层', YEL1)]
    for i, (t, d, fill) in enumerate(steps):
        col, row = i % 3, i // 3
        x = 40 + col * 236; y = 40 + row * 140
        s.append(f'<rect x="{x + 4}" y="{y + 4}" width="210" height="100" rx="14" fill="{INK}"/><rect x="{x}" y="{y}" width="210" height="100" rx="14" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(badge(x + 26, y + 28, i + 1))
        s.append(text(x + 48, y + 34, t, 18, 800))
        words = d
        s.append(text(x + 16, y + 70, words[:13], 13, 600, MUTED))
        if len(words) > 13:
            s.append(text(x + 16, y + 90, words[13:], 13, 600, MUTED))
        if col < 2:
            s.append(arrow(x + 214, y + 50, x + 232, y + 50, INK, 3))
    s.append(f'<path d="M{40 + 2 * 236 + 105} {144} C{40 + 2 * 236 + 105} {162} {40 + 105} {162} {40 + 105} {176}" fill="none" stroke="{INK}" stroke-width="3" marker-end="url(#arw)"/>')
    save('p-flow', svg(Wd, Hd, ''.join(s), '后期全流程 6 步'))



# ================= v4 新增 =================
def check(x, y, on=True):
    """图库选择模式里的蓝色小勾"""
    if on:
        return (f'<circle cx="{x}" cy="{y}" r="12" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
                f'<path d="M{x - 6} {y} l4 5 l8 -10" fill="none" stroke="{WHITE}" stroke-width="3" stroke-linecap="round"/>')
    return f'<circle cx="{x}" cy="{y}" r="12" fill="none" stroke="{UIDIM}" stroke-width="2"/>'


def info_panel(tab, rows, hl_row=0, px=170, py=70, pw=460, ph=440):
    """画布信息面板：tab 为左边选中的分类，rows 为右边 [(名称, 值)]"""
    s = panel(px, py, pw, ph) + text(px + pw / 2, py + 30, '画布信息', 18, 800, UITEXT, 'middle')
    cats = ['关于本作品', '尺寸', '图层', '颜色配置文件', '视频设置', '统计']
    for i, t in enumerate(cats):
        y = py + 56 + i * 42
        s += f'<rect x="{px + 12}" y="{y}" width="140" height="34" rx="8" fill="{UIBLUE if t == tab else UIBAR}"/>' + text(px + 24, y + 23, t, 14, 700, UITEXT)
    for i, (k, v) in enumerate(rows):
        y = py + 60 + i * 46
        s += text(px + 172, y + 22, k, 15, 700, UITEXT) + text(px + pw - 20, y + 22, v, 15, 800, YEL if i == hl_row else UITEXT, 'end')
    return s


def u_pressure_test():
    strokes = (f'<path d="M290 170 C340 150 400 190 460 165" fill="none" stroke="{VIO}" stroke-opacity=".35" stroke-width="5" stroke-linecap="round"/>'
               f'<path d="M290 300 C340 280 400 320 460 295" fill="none" stroke="{VIO7}" stroke-width="22" stroke-linecap="round"/>')
    cont = canvas(strokes, x=250, y=70, w=250, h=410)
    cont += text(275, 140, '轻轻画', 14, 800, INK) + text(275, 268, '用力画', 14, 800, INK)
    px, py, pw = 520, 62, 254
    lib = panel(px, py, pw, 330, '画笔库')
    groups = ['素描', '着墨', '绘图', '上漆', '艺术效果', '书法', '气笔修饰', '纹理']
    for i, g in enumerate(groups):
        y = py + 44 + i * 34
        lib += f'<rect x="{px + 8}" y="{y}" width="96" height="28" rx="6" fill="{UIBLUE if g == "气笔修饰" else UIBAR}"/>' + text(px + 16, y + 19, g, 13, 700, UITEXT)
    for i, b in enumerate(['软画笔', '中等画笔', '硬画笔', '软气笔']):
        y = py + 44 + i * 52
        lib += f'<rect x="{px + 112}" y="{y}" width="134" height="44" rx="6" fill="{UIBAR}"/>' + text(px + 122, y + 18, b, 13, 700, UITEXT)
        lib += f'<path d="M{px + 122} {y + 34} q30 -10 60 0 t50 0" fill="none" stroke="{UITEXT}" stroke-opacity="{.9 - i * .15}" stroke-width="{6 - i}" stroke-linecap="round"/>'
    lib += ringrect(px + 4, py + 44 + 6 * 34 - 3, 104, 34) + ringrect(px + 108, py + 41, 142, 50)
    s = screen(cont + lib, active='brush')
    s += ring(*icon_pos('brush'), 18)
    s += badge(icon_pos('brush')[0] - 26, 60, 1) + badge(px - 4, py + 44 + 6 * 34 + 14, 2) + badge(px + 236, py + 100, 3)
    s += label(520, 430, '① 画笔图标 ② 气笔修饰 ③ 软画笔', YEL1, 14)
    s += label(520, 466, '轻的一笔淡、重的一笔深 = 有压感', MINT1, 14)
    s += note('示意图：画笔名称和排列以实际界面为准')
    save('u-pressure-test', svg(W, H, s, '在气笔修饰里选软画笔，轻画一笔、重画一笔'))


def u_cursor():
    cur = (f'<circle cx="400" cy="300" r="34" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="4 3"/>'
           f'<line x1="400" y1="300" x2="455" y2="250" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>'
           f'<line x1="400" y1="300" x2="455" y2="250" stroke="{WHITE}" stroke-width="3" stroke-linecap="round"/>')
    cont = canvas(cur, x=420, y=200, w=0, h=0) if False else canvas(cur)
    rows = ['浅色界面', '右侧界面', '画笔光标', '动态画笔缩放', '投射画布', '快速撤销延迟', '压力与平滑度', '手势控制']
    menu = actions_menu('偏好设置', rows=rows, hl='画笔光标', x=40, y=62, w=300,
                        toggles={'浅色界面': False, '右侧界面': False, '画笔光标': True, '投射画布': False})
    s = screen(cont + menu, active='actions', side=False)
    s += ring(*icon_pos('actions'), 18) + badge(330, 62 + 50 + 2 * 34 + 17, 1)
    s += label(560, 270, '笔尖碰到画布时', YEL1, 14) + label(560, 302, '出现一圈笔刷边缘', YEL1, 14)
    s += arrow(555, 290, 440, 300, INK, 2.5)
    s += label(40, 470, '① 操作 › 偏好设置 › 打开「画笔光标」', YEL1, 14)
    s += note('示意图：偏好设置的排列以实际界面为准')
    save('u-cursor', svg(W, H, s, '偏好设置里打开画笔光标'))


def u_canvas_size():
    s = f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>' + topbar('actions')
    s += info_panel('尺寸', [('像素宽度', '4032 px'), ('像素高度', '3024 px'), ('物理宽度', '（按 DPI 换算）'), ('DPI', '（显示值）')])
    s += ringrect(170 + 162, 70 + 56, 460 - 174, 80)
    s += ring(*icon_pos('actions'), 18)
    s += badge(170 - 2, 70 + 56 + 42 + 17, 1) + badge(170 + 460 - 20, 70 + 46, 2)
    s += label(342, 330, '① 左边点「尺寸」', YEL1, 14)
    s += label(342, 362, '② 看像素宽度和高度，长边是较大的那个', YEL1, 14)
    s += label(342, 394, '改 DPI 不会改变像素数', WHITE, 14)
    s += note('示意图：操作 › 画布 › 画布信息；4032 × 3024 是示范读数')
    save('u-canvas-size', svg(W, H, s, '画布信息的尺寸一栏：像素宽度和高度'))


def u_color_profile():
    s = f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>' + topbar('actions')
    px, py, pw = 170, 70, 460
    s += info_panel('颜色配置文件', [], px=px, py=py, pw=pw)
    s += text(px + 172, py + 80, 'RGB', 14, 800, UIDIM)
    for i, r in enumerate(['Display P3', 'sRGB IEC61966-2.1', '其他 RGB 配置……']):
        y = py + 92 + i * 40
        s += f'<rect x="{px + 166}" y="{y}" width="{pw - 182}" height="34" rx="8" fill="{UIBAR}"/>' + text(px + 180, y + 23, r, 14, 700, UITEXT)
        if i == 1:
            s += text(px + pw - 30, y + 23, '✓', 16, 900, UIBLUE, 'end') + ringrect(px + 162, y - 3, pw - 174, 40)
    s += text(px + 172, py + 240, 'CMYK（RGB 画布不能换成 CMYK）', 14, 700, UIDIM)
    s += ring(*icon_pos('actions'), 18)
    s += badge(px - 2, py + 56 + 3 * 42 + 17, 1) + badge(px + pw - 14, py + 92 + 40 + 17, 2)
    s += label(px + 172, py + 300, '① 左边点「颜色配置文件」', YEL1, 14)
    s += label(px + 172, py + 332, '② 选 sRGB IEC61966-2.1', YEL1, 14)
    s += label(px + 172, py + 364, '改之前先在图库里复制一份作品', WHITE, 14)
    s += note('示意图：列表内容以实际界面为准')
    save('u-color-profile', svg(W, H, s, '画布信息里把颜色配置文件改成 sRGB'))


def select_top(hl=None):
    s = text(SX + 26, 52, '选择', 20, 800, UIBLUE)
    xs = {'堆': 470, '预览': 530, '分享': 600, '复制': 670, '删除': 740}
    for k, x in xs.items():
        s += text(x, 52, k, 17, 700, UITEXT, 'middle')
        if hl == k:
            s += ringrect(x - 28, 26, 56, 38)
    return s, xs


def gallery_grid(names, checked=(), y=100, kinds=None):
    s = ''
    pos = []
    for i, n in enumerate(names):
        x = 50 + (i % 4) * 180
        yy = y + (i // 4) * 210
        s += thumb(x, yy, 140, 160, (kinds[i] if kinds else i % 3), n)
        if checked is not None:
            s += check(x + 124, yy + 144, i in checked)
        pos.append((x, yy))
    return s, pos


def u_gallery_select(name='u-gallery-select', fmt='Procreate', title='选择模式里勾选多张作品，一起分享'):
    top, xs = select_top('分享')
    names = ['雷电将军_01', '雷电将军_02', '雷电将军_03', '雷电将军_04', '练习_光影球', '未命名作品']
    grid, pos = gallery_grid(names, checked=(0, 1, 2, 3), y=90)
    s = top + grid
    px, py = 548, 280
    fm = ['Procreate', 'PSD', 'PDF', 'JPEG', 'PNG', 'TIFF']
    s += panel(px, py, 220, 48 + len(fm) * 30, '导出格式')
    for i, f in enumerate(fm):
        y = py + 40 + i * 30
        s += text(px + 18, y + 20, f, 14, 700, UITEXT)
        if f == fmt:
            s += ringrect(px + 8, y - 1, 204, 28)
    s += badge(SX + 60, 82, 1) + badge(pos[0][0] + 124, pos[0][1] + 120, 2) + badge(xs['分享'], 82, 3) + badge(px + 230, py + 40 + fm.index(fmt) * 30 + 14, 4)
    s += label(40, 520, f'① 点「选择」 ② 轻点作品出现蓝勾 ③ 分享 ④ 选「{fmt}」', YEL1, 14)
    s += note('示意图：选择模式顶部按钮以实际界面为准')
    save(name, svg(W, H, frame(s), title))


def u_rename():
    top, xs = gallery_top()
    names = ['雷电将军_01', '雷电将军_02', '未命名作品']
    grid, pos = gallery_grid(names, checked=None, y=90)
    s = top + grid
    x, y = pos[2]
    s += f'<rect x="{x - 6}" y="{y + 166}" width="210" height="30" rx="6" fill="{WHITE}" stroke="{UIBLUE}" stroke-width="2"/>'
    s += text(x + 2, y + 187, '雷电将军_20261021_03', 13, 700, INK) + f'<line x1="{x + 172}" y1="{y + 172}" x2="{x + 172}" y2="{y + 192}" stroke="{UIBLUE}" stroke-width="2"/>'
    s += ringrect(x - 10, y + 162, 218, 38)
    s += badge(x + 220, y + 181, 1)
    # 屏幕键盘
    ky = 330
    s += f'<rect x="{SX}" y="{ky}" width="{SW}" height="{SY + SH - ky}" fill="#4B5563"/>'
    rows = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM']
    for r, keys in enumerate(rows):
        kx0 = 60 + r * 30
        for j, k in enumerate(keys):
            s += f'<rect x="{kx0 + j * 66}" y="{ky + 18 + r * 52}" width="58" height="42" rx="6" fill="#9CA3AF"/>' + text(kx0 + j * 66 + 29, ky + 46 + r * 52, k, 15, 700, INK, 'middle')
    s += f'<rect x="620" y="{ky + 122}" width="140" height="42" rx="6" fill="{UIBLUE}"/>' + text(690, ky + 150, '完成', 15, 800, WHITE, 'middle')
    s += badge(770, ky + 112, 2) + ringrect(616, ky + 118, 148, 50)
    s += label(40, ky - 20, '① 轻点作品下面的名字 → 输入新名字  ② 完成', YEL1, 14)
    s += note('示意图')
    save('u-rename', svg(W, H, frame(s), '图库里轻点作品名称，用键盘改名'))


def u_stack():
    top, xs = gallery_top()
    s = top
    # 被拖着的作品
    s += thumb(60, 100, 140, 160, 0, '雷电将军_02')
    s += f'<rect x="56" y="96" width="148" height="168" rx="8" fill="none" stroke="{UIDIM}" stroke-width="2" stroke-dasharray="6 4"/>'
    s += f'<g transform="translate(190 120) rotate(-6)"><rect x="0" y="0" width="140" height="160" rx="6" fill="#FFF7E6" opacity=".85"/>' \
         f'<path d="M70 152 q-14 -40 0 -70 q14 30 0 70" fill="{PINK}" stroke="{INK}" stroke-width="1.5"/></g>'
    s += f'<ellipse cx="270" cy="210" rx="10" ry="13" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>'
    # 目标作品，高亮
    s += thumb(370, 100, 140, 160, 0, '雷电将军_01')
    s += f'<rect x="364" y="94" width="152" height="172" rx="9" fill="none" stroke="{UIBLUE}" stroke-width="4"/>'
    s += arrow(290, 200, 356, 190, YEL, 4)
    s += badge(240, 108, 1) + badge(500, 108, 2)
    # 结果：一个堆
    sx, sy = 580, 110
    for k in range(3):
        s += f'<rect x="{sx + 8 - k * 6}" y="{sy - 8 + k * 6}" width="140" height="160" rx="6" fill="#FFF7E6" stroke="{INK}" stroke-width="1.5"/>'
    s += f'<path d="M{sx + 66} {sy + 150} q-14 -40 0 -70 q14 30 0 70" fill="{PINK}" stroke="{INK}" stroke-width="1.5"/>'
    s += text(sx - 4, sy + 190, '堆 → 改名「雷电将军_20261021」', 12, 700, UITEXT)
    s += arrow(520, 180, 566, 180, UITEXT, 3)
    s += label(40, 360, '① 按住一张作品拖起来  ② 拖到另一张上，它变蓝时松手', YEL1, 14)
    s += label(40, 396, '两张叠成一个「堆」；名字默认叫「堆」，轻点名字改', YEL1, 14)
    s += label(40, 432, '也可以：「选择」勾上几张 → 点顶上的「堆」', WHITE, 14)
    s += label(40, 468, '往已有的堆里加：拖到堆上多停一会儿，等它闪两下再进去放', WHITE, 14)
    s += note('示意图')
    save('u-stack', svg(W, H, frame(s), '把一张作品拖到另一张上，叠成一个堆'))


# ---------- Lightroom 手机版示意 ----------
def lr_frame(inner, note_text):
    s = f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#18191C"/>'
    s += f'<rect x="{SX}" y="{SY}" width="{SW}" height="46" rx="16" fill="#26282C"/>'
    s += text(SX + 22, 44, '‹', 26, 700, UITEXT) + text(SX + 50, 44, 'Lightroom（示意）', 15, 700, UIDIM)
    return s + inner + text(SX + SW - 12, SY + SH - 10, note_text, 12, 600, UIDIM, 'end')


def mini_photo(x, y, w, h):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#5B6B8C"/>'
    s += f'<rect x="{x}" y="{y + h * 0.72}" width="{w}" height="{h * 0.28}" fill="#3B4458"/>'
    cx = x + w / 2
    s += f'<path d="M{cx - 60} {y + h} Q{cx} {y + h * 0.55} {cx + 60} {y + h} Z" fill="{VIO2}" stroke="{INK}" stroke-width="2"/>'
    s += f'<circle cx="{cx}" cy="{y + h * 0.45}" r="{h * 0.13}" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>'
    s += f'<path d="M{cx - h * 0.16} {y + h * 0.47} Q{cx - h * 0.18} {y + h * 0.26} {cx} {y + h * 0.27} Q{cx + h * 0.18} {y + h * 0.26} {cx + h * 0.16} {y + h * 0.47} Q{cx + h * 0.05} {y + h * 0.36} {cx - h * 0.16} {y + h * 0.47} Z" fill="{PINK}" stroke="{INK}" stroke-width="2"/>'
    return s


def hist_path(x0, y0, w, h, bumps, base=0.03, clipL=0, clipR=0, fill=VIO2, stroke=INK):
    pts = []
    for k in range(121):
        t = k / 120
        v = base + sum(a * math.exp(-((t - c) / sd) ** 2) for a, c, sd in bumps)
        pts.append((x0 + t * w, y0 + h - min(v, 1) * (h - 6)))
    d = f'M{x0} {y0 + h} ' + ' '.join(f'L{a:.1f} {b:.1f}' for a, b in pts) + f' L{x0 + w} {y0 + h} Z'
    s = f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>'
    if clipL:
        s += f'<rect x="{x0}" y="{y0 + h - clipL * (h - 6):.1f}" width="5" height="{clipL * (h - 6):.1f}" fill="{RED}"/>'
    if clipR:
        s += f'<rect x="{x0 + w - 5}" y="{y0 + h - clipR * (h - 6):.1f}" width="5" height="{clipR * (h - 6):.1f}" fill="{RED}"/>'
    return s


def u_lr_histogram():
    s = mini_photo(140, 80, 520, 380)
    hx, hy, hw, hh = 156, 92, 170, 76
    s += f'<rect x="{hx - 6}" y="{hy - 6}" width="{hw + 12}" height="{hh + 12}" rx="8" fill="#000" fill-opacity=".55"/>'
    s += hist_path(hx, hy, hw, hh, [(0.5, 0.3, 0.12), (0.8, 0.58, 0.1)], fill='#E5E7EB', stroke='#E5E7EB')
    s += ringrect(hx - 9, hy - 9, hw + 18, hh + 18)
    # 两指轻点
    for dx in (-14, 14):
        s += f'<ellipse cx="{240 + dx}" cy="390" rx="11" ry="14" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>'
    s += f'<circle cx="240" cy="390" r="34" fill="none" stroke="{YEL}" stroke-width="3" stroke-dasharray="5 4"/>'
    s += badge(286, 358, 1) + badge(hx + hw + 18, hy + 6, 2)
    # 选项菜单
    s += text(SX + SW - 30, 44, '…', 26, 900, UITEXT, 'middle') + ring(SX + SW - 30, 36, 16)
    mx, my = 560, 64
    s += panel(mx, my, 210, 132)
    for i, r in enumerate(['视图选项 ›', '无叠加', '文件信息', '直方图']):
        s += text(mx + 16, my + 28 + i * 30, r, 14, 700 if i else 800, UITEXT if i != 3 else YEL)
    s += ringrect(mx + 6, my + 98, 198, 28) + badge(mx - 6, my + 112, 3)
    s += label(150, 492, '① 编辑时两根手指在照片上轻点  ② 直方图出现在角落', YEL1, 14)
    s += label(150, 526, '③ 或者：「…」选项 › 视图选项 › 直方图', WHITE, 14)
    save('u-lr-histogram', svg(W, H, lr_frame(s, '示意图，不是真机截图；位置以 App 为准'), 'Lightroom 手机版里打开直方图'))


def u_lr_export():
    s = mini_photo(40, 80, 300, 300)
    s += text(SX + SW - 80, 44, '⇪', 22, 800, UITEXT, 'middle') + ring(SX + SW - 80, 37, 16) + badge(SX + SW - 110, 37, 1)
    px, py, pw = 380, 66, 390
    s += panel(px, py, pw, 440) + text(px + 18, py + 30, '导出为', 18, 800, UITEXT) + text(px + pw - 18, py + 30, '完成', 16, 800, UIBLUE, 'end')
    rows = [('文件类型', 'JPG'), ('尺寸', '最大可用尺寸'), ('质量', '100%'), ('包含水印', '（付费功能）'), ('更多选项', '›'), ('色彩空间', 'sRGB')]
    for i, (k, v) in enumerate(rows):
        y = py + 52 + i * 52
        s += f'<rect x="{px + 12}" y="{y}" width="{pw - 24}" height="44" rx="8" fill="{UIBAR}"/>'
        s += text(px + 26, y + 28, k, 15, 700, UITEXT if i != 5 else UITEXT) + text(px + pw - 26, y + 28, v, 15, 800, YEL if i in (0, 2, 5) else UIDIM, 'end')
        if i in (0, 2, 5):
            s += ringrect(px + 8, y - 3, pw - 16, 50)
    s += f'<line x1="{px + 30}" y1="{py + 52 + 5 * 52 - 4}" x2="{px + 30}" y2="{py + 52 + 4 * 52 + 46}" stroke="{UIDIM}" stroke-width="2"/>'
    s += badge(px + pw + 2, py + 52 + 22, 2) + badge(px + pw + 2, py + 52 + 2 * 52 + 22, 3) + badge(px + pw + 2, py + 52 + 5 * 52 + 22, 4) + badge(px + pw - 76, py + 24, 5)
    s += label(40, 420, '① 共享 › 导出为', YEL1, 14)
    s += label(40, 452, '② 文件类型 JPG', YEL1, 14)
    s += label(40, 484, '③ 质量 100%（官方范围 10%～100%）', YEL1, 14)
    s += label(40, 516, '④ 色彩空间选 sRGB  ⑤ 完成', YEL1, 14)
    save('u-lr-export', svg(W, H, lr_frame(s, '示意图：色彩空间的位置和名称以 App 为准'), 'Lightroom 手机版的导出为面板：文件类型、质量、色彩空间'))


def u_zoom_check():
    # 画布：放大后的头发边缘和渐变背景，带色块
    cx, cy, cw, ch = 120, 70, 560, 400
    s = f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>'
    blk = 40
    for i in range(cw // blk):
        for j in range(ch // blk):
            t = round(j / (ch / blk) * 4) / 4
            r = int(0x7D + (0xFD - 0x7D) * t); g = int(0xD3 + (0xE6 - 0xD3) * t); b = int(0xFC + (0x8A - 0xFC) * t)
            s += f'<rect x="{cx + i * blk}" y="{cy + j * blk}" width="{blk}" height="{blk}" fill="#{r:02x}{g:02x}{b:02x}"/>'
    s += f'<path d="M{cx} {cy + 300} C{cx + 160} {cy + 250} {cx + 260} {cy + 360} {cx + 560} {cy + 280} L{cx + 560} {cy + 400} L{cx} {cy + 400} Z" fill="{PINK}"/>'
    s += f'<path d="M{cx} {cy + 300} C{cx + 160} {cy + 250} {cx + 260} {cy + 360} {cx + 560} {cy + 280}" fill="none" stroke="{INK}" stroke-width="12" stroke-opacity=".22"/>'
    s += f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" fill="none" stroke="#94A3B8"/>'
    s += topbar(None)
    s += f'<rect x="350" y="70" width="100" height="34" rx="17" fill="{UIBAR}"/>' + text(400, 93, '200%', 16, 800, WHITE, 'middle')
    s += ringrect(346, 66, 108, 42) + badge(466, 87, 2)
    # 双指张开
    for (fx, fy, ax, ay) in [(330, 330, 290, 370), (470, 250, 510, 210)]:
        s += f'<ellipse cx="{fx}" cy="{fy}" rx="12" ry="15" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>' + arrow(fx, fy, ax, ay, INK, 3)
    s += badge(400, 300, 1)
    s += label(140, 140, '色块：一格一格的方块', YEL1, 14) + label(140, 176, '渐变断成几条色带', YEL1, 14)
    s += label(430, 420, '头发边缘一圈发脏', YEL1, 14)
    s += label(130, 516, '① 两指张开放大  ② 上方显示的百分比到 200% 左右停', WHITE, 14)
    s += sidebar()
    s += note('示意图：缩放百分比的显示样式以实际界面为准')
    save('u-zoom-check', svg(W, H, f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/>' + s, '两指放大到 200% 左右，检查压缩痕迹'))


# ---------- 0.2 读直方图的三个案例 ----------
def bust(cx, base, h, face=SKIN, cloth=VIO2, hair=PINK, sw=2):
    s = f'<path d="M{cx - h * 0.9} {base} Q{cx} {base - h * 0.9} {cx + h * 0.9} {base} Z" fill="{cloth}" stroke="{INK}" stroke-width="{sw}"/>'
    s += f'<rect x="{cx - h * 0.12}" y="{base - h * 0.75}" width="{h * 0.24}" height="{h * 0.3}" fill="{face}" stroke="{INK}" stroke-width="{sw}"/>'
    s += f'<ellipse cx="{cx}" cy="{base - h * 1.0}" rx="{h * 0.32}" ry="{h * 0.38}" fill="{face}" stroke="{INK}" stroke-width="{sw}"/>'
    s += (f'<path d="M{cx - h * 0.4} {base - h * 0.85} Q{cx - h * 0.45} {base - h * 1.48} {cx} {base - h * 1.45} Q{cx + h * 0.45} {base - h * 1.48} {cx + h * 0.4} {base - h * 0.85} '
          f'Q{cx + h * 0.2} {base - h * 1.25} {cx - h * 0.05} {base - h * 1.18} Q{cx - h * 0.3} {base - h * 1.2} {cx - h * 0.4} {base - h * 0.85} Z" fill="{hair}" stroke="{INK}" stroke-width="{sw}"/>')
    return s


def hist_case(name, title, scene_svg, bumps, notes, clipL=0, clipR=0, caption=''):
    Wd, Hd = 760, 360
    s = [f'<rect x="20" y="10" width="720" height="340" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    s.append(f'<clipPath id="cp-{name}"><rect x="40" y="40" width="260" height="260" rx="8"/></clipPath>')
    s.append(f'<g clip-path="url(#cp-{name})">{scene_svg}</g><rect x="40" y="40" width="260" height="260" rx="8" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    x0, y0, w, h = 340, 60, 370, 170
    s.append(hist_path(x0, y0, w, h, bumps, clipL=clipL, clipR=clipR))
    s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>')
    zones = [('黑', 0, .06), ('暗部', .06, .32), ('中间调', .32, .68), ('亮部', .68, .94), ('白', .94, 1)]
    for n, a, b in zones:
        v = int(30 + (a + b) / 2 * 210)
        s.append(f'<rect x="{x0 + w * a:.1f}" y="{y0 + h + 4}" width="{w * (b - a):.1f}" height="14" fill="#{v:02x}{v:02x}{v:02x}" stroke="{INK}" stroke-width="1"/>')
        if b - a > .1:
            s.append(text(x0 + w * (a + b) / 2, y0 + h + 36, n, 12, 700, MUTED, 'middle'))
    for (tx, ty, t, col) in notes:
        s.append(label(tx, ty, t, col, 13))
    if caption:
        s.append(text(40, 334, caption, 13, 600, MUTED))
    save(name, svg(Wd, Hd, ''.join(s), title))


def case_hist_indoor():
    sc = f'<rect x="40" y="40" width="260" height="260" fill="#5B5F6B"/>'
    for x in (80, 170, 260):
        sc += f'<circle cx="{x}" cy="58" r="13" fill="{WHITE}" stroke="{YEL}" stroke-width="3"/>'
    for x in (60, 110, 230, 280):
        sc += f'<circle cx="{x}" cy="200" r="16" fill="#3A3D45"/><rect x="{x - 20}" y="214" width="40" height="90" rx="14" fill="#3A3D45"/>'
    sc += bust(170, 300, 110)
    hist_case('case-hist-indoor', '漫展室内场照的直方图', sc,
              [(0.55, 0.24, 0.1), (0.75, 0.6, 0.08), (0.25, 0.8, 0.06)], clipR=0.35,
              notes=[(345, 112, '人群、场馆暗处', WHITE), (520, 80, '脸、皮肤', YEL1), (596, 158, '右端窄尖：顶灯', RED1)],
              caption='示范读数：右端一根窄尖贴墙（顶灯），左端没贴墙，脸在中间调偏亮。')


def case_hist_backlit():
    sc = f'<rect x="40" y="40" width="260" height="260" fill="#FFFFFF"/>'
    sc += f'<circle cx="250" cy="80" r="40" fill="{WHITE}" stroke="{YEL}" stroke-width="4"/>'
    sc += f'<rect x="40" y="240" width="260" height="60" fill="#E2E8F0"/>'
    sc += bust(160, 300, 110, face='#8C7466', cloth='#5B4F86', hair='#8E3D66')
    sc += f'<path d="M106 160 Q160 110 214 160" fill="none" stroke="{WHITE}" stroke-width="4" stroke-opacity=".9"/>'
    hist_case('case-hist-backlit', '逆光外景的直方图', sc,
              [(0.7, 0.2, 0.09), (0.12, 0.5, 0.15), (0.6, 0.9, 0.06)], clipR=0.95,
              notes=[(345, 100, '人物：挤在暗部', YEL1), (610, 84, '天空', WHITE), (540, 140, '右端大片贴墙', RED1)],
              caption='示范读数：两头高、中间空。天空大片死白，脸掉进暗部。')


def case_hist_night():
    sc = f'<rect x="40" y="40" width="260" height="260" fill="#0F172A"/>'
    for x, y in [(70, 80), (120, 110), (250, 70), (280, 120)]:
        sc += f'<circle cx="{x}" cy="{y}" r="6" fill="#FDE68A"/><circle cx="{x}" cy="{y}" r="14" fill="#FDE68A" fill-opacity=".25"/>'
    sc += bust(170, 300, 110, face='#E9C8B4', cloth='#312E81', hair='#7C3AED')
    hist_case('case-hist-night', '夜景人像的直方图', sc,
              [(1.0, 0.04, 0.07), (0.35, 0.55, 0.07), (0.12, 0.85, 0.04)], clipL=0.9, clipR=0.15,
              notes=[(345, 84, '夜空：贴左墙', RED1), (500, 130, '脸：中间调', YEL1), (590, 176, '路灯', WHITE)],
              caption='示范读数：像素大量堆在左边，这是夜景本来的样子；要看的是脸落在哪。')


# ---------- 0.1 案例：画布大小和像素数 ----------
def case_canvas_size():
    Wd, Hd = 760, 340
    s = [f'<rect x="20" y="10" width="720" height="320" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    s.append(text(44, 46, '同一张照片，三种长边尺寸：面积按像素数等比例画', 16, 800))
    k = 0.04
    items = [(6000, 4000, VIO1, '相机原图'), (4500, 3000, MINT1, '缩到长边 4500'), (3000, 2000, YEL1, '缩到长边 3000')]
    x = 44
    for w, h, col, name in items:
        rw, rh = w * k, h * k
        s.append(f'<rect x="{x}" y="{70}" width="{rw:.0f}" height="{rh:.0f}" fill="{col}" stroke="{INK}" stroke-width="2.5"/>')
        mp = w * h / 1e6
        s.append(text(x + 8, 70 + 24, f'{w} × {h}', 14, 800))
        s.append(text(x + 8, 70 + 46, f'= {mp:.1f} 百万像素', 13, 700, MUTED))
        s.append(text(x, 70 + rh + 24, name, 14, 800))
        s.append(text(x, 70 + rh + 46, f'是原图的 {w * h / 24e6 * 100:.0f}%', 13, 700, MUTED))
        x += rw + 26
    s.append(text(44, 312, '每个图层都要存一整张画布大小的图。像素越少，每层占的内存越少，能开的层数越多；具体多少以画布信息为准。', 13, 600, MUTED))
    save('case-canvas-size', svg(Wd, Hd, ''.join(s), '画布像素数对比：6000×4000、4500×3000、3000×2000'))


# ---------- 0.3 案例：返工前后 ----------
def face(name, slim, mole, pale, title):
    Wd, Hd = 400, 400
    s = [f'<rect x="0" y="0" width="{Wd}" height="{Hd}" fill="#E0E7FF"/>']
    cx = 200
    skin = '#FBEFEA' if pale else SKIN
    jaw = 70 if slim else 92
    s.append(f'<path d="M{cx - 150} 400 Q{cx} 300 {cx + 150} 400 Z" fill="{VIO}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<rect x="{cx - 26}" y="250" width="52" height="70" fill="{skin}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M{cx - 98} 160 Q{cx - 100} 240 {cx - jaw * 0.55} 268 Q{cx} 312 {cx + jaw * 0.55} 268 Q{cx + 100} 240 {cx + 98} 160 Q{cx + 90} 60 {cx} 60 Q{cx - 90} 60 {cx - 98} 160 Z" fill="{skin}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M{cx - 118} 200 Q{cx - 130} 40 {cx} 38 Q{cx + 130} 40 {cx + 118} 200 Q{cx + 96} 110 {cx + 20} 100 Q{cx - 50} 96 {cx - 92} 140 Z" fill="{VIO7}" stroke="{INK}" stroke-width="3"/>')
    for dx in (-40, 40):
        s.append(f'<ellipse cx="{cx + dx}" cy="180" rx="16" ry="11" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/><circle cx="{cx + dx}" cy="180" r="7" fill="{VIO7}"/>')
    s.append(f'<path d="M{cx - 18} 250 q18 10 36 0" fill="none" stroke="{RED7}" stroke-width="3" stroke-linecap="round"/>')
    if mole:
        s.append(f'<circle cx="{cx - 34}" cy="204" r="3.5" fill="{INK}"/>')
    else:
        s.append(f'<circle cx="{cx - 34}" cy="204" r="9" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="3 3"/>')
    save(name, svg(Wd, Hd, ''.join(s), title))


def case_rework():
    face('case-rework-v1', slim=True, mole=False, pale=True, title='第一版：下巴收窄、泪痣被去掉、肤色偏白')
    face('case-rework-v2', slim=False, mole=True, pale=False, title='返工后：脸型还原、泪痣保留、肤色自然')


if __name__ == '__main__':
    for f in [u_gallery, u_custom_canvas, u_canvas_info, u_gesture, u_pressure, u_share, p_pixels, p_bits, p_gamut, p_compress, p_hist_zones, p_flow,
              u_pressure_test, u_cursor, u_canvas_size, u_color_profile, u_gallery_select, u_rename, u_stack,
              u_lr_histogram, u_lr_export, u_zoom_check, case_hist_indoor, case_hist_backlit, case_hist_night, case_canvas_size, case_rework]:
        f()
    u_gallery_select('u-batch-export', 'JPEG', '选择模式里勾选一组作品，一起导出 JPEG')
    print('done', len(os.listdir(OUT)))
