"""M8 风格和作品集 的示意图。运行：python tools/diagrams/m8.py"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'diagrams', 'm8')
os.makedirs(OUT, exist_ok=True)


def save(name, s):
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)


def base():
    return f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>'


def dark_frame(inner):
    return f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#1F2329"/>' + inner


# ---------------- 一张"照片" ----------------
TONES = {
    # 4x5 颜色矩阵（每行 R G B A 偏移）
    'flat': '0.86 0.06 0.04 0 0.06  0.05 0.85 0.05 0 0.06  0.04 0.05 0.80 0 0.05  0 0 0 1 0',
    'cold': '0.40 0.05 0.02 0 0.04  0.04 0.56 0.06 0 0.07  0.03 0.10 0.66 0 0.11  0 0 0 1 0',
    'coldfig': '0.88 0.05 0.00 0 0.00  0.03 0.80 0.05 0 0.01  0.02 0.08 0.80 0 0.04  0 0 0 1 0',
    'warm': '1.02 0.08 0.00 0 0.04  0.02 0.94 0.02 0 0.02  0.00 0.04 0.74 0 0.00  0 0 0 1 0',
    'pink': '0.98 0.04 0.06 0 0.05  0.02 0.86 0.06 0 0.02  0.06 0.04 0.96 0 0.06  0 0 0 1 0',
    'none': '1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 1 0',
}


def contrast(m, c):
    """在颜色矩阵上再乘一个对比度"""
    v = [float(t) for t in m.split()]
    for r in range(3):
        for k in range(3):
            v[r * 5 + k] *= c
        v[r * 5 + 4] = v[r * 5 + 4] * c + (1 - c) * 0.5
    return ' '.join(f'{t:.3f}' for t in v)


def pic(x, y, w, h, tone='flat', uid='a', fx=(), con=1.0, vig=0.0, lift=0.0, shade=0.28, hh=None, bg='wall'):
    """半身人像"照片"：墙、窗光、人物，按 tone 调色。fx：rim 边缘光、bokeh 光斑、dust 粒子、flare 光晕"""
    hh = hh or h * 0.21
    cx = x + w * 0.56
    top = y + h * 0.13
    m = contrast(TONES[tone], con)
    d = (f'<defs><clipPath id="c{uid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
         f'<filter id="f{uid}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="{m}"/></filter>'
         f'<filter id="g{uid}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="{contrast(TONES["coldfig"], con) if tone == "cold" else m}"/></filter>'
         f'<radialGradient id="v{uid}" cx="50%" cy="45%" r="70%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="{vig}"/></radialGradient>'
         f'<linearGradient id="s{uid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0.45" stop-color="#1E293B" stop-opacity="0"/><stop offset="1" stop-color="#1E293B" stop-opacity="{shade}"/></linearGradient>'
         f'<linearGradient id="w{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E7ECF3"/><stop offset="1" stop-color="#B8C2D1"/></linearGradient>'
         f'<radialGradient id="b{uid}"><stop offset="0" stop-color="#FFF7D6" stop-opacity=".95"/><stop offset="1" stop-color="#FFF7D6" stop-opacity="0"/></radialGradient></defs>')
    s = [d, f'<g clip-path="url(#c{uid})"><g filter="url(#f{uid})">']
    if bg == 'wall':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#w{uid})"/>')
        # 左上的窗
        wx, wy, ww, wh = x + w * 0.06, y + h * 0.08, w * 0.2, h * 0.42
        s.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{ww:.1f}" height="{wh:.1f}" fill="#F8FAFC" stroke="#94A3B8" stroke-width="3"/>'
                 f'<line x1="{wx + ww / 2:.1f}" y1="{wy:.1f}" x2="{wx + ww / 2:.1f}" y2="{wy + wh:.1f}" stroke="#94A3B8" stroke-width="3"/>'
                 f'<line x1="{wx:.1f}" y1="{wy + wh / 2:.1f}" x2="{wx + ww:.1f}" y2="{wy + wh / 2:.1f}" stroke="#94A3B8" stroke-width="3"/>')
        s.append(f'<path d="M{wx + ww:.1f} {wy:.1f} L{cx - hh * 0.3:.1f} {top + hh * 0.4:.1f} L{cx - hh * 0.2:.1f} {top + hh * 3.2:.1f} L{wx + ww:.1f} {wy + wh:.1f} Z" fill="#FFFFFF" fill-opacity=".28"/>')
    elif bg == 'night':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#334155"/>')
        for i in range(7):
            bx = x + w * (0.08 + 0.13 * i); bh = h * (0.25 + 0.3 * ((i * 37) % 5) / 5)
            s.append(f'<rect x="{bx:.1f}" y="{y + h - bh:.1f}" width="{w * 0.1:.1f}" height="{bh:.1f}" fill="#1E293B"/>')
    s.append('</g>')
    s.append(f'<g filter="url(#g{uid})">' + figure(cx, top, hh, top + hh * 3.6, top + hh * 6.6, sw=2.5) + '</g>')
    s.append(f'<rect x="{cx - hh * 1.3:.1f}" y="{y}" width="{hh * 2.6:.1f}" height="{h}" fill="url(#s{uid})"/>')
    if lift:
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#3B5B7A" fill-opacity="{lift}" style="mix-blend-mode:lighten"/>')
    if 'rim' in fx:
        s.append(f'<path d="M{cx - hh * 0.62:.1f} {top + hh * 0.5:.1f} Q{cx - hh * 0.78:.1f} {top + hh * 1.5:.1f} {cx - hh * 0.55:.1f} {top + hh * 1.95:.1f}" fill="none" stroke="#A5F3FC" stroke-width="4" stroke-opacity=".9"/>'
                 f'<path d="M{cx - hh * 0.8:.1f} {top + hh * 1.4:.1f} Q{cx - hh * 1.0:.1f} {top + hh * 2.2:.1f} {cx - hh * 0.95:.1f} {top + hh * 3.2:.1f}" fill="none" stroke="#A5F3FC" stroke-width="4" stroke-opacity=".8"/>')
    if 'bokeh' in fx:
        random.seed(5)
        for i in range(9):
            bx = x + w * random.uniform(0.02, 0.98); by = y + h * random.uniform(0.05, 0.55); r = random.uniform(10, 24)
            s.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{r:.1f}" fill="url(#b{uid})"/>')
    if 'dust' in fx:
        random.seed(9)
        for i in range(40):
            bx = x + w * random.random(); by = y + h * random.random()
            s.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{random.uniform(1, 2.6):.1f}" fill="#E0F2FE" fill-opacity=".85"/>')
    if 'flare' in fx:
        s.append(f'<circle cx="{x + w * 0.16:.1f}" cy="{y + h * 0.12:.1f}" r="{w * 0.22:.1f}" fill="url(#b{uid})"/>')
    if vig:
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#v{uid})"/>')
    s.append('</g>')
    return ''.join(s), dict(cx=cx, top=top, hh=hh)


def swatch(x, y, color, name, sub='', size=46):
    return (f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="8" fill="{color}" stroke="{INK}" stroke-width="2.5"/>'
            + text(x + size + 10, y + 19, name, 14, 800) + (text(x + size + 10, y + 39, sub, 13, 600, MUTED) if sub else ''))


def pin(x, y, n, color=YEL):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="none" stroke="{WHITE}" stroke-width="4"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="none" stroke="{INK}" stroke-width="2"/>'
            + badge(x + 18, y - 16, n, color))


def card(x, y, w, h, fill=WHITE):
    return f'<rect x="{x + 4}" y="{y + 4}" width="{w}" height="{h}" rx="14" fill="{INK}"/><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'


# ============ 8.1 复刻练习 ============
COLD = dict(tone='cold', con=1.18, vig=0.55, lift=0.10, shade=0.45)


def p_breakdown():
    """拆解一张冷色调电影感作品：取色点、光源方向、后加的特效、图层结构"""
    Wd, Hd = 780, 470
    s = [f'<rect x="10" y="10" width="760" height="450" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    ph, g = pic(30, 50, 330, 390, uid='bd', fx=('rim', 'dust'), **COLD)
    s.append(label(30, 40, '参考作品（示意）', YEL1, 14))
    s.append(ph)
    cx, t, hh = g['cx'], g['top'], g['hh']
    # 取色点：最暗、中性灰（墙）、最亮（窗）、皮肤
    pts = [(60, 420, 1), (300, 120, 2), (92, 110, 3), (cx + hh * 0.05, t + hh * 0.75, 4)]
    for px, py, n in pts:
        s.append(pin(px, py, n))
    # 光源方向
    s.append(arrow(70, 170, 150, 205, YEL, 5))
    s.append(label(40, 250, '光从左上来', YEL1, 13))
    # 右侧笔记
    x0 = 385
    s.append(text(x0, 52, '拆的时候问四个问题', 17, 800))
    rows = [
        ('1', '颜色：暗部、中间、亮部各偏什么色？', '吸管取 ①②③，看色相和饱和度'),
        ('2', '光：从哪来？软还是硬？', '看鼻子、脖子下的影子和眼神光'),
        ('3', '哪些是后加的？', '左边一圈青色边缘光、空中的粒子'),
        ('4', '图层大概怎么叠？', '从下往上写出来，见下图'),
    ]
    for i, (n, a, b) in enumerate(rows):
        yy = 80 + i * 62
        s.append(badge(x0 + 14, yy + 14, n))
        s.append(text(x0 + 36, yy + 19, a, 14, 800))
        s.append(text(x0 + 36, yy + 42, b, 13, 600, MUTED))
    # 图层推测
    stack = [('统一调色：暗部青、亮部暖，加暗角', MINT1), ('特效：边缘光、粒子', VIO1), ('光影：左亮右暗加强', PINK1), ('精修：皮肤、假发', YEL1), ('原片', '#E2E8F0')]
    for i, (nm, fill) in enumerate(stack):
        yy = 336 + i * 24
        s.append(f'<rect x="{x0 + 10}" y="{yy}" width="350" height="21" rx="5" fill="{fill}" stroke="{INK}" stroke-width="1.5"/>' + text(x0 + 20, yy + 15, nm, 12.5, 700))
    s.append(text(x0 + 10, 330, '推测的图层（从下往上做）', 13, 800, VIO7))
    save('p-breakdown', svg(Wd, Hd, ''.join(s), '拆解一张冷色调作品：取色、光源、后加特效、图层推测'))


def p_hsb():
    """用三个取样点的色相/饱和度/亮度读出调色思路"""
    Wd, Hd = 780, 380
    s = [f'<rect x="10" y="10" width="760" height="360" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    s.append(text(34, 48, '本来应该是灰色的地方，取出来是什么颜色，就说明后期往那个方向调了', 15, 800))
    cols = [('① 最暗处', '#1F3340', '色相 200° 左右', '饱和度 30%+', '亮度 12%～20%', '暗部被推向青蓝；最黑的地方不是 0%，说明黑色被提亮了（发灰、胶片感）'),
            ('② 中性的墙', '#7E8F99', '色相 200° 左右', '饱和度 10%～15%', '亮度 55%', '中间调也偏冷，但比暗部淡，说明整体色温调冷了一点'),
            ('③ 最亮处', '#F2E6D6', '色相 30°～40°', '饱和度 8%～15%', '亮度 92%～95%', '亮部反而偏暖，而且没到 100%，说明高光被压了一点')]
    for i, (t, c, a, b, d, e) in enumerate(cols):
        x = 34 + i * 246
        s.append(f'<rect x="{x}" y="70" width="226" height="80" rx="10" fill="{c}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(label(x + 8, 98, t, WHITE, 13))
        s.append(text(x, 176, a, 14, 800) + text(x, 198, b, 14, 800) + text(x, 220, d, 14, 800))
        words = e
        lines = [words[k:k + 16] for k in range(0, len(words), 16)]
        for j, ln in enumerate(lines):
            s.append(text(x, 248 + j * 21, ln, 13, 600, MUTED))
    s.append(f'<rect x="34" y="320" width="712" height="34" rx="10" fill="{MINT1}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(46, 343, '结论：暗部青、亮部暖、黑色提亮、整体偏冷——这就是常见的"冷色电影感"配方', 14, 800, MINT7))
    save('p-hsb', svg(Wd, Hd, ''.join(s), '从取样点的色相、饱和度、亮度读出调色思路'))


def u_ref_window():
    ph, g = pic(CAN[0], CAN[1], CAN[2], CAN[3], tone='flat', uid='rw')
    ref = pic(470, 260, 230, 160, uid='rw2', hh=30, **COLD)[0]
    win = (f'<rect x="462" y="226" width="246" height="238" rx="12" fill="{UIBAR}" stroke="#111827" stroke-width="1.5"/>'
           f'<rect x="560" y="234" width="50" height="6" rx="3" fill="{UIDIM}"/>' + ref)
    btns = ''
    for i, b in enumerate(['画布', '图像', '面容']):
        bx = 474 + i * 76
        btns += f'<rect x="{bx}" y="428" width="68" height="28" rx="8" fill="{UIBLUE if b == "图像" else UIPANEL}"/>' + text(bx + 34, 447, b, 14, 700, UITEXT, 'middle')
    menu = actions_menu('画布', x=60, y=62, w=300, hl='参考', toggles={'动画协助': False, '页面辅助': False, '绘图指引': False, '参考': True})
    s = screen(ph + win + btns + menu, active='actions')
    s += ring(*icon_pos('actions'), 18)
    s += badge(350, 62 + 50 + 5 * 34 + 17, 2)
    s += ringrect(548, 424, 76, 36) + badge(586, 412, 3)
    s += label(462, 210, '参考窗口：点「图像」放进参考作品', YEL1, 13)
    s += note('示意图，按钮位置以实际界面为准')
    save('u-ref-window', svg(W, H, s, '打开参考窗口，切到图像，导入参考作品'))


def u_eyedropper():
    ph, g = pic(CAN[0], CAN[1], CAN[2], CAN[3], uid='ed', **COLD)
    lx, ly = 300, 440
    loupe = (f'<circle cx="{lx}" cy="{ly - 70}" r="34" fill="#1F3340" stroke="{WHITE}" stroke-width="6"/>'
             f'<path d="M{lx - 34} {ly - 70} A34 34 0 0 0 {lx + 34} {ly - 70} Z" fill="{PINK}"/>'
             f'<circle cx="{lx}" cy="{ly - 70}" r="34" fill="none" stroke="{INK}" stroke-width="2"/>'
             f'<circle cx="{lx}" cy="{ly}" r="6" fill="none" stroke="{WHITE}" stroke-width="3"/>')
    # 值 面板
    px, py, pw = 470, 62, 300
    pnl = panel(px, py, pw, 330) + text(px + 16, py + 30, '颜色', 17, 800, UITEXT)
    rows = [('色相', '201°', 0.56), ('饱和度', '34%', 0.34), ('亮度', '18%', 0.18)]
    for i, (k, v, f) in enumerate(rows):
        yy = py + 70 + i * 50
        pnl += text(px + 16, yy, k, 14, 700, UITEXT) + text(px + pw - 16, yy, v, 14, 800, YEL, 'end')
        pnl += f'<rect x="{px + 16}" y="{yy + 10}" width="{pw - 32}" height="10" rx="5" fill="#6B7280"/><circle cx="{px + 16 + (pw - 32) * f:.1f}" cy="{yy + 15}" r="9" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
    pnl += text(px + 16, py + 236, '十六进制', 14, 700, UITEXT) + f'<rect x="{px + 110}" y="{py + 216}" width="120" height="30" rx="7" fill="{UIBAR}"/>' + text(px + 122, py + 237, '#1F3340', 15, 800, WHITE)
    tabs = ['色盘', '经典', '色彩调和', '值', '调色板']
    tx = px + 10
    for t in tabs:
        tw = len(t) * 14 + 14
        pnl += f'<rect x="{tx}" y="{py + 286}" width="{tw}" height="30" rx="8" fill="{UIBLUE if t == "值" else UIBAR}"/>' + text(tx + tw / 2, py + 306, t, 13, 700, UITEXT, 'middle')
        if t == '值':
            vx = tx
        tx += tw + 4
    s = screen(ph + loupe + pnl, active='color')
    s += badge(lx - 50, ly - 104, 1)
    s += ring(*icon_pos('color'), 18) + badge(icon_pos('color')[0] - 2, 74, 2)
    s += ringrect(vx - 4, py + 282, 40, 38) + ringrect(px + 8, py + 46, pw - 16, 150)
    s += badge(px + pw - 20, py + 46, 3)
    s += label(36, 520, '① 在画面上长按，拖到要取色的地方再松手', YEL1, 13)
    s += label(470, 420, '② 点颜色 → ③「值」里读三个数，抄下来', YEL1, 13)
    s += note('示意图')
    save('u-eyedropper', svg(W, H, s, '长按取色，再到颜色面板的值里读出色相、饱和度、亮度'))


def u_gray():
    ph, g = pic(CAN[0], CAN[1], CAN[2], CAN[3], uid='gr', tone='none', con=1.0, shade=0.45)
    gray = f'<g style="filter:grayscale(1)">{pic(CAN[0], CAN[1], CAN[2], CAN[3], uid="gr2", tone="none", shade=0.45)[0]}</g>'
    lay = layers_panel([('灰度检查', None, '', True), ('参考作品', 'scene', 'N', False)], x=470, y=62, w=300)
    # 混合模式弹出层
    lay += f'<rect x="486" y="112" width="44" height="34" rx="4" fill="#111"/>'
    bx, by = 470, 222
    pop = panel(bx, by, 300, 120) + text(bx + 16, by + 30, '颜色', 16, 800, UITEXT) + text(bx + 284, by + 30, '▾', 16, 800, UITEXT, 'end')
    pop += slider(bx + 16, by + 80, 268, '不透明度', 1.0)
    s = screen(gray + lay + pop, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += ringrect(bx + 8, by + 8, 284, 34) + badge(bx + 300, by + 24, 2)
    s += badge(470 + 300 - 44, 62 + 44 + 23, 1)
    s += label(470, 376, '① 新建一层，填充黑色', YEL1, 13)
    s += label(470, 408, '② 点它右边的字母，模式选「颜色」', YEL1, 13)
    s += label(470, 440, '画面变黑白，光从哪来一眼就看出来', WHITE, 13)
    s += note('示意图')
    save('u-gray', svg(W, H, s, '在最上面加一层黑色、混合模式设为颜色，看明暗'))


def u_board():
    """拆解板：一张横幅画布，左边放参考，右边放色卡和笔记"""
    x, y, w, h = 120, 90, 560, 380
    cnt = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{WHITE}" stroke="#94A3B8"/>'
    cnt += pic(x + 12, y + 12, 220, h - 24, uid='bo', hh=48, **COLD)[0]
    sw = [('#1F3340', '暗部'), ('#7E8F99', '中间'), ('#F2E6D6', '亮部'), ('#E9B9A0', '皮肤')]
    for i, (c, n) in enumerate(sw):
        cnt += f'<rect x="{x + 250}" y="{y + 20 + i * 52}" width="40" height="40" rx="6" fill="{c}" stroke="{INK}" stroke-width="2"/>' + text(x + 300, y + 46 + i * 52, n, 14, 700)
        cnt += f'<rect x="{x + 350}" y="{y + 34 + i * 52}" width="{150 - i * 20}" height="8" rx="4" fill="#CBD5E1"/>'
    for i in range(5):
        cnt += f'<rect x="{x + 250}" y="{y + 240 + i * 24}" width="{290 - (i % 3) * 40}" height="8" rx="4" fill="#CBD5E1"/>'
    cnt += f'<rect x="{x + 244}" y="{y + 228}" width="300" height="138" fill="none" stroke="{UIBLUE}" stroke-width="2" stroke-dasharray="6 5"/>'
    menu = actions_menu('添加', rows=['插入文件', '插入照片', '拍照', '添加文本'], hl='插入照片', x=60, y=62, w=260, toggles={})
    s = screen(cnt + menu, active='actions')
    s += ring(*icon_pos('actions'), 18)
    s += ringrect(66, 62 + 50 + 3 * 34 + 3, 248, 28)
    s += badge(330, 62 + 50 + 34 + 17, 1) + badge(330, 62 + 50 + 3 * 34 + 17, 2)
    s += label(x + 244, y + h + 34, '笔记用「添加文本」写，色卡用画笔点上去', YEL1, 13)
    s += note('示意图：操作 › 添加')
    save('u-board', svg(W, H, s, '拆解板：插入参考作品，旁边放色卡，用添加文本写笔记'))


def case_cold(after):
    Wd, Hd = 640, 520
    if after:
        ph, g = pic(20, 20, 600, 480, uid='cca', fx=('rim', 'dust'), **COLD)
        lab = '复刻后：暗部青、亮部暖，加了边缘光和粒子'
    else:
        ph, g = pic(20, 20, 600, 480, uid='ccb', tone='flat', con=0.92, shade=0.18)
        lab = '自己的原片：光线平、颜色发黄发灰'
    s = ph + (label(606, 56, lab, VIO1, 16, 'end') if after else label(34, 56, lab, YEL1, 16))
    save('case-cold-' + ('after' if after else 'before'), svg(Wd, Hd, s, lab))


def case_warm(after):
    Wd, Hd = 640, 520
    if after:
        ph, g = pic(20, 20, 600, 480, uid='cwa', tone='warm', con=1.08, vig=0.35, shade=0.38, fx=('bokeh', 'flare'))
        lab = '复刻后：暖金色，左上光晕，背景光斑'
    else:
        ph, g = pic(20, 20, 600, 480, uid='cwb', tone='flat', con=0.95, shade=0.2)
        lab = '自己的原片：室内窗光，偏灰'
    s = ph + (label(606, 56, lab, VIO1, 16, 'end') if after else label(34, 56, lab, YEL1, 16))
    save('case-warm-' + ('after' if after else 'before'), svg(Wd, Hd, s, lab))


def case_side():
    """原作和复刻并排对比（作业交付格式）"""
    Wd, Hd = 780, 400
    s = [f'<rect x="10" y="10" width="760" height="380" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    s.append(pic(30, 50, 300, 300, uid='sd1', hh=60, **COLD)[0])
    s.append(pic(350, 50, 300, 300, uid='sd2', hh=60, fx=('rim',), tone='cold', con=1.1, vig=0.45, lift=0.06, shade=0.4)[0])
    s.append(label(30, 40, '原作（只做练习参考）', YEL1, 13) + label(350, 40, '我的复刻', VIO1, 13))
    notes = ['暗部色相差 5°', '黑色提得不够', '边缘光偏粗', '粒子没加']
    for i, n in enumerate(notes):
        s.append(text(668, 80 + i * 30, n, 13, 700, MUTED))
    s.append(text(668, 58, '差在哪', 14, 800, RED7))
    s.append(text(30, 376, '交作业时左右并排，右边写上还差在哪里——这比"差不多"有用得多', 13, 600, MUTED))
    save('case-side', svg(Wd, Hd, ''.join(s), '原作和复刻并排对比，旁边写差异'))


# ============ 8.2 个人风格和预设 ============
def p_style():
    Wd, Hd = 780, 400
    s = [f'<rect x="10" y="10" width="760" height="380" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    s.append(text(34, 48, '"风格"拆开看，是三层东西', 17, 800))
    tiers = [('每张都一样', '存成预设、模板、笔刷组，一键套用', ['Lightroom 预设：颜色分级、混合、颗粒', 'Procreate 渐变映射、调色板', '模板里的图层组和混合模式'], MINT1, 620),
             ('每张小调', '固定范围，按照片微调', ['曝光度、白平衡（每张光线不同）', '边缘光、光斑的强弱', '暗角大小'], YEL1, 520),
             ('每张都不同', '靠诊断和手艺，不能预设', ['修瑕、比例、液化', '去路人、补背景'], PINK1, 420)]
    y = 70
    for name, sub, items, fill, w in tiers:
        x = 34 + (620 - w) / 2
        s.append(f'<rect x="{x:.1f}" y="{y}" width="{w}" height="92" rx="14" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(text(x + 18, y + 30, name, 16, 800) + text(x + 18, y + 54, sub, 13, 600, MUTED))
        for j, it in enumerate(items):
            s.append(text(x + w - 16, y + 26 + j * 22, it, 13, 700, INK, 'end'))
        y += 102
    s.append(arrow(690, 90, 690, 340, INK, 3))
    s.append(text(706, 200, '越往下', 13, 700, MUTED) + text(706, 220, '越靠手艺', 13, 700, MUTED))
    save('p-style', svg(Wd, Hd, ''.join(s), '风格的三层：每张都一样、每张小调、每张都不同'))


LRBG = '#1C1C1E'; LRPANEL = '#2C2C2E'; LRTEXT = '#F2F2F7'


def lr_frame(inner, tool=None):
    """Lightroom 手机版（iPad 横屏）示意：左边照片，右边竖排工具，工具左边是面板"""
    s = [f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="{LRBG}"/>']
    s.append(text(40, 46, '‹', 26, 800, LRTEXT) + text(SX + SW - 30, 46, '⋯', 22, 800, LRTEXT, 'end') + text(SX + SW - 70, 46, '↑', 18, 800, LRTEXT, 'end'))
    s.append(pic(40, 70, 380, 450, uid='lr' + (tool or 'x'), tone='flat', hh=80)[0])
    tools = ['预设', '编辑', '蒙版', '修复']
    for i, t in enumerate(tools):
        yy = 90 + i * 64
        on = (t == tool)
        s.append(f'<rect x="{SX + SW - 70}" y="{yy}" width="56" height="52" rx="10" fill="{UIBLUE if on else LRPANEL}"/>' + text(SX + SW - 42, yy + 32, t, 13, 700, LRTEXT, 'middle'))
    s.append(inner)
    return ''.join(s)


def lr_panel_box(h=440, title=None):
    x, y, w = 440, 66, 260
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{LRPANEL}"/>'
    if title:
        s += text(x + 16, y + 30, title, 16, 800, LRTEXT)
    return s, x, y, w


def u_lr_create():
    box, x, y, w = lr_panel_box(300, '预设')
    inner = box + text(x + w - 16, y + 30, '⋯', 22, 800, LRTEXT, 'end')
    tabs = ['推荐', '高级', '您的']
    for i, t in enumerate(tabs):
        inner += f'<rect x="{x + 12 + i * 80}" y="{y + 46}" width="74" height="28" rx="8" fill="{"#48484A" if t == "推荐" else LRBG}"/>' + text(x + 49 + i * 80, y + 65, t, 13, 700, LRTEXT, 'middle')
    for i in range(6):
        inner += f'<rect x="{x + 14 + (i % 3) * 80}" y="{y + 90 + (i // 3) * 80}" width="70" height="70" rx="8" fill="#636366"/>'
    # 弹出菜单
    mx, my = x + 40, y + 50
    inner += f'<rect x="{mx}" y="{my}" width="210" height="150" rx="12" fill="#3A3A3C" stroke="#111" stroke-width="1.5"/>'
    for i, r in enumerate(['创建预设', '管理预设', '导入预设']):
        inner += text(mx + 16, my + 34 + i * 44, r, 15, 700, LRTEXT)
        if i:
            inner += f'<line x1="{mx + 10}" y1="{my + 12 + i * 44}" x2="{mx + 200}" y2="{my + 12 + i * 44}" stroke="#555"/>'
    s = lr_frame(inner, '预设')
    s += ringrect(SX + SW - 73, 87, 62, 58) + badge(SX + SW - 76, 84, 1)
    s += ring(x + w - 24, y + 24, 18) + badge(x + w - 50, y + 10, 2)
    s += ringrect(mx + 6, my + 12, 198, 34) + badge(mx + 222, my + 30, 3)
    s += label(440, 400, '② 预设面板右上角的「选项」', YEL1, 13)
    s += label(440, 432, '③ 点「创建预设」', YEL1, 13)
    s += text(SX + SW - 12, SY + SH - 10, 'Lightroom 手机版示意图，菜单项和位置以实际界面为准', 12, 600, UIDIM, 'end')
    save('u-lr-create', svg(W, H, s, 'Lightroom 手机版：预设面板的选项菜单里点创建预设'))


def u_lr_new():
    box, x, y, w = lr_panel_box(456, '新建预设')
    inner = box + text(x + w - 16, y + 30, '✓', 20, 800, UIBLUE, 'end')
    fields = [('预设名称', '冷调电影感-人像'), ('预设组', '我的风格 ▾'), ('选择', '已修改 ▾')]
    for i, (k, v) in enumerate(fields):
        yy = y + 50 + i * 54
        inner += text(x + 16, yy + 14, k, 12, 700, UIDIM) + f'<rect x="{x + 14}" y="{yy + 20}" width="{w - 28}" height="28" rx="7" fill="{LRBG}"/>' + text(x + 24, yy + 39, v, 14, 700, LRTEXT)
    groups = [('亮度', False), ('颜色', True), ('效果', True), ('细节', False), ('光学', False), ('几何', False)]
    for i, (g, on) in enumerate(groups):
        yy = y + 222 + i * 36
        inner += f'<rect x="{x + 16}" y="{yy}" width="20" height="20" rx="4" fill="{UIBLUE if on else "none"}" stroke="{LRTEXT}" stroke-width="1.5"/>'
        if on:
            inner += f'<path d="M{x + 20} {yy + 10} l4 5 l8 -10" fill="none" stroke="{WHITE}" stroke-width="2.5"/>'
        inner += text(x + 46, yy + 16, g, 14, 700, LRTEXT)
    s = lr_frame(inner, '预设')
    s += ringrect(x + 8, y + 66, w - 16, 36) + badge(x - 14, y + 84, 1)
    s += ringrect(x + 8, y + 120, w - 16, 36) + badge(x - 14, y + 138, 2)
    s += ringrect(x + 8, y + 174, w - 16, 36) + badge(x - 14, y + 192, 3)
    s += ringrect(x + 8, y + 216, 110, 34) + badge(x + 132, y + 232, 4)
    s += ring(x + w - 22, y + 24, 16) + badge(x + w - 48, y + 8, 5)
    s += label(56, 500, '④ 「亮度」不勾：每张照片曝光不同，不该存进预设', YEL1, 13)
    s += text(SX + SW - 12, SY + SH - 10, 'Lightroom 手机版示意图，以实际界面为准', 12, 600, UIDIM, 'end')
    save('u-lr-new', svg(W, H, s, '新建预设：名称、预设组、选择已修改，亮度组不勾'))


def u_lr_apply():
    box, x, y, w = lr_panel_box(330, '预设')
    inner = box
    tabs = ['推荐', '高级', '您的']
    for i, t in enumerate(tabs):
        inner += f'<rect x="{x + 12 + i * 80}" y="{y + 46}" width="74" height="28" rx="8" fill="{"#48484A" if t == "您的" else LRBG}"/>' + text(x + 49 + i * 80, y + 65, t, 13, 700, LRTEXT, 'middle')
    inner += text(x + 16, y + 102, '我的风格', 14, 800, LRTEXT)
    names = ['冷调电影感', '冷调-夜景', '暖金逆光']
    for i, n in enumerate(names):
        tx = x + 14 + i * 80
        inner += f'<rect x="{tx}" y="{y + 114}" width="70" height="70" rx="8" fill="{["#3B5B7A", "#2A3F57", "#C99A5B"][i]}" stroke="{UIBLUE if i == 0 else "none"}" stroke-width="3"/>' + text(tx + 35, y + 202, n, 11, 700, LRTEXT, 'middle')
    inner += text(x + 16, y + 250, '数量', 13, 700, LRTEXT) + text(x + w - 16, y + 250, '70', 13, 800, LRTEXT, 'end')
    inner += f'<rect x="{x + 16}" y="{y + 262}" width="{w - 32}" height="6" rx="3" fill="#636366"/><rect x="{x + 16}" y="{y + 262}" width="{(w - 32) * 0.7:.1f}" height="6" rx="3" fill="{UIBLUE}"/><circle cx="{x + 16 + (w - 32) * 0.7:.1f}" cy="{y + 265}" r="9" fill="{WHITE}"/>'
    inner += text(x + w - 16, y + 312, '✓ 完成', 14, 800, UIBLUE, 'end')
    s = lr_frame(inner, '预设')
    s += ringrect(x + 170, y + 42, 82, 36) + badge(x + 262, y + 60, 1)
    s += ringrect(x + 10, y + 110, 78, 78) + badge(x - 12, y + 150, 2)
    s += ringrect(x + 8, y + 230, w - 16, 48) + badge(x - 12, y + 256, 3)
    s += label(440, 430, '③ 再点一次缩略图出「数量」，按照片调强弱', YEL1, 13)
    s += text(SX + SW - 12, SY + SH - 10, 'Lightroom 手机版示意图，以实际界面为准', 12, 600, UIDIM, 'end')
    save('u-lr-apply', svg(W, H, s, '应用预设：您的选项卡里选预设，用数量滑块调强弱'))


def u_palette():
    ph = pic(CAN[0] - 180, CAN[1], CAN[2], CAN[3], uid='pa', **COLD)[0]
    px, py, pw = 430, 62, 340
    pnl = panel(px, py, pw, 420) + text(px + 16, py + 30, '调色板', 17, 800, UITEXT) + text(px + pw - 22, py + 32, '+', 26, 700, UITEXT, 'middle')
    pals = [('冷调电影感', ['#1F3340', '#2F4A5C', '#7E8F99', '#B8C4CC', '#F2E6D6', '#E9B9A0', '#A5F3FC', '#334155']),
            ('角色：雷电将军', ['#4C1D95', '#7C3AED', '#C4B5FD', '#1E1B4B', '#F5D0FE', '#FDE2CF', '#B91C1C', '#FBBF24']),
            ('默认', ['#000', '#fff', '#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6', '#EC4899'])]
    for i, (n, cs) in enumerate(pals):
        yy = py + 60 + i * 74
        pnl += text(px + 16, yy, n, 14, 700, UITEXT)
        if i == 0:
            pnl += f'<circle cx="{px + pw - 54}" cy="{yy - 5}" r="8" fill="{UIBLUE}"/>'
        pnl += text(px + pw - 20, yy, '⋯', 18, 800, UITEXT, 'end')
        for j, c in enumerate(cs):
            pnl += f'<rect x="{px + 16 + j * 38}" y="{yy + 10}" width="32" height="32" rx="5" fill="{c}" stroke="#111" stroke-width="1"/>'
    # + 菜单
    mx, my = px + 120, py + 50
    menu = f'<rect x="{mx}" y="{my}" width="210" height="170" rx="12" fill="#4B5563" stroke="#111" stroke-width="1.5"/>'
    for i, r in enumerate(['新建调色板', '从"相机"新增', '从"文件"新增', '从"相片"新增']):
        menu += text(mx + 16, my + 32 + i * 40, r, 14, 700, UITEXT)
    tabs = ['色盘', '经典', '色彩调和', '值', '调色板']
    tx = px + 10
    for t in tabs:
        tw = len(t) * 14 + 14
        pnl += f'<rect x="{tx}" y="{py + 380}" width="{tw}" height="30" rx="8" fill="{UIBLUE if t == "调色板" else UIBAR}"/>' + text(tx + tw / 2, py + 400, t, 13, 700, UITEXT, 'middle')
        last = (tx, tw)
        tx += tw + 4
    s = screen(ph + pnl + menu, active='color')
    s += ring(*icon_pos('color'), 18)
    s += ringrect(last[0] - 4, py + 376, last[1] + 8, 38) + badge(last[0] + last[1] / 2, py + 366, 1)
    s += ring(px + pw - 22, py + 24, 18) + badge(px + pw - 50, py + 14, 2)
    s += ringrect(mx + 6, my + 140, 198, 30) + badge(mx - 14, my + 154, 3)
    s += label(60, 520, '③ 从「相片」新增：直接从参考作品或设定图取出一组颜色', YEL1, 13)
    s += note('示意图，菜单文字以实际界面为准')
    save('u-palette', svg(W, H, s, '颜色面板的调色板里点加号，新建或从相片新增调色板'))


def u_brushset():
    px, py, pw, ph_ = 120, 62, 560, 440
    pnl = panel(px, py, pw, ph_) + text(px + 16, py + 30, '画笔库', 17, 800, UITEXT) + text(px + pw - 26, py + 32, '+', 26, 700, UITEXT, 'middle')
    sets = ['最近', '我的修图', '素描', '着墨', '气笔修饰', '亮度', '元素']
    for i, n in enumerate(sets):
        yy = py + 52 + i * 52
        on = n == '我的修图'
        pnl += f'<rect x="{px + 10}" y="{yy}" width="190" height="44" rx="8" fill="{UIBLUE if on else UIBAR}"/>' + text(px + 24, yy + 28, n, 15, 700, UITEXT)
    brushes = [('软画笔', '气笔修饰'), ('技术笔', '着墨'), ('闪光', '亮度'), ('浅色画笔', '亮度')]
    for i, (b, src) in enumerate(brushes):
        yy = py + 52 + i * 70
        pnl += f'<rect x="{px + 214}" y="{yy}" width="{pw - 228}" height="60" rx="8" fill="{UIBAR}"/>' + text(px + 230, yy + 26, b, 15, 800, UITEXT) + text(px + 230, yy + 48, '原来在「' + src + '」', 12, 600, UIDIM)
        pnl += f'<path d="M{px + 380} {yy + 34} q40 -22 80 0 t80 0" fill="none" stroke="{UITEXT}" stroke-width="{[10, 3, 6, 8][i]}" stroke-linecap="round" stroke-opacity="{[0.4, 1, 0.8, 0.6][i]}"/>'
    # 正在拖动的画笔
    drag = f'<rect x="{px + 60}" y="{py + 300}" width="200" height="44" rx="8" fill="{UIPANEL}" stroke="{MINT}" stroke-width="2" opacity=".95"/>' + text(px + 76, py + 328, '湿海绵（拖动中）', 14, 700, UITEXT)
    drag += arrow(px + 120, py + 296, px + 110, py + 120, MINT, 3)
    s = base() + topbar('brush') + pnl + drag
    s += ring(*icon_pos('brush'), 18)
    s += ring(px + pw - 26, py + 26, 18) + badge(px + pw - 54, py + 18, 1)
    s += ringrect(px + 6, py + 52 + 52 - 4, 198, 52) + badge(px - 4, py + 52 + 52 + 22, 2)
    s += label(px + 270, py + ph_ - 70, '① 右上「+」→「创建新组合」，起名「我的修图」', YEL1, 13)
    s += label(px + 270, py + ph_ - 38, '② 长按画笔拖到组合名字上松手：拷贝一份进来', YEL1, 13)
    s += note('示意图，以实际界面为准')
    save('u-brushset', svg(W, H, s, '画笔库：新建画笔组合，把常用笔刷拷贝进来'))


def group_row(x, y, w, name, open_=True, sel=False):
    return (f'<rect x="{x + 8}" y="{y}" width="{w - 16}" height="34" rx="8" fill="{UIBLUE if sel else "#4B5563"}"/>'
            + text(x + 22, y + 23, ('▾ ' if open_ else '▸ ') + name, 15, 800, UITEXT)
            + f'<rect x="{x + w - 30}" y="{y + 9}" width="16" height="16" rx="3" fill="{UIBLUE}" stroke="{UITEXT}" stroke-width="1.5"/>')


def layer_row(x, y, w, name, mode='N', indent=18, lock=False, thumb=None):
    s = f'<rect x="{x + 8 + indent}" y="{y}" width="{w - 16 - indent}" height="30" rx="7" fill="{UIBAR}"/>'
    s += f'<rect x="{x + 14 + indent}" y="{y + 4}" width="32" height="22" rx="3" fill="{WHITE if thumb else "#E5E7EB"}"/>'
    if thumb == 'black':
        s += f'<rect x="{x + 14 + indent}" y="{y + 5}" width="32" height="24" rx="3" fill="#111"/>'
    elif thumb == 'photo':
        s += f'<path d="M{x + 30 + indent} {y + 28} q-5 -12 0 -20 q5 8 0 20" fill="{PINK}" stroke="{INK}" stroke-width="1"/>'
    s += text(x + 54 + indent, y + 20, name, 13.5, 700, UITEXT)
    if lock:
        s += f'<rect x="{x + w - 62}" y="{y + 15}" width="11" height="9" rx="2" fill="{UITEXT}"/><path d="M{x + w - 60} {y + 15} v-3 a3.5 3.5 0 0 1 7 0 v3" fill="none" stroke="{UITEXT}" stroke-width="1.6"/>'
    s += text(x + w - 36, y + 20, mode, 11.5, 700, UIDIM, 'end') + f'<rect x="{x + w - 28}" y="{y + 8}" width="14" height="14" rx="3" fill="{UIBLUE}" stroke="{UITEXT}" stroke-width="1.2"/>'
    return s


TEMPLATE = [
    ('group', '调色'), ('layer', '渐变映射', '正常 30%'), ('layer', '暗角', '正片叠底'),
    ('group', '特效'), ('layer', '边缘光', '添加'), ('layer', '光斑', '滤色'),
    ('group', '光影'), ('layer', '提亮', '滤色'), ('layer', '压暗', '正片叠底'),
    ('group', '精修'), ('layer', '修瑕', '正常'),
    ('layer0', '原图', '正常'),
]


def u_template():
    x, y, w = 420, 62, 360
    pnl = panel(x, y, w, 444, '图层') + text(x + w - 26, y + 30, '+', 24, 700, UITEXT, 'middle')
    yy = y + 44
    for it in TEMPLATE:
        if it[0] == 'group':
            pnl += group_row(x, yy, w, it[1]); yy += 36
        elif it[0] == 'layer':
            pnl += layer_row(x, yy, w, it[1], it[2]); yy += 31
        else:
            pnl += layer_row(x, yy, w, it[1], '', indent=0, lock=True, thumb='photo'); yy += 31
    ph = canvas('', 70, 80, 300, 400) + text(220, 280, '空白模板', 16, 700, MUTED, 'middle') + text(220, 304, '（尺寸和常修的照片一样）', 13, 600, MUTED, 'middle')
    s = base() + ph + topbar('layers') + sidebar() + pnl
    s += ring(*icon_pos('layers'), 18)
    s += label(70, 520, '组的名字就是顺序：从下往上做，做完一组折叠一组', YEL1, 13)
    s += note('示意图：右边灰字是混合模式，真机上显示的是缩写字母')
    save('u-template', svg(W, H, s, '模板文件的图层结构：调色、特效、光影、精修四个组，最下面是原图'))


def u_template_dup():
    s = text(SX + 26, 52, 'Procreate', 22, 800, UITEXT)
    for k, xx in {'选择': 520, '导入': 588, '照片': 656, '+': 730}.items():
        s += text(xx, 52, k, 18 if k != '+' else 30, 700, UITEXT, 'middle')
    def th(x, y, nm, kind):
        t = f'<rect x="{x}" y="{y}" width="170" height="220" rx="6" fill="{"#FFF7E6" if kind else WHITE}"/>'
        if kind == 'tpl':
            for i in range(4):
                t += f'<rect x="{x + 20}" y="{y + 30 + i * 40}" width="130" height="28" rx="5" fill="{[MINT1, VIO1, PINK1, YEL1][i]}" stroke="{INK}" stroke-width="1"/>'
        return t + text(x, y + 242, nm, 13, 700, UITEXT)
    s += th(60, 100, '模板_冷调电影感', 'tpl')
    for j, (b, col) in enumerate([('分享', '#4B5563'), ('复制', '#2563EB'), ('删除', '#DC2626')]):
        s += f'<rect x="{240 + j * 62}" y="160" width="58" height="100" rx="8" fill="{col}"/>' + text(240 + j * 62 + 29, 216, b, 15, 800, WHITE, 'middle')
    s += ringrect(299, 157, 64, 106) + badge(331, 146, 1)
    s += th(480, 100, '雷电将军_20261021_01', 'tpl')
    s += ringrect(476, 326, 190, 30) + badge(686, 341, 2)
    s += arrow(436, 210, 472, 210, UITEXT, 3)
    s += label(60, 430, '① 在模板上向左轻滑，点「复制」', YEL1, 14)
    s += label(60, 466, '② 点副本的名字改名，原模板永远不动', YEL1, 14)
    s += label(60, 502, '③ 打开副本：操作 › 添加 › 插入照片', YEL1, 14)
    s += note('示意图')
    save('u-template-dup', svg(W, H, dark_frame(s), '图库里复制模板，改名后再放照片'))


def u_fit():
    ph = pic(CAN[0], CAN[1], CAN[2], CAN[3], uid='fit', tone='flat')[0]
    box = (f'<rect x="{CAN[0]}" y="{CAN[1]}" width="{CAN[2]}" height="{CAN[3]}" fill="none" stroke="{UIBLUE}" stroke-width="2"/>')
    for hx, hy in [(CAN[0], CAN[1]), (CAN[0] + CAN[2], CAN[1]), (CAN[0], CAN[1] + CAN[3]), (CAN[0] + CAN[2], CAN[1] + CAN[3])]:
        box += f'<circle cx="{hx}" cy="{hy}" r="6" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
    s = screen(ph + box + bottom_bar(TF_ROWS, active=('等比',), hl='符合画布'), active='transform')
    s += ring(*icon_pos('transform'), 18)
    s += label(580, 140, '照片插进来以后', YEL1, 13) + label(580, 172, '点「符合画布」铺满', YEL1, 13)
    s += label(580, 220, '画布和照片尺寸一样时', WHITE, 13) + label(580, 252, '刚好铺满、不缩放', WHITE, 13)
    s += note('示意图')
    save('u-fit', svg(W, H, s, '插入照片后，在变换工具栏点符合画布'))


def case_set(after):
    Wd, Hd = 640, 520
    s = [f'<rect x="20" y="20" width="600" height="480" fill="{WHITE}"/>']
    if after:
        tones = [dict(tone='cold', con=1.15, vig=0.5, lift=0.1, shade=0.42)] * 3
        lab = '用同一套预设和模板：三张色调一致'
    else:
        tones = [dict(tone='flat', con=0.95), dict(tone='warm', con=1.1, vig=0.3), dict(tone='cold', con=1.25, vig=0.1)]
        lab = '每张从零开始调：三张三个样'
    for i, t in enumerate(tones):
        s.append(pic(32 + i * 198, 90, 180, 300, uid=f'st{int(after)}{i}', hh=40, **t)[0])
    s.append(label(606, 56, lab, VIO1, 16, 'end') if after else label(34, 56, lab, YEL1, 16))
    s.append(text(320, 440, '同一组返图（示意）', 15, 700, MUTED, 'middle'))
    save('case-set-' + ('after' if after else 'before'), svg(Wd, Hd, ''.join(s), lab))


# ============ 8.3 作品集 ============
def thumb_mini(x, y, w, h, uid, tone='cold', tag=None, tagfill=VIO1, **kw):
    s = pic(x, y, w, h, uid=uid, tone=tone, hh=h * 0.2, **kw)[0]
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
    if tag:
        s += label(x + 6, y + h - 10, tag, tagfill, 11)
    return s


def p_pick():
    Wd, Hd = 780, 470
    s = [f'<rect x="10" y="10" width="760" height="450" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    s.append(text(34, 46, '9 张不是挑"最好看的 9 张"，而是每张负责证明一件事', 16, 800))
    tags = [('封面：最强一张', YEL1), ('精修：皮肤', PINK1), ('比例修正', PINK1), ('换背景合成', VIO1), ('手绘光效', VIO1), ('粒子氛围', VIO1),
            ('按设定校色', MINT1), ('暖调', MINT1), ('夜景/冷调', MINT1)]
    tn = ['cold', 'flat', 'flat', 'cold', 'warm', 'pink', 'pink', 'warm', 'cold']
    for i, (t, f) in enumerate(tags):
        c, r = i % 3, i // 3
        x, y = 34 + c * 122, 66 + r * 128
        s.append(thumb_mini(x, y, 112, 118, f'pk{i}', tn[i], t, f, con=1.1, vig=0.3))
    x0 = 420
    s.append(text(x0, 82, '挑选标准', 16, 800))
    rules = ['① 每张都要有修图前的原片（没有就不放）', '② 覆盖你会的技能：精修、比例、合成、特效、调色', '③ 至少 2 种色调，证明不是只会一个滤镜', '④ 同一个角色最多 2 张', '⑤ 宁可 6 张都好，不要 9 张里有 3 张凑数', '⑥ 发布前确认出镜和摄影都同意']
    for i, r in enumerate(rules):
        s.append(text(x0, 116 + i * 30, r, 13.5, 700))
    s.append(f'<rect x="{x0 - 6}" y="320" width="342" height="120" rx="12" fill="{YEL1}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(x0 + 8, 346, '颜色标签', 14, 800))
    s.append(label(x0 + 8, 380, '精修', PINK1, 12) + label(x0 + 70, 380, '合成/特效', VIO1, 12) + label(x0 + 172, 380, '调色', MINT1, 12))
    s.append(text(x0 + 8, 420, '每种颜色至少出现 2 次，说明技能覆盖到了', 13, 600, MUTED))
    save('p-pick', svg(Wd, Hd, ''.join(s), '作品集选片：每张证明一种能力'))


def p_layouts():
    Wd, Hd = 780, 400
    s = [f'<rect x="10" y="10" width="760" height="380" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    items = [('A 左右并排', '竖图最常用'), ('B 上下排', '横图用'), ('C 局部放大', '展示精修细节'), ('D 拆成两张', '轮播：先成品后原片')]
    for i, (t, sub) in enumerate(items):
        x = 30 + i * 186
        s.append(text(x, 46, t, 15, 800) + text(x, 66, sub, 12.5, 600, MUTED))
        if i == 0:
            s.append(thumb_mini(x, 84, 80, 130, f'la{i}a', 'flat', None, con=0.9) + thumb_mini(x + 86, 84, 80, 130, f'la{i}b', 'cold', None, con=1.15, vig=0.4))
            s.append(label(x + 2, 236, '前', WHITE, 11) + label(x + 88, 236, '后', VIO1, 11))
        elif i == 1:
            s.append(thumb_mini(x, 84, 166, 72, f'la{i}a', 'flat', None, con=0.9) + thumb_mini(x, 160, 166, 72, f'la{i}b', 'cold', None, con=1.15, vig=0.4))
        elif i == 2:
            s.append(thumb_mini(x, 84, 166, 148, f'la{i}b', 'cold', None, con=1.15, vig=0.4))
            s.append(f'<circle cx="{x + 92}" cy="122" r="16" fill="none" stroke="{YEL}" stroke-width="3"/>')
            s.append(f'<rect x="{x + 104}" y="178" width="58" height="50" fill="{SKIN}" stroke="{YEL}" stroke-width="3"/>' + f'<line x1="{x + 104}" y1="132" x2="{x + 120}" y2="178" stroke="{YEL}" stroke-width="2"/>')
        else:
            s.append(thumb_mini(x, 84, 80, 130, f'la{i}b', 'cold', None, con=1.15, vig=0.4) + thumb_mini(x + 86, 84, 80, 130, f'la{i}a', 'flat', None, con=0.9))
            s.append(label(x + 2, 236, '第1张', VIO1, 11) + label(x + 88, 236, '第2张', WHITE, 11))
    tips = ['两边裁成同样大小、同样位置，眼睛才好对比', '标「修图前 / 修图后」，字小、放角上，不挡脸', '原片不要偷偷调暗调灰，观众看得出来', '原片也是别人的肖像：要先问过才能公开']
    for i, t in enumerate(tips):
        s.append(text(40, 290 + i * 24, '· ' + t, 13.5, 700))
    save('p-layouts', svg(Wd, Hd, ''.join(s), '修图前后对比的四种排法'))


def resize_panel(px, py, pw, vals, resample=True, hl=None):
    s = panel(px, py, pw, 250) + text(px + 16, py + 30, '设置', 16, 800, UITEXT)
    rows = [('宽度', vals[0]), ('高度', vals[1]), ('DPI', vals[2])]
    for i, (k, v) in enumerate(rows):
        yy = py + 50 + i * 46
        s += text(px + 16, yy + 22, k, 14, 700, UITEXT) + f'<rect x="{px + 90}" y="{yy}" width="150" height="32" rx="7" fill="{UIBAR}"/>' + text(px + 102, yy + 22, v, 14, 800, WHITE)
    yy = py + 196
    s += text(px + 16, yy + 20, '画布重新取样', 14, 700, UITEXT)
    s += f'<rect x="{px + pw - 58}" y="{yy + 4}" width="40" height="20" rx="10" fill="{UIBLUE if resample else "#6B7280"}"/><circle cx="{px + pw - (28 if resample else 48)}" cy="{yy + 14}" r="8" fill="{WHITE}"/>'
    return s


def u_double():
    """把画布加宽一倍，左边放原片，右边是成品"""
    x, y = 140, 110
    cnt = f'<rect x="{x}" y="{y}" width="360" height="270" fill="{WHITE}" stroke="{UIBLUE}" stroke-width="2"/>'
    cnt += pic(x + 180, y, 180, 270, uid='db', hh=40, **COLD)[0]
    cnt += f'<rect x="{x}" y="{y}" width="180" height="270" fill="#E5E7EB"/>' + text(x + 90, y + 140, '空出来，放原片', 13, 700, MUTED, 'middle')
    for hx in (x, x + 360):
        cnt += f'<circle cx="{hx}" cy="{y + 135}" r="6" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
    pnl = resize_panel(530, 70, 240, ('8000 px', '6000 px', '300'), resample=False)
    s = screen(cnt + pnl, active='actions')
    s += ring(*icon_pos('actions'), 18)
    s += ringrect(536, 116, 228, 40) + badge(520, 136, 1)
    s += ringrect(536, 262, 228, 32) + badge(520, 278, 2)
    s += label(530, 350, '① 宽度改成原来的 2 倍', YEL1, 13)
    s += label(530, 382, '② 「画布重新取样」关着', YEL1, 13)
    s += label(530, 414, '再把裁剪框往左边拉', WHITE, 13)
    s += note('示意图：操作 › 画布 › 裁剪并调整大小 › 设置')
    save('u-double', svg(W, H, s, '裁剪并调整大小：画布加宽一倍，画布重新取样关闭'))


def u_label():
    x, y = 200, 90
    cnt = f'<rect x="{x}" y="{y}" width="400" height="300" fill="{WHITE}" stroke="#94A3B8"/>'
    cnt += pic(x, y, 200, 300, uid='lb1', tone='flat', hh=44)[0] + pic(x + 200, y, 200, 300, uid='lb2', hh=44, **COLD)[0]
    cnt += f'<rect x="{x + 10}" y="{y + 266}" width="86" height="24" rx="4" fill="none" stroke="{UIBLUE}" stroke-width="2"/>' + text(x + 16, y + 284, '修图前', 15, 800, WHITE)
    cnt += text(x + 216, y + 284, '修图后', 15, 800, WHITE)
    menu = actions_menu('添加', rows=['插入文件', '插入照片', '拍照', '添加文本'], hl='添加文本', x=60, y=400 - 270, w=240, toggles={})
    s = screen(cnt + menu, active='actions')
    s += ring(*icon_pos('actions'), 18)
    s += badge(316, 130 + 50 + 3 * 34 + 17, 1) + badge(x + 108, y + 278, 2)
    s += label(x, y + 330, '① 操作 › 添加 › 添加文本   ② 拖到角上，字号小一点', YEL1, 13)
    s += note('示意图')
    save('u-label', svg(W, H, s, '用添加文本在角上标出修图前和修图后'))


def u_resize():
    cnt = pic(CAN[0], CAN[1], CAN[2], CAN[3], uid='rs', **COLD)[0]
    pnl = resize_panel(530, 70, 240, ('2400 px', '3200 px', '300'), resample=True)
    s = screen(cnt + pnl, active='actions')
    s += ring(*icon_pos('actions'), 18)
    s += ringrect(536, 262, 228, 32) + badge(520, 278, 1)
    s += ringrect(536, 116, 228, 86) + badge(520, 160, 2)
    s += label(530, 350, '① 打开「画布重新取样」', YEL1, 13)
    s += label(530, 382, '② 改长边，另一边自动跟着变', YEL1, 13)
    s += label(530, 422, '先复制作品再改，原件保留全尺寸', WHITE, 13)
    s += note('示意图：操作 › 画布 › 裁剪并调整大小 › 设置')
    save('u-resize', svg(W, H, s, '画布重新取样：按平台需要缩小长边'))


def u_export():
    cnt = pic(CAN[0], CAN[1], CAN[2], CAN[3], uid='ex', **COLD)[0]
    menu = actions_menu('分享', rows=['Procreate', 'PSD', 'PDF', 'JPEG', 'PNG', 'TIFF'], hl='JPEG', x=60, y=62, w=260, toggles={})
    s = screen(cnt + menu, active='actions')
    s += ring(*icon_pos('actions'), 18)
    s += badge(340, 62 + 50 + 3 * 34 + 17, 1)
    s += label(580, 140, '发平台：JPEG', YEL1, 13) + label(580, 172, '留底：Procreate', WHITE, 13)
    s += label(580, 220, '导出前先在画布信息里', YEL1, 13) + label(580, 252, '把颜色配置改成 sRGB', YEL1, 13)
    s += note('示意图：操作 › 分享')
    save('u-export', svg(W, H, s, '操作、分享里选 JPEG 导出'))


def p_compress():
    Wd, Hd = 780, 360
    s = [f'<rect x="10" y="10" width="760" height="340" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    steps = [('你上传的图', '长边很大、质量拉满', MINT1), ('平台处理', '①缩到它要的尺寸\n②再压缩一次', YEL1), ('别人看到的图', '已经被处理过两次', PINK1)]
    for i, (t, d, f) in enumerate(steps):
        x = 34 + i * 250
        s.append(card(x, 40, 200, 96, f))
        s.append(text(x + 16, 72, t, 16, 800))
        for j, ln in enumerate(d.split('\n')):
            s.append(text(x + 16, 98 + j * 22, ln, 13.5, 600, MUTED))
        if i < 2:
            s.append(arrow(x + 208, 88, x + 244, 88, INK, 3))
    s.append(text(34, 176, '压缩时最先被吃掉的东西', 15, 800))
    lost = [('细颗粒、噪点', '变成一片糊'), ('大面积渐变（天空、背景光）', '出现一圈圈色带'), ('细发丝、细文字水印', '边上发脏'), ('很饱和的红、紫', '溢色、变脏')]
    for i, (a, b) in enumerate(lost):
        x = 34 + (i % 2) * 370; y = 196 + (i // 2) * 52
        s.append(f'<rect x="{x}" y="{y}" width="350" height="42" rx="10" fill="{RED1}" stroke="{INK}" stroke-width="2"/>' + text(x + 14, y + 27, a + ' → ' + b, 13.5, 700))
    s.append(text(34, 320, '所以：自己先缩到合适尺寸、用 sRGB、少用细颗粒，发之前用"仅自己可见"测一次', 14, 800, VIO7))
    save('p-compress', svg(Wd, Hd, ''.join(s), '平台会缩图再压缩一次，细节最先丢'))


def case_folio(after):
    Wd, Hd = 640, 520
    s = [f'<rect x="20" y="20" width="600" height="480" fill="{WHITE}"/>']
    if after:
        tn = ['cold', 'flat', 'warm', 'pink', 'cold', 'warm', 'pink', 'cold', 'flat']
        fx = [('rim',), (), ('bokeh',), ('dust',), ('rim', 'dust'), ('flare',), (), (), ()]
        lab = '整理后：同一张封面开头，技能、色调都覆盖到'
    else:
        tn = ['cold'] * 4 + ['flat'] * 2 + ['cold'] * 3
        fx = [()] * 9
        lab = '整理前：同一个角色 5 张、色调全一样、没有原片'
    for i in range(9):
        c, r = i % 3, i // 3
        s.append(thumb_mini(110 + c * 142, 80 + r * 140, 132, 132, f'cf{int(after)}{i}', tn[i], None, fx=fx[i], con=1.1, vig=0.3))
        if after:
            s.append(f'<rect x="{110 + c * 142 + 98}" y="{80 + r * 140 + 6}" width="28" height="18" rx="4" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>' + text(110 + c * 142 + 112, 80 + r * 140 + 20, '前后', 10, 800, INK, 'middle'))
    s.append(label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15))
    save('case-folio-' + ('after' if after else 'before'), svg(Wd, Hd, ''.join(s), lab))


# ============ 8.4 接单交付 ============
def p_quote():
    Wd, Hd = 780, 420
    s = [f'<rect x="10" y="10" width="760" height="400" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    s.append(text(34, 48, '一张图的报价，是这几块加起来的', 17, 800))
    blocks = [('基础', '你修这类图要多少小时 × 你的时薪', MINT1, 260), ('难度', '合成、手绘特效、复杂比例另算时间', VIO1, 150),
              ('沟通和返修', '来回确认、按约定改的那几次', YEL1, 110), ('附加', '加急、商用、交分层文件', PINK1, 90)]
    x = 34
    for name, d, f, w in blocks:
        s.append(f'<rect x="{x}" y="70" width="{w}" height="60" fill="{f}" stroke="{INK}" stroke-width="2.5"/>' + text(x + 10, 106, name, 15, 800))
        x += w
    s.append(text(x + 14, 106, '= 单张价', 16, 800, VIO7))
    for i, (name, d, f, w) in enumerate(blocks):
        y = 170 + i * 40
        s.append(f'<rect x="34" y="{y}" width="22" height="22" rx="4" fill="{f}" stroke="{INK}" stroke-width="2"/>' + text(66, y + 17, name + '：' + d, 14, 700))
    s.append(f'<rect x="34" y="338" width="712" height="56" rx="12" fill="{YEL1}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(48, 362, '时间怎么来：用你自己的作业，在「画布信息 › 统计」里看跟踪时间，按同类型取平均', 14, 800))
    s.append(text(48, 384, '时薪怎么来：参考你所在城市同类兼职的收入水平，再看同水平后期的公开价目', 13, 600, MUTED))
    save('p-quote', svg(Wd, Hd, ''.join(s), '报价的组成：基础工时、难度、沟通返修、附加项'))


def u_stats():
    s = base() + topbar('actions')
    px, py, pw, ph_ = 170, 70, 460, 400
    s += panel(px, py, pw, ph_) + text(px + pw / 2, py + 30, '画布信息', 18, 800, UITEXT, 'middle')
    cats = ['关于本作品', '尺寸', '图层', '颜色配置文件', '视频设置', '统计']
    for i, t in enumerate(cats):
        y = py + 56 + i * 42
        s += f'<rect x="{px + 12}" y="{y}" width="140" height="34" rx="8" fill="{UIBLUE if t == "统计" else UIBAR}"/>' + text(px + 24, y + 23, t, 14, 700, UITEXT)
    rows = [('总笔划数', '3,412'), ('跟踪时间', '2 小时 40 分'), ('文件总大小', '186 MB')]
    for i, (k, v) in enumerate(rows):
        y = py + 60 + i * 46
        s += text(px + 172, y + 22, k, 15, 700, UITEXT) + text(px + pw - 20, y + 22, v, 15, 800, YEL if i == 1 else UITEXT, 'end')
    s += ringrect(px + 6, py + 56 + 5 * 42 - 4, 152, 42) + badge(px - 6, py + 56 + 5 * 42 + 17, 1)
    s += ringrect(px + 162, py + 102, pw - 174, 36) + badge(px + pw + 8, py + 120, 2)
    s += ring(*icon_pos('actions'), 18)
    s += label(px + 172, py + 250, '跟踪时间：这件作品打开着的总时长', YEL1, 13)
    s += label(px + 172, py + 282, '中途放着不动也会算进去，只当参考', WHITE, 13)
    s += note('示意图：操作 › 画布 › 画布信息 › 统计；数字是示例')
    save('u-stats', svg(W, H, s, '画布信息的统计里看跟踪时间'))


def p_scale():
    Wd, Hd = 780, 380
    s = [f'<rect x="10" y="10" width="760" height="360" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    s.append(text(34, 46, '尺度样张：同一张图修三档，让对方指着选', 16, 800))
    lv = [('轻', '去痘、去杂毛、校色', dict(tone='flat', con=1.0)), ('中', '再加：光影、轻微拉腿、统一调色', dict(tone='cold', con=1.08, vig=0.3)), ('重', '再加：换背景/特效、明显改比例', dict(tone='cold', con=1.18, vig=0.5, lift=0.1, fx=('rim', 'dust')))]
    for i, (n, d, kw) in enumerate(lv):
        x = 34 + i * 246
        s.append(pic(x, 64, 226, 220, uid=f'sc{i}', hh=46, **kw)[0])
        s.append(f'<rect x="{x}" y="64" width="226" height="220" fill="none" stroke="{INK}" stroke-width="2"/>')
        s.append(label(x + 8, 92, n, [WHITE, YEL1, VIO1][i], 15))
        s.append(text(x, 310, d, 13.5, 700))
    s.append(text(34, 348, '每档写清楚"做了什么、没做什么"，对方选完就把这一档写进约定', 13.5, 600, MUTED))
    save('p-scale', svg(Wd, Hd, ''.join(s), '修图尺度三档样张：轻、中、重'))


def u_review():
    ph, g = pic(CAN[0], CAN[1], CAN[2], CAN[3], uid='rv', **COLD)
    cx, t, hh = g['cx'], g['top'], g['hh']
    mk = (f'<circle cx="{cx - hh * 0.05:.1f}" cy="{t + hh * 0.6:.1f}" r="30" fill="none" stroke="{RED}" stroke-width="4"/>'
          + text(cx + hh * 0.5, t + hh * 0.3, '1', 22, 900, RED)
          + f'<circle cx="{cx - hh * 1.0:.1f}" cy="{t + hh * 2.6:.1f}" r="26" fill="none" stroke="{RED}" stroke-width="4"/>' + text(cx - hh * 1.6, t + hh * 2.4, '2', 22, 900, RED))
    lay = layers_panel([('返修标注', None, 'N', True), ('成品 v1', 'scene', 'N', False)], x=470, y=62, w=300)
    s = screen(ph + mk + lay, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += label(470, 230, '对方在新图层上用红笔圈，写编号', YEL1, 13)
    s += label(470, 262, '旁边一条一条写：1. 脸再亮一点', WHITE, 13)
    s += label(470, 294, '2. 手臂边缘有残影', WHITE, 13)
    s += label(470, 342, '你改完把这一层关掉，导出 v2', YEL1, 13)
    s += note('示意图')
    save('u-review', svg(W, H, s, '返修标注：在单独图层上圈出要改的地方并编号'))


def u_watermark():
    ph = pic(CAN[0], CAN[1], CAN[2], CAN[3], uid='wm', **COLD)[0]
    wm = ''
    for i in range(4):
        wm += f'<text x="{CAN[0] + 20}" y="{CAN[1] + 90 + i * 100}" font-size="22" font-weight="800" fill="{WHITE}" fill-opacity=".45" transform="rotate(-20 {CAN[0] + 150} {CAN[1] + 90 + i * 100})">预览图 @张宇涵 请勿转载</text>'
    lay = layers_panel([('预览水印（文本）', None, 'N', True), ('成品', 'scene', 'N', False)], x=470, y=62, w=300)
    bx, by = 470, 222
    pop = panel(bx, by, 300, 110) + text(bx + 16, by + 30, '正常', 16, 800, UITEXT) + slider(bx + 16, by + 80, 268, '不透明度', 0.45, hl=True)
    s = screen(ph + wm + lay + pop, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += badge(470 + 300 - 44, 62 + 44 + 23, 1) + badge(bx + 300, by + 80, 2)
    s += label(470, 370, '① 点文本图层右边的 N', YEL1, 13)
    s += label(470, 402, '② 不透明度拉到 40%～50%', YEL1, 13)
    s += label(470, 446, '只给预览图加；终稿不加或按约定', WHITE, 13)
    s += note('示意图')
    save('u-watermark', svg(W, H, s, '预览图水印：添加文本后调低图层不透明度'))


def p_timeline():
    Wd, Hd = 780, 300
    s = [f'<rect x="10" y="10" width="760" height="280" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    s.append(text(34, 46, '交付时间要按节点约，不要只说"两周"', 16, 800))
    nodes = [('确认约定', '尺度、张数、价格', MINT1), ('收定金', '按约定比例', MINT1), ('样片 1 张', '先定方向', YEL1), ('批量修', '按样片的方向', VIO1), ('返修', '按约定次数', PINK1), ('终稿交付', '收尾款后', MINT1)]
    y = 130
    s.append(f'<line x1="92" y1="{y}" x2="692" y2="{y}" stroke="{INK}" stroke-width="4"/>')
    for i, (t, d, f) in enumerate(nodes):
        x = 92 + i * 120
        s.append(f'<circle cx="{x}" cy="{y}" r="16" fill="{f}" stroke="{INK}" stroke-width="3"/>' + text(x, y + 6, str(i + 1), 14, 900, INK, 'middle'))
        s.append(text(x, y - 32, t, 14, 800, INK, 'middle') + text(x, y + 44, d, 12.5, 600, MUTED, 'middle'))
    s.append(f'<rect x="300" y="200" width="300" height="34" rx="10" fill="{YEL1}" stroke="{INK}" stroke-width="2"/>' + text(450, 223, '样片确认前不开始批量修', 14, 800, INK, 'middle'))
    s.append(text(34, 268, '每个节点写上日期；对方哪一步晚了，后面的日期一起往后顺延', 13.5, 600, MUTED))
    save('p-timeline', svg(Wd, Hd, ''.join(s), '交付节点：确认、定金、样片、批量、返修、终稿'))


def case_revise(after):
    Wd, Hd = 640, 520
    if after:
        ph, g = pic(20, 20, 600, 480, uid='cra', fx=('rim',), tone='cold', con=1.12, vig=0.45, lift=0.06, shade=0.3)
        lab = 'v2：脸提亮，手臂残影修掉（按标注改）'
    else:
        ph, g = pic(20, 20, 600, 480, uid='crb', fx=('rim',), tone='cold', con=1.2, vig=0.6, lift=0.1, shade=0.5)
        cx, t, hh = g['cx'], g['top'], g['hh']
        ph += f'<ellipse cx="{cx:.1f}" cy="{t + hh * 0.6:.1f}" rx="{hh * 0.42:.1f}" ry="{hh * 0.5:.1f}" fill="#0F172A" fill-opacity=".35"/>'
        ph += f'<path d="M{cx - hh * 1.05:.1f} {t + hh * 2.0:.1f} q-12 30 -4 70" fill="none" stroke="{SKIN}" stroke-width="10" stroke-opacity=".6"/>'
        lab = 'v1：对方觉得脸太暗，手臂边上有残影'
    s = ph + (label(606, 56, lab, VIO1, 16, 'end') if after else label(34, 56, lab, YEL1, 16))
    save('case-revise-' + ('after' if after else 'before'), svg(Wd, Hd, s, lab))


if __name__ == '__main__':
    fs = [p_breakdown, p_hsb, u_ref_window, u_eyedropper, u_gray, u_board, case_side,
          p_style, u_lr_create, u_lr_new, u_lr_apply, u_palette, u_brushset, u_template, u_template_dup, u_fit,
          p_pick, p_layouts, u_double, u_label, u_resize, u_export, p_compress,
          p_quote, u_stats, p_scale, u_review, u_watermark, p_timeline]
    for f in fs:
        f()
    for a in (False, True):
        case_cold(a); case_warm(a); case_set(a); case_folio(a); case_revise(a)
    print('done', len(os.listdir(OUT)))
