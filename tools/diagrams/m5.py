"""M5 cos 专项（5.1 5.2 5.3 5.5 5.6）的示意图。5.4 的图在 m5_04.py。运行：python tools/diagrams/m5.py"""
import colorsys, math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'diagrams', 'm5')
os.makedirs(OUT, exist_ok=True)
MADE = []


def save(name, s):
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)
    MADE.append(name)


_uid = [0]


def uid(p='c'):
    _uid[0] += 1
    return f'{p}{_uid[0]}'


def clipped(shape_d, inner, kind='path'):
    i = uid('clip')
    sh = f'<path d="{shape_d}"/>' if kind == 'path' else shape_d
    return f'<defs><clipPath id="{i}">{sh}</clipPath></defs><g clip-path="url(#{i})">{inner}</g>'


def rect_clip(x, y, w, h, inner):
    return clipped(f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>', inner, 'raw')


def hexmix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02X}' for x, y in zip(a, b))


def rgb(h):
    return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]


def tohex(c):
    return '#' + ''.join(f'{max(0, min(255, round(v * 255))):02X}' for v in c)


def lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def blend_color(base, top):
    """「颜色」模式的近似：保留底色明度，用上层的色相和饱和度"""
    b, t = rgb(base), rgb(top)
    d = lum(b) - lum(t)
    c = [v + d for v in t]
    L = lum(c); n, x = min(c), max(c)
    if n < 0: c = [L + (v - L) * L / (L - n) for v in c]
    if x > 1: c = [L + (v - L) * (1 - L) / (x - L) for v in c]
    return tohex(c)


def blend_overlay(base, top):
    b, t = rgb(base), rgb(top)
    return tohex([2 * x * y if x < .5 else 1 - 2 * (1 - x) * (1 - y) for x, y in zip(b, t)])


def blend_softlight(base, top):
    b, t = rgb(base), rgb(top)
    return tohex([(1 - 2 * y) * x * x + 2 * y * x for x, y in zip(b, t)])


# ---------------- 通用界面组件 ----------------
def ui_note(s='示意图，按钮位置以实际界面为准'):
    return note(s)


def disc(x, y, locked=False):
    c = YEL if locked else WHITE
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="none" stroke="{c}" stroke-width="4"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="16" fill="none" stroke="{INK}" stroke-width="2"/>'
            f'<line x1="{x - 8:.1f}" y1="{y:.1f}" x2="{x + 8:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="2"/>'
            f'<line x1="{x:.1f}" y1="{y - 8:.1f}" x2="{x:.1f}" y2="{y + 8:.1f}" stroke="{INK}" stroke-width="2"/>')


def popup(x, y, w, rows, hl=None, title=None, row_h=34, toggles=()):
    h = (44 if title else 8) + len(rows) * row_h + 6
    s = panel(x, y, w, h, title)
    s += menu_rows(x, y + (40 if title else 4), w, rows, hl, row_h=row_h, toggles=toggles)
    return s


LAYER_OPTS = ['重命名', '选择', '拷贝', '填充图层', '清除', '阿尔法锁定', '蒙版', '剪辑蒙版', '辅助绘图', '反转', '参考', '向下合并', '向下组合']
ADJ_ROWS = ['色相、饱和度、亮度', '颜色平衡', '曲线', '渐变映射', '高斯模糊', '动态模糊', '透视模糊', '杂色', '锐化', '泛光', '故障艺术', '半色调', '色像差', '液化', '克隆']


def layer_options(x, y, hl, rows=None):
    rows = rows or LAYER_OPTS
    return popup(x, y, 170, rows, hl, None, row_h=30)


def adjust_menu(hl, x=70, y=62, rows=None):
    rows = rows or ADJ_ROWS
    return popup(x, y, 230, rows, hl, '调整', row_h=29)


def layers2(rows, x=470, y=62, w=300, title='图层'):
    """rows: dict(name, col, mode, sel, clip, mask, lock, thumb)"""
    row_h = 50
    h = 50 + len(rows) * row_h + 8
    s = [panel(x, y, w, h, title), text(x + w - 26, y + 30, '+', 24, 700, UITEXT, 'middle')]
    POS_L = {}
    for i, r in enumerate(rows):
        yy = y + 44 + i * row_h
        ind = 22 if r.get('clip') or r.get('mask') else 0
        fill = UIBLUE if r.get('sel') else UIBAR
        s.append(f'<rect x="{x + 8 + ind}" y="{yy}" width="{w - 16 - ind}" height="{row_h - 6}" rx="8" fill="{fill}"/>')
        if r.get('clip'):
            s.append(f'<path d="M{x + 18} {yy + 8} L{x + 18} {yy + 30}" stroke="{UITEXT}" stroke-width="2" marker-end="url(#arw)"/>')
        tx = x + 16 + ind
        col = r.get('col', WHITE)
        s.append(f'<rect x="{tx}" y="{yy + 6}" width="40" height="32" rx="4" fill="{col}" stroke="#94A3B8"/>')
        if r.get('thumb') == 'photo':
            s.append(f'<path d="M{tx + 20} {yy + 36} q-6 -14 0 -24 q6 10 0 24" fill="{PINK}" stroke="{INK}" stroke-width="1"/>')
        if r.get('mask'):
            s.append(f'<rect x="{tx}" y="{yy + 6}" width="40" height="32" rx="4" fill="{WHITE}"/><path d="M{tx} {yy + 38} L{tx + 40} {yy + 6} L{tx + 40} {yy + 38} Z" fill="{INK}"/>')
        s.append(text(tx + 50, yy + 28, r['name'], 14, 700, UITEXT))
        m = r.get('mode', 'N')
        mw = 14 if len(m) <= 2 and m.isascii() else len(m) * 13 + 10
        s.append(f'<rect x="{x + w - 42 - mw}" y="{yy + 13}" width="{mw + 8}" height="20" rx="6" fill="#00000033"/>')
        s.append(text(x + w - 38 - mw / 2, yy + 28, m, 13, 800, YEL if not m.isascii() else UITEXT, 'middle'))
        if r.get('lock'):
            lx = x + w - 66 - mw
            s.append(f'<rect x="{lx}" y="{yy + 20}" width="12" height="10" rx="2" fill="{UITEXT}"/><path d="M{lx + 2} {yy + 20} v-4 a4 4 0 0 1 8 0 v4" fill="none" stroke="{UITEXT}" stroke-width="2"/>')
        s.append(f'<rect x="{x + w - 28}" y="{yy + 14}" width="16" height="16" rx="3" fill="{UIBLUE}" stroke="{UITEXT}" stroke-width="1.5"/>')
        POS_L[i] = (x + 8 + ind, yy, w - 16 - ind, row_h - 6)
    return ''.join(s), POS_L


def blend_popup(x, y, modes, sel, opacity=1.0, w=210):
    s = panel(x, y, w, 64 + len(modes) * 30)
    s += text(x + 14, y + 26, '不透明度', 13, 700, UITEXT)
    s += f'<rect x="{x + 80}" y="{y + 16}" width="{w - 96}" height="8" rx="4" fill="#6B7280"/><rect x="{x + 80}" y="{y + 16}" width="{(w - 96) * opacity:.1f}" height="8" rx="4" fill="{UIBLUE}"/>'
    s += f'<circle cx="{x + 80 + (w - 96) * opacity:.1f}" cy="{y + 20}" r="8" fill="{WHITE}" stroke="{INK}"/>'
    s += text(x + w - 14, y + 46, f'{int(opacity * 100)}%', 12, 700, UIDIM, 'end')
    for i, m in enumerate(modes):
        yy = y + 54 + i * 30
        on = m == sel
        s += f'<rect x="{x + 8}" y="{yy}" width="{w - 16}" height="26" rx="6" fill="{UIBLUE if on else UIBAR}"/>' + text(x + 20, yy + 18, m, 14, 700, UITEXT)
        if on:
            s += ringrect(x + 4, yy - 3, w - 8, 32)
    return s


def brush_lib(groups, ghl, brushes, bhl, x=330, y=62, w=440):
    h = 40 + max(len(groups), len(brushes)) * 36 + 10
    s = panel(x, y, w, h) + text(x + 16, y + 28, '画笔库', 16, 800, UITEXT)
    for i, g in enumerate(groups):
        yy = y + 42 + i * 36
        s += f'<rect x="{x + 8}" y="{yy}" width="130" height="30" rx="7" fill="{UIBLUE if g == ghl else UIBAR}"/>' + text(x + 20, yy + 20, g, 14, 700, UITEXT)
        if g == ghl:
            s += ringrect(x + 4, yy - 3, 138, 36)
    for i, b in enumerate(brushes):
        yy = y + 42 + i * 36
        on = b == bhl
        s += f'<rect x="{x + 150}" y="{yy}" width="{w - 160}" height="30" rx="7" fill="{UIBLUE if on else UIBAR}"/>' + text(x + 162, yy + 20, b, 14, 700, UITEXT)
        s += f'<path d="M{x + 270} {yy + 16} q30 -10 60 0 t60 0 t40 -2" fill="none" stroke="{UITEXT}" stroke-width="{3 if on else 2}" stroke-linecap="round"/>'
        if on:
            s += ringrect(x + 146, yy - 3, w - 152, 36)
    return s


def eyedropper(x, y, new, cur, r=30):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M{x - r + 6} {y} A{r - 6} {r - 6} 0 0 1 {x + r - 6} {y} Z" fill="{new}"/>'
            f'<path d="M{x - r + 6} {y} A{r - 6} {r - 6} 0 0 0 {x + r - 6} {y} Z" fill="{cur}"/>'
            f'<circle cx="{x}" cy="{y}" r="{r - 6}" fill="none" stroke="{WHITE}" stroke-width="3"/>'
            f'<circle cx="{x}" cy="{y}" r="3" fill="none" stroke="{INK}" stroke-width="1.5"/>')


def sel_ants_path(d):
    return (f'<path d="{d}" fill="{UIBLUE}" fill-opacity=".10" stroke="{WHITE}" stroke-width="2.5"/>'
            f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 6"/>')


def ellipse_d(cx, cy, rx, ry, n=36):
    return 'M' + ' L'.join(f'{cx + rx * math.cos(2 * math.pi * i / n):.1f} {cy + ry * math.sin(2 * math.pi * i / n):.1f}' for i in range(n)) + ' Z'


def bbox(x, y, w, h, handles=True, warp=False):
    s = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{UIBLUE}" stroke-width="2"/>'
    if warp:
        for i in (1, 2):
            s += f'<line x1="{x + w * i / 3:.1f}" y1="{y:.1f}" x2="{x + w * i / 3:.1f}" y2="{y + h:.1f}" stroke="{UIBLUE}" stroke-width="1"/>'
            s += f'<line x1="{x:.1f}" y1="{y + h * i / 3:.1f}" x2="{x + w:.1f}" y2="{y + h * i / 3:.1f}" stroke="{UIBLUE}" stroke-width="1"/>'
    if handles:
        for hx, hy in [(x, y), (x + w / 2, y), (x + w, y), (x, y + h / 2), (x + w, y + h / 2), (x, y + h), (x + w / 2, y + h), (x + w, y + h)]:
            s += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="6" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
    return s


def topinfo(s_):
    """画布上方的蓝色提示条（如「克隆锁定状态」「滑动调整」）"""
    w = len(s_) * 14 + 30
    return f'<rect x="{400 - w / 2}" y="62" width="{w}" height="28" rx="14" fill="{UIBLUE}"/>' + text(400, 81, s_, 14, 700, WHITE, 'middle')


def stroke_dots(pts, col=VIO7):
    return ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{col}"/>' for x, y in pts)


def caption_box(x, y, w, h, title, fill=WHITE):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'


# ---------------- 头发 ----------------
SILVER = '#E2E8F0'; SILVER_D = '#94A3B8'; SILVER_L = '#F8FAFC'
WIGPINK = '#F9A8D4'; WIGPINK_D = '#DB2777'
REALHAIR = '#3F3F46'


def clump(rx, ry, tx, ty, w, bend=0.0, fill=SILVER, sw=2, stroke=INK):
    dx, dy = tx - rx, ty - ry
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    mx, my = (rx + tx) / 2 + nx * bend * L, (ry + ty) / 2 + ny * bend * L
    a = (rx + nx * w / 2, ry + ny * w / 2); b = (rx - nx * w / 2, ry - ny * w / 2)
    c1 = (mx + nx * w * 0.32, my + ny * w * 0.32); c2 = (mx - nx * w * 0.32, my - ny * w * 0.32)
    d = f'M{a[0]:.1f} {a[1]:.1f} Q{c1[0]:.1f} {c1[1]:.1f} {tx:.1f} {ty:.1f} Q{c2[0]:.1f} {c2[1]:.1f} {b[0]:.1f} {b[1]:.1f} Z'
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def strand(x1, y1, x2, y2, bend=0.1, col=INK, w=1.3, op=1.0):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    mx, my = (x1 + x2) / 2 - dy / L * bend * L, (y1 + y2) / 2 + dx / L * bend * L
    return f'<path d="M{x1:.1f} {y1:.1f} Q{mx:.1f} {my:.1f} {x2:.1f} {y2:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-opacity="{op}"/>'


def taper(x1, y1, x2, y2, bend=0.1, col=INK, w=3.0):
    """起笔粗、收笔尖的一笔（用细长三角形 + 二次曲线）"""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    mx, my = (x1 + x2) / 2 + nx * bend * L, (y1 + y2) / 2 + ny * bend * L
    return (f'<path d="M{x1 + nx * w / 2:.1f} {y1 + ny * w / 2:.1f} Q{mx + nx * w * 0.3:.1f} {my + ny * w * 0.3:.1f} {x2:.1f} {y2:.1f} '
            f'Q{mx - nx * w * 0.3:.1f} {my - ny * w * 0.3:.1f} {x1 - nx * w / 2:.1f} {y1 - ny * w / 2:.1f} Z" fill="{col}"/>')


def head_bangs(cx, cy, s, wig=SILVER, wig_d=SILVER_D, wig_l=SILVER_L, flyaways=False, real_hair=False, fixed=False,
               bg='#FFF7E6', glint=True):
    """齐刘海长发的头部特写。cx,cy：脸中心；s：脸宽的一半左右"""
    o = []
    # 后发
    o.append(f'<path d="M{cx - s * 1.15:.1f} {cy - s * 0.3:.1f} Q{cx - s * 1.35:.1f} {cy + s * 1.2:.1f} {cx - s * 1.1:.1f} {cy + s * 2.2:.1f} '
             f'L{cx + s * 1.1:.1f} {cy + s * 2.2:.1f} Q{cx + s * 1.35:.1f} {cy + s * 1.2:.1f} {cx + s * 1.15:.1f} {cy - s * 0.3:.1f} '
             f'Q{cx:.1f} {cy - s * 2.0:.1f} {cx - s * 1.15:.1f} {cy - s * 0.3:.1f} Z" fill="{wig_d}" stroke="{INK}" stroke-width="2.5"/>')
    # 脖子和脸
    o.append(f'<rect x="{cx - s * 0.32:.1f}" y="{cy + s * 0.8:.1f}" width="{s * 0.64:.1f}" height="{s * 1.4:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
    o.append(f'<ellipse cx="{cx:.1f}" cy="{cy + s * 0.15:.1f}" rx="{s * 0.78:.1f}" ry="{s * 0.98:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
    # 露出来的真发（鬓角下面的深色）
    if real_hair and not fixed:
        for sg in (-1, 1):
            o.append(f'<path d="M{cx + sg * s * 0.74:.1f} {cy - s * 0.2:.1f} Q{cx + sg * s * 0.86:.1f} {cy + s * 0.2:.1f} {cx + sg * s * 0.7:.1f} {cy + s * 0.5:.1f} '
                     f'L{cx + sg * s * 0.6:.1f} {cy + s * 0.42:.1f} Q{cx + sg * s * 0.7:.1f} {cy + s * 0.15:.1f} {cx + sg * s * 0.62:.1f} {cy - s * 0.15:.1f} Z" fill="{REALHAIR}" stroke="{INK}" stroke-width="1.5"/>')
    # 眼睛、嘴
    for sg in (-1, 1):
        o.append(f'<ellipse cx="{cx + sg * s * 0.32:.1f}" cy="{cy + s * 0.2:.1f}" rx="{s * 0.13:.1f}" ry="{s * 0.09:.1f}" fill="{INK}"/>')
        o.append(f'<circle cx="{cx + sg * s * 0.32 - s * 0.04:.1f}" cy="{cy + s * 0.17:.1f}" r="{s * 0.03:.1f}" fill="{WHITE}"/>')
    o.append(f'<path d="M{cx - s * 0.12:.1f} {cy + s * 0.68:.1f} q{s * 0.12:.1f} {s * 0.06:.1f} {s * 0.24:.1f} 0" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    # 两侧鬓发
    for sg in (-1, 1):
        o.append(clump(cx + sg * s * 0.82, cy - s * 0.55, cx + sg * s * 0.86, cy + s * 1.05, s * 0.32, -sg * 0.06, wig))
        o.append(clump(cx + sg * s * 0.98, cy - s * 0.5, cx + sg * s * 1.12, cy + s * 1.55, s * 0.36, -sg * 0.05, wig))
    # 头顶
    o.append(f'<path d="M{cx - s * 1.0:.1f} {cy - s * 0.35:.1f} Q{cx - s * 0.9:.1f} {cy - s * 1.45:.1f} {cx:.1f} {cy - s * 1.5:.1f} '
             f'Q{cx + s * 0.9:.1f} {cy - s * 1.45:.1f} {cx + s * 1.0:.1f} {cy - s * 0.35:.1f} Q{cx + s * 0.75:.1f} {cy - s * 0.9:.1f} {cx:.1f} {cy - s * 1.0:.1f} '
             f'Q{cx - s * 0.75:.1f} {cy - s * 0.9:.1f} {cx - s * 1.0:.1f} {cy - s * 0.35:.1f} Z" fill="{wig}" stroke="{INK}" stroke-width="2.5"/>')
    # 刘海：一组一组的发束，从发旋往下
    tips = [-0.72, -0.5, -0.27, -0.05, 0.18, 0.4, 0.62]
    for i, t in enumerate(tips):
        rx_ = cx + t * s * 0.55
        o.append(clump(rx_, cy - s * 1.35, cx + t * s, cy - s * (0.12 if i % 2 else 0.22), s * 0.36, 0.04 * (1 if t < 0 else -1), wig))
    # 发束之间的暗缝
    for t in tips[:-1]:
        x0 = cx + (t + 0.11) * s
        o.append(strand(x0 * 0.5 + cx * 0.5 + (x0 - cx) * 0.1, cy - s * 1.2, x0, cy - s * 0.3, 0.03, wig_d, 2.2))
    # 高光带：横跨所有发束、在同一高度
    if glint:
        for t in tips:
            x0 = cx + t * s * 0.82
            o.append(taper(x0 - s * 0.02, cy - s * 1.0, x0 + s * 0.02, cy - s * 0.72, 0.0, wig_l, s * 0.1))
    # 杂毛
    if flyaways and not fixed:
        random.seed(3)
        for i in range(9):
            a = math.radians(200 + i * 16)
            bx, by = cx + math.cos(a) * s * 1.05, cy - s * 0.65 + math.sin(a) * s * 0.85
            o.append(strand(bx, by, bx + math.cos(a) * s * random.uniform(.25, .5), by + math.sin(a) * s * random.uniform(.25, .5) - s * 0.05, random.uniform(-.4, .4), INK, 1.2))
        o.append(strand(cx - s * 0.2, cy - s * 0.6, cx + s * 0.45, cy - s * 0.05, 0.25, INK, 1.2))
        o.append(strand(cx + s * 0.3, cy - s * 0.5, cx + s * 0.75, cy + s * 0.3, -0.2, INK, 1.2))
    if real_hair and fixed:
        # 补画的银色发丝盖住真发
        for sg in (-1, 1):
            for k in range(4):
                o.append(taper(cx + sg * s * (0.64 + k * 0.05), cy - s * 0.25, cx + sg * s * (0.66 + k * 0.05), cy + s * 0.5, -sg * 0.04, wig_d if k % 2 else INK, 1.6))
    return ''.join(o)


def head_back(cx, cy, s, wig=WIGPINK, wig_d=WIGPINK_D, peak=False, lace=False, lace_fixed=False, baby=False, strands=True):
    """背头（露出发际线）的头部特写"""
    o = []
    o.append(f'<rect x="{cx - s * 0.32:.1f}" y="{cy + s * 0.8:.1f}" width="{s * 0.64:.1f}" height="{s * 1.4:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
    o.append(f'<ellipse cx="{cx:.1f}" cy="{cy + s * 0.05:.1f}" rx="{s * 0.8:.1f}" ry="{s * 1.08:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
    for sg in (-1, 1):
        o.append(f'<path d="M{cx + sg * s * 0.47:.1f} {cy + s * 0.05:.1f} q{-sg * s * 0.15:.1f} {-s * 0.06:.1f} {-sg * s * 0.3:.1f} 0" fill="none" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>')
        o.append(f'<ellipse cx="{cx + sg * s * 0.32:.1f}" cy="{cy + s * 0.22:.1f}" rx="{s * 0.12:.1f}" ry="{s * 0.085:.1f}" fill="{INK}"/>')
    o.append(f'<path d="M{cx - s * 0.12:.1f} {cy + s * 0.72:.1f} q{s * 0.12:.1f} {s * 0.06:.1f} {s * 0.24:.1f} 0" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    hl = cy - s * 0.48           # 发际线高度
    pk = cy - s * 0.24 if peak else hl + s * 0.03
    d = (f'M{cx - s * 0.86:.1f} {cy + s * 0.05:.1f} Q{cx - s * 0.9:.1f} {hl:.1f} {cx - s * 0.62:.1f} {hl - s * 0.05:.1f} '
         f'Q{cx - s * 0.3:.1f} {hl - s * 0.12:.1f} {cx - s * 0.12:.1f} {hl - s * 0.02:.1f} L{cx:.1f} {pk:.1f} L{cx + s * 0.12:.1f} {hl - s * 0.02:.1f} '
         f'Q{cx + s * 0.3:.1f} {hl - s * 0.12:.1f} {cx + s * 0.62:.1f} {hl - s * 0.05:.1f} Q{cx + s * 0.9:.1f} {hl:.1f} {cx + s * 0.86:.1f} {cy + s * 0.05:.1f} '
         f'Q{cx + s * 1.15:.1f} {cy - s * 1.6:.1f} {cx:.1f} {cy - s * 1.62:.1f} Q{cx - s * 1.15:.1f} {cy - s * 1.6:.1f} {cx - s * 0.86:.1f} {cy + s * 0.05:.1f} Z')
    if lace:
        # 贴片：比皮肤稍浅、边缘一条硬线
        ly = hl + s * 0.14
        ld = f'M{cx - s * 0.78:.1f} {hl + s * 0.1:.1f} Q{cx:.1f} {ly - s * 0.1 + (s * 0.24 if peak else 0):.1f} {cx + s * 0.78:.1f} {hl + s * 0.1:.1f} L{cx + s * 0.7:.1f} {hl - s * 0.1:.1f} L{cx - s * 0.7:.1f} {hl - s * 0.1:.1f} Z'
        if not lace_fixed:
            o.append(f'<path d="{ld}" fill="#FFF1E6" stroke="{MUTED}" stroke-width="1.8"/>')
            o.append(f'<ellipse cx="{cx + s * 0.3:.1f}" cy="{hl + s * 0.04:.1f}" rx="{s * 0.16:.1f}" ry="{s * 0.04:.1f}" fill="{WHITE}" fill-opacity=".9"/>')
            o.append(f'<ellipse cx="{cx - s * 0.42:.1f}" cy="{hl + s * 0.05:.1f}" rx="{s * 0.1:.1f}" ry="{s * 0.03:.1f}" fill="{WHITE}" fill-opacity=".9"/>')
    o.append(f'<path d="{d}" fill="{wig}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
    if strands:
        # 发丝：从发际线往后脑梳
        for i in range(-6, 7):
            x0 = cx + i * s * 0.12
            y0 = hl - s * 0.02 if abs(i) > 1 else (pk - s * 0.05 if i == 0 else hl - s * 0.0)
            o.append(strand(x0, y0, cx + i * s * 0.05, cy - s * 1.45, 0.02 * i, wig_d, 1.6, 0.8))
    if baby:
        # 发际线边缘的细碎短发：密度从里到外变稀
        random.seed(7)
        for i in range(26):
            t = -0.75 + i * 0.06
            x0 = cx + t * s
            if peak and abs(t) < 0.14:
                y0 = pk - abs(t) * s * 1.6
            else:
                y0 = hl - s * 0.05 - (0.04 if abs(t) < .6 else 0) * s
            L = s * random.uniform(0.06, 0.13)
            o.append(strand(x0, y0 + s * 0.02, x0 + random.uniform(-2, 2), y0 + L, 0.1, wig_d, 1.2))
    return ''.join(o)


def photo_box(x, y, w, h, inner, bg='#FFF7E6'):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}" stroke="#94A3B8" stroke-width="1"/>'
            + rect_clip(x, y, w, h, f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>' + inner))


def bangs_photo(x, y, w, h, **kw):
    return photo_box(x, y, w, h, head_bangs(x + w / 2, y + h * 0.5, w * 0.27, **kw))


def back_photo(x, y, w, h, **kw):
    return photo_box(x, y, w, h, head_back(x + w / 2, y + h * 0.56, w * 0.27, **kw))


# ================= 5.1 假发和发际线 =================
def p_hair_flow():
    Wd, Hd = 760, 400
    s = [caption_box(20, 10, 360, 380, ''), caption_box(390, 10, 350, 380, '')]
    s.append(label(36, 44, '头发从发旋和发际线长出来', YEL1, 15))
    cx, cy = 200, 230
    s.append(f'<circle cx="{cx}" cy="{cy}" r="120" fill="{SILVER}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(f'<path d="M{cx - 120} {cy + 20} Q{cx} {cy + 150} {cx + 120} {cy + 20}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
    vx, vy = cx + 20, cy - 70
    for a in range(0, 360, 30):
        r = math.radians(a)
        s.append(arrow(vx + math.cos(r) * 14, vy + math.sin(r) * 14, vx + math.cos(r) * 70, vy + math.sin(r) * 70 + 10, VIO7, 2.5, marker='arwv'))
    s.append(f'<circle cx="{vx}" cy="{vy}" r="6" fill="{VIO7}"/>')
    s.append(label(vx + 26, vy - 50, '发旋', VIO1, 13))
    s.append(text(cx, 372, '每一根都从发根往发梢走，方向连续地变', 13, 600, MUTED, 'middle'))
    # 右：一束头发的结构
    s.append(label(406, 44, '一组发束的结构', YEL1, 15))
    bx = 520
    for i, dx in enumerate((-46, 0, 46)):
        s.append(clump(bx + dx, 70, bx + dx * 1.3 + 10, 330, 52, 0.05, SILVER))
    for dx in (-46, 0, 46):
        s.append(taper(bx + dx - 3, 150, bx + dx + 3, 205, 0, SILVER_L, 14))
    for dx in (-23, 23):
        s.append(strand(bx + dx, 80, bx + dx * 1.3 + 8, 300, 0.03, SILVER_D, 3))
    s.append(f'<rect x="{bx - 80}" y="{70}" width="160" height="40" fill="{INK}" fill-opacity=".12"/>')
    s.append(label(612, 98, '发根：粗、偏暗', WHITE, 13))
    s.append(label(612, 186, '高光带：横跨所有发束', VIO1, 13))
    s.append(label(612, 300, '发梢：变细、分叉', WHITE, 13))
    s.append(arrow(606, 92, 570, 92, INK, 2)); s.append(arrow(606, 180, 575, 180, INK, 2)); s.append(arrow(606, 294, 585, 312, INK, 2))
    s.append(text(565, 372, '发束之间是暗缝；高光在同一高度连成一条', 13, 600, MUTED, 'middle'))
    save('p-hair-flow', svg(Wd, Hd, ''.join(s), '头发的生长方向和发束结构'))


def p_strand():
    Wd, Hd = 760, 330
    s = []
    cols = [('粗细一样、平行等距', RED1, 'same'), ('方向和周围不一致', RED1, 'dir'), ('起笔粗、收笔尖、成组', MINT1, 'good')]
    for i, (t, f, k) in enumerate(cols):
        ox = 20 + i * 245
        s.append(caption_box(ox, 10, 230, 310, ''))
        s.append(label(ox + 14, 44, t, f, 14))
        # 底层发束（参考方向）
        for j in range(3):
            s.append(clump(ox + 60 + j * 55, 70, ox + 70 + j * 55, 290, 50, 0.08, SILVER, 2))
        if k == 'same':
            for j in range(7):
                s.append(f'<line x1="{ox + 70 + j * 16}" y1="110" x2="{ox + 70 + j * 16}" y2="250" stroke="{INK}" stroke-width="2.4"/>')
        elif k == 'dir':
            for j in range(6):
                s.append(strand(ox + 60 + j * 18, 120, ox + 140 + j * 14, 230, -0.1, INK, 2))
        else:
            random.seed(5)
            for g in range(3):
                for j in range(4):
                    x0 = ox + 66 + g * 55 + j * 6
                    L = random.uniform(120, 190)
                    s.append(taper(x0, 82, x0 + 10 + j * 2, 82 + L, 0.08, INK, random.uniform(1.6, 3.2)))
            s.append(taper(ox + 120, 90, ox + 92, 250, -0.05, INK, 2.2))
        mark = '✕' if f == RED1 else '✓'
        s.append(text(ox + 205, 46, mark, 22, 900, RED7 if f == RED1 else MINT7, 'middle'))
    save('p-strand', svg(Wd, Hd, ''.join(s), '补发丝的三种画法对比'))


def p_hairline():
    Wd, Hd = 760, 330
    s = []
    items = [('真发际线：越往外越稀、越短', MINT1, dict(baby=True)), ('贴片边：一条硬线 + 胶的反光', RED1, dict(lace=True)), ('修好：盖住硬线，补细碎短发', MINT1, dict(lace=True, lace_fixed=True, baby=True))]
    for i, (t, f, kw) in enumerate(items):
        ox = 20 + i * 245
        s.append(caption_box(ox, 10, 230, 310, ''))
        s.append(rect_clip(ox + 3, 60, 224, 256, head_back(ox + 115, 250, 95, **kw)))
        s.append(label(ox + 10, 44, t, f, 13))
    save('p-hairline', svg(Wd, Hd, ''.join(s), '发际线的密度变化：真发、贴片、修好以后'))


# 5.1 界面图的画布（左侧，给右边面板留位置）
LX, LY, LW, LH = 70, 66, 380, 380


def u_hair_clone():
    ph = bangs_photo(230, 66, 340, 340, flyaways=True)
    cx, cy, s_ = 400, 236, 340 * 0.27
    content = ph + disc(cx - s_ * 1.45, cy - s_ * 1.3)
    content += f'<path d="M{cx - s_ * 0.6:.1f} {cy - s_ * 1.72:.1f} q{s_ * 0.5:.1f} -12 {s_ * 1.0:.1f} 0" fill="none" stroke="#FFF7E6" stroke-width="16" stroke-linecap="round" stroke-opacity=".9"/>'
    s = screen(content + tool_sliders([('画笔尺寸', 0.12), ('强度', 1.0)]), active='adjust')
    s += ring(*icon_pos('adjust'), 18) + topinfo('克隆锁定状态')
    s += badge(cx - s_ * 1.45, cy - s_ * 1.3 - 30, 1) + badge(cx - s_ * 0.1, cy - s_ * 1.95, 2)
    s += label(36, 300, '① 圆盘放在杂毛旁边', YEL1, 14) + label(36, 332, '　 干净的背景上，长按锁定', YEL1, 14)
    s += label(584, 120, '② 沿发型外轮廓', YEL1, 14) + label(584, 152, '　 小段小段地涂', YEL1, 14)
    s += label(584, 200, '画笔尺寸调小，', WHITE, 13) + label(584, 228, '只盖住杂毛，别碰到发束', WHITE, 13)
    s += ui_note()
    save('u-hair-clone', svg(W, H, s, '克隆：用旁边的背景盖掉飞出来的杂毛'))


def u_brush_lib():
    ph = bangs_photo(60, 66, 260, 340)
    groups = ['最近', '素描', '着墨', '绘图', '上漆', '气笔修饰', '亮度']
    brushes = ['细尖', '技术笔', '凝胶墨水笔', '墨水渗流', '工作室笔', '干油墨']
    s = screen(ph + brush_lib(groups, '着墨', brushes, '工作室笔'), active='brush')
    s += ring(*icon_pos('brush'), 18) + badge(icon_pos('brush')[0] - 26, 62, 1)
    s += badge(330 + 8 + 116, 62 + 42 + 2 * 36 + 15, 2) + badge(756, 62 + 42 + 4 * 36 + 15, 3)
    s += label(330, 400, '「工作室笔」或「细尖」：压感控制粗细，抬笔时会变尖', YEL1, 14)
    s += label(330, 432, '新版画笔库里，「着墨」在「经典库」中', WHITE, 13)
    s += ui_note('示意图，画笔名称和排序以实际界面为准')
    save('u-brush-lib', svg(W, H, s, '画笔库：着墨里的工作室笔'))


def u_hair_pick():
    ph = bangs_photo(230, 66, 340, 340)
    cx, cy, s_ = 400, 236, 340 * 0.27
    content = ph + eyedropper(cx - s_ * 0.25, cy - s_ * 0.85, SILVER_L, SILVER)
    content += f'<circle cx="{cx - s_ * 0.25:.1f}" cy="{cy - s_ * 0.85:.1f}" r="4" fill="{INK}"/>'
    s = screen(content, active='color')
    s += badge(cx - s_ * 0.25 + 40, cy - s_ * 0.85 - 30, 1)
    sw = [('暗：发束之间的缝', SILVER_D), ('中：发束本身', SILVER), ('亮：高光带', SILVER_L)]
    for i, (t, c) in enumerate(sw):
        yy = 150 + i * 56
        s += f'<rect x="590" y="{yy}" width="36" height="36" rx="8" fill="{c}" stroke="{INK}" stroke-width="2"/>' + label(636, yy + 24, t, YEL1, 13)
    s += label(36, 240, '① 手指长按画布，', YEL1, 14) + label(36, 272, '　 出现吸管再拖到要取的地方', YEL1, 14)
    s += label(36, 316, '上半圈：要取的新颜色', WHITE, 13) + label(36, 344, '下半圈：当前颜色', WHITE, 13)
    s += label(590, 340, '② 在补的位置旁边各取一次', YEL1, 14)
    s += ui_note()
    save('u-hair-pick', svg(W, H, s, '长按画布调出吸管，在补发丝的位置旁边取暗、中、亮三个颜色'))


def u_hair_layers():
    ph = bangs_photo(60, 66, 300, 340)
    lay, P = layers2([dict(name='发丝高光', col=WHITE, mode='添加', sel=True),
                      dict(name='补发丝', col=WHITE),
                      dict(name='修补', col='#FFF7E6', thumb='photo'),
                      dict(name='原图', col='#FFF7E6', thumb='photo', lock=True)], x=470)
    pop = blend_popup(470, 330, ['滤色', '颜色减淡', '添加', '浅色'], '添加', 0.45, 300)
    s = screen(ph + lay + pop, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += badge(470 + 300 - 100, 62 + 44 + 22, 1)
    s += badge(456, 330 + 54 + 2 * 30 + 13, 2)
    s += label(66, 440, '① 点「发丝高光」右边的模式字母', YEL1, 13)
    s += label(66, 470, '② 选「添加」，不透明度先放 40%～50%', YEL1, 13)
    s += ui_note('示意图：实际界面里模式显示为缩写字母')
    save('u-hair-layers', svg(W, H, s, '补发丝的图层：修补、补发丝、发丝高光（添加模式）'))


def u_hair_paint():
    ph = bangs_photo(230, 66, 340, 340, glint=True)
    cx, cy, s_ = 400, 236, 340 * 0.27
    content = ph
    random.seed(11)
    # 正在补的一组发丝（在左侧刘海缺口处）
    gx = cx - s_ * 0.45
    for j in range(5):
        x0 = gx + j * 5
        content += taper(x0, cy - s_ * 1.3, x0 - 6 + j * 3, cy - s_ * 0.2 - random.uniform(0, 14), 0.04, INK, random.uniform(1.6, 2.8))
    content += arrow(gx + 40, cy - s_ * 1.3, gx + 36, cy - s_ * 0.35, VIO7, 3, marker='arwv')
    s = screen(content, active='brush')
    s += ring(*icon_pos('brush'), 18) + ringrect(26, 160, 26, 100, 10)
    s += badge(64, 210, 1)
    s += label(584, 110, '② 从发根起笔，往发梢画', YEL1, 14)
    s += label(584, 142, '　 起笔压重，收笔抬轻', YEL1, 14)
    s += label(584, 190, '③ 三五根一组，长短不一', YEL1, 14)
    s += label(584, 222, '　 方向跟旁边的发束一致', YEL1, 14)
    s += label(76, 300, '① 尺寸 1%～3%', YEL1, 14) + label(76, 332, '不透明度 80%～100%', WHITE, 13)
    s += badge(gx + 60, cy - s_ * 0.8, 2)
    s += ui_note()
    save('u-hair-paint', svg(W, H, s, '在补发丝图层上，用细笔沿发束方向从发根画到发梢'))


def u_peak_sel():
    ph = back_photo(230, 66, 340, 340)
    cx, cy, s_ = 400, 66 + 340 * 0.56, 340 * 0.27
    d = ellipse_d(cx, cy - s_ * 0.75, s_ * 0.32, s_ * 0.24)
    s = screen(ph + sel_ants_path(d) + bottom_bar(SEL_ROWS, active=('手绘',), hl='拷贝并粘贴'), active='select')
    s += ring(*icon_pos('select'), 18) + badge(icon_pos('select')[0] + 26, 62, 1)
    px, py, pw, phh = POS['拷贝并粘贴']
    s += badge(cx + s_ * 0.45, cy - s_ * 0.9, 2) + badge(px + pw / 2, py - 14, 3)
    s += label(584, 140, '② 圈一块发际线上方的头发', YEL1, 14)
    s += label(584, 172, '　 包括一段发际线边缘', YEL1, 14)
    s += label(584, 220, '③ 拷贝并粘贴到新图层', YEL1, 14)
    s += ui_note()
    save('u-peak-sel', svg(W, H, s, '手绘选取圈一块发际线附近的头发，拷贝并粘贴'))


def u_peak_warp():
    cx, cy, s_ = 400, 66 + 340 * 0.56, 340 * 0.27
    ph = back_photo(230, 66, 340, 340, peak=True, strands=True)
    bx, by, bw, bh = cx - s_ * 0.36, cy - s_ * 1.0, s_ * 0.72, s_ * 0.62
    s = screen(ph + bbox(bx, by, bw, bh, True, warp=True) + bottom_bar(TF_ROWS, active=('弯曲',)), active='transform')
    s += ring(*icon_pos('transform'), 18)
    s += arrow(cx, by + bh + 34, cx, by + bh + 4, INK, 3)
    s += badge(cx + 24, by + bh + 26, 1)
    s += label(584, 150, '① 选「弯曲」，把网格下边', YEL1, 14)
    s += label(584, 182, '　 中间往下拖，做出尖角', YEL1, 14)
    s += label(584, 230, '尖角往下 0.3～0.5 个指节宽', WHITE, 13)
    s += label(584, 258, '左右两边保持原来的发际线', WHITE, 13)
    s += ui_note()
    save('u-peak-warp', svg(W, H, s, '变换选弯曲，把复制出的发际线中间往下拉出美人尖'))


def u_real_hair_sel():
    ph = bangs_photo(230, 66, 340, 340, real_hair=True)
    cx, cy, s_ = 400, 236, 340 * 0.27
    hi = f'<path d="M{cx + s_ * 0.74:.1f} {cy - s_ * 0.2:.1f} Q{cx + s_ * 0.86:.1f} {cy + s_ * 0.2:.1f} {cx + s_ * 0.7:.1f} {cy + s_ * 0.5:.1f} L{cx + s_ * 0.6:.1f} {cy + s_ * 0.42:.1f} Q{cx + s_ * 0.7:.1f} {cy + s_ * 0.15:.1f} {cx + s_ * 0.62:.1f} {cy - s_ * 0.15:.1f} Z" fill="{YEL}" fill-opacity=".85"/>'
    bar = f'<rect x="250" y="62" width="300" height="30" rx="15" fill="{UIBLUE}"/>' + text(400, 82, '选区阈值：42%', 14, 700, WHITE, 'middle')
    s = screen(ph + hi + bar + bottom_bar(SEL_ROWS, active=('自动',)), active='select')
    s += ring(*icon_pos('select'), 18)
    s += badge(cx + s_ * 0.95, cy + s_ * 0.1, 1) + badge(560, 77, 2)
    s += label(584, 150, '① 「自动」：轻点露出的真发', YEL1, 14)
    s += label(584, 182, '② 按住不放，左右拖调阈值', YEL1, 14)
    s += label(584, 230, '选区会显示成反差色（这里是黄色）', WHITE, 13)
    s += label(584, 258, '刚好盖满真发、不漏到皮肤就停', WHITE, 13)
    s += ui_note()
    save('u-real-hair-sel', svg(W, H, s, '自动选取轻点露出的真发，拖动调整选区阈值'))


def case51(kind, after):
    Wd, Hd = 640, 480
    x, y, w, h = 20, 20, 600, 440
    if kind == 'fly':
        inner = head_bangs(320, 250, 120, flyaways=not after, real_hair=True, fixed=after)
        lab = '修之后：杂毛去掉，鬓角的真发盖住了' if after else '修之前：头顶杂毛，鬓角露出黑色真发'
    elif kind == 'peak':
        inner = head_back(320, 270, 120, peak=after, baby=after)
        lab = '修之后：补出美人尖，边缘有细碎短发' if after else '修之前：发际线平直，没有美人尖'
    else:
        inner = head_back(320, 270, 120, wig='#A78BFA', wig_d='#6D28D9', lace=True, lace_fixed=after, baby=after)
        lab = '修之后：贴片边和反光去掉，发际线有过渡' if after else '修之前：贴片边一条硬线，胶有反光'
    s = photo_box(x, y, w, h, inner)
    s += label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15)
    return svg(Wd, Hd, s, lab)

if __name__ == '__main__' and 'only51' in sys.argv:
    for f in [p_hair_flow, p_strand, p_hairline, u_hair_clone, u_brush_lib, u_hair_pick, u_hair_layers, u_hair_paint, u_peak_sel, u_peak_warp, u_real_hair_sel]:
        f()
    for k in ('fly', 'peak', 'lace'):
        save(f'case-{k}-before', case51(k, False)); save(f'case-{k}-after', case51(k, True))
    print('ok', len(MADE))


# ================= 5.2 美瞳和眼神光 =================
BROWN = '#5B3A29'; BROWN_L = '#8B5E3C'


def eye(cx, cy, w, iris=BROWN, pupil='round', catch='main', glare=False, veins=False, lens_edge=False,
        fibers=True, lid_shadow=True, extra_catch=False, ring_col=None, pattern=None, sclera='#F4F1EC'):
    """眼睛特写。w：眼睛宽度"""
    o = []
    x0, x1 = cx - w / 2, cx + w / 2
    up = f'M{x0:.1f} {cy:.1f} Q{cx - w * 0.1:.1f} {cy - w * 0.52:.1f} {x1:.1f} {cy - w * 0.04:.1f}'
    eye_d = up + f' Q{cx + w * 0.05:.1f} {cy + w * 0.34:.1f} {x0:.1f} {cy:.1f} Z'
    r = w * 0.2
    ix, iy = cx + w * 0.02, cy - w * 0.06
    inner = [f'<path d="{eye_d}" fill="{sclera}"/>']
    # 眼白两端偏暗（眼球是球）
    inner.append(f'<ellipse cx="{x0 + w * 0.08:.1f}" cy="{cy:.1f}" rx="{w * 0.12:.1f}" ry="{w * 0.12:.1f}" fill="#D6CFC4" fill-opacity=".7"/>')
    inner.append(f'<ellipse cx="{x1 - w * 0.06:.1f}" cy="{cy - w * 0.03:.1f}" rx="{w * 0.1:.1f}" ry="{w * 0.1:.1f}" fill="#D6CFC4" fill-opacity=".7"/>')
    if veins:
        for k, (a, L) in enumerate([(170, .2), (190, .16), (12, .18), (-8, .14), (160, .1)]):
            rr = math.radians(a)
            sx = ix + math.cos(rr) * (r + 3); sy = iy + math.sin(rr) * (r + 3)
            inner.append(strand(sx + math.cos(rr) * w * L, sy + math.sin(rr) * w * L * 0.6, sx, sy, 0.25 * (-1) ** k, '#E11D48', 1.4, 0.8))
    if lens_edge:
        inner.append(f'<circle cx="{ix + w * 0.035:.1f}" cy="{iy + w * 0.01:.1f}" r="{r * 1.28:.1f}" fill="none" stroke="#B8AFA3" stroke-width="2"/>')
    inner.append(f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="{r:.1f}" fill="{iris}"/>')
    light = hexmix(iris, '#FFFFFF', 0.45); dark = hexmix(iris, '#000000', 0.45)
    if fibers:
        random.seed(int(cx + cy))
        for a in range(0, 360, 9):
            rr = math.radians(a + random.uniform(-3, 3))
            r0 = r * 0.36; r1 = r * random.uniform(0.75, 0.95)
            inner.append(f'<line x1="{ix + math.cos(rr) * r0:.1f}" y1="{iy + math.sin(rr) * r0:.1f}" x2="{ix + math.cos(rr) * r1:.1f}" y2="{iy + math.sin(rr) * r1:.1f}" '
                         f'stroke="{light if a % 18 else dark}" stroke-width="{w * 0.008 + 0.8:.1f}" stroke-linecap="round" stroke-opacity=".8"/>')
        inner.append(f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="{r * 0.48:.1f}" fill="none" stroke="{light}" stroke-width="{w * 0.012:.1f}" stroke-opacity=".6"/>')
    if pattern == 'star':
        pts = []
        for k in range(10):
            rr = math.radians(-90 + k * 36); rad = r * (0.7 if k % 2 == 0 else 0.4)
            pts.append(f'{ix + math.cos(rr) * rad:.1f},{iy + math.sin(rr) * rad:.1f}')
        inner.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="{hexmix(iris, "#FFFFFF", 0.7)}" stroke-width="{w * 0.01 + 1:.1f}"/>')
    # 边缘环
    inner.append(f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="{r * 0.97:.1f}" fill="none" stroke="{ring_col or dark}" stroke-width="{w * 0.025:.1f}"/>')
    if pupil == 'round':
        inner.append(f'<circle cx="{ix:.1f}" cy="{iy:.1f}" r="{r * 0.34:.1f}" fill="#111"/>')
    elif pupil == 'slit':
        inner.append(f'<path d="M{ix:.1f} {iy - r * 0.82:.1f} Q{ix + r * 0.2:.1f} {iy:.1f} {ix:.1f} {iy + r * 0.82:.1f} Q{ix - r * 0.2:.1f} {iy:.1f} {ix:.1f} {iy - r * 0.82:.1f} Z" fill="#111"/>')
    if lid_shadow:
        g = uid('g')
        inner.append(f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient></defs>')
        inner.append(f'<rect x="{x0:.1f}" y="{cy - w * 0.5:.1f}" width="{w:.1f}" height="{w * 0.36:.1f}" fill="url(#{g})"/>')
    if glare:
        inner.append(f'<ellipse cx="{ix - r * 0.15:.1f}" cy="{iy + r * 0.1:.1f}" rx="{r * 0.95:.1f}" ry="{r * 0.75:.1f}" fill="#FFFFFF" fill-opacity=".55"/>')
        inner.append(f'<ellipse cx="{ix + r * 0.4:.1f}" cy="{iy + r * 0.45:.1f}" rx="{r * 0.25:.1f}" ry="{r * 0.12:.1f}" fill="#FFFFFF" fill-opacity=".8"/>')
    if catch in ('main', 'ring', 'rect'):
        kx, ky = ix - r * 0.42, iy - r * 0.42
        if catch == 'main':
            inner.append(f'<circle cx="{kx:.1f}" cy="{ky:.1f}" r="{r * 0.2:.1f}" fill="#FFFFFF"/>')
        elif catch == 'ring':
            inner.append(f'<circle cx="{ix:.1f}" cy="{iy - r * 0.05:.1f}" r="{r * 0.6:.1f}" fill="none" stroke="#FFFFFF" stroke-width="{r * 0.13:.1f}"/>')
        else:
            inner.append(f'<rect x="{kx - r * 0.18:.1f}" y="{ky - r * 0.14:.1f}" width="{r * 0.36:.1f}" height="{r * 0.28:.1f}" rx="2" fill="#FFFFFF"/>')
    if extra_catch:
        inner.append(f'<circle cx="{ix + r * 0.5:.1f}" cy="{iy + r * 0.35:.1f}" r="{r * 0.07:.1f}" fill="#FFFFFF" fill-opacity=".9"/>')
        inner.append(f'<circle cx="{ix + r * 0.62:.1f}" cy="{iy - r * 0.2:.1f}" r="{r * 0.05:.1f}" fill="#FFFFFF" fill-opacity=".9"/>')
    o.append(clipped(eye_d, ''.join(inner)))
    o.append(f'<path d="{up}" fill="none" stroke="{INK}" stroke-width="{w * 0.045:.1f}" stroke-linecap="round"/>')
    o.append(f'<path d="M{x1:.1f} {cy - w * 0.04:.1f} Q{cx + w * 0.05:.1f} {cy + w * 0.34:.1f} {x0:.1f} {cy:.1f}" fill="none" stroke="{INK}" stroke-width="{w * 0.015 + 1:.1f}" stroke-opacity=".7"/>')
    # 睫毛
    for k in range(6):
        t = 0.45 + k * 0.1
        px = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * (cx - w * 0.1) + t * t * x1
        py = (1 - t) ** 2 * cy + 2 * (1 - t) * t * (cy - w * 0.52) + t * t * (cy - w * 0.04)
        o.append(strand(px, py, px + w * 0.06 + k * w * 0.012, py - w * 0.08 + k * w * 0.012, -0.2, INK, w * 0.012 + 1))
    return ''.join(o), (ix, iy, r)


def skin_box(x, y, w, h, inner):
    return photo_box(x, y, w, h, inner, bg=SKIN)


def eye_photo(x, y, w, h, **kw):
    e, geo = eye(x + w / 2, y + h * 0.55, w * 0.78, **kw)
    brow = f'<path d="M{x + w * 0.12:.1f} {y + h * 0.16:.1f} Q{x + w * 0.5:.1f} {y + h * 0.02:.1f} {x + w * 0.9:.1f} {y + h * 0.14:.1f}" fill="none" stroke="#6B4F3F" stroke-width="{w * 0.05:.1f}" stroke-linecap="round"/>'
    return skin_box(x, y, w, h, brow + e), geo


def p_eye_anatomy():
    Wd, Hd = 760, 420
    s = [caption_box(20, 10, 720, 400, '')]
    e, (ix, iy, r) = eye(240, 240, 400, iris='#6B8E9B', catch='main')
    s.append(e)
    items = [('瞳孔：最黑的圆点', ix + r * 0.2, iy + r * 0.1, 500, 120),
             ('虹膜：从瞳孔往外放射的纹理', ix + r * 0.6, iy + r * 0.25, 500, 170),
             ('边缘环：虹膜外圈的一圈深色', ix + r * 0.95, iy + r * 0.2, 500, 220),
             ('眼神光：主光源在眼球上的倒影', ix - r * 0.42, iy - r * 0.42, 500, 70),
             ('上眼皮的投影：虹膜上半偏暗', ix + r * 0.1, iy - r * 0.8, 500, 270),
             ('眼白：不是纯白，两头偏暗', 110, 250, 500, 320)]
    for t, ax, ay, lx, ly in items:
        s.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{lx - 10}" y2="{ly - 6}" stroke="{INK}" stroke-width="1.8"/>')
        s.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="4" fill="{YEL}" stroke="{INK}" stroke-width="1.5"/>')
        s.append(label(lx - 10, ly, t, YEL1, 13, 'start'))
    s.append(label(36, 44, '眼睛的结构', YEL1, 15))
    save('p-eye-anatomy', svg(Wd, Hd, ''.join(s).replace('x="610.0"', 'x="610.0"'), '眼睛的结构：瞳孔、虹膜、边缘环、眼神光、眼白'))


def p_catchlight():
    Wd, Hd = 760, 300
    s = []
    cases = [('保留主眼神光：有神', MINT1, dict(catch='main')), ('全部去掉：像黑洞', RED1, dict(catch='none')),
             ('多余的小反光：可以去', YEL1, dict(catch='main', extra_catch=True))]
    for i, (t, f, kw) in enumerate(cases):
        ox = 20 + i * 245
        s.append(caption_box(ox, 10, 230, 280, ''))
        s.append(rect_clip(ox + 3, 56, 224, 230, f'<rect x="{ox}" y="56" width="230" height="230" fill="{SKIN}"/>' + eye(ox + 115, 180, 190, iris='#2B2B2B', **kw)[0]))
        s.append(label(ox + 12, 44, t, f, 14))
    save('p-catchlight', svg(Wd, Hd, ''.join(s), '主眼神光要留，杂乱的小反光可以去'))


def p_blend_eye():
    """「颜色」和「覆盖」在深色、浅色虹膜上的效果（按公式近似计算）"""
    Wd, Hd = 760, 360
    s = [caption_box(20, 10, 720, 340, '')]
    bases = [('深棕虹膜', '#3B2A20'), ('提亮后的虹膜', '#9A8578')]
    tops = [('蓝色', '#3B82F6'), ('金色', '#F5B301')]
    s.append(text(200, 52, '直接用「颜色」', 15, 800, INK, 'middle'))
    s.append(text(380, 52, '直接用「覆盖」', 15, 800, INK, 'middle'))
    s.append(text(560, 52, '原色', 15, 800, INK, 'middle'))
    for i, (bn, bc) in enumerate(bases):
        for j, (tn, tc) in enumerate(tops):
            row = i * 2 + j
            yy = 76 + row * 66
            s.append(text(40, yy + 36, f'{bn} + {tn}', 13, 700, INK))
            for k, col in enumerate([blend_color(bc, tc), blend_overlay(bc, tc), bc]):
                xx = 170 + k * 180
                s.append(f'<circle cx="{xx + 30}" cy="{yy + 30}" r="26" fill="{col}" stroke="{INK}" stroke-width="2"/><circle cx="{xx + 30}" cy="{yy + 30}" r="9" fill="#111"/>')
                s.append(f'<circle cx="{xx + 21}" cy="{yy + 21}" r="5" fill="#FFF"/>')
    s.append(label(620, 120, '深色虹膜：', RED1, 13))
    s.append(label(620, 148, '两种都换不亮', RED1, 13))
    s.append(label(620, 250, '先提亮虹膜，', MINT1, 13))
    s.append(label(620, 278, '再换色就鲜艳', MINT1, 13))
    save('p-blend-eye', svg(Wd, Hd, ''.join(s), '颜色模式和覆盖模式：深色虹膜要先提亮再换色'))


EX, EY, EW, EH = 150, 70, 380, 330


def u_iris_sel():
    ph, (ix, iy, r) = eye_photo(EX, EY, EW, EH, glare=True, iris=BROWN)
    d = ellipse_d(ix, iy, r * 1.02, r * 1.02)
    s = screen(ph + sel_ants_path(d) + bottom_bar(SEL_ROWS, active=('椭圆',), hl='羽化'), active='select')
    s += ring(*icon_pos('select'), 18) + badge(icon_pos('select')[0] + 26, 62, 1)
    s += badge(POS['椭圆'][0] + POS['椭圆'][2] / 2, POS['椭圆'][1] - 14, 2)
    s += badge(ix + r + 26, iy - r, 3)
    s += badge(POS['羽化'][0] + POS['羽化'][2] / 2, POS['羽化'][1] - 14, 4)
    s += label(546, 130, '② 选「椭圆」', YEL1, 14)
    s += label(546, 162, '③ 沿虹膜外圈拖一个圆', YEL1, 14)
    s += label(546, 194, '④ 「羽化」1%～2%', YEL1, 14)
    s += label(546, 240, '上眼皮盖住的部分', WHITE, 13) + label(546, 268, '下一步再擦掉', WHITE, 13)
    s += ui_note()
    save('u-iris-sel', svg(W, H, s, '椭圆选取框住虹膜，稍微羽化'))


def u_iris_layers():
    ph, (ix, iy, r) = eye_photo(40, 70, 240, 260, glare=False, iris=BROWN)
    lay, P = layers2([dict(name='眼神光', col=WHITE, sel=False),
                      dict(name='瞳色', col='#3B82F6', mode='颜色', clip=True, sel=True),
                      dict(name='虹膜', col=BROWN),
                      dict(name='修补', col=SKIN, thumb=None),
                      dict(name='原图', col=SKIN, lock=True)], x=470)
    opts = layer_options(290, 62, '剪辑蒙版')
    s = screen(ph + lay + opts, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += badge(470 + 22 + 20, 62 + 44 + 50 + 22, 1)
    s += badge(276, 62 + 4 + 7 * 30 + 15, 2)
    s += label(40, 488, '① 在「虹膜」上面新建「瞳色」层，轻点两次打开图层选项', YEL1, 13)
    s += label(40, 518, '② 点「剪辑蒙版」：左边出现小箭头，颜色只出现在虹膜范围内', YEL1, 13)
    s += ui_note('示意图：实际界面里模式显示为缩写字母')
    save('u-iris-layers', svg(W, H, s, '新建瞳色图层，在图层选项里设成剪辑蒙版'))


def u_eye_curves():
    ph, (ix, iy, r) = eye_photo(EX, EY, EW, EH, glare=True, iris=BROWN)
    px, py, pw, phh = 520, 120, 250, 260
    cv = panel(px, py, pw, phh, '曲线')
    gx, gy, gw, gh = px + 20, py + 46, pw - 40, phh - 66
    cv += f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="#1F2329"/>'
    for i in range(1, 4):
        cv += f'<line x1="{gx + gw * i / 4:.1f}" y1="{gy}" x2="{gx + gw * i / 4:.1f}" y2="{gy + gh}" stroke="#4B5563"/><line x1="{gx}" y1="{gy + gh * i / 4:.1f}" x2="{gx + gw}" y2="{gy + gh * i / 4:.1f}" stroke="#4B5563"/>'
    cv += f'<line x1="{gx}" y1="{gy + gh}" x2="{gx + gw}" y2="{gy}" stroke="#6B7280" stroke-dasharray="4 4"/>'
    cv += f'<path d="M{gx} {gy + gh} C{gx + gw * 0.35} {gy + gh * 1.0} {gx + gw * 0.6} {gy + gh * 0.45} {gx + gw} {gy}" fill="none" stroke="{WHITE}" stroke-width="3"/>'
    cv += f'<circle cx="{gx + gw * 0.55:.1f}" cy="{gy + gh * 0.62:.1f}" r="7" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'
    s = screen(ph + cv, active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += badge(gx + gw * 0.55 + 22, gy + gh * 0.62 + 10, 1)
    s += label(40, 440, '① 在「虹膜」层上：中间调往下拉、亮部点留在原位，蒙在虹膜上的白雾被压下去', YEL1, 13)
    s += ui_note()
    save('u-eye-curves', svg(W, H, s, '调整、曲线：压暗中间调，去掉美瞳上的反光雾'))


def u_iris_paint():
    ph, (ix, iy, r) = eye_photo(EX, EY, EW, EH, iris='#4A6FA5', fibers=False, catch='none')
    strokes = ''
    for a in range(-160, 20, 22):
        rr = math.radians(a)
        strokes += taper(ix + math.cos(rr) * r * 0.4, iy + math.sin(rr) * r * 0.4, ix + math.cos(rr) * r * 0.9, iy + math.sin(rr) * r * 0.9, 0.05, '#BFD7F2', 3)
    strokes += arrow(ix + r * 0.35, iy + r * 0.35, ix + r * 0.85, iy + r * 0.85, VIO7, 3, marker='arwv')
    s = screen(ph + strokes, active='brush')
    s += ring(*icon_pos('brush'), 18)
    s += badge(ix + r * 0.95, iy + r * 0.95, 1)
    s += label(546, 130, '① 从瞳孔边往外画', YEL1, 14)
    s += label(546, 162, '　 短线，压重起笔，抬笔收尖', YEL1, 14)
    s += label(546, 210, '亮线一层（覆盖模式）', WHITE, 13)
    s += label(546, 238, '暗线一层（正片叠底）', WHITE, 13)
    s += label(546, 266, '间隔不均、长短不一', WHITE, 13)
    s += ui_note()
    save('u-iris-paint', svg(W, H, s, '在虹膜上沿放射方向画纹理'))


def u_catch_paint():
    ph, (ix, iy, r) = eye_photo(EX, EY, EW, EH, iris='#4A6FA5', catch='none')
    kx, ky = ix - r * 0.42, iy - r * 0.42
    c = ph + f'<circle cx="{kx:.1f}" cy="{ky:.1f}" r="{r * 0.2:.1f}" fill="#FFFFFF"/><circle cx="{kx:.1f}" cy="{ky:.1f}" r="{r * 0.2 + 10:.1f}" fill="none" stroke="{YEL}" stroke-width="3" stroke-dasharray="5 4"/>'
    s = screen(c, active='brush')
    s += ring(*icon_pos('brush'), 18)
    s += badge(kx - r * 0.2 - 22, ky, 1)
    s += label(546, 120, '① 位置：和脸上的主光同一侧', YEL1, 14)
    s += label(546, 152, '　 两只眼睛在同一个方位', YEL1, 14)
    s += label(546, 200, '形状跟着光源：', WHITE, 13)
    s += label(546, 228, '环形灯是圈，柔光箱是方块，', WHITE, 13)
    s += label(546, 256, '窗户是带格子的方块', WHITE, 13)
    s += label(546, 304, '② 一半压在瞳孔上，一半在虹膜上', YEL1, 13)
    s += ui_note()
    save('u-catch-paint', svg(W, H, s, '在新图层上补画眼神光'))


def u_slit():
    ph, (ix, iy, r) = eye_photo(EX, EY, EW, EH, iris='#D9A400', pupil='slit', catch='main', ring_col='#7A4B00')
    s = screen(ph + bbox(ix - r * 0.25, iy - r * 0.85, r * 0.5, r * 1.7, True), active='transform')
    s += ring(*icon_pos('transform'), 18)
    s += label(546, 120, '竖瞳单独画在一层上', YEL1, 14)
    s += label(546, 152, '高约虹膜的 3/4，中间最宽', YEL1, 14)
    s += label(546, 200, '先把原来的圆瞳孔盖掉', WHITE, 13)
    s += label(546, 228, '（用虹膜颜色和纹理补）', WHITE, 13)
    s += label(546, 276, '眼神光画在竖瞳上面一层', WHITE, 13)
    s += ui_note()
    save('u-slit', svg(W, H, s, '竖瞳：单独一层画好后用变换调整高度和位置'))


def case52(kind, after):
    Wd, Hd = 640, 420
    x, y, w, h = 20, 20, 600, 380
    if kind == 'glare':
        kw = dict(iris='#6B5B95', glare=not after, catch='ring', lens_edge=not after, veins=not after)
        lab = '修之后：反光雾去掉，环形灯的眼神光留着' if after else '修之前：美瞳一层白雾，边缘露出来，眼白有血丝'
    elif kind == 'slit':
        kw = dict(iris='#D9A400', pupil='slit', ring_col='#7A4B00', catch='main') if after else dict(iris=BROWN, catch='main')
        lab = '修之后：金色竖瞳，纹理和眼神光都在' if after else '修之前：本人深棕色圆瞳孔'
    else:
        kw = dict(iris='#2F2F2F', catch='rect' if after else 'none', lid_shadow=True)
        lab = '修之后：补了和主光一致的眼神光' if after else '修之前：背光拍摄，眼睛里没有光'
    inner, _ = eye(x + w / 2, y + h * 0.6, w * 0.7, **kw)
    brow = f'<path d="M{x + w * 0.15:.1f} {y + h * 0.2:.1f} Q{x + w * 0.5:.1f} {y + h * 0.05:.1f} {x + w * 0.88:.1f} {y + h * 0.18:.1f}" fill="none" stroke="#6B4F3F" stroke-width="22" stroke-linecap="round"/>'
    s = skin_box(x, y, w, h, brow + inner)
    s += label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15)
    return svg(Wd, Hd, s, lab)

if __name__ == '__main__' and 'only52' in sys.argv:
    for f in [p_eye_anatomy, p_catchlight, p_blend_eye, u_iris_sel, u_iris_layers, u_eye_curves, u_iris_paint, u_catch_paint, u_slit]:
        f()
    for k in ('glare', 'slit', 'nocatch'):
        save(f'case-{k}-before', case52(k, False)); save(f'case-{k}-after', case52(k, True))
    print('ok', len(MADE))


# ================= 5.3 衣服褶皱和道具接缝 =================
SHIRT = '#E0E7FF'; SHIRT_D = '#8A94B8'; SHIRT_L = '#FFFFFF'


def fold(x1, y1, x2, y2, bend=0.15, w=3.0, d=SHIRT_D, l=SHIRT_L):
    """一道褶：暗沟 + 旁边的亮棱"""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * 3, dx / L * 3
    return (taper(x1 + nx, y1 + ny, x2 + nx, y2 + ny, bend, l, w * 1.3) + taper(x1, y1, x2, y2, bend, d, w))


def shirt(cx, top, s, messy=True, crease=True, structure=True, gray=False):
    """上半身衬衫：右臂弯曲（手肘结构褶），腰部乱褶，胸口叠放压痕"""
    base = '#D4D4D8' if gray else SHIRT
    dcol = '#71717A' if gray else SHIRT_D
    o = []
    # 弯曲的右臂（画面左侧）：上臂往下，前臂往前抬
    sh = (cx - s * 0.95, top + s * 0.35)
    el = (cx - s * 1.15, top + s * 1.45)
    wr = (cx - s * 0.35, top + s * 1.75)
    o.append(f'<path d="M{sh[0]:.1f} {sh[1]:.1f} L{el[0]:.1f} {el[1]:.1f} L{wr[0]:.1f} {wr[1]:.1f}" fill="none" stroke="{INK}" stroke-width="{s * 0.5 + 5:.1f}" stroke-linejoin="round" stroke-linecap="round"/>')
    o.append(f'<path d="M{sh[0]:.1f} {sh[1]:.1f} L{el[0]:.1f} {el[1]:.1f} L{wr[0]:.1f} {wr[1]:.1f}" fill="none" stroke="{base}" stroke-width="{s * 0.5:.1f}" stroke-linejoin="round" stroke-linecap="round"/>')
    o.append(f'<circle cx="{wr[0] + s * 0.12:.1f}" cy="{wr[1]:.1f}" r="{s * 0.17:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
    # 躯干
    o.append(f'<path d="M{cx - s * 0.95:.1f} {top + s * 0.2:.1f} Q{cx:.1f} {top:.1f} {cx + s * 0.95:.1f} {top + s * 0.2:.1f} L{cx + s * 0.8:.1f} {top + s * 2.4:.1f} '
             f'L{cx - s * 0.8:.1f} {top + s * 2.4:.1f} Z" fill="{base}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
    # 左臂（自然下垂）
    o.append(f'<path d="M{cx + s * 0.95:.1f} {top + s * 0.3:.1f} Q{cx + s * 1.2:.1f} {top + s * 1.3:.1f} {cx + s * 1.05:.1f} {top + s * 2.3:.1f}" fill="none" stroke="{INK}" stroke-width="{s * 0.42 + 5:.1f}" stroke-linecap="round"/>')
    o.append(f'<path d="M{cx + s * 0.95:.1f} {top + s * 0.3:.1f} Q{cx + s * 1.2:.1f} {top + s * 1.3:.1f} {cx + s * 1.05:.1f} {top + s * 2.3:.1f}" fill="none" stroke="{base}" stroke-width="{s * 0.42:.1f}" stroke-linecap="round"/>')
    # 领口、扣子
    o.append(f'<path d="M{cx - s * 0.3:.1f} {top + s * 0.08:.1f} L{cx:.1f} {top + s * 0.45:.1f} L{cx + s * 0.3:.1f} {top + s * 0.08:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
    for k in range(4):
        o.append(f'<circle cx="{cx:.1f}" cy="{top + s * (0.7 + k * 0.42):.1f}" r="{s * 0.04:.1f}" fill="{INK}"/>')
    # 腰带
    o.append(f'<rect x="{cx - s * 0.82:.1f}" y="{top + s * 2.25:.1f}" width="{s * 1.64:.1f}" height="{s * 0.18:.1f}" fill="{INK}"/>')
    if structure:
        # 手肘内侧：从弯折点放射出去的褶
        for a in (-35, -10, 15):
            r = math.radians(a)
            o.append(fold(el[0] + s * 0.18, el[1] - s * 0.05, el[0] + s * 0.18 + math.cos(r) * s * 0.5, el[1] - s * 0.05 + math.sin(r) * s * 0.5 - s * 0.2, 0.1, 2.6, dcol))
        # 腋下往胸口斜拉的褶
        o.append(fold(cx - s * 0.8, top + s * 0.5, cx - s * 0.35, top + s * 0.9, 0.08, 2.6, dcol))
        o.append(fold(cx - s * 0.78, top + s * 0.68, cx - s * 0.4, top + s * 1.15, 0.06, 2.2, dcol))
    if messy:
        random.seed(21)
        for k in range(10):
            x0 = cx + random.uniform(-0.65, 0.6) * s
            y0 = top + random.uniform(1.75, 2.15) * s
            a = random.uniform(-0.8, 0.8)
            L = random.uniform(0.15, 0.32) * s
            o.append(fold(x0, y0, x0 + math.cos(a) * L, y0 + math.sin(a) * L, random.uniform(-0.3, 0.3), 2.2, dcol))
    if crease:
        o.append(f'<line x1="{cx - s * 0.75:.1f}" y1="{top + s * 1.25:.1f}" x2="{cx + s * 0.85:.1f}" y2="{top + s * 1.25:.1f}" stroke="{dcol}" stroke-width="2"/>')
        o.append(f'<line x1="{cx - s * 0.75:.1f}" y1="{top + s * 1.25 + 3:.1f}" x2="{cx + s * 0.85:.1f}" y2="{top + s * 1.25 + 3:.1f}" stroke="{SHIRT_L}" stroke-width="2"/>')
        o.append(f'<line x1="{cx + s * 0.45:.1f}" y1="{top + s * 0.25:.1f}" x2="{cx + s * 0.42:.1f}" y2="{top + s * 2.2:.1f}" stroke="{dcol}" stroke-width="2"/>')
        o.append(f'<line x1="{cx + s * 0.45 + 3:.1f}" y1="{top + s * 0.25:.1f}" x2="{cx + s * 0.42 + 3:.1f}" y2="{top + s * 2.2:.1f}" stroke="{SHIRT_L}" stroke-width="2"/>')
    # 头（只露下巴）
    o.append(f'<rect x="{cx - s * 0.17:.1f}" y="{top - s * 0.3:.1f}" width="{s * 0.34:.1f}" height="{s * 0.4:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
    return ''.join(o), dict(elbow=el, waist=(cx, top + s * 1.95), crease=(cx, top + s * 1.25))


def p_folds():
    Wd, Hd = 760, 330
    s = []
    titles = [('结构褶：从受力点放射，要留', MINT1), ('乱褶：堆在一起、方向乱，去掉', RED1), ('死褶：叠放压痕，笔直成格，去掉', RED1)]
    for i, (t, f) in enumerate(titles):
        ox = 20 + i * 245
        s.append(caption_box(ox, 10, 230, 310, ''))
        s.append(label(ox + 10, 44, t, f, 12))
        s.append(f'<rect x="{ox + 25}" y="70" width="180" height="230" rx="10" fill="{SHIRT}" stroke="{INK}" stroke-width="2"/>')
        cx, cy = ox + 115, 185
        if i == 0:
            s.append(f'<circle cx="{ox + 40}" cy="{cy}" r="8" fill="{VIO}" stroke="{INK}" stroke-width="2"/>')
            for a in (-40, -15, 10, 35):
                r = math.radians(a)
                s.append(fold(ox + 50, cy, ox + 50 + math.cos(r) * 130, cy + math.sin(r) * 110, 0.06, 3))
            s.append(label(ox + 30, 290, '受力点（手肘、腋下、胯）', WHITE, 11))
        elif i == 1:
            random.seed(4)
            for k in range(14):
                x0, y0 = cx + random.uniform(-70, 60), cy + random.uniform(-80, 80)
                a = random.uniform(0, 6.28); L = random.uniform(20, 45)
                s.append(fold(x0, y0, x0 + math.cos(a) * L, y0 + math.sin(a) * L, random.uniform(-.3, .3), 2.4))
        else:
            for yy in (130, 220):
                s.append(f'<line x1="{ox + 25}" y1="{yy}" x2="{ox + 205}" y2="{yy}" stroke="{SHIRT_D}" stroke-width="2.5"/><line x1="{ox + 25}" y1="{yy + 3}" x2="{ox + 205}" y2="{yy + 3}" stroke="{WHITE}" stroke-width="2.5"/>')
            s.append(f'<line x1="{cx}" y1="70" x2="{cx}" y2="300" stroke="{SHIRT_D}" stroke-width="2.5"/><line x1="{cx + 3}" y1="70" x2="{cx + 3}" y2="300" stroke="{WHITE}" stroke-width="2.5"/>')
    save('p-folds', svg(Wd, Hd, ''.join(s), '三种褶皱：结构褶留，乱褶和死褶去'))


def p_softlight():
    Wd, Hd = 760, 330
    s = [caption_box(20, 10, 720, 310, '')]
    s.append(label(36, 44, '横切一道褶，看明暗的起伏', YEL1, 14))
    x0, x1, base = 70, 690, 200
    def prof(f):
        pts = []
        for i in range(0, 101):
            t = i / 100
            pts.append((x0 + (x1 - x0) * t, base - f(t)))
        return ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts)
    raw = lambda t: 50 * math.exp(-((t - 0.42) / 0.05) ** 2) - 70 * math.exp(-((t - 0.5) / 0.05) ** 2)
    fixd = lambda t: 0.15 * raw(t)
    s.append(f'<line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{LINE}" stroke-width="2" stroke-dasharray="5 4"/>')
    s.append(f'<polyline points="{prof(raw)}" fill="none" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<polyline points="{prof(fixd)}" fill="none" stroke="{MINT7}" stroke-width="3"/>')
    s.append(text(x0, base - 70, '亮', 14, 800, MUTED)); s.append(text(x0, base + 80, '暗', 14, 800, MUTED))
    pk = x0 + (x1 - x0) * 0.42; tr = x0 + (x1 - x0) * 0.5
    s.append(arrow(pk, base - 60, pk, base - 18, INK, 2.5))
    s.append(label(pk - 210, base - 66, '亮棱：用黑色压暗', WHITE, 13))
    s.append(arrow(tr + 4, base + 80, tr + 4, base + 22, INK, 2.5))
    s.append(label(tr + 24, base + 60, '暗沟：用白色提亮', WHITE, 13))
    s.append(label(470, 140, '黑线：修之前', WHITE, 13))
    s.append(label(470, 170, '绿线：修之后，起伏变小，纹理不动', MINT1, 13))
    s.append(text(380, 306, '柔光图层：白色变亮、黑色变暗、透明处不变；只改明暗，布料的织纹留在下面的原图里', 13, 600, MUTED, 'middle'))
    save('p-softlight', svg(Wd, Hd, ''.join(s), '用柔光图层拉平一道褶皱的明暗'))


def plate(cx, cy, w, h, metal=False, seam=False, glue=False):
    """一块盔甲护板（圆角板 + 铆钉）"""
    g = uid('pl')
    if metal:
        grad = (f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E5E7EB"/><stop offset=".28" stop-color="#6B7280"/>'
                f'<stop offset=".5" stop-color="#1F2937"/><stop offset=".62" stop-color="#9CA3AF"/><stop offset=".7" stop-color="#F9FAFB"/><stop offset="1" stop-color="#374151"/></linearGradient></defs>')
    else:
        grad = (f'<defs><radialGradient id="{g}" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#E5E7EB"/><stop offset=".55" stop-color="#C3C8CF"/>'
                f'<stop offset="1" stop-color="#A3A9B3"/></radialGradient></defs>')
    o = [grad, f'<rect x="{cx - w / 2:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h * 0.25:.1f}" fill="url(#{g})" stroke="{INK}" stroke-width="3"/>']
    o.append(f'<rect x="{cx - w / 2 + 14:.1f}" y="{cy - h / 2 + 14:.1f}" width="{w - 28:.1f}" height="{h - 28:.1f}" rx="{h * 0.2:.1f}" fill="none" stroke="{INK}" stroke-opacity=".5" stroke-width="2"/>')
    if metal:
        o.append(f'<path d="M{cx - w / 2 + 16:.1f} {cy - h / 2 + 6:.1f} L{cx + w / 2 - 30:.1f} {cy - h / 2 + 6:.1f}" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>')
        o.append(f'<circle cx="{cx + w * 0.22:.1f}" cy="{cy - h * 0.12:.1f}" r="5" fill="#FFFFFF"/>')
    for sx in (-1, 1):
        for sy in (-1, 1):
            rx_, ry_ = cx + sx * (w / 2 - 26), cy + sy * (h / 2 - 26)
            o.append(f'<circle cx="{rx_:.1f}" cy="{ry_:.1f}" r="7" fill="{"#D1D5DB" if metal else "#B9BEC6"}" stroke="{INK}" stroke-width="2"/>')
            if metal:
                o.append(f'<circle cx="{rx_ - 2:.1f}" cy="{ry_ - 2:.1f}" r="2" fill="#FFF"/>')
    if seam:
        o.append(f'<path d="M{cx - w * 0.08:.1f} {cy - h / 2:.1f} L{cx - w * 0.05:.1f} {cy:.1f} L{cx - w * 0.09:.1f} {cy + h / 2:.1f}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
        o.append(f'<path d="M{cx - w * 0.08 + 4:.1f} {cy - h / 2:.1f} L{cx - w * 0.05 + 4:.1f} {cy:.1f} L{cx - w * 0.09 + 4:.1f} {cy + h / 2:.1f}" fill="none" stroke="#FFFFFF" stroke-opacity=".6" stroke-width="2"/>')
    if glue:
        for gx, gy, rr in [(-0.02, 0.2, 10), (-0.12, -0.25, 7), (0.0, -0.05, 5)]:
            o.append(f'<ellipse cx="{cx + w * gx:.1f}" cy="{cy + h * gy:.1f}" rx="{rr * 1.5}" ry="{rr}" fill="#F8FAFC" fill-opacity=".85" stroke="#CBD5E1"/>')
    return ''.join(o)


def p_material():
    Wd, Hd = 760, 350
    s = []
    for i, (t, f, m) in enumerate([('塑料：高光大而软，对比低', YEL1, False), ('金属：对比强，高光又细又亮', MINT1, True)]):
        ox = 20 + i * 370
        s.append(caption_box(ox, 10, 355, 310, ''))
        s.append(label(ox + 14, 44, t, f, 14))
        s.append(plate(ox + 178, 175, 260, 170, metal=m))
    s.append(text(380, 340, '把塑料修成金属：拉大明暗对比、降一点饱和度、沿边缘加细高光', 13, 600, MUTED, 'middle'))
    save('p-material', svg(Wd, Hd, ''.join(s), '塑料和金属的质感区别'))


def shirt_photo(x, y, w, h, **kw):
    sh, g = shirt(x + w * 0.56, y + h * 0.22, w * 0.27, **kw)
    return photo_box(x, y, w, h, sh), g


def u_gray_view():
    ph, g = shirt_photo(40, 66, 300, 340, gray=True)
    lay, P = layers2([dict(name='观察（看完删）', col='#000000', mode='颜色', sel=True),
                      dict(name='褶皱明暗', col=WHITE, mode='柔光'),
                      dict(name='修补', col=SHIRT, thumb='photo'),
                      dict(name='原图', col=SHIRT, thumb='photo', lock=True)], x=470)
    s = screen(ph + lay, active='layers')
    s += ring(*icon_pos('layers'), 18) + badge(470 + 300 - 100, 62 + 44 + 22, 1)
    s += label(470, 340, '① 新建一层，填充黑色，', YEL1, 14)
    s += label(470, 372, '　 模式改成「颜色」', YEL1, 14)
    s += label(470, 420, '画面变成黑白，褶皱的明暗', WHITE, 13)
    s += label(470, 448, '一下子看得很清楚', WHITE, 13)
    s += ui_note('示意图：实际界面里模式显示为缩写字母')
    save('u-gray-view', svg(W, H, s, '观察层：填黑色设为颜色模式，画面变成黑白'))


def u_softlight():
    ph, g = shirt_photo(40, 66, 300, 340)
    lay, P = layers2([dict(name='褶皱明暗', col=WHITE, mode='柔光', sel=True),
                      dict(name='修补', col=SHIRT, thumb='photo'),
                      dict(name='原图', col=SHIRT, thumb='photo', lock=True)], x=470)
    pop = blend_popup(470, 270, ['覆盖', '柔光', '强光'], '柔光', 1.0, 300)
    s = screen(ph + lay + pop, active='layers')
    s += ring(*icon_pos('layers'), 18) + badge(470 + 300 - 100, 62 + 44 + 22, 1)
    s += badge(456, 270 + 54 + 30 + 13, 2)
    s += label(40, 440, '① 在「修补」上面新建「褶皱明暗」层', YEL1, 13)
    s += label(40, 470, '② 模式选「柔光」，不透明度 100%（深浅靠笔刷控制）', YEL1, 13)
    s += ui_note('示意图：实际界面里模式显示为缩写字母')
    save('u-softlight', svg(W, H, s, '新建图层，混合模式选柔光'))


def u_dodge_burn():
    ph, g = shirt_photo(230, 66, 340, 340, crease=False, structure=True)
    wx, wy = g['waist']
    c = ph
    c += f'<path d="M{wx - 60:.1f} {wy - 10:.1f} q30 -8 60 0 t60 0" fill="none" stroke="#FFFFFF" stroke-width="16" stroke-opacity=".45" stroke-linecap="round"/>'
    c += f'<path d="M{wx - 50:.1f} {wy + 20:.1f} q30 -8 60 0 t50 0" fill="none" stroke="#000000" stroke-width="14" stroke-opacity=".25" stroke-linecap="round"/>'
    s = screen(c, active='brush')
    s += ring(*icon_pos('brush'), 18) + ringrect(26, 290, 26, 100, 10)
    s += badge(64, 340, 1)
    s += label(76, 410, '① 不透明度 5%～10%', YEL1, 13)
    s += label(584, 110, '「气笔修饰」›「软画笔」', YEL1, 14)
    s += label(584, 142, '尺寸和褶一样宽', YEL1, 14)
    s += label(584, 200, '② 白色：涂在暗沟里', WHITE, 14)
    s += label(584, 232, '③ 黑色：涂在鼓起的亮棱上', WHITE, 14)
    s += label(584, 280, '一笔一笔叠，宁可多涂几遍', WHITE, 13)
    s += label(584, 330, '手肘那几道结构褶不要涂', RED1, 13)
    s += badge(wx + 76, wy - 12, 2) + badge(wx + 70, wy + 22, 3)
    s += ui_note()
    save('u-dodge-burn', svg(W, H, s, '在柔光图层上，白色提亮暗沟、黑色压暗亮棱'))


def u_fabric_clone():
    # 条纹布料
    stripes = ''.join(f'<line x1="{230 + i * 14}" y1="66" x2="{230 + i * 14 - 60}" y2="406" stroke="#A5B4FC" stroke-width="4"/>' for i in range(0, 30))
    lint = strand(400, 230, 430, 250, 0.4, '#111', 1.6) + strand(330, 300, 345, 330, -0.5, '#111', 1.4)
    c = photo_box(230, 66, 340, 340, stripes + lint, bg=SHIRT)
    c += disc(340, 180) + f'<circle cx="420" cy="242" r="22" fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-dasharray="4 4"/>'
    c += arrow(355, 190, 400, 230, VIO7, 2.5, dash='5 4', marker='arwv')
    s = screen(c + tool_sliders([('画笔尺寸', 0.08), ('强度', 1.0)]), active='adjust')
    s += ring(*icon_pos('adjust'), 18) + topinfo('克隆锁定状态')
    s += badge(340, 150, 1) + badge(450, 242, 2)
    s += label(584, 120, '① 取样点和线头隔一两条纹', YEL1, 14)
    s += label(584, 152, '　 沿着条纹方向错开', YEL1, 14)
    s += label(584, 200, '② 在线头上点涂', YEL1, 14)
    s += label(584, 248, '条纹对上了，接缝就看不出来', WHITE, 13)
    s += ui_note()
    save('u-fabric-clone', svg(W, H, s, '克隆去线头：取样点沿着布料纹理的方向'))


def curves_panel(px, py, pw, phh, path_fn, pts):
    cv = panel(px, py, pw, phh, '曲线')
    gx, gy, gw, gh = px + 20, py + 46, pw - 40, phh - 66
    cv += f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="#1F2329"/>'
    for i in range(1, 4):
        cv += f'<line x1="{gx + gw * i / 4:.1f}" y1="{gy}" x2="{gx + gw * i / 4:.1f}" y2="{gy + gh}" stroke="#4B5563"/><line x1="{gx}" y1="{gy + gh * i / 4:.1f}" x2="{gx + gw}" y2="{gy + gh * i / 4:.1f}" stroke="#4B5563"/>'
    cv += f'<line x1="{gx}" y1="{gy + gh}" x2="{gx + gw}" y2="{gy}" stroke="#6B7280" stroke-dasharray="4 4"/>'
    cv += f'<path d="{path_fn(gx, gy, gw, gh)}" fill="none" stroke="{WHITE}" stroke-width="3"/>'
    for (u, v) in pts:
        cv += f'<circle cx="{gx + gw * u:.1f}" cy="{gy + gh * (1 - v):.1f}" r="7" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'
    return cv, (gx, gy, gw, gh)


def u_prop_sel():
    c = photo_box(150, 66, 380, 340, plate(340, 236, 250, 170, seam=True, glue=True), bg='#E7E5E4')
    d = f'M{340 - 128} {236 - 88} L{340 + 128} {236 - 88} L{340 + 128} {236 + 88} L{340 - 128} {236 + 88} Z'
    s = screen(c + sel_ants_path(d) + bottom_bar(SEL_ROWS, active=('手绘',), hl='拷贝并粘贴'), active='select')
    s += ring(*icon_pos('select'), 18) + badge(icon_pos('select')[0] + 26, 62, 1)
    px, py, pw, phh = POS['拷贝并粘贴']
    s += badge(px + pw / 2, py - 14, 2)
    s += label(546, 130, '① 「手绘」沿道具外轮廓', YEL1, 14)
    s += label(546, 162, '　 一点一点点出折线', YEL1, 14)
    s += label(546, 210, '② 拷贝并粘贴：道具单独一层', YEL1, 14)
    s += label(546, 258, '后面的调整只改道具，', WHITE, 13)
    s += label(546, 286, '不会碰到衣服和背景', WHITE, 13)
    s += ui_note()
    save('u-prop-sel', svg(W, H, s, '手绘选取框出道具，拷贝并粘贴到新图层'))


def u_prop_curves():
    c = photo_box(150, 66, 360, 340, plate(330, 236, 240, 160), bg='#E7E5E4')
    fn = lambda gx, gy, gw, gh: f'M{gx} {gy + gh} C{gx + gw * 0.3} {gy + gh} {gx + gw * 0.25} {gy + gh * 0.72} {gx + gw * 0.5} {gy + gh * 0.5} S{gx + gw * 0.72} {gy} {gx + gw} {gy}'
    cv, (gx, gy, gw, gh) = curves_panel(526, 110, 250, 260, fn, [(0.28, 0.2), (0.72, 0.8)])
    s = screen(c + cv, active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += badge(gx + gw * 0.28 - 22, gy + gh * 0.8, 1) + badge(gx + gw * 0.72 + 22, gy + gh * 0.2, 2)
    s += label(40, 440, '在「道具」层上：① 暗部点往下压　② 亮部点往上提，拉成 S 形，对比变强', YEL1, 13)
    s += ui_note()
    save('u-prop-curves', svg(W, H, s, '曲线拉成 S 形，加大道具的明暗对比'))


def u_prop_hl():
    c = photo_box(40, 66, 330, 340, plate(205, 236, 240, 160, metal=True), bg='#E7E5E4')
    c += f'<line x1="{205 - 104}" y1="{236 - 74}" x2="{205 + 80}" y2="{236 - 74}" stroke="{YEL}" stroke-width="2" stroke-dasharray="4 4"/>'
    lay, P = layers2([dict(name='金属高光', col=WHITE, mode='添加', clip=True, sel=True),
                      dict(name='金属暗部', col='#6B7280', mode='正片叠底', clip=True),
                      dict(name='道具', col='#C3C8CF'),
                      dict(name='修补', col='#E7E5E4', thumb='photo')], x=470)
    s = screen(c + lay, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += badge(205 - 120, 236 - 74, 1)
    s += label(470, 340, '两层都「剪辑蒙版」到「道具」上', YEL1, 13)
    s += label(470, 372, '暗部：正片叠底，压中间那条', WHITE, 13)
    s += label(470, 400, '高光：添加，技术笔沿边缘画细线', WHITE, 13)
    s += label(40, 440, '① 画到头停住，线会变直（速创形状）', YEL1, 13)
    s += ui_note('示意图：实际界面里模式显示为缩写字母')
    save('u-prop-hl', svg(W, H, s, '剪辑到道具上的暗部层和高光层'))


def case53(kind, after):
    Wd, Hd = 640, 480
    x, y, w, h = 20, 20, 600, 440
    if kind == 'shirt':
        inner, _ = shirt(x + w * 0.56, y + h * 0.24, 112, messy=not after, crease=not after, structure=True)
        s = photo_box(x, y, w, h, inner)
        lab = '修之后：腰部乱褶和压痕去掉，手肘的褶留着' if after else '修之前：腰上堆了乱褶，胸口有叠放压痕'
    elif kind == 'seam':
        s = photo_box(x, y, w, h, plate(320, 250, 380, 240, metal=False, seam=not after, glue=not after), bg='#E7E5E4')
        lab = '修之后：接缝和胶痕看不出来' if after else '修之前：护板中间一道拼接缝，旁边有胶痕'
    else:
        s = photo_box(x, y, w, h, plate(320, 250, 380, 240, metal=after), bg='#E7E5E4')
        lab = '修之后：对比拉开、边缘有细高光，像金属' if after else '修之前：灰色喷漆，一看就是塑料'
    s += label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15)
    return svg(Wd, Hd, s, lab)

if __name__ == '__main__' and 'only53' in sys.argv:
    for f in [p_folds, p_softlight, p_material, u_gray_view, u_softlight, u_dodge_burn, u_fabric_clone, u_prop_sel, u_prop_curves, u_prop_hl]:
        f()
    for k in ('shirt', 'seam', 'metal'):
        save(f'case-{k}-before', case53(k, False)); save(f'case-{k}-after', case53(k, True))
    print('ok', len(MADE))


# ================= 5.5 去路人、去灯架、改构图 =================
WALL = '#F3E8D2'; FLOOR2 = '#DCE3EC'


def passerby(x, feet, h, col='#9CA3AF'):
    hd = h * 0.13
    return (f'<rect x="{x - h * 0.13:.1f}" y="{feet - h * 0.86:.1f}" width="{h * 0.26:.1f}" height="{h * 0.5:.1f}" rx="{h * 0.08:.1f}" fill="{col}" stroke="{INK}" stroke-width="2"/>'
            f'<rect x="{x - h * 0.1:.1f}" y="{feet - h * 0.42:.1f}" width="{h * 0.08:.1f}" height="{h * 0.42:.1f}" fill="{hexmix(col, "#000000", 0.25)}" stroke="{INK}" stroke-width="1.5"/>'
            f'<rect x="{x + h * 0.02:.1f}" y="{feet - h * 0.42:.1f}" width="{h * 0.08:.1f}" height="{h * 0.42:.1f}" fill="{hexmix(col, "#000000", 0.25)}" stroke="{INK}" stroke-width="1.5"/>'
            f'<circle cx="{x:.1f}" cy="{feet - h * 0.86 - hd:.1f}" r="{hd:.1f}" fill="{hexmix(col, "#FFFFFF", 0.3)}" stroke="{INK}" stroke-width="2"/>')


def light_stand(x, feet, h):
    top = feet - h
    return (f'<line x1="{x}" y1="{top + h * 0.15:.1f}" x2="{x}" y2="{feet - h * 0.12:.1f}" stroke="{INK}" stroke-width="3"/>'
            f'<line x1="{x}" y1="{feet - h * 0.14:.1f}" x2="{x - h * 0.12:.1f}" y2="{feet:.1f}" stroke="{INK}" stroke-width="3"/>'
            f'<line x1="{x}" y1="{feet - h * 0.14:.1f}" x2="{x + h * 0.12:.1f}" y2="{feet:.1f}" stroke="{INK}" stroke-width="3"/>'
            f'<line x1="{x}" y1="{feet - h * 0.14:.1f}" x2="{x + h * 0.02:.1f}" y2="{feet + h * 0.03:.1f}" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="{x - h * 0.16:.1f}" y="{top:.1f}" width="{h * 0.32:.1f}" height="{h * 0.22:.1f}" rx="4" fill="#F8FAFC" stroke="{INK}" stroke-width="3"/>')


def con_scene(x, y, w, h, people=True, stand=True, stand_floor=False, grid=False, extend=None, horizon=0.55, fig=True):
    """漫展场照：墙、透视地砖、路人、灯架、主角。返回 svg 和几何信息"""
    hy = y + h * horizon
    vx = x + w * 0.5
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{hy - y:.1f}" fill="{WALL}"/>',
         f'<rect x="{x}" y="{hy:.1f}" width="{w}" height="{y + h - hy:.1f}" fill="{FLOOR2}"/>']
    # 展位横幅和柱子
    o.append(f'<rect x="{x + w * 0.05:.1f}" y="{y + h * 0.1:.1f}" width="{w * 0.3:.1f}" height="{h * 0.12:.1f}" fill="{VIO1}" stroke="{INK}" stroke-width="2"/>')
    o.append(f'<rect x="{x + w * 0.62:.1f}" y="{y + h * 0.1:.1f}" width="{w * 0.33:.1f}" height="{h * 0.12:.1f}" fill="{PINK1}" stroke="{INK}" stroke-width="2"/>')
    o.append(f'<rect x="{x + w * 0.42:.1f}" y="{y}" width="{w * 0.08:.1f}" height="{hy - y:.1f}" fill="#E7D9BE" stroke="{INK}" stroke-width="2"/>')
    # 地砖透视线
    lines = []
    for i in range(-8, 9):
        bx = vx + i * w * 0.16
        lines.append(f'<line x1="{vx:.1f}" y1="{hy:.1f}" x2="{bx:.1f}" y2="{y + h:.1f}" stroke="#A8B3C2" stroke-width="1.6"/>')
    for k in range(1, 7):
        t = (k / 6) ** 1.8
        yy = hy + (y + h - hy) * t
        lines.append(f'<line x1="{x}" y1="{yy:.1f}" x2="{x + w}" y2="{yy:.1f}" stroke="#A8B3C2" stroke-width="1.6"/>')
    o.append(rect_clip(x, hy, w, y + h - hy, ''.join(lines)))
    o.append(f'<line x1="{x}" y1="{hy:.1f}" x2="{x + w}" y2="{hy:.1f}" stroke="{INK}" stroke-width="2"/>')
    feet0 = hy + (y + h - hy) * 0.18
    if people:
        o.append(passerby(x + w * 0.14, feet0, h * 0.34, '#A3A3A3'))
        o.append(passerby(x + w * 0.3, feet0 + h * 0.02, h * 0.36, '#93C5FD'))
        o.append(passerby(x + w * 0.86, feet0 - h * 0.01, h * 0.33, '#FCA5A5'))
    if stand:
        o.append(light_stand(x + w * 0.72, feet0 + h * 0.03, h * 0.42))
    if stand_floor:
        o.append(light_stand(x + w * 0.24, y + h * 0.93, h * 0.55))
    if fig:
        hh = h * 0.085
        ft = y + h * 0.95
        o.append(figure(x + w * 0.56, ft - hh * 6.8, hh, ft - hh * 6.8 + hh * 3.6, ft, sw=2))
    if grid:
        o.append(f'<circle cx="{vx:.1f}" cy="{hy:.1f}" r="6" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>')
    return ''.join(o), dict(hy=hy, vx=vx, feet0=feet0)


def scene_box(x, y, w, h, **kw):
    sc, g = con_scene(x, y, w, h, **kw)
    return rect_clip(x, y, w, h, sc) + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#94A3B8"/>', g


def p_clone_repeat():
    Wd, Hd = 760, 300
    s = []
    for i, (t, f) in enumerate([('一直用同一个取样点：印章感', RED1), ('经常换取样点、换方向：看不出', MINT1)]):
        ox = 20 + i * 370
        s.append(caption_box(ox, 10, 355, 280, ''))
        s.append(label(ox + 14, 44, t, f, 14))
        s.append(f'<rect x="{ox + 20}" y="64" width="315" height="206" fill="{WALL}" stroke="{INK}" stroke-width="2"/>')
        random.seed(9)
        if i == 0:
            for k in range(4):
                cx = ox + 70 + k * 70
                for (dx, dy, r) in [(0, 0, 14), (18, 10, 7), (-12, 20, 5)]:
                    s.append(f'<circle cx="{cx + dx}" cy="{150 + dy}" r="{r}" fill="#D9C7A3"/>')
            s.append(f'<rect x="{ox + 40}" y="118" width="275" height="70" fill="none" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6 5"/>')
        else:
            for k in range(14):
                cx, cy, r = ox + random.uniform(40, 310), random.uniform(85, 255), random.uniform(4, 14)
                s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#D9C7A3"/>')
    save('p-clone-repeat', svg(Wd, Hd, ''.join(s), '克隆的印章感：同一块纹理重复出现'))


def p_persp_patch():
    Wd, Hd = 760, 320
    s = []
    for i, (t, f) in enumerate([('补丁直接贴上：地砖线断了', RED1), ('补丁按透视「扭曲」过：线接上了', MINT1)]):
        ox = 20 + i * 370
        s.append(caption_box(ox, 10, 355, 300, ''))
        s.append(label(ox + 14, 44, t, f, 14))
        x0, y0, w0, h0 = ox + 20, 64, 315, 230
        vx, vy = x0 + w0 / 2, y0 + 10
        ln = ''
        for k in range(-5, 6):
            ln += f'<line x1="{vx}" y1="{vy}" x2="{vx + k * 70}" y2="{y0 + h0}" stroke="#94A3B8" stroke-width="2"/>'
        for t2 in (0.25, 0.45, 0.7, 1.0):
            yy = vy + (y0 + h0 - vy) * t2
            ln += f'<line x1="{x0}" y1="{yy:.1f}" x2="{x0 + w0}" y2="{yy:.1f}" stroke="#94A3B8" stroke-width="2"/>'
        s.append(f'<rect x="{x0}" y="{y0}" width="{w0}" height="{h0}" fill="{FLOOR2}"/>' + rect_clip(x0, y0, w0, h0, ln))
        px, py, pw, ph_ = x0 + 30, y0 + 120, 110, 80
        if i == 0:
            patch = f'<rect x="{px}" y="{py}" width="{pw}" height="{ph_}" fill="{FLOOR2}" stroke="{RED}" stroke-width="2.5" stroke-dasharray="5 4"/>'
            for k in range(3):
                patch += f'<line x1="{px + 15 + k * 40}" y1="{py}" x2="{px + 15 + k * 40}" y2="{py + ph_}" stroke="#94A3B8" stroke-width="2"/>'
            s.append(patch)
        else:
            s.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph_}" fill="none" stroke="{MINT7}" stroke-width="2.5" stroke-dasharray="5 4"/>')
            s.append(f'<circle cx="{vx}" cy="{vy}" r="6" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>')
            s.append(label(vx + 12, vy + 22, '消失点', WHITE, 12))
    save('p-persp-patch', svg(Wd, Hd, ''.join(s), '补出来的地面要顺着透视线'))


SC = (230, 66, 340, 340)


def u_clone_big():
    ph, g = scene_box(*SC)
    x, y, w, h = SC
    c = ph + disc(x + w * 0.22, y + h * 0.3, True)
    c += f'<circle cx="{x + w * 0.3:.1f}" cy="{y + h * 0.36:.1f}" r="26" fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-dasharray="4 4"/>'
    s = screen(c + tool_sliders([('画笔尺寸', 0.35), ('强度', 1.0)]), active='adjust')
    s += ring(*icon_pos('adjust'), 18) + topinfo('克隆锁定状态')
    s += badge(x + w * 0.22, y + h * 0.3 - 30, 1) + badge(x + w * 0.3 + 34, y + h * 0.36 - 20, 2)
    s += label(584, 120, '① 取样点放在同一面墙上', YEL1, 14)
    s += label(584, 152, '　 高度和要补的地方一样', YEL1, 14)
    s += label(584, 200, '② 从路人的外缘往里涂', YEL1, 14)
    s += label(584, 248, '涂一小块就换一次取样点', WHITE, 13)
    s += label(584, 276, '墙和地面的交界线要先补齐', WHITE, 13)
    s += ui_note()
    save('u-clone-big', svg(W, H, s, '大面积克隆：取样点放在同一面墙、同一高度'))


def u_patch_copy():
    ph, g = scene_box(*SC, people=False)
    x, y, w, h = SC
    d = f'M{x + w * 0.05} {y + h * 0.25} L{x + w * 0.38} {y + h * 0.25} L{x + w * 0.38} {g["hy"] + 20} L{x + w * 0.05} {g["hy"] + 20} Z'
    bar_items = ['剪切', '拷贝', '全部拷贝', '复制', '剪切并粘贴', '粘贴']
    bx = 170; by = 100; s_bar = f'<rect x="{bx}" y="{by}" width="460" height="46" rx="12" fill="{UIBAR}"/>'
    xx = bx + 10; hx = 0
    for it in bar_items:
        ww = len(it) * 15 + 20
        s_bar += f'<rect x="{xx}" y="{by + 7}" width="{ww}" height="32" rx="8" fill="{UIPANEL}"/>' + text(xx + ww / 2, by + 29, it, 14, 700, UITEXT, 'middle')
        if it == '复制':
            s_bar += ringrect(xx - 3, by + 4, ww + 6, 38); hx = xx + ww / 2
        xx += ww + 6
    s = screen(ph + sel_ants_path(d) + s_bar + finger(680, 250, 3, 40), active='select')
    s += badge(hx, by + 62, 2) + badge(628, 242, 1)
    s += label(584, 330, '① 三指往下拖', YEL1, 14)
    s += label(584, 362, '② 点「复制」', YEL1, 14)
    s += label(584, 410, '框的是一块干净的墙和地面', WHITE, 13)
    s += ui_note()
    save('u-patch-copy', svg(W, H, s, '矩形框一块干净的背景，三指下拖点复制'))


def u_patch_move():
    ph, g = scene_box(*SC)
    x, y, w, h = SC
    bx_, by_, bw, bh = x + w * 0.72, y + h * 0.25, w * 0.28, g['hy'] + 20 - (y + h * 0.25)
    s = screen(ph + f'<rect x="{bx_:.1f}" y="{by_:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{WALL}" fill-opacity=".85"/>' + bbox(bx_, by_, bw, bh) + bottom_bar(TF_ROWS, active=('自由变换',), hl='水平翻转'), active='transform')
    s += ring(*icon_pos('transform'), 18)
    s += badge(bx_ - 16, by_ + bh / 2, 1)
    s += badge(POS['水平翻转'][0] + POS['水平翻转'][2] / 2, POS['水平翻转'][1] - 14, 2)
    s += label(584, 120, '① 拖到要盖住的路人上', YEL1, 14)
    s += label(584, 152, '　 墙脚线和原图对齐', YEL1, 14)
    s += label(584, 200, '② 「水平翻转」一次', YEL1, 14)
    s += label(584, 248, '翻过来以后不容易看出', WHITE, 13)
    s += label(584, 276, '是同一块墙复制的', WHITE, 13)
    s += ui_note()
    save('u-patch-move', svg(W, H, s, '把复制出的背景块挪过去盖住干扰物，水平翻转一次'))


def u_patch_mask():
    ph, g = scene_box(40, 66, 300, 340)
    lay, P = layers2([dict(name='图层蒙版', mask=True, sel=True, mode='N'),
                      dict(name='补丁（墙）', col=WALL),
                      dict(name='修补', col=WALL, thumb='photo'),
                      dict(name='原图', col=WALL, thumb='photo', lock=True)], x=470)
    s = screen(ph + f'<path d="M260 140 q20 40 0 90" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="18" stroke-linecap="round"/>' + lay, active='layers')
    s += ring(*icon_pos('layers'), 18) + badge(470 + 22 + 20, 62 + 44 + 22, 1)
    s += label(470, 340, '① 「补丁」层轻点两次 › 「蒙版」', YEL1, 13)
    s += label(470, 372, '② 选中蒙版，用黑色软画笔', YEL1, 13)
    s += label(470, 400, '　 擦补丁的边，让它融进去', YEL1, 13)
    s += label(470, 440, '擦多了用白色涂回来', WHITE, 13)
    s += badge(290, 120, 2)
    s += ui_note('示意图：实际界面里模式显示为缩写字母')
    save('u-patch-mask', svg(W, H, s, '给补丁图层加蒙版，用黑色软画笔把边缘融进去'))


def u_crop_extend():
    x, y, w, h = 300, 120, 220, 280
    ph, g = scene_box(x, y, w, h)
    ex, ey, ew, eh = x - 70, y - 50, w + 70, h + 50
    c = f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" fill="{WHITE}"/>' + ph
    c += f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" fill="none" stroke="{WHITE}" stroke-width="3"/>'
    for i in (1, 2):
        c += f'<line x1="{ex + ew * i / 3:.1f}" y1="{ey}" x2="{ex + ew * i / 3:.1f}" y2="{ey + eh}" stroke="{WHITE}" stroke-width="1.2"/><line x1="{ex}" y1="{ey + eh * i / 3:.1f}" x2="{ex + ew}" y2="{ey + eh * i / 3:.1f}" stroke="{WHITE}" stroke-width="1.2"/>'
    c += f'<rect x="{ex}" y="{ey}" width="{ew}" height="{eh}" fill="none" stroke="{INK}" stroke-width="1.5" stroke-dasharray="6 5"/>'
    bar = f'<rect x="220" y="470" width="360" height="56" rx="12" fill="{UIBAR}"/>' + text(240, 504, '宽 3500 px', 15, 700, UITEXT) + text(400, 504, '🔗', 14, 400, UITEXT, 'middle') + text(560, 504, '高 4300 px', 15, 700, UITEXT, 'end')
    bar = bar.replace(text(400, 504, '🔗', 14, 400, UITEXT, 'middle'), f'<rect x="392" y="492" width="16" height="16" rx="4" fill="none" stroke="{UITEXT}" stroke-width="2"/>')
    s = screen(c + bar, active='actions')
    s += arrow(x - 6, y + h / 2, ex + 4, y + h / 2, INK, 3) + arrow(x + w / 2, y - 6, x + w / 2, ey + 4, INK, 3)
    s += badge(ex - 18, y + h / 2, 1) + badge(x + w / 2 + 24, ey - 6, 2)
    s += label(584, 150, '① 往左拖网格的左边', YEL1, 14)
    s += label(584, 182, '② 往上拖上边', YEL1, 14)
    s += label(584, 230, '多出来的地方是空白，', WHITE, 13)
    s += label(584, 258, '下一步用原图里的内容补', WHITE, 13)
    s += label(584, 306, '宽高数字会跟着变', WHITE, 13)
    s += ui_note('示意图：操作 › 画布 › 裁剪并调整大小')
    save('u-crop-extend', svg(W, H, s, '裁剪并调整大小：把网格往外拖，画布变大'))


def u_persp_guide():
    ph, g = scene_box(*SC, grid=True)
    x, y, w, h = SC
    vx, hy = g['vx'], g['hy']
    gl = ''
    for k in range(-6, 7):
        gl += f'<line x1="{vx:.1f}" y1="{hy:.1f}" x2="{vx + k * 70:.1f}" y2="{y + h + 200:.1f}" stroke="{UIBLUE}" stroke-width="1.5" stroke-opacity=".9"/>'
    gl = rect_clip(x, y, w, h, gl)
    gl += f'<line x1="{x}" y1="{hy:.1f}" x2="{x + w}" y2="{hy:.1f}" stroke="{UIBLUE}" stroke-width="2"/>'
    bar = bottom_bar([['2D 网格', '等距', '透视', '对称']], active=('透视',), hl='透视')
    s = screen(ph + gl + f'<circle cx="{vx:.1f}" cy="{hy:.1f}" r="8" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>' + bar, active='actions')
    s += badge(vx + 22, hy - 18, 1) + badge(POS['透视'][0] + POS['透视'][2] / 2, POS['透视'][1] - 14, 2)
    s += label(584, 120, '② 底部选「透视」', YEL1, 14)
    s += label(584, 152, '① 在地砖线延长的交点', YEL1, 14)
    s += label(584, 184, '　 轻点，放一个透视点', YEL1, 14)
    s += label(584, 232, '蓝线和地砖缝重合就对了', WHITE, 13)
    s += label(584, 260, '点「完成」后蓝线留在画面上', WHITE, 13)
    s += ui_note('示意图：操作 › 画布 › 编辑绘图指引')
    save('u-persp-guide', svg(W, H, s, '编辑绘图指引：透视，透视点放在地砖线的交点'))


def u_distort():
    ph, g = scene_box(*SC, people=False, stand=False)
    x, y, w, h = SC
    vx, hy = g['vx'], g['hy']
    p1 = (x + w * 0.05, y + h * 0.78); p2 = (x + w * 0.32, y + h * 0.78)
    p3 = (x + w * 0.36, y + h * 0.99); p4 = (x + w * 0.0, y + h * 0.99)
    q = f'M{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} L{p3[0]:.1f} {p3[1]:.1f} L{p4[0]:.1f} {p4[1]:.1f} Z'
    c = ph + f'<path d="{q}" fill="{FLOOR2}" fill-opacity=".6" stroke="{UIBLUE}" stroke-width="2"/>'
    for p in (p1, p2, p3, p4):
        c += f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="6" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
    for p in (p1, p2):
        c += f'<line x1="{vx:.1f}" y1="{hy:.1f}" x2="{p[0]:.1f}" y2="{p[1]:.1f}" stroke="{YEL}" stroke-width="2" stroke-dasharray="5 4"/>'
    s = screen(c + bottom_bar(TF_ROWS, active=('扭曲',)), active='transform')
    s += ring(*icon_pos('transform'), 18)
    s += badge(p2[0] + 18, p2[1] - 14, 1)
    s += label(584, 140, '① 「扭曲」：一个角一个角拖', YEL1, 14)
    s += label(584, 172, '　 让补丁的边对准透视线', YEL1, 14)
    s += label(584, 220, '近处（下面）宽，远处窄', WHITE, 13)
    s += label(584, 248, '地砖缝和旁边的接上为止', WHITE, 13)
    s += ui_note()
    save('u-distort', svg(W, H, s, '变换选扭曲，让补丁顺着透视线'))


def case55(kind, after):
    Wd, Hd = 640, 480
    if kind == 'crowd':
        ph, _ = scene_box(20, 20, 600, 440, people=not after, stand=not after)
        lab = '修之后：三个路人和灯架都去掉了' if after else '修之前：背后有三个路人和一个灯架'
    elif kind == 'floor':
        ph, _ = scene_box(20, 20, 600, 440, people=False, stand=False, stand_floor=not after)
        lab = '修之后：灯架去掉，地砖线连续' if after else '修之前：灯架脚踩在地砖上，压着好几条地砖缝'
    else:
        if after:
            ph, _ = scene_box(20, 20, 600, 440, people=False, stand=False)
            ph += f'<rect x="20" y="20" width="600" height="440" fill="none"/><rect x="150" y="20" width="470" height="70" fill="none" stroke="{VIO7}" stroke-width="2.5" stroke-dasharray="7 6"/>'
            ph += f'<rect x="20" y="20" width="130" height="440" fill="none" stroke="{VIO7}" stroke-width="2.5" stroke-dasharray="7 6"/>'
        else:
            inner, _ = scene_box(150, 90, 470, 370, people=False, stand=False)
            ph = f'<rect x="20" y="20" width="600" height="440" fill="{CREAM}"/>' + inner
        lab = '修之后：画布往左、往上扩，补出背景，有了留白' if after else '修之前：人物顶天立地，四周没有留白'
    s = ph + (label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15))
    return svg(Wd, Hd, s, lab)

if __name__ == '__main__' and 'only55' in sys.argv:
    for f in [p_clone_repeat, p_persp_patch, u_clone_big, u_patch_copy, u_patch_move, u_patch_mask, u_crop_extend, u_persp_guide, u_distort]:
        f()
    for k in ('crowd', 'floor', 'extend'):
        save(f'case-{k}-before', case55(k, False)); save(f'case-{k}-after', case55(k, True))
    print('ok', len(MADE))


# ================= 5.6 按角色设定还原颜色 =================
TARGET_PINK = '#F472B6'      # 设定发色
PHOTO_PINK = '#F59E8B'       # 实物偏橘
TARGET_SILVER = '#DCE4F0'; PHOTO_SILVER = '#E8DEC6'


def swatch_strip(x, y, cols, names, size=46, title=None):
    s = ''
    if title:
        s += text(x, y - 10, title, 13, 800, INK)
    for i, (c, n) in enumerate(zip(cols, names)):
        s += f'<rect x="{x + i * (size + 10)}" y="{y}" width="{size}" height="{size}" rx="8" fill="{c}" stroke="{INK}" stroke-width="2"/>'
        s += text(x + i * (size + 10) + size / 2, y + size + 16, n, 11, 700, MUTED, 'middle')
    return s


def ref_sheet(x, y, w, h, hair=TARGET_PINK, cloth='#7C3AED'):
    """简笔的角色设定图：平涂 + 一层阴影色"""
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'
    cx = x + w / 2; t = y + h * 0.12; u = h * 0.1
    sh = hexmix(hair, '#4C1D95', 0.35)
    s += f'<path d="M{cx - u * 1.3:.1f} {t + u * 0.6:.1f} Q{cx:.1f} {t - u * 0.9:.1f} {cx + u * 1.3:.1f} {t + u * 0.6:.1f} L{cx + u * 1.2:.1f} {t + u * 3.2:.1f} L{cx - u * 1.2:.1f} {t + u * 3.2:.1f} Z" fill="{hair}" stroke="{INK}" stroke-width="2"/>'
    s += f'<path d="M{cx + u * 0.3:.1f} {t + u * 0.2:.1f} Q{cx + u * 1.3:.1f} {t + u * 0.6:.1f} {cx + u * 1.2:.1f} {t + u * 3.2:.1f} L{cx + u * 0.7:.1f} {t + u * 3.2:.1f} Z" fill="{sh}"/>'
    s += f'<ellipse cx="{cx:.1f}" cy="{t + u * 1.4:.1f}" rx="{u * 0.75:.1f}" ry="{u * 0.95:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>'
    s += f'<path d="M{cx - u * 0.9:.1f} {t + u * 0.9:.1f} Q{cx:.1f} {t - u * 0.2:.1f} {cx + u * 0.9:.1f} {t + u * 0.9:.1f} L{cx + u * 0.5:.1f} {t + u * 0.5:.1f} L{cx:.1f} {t + u * 0.9:.1f} L{cx - u * 0.5:.1f} {t + u * 0.5:.1f} Z" fill="{hair}" stroke="{INK}" stroke-width="2"/>'
    s += f'<path d="M{cx - u * 1.1:.1f} {t + u * 2.6:.1f} L{cx + u * 1.1:.1f} {t + u * 2.6:.1f} L{cx + u * 1.4:.1f} {t + u * 6.5:.1f} L{cx - u * 1.4:.1f} {t + u * 6.5:.1f} Z" fill="{cloth}" stroke="{INK}" stroke-width="2"/>'
    s += f'<path d="M{cx + u * 0.4:.1f} {t + u * 2.6:.1f} L{cx + u * 1.1:.1f} {t + u * 2.6:.1f} L{cx + u * 1.4:.1f} {t + u * 6.5:.1f} L{cx + u * 0.8:.1f} {t + u * 6.5:.1f} Z" fill="{hexmix(cloth, "#1E1B4B", 0.4)}"/>'
    s += text(x + 8, y + h - 8, '设定图', 12, 800, MUTED)
    return s


def p_local_color():
    Wd, Hd = 760, 340
    s = [caption_box(20, 10, 720, 320, '')]
    s.append(label(36, 44, '设定图上的颜色 = 固有色；照片上的颜色 = 固有色 + 光', YEL1, 14))
    s.append(ref_sheet(40, 66, 180, 250))
    s.append(swatch_strip(240, 110, [TARGET_PINK, hexmix(TARGET_PINK, '#4C1D95', 0.35)], ['底色', '阴影色'], title='设定色卡'))
    # 照片里的假发：一条从亮到暗的渐变
    g = uid('lg')
    lit = [hexmix(PHOTO_PINK, '#FFFFFF', 0.55), PHOTO_PINK, hexmix(PHOTO_PINK, '#3B0764', 0.5)]
    s.append(f'<defs><linearGradient id="{g}" x1="0" x2="1"><stop offset="0" stop-color="{lit[0]}"/><stop offset=".5" stop-color="{lit[1]}"/><stop offset="1" stop-color="{lit[2]}"/></linearGradient></defs>')
    s.append(text(240, 215, '照片里的同一顶假发', 13, 800, INK))
    s.append(f'<rect x="240" y="225" width="480" height="40" rx="8" fill="url(#{g})" stroke="{INK}" stroke-width="2"/>')
    for i, (t, xx) in enumerate([('高光：发白，别拿来比', 260), ('灰面：拿这里和底色比', 440), ('暗部：和阴影色比', 620)]):
        s.append(f'<line x1="{xx + 20}" y1="265" x2="{xx + 20}" y2="282" stroke="{INK}" stroke-width="2"/>')
        s.append(label(xx - 30, 304, t, MINT1 if i == 1 else WHITE, 12))
    s.append(f'<rect x="458" y="229" width="44" height="32" rx="6" fill="none" stroke="{YEL}" stroke-width="4"/>')
    s.append(arrow(400, 140, 470, 222, VIO7, 2.5, '6 5', 'arwv'))
    save('p-local-color', svg(Wd, Hd, ''.join(s), '设定色是固有色，要和照片的灰面比'))


def p_color_mode_hair():
    Wd, Hd = 760, 300
    s = [caption_box(20, 10, 720, 280, '')]
    s.append(label(36, 44, '「颜色」模式：换色相和饱和度，明暗不变', YEL1, 14))
    rows = [('实物偏橘的粉', PHOTO_PINK, TARGET_PINK), ('实物偏黄的银白', PHOTO_SILVER, TARGET_SILVER)]
    for i, (n, base, tgt) in enumerate(rows):
        yy = 80 + i * 100
        s.append(text(40, yy + 34, n, 13, 700))
        res = blend_color(base, tgt)
        for k, (c, t) in enumerate([(base, '原来'), (tgt, '叠一层设定色（颜色模式）'), (res, '结果')]):
            xx = 180 + k * 150
            s.append(f'<rect x="{xx}" y="{yy}" width="70" height="56" rx="8" fill="{c}" stroke="{INK}" stroke-width="2"/>')
            s.append(text(xx + 35, yy + 76, t, 11, 700, MUTED, 'middle'))
            if k < 2:
                s.append(text(xx + 110, yy + 36, '→' if k == 1 else '+', 22, 800, INK, 'middle'))
    s.append(label(566, 116, '粉色：基本对了', MINT1, 12))
    s.append(label(566, 216, '银白：偏差主要在饱和度，', YEL1, 12))
    s.append(label(566, 244, '要配合降饱和、调亮度', YEL1, 12))
    save('p-color-mode-hair', svg(Wd, Hd, ''.join(s), '颜色模式只换色相和饱和度，亮度要另外调'))


def p_gradient_map():
    Wd, Hd = 760, 300
    s = [caption_box(20, 10, 720, 280, '')]
    s.append(label(36, 44, '渐变映射：按亮度把颜色换掉', YEL1, 14))
    g1, g2 = uid('lg'), uid('lg')
    s.append(f'<defs><linearGradient id="{g1}" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#FFF"/></linearGradient>'
             f'<linearGradient id="{g2}" x1="0" x2="1"><stop offset="0" stop-color="#1E1B4B"/><stop offset=".5" stop-color="#3B82F6"/><stop offset="1" stop-color="#E0F2FE"/></linearGradient></defs>')
    s.append(text(60, 100, '照片的亮度', 13, 800))
    s.append(f'<rect x="180" y="80" width="520" height="34" rx="6" fill="url(#{g1})" stroke="{INK}" stroke-width="2"/>')
    for k in range(5):
        xx = 200 + k * 120
        s.append(arrow(xx, 120, xx, 160, INK, 2))
    s.append(text(60, 190, '换成的颜色', 13, 800))
    s.append(f'<rect x="180" y="168" width="520" height="34" rx="6" fill="url(#{g2})" stroke="{INK}" stroke-width="2"/>')
    s.append(text(180, 232, '最暗的地方 → 左端颜色', 12, 700, MUTED))
    s.append(text(700, 232, '最亮的地方 → 右端颜色', 12, 700, MUTED, 'end'))
    s.append(text(380, 266, '整张图被换成一套配色，再降低不透明度或换成柔光模式叠回去，就是"统一氛围"', 13, 600, MUTED, 'middle'))
    save('p-gradient-map', svg(Wd, Hd, ''.join(s), '渐变映射按亮度把颜色换成渐变里的颜色'))


def color_panel(x, y, w, tab, inner_h=200):
    tabs = ['色盘', '经典', '色彩调和', '值', '调色板']
    h = inner_h + 90
    s = panel(x, y, w, h) + text(x + 16, y + 28, '颜色', 16, 800, UITEXT)
    s += f'<rect x="{x + w - 70}" y="{y + 12}" width="54" height="22" rx="4" fill="{TARGET_PINK}"/>'
    tx = x + 10
    ty = y + h - 40
    for t in tabs:
        tw = len(t) * 13 + 16
        s += f'<rect x="{tx}" y="{ty}" width="{tw}" height="28" rx="8" fill="{UIBLUE if t == tab else UIBAR}"/>' + text(tx + tw / 2, ty + 19, t, 13, 700, UITEXT, 'middle')
        POS['tab_' + t] = (tx, ty, tw, 28)
        tx += tw + 4
    return s


def u_ref_pick():
    ph = bangs_photo(60, 66, 300, 340, wig=PHOTO_PINK, wig_d=hexmix(PHOTO_PINK, '#7F1D1D', 0.35), wig_l=hexmix(PHOTO_PINK, '#FFFFFF', 0.5))
    rx, ry, rw, rh = 400, 80, 260, 300
    win = panel(rx, ry, rw, rh) + f'<rect x="{rx + rw / 2 - 20}" y="{ry + 6}" width="40" height="5" rx="2" fill="{UIDIM}"/>'
    win += ref_sheet(rx + 40, ry + 22, 180, 220)
    for i, t in enumerate(['画布', '图像', '面容']):
        bx = rx + 20 + i * 76
        win += f'<rect x="{bx}" y="{ry + rh - 42}" width="68" height="28" rx="8" fill="{UIBLUE if t == "图像" else UIBAR}"/>' + text(bx + 34, ry + rh - 23, t, 13, 700, UITEXT, 'middle')
    win += eyedropper(rx + 40 + 90 - 40, ry + 22 + 70, TARGET_PINK, PHOTO_PINK, 26)
    s = screen(ph + win, active='actions')
    s += badge(rx + 20 + 76 + 34, ry + rh - 56, 1) + badge(rx + 90 + 30, ry + 92 - 30, 2)
    s += label(400, 420, '① 「参考」窗口切到「图像」，导入设定图', YEL1, 13)
    s += label(400, 450, '② 在窗口里长按设定图的头发，吸管取色', YEL1, 13)
    s += ui_note('示意图：操作 › 画布 › 参考')
    save('u-ref-pick', svg(W, H, s, '参考窗口的图像模式：在设定图上长按取色'))


def u_palette_add():
    ph = bangs_photo(60, 66, 300, 340, wig=PHOTO_PINK, wig_d=hexmix(PHOTO_PINK, '#7F1D1D', 0.35), wig_l=hexmix(PHOTO_PINK, '#FFFFFF', 0.5))
    cp = color_panel(400, 62, 370, '调色板', 260)
    cp += text(750, 112, '+', 26, 700, UITEXT, 'middle')
    cp += ring(750, 104, 16)
    menu = popup(520, 124, 230, ['新建调色板', '从“相机”新增', '从“文件”新增', '从“相片”新增'], '从“相片”新增')
    for r in range(2):
        for k in range(10):
            cp += f'<rect x="{416 + k * 34}" y="{290 + r * 34}" width="28" height="28" rx="4" fill="{["#F472B6", "#7C3AED", "#FDE2CF", "#1E293B"][k] if (r == 0 and k < 4) else "#4B5563"}"/>'
    s = screen(ph + cp + menu, active='color')
    s += ring(*icon_pos('color'), 16)
    s += badge(POS['tab_调色板'][0] + POS['tab_调色板'][2] / 2, POS['tab_调色板'][1] - 14, 1) + badge(726, 104, 2) + badge(506, 124 + 40 + 3 * 34 - 17 + 8, 3)
    s += label(60, 440, '① 颜色面板底部点「调色板」　② 点右上角「+」', YEL1, 13)
    s += label(60, 470, '③ 「从“相片”新增」，选设定图：自动生成一组色卡', YEL1, 13)
    s += ui_note('示意图，菜单文字以实际界面为准')
    save('u-palette-add', svg(W, H, s, '调色板右上角的加号：从相片新增'))


def u_value_hex():
    ph = bangs_photo(60, 66, 300, 340, wig=PHOTO_PINK, wig_d=hexmix(PHOTO_PINK, '#7F1D1D', 0.35), wig_l=hexmix(PHOTO_PINK, '#FFFFFF', 0.5))
    cp = color_panel(400, 62, 370, '值', 260)
    for i, (n, v) in enumerate([('色相', 0.92), ('饱和度', 0.53), ('亮度', 0.96)]):
        yy = 112 + i * 46
        cp += text(416, yy, n, 13, 700, UITEXT) + f'<rect x="480" y="{yy - 10}" width="190" height="10" rx="5" fill="#6B7280"/><circle cx="{480 + 190 * v:.1f}" cy="{yy - 5}" r="9" fill="{WHITE}" stroke="{INK}"/>'
        cp += text(752, yy, f'{int(v * (360 if n == "色相" else 100))}', 13, 700, UITEXT, 'end')
    cp += text(416, 262, '十六进制', 13, 700, UITEXT) + f'<rect x="520" y="244" width="150" height="28" rx="6" fill="{UIBAR}"/>' + text(534, 263, '#F472B6', 14, 800, WHITE)
    cp += ringrect(512, 240, 166, 36)
    for k in range(10):
        cp += f'<rect x="{416 + k * 34}" y="296" width="28" height="28" rx="4" fill="{TARGET_PINK if k == 0 else ("#4B5563" if k > 1 else "#4B5563")}"/>'
    cp += ringrect(446, 292, 36, 36, 6)
    s = screen(ph + cp, active='color')
    s += ring(*icon_pos('color'), 16)
    s += badge(POS['tab_值'][0] + POS['tab_值'][2] / 2, POS['tab_值'][1] - 14, 1) + badge(694, 258, 2) + badge(464, 342, 3)
    s += label(60, 440, '① 「值」里能看到色相、饱和度、亮度的数字　② 十六进制色码，记到笔记里', YEL1, 13)
    s += label(60, 470, '③ 轻点底部调色板的空格子，把当前颜色存成色卡', YEL1, 13)
    s += ui_note()
    save('u-value-hex', svg(W, H, s, '颜色面板的值：读数字、记色码，轻点空色卡保存'))


def u_wig_fill():
    ph = bangs_photo(40, 66, 240, 300, wig=PHOTO_PINK, wig_d=hexmix(PHOTO_PINK, '#7F1D1D', 0.35), wig_l=hexmix(PHOTO_PINK, '#FFFFFF', 0.5))
    lay, P = layers2([dict(name='发色', col=TARGET_PINK, mode='颜色', clip=True, sel=True),
                      dict(name='假发', col=PHOTO_PINK),
                      dict(name='修补', col='#FFF7E6', thumb='photo'),
                      dict(name='原图', col='#FFF7E6', thumb='photo', lock=True)], x=470)
    opts = layer_options(290, 62, '填充图层')
    s = screen(ph + lay + opts, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += badge(470 + 22 + 20, 62 + 44 + 22, 1) + badge(276, 62 + 4 + 3 * 30 + 15, 2)
    s += label(40, 488, '① 在「假发」上新建「发色」层，设成剪辑蒙版，模式选「颜色」', YEL1, 13)
    s += label(40, 518, '② 当前颜色选设定色卡里的底色，打开图层选项点「填充图层」', YEL1, 13)
    s += ui_note('示意图：实际界面里模式显示为缩写字母')
    save('u-wig-fill', svg(W, H, s, '发色层：剪辑到假发上，颜色模式，填充设定色'))


def u_hsb():
    ph = bangs_photo(230, 66, 340, 340, wig=TARGET_SILVER, wig_d='#8EA0BA', wig_l='#FFFFFF')
    s = screen(ph + tool_sliders([('色相', 0.5), ('饱和度', 0.35), ('亮度', 0.58)]), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += label(584, 120, '在「假发」层上：', YEL1, 14)
    s += label(584, 152, '饱和度往左：去掉发黄', YEL1, 14)
    s += label(584, 184, '亮度往右一点：更像银白', YEL1, 14)
    s += label(584, 232, '色相不动（交给发色层）', WHITE, 13)
    s += label(584, 260, '50% 是不变的位置', WHITE, 13)
    s += ui_note('示意图：调整 › 色相、饱和度、亮度')
    save('u-hsb', svg(W, H, s, '色相、饱和度、亮度：降饱和、略提亮'))


def u_copy_all():
    ph = bangs_photo(230, 66, 340, 340, wig=TARGET_PINK, wig_d=hexmix(TARGET_PINK, '#4C1D95', 0.35), wig_l='#FDE7F3')
    bar_items = ['剪切', '拷贝', '全部拷贝', '复制', '剪切并粘贴', '粘贴']
    bx = 170; by = 64; s_bar = f'<rect x="{bx}" y="{by}" width="460" height="46" rx="12" fill="{UIBAR}"/>'
    xx = bx + 10; P_ = {}
    for it in bar_items:
        ww = len(it) * 15 + 20
        s_bar += f'<rect x="{xx}" y="{by + 7}" width="{ww}" height="32" rx="8" fill="{UIPANEL}"/>' + text(xx + ww / 2, by + 29, it, 14, 700, UITEXT, 'middle')
        P_[it] = xx + ww / 2
        if it in ('全部拷贝', '粘贴'):
            s_bar += ringrect(xx - 3, by + 4, ww + 6, 38)
        xx += ww + 6
    s = screen(ph + s_bar + finger(680, 250, 3, 40))
    s += badge(P_['全部拷贝'], by + 62, 1) + badge(P_['粘贴'], by + 62, 2)
    s += label(584, 330, '① 「全部拷贝」：所有可见', YEL1, 14)
    s += label(584, 362, '　 图层合成一张拷走', YEL1, 14)
    s += label(584, 394, '② 再三指下拖点「粘贴」', YEL1, 14)
    s += label(584, 440, '得到一层合并好的副本', WHITE, 13)
    s += ui_note()
    save('u-copy-all', svg(W, H, s, '三指下拖：全部拷贝，再粘贴成一层合并副本'))


PRESETS = ['神秘', '微风', '瞬间', '威尼斯', '火焰', '霓虹灯', '黑暗', '摩卡']
PRESET_COLS = [('#1E1B4B', '#C084FC'), ('#0F172A', '#7DD3FC'), ('#422006', '#FDE68A'), ('#1E3A8A', '#FBCFE8'),
               ('#450A0A', '#FDBA74'), ('#2E1065', '#22D3EE'), ('#000000', '#9CA3AF'), ('#292524', '#E7C9A9')]


def gradient_lib(x, y, w, hl=None):
    s = panel(x, y, w, 132) + text(x + 16, y + 26, '渐变色库', 15, 800, UITEXT) + text(x + w - 22, y + 28, '+', 24, 700, UITEXT, 'middle')
    cw = (w - 20 - 7 * 8) / 8
    for i, (n, (a, b)) in enumerate(zip(PRESETS, PRESET_COLS)):
        g = uid('lg')
        xx = x + 10 + i * (cw + 8)
        s += f'<defs><linearGradient id="{g}" x1="0" x2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient></defs>'
        s += f'<rect x="{xx:.1f}" y="{y + 42}" width="{cw:.1f}" height="50" rx="6" fill="url(#{g})"/>' + text(xx + cw / 2, y + 112, n, 12, 700, UITEXT, 'middle')
        if n == hl:
            s += ringrect(xx - 3, y + 39, cw + 6, 56, 8)
    return s


def u_gradient_lib():
    ph = bangs_photo(230, 66, 340, 340, wig=TARGET_PINK, wig_d=hexmix(TARGET_PINK, '#4C1D95', 0.35), wig_l='#FDE7F3')
    s = screen(ph + gradient_lib(60, 400, 680), active='adjust')
    s += ring(*icon_pos('adjust'), 18) + ring(718, 426, 16)
    s += badge(696, 426, 1)
    s += label(584, 120, '调整 › 渐变映射', YEL1, 14)
    s += label(584, 152, '下面八个是自带的渐变', WHITE, 13)
    s += label(584, 180, '左右滑动可以挨个预览', WHITE, 13)
    s += label(584, 228, '① 点「+」新建自己的渐变', YEL1, 14)
    s += ui_note('示意图：渐变的颜色只是示意')
    save('u-gradient-lib', svg(W, H, s, '渐变映射的渐变色库，加号新建自定义渐变'))


def u_gradient_edit():
    ph = bangs_photo(230, 66, 340, 300, wig=TARGET_PINK, wig_d=hexmix(TARGET_PINK, '#4C1D95', 0.35), wig_l='#FDE7F3')
    x, y, w = 60, 380, 680
    g = uid('lg')
    stops = [(0.0, '#1E1B4B'), (0.5, '#6366F1'), (1.0, '#E0F2FE')]
    ed = panel(x, y, w, 150) + text(x + 16, y + 26, '冷色氛围', 15, 800, UITEXT) + text(x + w - 16, y + 26, '完成', 15, 800, UIBLUE, 'end')
    ed += f'<defs><linearGradient id="{g}" x1="0" x2="1">' + ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops) + '</linearGradient></defs>'
    ed += f'<rect x="{x + 20}" y="{y + 50}" width="{w - 40}" height="40" rx="6" fill="url(#{g})" stroke="#111"/>'
    for o, c in stops:
        px = x + 20 + (w - 40) * o
        ed += f'<path d="M{px:.1f} {y + 92} l-10 16 h20 z" fill="{c}" stroke="{WHITE}" stroke-width="2"/>'
    ed += text(x + 20, y + 132, '左端：暗部换成的颜色', 12, 700, UIDIM) + text(x + w - 20, y + 132, '右端：亮部换成的颜色', 12, 700, UIDIM, 'end')
    s = screen(ph + ed, active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += badge(x + 20 + (w - 40) * 0.5, y + 124, 1) + badge(x + 20 + (w - 40) * 0.75, y + 72, 2)
    s += label(584, 110, '① 轻点色点：换这个位置的颜色', YEL1, 13)
    s += label(584, 140, '② 轻点渐变条的空处：加色点', YEL1, 13)
    s += label(584, 170, '长按色点：删除', WHITE, 13)
    s += ui_note()
    save('u-gradient-edit', svg(W, H, s, '编辑渐变：轻点色点换色，轻点空处加色点'))


def case56(kind, after):
    Wd, Hd = 640, 480
    if kind == 'pink':
        c = TARGET_PINK if after else PHOTO_PINK
        inner = head_bangs(250, 230, 110, wig=c, wig_d=hexmix(c, '#4C1D95' if after else '#7F1D1D', 0.35), wig_l=hexmix(c, '#FFFFFF', 0.5))
        s = photo_box(20, 20, 600, 440, inner)
        s += f'<rect x="470" y="300" width="130" height="140" rx="12" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'
        s += swatch_strip(486, 340, [TARGET_PINK, c], ['设定', '照片'], 46, '并排对比')
        lab = '修之后：发色和设定色卡几乎一样' if after else '修之前：假发实物偏橘'
    elif kind == 'silver':
        c = TARGET_SILVER if after else PHOTO_SILVER
        inner = head_bangs(250, 230, 110, wig=c, wig_d=hexmix(c, '#334155', 0.35), wig_l='#FFFFFF')
        s = photo_box(20, 20, 600, 440, inner)
        s += f'<rect x="470" y="300" width="130" height="140" rx="12" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'
        s += swatch_strip(486, 340, [TARGET_SILVER, c], ['设定', '照片'], 46, '并排对比')
        lab = '修之后：发黄去掉，偏冷的银白' if after else '修之前：银白假发在暖光下发黄'
    else:
        sc, _ = con_scene(20, 20, 600, 440, people=False, stand=False)
        s = rect_clip(20, 20, 600, 440, sc)
        if after:
            s += f'<rect x="20" y="20" width="600" height="440" fill="#1E3A8A" fill-opacity=".28"/><rect x="20" y="20" width="600" height="440" fill="#A5F3FC" fill-opacity=".10"/>'
        lab = '修之后：整体偏冷、暗部发蓝，贴近冰系角色' if after else '修之前：场馆暖黄灯，和冰系角色不搭'
    s += label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15)
    return svg(Wd, Hd, s, lab)


ALL = [p_hair_flow, p_strand, p_hairline, u_hair_clone, u_brush_lib, u_hair_pick, u_hair_layers, u_hair_paint, u_peak_sel, u_peak_warp, u_real_hair_sel,
       p_eye_anatomy, p_catchlight, p_blend_eye, u_iris_sel, u_iris_layers, u_eye_curves, u_iris_paint, u_catch_paint, u_slit,
       p_folds, p_softlight, p_material, u_gray_view, u_softlight, u_dodge_burn, u_fabric_clone, u_prop_sel, u_prop_curves, u_prop_hl,
       p_clone_repeat, p_persp_patch, u_clone_big, u_patch_copy, u_patch_move, u_patch_mask, u_crop_extend, u_persp_guide, u_distort,
       p_local_color, p_color_mode_hair, p_gradient_map, u_ref_pick, u_palette_add, u_value_hex, u_wig_fill, u_hsb, u_copy_all, u_gradient_lib, u_gradient_edit]

if __name__ == '__main__' and len(sys.argv) == 1:
    for f in ALL:
        f()
    for k in ('fly', 'peak', 'lace'):
        save(f'case-{k}-before', case51(k, False)); save(f'case-{k}-after', case51(k, True))
    for k in ('glare', 'slit', 'nocatch'):
        save(f'case-{k}-before', case52(k, False)); save(f'case-{k}-after', case52(k, True))
    for k in ('shirt', 'seam', 'metal'):
        save(f'case-{k}-before', case53(k, False)); save(f'case-{k}-after', case53(k, True))
    for k in ('crowd', 'floor', 'extend'):
        save(f'case-{k}-before', case55(k, False)); save(f'case-{k}-after', case55(k, True))
    for k in ('pink', 'silver', 'mood'):
        save(f'case-{k}-before', case56(k, False)); save(f'case-{k}-after', case56(k, True))
    print('done', len(MADE))

if __name__ == '__main__' and 'only56' in sys.argv:
    for f in [p_local_color, p_color_mode_hair, p_gradient_map, u_ref_pick, u_palette_add, u_value_hex, u_wig_fill, u_hsb, u_copy_all, u_gradient_lib, u_gradient_edit]:
        f()
    for k in ('pink', 'silver', 'mood'):
        save(f'case-{k}-before', case56(k, False)); save(f'case-{k}-after', case56(k, True))
    print('ok', len(MADE))
