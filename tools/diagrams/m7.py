"""M7 合成 的示意图。运行：python tools/diagrams/m7.py"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'diagrams', 'm7')
os.makedirs(OUT, exist_ok=True)


def save(name, s):
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)


_n = [0]


def uid(p='k'):
    _n[0] += 1
    return f'{p}{_n[0]}'


# ---------------- 通用小件 ----------------
def grad(i, c1, c2, vertical=True):
    a = 'x1="0" y1="0" x2="0" y2="1"' if vertical else 'x1="0" y1="0" x2="1" y2="0"'
    return f'<defs><linearGradient id="{i}" {a}><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>'


def blur_filter(i, sd):
    return f'<defs><filter id="{i}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="{sd}"/></filter></defs>'


def gray_filter(i):
    return f'<defs><filter id="{i}"><feColorMatrix type="saturate" values="0"/></filter></defs>'


def clip_rect(x, y, w, h, body):
    i = uid('c')
    return f'<defs><clipPath id="{i}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/></clipPath></defs><g clip-path="url(#{i})">{body}</g>'


def sun(x, y, r=18, c=YEL):
    rays = ''.join(f'<line x1="{x + math.cos(a) * (r + 5):.1f}" y1="{y + math.sin(a) * (r + 5):.1f}" x2="{x + math.cos(a) * (r + 13):.1f}" y2="{y + math.sin(a) * (r + 13):.1f}" stroke="{INK}" stroke-width="2.5" stroke-linecap="round"/>'
                   for a in [k * math.pi / 4 for k in range(8)])
    return rays + f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}" stroke="{INK}" stroke-width="2.5"/>'


def ok_mark(x, y, good=True, r=14):
    if good:
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{MINT}" stroke="{INK}" stroke-width="2.5"/><path d="M{x - 6} {y} l4 5 l8 -10" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{RED}" stroke="{INK}" stroke-width="2.5"/><path d="M{x - 5} {y - 5} l10 10 M{x + 5} {y - 5} l-10 10" stroke="{WHITE}" stroke-width="3" stroke-linecap="round"/>'


def card(ox, oy, w, h, title=None, fill=YEL1):
    s = f'<rect x="{ox}" y="{oy}" width="{w}" height="{h}" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>'
    if title:
        s += label(ox + 16, oy + 34, title, fill, 15)
    return s


def hline(x1, x2, y, color=VIO7, w=2.5, dash='8 6'):
    return f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="{w}" stroke-dasharray="{dash}"/>'


def dim_v(x, y1, y2, txt=None, color=INK, size=13, side=1):
    s = (f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="2"/>'
         f'<line x1="{x - 6:.1f}" y1="{y1:.1f}" x2="{x + 6:.1f}" y2="{y1:.1f}" stroke="{color}" stroke-width="2"/>'
         f'<line x1="{x - 6:.1f}" y1="{y2:.1f}" x2="{x + 6:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="2"/>')
    if txt:
        s += text(x + side * 9, (y1 + y2) / 2 + 5, txt, size, 800, color, 'start' if side > 0 else 'end')
    return s


# ---------------- 人物 ----------------
def person(cx, feet, height, light=None, sw=2, shade=.24, rim=None, **kw):
    """height：人物总高（像素）。light='left'/'right'：光从哪边来，另一侧加暗面。rim：边缘光颜色。"""
    hh = height / 7.0
    top = feet - height
    hip = top + hh * 3.6
    fig = figure(cx, top, hh, hip, feet, sw=sw, **kw)
    s = fig
    if light in ('left', 'right'):
        i = uid('pc')
        x0 = cx - hh * 0.05 if light == 'left' else cx - hh * 2.2
        s += (f'<defs><clipPath id="{i}">{fig}</clipPath></defs><g clip-path="url(#{i})">'
              f'<rect x="{x0:.1f}" y="{top - hh:.1f}" width="{hh * 2.25:.1f}" height="{height + hh * 1.5:.1f}" fill="{INK}" fill-opacity="{shade}"/></g>')
        if rim:
            xr = cx - hh * 1.2 if light == 'left' else cx + hh * 0.85
            s += (f'<g clip-path="url(#{i})"><rect x="{xr:.1f}" y="{top - hh:.1f}" width="{hh * 0.35:.1f}" height="{height + hh * 1.5:.1f}" fill="{rim}" fill-opacity=".85"/></g>')
    return s


def contact(cx, feet, height, k=1.0, op=.55):
    hh = height / 7.0
    return (f'<ellipse cx="{cx + hh * 0.02:.1f}" cy="{feet - hh * 0.04:.1f}" rx="{hh * 0.95 * k:.1f}" ry="{hh * 0.2 * k:.1f}" fill="{INK}" fill-opacity="{op * 0.35:.2f}"/>'
            f'<ellipse cx="{cx + hh * 0.02:.1f}" cy="{feet - hh * 0.05:.1f}" rx="{hh * 0.62 * k:.1f}" ry="{hh * 0.08 * k:.1f}" fill="{INK}" fill-opacity="{op:.2f}"/>')


def cast(cx, feet, height, dx, dy, op=.32, width=1.0):
    """投影：从脚底出发，往 (dx, dy) 方向躺在地面上，远端变淡。"""
    hh = height / 7.0
    i = uid('cg')
    bx1, bx2 = cx - hh * width * 0.6, cx + hh * width * 0.6
    tx, ty = cx + dx, feet + dy
    nx, ny = -(dy), dx
    L = math.hypot(nx, ny) or 1
    nx, ny = nx / L * hh * 0.55, ny / L * hh * 0.55
    return (f'<defs><linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="{cx:.1f}" y1="{feet:.1f}" x2="{tx:.1f}" y2="{ty:.1f}">'
            f'<stop offset="0" stop-color="{INK}" stop-opacity="{op}"/><stop offset="1" stop-color="{INK}" stop-opacity="0.03"/></linearGradient></defs>'
            f'<path d="M{bx1:.1f} {feet - hh * 0.05:.1f} Q{(bx1 + tx) / 2 + nx:.1f} {(feet + ty) / 2 + ny:.1f} {tx + nx * 0.4:.1f} {ty + ny * 0.4:.1f} '
            f'L{tx - nx * 0.4:.1f} {ty - ny * 0.4:.1f} Q{(bx2 + tx) / 2 - nx:.1f} {(feet + ty) / 2 - ny:.1f} {bx2:.1f} {feet - hh * 0.05:.1f} Z" fill="url(#{i})"/>')


def stand_h(yb, hz, H=1.65, cam=1.5):
    """站在地面上、底部在 yb 的东西，照片里有多高（相机水平时）"""
    return (yb - hz) * H / cam


# ---------------- 场景 ----------------
def tree(x, yb, hgt, sun_side='left', crown=MINT, shadow=True, sw=2):
    r = hgt * 0.3
    s = ''
    if shadow:
        d = 1 if sun_side == 'left' else -1
        s += f'<ellipse cx="{x + d * r * 1.25:.1f}" cy="{yb + 2:.1f}" rx="{r * 1.35:.1f}" ry="{max(2, r * 0.22):.1f}" fill="{INK}" fill-opacity=".22"/>'
    s += f'<rect x="{x - hgt * 0.04:.1f}" y="{yb - hgt * 0.5:.1f}" width="{hgt * 0.08:.1f}" height="{hgt * 0.5:.1f}" fill="#A16207" stroke="{INK}" stroke-width="{sw}"/>'
    s += f'<circle cx="{x:.1f}" cy="{yb - hgt * 0.68:.1f}" r="{r:.1f}" fill="{crown}" stroke="{INK}" stroke-width="{sw}"/>'
    return s


def park(x, y, w, h, hz, vpx, cam=1.5, sun_side='left', blossom=False, golden=False, show_sun=True, trees=True, sw=2):
    i = uid('sky')
    c1, c2 = ('#FDBA74', '#FEF3C7') if golden else ('#93C5FD', '#E0F2FE')
    s = grad(i, c1, c2) + f'<rect x="{x}" y="{y}" width="{w}" height="{hz - y:.1f}" fill="url(#{i})"/>'
    if show_sun:
        sx = x + w * (0.14 if sun_side == 'left' else 0.86)
        s += sun(sx, y + (hz - y) * (0.62 if golden else 0.3), 16)
    # 远山
    s += f'<path d="M{x} {hz:.1f} Q{x + w * 0.2:.1f} {hz - h * 0.12:.1f} {x + w * 0.42:.1f} {hz - h * 0.03:.1f} Q{x + w * 0.62:.1f} {hz - h * 0.16:.1f} {x + w * 0.82:.1f} {hz - h * 0.04:.1f} Q{x + w * 0.92:.1f} {hz - h * 0.08:.1f} {x + w} {hz - h * 0.02:.1f} L{x + w} {hz:.1f} Z" fill="#A7C4BC" stroke="{INK}" stroke-width="1.5"/>'
    s += f'<rect x="{x}" y="{hz:.1f}" width="{w}" height="{y + h - hz:.1f}" fill="{"#D9E7A0" if golden else "#BBE5A8"}"/>'
    s += f'<line x1="{x}" y1="{hz:.1f}" x2="{x + w}" y2="{hz:.1f}" stroke="{INK}" stroke-width="1.5"/>'
    # 小路（一点透视）
    s += f'<path d="M{vpx - 2:.1f} {hz:.1f} L{vpx + 2:.1f} {hz:.1f} L{x + w * 0.78:.1f} {y + h} L{x + w * 0.3:.1f} {y + h} Z" fill="#F5E6C8" stroke="{INK}" stroke-width="{sw}"/>'
    if trees:
        crown = PINK1 if blossom else MINT
        for fx, t in [(0.34, 0.04), (0.66, 0.04), (0.2, 0.12), (0.8, 0.12), (0.05, 0.26), (0.95, 0.28)]:
            yb = hz + (y + h - hz) * t
            s += tree(x + w * fx, yb, stand_h(yb, hz, 3.0, cam), sun_side, crown, sw=sw)
    return s


def studio(x, y, w, h, floor_frac=0.86):
    fy = y + h * floor_frac
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#E5E7EB"/>'
            f'<rect x="{x}" y="{fy:.1f}" width="{w}" height="{y + h - fy:.1f}" fill="#CBD5E1"/>'
            f'<line x1="{x}" y1="{fy:.1f}" x2="{x + w}" y2="{fy:.1f}" stroke="{INK}" stroke-width="1.5"/>')


def street(x, y, w, h, hz, vpx, cam=1.5, strong=False, sw=2, lanterns=True):
    """古风街道，一点透视。strong=True：广角，透视强烈。"""
    i = uid('sky')
    s = grad(i, '#BAE6FD', '#F0F9FF') + f'<rect x="{x}" y="{y}" width="{w}" height="{hz - y:.1f}" fill="url(#{i})"/>'
    s += f'<rect x="{x}" y="{hz:.1f}" width="{w}" height="{y + h - hz:.1f}" fill="#D6D3D1"/>'
    # 地面石板缝（汇向灭点）
    for k in range(-5, 6):
        bx = vpx + k * w * (0.32 if strong else 0.16)
        s += f'<line x1="{vpx:.1f}" y1="{hz:.1f}" x2="{bx:.1f}" y2="{y + h}" stroke="#A8A29E" stroke-width="1.5"/>'
    for t in ([0.08, 0.2, 0.4, 0.7] if not strong else [0.04, 0.1, 0.22, 0.45, 0.85]):
        yy = hz + (y + h - hz) * t
        s += f'<line x1="{x}" y1="{yy:.1f}" x2="{x + w}" y2="{yy:.1f}" stroke="#A8A29E" stroke-width="1.2"/>'
    # 两侧房屋：上下边线都汇向灭点
    k_top = 1.9 if strong else 1.0
    for side in (-1, 1):
        xn = x if side < 0 else x + w
        xf = vpx + side * w * 0.07
        def ln(y0, xx):   # 在 x=xx 处，从 (xn, y0) 汇向 (vpx, hz) 的线的 y
            return hz + (y0 - hz) * (xx - vpx) / (xn - vpx)
        bot0 = hz + (y + h - hz) * (0.62 if strong else 0.42)
        top0 = hz - (hz - y) * (1.15 if strong else 0.7) * k_top / (1.9 if strong else 1.0)
        eave0 = top0 - (hz - y) * 0.12
        pts = [(xn, top0), (xf, ln(top0, xf)), (xf, ln(bot0, xf)), (xn, bot0)]
        s += '<path d="M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts) + f' Z" fill="{YEL1}" stroke="{INK}" stroke-width="{sw}"/>'
        roof = [(xn, eave0), (xf, ln(eave0, xf)), (xf, ln(top0, xf)), (xn, top0)]
        s += '<path d="M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in roof) + f' Z" fill="#475569" stroke="{INK}" stroke-width="{sw}"/>'
        # 立柱
        for t in [0.0, 0.35, 0.6, 0.78, 0.9]:
            xx = xn + (xf - xn) * t
            s += f'<line x1="{xx:.1f}" y1="{ln(top0, xx):.1f}" x2="{xx:.1f}" y2="{ln(bot0, xx):.1f}" stroke="#B91C1C" stroke-width="{max(1.5, 7 * (1 - t)):.1f}"/>'
            if lanterns and t in (0.35, 0.78):
                ly = ln(top0, xx) + (ln(bot0, xx) - ln(top0, xx)) * 0.12
                r = max(3, 14 * (1 - t))
                s += f'<ellipse cx="{xx + side * -r * 1.2:.1f}" cy="{ly + r:.1f}" rx="{r:.1f}" ry="{r * 1.2:.1f}" fill="{RED}" stroke="{INK}" stroke-width="1.5"/>'
    # 远处牌楼
    s += f'<rect x="{vpx - w * 0.07:.1f}" y="{hz - (hz - y) * 0.42:.1f}" width="{w * 0.14:.1f}" height="{(hz - y) * 0.42:.1f}" fill="#FDE68A" stroke="{INK}" stroke-width="1.5"/>'
    s += f'<path d="M{vpx - w * 0.1:.1f} {hz - (hz - y) * 0.42:.1f} L{vpx:.1f} {hz - (hz - y) * 0.55:.1f} L{vpx + w * 0.1:.1f} {hz - (hz - y) * 0.42:.1f} Z" fill="#475569" stroke="{INK}" stroke-width="1.5"/>'
    s += f'<line x1="{x}" y1="{hz:.1f}" x2="{x + w}" y2="{hz:.1f}" stroke="{INK}" stroke-width="1"/>'
    return s


def crowd(x, y, w, hz, rows, cam=1.5, seed=3, sw=1.5):
    """漫展人群：rows=[(底边 y, 人数)]"""
    rnd = random.Random(seed)
    cols = [VIO2, PINK, MINT, YEL, '#93C5FD', '#FCA5A5', '#A5B4FC', '#475569']
    s = ''
    for yb, n in rows:
        hgt = stand_h(yb, hz, 1.68, cam)
        for k in range(n):
            px = x + w * (k + 0.5 + rnd.uniform(-0.3, 0.3)) / n
            hh = hgt / 7.2
            c = rnd.choice(cols)
            s += f'<rect x="{px - hh * 0.75:.1f}" y="{yb - hgt + hh:.1f}" width="{hh * 1.5:.1f}" height="{hgt - hh:.1f}" rx="{hh * 0.6:.1f}" fill="{c}" stroke="{INK}" stroke-width="{sw}"/>'
            s += f'<circle cx="{px:.1f}" cy="{yb - hgt + hh * 0.5:.1f}" r="{hh * 0.5:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>'
    return s


def hall(x, y, w, h, hz, vpx, cam=1.5, floor='#CBD5E1', glossy=False, people=True, tape=True, sw=2):
    """室内漫展展馆"""
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{hz - y:.1f}" fill="#475569"/>'
    # 天花桁架和灯
    for k in range(7):
        xx = x + w * (k + 0.5) / 7
        s += f'<line x1="{xx:.1f}" y1="{y}" x2="{vpx + (xx - vpx) * 0.3:.1f}" y2="{y + (hz - y) * 0.45:.1f}" stroke="#64748B" stroke-width="2"/>'
        s += f'<circle cx="{xx:.1f}" cy="{y + (hz - y) * 0.12:.1f}" r="5" fill="{YEL1}"/>'
    s += f'<rect x="{x}" y="{y + (hz - y) * 0.42:.1f}" width="{w}" height="{(hz - y) * 0.58:.1f}" fill="#E2E8F0"/>'
    # 展位
    cols = [PINK, VIO, MINT, YEL, '#60A5FA', RED]
    for k in range(6):
        bx = x + w * (0.02 + k * 0.165)
        s += f'<rect x="{bx:.1f}" y="{y + (hz - y) * 0.5:.1f}" width="{w * 0.15:.1f}" height="{(hz - y) * 0.5:.1f}" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
        s += f'<rect x="{bx:.1f}" y="{y + (hz - y) * 0.5:.1f}" width="{w * 0.15:.1f}" height="{(hz - y) * 0.16:.1f}" fill="{cols[k]}" stroke="{INK}" stroke-width="1.5"/>'
    s += f'<rect x="{x}" y="{hz:.1f}" width="{w}" height="{y + h - hz:.1f}" fill="{floor}"/>'
    for k in range(-6, 7):
        s += f'<line x1="{vpx:.1f}" y1="{hz:.1f}" x2="{vpx + k * w * 0.2:.1f}" y2="{y + h}" stroke="#94A3B8" stroke-width="1.2"/>'
    for t in [0.06, 0.16, 0.32, 0.58, 0.95]:
        yy = hz + (y + h - hz) * t
        s += f'<line x1="{x}" y1="{yy:.1f}" x2="{x + w}" y2="{yy:.1f}" stroke="#94A3B8" stroke-width="1.2"/>'
    if glossy:
        for k in range(6):
            xx = x + w * (0.02 + k * 0.165) + w * 0.075
            s += f'<rect x="{xx - w * 0.03:.1f}" y="{hz + 2:.1f}" width="{w * 0.06:.1f}" height="{(y + h - hz) * 0.35:.1f}" fill="{WHITE}" fill-opacity=".35"/>'
    if tape:
        s += f'<rect x="{x + w * 0.12:.1f}" y="{hz + (y + h - hz) * 0.7:.1f}" width="{w * 0.1:.1f}" height="5" fill="{YEL}" transform="rotate(-8 {x + w * 0.12:.1f} {hz + (y + h - hz) * 0.7:.1f})"/>'
        s += f'<path d="M{x + w * 0.85:.1f} {y + h} q-{w * 0.05:.1f} -{(y + h - hz) * 0.3:.1f} -{w * 0.12:.1f} -{(y + h - hz) * 0.4:.1f}" fill="none" stroke="{INK}" stroke-width="2.5"/>'
    if people:
        s += crowd(x, y, w, hz, [(hz + 6, 9), (hz + 16, 6)], cam, seed=5)
    s += f'<line x1="{x}" y1="{hz:.1f}" x2="{x + w}" y2="{hz:.1f}" stroke="{INK}" stroke-width="1.2"/>'
    return s


def plaza(x, y, w, h, hz, vpx, cam=1.5, people=True, sw=2):
    """室外漫展广场：阴天、帐篷、人群、灰色地砖"""
    i = uid('sky')
    s = grad(i, '#CBD5E1', '#F1F5F9') + f'<rect x="{x}" y="{y}" width="{w}" height="{hz - y:.1f}" fill="url(#{i})"/>'
    s += f'<rect x="{x}" y="{hz - (hz - y) * 0.45:.1f}" width="{w}" height="{(hz - y) * 0.45:.1f}" fill="#94A3B8"/>'
    for k in range(5):
        tx = x + w * (0.05 + k * 0.2)
        ty = hz - (hz - y) * 0.3
        c = [PINK, '#60A5FA', YEL, MINT, VIO2][k]
        s += f'<path d="M{tx:.1f} {ty:.1f} L{tx + w * 0.08:.1f} {ty - (hz - y) * 0.18:.1f} L{tx + w * 0.16:.1f} {ty:.1f} Z" fill="{c}" stroke="{INK}" stroke-width="1.5"/>'
        s += f'<rect x="{tx + w * 0.01:.1f}" y="{ty:.1f}" width="{w * 0.14:.1f}" height="{hz - ty:.1f}" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
    s += f'<rect x="{x}" y="{hz:.1f}" width="{w}" height="{y + h - hz:.1f}" fill="#D4D4D8"/>'
    for k in range(-7, 8):
        s += f'<line x1="{vpx:.1f}" y1="{hz:.1f}" x2="{vpx + k * w * 0.16:.1f}" y2="{y + h}" stroke="#A1A1AA" stroke-width="1.2"/>'
    for t in [0.05, 0.13, 0.26, 0.46, 0.76]:
        yy = hz + (y + h - hz) * t
        s += f'<line x1="{x}" y1="{yy:.1f}" x2="{x + w}" y2="{yy:.1f}" stroke="#A1A1AA" stroke-width="1.2"/>'
    if people:
        s += crowd(x, y, w, hz, [(hz + 5, 10), (hz + 14, 7), (hz + 30, 3)], cam, seed=9)
    s += f'<line x1="{x}" y1="{hz:.1f}" x2="{x + w}" y2="{hz:.1f}" stroke="{INK}" stroke-width="1.2"/>'
    return s


def night_city(x, y, w, h, hz, vpx, ground=True, wet=True):
    i = uid('sky'); b = uid('bl')
    s = grad(i, '#0F172A', '#4C1D95') + blur_filter(b, 6) + f'<rect x="{x}" y="{y}" width="{w}" height="{hz - y:.1f}" fill="url(#{i})"/>'
    rnd = random.Random(11)
    bx = x
    k = 0
    while bx < x + w:
        bw = w * rnd.uniform(0.08, 0.16)
        bh = (hz - y) * rnd.uniform(0.35, 0.92)
        s += f'<rect x="{bx:.1f}" y="{hz - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="#1E1B4B" stroke="{INK}" stroke-width="1.5"/>'
        for r in range(int(bh // 14)):
            for c in range(int(bw // 10)):
                if rnd.random() < 0.35:
                    s += f'<rect x="{bx + 3 + c * 10:.1f}" y="{hz - bh + 5 + r * 14:.1f}" width="5" height="6" fill="{YEL1}" fill-opacity=".8"/>'
        if k % 2 == 0:
            nc = PINK if k % 4 == 0 else '#22D3EE'
            ny = hz - bh * 0.6
            s += f'<rect x="{bx + bw * 0.2:.1f}" y="{ny:.1f}" width="{bw * 0.6:.1f}" height="10" fill="{nc}" filter="url(#{b})"/><rect x="{bx + bw * 0.2:.1f}" y="{ny:.1f}" width="{bw * 0.6:.1f}" height="10" fill="{nc}"/>'
        bx += bw
        k += 1
    if ground:
        s += f'<rect x="{x}" y="{hz:.1f}" width="{w}" height="{y + h - hz:.1f}" fill="#1E293B"/>'
        for k in range(-5, 6):
            s += f'<line x1="{vpx:.1f}" y1="{hz:.1f}" x2="{vpx + k * w * 0.22:.1f}" y2="{y + h}" stroke="#334155" stroke-width="1.5"/>'
        if wet:
            for xx, c in [(0.18, PINK), (0.5, '#22D3EE'), (0.8, PINK)]:
                s += f'<rect x="{x + w * xx - 10:.1f}" y="{hz + 4:.1f}" width="20" height="{(y + h - hz) * 0.6:.1f}" fill="{c}" fill-opacity=".45" filter="url(#{b})"/>'
    return s


def courtyard(x, y, w, h, hz, vpx, cam=1.5, mist=False):
    """古风庭院：远处殿宇、院墙、树，地面为石板"""
    i = uid('sky')
    s = grad(i, '#A5B4FC', '#FDF2F8') + f'<rect x="{x}" y="{y}" width="{w}" height="{hz - y:.1f}" fill="url(#{i})"/>'
    s += f'<path d="M{x} {hz - (hz - y) * 0.3:.1f} Q{x + w * 0.25:.1f} {hz - (hz - y) * 0.6:.1f} {x + w * 0.5:.1f} {hz - (hz - y) * 0.35:.1f} T{x + w} {hz - (hz - y) * 0.4:.1f} L{x + w} {hz:.1f} L{x} {hz:.1f} Z" fill="#C4B5FD" fill-opacity=".6"/>'
    # 殿宇
    hx, hw = vpx - w * 0.22, w * 0.44
    base = hz + 2
    s += f'<rect x="{hx:.1f}" y="{base - (hz - y) * 0.42:.1f}" width="{hw:.1f}" height="{(hz - y) * 0.42:.1f}" fill="#FCA5A5" stroke="{INK}" stroke-width="1.8"/>'
    for t in range(1, 6):
        xx = hx + hw * t / 6
        s += f'<line x1="{xx:.1f}" y1="{base - (hz - y) * 0.42:.1f}" x2="{xx:.1f}" y2="{base:.1f}" stroke="{RED7}" stroke-width="3"/>'
    ry = base - (hz - y) * 0.42
    s += f'<path d="M{hx - w * 0.06:.1f} {ry:.1f} Q{hx + hw * 0.1:.1f} {ry - 8:.1f} {hx + hw * 0.2:.1f} {ry - (hz - y) * 0.2:.1f} L{hx + hw * 0.8:.1f} {ry - (hz - y) * 0.2:.1f} Q{hx + hw * 0.9:.1f} {ry - 8:.1f} {hx + hw + w * 0.06:.1f} {ry:.1f} Z" fill="#334155" stroke="{INK}" stroke-width="1.8"/>'
    # 院墙
    for side in (-1, 1):
        wx = x if side < 0 else hx + hw
        ww = (hx - x) if side < 0 else (x + w - hx - hw)
        s += f'<rect x="{wx:.1f}" y="{hz - (hz - y) * 0.16:.1f}" width="{ww:.1f}" height="{(hz - y) * 0.16 + 2:.1f}" fill="#FEF2F2" stroke="{INK}" stroke-width="1.5"/>'
        s += f'<rect x="{wx:.1f}" y="{hz - (hz - y) * 0.2:.1f}" width="{ww:.1f}" height="{(hz - y) * 0.05:.1f}" fill="#475569"/>'
    for fx in (0.08, 0.92):
        s += tree(x + w * fx, hz + 3, (hz - y) * 0.75, 'left', PINK1, shadow=False, sw=1.5)
    s += f'<rect x="{x}" y="{hz:.1f}" width="{w}" height="{y + h - hz:.1f}" fill="#D6D3D1"/>'
    for k in range(-6, 7):
        s += f'<line x1="{vpx:.1f}" y1="{hz:.1f}" x2="{vpx + k * w * 0.2:.1f}" y2="{y + h}" stroke="#A8A29E" stroke-width="1.2"/>'
    if mist:
        m = uid('mist')
        s += (f'<defs><linearGradient id="{m}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WHITE}" stop-opacity="0"/>'
              f'<stop offset=".5" stop-color="{WHITE}" stop-opacity=".75"/><stop offset="1" stop-color="{WHITE}" stop-opacity="0"/></linearGradient></defs>'
              f'<rect x="{x}" y="{hz - (hz - y) * 0.25:.1f}" width="{w}" height="{(hz - y) * 0.25 + (y + h - hz) * 0.25:.1f}" fill="url(#{m})"/>')
    return s


def forest_hills(x, y, w, h, hz, mist=True):
    i = uid('sky')
    s = grad(i, '#7DD3FC', '#F0FDFA') + f'<rect x="{x}" y="{y}" width="{w}" height="{hz - y:.1f}" fill="url(#{i})"/>'
    s += f'<path d="M{x} {hz - (hz - y) * 0.35:.1f} L{x + w * 0.22:.1f} {hz - (hz - y) * 0.75:.1f} L{x + w * 0.45:.1f} {hz - (hz - y) * 0.4:.1f} L{x + w * 0.7:.1f} {hz - (hz - y) * 0.85:.1f} L{x + w} {hz - (hz - y) * 0.45:.1f} L{x + w} {hz:.1f} L{x} {hz:.1f} Z" fill="#94A3B8" fill-opacity=".7" stroke="{INK}" stroke-width="1.2"/>'
    rnd = random.Random(4)
    for k in range(22):
        tx = x + w * (k + rnd.uniform(0, 0.6)) / 22
        th = (hz - y) * rnd.uniform(0.22, 0.4)
        s += f'<path d="M{tx:.1f} {hz - th:.1f} L{tx + th * 0.28:.1f} {hz + 1:.1f} L{tx - th * 0.28:.1f} {hz + 1:.1f} Z" fill="#059669" stroke="{INK}" stroke-width="1.2"/>'
    if mist:
        m = uid('mist')
        s += (f'<defs><linearGradient id="{m}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WHITE}" stop-opacity="0"/>'
              f'<stop offset=".6" stop-color="{WHITE}" stop-opacity=".8"/><stop offset="1" stop-color="{WHITE}" stop-opacity=".2"/></linearGradient></defs>'
              f'<rect x="{x}" y="{hz - (hz - y) * 0.3:.1f}" width="{w}" height="{(hz - y) * 0.3 + 4:.1f}" fill="url(#{m})"/>')
    return s


def snowfield(x, y, w, h, hz, vpx):
    i = uid('sky')
    s = grad(i, '#312E81', '#A5B4FC') + f'<rect x="{x}" y="{y}" width="{w}" height="{hz - y:.1f}" fill="url(#{i})"/>'
    rnd = random.Random(2)
    for k in range(40):
        s += f'<circle cx="{x + rnd.uniform(0, w):.1f}" cy="{y + rnd.uniform(0, (hz - y) * 0.6):.1f}" r="{rnd.uniform(0.8, 2):.1f}" fill="{WHITE}"/>'
    s += f'<path d="M{x} {hz:.1f} L{x + w * 0.15:.1f} {hz - (hz - y) * 0.5:.1f} L{x + w * 0.3:.1f} {hz - (hz - y) * 0.2:.1f} L{x + w * 0.5:.1f} {hz - (hz - y) * 0.7:.1f} L{x + w * 0.7:.1f} {hz - (hz - y) * 0.25:.1f} L{x + w * 0.85:.1f} {hz - (hz - y) * 0.55:.1f} L{x + w} {hz - (hz - y) * 0.2:.1f} L{x + w} {hz:.1f} Z" fill="#E0E7FF" stroke="{INK}" stroke-width="1.5"/>'
    s += f'<path d="M{x + w * 0.5:.1f} {hz - (hz - y) * 0.7:.1f} L{x + w * 0.56:.1f} {hz - (hz - y) * 0.48:.1f} L{x + w * 0.5:.1f} {hz - (hz - y) * 0.5:.1f} L{x + w * 0.45:.1f} {hz - (hz - y) * 0.45:.1f} Z" fill="{VIO2}"/>'
    s += f'<rect x="{x}" y="{hz:.1f}" width="{w}" height="{y + h - hz:.1f}" fill="#F1F5F9"/>'
    for k in range(-4, 5):
        s += f'<line x1="{vpx:.1f}" y1="{hz:.1f}" x2="{vpx + k * w * 0.3:.1f}" y2="{y + h}" stroke="#E2E8F0" stroke-width="1.5"/>'
    for fx, fy, sz in [(0.12, 0.8, 26), (0.85, 0.75, 34), (0.3, 0.62, 14), (0.7, 0.6, 12)]:
        cx_, cy_ = x + w * fx, y + h * fy
        s += f'<path d="M{cx_ - sz * 0.5:.1f} {cy_:.1f} L{cx_ - sz * 0.2:.1f} {cy_ - sz * 1.6:.1f} L{cx_ + sz * 0.1:.1f} {cy_ - sz * 0.6:.1f} L{cx_ + sz * 0.3:.1f} {cy_ - sz * 1.1:.1f} L{cx_ + sz * 0.55:.1f} {cy_:.1f} Z" fill="#BAE6FD" stroke="{INK}" stroke-width="1.5"/>'
    return s


# ---------------- 界面里的画布位置 ----------------
LAND = (170, 66, 460, 345)     # 横幅，界面中间
LANDL = (66, 66, 390, 300)     # 横幅，靠左（右边放图层面板）
PORT = (262, 66, 276, 340)


def frame_rect(r):
    x, y, w, h = r
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#94A3B8" stroke-width="1"/>'


def bbox(x, y, w, h, handles=True):
    s = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{UIBLUE}" stroke-width="2"/>'
    if handles:
        for hx, hy in [(x, y), (x + w / 2, y), (x + w, y), (x, y + h / 2), (x + w, y + h / 2), (x, y + h), (x + w / 2, y + h), (x + w, y + h)]:
            s += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="6" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
    return s


def copy_bar(hl, by=64, bx=170):
    items = ['剪切', '拷贝', '全部拷贝', '复制', '剪切并粘贴', '粘贴']
    s = f'<rect x="{bx}" y="{by}" width="460" height="46" rx="12" fill="{UIBAR}"/>'
    xx = bx + 10
    pos = {}
    for it in items:
        w = len(it) * 15 + 20
        s += f'<rect x="{xx}" y="{by + 7}" width="{w}" height="32" rx="8" fill="{UIPANEL}"/>' + text(xx + w / 2, by + 29, it, 14, 700, UITEXT, 'middle')
        pos[it] = (xx, w)
        if it == hl:
            s += ringrect(xx - 3, by + 4, w + 6, 38)
        xx += w + 6
    return s, pos


def layer_rows(x, y, w, rows, title='图层', row_h=46):
    """rows: (名称, 缩略图颜色, 模式, 选中, 缩进/剪辑, 是否组)"""
    h = 50 + len(rows) * row_h + 8
    s = panel(x, y, w, h, title) + text(x + w - 26, y + 30, '+', 24, 700, UITEXT, 'middle')
    for i, r in enumerate(rows):
        name, col, mode, sel = r[:4]
        clip = r[4] if len(r) > 4 else False
        grp = r[5] if len(r) > 5 else False
        yy = y + 44 + i * row_h
        ind = 22 if clip else 0
        s += f'<rect x="{x + 8 + ind}" y="{yy}" width="{w - 16 - ind}" height="{row_h - 6}" rx="8" fill="{UIBLUE if sel else UIBAR}"/>'
        if grp:
            s += text(x + 22, yy + row_h / 2 + 3, '▾', 15, 800, UITEXT) + text(x + 40, yy + row_h / 2 + 3, name, 15, 800, UITEXT)
        else:
            if clip:
                s += f'<path d="M{x + 16} {yy + 4} L{x + 16} {yy + 22} L{x + 26} {yy + 22}" fill="none" stroke="{UITEXT}" stroke-width="2" marker-end="url(#arw)"/>'
            s += f'<rect x="{x + 16 + ind}" y="{yy + 4}" width="40" height="{row_h - 14}" rx="4" fill="{col}" stroke="{INK}" stroke-width="1"/>'
            s += text(x + 66 + ind, yy + row_h / 2 + 3, name, 14, 700, UITEXT)
        s += text(x + w - 44, yy + row_h / 2 + 3, mode, 13, 800, UITEXT, 'middle')
        s += f'<rect x="{x + w - 30}" y="{yy + row_h / 2 - 11}" width="16" height="16" rx="3" fill="{UIBLUE}" stroke="{UITEXT}" stroke-width="1.5"/>'
    return s


# ---------------- 7.1 原理图 ----------------
def cam_icon(x, y):
    return f'<rect x="{x - 15}" y="{y - 10}" width="30" height="20" rx="4" fill="{INK}"/><circle cx="{x + 5}" cy="{y}" r="5.5" fill="{VIO2}"/>'


def p_horizon():
    Wd, Hd = 760, 400
    s = ''
    for col, (cam, hzf, title, note_) in enumerate([(1.5, 0.42, '镜头在 1.5 米（大约眼睛高）', '视平线穿过每个人的眼睛'),
                                                     (1.0, 0.55, '镜头在 1 米（大约腰的高度）', '视平线穿过每个人的腰')]):
        ox = 20 + col * 370
        s += card(ox, 10, 350, 380, title, VIO1 if col else YEL1)
        x0, y0, w, h = ox + 14, 58, 322, 268
        hz = y0 + h * hzf
        body = park(x0, y0, w, h, hz, x0 + w * 0.55, cam, trees=False, show_sun=False)
        for fx, ybf in [(0.72, 0.97), (0.38, 0.78), (0.6, 0.64)]:
            yb = y0 + h * ybf
            body += person(x0 + w * fx, yb, stand_h(yb, hz, 1.65, cam), sw=1.6)
        s += clip_rect(x0, y0, w, h, body) + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
        s += hline(x0, x0 + w, hz, VIO7, 3)
        s += cam_icon(x0 + 22, hz)
        s += label(x0 + 42, hz - 10, '视平线', VIO1, 13)
        s += text(ox + 175, 356, note_, 16, 800, INK, 'middle')
        s += text(ox + 175, 378, '人站得远近不同，视平线穿过的身体位置一样', 13, 500, MUTED, 'middle')
    save('p-horizon', svg(Wd, Hd, s, '视平线就是镜头的高度：站在同一地面上的人，视平线都穿过他们身上同一个高度'))


def p_light():
    Wd, Hd = 760, 340
    s = ''
    for col, (good, title) in enumerate([(True, '光向一致'), (False, '光向相反：一眼假')]):
        ox = 20 + col * 370
        s += card(ox, 10, 350, 320, title, MINT1 if good else RED1)
        x0, y0, w, h = ox + 14, 58, 322, 230
        hz = y0 + h * 0.45
        body = park(x0, y0, w, h, hz, x0 + w * 0.3, 1.5, trees=False, sun_side='left')
        yb_t = y0 + h * 0.6
        body += tree(x0 + w * 0.3, yb_t, stand_h(yb_t, hz, 4.0), 'left')
        yb = y0 + h * 0.93
        ph = stand_h(yb, hz, 1.65)
        cx = x0 + w * 0.66
        if good:
            body += cast(cx, yb, ph, ph * 0.7, -ph * 0.08, op=.5)
        else:
            body += cast(cx, yb, ph, -ph * 0.7, -ph * 0.08, op=.5)
        body += person(cx, yb, ph, light='left' if good else 'right', sw=1.6, shade=.38)
        s += clip_rect(x0, y0, w, h, body) + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
        s += ok_mark(ox + 326, 34, good)
        if good:
            s += text(ox + 175, 312, '树影、人影都朝右；人的暗面也在右边', 14, 700, INK, 'middle')
        else:
            s += text(ox + 175, 312, '太阳在左，人的暗面和影子却在左边', 14, 700, RED7, 'middle')
    save('p-light', svg(Wd, Hd, s, '光向一致与相反的对比：树影朝右，人物的暗面和影子也应该朝右'))


def p_focal():
    Wd, Hd = 760, 340
    s = ''
    for col, (strong, title, n1) in enumerate([(True, '广角拍的背景', '线条汇聚得很急，近处的柱子又粗又大'),
                                                (False, '中长焦拍的背景', '只拍到远处一段，远近的东西大小差得少')]):
        ox = 20 + col * 370
        s += card(ox, 10, 350, 320, title, YEL1 if strong else VIO1)
        x0, y0, w, h = ox + 14, 58, 322, 230
        hz = y0 + h * 0.5
        vx = x0 + w / 2
        st = street(x0, y0, w, h, hz, vx, strong=True, sw=1.5 if strong else 0.7)
        if not strong:
            st = f'<g transform="translate({vx:.1f},{hz:.1f}) scale(2.6) translate({-vx:.1f},{-hz:.1f})">{st}</g>'
        s += clip_rect(x0, y0, w, h, st) + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
        s += text(ox + 175, 312, n1, 14, 700, INK, 'middle')
    save('p-focal', svg(Wd, Hd, s, '同一条街，广角和中长焦拍出来的透视强弱不同'))



# ---------------- 7.1 界面图 ----------------
def park_canvas(r, hzf=0.42, vpf=0.55, **kw):
    x, y, w, h = r
    hz = y + h * hzf
    return park(x, y, w, h, hz, x + w * vpf, **kw), hz, x + w * vpf


def u_paste():
    x, y, w, h = LAND
    bg, hz, vx = park_canvas(LAND, blossom=True, sun_side='left')
    bar, pos = copy_bar('粘贴')
    fx = x + w + 70
    s = screen(clip_rect(x, y, w, h, bg) + frame_rect(LAND) + bar + finger(fx, 250, 3, 40))
    px, pw = pos['粘贴']
    s += badge(px + pw / 2, 128, 2)
    s += badge(fx - 52, 242, 1)
    s += label(x + w + 8, 350, '三指在画布上向下拖', YEL1, 14)
    s += label(36, 452, '① 在人物画布：选中抠好的人物层，三指下拖 → 「拷贝」', WHITE, 14)
    s += label(36, 488, '② 回到背景画布：三指下拖 → 「粘贴」，人物会粘贴成一个新图层', YEL1, 14)
    s += note('示意图，以实际界面为准')
    save('u-paste', svg(W, H, s, '在人物画布里拷贝人物层，回到背景画布三指下拖粘贴'))


def guide_ui(content, hl='透视'):
    s = f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>' + content
    s += f'<rect x="{SX}" y="{SY}" width="{SW}" height="42" rx="16" fill="{UIBAR}"/><rect x="{SX}" y="{SY + 26}" width="{SW}" height="16" fill="{UIBAR}"/>'
    s += text(SX + 24, 41, '取消', 15, 700, UITEXT) + text(SX + SW - 24, 41, '完成', 15, 800, UIBLUE, 'end')
    hue = uid('hue')
    s += (f'<defs><linearGradient id="{hue}" x1="0" x2="1"><stop offset="0" stop-color="#EF4444"/><stop offset=".2" stop-color="#F59E0B"/><stop offset=".4" stop-color="#22C55E"/>'
          f'<stop offset=".6" stop-color="#06B6D4"/><stop offset=".8" stop-color="#6366F1"/><stop offset="1" stop-color="#EC4899"/></linearGradient></defs>'
          f'<rect x="260" y="28" width="280" height="12" rx="6" fill="url(#{hue})"/>')
    s += bottom_bar([['2D 网格', '等距', '透视', '对称']], active=(hl,), hl=hl)
    return s


def u_persp_guide():
    x, y, w, h = LAND
    bg, hz, vx = park_canvas(LAND, blossom=True)
    rays = ''
    for a in range(-80, 81, 16):
        r = math.radians(a)
        rays += f'<line x1="{vx:.1f}" y1="{hz:.1f}" x2="{vx + math.sin(r) * 600:.1f}" y2="{hz + math.cos(r) * 600:.1f}" stroke="{UIBLUE}" stroke-width="1.2" stroke-opacity=".7"/>'
        rays += f'<line x1="{vx:.1f}" y1="{hz:.1f}" x2="{vx + math.sin(r) * 600:.1f}" y2="{hz - math.cos(r) * 600:.1f}" stroke="{UIBLUE}" stroke-width="1.2" stroke-opacity=".35"/>'
    rays += f'<line x1="{x}" y1="{hz:.1f}" x2="{x + w}" y2="{hz:.1f}" stroke="{UIBLUE}" stroke-width="3"/>'
    rays += f'<circle cx="{vx:.1f}" cy="{hz:.1f}" r="9" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="3"/>'
    s = guide_ui(clip_rect(x, y, w, h, bg + rays) + frame_rect(LAND))
    tx, ty, tw, th = POS['透视']
    s += badge(tx + tw / 2, ty - 14, 1)
    s += badge(vx + 22, hz - 22, 2)
    s += label(x + w + 10, hz - 30, '② 在小路两条边', YEL1, 14)
    s += label(x + w + 10, hz + 2, '　 延长线的交点', YEL1, 14)
    s += label(x + w + 10, hz + 34, '　 轻点，加透视点', YEL1, 14)
    s += label(x + w + 10, hz + 80, '蓝色横线 = 视平线', VIO1, 14)
    s += label(36, 120, '① 选「透视」', YEL1, 14)
    s += note('示意图，以实际界面为准')
    save('u-persp-guide', svg(W, H, s, '编辑绘图指引里选透视，在透视线交点处轻点添加透视点，横线就是视平线'))


def u_place():
    R = (262, 66, 370, 300)
    x, y, w, h = R
    bg, hz, vx = park_canvas(R, blossom=True)
    yb = y + h * 0.9
    ph = stand_h(yb, hz, 1.65, 1.5)
    cx = x + w * 0.6
    hh = ph / 7
    body = bg + f'<line x1="{x}" y1="{hz:.1f}" x2="{x + w}" y2="{hz:.1f}" stroke="{UIBLUE}" stroke-width="2.5"/>'
    body += person(cx, yb, ph, light='left', sw=1.8, shade=.3)
    content = clip_rect(x, y, w, h, body) + frame_rect(R) + bbox(cx - hh * 1.3, yb - ph - hh * 0.2, hh * 2.6, ph + hh * 0.3)
    s = screen(content + bottom_bar(TF_ROWS, active=('等比',)), active='transform')
    s += ring(*icon_pos('transform'), 18) + badge(icon_pos('transform')[0] + 26, 62, 1)
    s += badge(cx + hh * 1.3 + 16, yb + 8, 2)
    s += label(x + w + 8, hz + 6, '视平线', VIO1, 14)
    s += label(64, 120, '① 变换工具，选「等比」', YEL1, 14)
    s += label(64, 156, '② 拖角上的点缩放，', YEL1, 14)
    s += label(64, 188, '　 一指拖动摆位置', YEL1, 14)
    s += label(64, 236, '脚踩在小路上，', WHITE, 14)
    s += label(64, 268, '视平线穿过眼睛附近', WHITE, 14)
    s += note('示意图')
    save('u-place', svg(W, H, s, '变换工具选等比，缩放并摆放人物，让视平线穿过人物身上正确的高度'))


def u_flip_bg():
    x, y, w, h = LANDL
    bg, hz, vx = park_canvas(LANDL, blossom=True, sun_side='right')
    yb = y + h * 0.9
    ph = stand_h(yb, hz)
    body = bg + person(x + w * 0.62, yb, ph, light='left', sw=1.6, shade=.32)
    lay = layer_rows(470, 62, 300, [('人物', PINK1, 'N', False), ('背景', MINT1, 'N', True)])
    s = screen(clip_rect(x, y, w, h, body) + frame_rect(LANDL) + lay + bottom_bar(TF_ROWS, active=('自由变换',), hl='水平翻转'), active='transform')
    s += ring(*icon_pos('transform'), 18)
    s += badge(462, 62 + 44 + 46 + 20, 1)
    fx, fy, fw, fh = POS['水平翻转']
    s += badge(fx + fw / 2, fy - 12, 2)
    s += label(478, 250, '① 点选「背景」层', YEL1, 14)
    s += label(478, 282, '② 变换 → 「水平翻转」', YEL1, 14)
    s += label(478, 330, '背景里太阳在右，人物光从左来', RED1, 13)
    s += label(478, 360, '翻转背景后两边就一致了', MINT1, 13)
    s += note('示意图')
    save('u-flip-bg', svg(W, H, s, '选中背景层，用变换工具的水平翻转，让背景的光向和人物一致'))


def u_edge():
    x, y, w, h = LAND
    bg = park(x - 200, y - 300, w * 2.2, h * 2.2, y + h * 0.75, x + w * 0.4, blossom=True, trees=False, show_sun=False)
    # 放大后的头发和肩膀边缘
    hair = f'M{x + w * 0.35:.1f} {y + h + 10} L{x + w * 0.35:.1f} {y + h * 0.55:.1f} Q{x + w * 0.38:.1f} {y + h * 0.1:.1f} {x + w * 0.62:.1f} {y + h * 0.08:.1f} Q{x + w * 0.85:.1f} {y + h * 0.1:.1f} {x + w * 0.88:.1f} {y + h * 0.5:.1f} L{x + w * 0.88:.1f} {y + h + 10}'
    body = bg
    body += f'<path d="{hair}" fill="none" stroke="{WHITE}" stroke-width="9"/>'
    body += f'<path d="{hair} Z" fill="{PINK}" stroke="{INK}" stroke-width="2"/>'
    for k in range(9):
        a = x + w * (0.38 + k * 0.05)
        body += f'<path d="M{a:.1f} {y + h * 0.14:.1f} q-6 -18 -2 -34" fill="none" stroke="{PINK}" stroke-width="2"/>'
    body += f'<circle cx="{x + w * 0.36:.1f}" cy="{y + h * 0.5:.1f}" r="40" fill="none" stroke="{YEL}" stroke-width="4"/>'
    s = screen(clip_rect(x, y, w, h, body) + frame_rect(LAND))
    s += label(36, 116, '放大到 200% 以上，沿边缘看一圈', YEL1, 14)
    s += badge(x + w * 0.36 - 52, y + h * 0.5, 1)
    s += label(36, 300, '① 白边：原背景的颜色残留', RED1, 14)
    s += label(36, 332, '　→ 按 2.5 课去白边', RED1, 14)
    s += label(x + w * 0.62, y + h * 0.04 - 6, '② 发丝：保留半透明，不要一刀切', YEL1, 13, 'middle')
    s += note('示意图')
    save('u-edge', svg(W, H, s, '换完背景放大检查人物边缘：白边、发丝'))


# ---------------- 7.1 案例图 ----------------
CW_, CH_ = 640, 480


def frame_case(body, lab, after, w=CW_, h=CH_):
    s = clip_rect(20, 20, w - 40, h - 40, body) + f'<rect x="20" y="20" width="{w - 40}" height="{h - 40}" fill="none" stroke="{INK}" stroke-width="2.5"/>'
    s += label(w - 34, 56, lab, VIO1, 16, 'end') if after else label(34, 56, lab, YEL1, 16)
    return svg(w, h, s, lab)


def case_park_before():
    x, y, w, h = 20, 20, 600, 440
    body = studio(x, y, w, h, 0.86)
    yb = y + h * 0.95
    ph = h * 0.8
    body += f'<ellipse cx="{x + w * 0.5:.1f}" cy="{yb - 4:.1f}" rx="60" ry="10" fill="{INK}" fill-opacity=".18"/>'
    body += person(x + w * 0.5, yb, ph, light='left', sw=2.5, shade=.3)
    body += sun(x + 50, y + 110, 14, YEL1)
    body += label(x + 20, y + 150, '主光从左前方来', WHITE, 14)
    save('case-park-before', frame_case(body, '原图：灰墙前拍的全身照', False))


def case_park_after(shadows=False, grade=False, name='case-park-after', lab='换好背景：光向一致，脚踩在小路上'):
    x, y, w, h = 20, 20, 600, 440
    hz = y + h * 0.4
    body = park(x, y, w, h, hz, x + w * 0.45, 1.5, sun_side='left', blossom=True)
    yb = y + h * 0.95
    ph = stand_h(yb, hz)
    cx = x + w * 0.56
    if shadows:
        body += sil_shadow(cx, yb, ph, shx=-0.8, sy=0.35, op=.42, blur=2)
        body += contact(cx, yb, ph)
    body += person(cx, yb, ph, light='left', sw=2.5, shade=.3, rim=(YEL1 if grade else None))
    if grade:
        g = uid('gr')
        body += grad(g, '#F9A8D4', '#FDE68A') + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{g})" fill-opacity=".16"/>'
    save(name, frame_case(body, lab, True))


def case_street_before():
    x, y, w, h = 20, 20, 600, 440
    hz = y + h * 0.46
    body = street(x, y, w, h, hz, x + w * 0.5, strong=False)
    yb = y + h * 0.84
    ph = stand_h(yb, hz) * 1.6
    body += person(x + w * 0.5, yb, ph, sw=2.5)
    body += hline(x, x + w, hz, VIO7, 3)
    body += label(x + 16, hz - 10, '视平线', VIO1, 14)
    body += label(x + w - 16, hz + 30, '视平线穿过膝盖：人太大了', RED1, 14, 'end')
    save('case-street-before', frame_case(body, '直接贴上去：人像巨人', False))


def case_street_after():
    x, y, w, h = 20, 20, 600, 440
    hz = y + h * 0.46
    body = street(x, y, w, h, hz, x + w * 0.5, strong=False)
    yb = y + h * 0.84
    ph = stand_h(yb, hz)
    body += contact(x + w * 0.5, yb, ph, op=.35)
    body += person(x + w * 0.5, yb, ph, sw=2.5)
    body += hline(x, x + w, hz, VIO7, 3)
    body += label(x + 16, hz - 10, '视平线', VIO1, 14)
    body += label(x + w - 16, hz + 30, '视平线穿过眼睛：大小对了', MINT1, 14, 'end')
    save('case-street-after', frame_case(body, '按视平线缩小、摆位置', True))


def case_backlit():
    Wd, Hd = 760, 330
    s = ''
    ox = 20
    s += card(ox, 10, 340, 310, '背景：夕阳逆光', YEL1)
    x0, y0, w, h = ox + 14, 58, 312, 220
    hz = y0 + h * 0.62
    b = park(x0, y0, w, h, hz, x0 + w * 0.5, golden=True, sun_side='right', trees=False, show_sun=False)
    b += sun(x0 + w * 0.5, hz - 22, 22, '#FB923C')
    for fx in (0.15, 0.82):
        yb = y0 + h * 0.86
        th = stand_h(yb, hz, 4.0)
        b += f'<ellipse cx="{x0 + w * fx:.1f}" cy="{yb + 20:.1f}" rx="10" ry="40" fill="{INK}" fill-opacity=".3"/>'
        b += tree(x0 + w * fx, yb, th, 'left', '#57534E', shadow=False)
    s += clip_rect(x0, y0, w, h, b) + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
    s += text(ox + 170, 304, '太阳在正后方，影子朝镜头拉长', 14, 700, INK, 'middle')
    ox2 = 400
    s += card(ox2, 10, 340, 310, '人物：正面打光', VIO1)
    x1 = ox2 + 14
    b2 = studio(x1, y0, w, h)
    b2 += person(x1 + w * 0.5, y0 + h * 0.96, h * 0.86, sw=1.8)
    b2 += sun(x1 + 40, y0 + 40, 12, YEL1)
    s += clip_rect(x1, y0, w, h, b2) + f'<rect x="{x1}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
    s += text(ox2 + 170, 304, '脸和衣服正面都亮，没有逆光的亮边', 14, 700, INK, 'middle')
    s += ok_mark(380, 165, False, 18)
    save('case-backlit', svg(Wd, Hd, s, '逆光背景和正面打光的人物：光的方向差太多，不适合合成'))



# ---------------- 7.2 ----------------
CYAN = '#22D3EE'


def person_fx(cx, feet, height, dark=0.0, rims=(), sw=2, light=None, shade=.3, **kw):
    """人物 + 整体压暗 + 两侧边缘光。rims=[('left', 颜色), ('right', 颜色)]"""
    hh = height / 7.0
    top = feet - height
    hip = top + hh * 3.6
    fig = figure(cx, top, hh, hip, feet, sw=sw, **kw)
    i = uid('pf')
    s = fig + f'<defs><clipPath id="{i}">{fig}</clipPath></defs><g clip-path="url(#{i})">'
    if dark:
        s += f'<rect x="{cx - hh * 2.5:.1f}" y="{top - hh:.1f}" width="{hh * 5:.1f}" height="{height + hh * 2:.1f}" fill="#1E1B4B" fill-opacity="{dark}"/>'
    if light in ('left', 'right'):
        x0 = cx - hh * 0.05 if light == 'left' else cx - hh * 2.2
        s += f'<rect x="{x0:.1f}" y="{top - hh:.1f}" width="{hh * 2.25:.1f}" height="{height + hh * 1.5:.1f}" fill="{INK}" fill-opacity="{shade}"/>'
    for side, col in rims:
        xr = cx - hh * 1.2 if side == 'left' else cx + hh * 0.85
        s += f'<rect x="{xr:.1f}" y="{top - hh:.1f}" width="{hh * 0.35:.1f}" height="{height + hh * 1.5:.1f}" fill="{col}" fill-opacity=".9"/>'
    return s + '</g>'


def sil_shadow(cx, feet, height, shx=-1.0, sy=0.3, op=.45, blur=1.5, fade=True, **kw):
    """把人物轮廓"放倒"在地面上做投影。shx<0 往右倒，>0 往左倒；sy 越小影子越短。"""
    hh = height / 7.0
    top = feet - height
    fig = figure(cx, top, hh, top + hh * 3.6, feet, sw=1, **kw)
    f = uid('sf')
    m = uid('sm')
    g = uid('sg')
    tipx = cx + (-shx) * height
    tipy = feet - sy * height
    s = (f'<defs><filter id="{f}" x="-30%" y="-30%" width="160%" height="160%"><feColorMatrix type="matrix" values="0 0 0 0 0.12 0 0 0 0 0.14 0 0 0 0 0.22 0 0 0 {op} 0"/>'
         f'<feGaussianBlur stdDeviation="{blur}"/></filter>')
    if fade:
        s += (f'<linearGradient id="{g}" gradientUnits="userSpaceOnUse" x1="{cx:.1f}" y1="{feet:.1f}" x2="{tipx:.1f}" y2="{tipy:.1f}">'
              f'<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity=".15"/></linearGradient>'
              f'<mask id="{m}" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="5000" height="5000"><rect x="-2000" y="-2000" width="5000" height="5000" fill="url(#{g})"/></mask>')
    s += '</defs>'
    mt = f'matrix(1 0 {shx} {sy} {-shx * feet:.2f} {feet - sy * feet:.2f})'
    s += f'<g {"mask=" + chr(34) + "url(#" + m + ")" + chr(34) if fade else ""}><g filter="url(#{f})" transform="{mt}">{fig}</g></g>'
    return s


def p_shadow_read():
    Wd, Hd = 760, 330
    s = ''
    titles = ['影子朝哪边，光从反方向来', '影子越长，光越低', '影子边缘越虚，光越软']
    for k in range(3):
        ox = 20 + k * 246
        s += card(ox, 10, 230, 310, titles[k], [YEL1, VIO1, MINT1][k])
        x0, y0, w, h = ox + 12, 58, 206, 200
        gy = y0 + h * 0.62
        b = f'<rect x="{x0}" y="{y0}" width="{w}" height="{gy - y0:.1f}" fill="#E0F2FE"/><rect x="{x0}" y="{gy:.1f}" width="{w}" height="{y0 + h - gy:.1f}" fill="#E7E5E4"/>'
        if k == 0:
            px, pb = x0 + 80, y0 + h * 0.85
            b += f'<path d="M{px - 5} {pb} L{px + 5} {pb} L{px + 95} {pb - 18} L{px + 85} {pb - 20} Z" fill="{INK}" fill-opacity=".35"/>'
            b += f'<rect x="{px - 5}" y="{pb - 80}" width="10" height="80" fill="#A16207" stroke="{INK}" stroke-width="2"/>'
            b += sun(x0 + 30, y0 + 30, 12)
            b += f'<line x1="{px + 90}" y1="{pb - 19}" x2="{x0 + 38}" y2="{y0 + 38}" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6 5" marker-end="url(#arwr)"/>'
            note_ = '从影子尖连到柱顶，延长就指向光源'
        elif k == 1:
            for px, L, sy_ in [(x0 + 45, 30, y0 + 22), (x0 + 130, 70, y0 + 92)]:
                pb = y0 + h * 0.85
                b += f'<path d="M{px - 4} {pb} L{px + 4} {pb} L{px + 4 + L} {pb - 8} L{px - 4 + L} {pb - 9} Z" fill="{INK}" fill-opacity=".35"/>'
                b += f'<rect x="{px - 4}" y="{pb - 50}" width="8" height="50" fill="#A16207" stroke="{INK}" stroke-width="2"/>'
            b += sun(x0 + 30, y0 + 22, 10) + sun(x0 + 20, y0 + 92, 10)
            note_ = '中午影子短，早晚影子长'
        else:
            bf = uid('bf')
            b += blur_filter(bf, 5)
            pb = y0 + h * 0.85
            b += f'<ellipse cx="{x0 + 62}" cy="{pb}" rx="34" ry="8" fill="{INK}" fill-opacity=".5"/>'
            b += f'<circle cx="{x0 + 50}" cy="{pb - 30}" r="22" fill="{VIO2}" stroke="{INK}" stroke-width="2"/>'
            b += f'<ellipse cx="{x0 + 160}" cy="{pb}" rx="38" ry="11" fill="{INK}" fill-opacity=".35" filter="url(#{bf})"/>'
            b += f'<circle cx="{x0 + 150}" cy="{pb - 30}" r="22" fill="{VIO2}" stroke="{INK}" stroke-width="2"/>'
            b += text(x0 + 50, y0 + 30, '晴天', 13, 800, INK, 'middle') + text(x0 + 150, y0 + 30, '阴天', 13, 800, INK, 'middle')
            note_ = '晴天边缘清楚，阴天糊成一片'
        s += clip_rect(x0, y0, w, h, b) + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
        s += text(ox + 115, 290, note_, 13, 700, INK, 'middle')
    save('p-shadow-read', svg(Wd, Hd, s, '从背景里的影子读出光源：方向、高低、软硬'))


def p_horizon_ratio():
    Wd, Hd = 760, 420
    s = card(20, 10, 720, 400, '用门量出镜头高度，再算人该多高', YEL1)
    x0, y0, w, h = 36, 58, 420, 336
    hz = y0 + h * 0.4
    b = park(x0, y0, w, h, hz, x0 + w * 0.6, trees=False, show_sun=False)
    db = y0 + h * 0.72
    dh = (db - hz) * 2.0 / 1.5
    b += door(x0 + 40, db - dh, 46, db)
    pf = y0 + h * 0.95
    ph = stand_h(pf, hz)
    b += person(x0 + w * 0.68, pf, ph, sw=2)
    s += clip_rect(x0, y0, w, h, b) + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
    s += hline(x0, x0 + w, hz, VIO7, 3)
    s += label(x0 + w - 8, hz - 10, '视平线', VIO1, 13, 'end')
    s += dim_v(x0 + 104, hz, db, 'a', RED7, 16)
    s += dim_v(x0 + 30, db - dh, db, 'b', VIO7, 16, -1)
    s += dim_v(x0 + w * 0.68 + 44, hz, pf, 'd', RED7, 16)
    s += dim_v(x0 + w * 0.68 - 44, pf - ph, pf, '人高', VIO7, 14, -1)
    tx = 476
    rows = [('1. 量门', 800), ('a = 门底到视平线', 400), ('b = 门的高度（约 2 米）', 400), ('镜头高度 = 2 米 × a ÷ b', 800),
            ('', 400), ('2. 算人', 800), ('d = 人的脚底到视平线', 400), ('人高 = d × 身高 ÷ 镜头高度', 800),
            ('', 400), ('例：a = 60，b = 80', 400), ('→ 镜头 = 2 × 60 ÷ 80 = 1.5 米', 400), ('身高 1.65 米，d = 100', 400), ('→ 人高 = 100 × 1.65 ÷ 1.5 = 110', 400)]
    for k, (t, wt) in enumerate(rows):
        s += text(tx, 92 + k * 23, t, 15, wt, INK)
    s += text(tx, 396, 'a、b、d 都是照片上量的长度，单位随意', 12, 500, MUTED)
    save('p-horizon-ratio', svg(Wd, Hd, s, '用背景里已知高度的门量出镜头高度，再算出人物在这个位置应该多高'))


def p_dof():
    Wd, Hd = 760, 300
    s = card(20, 10, 720, 280, '对焦在人身上：离人越远（前后都算），越模糊', VIO1)
    gy = 210
    s += f'<rect x="40" y="{gy}" width="680" height="34" fill="#E7E5E4"/><line x1="40" y1="{gy}" x2="720" y2="{gy}" stroke="{INK}" stroke-width="2"/>'
    s += cam_icon(64, gy - 40)
    items = [(150, 4, '前景', 'bush'), (300, 0, '人物：最清楚', 'person'), (450, 2, '中景：稍虚', 'tree'), (620, 5, '远景：更虚', 'hill')]
    for x, sd, name, kind in items:
        f = uid('df')
        g = ''
        if kind == 'bush':
            g = f'<ellipse cx="{x}" cy="{gy - 22}" rx="40" ry="26" fill="{MINT}" stroke="{INK}" stroke-width="2"/>'
        elif kind == 'person':
            g = person(x, gy, 140, sw=2)
        elif kind == 'tree':
            g = tree(x, gy, 120, shadow=False)
        else:
            g = f'<path d="M{x - 80} {gy} L{x} {gy - 110} L{x + 80} {gy} Z" fill="#A7C4BC" stroke="{INK}" stroke-width="2"/>'
        if sd:
            s += blur_filter(f, sd) + f'<g filter="url(#{f})">{g}</g>'
        else:
            s += g
        s += label(x, gy + 28, name, WHITE if sd else MINT1, 13, 'middle')
    s += f'<line x1="300" y1="56" x2="300" y2="{gy}" stroke="{MINT7}" stroke-width="2" stroke-dasharray="5 4"/>'
    s += label(282, 72, '对焦平面', MINT1, 13, 'end')
    save('p-dof', svg(Wd, Hd, s, '景深：对焦在人物上，比人近或比人远的东西都会变模糊，越远越模糊'))


def p_color():
    Wd, Hd = 760, 320
    s = ''
    ox = 20
    s += card(ox, 10, 350, 300, '先看亮度：切成灰度比', YEL1)
    x0, y0, w, h = ox + 14, 56, 322, 200
    hz = y0 + h * 0.45
    gf = uid('gf')
    b = park(x0, y0, w, h, hz, x0 + w * 0.5, trees=True, show_sun=False, golden=True)
    b += f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#1E1B4B" fill-opacity=".45"/>'
    yb = y0 + h * 0.95
    ph = stand_h(yb, hz)
    b += person_fx(x0 + w * 0.5, yb, ph, sw=1.6)
    i = uid('pc')
    s += gray_filter(gf) + f'<g filter="url(#{gf})">' + clip_rect(x0, y0, w, h, b) + '</g>'
    s += f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
    s += text(ox + 175, 282, '背景是傍晚，人却比背景亮一截', 14, 700, RED7, 'middle')
    ox = 390
    s += card(ox, 10, 350, 300, '再看颜色：吸暗部比', VIO1)
    sw_ = [('背景的暗部', '#57534E', '#6B5B95'), ('人物的暗部', '#8B5E3C', '#6B5B95')]
    for k, (nm, c_bad, c_ok) in enumerate(sw_):
        y = 80 + k * 90
        s += text(ox + 24, y + 30, nm, 15, 800, INK)
        s += f'<circle cx="{ox + 170}" cy="{y + 24}" r="26" fill="{"#5B5470" if k == 0 else c_bad}" stroke="{INK}" stroke-width="2.5"/>'
        s += text(ox + 210, y + 22, '偏冷紫' if k == 0 else '偏暖橙', 14, 700, INK)
        s += text(ox + 210, y + 42, '（天光照的）' if k == 0 else '（棚里暖灯照的）', 12, 500, MUTED)
    s += text(ox + 175, 282, '两边暗部颜色不一样，人就"不在这里"', 14, 700, RED7, 'middle')
    save('p-color', svg(Wd, Hd, s, '色彩匹配：先在灰度下比亮度，再吸取暗部比颜色'))


def noise_sq(x, y, sz, amount, seed, base='#93C5FD'):
    rnd = random.Random(seed)
    s = f'<rect x="{x}" y="{y}" width="{sz}" height="{sz}" fill="{base}"/>'
    n = int(amount * 900)
    for _ in range(n):
        px, py = x + rnd.uniform(0, sz - 3), y + rnd.uniform(0, sz - 3)
        c = rnd.choice(['#FFFFFF', '#1E293B'])
        s += f'<rect x="{px:.1f}" y="{py:.1f}" width="3" height="3" fill="{c}" fill-opacity="{rnd.uniform(.15, .45):.2f}"/>'
    return s + f'<rect x="{x}" y="{y}" width="{sz}" height="{sz}" fill="none" stroke="{INK}" stroke-width="2.5"/>'


def p_grain():
    Wd, Hd = 760, 280
    s = card(20, 10, 720, 260, '放大到 200%，比较平滑区域（天空、墙、皮肤）', YEL1)
    s += noise_sq(50, 60, 150, 0.0, 1) + text(125, 236, '背景：模糊过，很干净', 13, 700, INK, 'middle')
    s += noise_sq(230, 60, 150, 0.6, 2, '#FDE2CF') + text(305, 236, '人物：手机噪点', 13, 700, INK, 'middle')
    s += arrow(400, 135, 450, 135, INK, 3)
    s += noise_sq(470, 60, 110, 0.35, 3) + noise_sq(590, 60, 110, 0.45, 4, '#FDE2CF')
    s += text(585, 200, '最上面统一加一层颗粒后', 13, 800, MINT7, 'middle')
    s += text(585, 222, '两边的颗粒差不多粗', 13, 600, INK, 'middle')
    save('p-grain', svg(Wd, Hd, s, '颗粒：背景干净、人物有噪点时，在最上面统一加一层颗粒'))


def p_shadows():
    Wd, Hd = 760, 360
    s = card(20, 10, 720, 340, '两种阴影', VIO1)
    x0, y0, w, h = 36, 56, 688, 280
    hz = y0 + h * 0.3
    b = park(x0, y0, w, h, hz, x0 + w * 0.3, trees=False, show_sun=False)
    b += sun(x0 + 60, y0 + 34, 16)
    yb = y0 + h * 0.86
    ph = 200
    cx = x0 + w * 0.36
    b += sil_shadow(cx, yb, ph, shx=-0.9, sy=0.45, op=.5, blur=2)
    b += contact(cx, yb, ph, 1.1, .7)
    b += person(cx, yb, ph, light='left', sw=2, shade=.3)
    s += clip_rect(x0, y0, w, h, b) + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
    s += label(x0 + 20, yb + 30, '接触阴影：贴着鞋底，最暗、最窄', YEL1, 14)
    s += arrow(x0 + 240, yb + 14, cx - 10, yb - 2, INK, 2)
    s += label(x0 + w - 16, yb - 90, '投影：背着光源躺在地上', WHITE, 14, 'end')
    s += label(x0 + w - 16, yb - 58, '离脚越远越淡、越虚', WHITE, 14, 'end')
    save('p-shadows', svg(Wd, Hd, s, '接触阴影和投影：接触阴影贴着鞋底最暗，投影背着光源、越远越淡'))



def info_bar(t):
    return f'<rect x="300" y="62" width="200" height="30" rx="8" fill="{UIBLUE}"/>' + text(400, 82, t, 14, 800, WHITE, 'middle')


def u_light_arrows():
    x, y, w, h = LAND
    hz = y + h * 0.42
    bg = park(x, y, w, h, hz, x + w * 0.4, trees=False, sun_side='left')
    ty = hz + (y + h - hz) * 0.25
    th = stand_h(ty, hz, 3.0)
    tx = x + w * 0.25
    bg += tree(tx, ty, th, 'left')
    r = th * 0.3
    tip = (tx + r * 2.6, ty + 2)
    top = (tx, ty - th * 0.68 - r)
    sx, sy_ = x + w * 0.14, y + (hz - y) * 0.3
    yb = y + h * 0.92
    ph = stand_h(yb, hz)
    cx = x + w * 0.66
    bg += person(cx, yb, ph, light='left', sw=1.8, shade=.32)
    chk = f'<line x1="{tip[0]:.1f}" y1="{tip[1]:.1f}" x2="{sx + 18:.1f}" y2="{sy_ + 16:.1f}" stroke="{RED}" stroke-width="3" marker-end="url(#arwr)"/>'
    hh = ph / 7
    chk += f'<line x1="{cx - hh * 2.6:.1f}" y1="{yb - ph * 0.6:.1f}" x2="{cx - hh * 1.2:.1f}" y2="{yb - ph * 0.6:.1f}" stroke="{RED}" stroke-width="3" marker-end="url(#arwr)"/>'
    s = screen(clip_rect(x, y, w, h, bg + chk) + frame_rect(LAND), active='brush')
    s += ring(*icon_pos('brush'), 18)
    s += badge(tip[0] + 14, tip[1] + 14, 1) + badge(cx - hh * 2.9, yb - ph * 0.6 - 18, 2)
    s += label(36, 452, '新建「检查」图层，用红色细笔画箭头（检查完删掉）', WHITE, 14)
    s += label(36, 488, '① 影子尖 → 物体顶，延长指向光源　② 人物的亮面要朝向同一边', YEL1, 14)
    s += note('示意图')
    save('u-light-arrows', svg(W, H, s, '在检查图层上画箭头：从影子尖经过物体顶端延长，指向光源；人物亮面朝向同一边'))


def u_persp_check():
    x, y, w, h = LAND
    hz = y + h * 0.42
    bg = park(x, y, w, h, hz, x + w * 0.5, blossom=True)
    yb = y + h * 0.9
    ph = stand_h(yb, hz)
    cx = x + w * 0.6
    bg += person(cx, yb, ph, light='left', sw=1.8, shade=.3)
    bg += f'<line x1="{x}" y1="{hz:.1f}" x2="{x + w}" y2="{hz:.1f}" stroke="{UIBLUE}" stroke-width="2.5"/>'
    hh = ph / 7
    ms = dim_v(cx + hh * 1.8, hz, yb, 'd', MINT7, 16) + dim_v(cx - hh * 1.8, yb - ph, yb, '', VIO7, 14, -1)
    s = screen(clip_rect(x, y, w, h, bg) + ms + frame_rect(LAND), active='brush')
    s += label(x + w + 8, hz + 6, '视平线', VIO1, 14)
    s += label(36, 452, '新建「标尺」层，量 d（脚底到视平线）和人物的高度', WHITE, 14)
    s += label(36, 488, '镜头 1.5 米、人身高 1.65 米时：人高 ≈ 1.1 × d', YEL1, 14)
    s += note('示意图')
    save('u-persp-check', svg(W, H, s, '在标尺图层上量脚底到视平线的距离 d，检查人物高度'))


def ants_path(d):
    return (f'<path d="{d}" fill="{UIBLUE}" fill-opacity=".10" stroke="{WHITE}" stroke-width="2.5"/>'
            f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 6"/>')


def u_blur():
    x, y, w, h = LAND
    hz = y + h * 0.42
    bf = uid('bb')
    far = park(x, y, w, h, hz, x + w * 0.5, blossom=True)
    near = far
    split = hz + (y + h - hz) * 0.18
    body = near + blur_filter(bf, 3) + clip_rect(x, y, w, split - y, f'<g filter="url(#{bf})">{far}</g>')
    yb = y + h * 0.92
    ph = stand_h(yb, hz)
    body += person(x + w * 0.6, yb, ph, light='left', sw=1.8, shade=.3)
    d = f'M{x + 2} {y + 2} L{x + w - 2} {y + 2} L{x + w - 2} {split:.1f} L{x + 2} {split:.1f} Z'
    s = screen(clip_rect(x, y, w, h, body) + ants_path(d) + frame_rect(LAND) + info_bar('高斯模糊 8%'), active='adjust')
    s += arrow(x + w + 40, 280, x + w + 100, 280, INK, 3) + arrow(x + w + 100, 280, x + w + 40, 280, INK, 3)
    s += ring(*icon_pos('adjust'), 18)
    s += label(x + w + 8, 320, '左右滑动', YEL1, 14)
    s += label(x + w + 8, 350, '调模糊程度', YEL1, 14)
    s += badge(x - 20, (y + split) / 2, 1)
    s += label(36, 452, '① 在「背景」层上，用选区框住远处、羽化，再进 调整 → 高斯模糊', YEL1, 14)
    s += label(36, 488, '脚边的地面不模糊；人物在单独的图层上，不受影响', WHITE, 14)
    s += note('示意图')
    save('u-blur', svg(W, H, s, '在背景层上选中远处并羽化，用高斯模糊按距离模糊'))


def u_gray_check():
    x, y, w, h = LANDL
    hz = y + h * 0.42
    gf = uid('g')
    b = park(x, y, w, h, hz, x + w * 0.5, blossom=True)
    yb = y + h * 0.92
    b += person(x + w * 0.6, yb, stand_h(yb, hz), light='left', sw=1.6, shade=.3)
    lay = layer_rows(470, 62, 300, [('灰度检查', '#111827', '颜色', True), ('人物', PINK1, 'N', False), ('背景', MINT1, 'N', False)])
    s = screen(gray_filter(gf) + f'<g filter="url(#{gf})">' + clip_rect(x, y, w, h, b) + '</g>' + frame_rect(LANDL) + lay, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += badge(462, 62 + 44 + 20, 1)
    s += label(478, 300, '最上面新建一层，填充黑色', YEL1, 14)
    s += label(478, 332, '混合模式改成「颜色」', YEL1, 14)
    s += label(478, 380, '画面变灰度，只比亮度', WHITE, 14)
    s += label(478, 412, '看完把这层关掉（取消勾选）', WHITE, 14)
    s += note('示意图，混合模式在图层右边的字母处修改')
    save('u-gray-check', svg(W, H, s, '在最上面加一层黑色、混合模式设为颜色，切成灰度比较人物和背景的亮度'))


LAYER_OPTS = ['重命名', '选择', '拷贝', '填充图层', '清除', '阿尔法锁定', '蒙版', '剪辑蒙版', '辅助绘图', '反转', '参考', '向下合并', '向下组合']


def u_clip_color():
    x, y, w, h = LANDL
    hz = y + h * 0.42
    b = park(x, y, w, h, hz, x + w * 0.5, blossom=True)
    yb = y + h * 0.92
    b += person(x + w * 0.6, yb, stand_h(yb, hz), light='left', sw=1.6, shade=.3)
    lay = layer_rows(470, 62, 300, [('统一色调', '#C4B5FD', '柔光', True, True), ('人物', PINK1, 'N', False), ('背景', MINT1, 'N', False)])
    px, py, pw = 240, 96, 210
    pop = panel(px, py, pw, 28 * len(LAYER_OPTS) + 12) + menu_rows(px, py + 6, pw, LAYER_OPTS, hl='剪辑蒙版', row_h=28)
    s = screen(clip_rect(x, y, w, h, b) + frame_rect(LANDL) + lay + pop, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += badge(462, 62 + 44 + 20, 1)
    s += badge(px - 16, py + 6 + 7 * 28 + 14, 2)
    s += label(478, 290, '① 在人物层上面新建一层，', YEL1, 14)
    s += label(478, 320, '　 轻点两次打开图层选项', YEL1, 14)
    s += label(478, 360, '② 点「剪辑蒙版」', YEL1, 14)
    s += label(478, 408, '这层只作用在人物身上', WHITE, 14)
    s += note('示意图，以实际界面为准')
    save('u-clip-color', svg(W, H, s, '新建图层并设为剪辑蒙版，只给人物统一色调'))


def u_copyall():
    x, y, w, h = LANDL
    hz = y + h * 0.42
    b = park(x, y, w, h, hz, x + w * 0.5, blossom=True)
    yb = y + h * 0.92
    b += person(x + w * 0.6, yb, stand_h(yb, hz), light='left', sw=1.6, shade=.3)
    lay = layer_rows(470, 62, 300, [('合并副本', '#FBCFE8', 'N', True), ('人物', PINK1, 'N', False), ('背景', MINT1, 'N', False)])
    bar, pos = copy_bar('全部拷贝', by=420, bx=40)
    s = screen(clip_rect(x, y, w, h, b) + frame_rect(LANDL) + lay + bar)
    px, pw = pos['全部拷贝']
    s += badge(px + pw / 2, 486, 1)
    px2, pw2 = pos['粘贴']
    s += badge(px2 + pw2 / 2, 486, 2)
    s += label(478, 290, '① 三指下拖 →「全部拷贝」', YEL1, 14)
    s += label(478, 322, '② 再三指下拖 →「粘贴」', YEL1, 14)
    s += label(478, 362, '得到一张合并好的「合并副本」', WHITE, 14)
    s += label(478, 394, '原来的图层都还在', WHITE, 14)
    s += note('示意图')
    save('u-copyall', svg(W, H, s, '三指下拖全部拷贝，再粘贴，得到一张合并好的新图层'))


def u_gradmap():
    x, y, w, h = LANDL
    hz = y + h * 0.42
    b = park(x, y, w, h, hz, x + w * 0.5, blossom=True)
    yb = y + h * 0.92
    b += person(x + w * 0.6, yb, stand_h(yb, hz), light='left', sw=1.6, shade=.3)
    g = uid('gm')
    b += grad(g, '#7C3AED', '#FDE68A') + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{g})" fill-opacity=".22"/>'
    px, py, pw = 470, 62, 300
    pres = [('神秘', '#1E1B4B', '#F472B6'), ('微风', '#0EA5E9', '#ECFEFF'), ('瞬间', '#7C2D12', '#FDE68A'), ('威尼斯', '#134E4A', '#FDBA74'),
            ('火焰', '#450A0A', '#FACC15'), ('霓虹灯', '#312E81', '#22D3EE'), ('黑暗', '#020617', '#94A3B8'), ('摩卡', '#3F2A1D', '#F5E6C8')]
    s_ = panel(px, py, pw, 330, '渐变库') + text(px + pw - 26, py + 30, '+', 24, 700, UITEXT, 'middle')
    for k, (nm, c1, c2) in enumerate(pres):
        cx_ = px + 16 + (k % 2) * 140
        cy_ = py + 52 + (k // 2) * 66
        gi = uid('gp')
        s_ += grad(gi, c1, c2, vertical=False) + f'<rect x="{cx_}" y="{cy_}" width="128" height="30" rx="6" fill="url(#{gi})" stroke="#111827"/>'
        s_ += text(cx_, cy_ + 48, nm, 13, 700, UITEXT)
        if nm == '神秘':
            s_ += ringrect(cx_ - 4, cy_ - 4, 136, 38)
    s = screen(clip_rect(x, y, w, h, b) + frame_rect(LANDL) + s_, active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += ring(px + pw - 26, py + 22, 16)
    s += badge(px - 8, py + 66, 1) + badge(px + pw - 54, py + 22, 2)
    s += label(36, 420, '在「合并副本」上：调整 → 渐变映射', WHITE, 14)
    s += label(36, 452, '① 点预设试效果　② 点「+」自己建：左端放暗部色，右端放亮部色', YEL1, 14)
    s += label(36, 488, '确认后把这层不透明度降到 15%～30%', YEL1, 14)
    s += note('示意图，以实际界面为准')
    save('u-gradmap', svg(W, H, s, '渐变映射：选预设或新建渐变，确认后降低图层不透明度'))


def u_noise():
    R = (262, 66, 370, 300)
    x, y, w, h = R
    hz = y + h * 0.42
    b = park(x, y, w, h, hz, x + w * 0.5, blossom=True)
    yb = y + h * 0.92
    b += person(x + w * 0.6, yb, stand_h(yb, hz), light='left', sw=1.8, shade=.3)
    rnd = random.Random(7)
    for _ in range(1400):
        b += f'<rect x="{x + rnd.uniform(0, w):.1f}" y="{y + rnd.uniform(0, h):.1f}" width="2" height="2" fill="{rnd.choice([WHITE, INK])}" fill-opacity=".25"/>'
    bar = tool_sliders([('比例', 0.15), ('倍频', 0.3), ('湍流', 0.1)], buttons=('云', '巨浪', '背脊'))
    cbx, cby = 700, SY + SH - 74 + 12
    ch = f'<rect x="{cbx}" y="{cby}" width="62" height="38" rx="10" fill="{UIBAR}" stroke="{UIPANEL}"/>' + text(cbx + 31, cby + 25, '通道', 13, 700, UITEXT, 'middle')
    pop = panel(cbx - 110, cby - 130, 172, 116) + menu_rows(cbx - 110, cby - 124, 172, ['单一', '多个', '叠加'], hl='单一', row_h=34, toggles={'叠加': False})
    s = screen(clip_rect(x, y, w, h, b) + frame_rect(R) + info_bar('杂色 20%') + bar + ch + pop, active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += label(64, 120, '最上面新建一层，填充中灰', YEL1, 14)
    s += label(64, 152, '混合模式「覆盖」', YEL1, 14)
    s += label(64, 184, '再进 调整 → 杂色', YEL1, 14)
    s += label(64, 230, '左右滑动调颗粒多少', WHITE, 14)
    s += label(cbx - 116, cby - 140, '单一 = 黑白颗粒', YEL1, 13, 'end')
    s += note('示意图，通道按钮的位置以实际界面为准')
    save('u-noise', svg(W, H, s, '在覆盖模式的中灰图层上加杂色，统一全图颗粒'))


def u_contact():
    x, y, w, h = LANDL
    hz = y - 400
    b = park(x - 300, y - 600, w + 600, h + 600, hz, x + w * 0.5, trees=False, show_sun=False)
    # 放大的脚
    for dx in (-60, 40):
        b += f'<rect x="{x + w / 2 + dx:.1f}" y="{y - 10}" width="46" height="{h * 0.62:.1f}" rx="16" fill="{SKIN}" stroke="{INK}" stroke-width="3"/>'
    fy = y + h * 0.72
    b += f'<path d="M{x + w / 2 - 110:.1f} {fy + 6:.1f} Q{x + w / 2:.1f} {fy + 26:.1f} {x + w / 2 + 120:.1f} {fy + 6:.1f}" fill="none" stroke="{INK}" stroke-opacity=".25" stroke-width="30" stroke-linecap="round"/>'
    b += f'<path d="M{x + w / 2 - 95:.1f} {fy + 4:.1f} Q{x + w / 2:.1f} {fy + 14:.1f} {x + w / 2 + 105:.1f} {fy + 4:.1f}" fill="none" stroke="{INK}" stroke-opacity=".75" stroke-width="7" stroke-linecap="round"/>'
    for dx in (-37, 63):
        b += f'<ellipse cx="{x + w / 2 + dx:.1f}" cy="{fy - 14:.1f}" rx="58" ry="22" fill="{INK}"/>'
    lay = layer_rows(470, 62, 300, [('人物', PINK1, 'N', False), ('接触阴影', '#475569', 'M', True), ('背景', MINT1, 'N', False)])
    s = screen(clip_rect(x, y, w, h, b) + frame_rect(LANDL) + lay, active='brush')
    s += ring(*icon_pos('brush'), 18)
    s += badge(462, 62 + 44 + 46 + 20, 1)
    s += badge(x + w / 2 + 128, fy + 6, 2) + badge(x + w / 2 - 128, fy + 22, 3)
    s += label(478, 290, '① 新层放在人物下面，「正片叠底」', YEL1, 14)
    s += label(478, 322, '② 吸地面最暗的颜色，', YEL1, 14)
    s += label(478, 352, '　 小号软笔沿鞋底画一条细线', YEL1, 14)
    s += label(478, 384, '③ 换大号、低不透明度，', YEL1, 14)
    s += label(478, 414, '　 在外面淡淡晕开一圈', YEL1, 14)
    s += note('示意图')
    save('u-contact', svg(W, H, s, '在人物下面新建正片叠底图层，沿鞋底画接触阴影'))


def u_cast():
    x, y, w, h = LAND
    hz = y + h * 0.36
    b = park(x, y, w, h, hz, x + w * 0.4, trees=False, sun_side='left')
    yb = y + h * 0.9
    ph = stand_h(yb, hz)
    cx = x + w * 0.42
    shx, sy = -0.9, 0.42
    b += sil_shadow(cx, yb, ph, shx=shx, sy=sy, op=.5, blur=0.8, fade=False)
    b += person(cx, yb, ph, light='left', sw=1.8, shade=.3)
    hh = ph / 7
    top = yb - ph
    def T(px, py):
        return px + shx * (py - yb), yb + sy * (py - yb)
    corners = [T(cx - hh * 1.2, top), T(cx + hh * 1.2, top), T(cx + hh * 1.2, yb), T(cx - hh * 1.2, yb)]
    q = f'<path d="M' + ' L'.join(f'{a:.1f} {c:.1f}' for a, c in corners) + f' Z" fill="none" stroke="{UIBLUE}" stroke-width="2"/>'
    for a, c in corners:
        q += f'<circle cx="{a:.1f}" cy="{c:.1f}" r="6" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
    s = screen(clip_rect(x, y, w, h, b) + q + frame_rect(LAND) + bottom_bar(TF_ROWS, active=('扭曲',)), active='transform')
    s += ring(*icon_pos('transform'), 18)
    s += badge(corners[1][0] + 16, corners[1][1] - 14, 1)
    s += label(x + w - 150, y + 30, '① 拖上面两个角，', YEL1, 14)
    s += label(x + w - 150, y + 62, '　 把影子"放倒"', YEL1, 14)
    s += label(36, 300, '② 下面两个角', YEL1, 14)
    s += label(36, 332, '　 留在鞋底', YEL1, 14)
    s += badge(corners[3][0] - 14, corners[3][1] + 16, 2)
    s += note('示意图')
    save('u-cast', svg(W, H, s, '把复制出来的深色人形用变换的扭曲模式放倒在地面上，做投影'))


def case_park_fixed():
    case_park_after(shadows=True, grade=True, name='case-park-fixed', lab='逐项修完：有了阴影，色调统一')


def city_scene(after):
    x, y, w, h = 20, 20, 600, 440
    hz = y + h * 0.62
    body = night_city(x, y, w, h, hz, x + w * 0.5)
    yb = y + h * 0.84
    ph = h * 0.68
    cx = x + w * 0.5
    if after:
        rf = uid('rf')
        body += blur_filter(rf, 3) + f'<g opacity=".28" filter="url(#{rf})" transform="translate(0,{2 * yb:.1f}) scale(1,-1)">{person_fx(cx, yb, ph, dark=.45, sw=2)}</g>'
        body += contact(cx, yb, ph, 1.0, .7)
        body += person_fx(cx, yb, ph, dark=.42, rims=[('left', PINK), ('right', CYAN)], sw=2.5)
    else:
        body += person_fx(cx, yb, ph, sw=2.5)
    return body


def case_night_before():
    save('case-night-before', frame_case(city_scene(False), '直接放进去：人比夜景亮一大截', False))


def case_night_after():
    save('case-night-after', frame_case(city_scene(True), '压暗人物，两侧加霓虹边缘光和倒影', True))



# ---------------- 7.3 ----------------
def hatch(x, y, w, h, col='#64748B'):
    pid = uid('ht')
    return (f'<defs><pattern id="{pid}" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<line x1="0" y1="0" x2="0" y2="12" stroke="{col}" stroke-width="4" stroke-opacity=".45"/></pattern></defs>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="url(#{pid})"/>')


def grass(x1, x2, y, seed=1, hgt=14):
    rnd = random.Random(seed)
    s = ''
    xx = x1
    while xx < x2:
        hh = hgt * rnd.uniform(0.6, 1.3)
        s += f'<path d="M{xx:.1f} {y + 4:.1f} q{rnd.uniform(-4, 4):.1f} {-hh / 2:.1f} {rnd.uniform(-6, 6):.1f} {-hh:.1f}" fill="none" stroke="#15803D" stroke-width="2.5" stroke-linecap="round"/>'
        xx += rnd.uniform(3, 7)
    return s


def soft_band(x, y, w, h, col=WHITE, op=.8):
    m = uid('sb')
    return (f'<defs><linearGradient id="{m}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{col}" stop-opacity="{op}"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="url(#{m})"/>')


def hall_photo(x, y, w, h, hzf=0.45, person_x=0.55, **kw):
    """展馆场照 + 人物位置"""
    hz = y + h * hzf
    b = hall(x, y, w, h, hz, x + w * 0.5, **kw)
    yb = y + h * 0.93
    ph = stand_h(yb, hz)
    cx = x + w * person_x
    return b, hz, yb, ph, cx


def p_half():
    Wd, Hd = 760, 400
    s = card(20, 10, 720, 380, '半合成：上面换掉，下面留着', VIO1)
    x0, y0, w, h = 40, 58, 440, 316
    b, hz, yb, ph, cx = hall_photo(x0, y0, w, h)
    seam = hz + 10
    b += contact(cx, yb, ph, 1, .5) + person(cx, yb, ph, light='left', sw=2, shade=.25)
    over = hatch(x0, y0, w, seam - y0) + f'<rect x="{x0}" y="{y0}" width="{w}" height="{seam - y0:.1f}" fill="{RED}" fill-opacity=".12"/>'
    over += f'<rect x="{x0}" y="{seam - 8:.1f}" width="{w}" height="16" fill="{YEL}" fill-opacity=".55"/>'
    s += clip_rect(x0, y0, w, h, b + over) + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
    s += clip_rect(x0, y0, w, h, person(cx, yb, ph, light='left', sw=2, shade=.25))
    tx = 500
    s += label(tx, 110, '替换：展位、人群、天花', RED1, 15)
    s += text(tx, 140, '这里换成新背景', 14, 500, MUTED)
    s += label(tx, seam + 6 - 0, '接缝带', YEL1, 15)
    s += text(tx, seam + 34, '新旧背景交界，要藏好', 14, 500, MUTED)
    s += label(tx, 300, '保留：人物 + 地面', MINT1, 15)
    s += text(tx, 330, '脚、影子、地面透视都是真的', 14, 500, MUTED)
    s += text(tx, 352, '最难的接触阴影不用自己画', 14, 500, MUTED)
    save('p-half', svg(Wd, Hd, s, '半合成：保留人物和地面，替换上半部分背景，交界处是接缝带'))


def mini_ground(x0, y0, w, h, hz):
    return (f'<rect x="{x0}" y="{y0}" width="{w}" height="{hz - y0:.1f}" fill="#C7D2FE"/>'
            f'<rect x="{x0}" y="{hz:.1f}" width="{w}" height="{y0 + h - hz:.1f}" fill="#D4D4D8"/>'
            + ''.join(f'<line x1="{x0 + w / 2:.1f}" y1="{hz:.1f}" x2="{x0 + w / 2 + k * w * 0.25:.1f}" y2="{y0 + h}" stroke="#A1A1AA" stroke-width="1.2"/>' for k in range(-4, 5)))


def p_seam_where():
    Wd, Hd = 760, 330
    s = ''
    data = [('地面远处，靠近视平线', True), ('顺着墙脚、台阶边', True), ('穿过腿或影子', False)]
    for k, (t, good) in enumerate(data):
        ox = 20 + k * 246
        s += card(ox, 10, 230, 310, t, MINT1 if good else RED1)
        x0, y0, w, h = ox + 12, 58, 206, 200
        hz = y0 + h * 0.42
        b = mini_ground(x0, y0, w, h, hz)
        yb = y0 + h * 0.92
        ph = stand_h(yb, hz)
        cx = x0 + w * 0.55
        if k == 1:
            b += f'<rect x="{x0}" y="{hz + 30:.1f}" width="{w}" height="10" fill="#A8A29E" stroke="{INK}" stroke-width="1.5"/>'
            sy_ = hz + 30
        elif k == 0:
            sy_ = hz + 4
        else:
            sy_ = yb - ph * 0.3
        b += cast(cx, yb, ph, ph * 0.5, -ph * 0.1, op=.4)
        seam_l = f'<line x1="{x0}" y1="{sy_:.1f}" x2="{x0 + w}" y2="{sy_:.1f}" stroke="{YEL}" stroke-width="6" stroke-opacity=".85"/>'
        b += (seam_l + person(cx, yb, ph, sw=1.5)) if good else (person(cx, yb, ph, sw=1.5) + seam_l)
        s += clip_rect(x0, y0, w, h, b) + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
        s += ok_mark(ox + 206, 34, good)
        n = ['地面在那里最窄，最好藏', '本来就有一条线，接缝不突兀', '腿和影子被切断，一眼假'][k]
        s += text(ox + 115, 290, n, 13, 700, INK if good else RED7, 'middle')
    save('p-seam-where', svg(Wd, Hd, s, '接缝放在哪里：靠近视平线的地面远处、顺着已有的线，不要穿过腿和影子'))


def p_seam_ways():
    Wd, Hd = 760, 330
    s = ''
    data = ['软过渡', '雾或光盖住', '东西压住']
    for k, t in enumerate(data):
        ox = 20 + k * 246
        s += card(ox, 10, 230, 310, t, [YEL1, VIO1, MINT1][k])
        x0, y0, w, h = ox + 12, 58, 206, 200
        hz = y0 + h * 0.5
        top = forest_hills(x0, y0, w, h, hz, mist=False)
        b = mini_ground(x0, y0, w, h, hz)
        g = uid('fd')
        if k == 0:
            b += (f'<defs><linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".8" stop-color="#fff"/>'
                  f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient><mask id="{g}m" maskUnits="userSpaceOnUse" x="{x0}" y="{y0}" width="{w}" height="{h}">'
                  f'<rect x="{x0}" y="{y0}" width="{w}" height="{hz - y0 + 24:.1f}" fill="url(#{g})"/></mask></defs><g mask="url(#{g}m)">{top}</g>')
            n = '新背景下边缘用软笔擦淡'
        elif k == 1:
            b += clip_rect(x0, y0, w, hz - y0, top) + soft_band(x0, hz - 30, w, 60, WHITE, .9)
            n = '一层薄雾横着盖住交界'
        else:
            b += clip_rect(x0, y0, w, hz - y0, top) + grass(x0, x0 + w, hz + 2, seed=k, hgt=18)
            n = '草、石块、栏杆压在交界上'
        s += clip_rect(x0, y0, w, h, b) + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
        s += text(ox + 115, 290, n, 13, 700, INK, 'middle')
    save('p-seam-ways', svg(Wd, Hd, s, '藏接缝的三种办法：软过渡、雾或光盖住、用东西压住'))


def u_floor_vp():
    x, y, w, h = LAND
    b, hz, yb, ph, cx = hall_photo(x, y, w, h)
    b += person(cx, yb, ph, sw=1.8)
    vx = x + w * 0.5
    rays = ''.join(f'<line x1="{vx:.1f}" y1="{hz:.1f}" x2="{vx + math.sin(math.radians(a)) * 600:.1f}" y2="{hz + math.cos(math.radians(a)) * 600:.1f}" stroke="{UIBLUE}" stroke-width="1.2" stroke-opacity=".7"/>' for a in range(-80, 81, 16))
    rays += f'<line x1="{x}" y1="{hz:.1f}" x2="{x + w}" y2="{hz:.1f}" stroke="{UIBLUE}" stroke-width="3"/><circle cx="{vx:.1f}" cy="{hz:.1f}" r="9" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="3"/>'
    s = guide_ui(clip_rect(x, y, w, h, b + rays) + frame_rect(LAND))
    s += badge(vx + 24, hz - 20, 1)
    s += label(x + w + 10, hz - 30, '① 透视点放在', YEL1, 14)
    s += label(x + w + 10, hz + 2, '　 地砖缝的交点', YEL1, 14)
    s += label(x + w + 10, hz + 50, '蓝色横线 = 视平线', VIO1, 14)
    s += label(36, 120, '在场照上找视平线，', WHITE, 14)
    s += label(36, 152, '新背景要对齐它', WHITE, 14)
    s += note('示意图，以实际界面为准')
    save('u-floor-vp', svg(W, H, s, '用透视指引在场照的地砖缝上找到视平线'))


def u_seam_mask():
    x, y, w, h = LANDL
    hz = y + h * 0.45
    seam = hz + 8
    newbg = courtyard(x, y, w, h, hz, x + w * 0.5)
    b, _, yb, ph, cx = hall_photo(x, y, w, h, people=False)
    b += clip_rect(x, y, w, seam - y, newbg)
    b += contact(cx, yb, ph, 1, .5) + person(cx, yb, ph, sw=1.6)
    sel = ants_path(f'M{x + 2} {seam:.1f} L{x + w - 2} {seam:.1f} L{x + w - 2} {y + h - 2} L{x + 2} {y + h - 2} Z')
    lay = layer_rows(470, 62, 300, [('人物', PINK1, 'N', False), ('蒙版', '#FFFFFF', '', True, True), ('新背景', '#FBCFE8', 'N', False), ('场照', '#CBD5E1', 'N', False)])
    s = screen(clip_rect(x, y, w, h, b) + sel + frame_rect(LANDL) + lay + bottom_bar(SEL_ROWS, active=('矩形',)), active='select')
    s += ring(*icon_pos('select'), 18)
    s += badge(462, 62 + 44 + 46 + 20, 1)
    s += badge(x + w - 20, seam + 22, 2)
    s += label(478, 330, '① 点选「新背景」的蒙版', YEL1, 14)
    s += label(478, 362, '② 矩形框住接缝以下，', YEL1, 14)
    s += label(478, 392, '　 用黑色涂满：露出场照地面', YEL1, 14)
    s += note('示意图')
    save('u-seam-mask', svg(W, H, s, '在新背景的蒙版上框住接缝以下的地面，涂黑，露出原来的场照地面'))


def u_haze():
    x, y, w, h = LAND
    hz = y + h * 0.45
    seam = hz + 8
    b, _, yb, ph, cx = hall_photo(x, y, w, h, tape=False, people=False)
    b += clip_rect(x, y, w, seam - y, courtyard(x, y, w, h, hz, x + w * 0.5))
    b += soft_band(x, seam - 34, w * 0.7, 68, WHITE, .75)
    b += contact(cx, yb, ph, 1, .5) + person(cx, yb, ph, sw=1.8)
    b += f'<circle cx="{x + w * 0.72:.1f}" cy="{seam:.1f}" r="34" fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-dasharray="5 4"/>'
    b += arrow(x + w * 0.3, seam + 46, x + w * 0.66, seam + 46, INK, 3)
    s = screen(clip_rect(x, y, w, h, b) + frame_rect(LAND), active='brush')
    s += ring(*icon_pos('brush'), 18)
    s += label(36, 452, '新建「雾」图层：气笔修饰 → 软画笔，尺寸调大；吸新背景地平线附近的天色', YEL1, 14)
    s += label(36, 488, '沿接缝横着扫两三遍，图层不透明度 30%～50%；雾不要盖到人身上', WHITE, 14)
    s += note('示意图')
    save('u-haze', svg(W, H, s, '用大号软画笔沿接缝横着画一层薄雾'))


def hall_case(kind, after):
    x, y, w, h = 20, 20, 600, 440
    hz = y + h * 0.45
    seam = hz + 8
    glossy = kind == 'neon'
    floor = '#CBD5E1'
    b, _, yb, ph, cx = hall_photo(x, y, w, h, floor=floor, glossy=glossy, tape=not after, people=not after)
    if after:
        if kind == 'hall':
            top = courtyard(x, y, w, h, hz, x + w * 0.5)
            b += f'<rect x="{x}" y="{seam:.1f}" width="{w}" height="{y + h - seam:.1f}" fill="#A8A29E" fill-opacity=".25"/>'
            b += clip_rect(x, y, w, seam - y, top) + soft_band(x, seam - 30, w, 60, WHITE, .7)
        elif kind == 'plaza':
            pass
        else:
            top = night_city(x, y, w, h, hz, x + w * 0.5, ground=False)
            bf = uid('nb')
            b += f'<rect x="{x}" y="{seam:.1f}" width="{w}" height="{y + h - seam:.1f}" fill="#1E1B4B" fill-opacity=".72"/>'
            b += blur_filter(bf, 6)
            for xx, c in [(0.12, PINK), (0.3, CYAN), (0.75, PINK), (0.9, CYAN)]:
                b += f'<rect x="{x + w * xx - 9:.1f}" y="{seam:.1f}" width="18" height="{(y + h - seam) * 0.7:.1f}" fill="{c}" fill-opacity=".45" filter="url(#{bf})"/>'
            b += clip_rect(x, y, w, seam - y, top) + soft_band(x, seam - 20, w, 40, '#A78BFA', .5)
    sh = contact(cx, yb, ph, 1, .5)
    if kind == 'neon' and after:
        b += sh + person_fx(cx, yb, ph, dark=.35, rims=[('left', PINK), ('right', CYAN)], sw=2.5)
    else:
        b += sh + person(cx, yb, ph, light='left', sw=2.5, shade=.22)
    labs = {('hall', False): '原图：展馆场照，背后全是展位和人', ('hall', True): '换成古风庭院，接缝处加薄雾',
            ('neon', False): '原图：亮面地板反着顶灯', ('neon', True): '换成夜城，地面压暗、加霓虹倒影'}
    return frame_case(b, labs[(kind, after)], after)


def plaza_case(after):
    x, y, w, h = 20, 20, 600, 440
    hz = y + h * 0.42
    seam = hz + 6
    b = plaza(x, y, w, h, hz, x + w * 0.5, people=not after)
    yb = y + h * 0.93
    ph = stand_h(yb, hz)
    cx = x + w * 0.42
    if after:
        b += f'<rect x="{x}" y="{seam:.1f}" width="{w}" height="{y + h - seam:.1f}" fill="#84CC16" fill-opacity=".12"/>'
        b += clip_rect(x, y, w, seam - y, forest_hills(x, y, w, h, hz, mist=True))
        b += soft_band(x, seam - 26, w, 52, WHITE, .65)
        b += grass(x, x + w * 0.3, seam + 6, seed=3, hgt=16) + grass(x + w * 0.62, x + w, seam + 6, seed=5, hgt=16)
    b += contact(cx, yb, ph, 1, .35) + person(cx, yb, ph, sw=2.5)
    lab = '换成远山森林：雾 + 草压住接缝' if after else '原图：室外广场，帐篷和人群'
    return frame_case(b, lab, after)


def case_hall_before():
    save('case-hall-before', hall_case('hall', False))


def case_hall_after():
    save('case-hall-after', hall_case('hall', True))


def case_neon_before():
    save('case-neon-before', hall_case('neon', False))


def case_neon_after():
    save('case-neon-after', hall_case('neon', True))


def case_plaza_before():
    save('case-plaza-before', plaza_case(False))


def case_plaza_after():
    save('case-plaza-after', plaza_case(True))



# ---------------- 7.4 ----------------
def p_pipeline():
    Wd, Hd = 760, 250
    s = ''
    steps = [('草图构思', '定故事、构图、\n视平线、光向', YEL1), ('收集素材', '按草图拍人物，\n找背景和配件', VIO1), ('合成', '摆位置、对五要素、\n加阴影', MINT1),
             ('特效', '光效、粒子、\n环境光', PINK1), ('统一调色', '渐变映射、颗粒、\n导出', '#E0F2FE')]
    for k, (t, sub, c) in enumerate(steps):
        x = 16 + k * 150
        s += f'<rect x="{x}" y="40" width="128" height="170" rx="16" fill="{c}" stroke="{INK}" stroke-width="2.5"/>'
        s += f'<circle cx="{x + 64}" cy="74" r="20" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>' + text(x + 64, 81, str(k + 1), 18, 900, INK, 'middle')
        s += text(x + 64, 124, t, 17, 800, INK, 'middle')
        for j, line in enumerate(sub.split('\n')):
            s += text(x + 64, 156 + j * 22, line, 13, 500, INK, 'middle')
        if k < 4:
            s += arrow(x + 130, 125, x + 146, 125, INK, 3)
    s += text(380, 236, '每一步都对照草图：后面的步骤只是在实现草图里已经决定好的事', 13, 600, MUTED, 'middle')
    save('p-pipeline', svg(Wd, Hd, s, '完整合成的五个阶段：草图构思、收集素材、合成、特效、统一调色'))


def sketch(x, y, w, h, notes=True):
    hz = y + h * 0.6
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#F8FAFC"/>'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{hz - y:.1f}" fill="#475569"/>'
    s += f'<path d="M{x} {hz:.1f} L{x + w * 0.2:.1f} {hz - h * 0.2:.1f} L{x + w * 0.4:.1f} {hz - h * 0.06:.1f} L{x + w * 0.62:.1f} {hz - h * 0.28:.1f} L{x + w * 0.85:.1f} {hz - h * 0.1:.1f} L{x + w} {hz - h * 0.15:.1f} L{x + w} {hz:.1f} Z" fill="#94A3B8"/>'
    s += f'<rect x="{x}" y="{hz:.1f}" width="{w}" height="{y + h - hz:.1f}" fill="#E2E8F0"/>'
    for fx, sz in [(0.1, 0.22), (0.9, 0.28)]:
        cx_ = x + w * fx
        s += f'<path d="M{cx_ - w * 0.06:.1f} {y + h} L{cx_:.1f} {y + h - h * sz:.1f} L{cx_ + w * 0.07:.1f} {y + h} Z" fill="#334155"/>'
    yb = y + h * 0.9
    ph = h * 0.55
    cx = x + w * 0.5
    hh = ph / 7
    top = yb - ph
    s += f'<ellipse cx="{cx:.1f}" cy="{top + hh * 0.5:.1f}" rx="{hh * 0.5:.1f}" ry="{hh * 0.55:.1f}" fill="#1E293B"/>'
    s += f'<path d="M{cx - hh * 0.8:.1f} {top + hh * 1.3:.1f} L{cx + hh * 0.8:.1f} {top + hh * 1.3:.1f} L{cx + hh * 1.1:.1f} {top + hh * 4:.1f} L{cx - hh * 1.1:.1f} {top + hh * 4:.1f} Z" fill="#1E293B"/>'
    s += f'<line x1="{cx - hh * 0.35:.1f}" y1="{top + hh * 4:.1f}" x2="{cx - hh * 0.35:.1f}" y2="{yb:.1f}" stroke="#1E293B" stroke-width="{hh * 0.4:.1f}"/><line x1="{cx + hh * 0.35:.1f}" y1="{top + hh * 4:.1f}" x2="{cx + hh * 0.35:.1f}" y2="{yb:.1f}" stroke="#1E293B" stroke-width="{hh * 0.4:.1f}"/>'
    s += f'<line x1="{cx + hh * 0.8:.1f}" y1="{top + hh * 1.4:.1f}" x2="{cx + hh * 1.9:.1f}" y2="{top + hh * 0.6:.1f}" stroke="#1E293B" stroke-width="{hh * 0.35:.1f}" stroke-linecap="round"/>'
    s += f'<circle cx="{cx + hh * 2.1:.1f}" cy="{top + hh * 0.4:.1f}" r="{hh * 0.9:.1f}" fill="{WHITE}" stroke="{INK}" stroke-width="2" stroke-dasharray="4 3"/>'
    s += f'<line x1="{x}" y1="{top + hh * 3.2:.1f}" x2="{x + w}" y2="{top + hh * 3.2:.1f}" stroke="{RED}" stroke-width="2.5" stroke-dasharray="8 6"/>'
    if notes:
        s += label(x + 10, top + hh * 3.2 - 8, '视平线：腰（镜头 1 米）', RED1, 13)
        s += arrow(x + w - 30, y + 30, x + w - 90, y + 80, YEL, 4)
        s += label(x + w - 34, y + 30, '月光：右上', YEL1, 13, 'end')
        s += label(cx + hh * 3.2, top + hh * 0.2, '法阵光：第二光源', WHITE, 13)
        s += label(x + 10, y + h - 14, '前景冰块：最暗', WHITE, 13)
        s += label(x + w - 10, y + h - 14, '雪地：最亮', WHITE, 13, 'end')
    return s


def case_sketch():
    Wd, Hd = 640, 480
    s = clip_rect(20, 20, 600, 440, sketch(20, 20, 600, 440)) + f'<rect x="20" y="20" width="600" height="440" fill="none" stroke="{INK}" stroke-width="2.5"/>'
    save('case-sketch', svg(Wd, Hd, s, '构思草图：只用三种灰度，标出视平线、光向和第二光源'))


def ice_scene(x, y, w, h, stage=4):
    """stage 1 草图，2 背景，3 人物+阴影，4 特效+调色"""
    if stage == 1:
        return sketch(x, y, w, h, notes=False)
    hz = y + h * 0.58
    s = snowfield(x, y, w, h, hz, x + w * 0.5)
    if stage == 2:
        return s
    yb = y + h * 0.92
    ph = stand_h(yb, hz, 1.65, 1.0)
    cx = x + w * 0.5
    hh = ph / 7
    hx, hy = cx + hh * 1.9, yb - ph + hh * 0.65
    if stage >= 4:
        g = uid('glow')
        s += (f'<defs><radialGradient id="{g}"><stop offset="0" stop-color="{WHITE}" stop-opacity=".95"/><stop offset=".35" stop-color="{CYAN}" stop-opacity=".7"/>'
              f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient></defs>')
        s += f'<ellipse cx="{cx + hh * 1.0:.1f}" cy="{yb:.1f}" rx="{hh * 3:.1f}" ry="{hh * 0.6:.1f}" fill="{CYAN}" fill-opacity=".25"/>'
    s += sil_shadow(cx, yb, ph, shx=0.7, sy=0.3, op=.35, blur=1.5)
    s += contact(cx, yb, ph, 1, .6)
    if stage >= 4:
        s += person_fx(cx, yb, ph, dark=.25, rims=[('right', '#E0F2FE')], sw=max(1.5, w / 300), arm_raise=True, hand_side=1, light='left', shade=.2)
        s += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{hh * 2.2:.1f}" fill="url(#{g})"/>'
        s += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{hh * 1.1:.1f}" fill="none" stroke="{WHITE}" stroke-width="{max(1.2, w / 400):.1f}" stroke-dasharray="4 3"/>'
        rnd = random.Random(8)
        for _ in range(int(w / 6)):
            s += f'<circle cx="{x + rnd.uniform(0, w):.1f}" cy="{y + rnd.uniform(0, h):.1f}" r="{rnd.uniform(0.6, 2.4) * w / 600:.1f}" fill="{WHITE}" fill-opacity=".85"/>'
        gi = uid('tone')
        s += grad(gi, '#4338CA', '#67E8F9') + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{gi})" fill-opacity=".14"/>'
    else:
        s += person_fx(cx, yb, ph, sw=max(1.5, w / 300), arm_raise=True, hand_side=1, light='left', shade=.2)
    return s


def case_stages():
    Wd, Hd = 760, 230
    s = ''
    names = ['① 草图', '② 背景拼好', '③ 人物 + 阴影', '④ 特效 + 调色']
    for k in range(4):
        x = 16 + k * 186
        s += clip_rect(x, 20, 170, 150, ice_scene(x, 20, 170, 150, k + 1)) + f'<rect x="{x}" y="20" width="170" height="150" fill="none" stroke="{INK}" stroke-width="2"/>'
        s += text(x + 85, 196, names[k], 15, 800, INK, 'middle')
        if k < 3:
            s += arrow(x + 172, 95, x + 184, 95, INK, 2.5)
    save('case-stages', svg(Wd, Hd, s, '冰原法师案例的四个阶段'))


def case_ice_before():
    x, y, w, h = 20, 20, 600, 440
    b = studio(x, y, w, h, 0.86)
    yb = y + h * 0.92
    ph = h * 0.66
    b += f'<ellipse cx="{x + w * 0.5:.1f}" cy="{yb - 4:.1f}" rx="54" ry="9" fill="{INK}" fill-opacity=".18"/>'
    b += person_fx(x + w * 0.5, yb, ph, sw=2.5, arm_raise=True, hand_side=1, light='left', shade=.2)
    b += label(x + 20, y + 110, '按草图拍：镜头 1 米，主光在右上', WHITE, 14)
    save('case-ice-before', frame_case(b, '人物原片：灰墙前，按草图摆好姿势', False))


def case_ice_after():
    save('case-ice-after', frame_case(ice_scene(20, 20, 600, 440, 4), '完成：冰原、法阵光、雪花、统一冷色调', True))


def u_groups():
    R = (66, 66, 360, 280)
    x, y, w, h = R
    b = ice_scene(x, y, w, h, 4)
    rows = [('调色', '', '', False, False, True), ('特效', '', '', False, False, True), ('前景', '', '', False, False, True),
            ('人物', '', '', True, False, True), ('边缘光', '#E0F2FE', '添加', False, True), ('统一色调', '#A5B4FC', '柔光', False, True),
            ('人物', PINK1, 'N', False, True), ('接触阴影', '#475569', 'M', False, True), ('投影', '#475569', 'M', False, True),
            ('中景', '', '', False, False, True), ('背景', '', '', False, False, True)]
    lay = layer_rows(440, 58, 330, rows, row_h=36)
    s = screen(clip_rect(x, y, w, h, b) + frame_rect(R) + lay, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += label(60, 390, '从下往上：背景、中景、人物、', YEL1, 14)
    s += label(60, 420, '　　　　　前景、特效、调色', YEL1, 14)
    s += label(60, 460, '人物组里：投影、接触阴影在人物下面，', WHITE, 13)
    s += label(60, 490, '统一色调、边缘光剪辑到人物上面', WHITE, 13)
    s += note('示意图；图层组用向右轻滑多选后点「组」建立')
    save('u-groups', svg(W, H, s, '完整合成的图层组结构'))


if __name__ == '__main__':
    import inspect
    only = sys.argv[1:] 
    for name, f in list(globals().items()):
        if callable(f) and (name.startswith('p_') or name.startswith('u_') or name.startswith('case_')) and f.__module__ == '__main__':
            if not only or any(name.startswith(o) for o in only):
                f()
    print('done', len(os.listdir(OUT)))
