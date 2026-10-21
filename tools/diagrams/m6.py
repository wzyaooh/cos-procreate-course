"""M6 特效和氛围 的示意图。运行：python tools/diagrams/m6.py"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'diagrams', 'm6')
os.makedirs(OUT, exist_ok=True)
ALL = []


def save(name, s):
    s = s.replace('</defs>', _defs() + '</defs>', 1)
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)


def reg(f):
    ALL.append(f)
    return f


CX, CY, CW, CH = 262, 66, 276, 340   # 界面里的画布
NIGHT = '#1B2340'; NIGHT2 = '#2A3358'; GLOWB = '#38BDF8'; GLOWB2 = '#7DD3FC'; FIRE = '#F97316'; FIRE2 = '#FACC15'
GOLD = '#FDE68A'; SAKURA = '#F9A8D4'


# ---------------- 通用：滤镜（用到哪个模糊值就登记，保存时统一写进 defs） ----------------
_BL = set(); _WH = set()


def blur(uid, b):
    b = max(0.3, round(b, 1))
    _BL.add((uid, b))
    return f'url(#bl{uid}{str(b).replace(".", "_")})'


def white(uid):
    _WH.add(uid)
    return f'url(#white{uid})'


def _defs():
    s = []
    for uid, b in sorted(_BL):
        s.append(f'<filter id="bl{uid}{str(b).replace(".", "_")}" filterUnits="userSpaceOnUse" x="-2000" y="-2000" width="6000" height="6000">'
                 f'<feGaussianBlur stdDeviation="{b}"/></filter>')
    for uid in sorted(_WH):
        s.append(f'<filter id="white{uid}" filterUnits="userSpaceOnUse" x="-2000" y="-2000" width="6000" height="6000">'
                 f'<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1 0"/></filter>')
    _BL.clear(); _WH.clear()
    return ''.join(s)


def glow_line(uid, x1, y1, x2, y2, color, width, b, op=1.0):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width:.1f}" stroke-linecap="round" '
            f'opacity="{op}" filter="{blur(uid, b)}" style="mix-blend-mode:screen"/>')


def glow_dot(uid, x, y, r, color, b, op=1.0):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{color}" opacity="{op}" filter="{blur(uid, b)}" style="mix-blend-mode:screen"/>'


def star(x, y, r, color=WHITE, op=1.0, thin=0.18):
    """四角星光（闪光笔刷点出来的那种）"""
    t = r * thin
    d = f'M{x} {y - r} Q{x + t} {y - t} {x + r} {y} Q{x + t} {y + t} {x} {y + r} Q{x - t} {y + t} {x - r} {y} Q{x - t} {y - t} {x} {y - r} Z'
    return f'<path d="{d}" fill="{color}" opacity="{op}"/>'


def petal(x, y, r, rot, color=SAKURA, op=1.0, stroke=None):
    """樱花花瓣：一头尖一头带缺口"""
    d = (f'M0 {-r} Q{r * 0.9} {-r * 0.5} {r * 0.35} {r * 0.75} L0 {r * 0.45} L{-r * 0.35} {r * 0.75} Q{-r * 0.9} {-r * 0.5} 0 {-r} Z')
    st = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ''
    return f'<path d="{d}" transform="translate({x:.1f},{y:.1f}) rotate({rot:.0f})" fill="{color}" opacity="{op}"{st}/>'


def flake(x, y, r, color=WHITE, op=1.0, sw=None):
    sw = sw or max(1.2, r * 0.16)
    s = []
    for k in range(6):
        a = math.radians(k * 60)
        ex, ey = x + math.cos(a) * r, y + math.sin(a) * r
        s.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{ex:.1f}" y2="{ey:.1f}"/>')
        for f in (0.55,):
            bx, by = x + math.cos(a) * r * f, y + math.sin(a) * r * f
            for da in (-35, 35):
                b2 = math.radians(k * 60 + da)
                s.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx + math.cos(b2) * r * 0.35:.1f}" y2="{by + math.sin(b2) * r * 0.35:.1f}"/>')
    return f'<g stroke="{color}" stroke-width="{sw:.1f}" stroke-linecap="round" opacity="{op}">' + ''.join(s) + '</g>'


# ---------------- 照片场景 ----------------
def geo(x, y, w, h, fcx=0.48):
    hh = h * 0.1
    feet = y + h * 0.93
    top = feet - hh * 6.7
    cx = x + w * fcx
    hip = top + hh * 3.6
    sh_y = top + hh * 1.35
    sx = cx + hh * 0.78
    hand = (sx + hh * 1.1, sh_y - hh * 0.7)
    tip = (hand[0] + hh * 0.65, hand[1] - hh * 2.6)
    base = (hand[0], hand[1] + hh * 0.17)
    return dict(hh=hh, feet=feet, top=top, cx=cx, hip=hip, sh_y=sh_y, hand=hand, tip=tip, base=base, x=x, y=y, w=w, h=h)


def background(kind, x, y, w, h, g, uid):
    s = []
    if kind == 'night':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{NIGHT}"/>')
        for i, (bx, bh) in enumerate([(0.02, 0.42), (0.18, 0.55), (0.62, 0.48), (0.8, 0.6)]):
            s.append(f'<rect x="{x + w * bx:.1f}" y="{y + h * (0.78 - bh):.1f}" width="{w * 0.16:.1f}" height="{h * bh:.1f}" fill="#252E52"/>')
            for j in range(3):
                s.append(f'<rect x="{x + w * (bx + 0.04):.1f}" y="{y + h * (0.82 - bh + j * 0.09):.1f}" width="{w * 0.03:.1f}" height="{h * 0.03:.1f}" fill="#FDE68A" opacity=".55"/>')
        s.append(f'<rect x="{x}" y="{y + h * 0.78:.1f}" width="{w}" height="{h * 0.22:.1f}" fill="{NIGHT2}"/>')
    elif kind == 'day':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#DCEBF7"/>')
        s.append(f'<ellipse cx="{x + w * 0.15:.1f}" cy="{y + h * 0.72:.1f}" rx="{w * 0.2:.1f}" ry="{h * 0.2:.1f}" fill="#A7D3A0"/>')
        s.append(f'<ellipse cx="{x + w * 0.9:.1f}" cy="{y + h * 0.7:.1f}" rx="{w * 0.22:.1f}" ry="{h * 0.22:.1f}" fill="#B9DDB1"/>')
        s.append(f'<rect x="{x}" y="{y + h * 0.78:.1f}" width="{w}" height="{h * 0.22:.1f}" fill="#CFE6C4"/>')
    elif kind == 'room':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#6B5B4E"/>')
        wx, wy, ww, wh = x + w * 0.06, y + h * 0.08, w * 0.3, h * 0.34
        s.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{ww:.1f}" height="{wh:.1f}" fill="#FFF7D6"/>')
        s.append(f'<line x1="{wx + ww / 2:.1f}" y1="{wy:.1f}" x2="{wx + ww / 2:.1f}" y2="{wy + wh:.1f}" stroke="#4B3F36" stroke-width="{w * 0.012:.1f}"/>')
        s.append(f'<line x1="{wx:.1f}" y1="{wy + wh / 2:.1f}" x2="{wx + ww:.1f}" y2="{wy + wh / 2:.1f}" stroke="#4B3F36" stroke-width="{w * 0.012:.1f}"/>')
        s.append(f'<rect x="{x}" y="{y + h * 0.78:.1f}" width="{w}" height="{h * 0.22:.1f}" fill="#57493F"/>')
    elif kind == 'sakura':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#EEF2F7"/>')
        s.append(f'<g filter="{blur(uid, 2.5)}"><rect x="{x + w * 0.78:.1f}" y="{y + h * 0.25:.1f}" width="{w * 0.05:.1f}" height="{h * 0.55:.1f}" fill="#8B7468"/>'
                 f'<ellipse cx="{x + w * 0.82:.1f}" cy="{y + h * 0.26:.1f}" rx="{w * 0.3:.1f}" ry="{h * 0.16:.1f}" fill="#F7C6DC"/>'
                 f'<ellipse cx="{x + w * 0.1:.1f}" cy="{y + h * 0.18:.1f}" rx="{w * 0.25:.1f}" ry="{h * 0.13:.1f}" fill="#F9D3E3"/></g>')
        s.append(f'<rect x="{x}" y="{y + h * 0.78:.1f}" width="{w}" height="{h * 0.22:.1f}" fill="#DCD3CF"/>')
    elif kind == 'snow':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#C9D3DF"/>')
        for tx in (0.08, 0.22, 0.8):
            s.append(f'<path d="M{x + w * tx:.1f} {y + h * 0.3:.1f} l{w * 0.07:.1f} {h * 0.48:.1f} l{-w * 0.14:.1f} 0 Z" fill="#7C8BA0"/>')
        s.append(f'<rect x="{x}" y="{y + h * 0.78:.1f}" width="{w}" height="{h * 0.22:.1f}" fill="#F1F5F9"/>')
    elif kind == 'flat':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#B9B4AE"/>')
        s.append(f'<rect x="{x + w * 0.05:.1f}" y="{y + h * 0.1:.1f}" width="{w * 0.22:.1f}" height="{h * 0.5:.1f}" fill="#CFCAC2"/>')
        s.append(f'<rect x="{x + w * 0.72:.1f}" y="{y + h * 0.18:.1f}" width="{w * 0.2:.1f}" height="{h * 0.42:.1f}" fill="#A9A49C"/>')
        s.append(f'<circle cx="{x + w * 0.83:.1f}" cy="{y + h * 0.12:.1f}" r="{w * 0.05:.1f}" fill="#F4F1EA"/>')
        s.append(f'<rect x="{x}" y="{y + h * 0.78:.1f}" width="{w}" height="{h * 0.22:.1f}" fill="#9E9891"/>')
    return ''.join(s)


def person(g, pose='stand', sw=2):
    hh = g['hh']
    kw = dict(sw=sw)
    if pose == 'sword':
        kw.update(weapon=True, arm_raise=True, hand_side=1)
    elif pose in ('cast', 'palm'):
        kw.update(arm_raise=True, hand_side=1, hand_scale=1.01)
    return figure(g['cx'], g['top'], hh, g['hip'], g['feet'], **kw)


def fig_mask(uid, g, pose):
    return f'<mask id="fm{uid}" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="6000" height="6000"><g filter="{white(uid)}">{person(g, pose)}</g></mask>'


# ---------------- 特效 ----------------
def fx_saber(uid, g, color=GLOWB, flat=False, scale=1.0):
    (x1, y1), (x2, y2) = g['base'], g['tip']
    hh = g['hh'] * scale
    if flat:
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{hh * 0.2:.1f}" stroke-linecap="round"/>'
    return (glow_line(uid, x1, y1, x2, y2, color, hh * 0.75, hh * 0.45, 0.75) + glow_line(uid, x1, y1, x2, y2, color, hh * 0.3, hh * 0.12)
            + f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{WHITE}" stroke-width="{hh * 0.1:.1f}" stroke-linecap="round"/>')


def circle_art(cx, cy, r, color, sw):
    """魔法阵线稿（正圆，未加透视）"""
    s = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{sw * 1.4:.1f}"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r * 0.86:.1f}" fill="none" stroke="{color}" stroke-width="{sw:.1f}"/>',
         f'<circle cx="{cx}" cy="{cy}" r="{r * 0.5:.1f}" fill="none" stroke="{color}" stroke-width="{sw:.1f}"/>']
    pts = []
    for k in range(8):
        a = math.radians(k * 45 - 90)
        pts.append((cx + math.cos(a) * r * 0.86, cy + math.sin(a) * r * 0.86))
    for k in range(8):
        a, b = pts[k], pts[(k + 3) % 8]
        s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{color}" stroke-width="{sw * 0.8:.1f}"/>')
    for k in range(8):
        a = math.radians(k * 45 - 67.5)
        rx, ry = cx + math.cos(a) * r * 0.93, cy + math.sin(a) * r * 0.93
        s.append(f'<circle cx="{rx:.1f}" cy="{ry:.1f}" r="{r * 0.035:.1f}" fill="{color}"/>')
    return ''.join(s)


def fx_circle(uid, cx, cy, r, squash=0.32, color='#A855F7', glow=True):
    """地面上的魔法阵：正圆线稿压扁成椭圆，加发光"""
    art = circle_art(0, 0, r, WHITE, max(1.2, r * 0.025))
    tr = f'translate({cx:.1f},{cy:.1f}) scale(1,{squash})'
    s = ''
    if glow:
        s += f'<g transform="{tr}" filter="{blur(uid, r * 0.06)}" style="mix-blend-mode:screen" opacity=".95">' + circle_art(0, 0, r, color, max(2, r * 0.07)) + '</g>'
        s += f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{r * 1.1:.1f}" ry="{r * squash * 1.2:.1f}" fill="{color}" opacity=".35" filter="{blur(uid, r * 0.2)}" style="mix-blend-mode:screen"/>'
    s += f'<g transform="{tr}">{art}</g>'
    return s


def flame_path(x, y, s, k=0):
    """一簇火焰：底部在 (x,y)，高约 2.2s"""
    return (f'M{x - s * 0.55:.1f} {y:.1f} Q{x - s * 0.75:.1f} {y - s * 0.9:.1f} {x - s * 0.2:.1f} {y - s * 1.5:.1f} '
            f'Q{x - s * 0.15:.1f} {y - s * 1.0:.1f} {x + s * 0.05:.1f} {y - s * 0.9:.1f} Q{x + s * 0.05:.1f} {y - s * 1.7:.1f} {x + s * 0.3:.1f} {y - s * 2.2:.1f} '
            f'Q{x + s * 0.45:.1f} {y - s * 1.5:.1f} {x + s * 0.35:.1f} {y - s * 1.1:.1f} Q{x + s * 0.7:.1f} {y - s * 1.2:.1f} {x + s * 0.65:.1f} {y - s * 1.6:.1f} '
            f'Q{x + s * 0.95:.1f} {y - s * 0.9:.1f} {x + s * 0.55:.1f} {y:.1f} Z')


def fx_fire(uid, x, y, s):
    return (f'<path d="{flame_path(x, y, s * 1.25)}" fill="#DC2626" opacity=".9" filter="{blur(uid, s * 0.18)}" style="mix-blend-mode:screen"/>'
            f'<path d="{flame_path(x, y, s)}" fill="{FIRE}" filter="{blur(uid, s * 0.05)}" style="mix-blend-mode:screen"/>'
            f'<path d="{flame_path(x + s * 0.05, y, s * 0.6)}" fill="{FIRE2}" filter="{blur(uid, s * 0.05)}" style="mix-blend-mode:screen"/>'
            f'<ellipse cx="{x + s * 0.05:.1f}" cy="{y - s * 0.25:.1f}" rx="{s * 0.25:.1f}" ry="{s * 0.3:.1f}" fill="#FFFBEB" filter="{blur(uid, s * 0.06)}"/>'
            + glow_dot(uid, x, y - s * 0.8, s * 1.4, FIRE, s * 0.6, 0.35))


def fx_rays(uid, sx, sy, angles, length, width, color=GOLD, op=0.5):
    s = []
    for a, wd in zip(angles, width):
        r = math.radians(a)
        ex, ey = sx + math.cos(r) * length, sy + math.sin(r) * length
        px, py = -math.sin(r), math.cos(r)
        w0, w1 = wd * 0.3, wd
        d = (f'M{sx + px * w0:.1f} {sy + py * w0:.1f} L{ex + px * w1:.1f} {ey + py * w1:.1f} L{ex - px * w1:.1f} {ey - py * w1:.1f} L{sx - px * w0:.1f} {sy - py * w0:.1f} Z')
        s.append(f'<path d="{d}" fill="{color}" opacity="{op}" filter="{blur(uid, wd * 0.35)}" style="mix-blend-mode:screen"/>')
    return ''.join(s)


def fx_flares(uid, x0, y0, x1, y1, size, color=GOLD):
    s = [glow_dot(uid, x0, y0, size * 1.2, WHITE, size * 0.5), star(x0, y0, size * 2.2, WHITE, 0.9, 0.08)]
    for t, r, c in [(0.35, 0.35, '#A5F3FC'), (0.55, 0.22, color), (0.75, 0.5, '#F0ABFC'), (1.0, 0.3, '#A5F3FC')]:
        px, py = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{size * r:.1f}" fill="{c}" opacity=".35" style="mix-blend-mode:screen"/>')
    return ''.join(s)


def scatter(seed, n, x, y, w, h):
    rnd = random.Random(seed)
    return [(x + rnd.random() * w, y + rnd.random() * h, rnd.random(), rnd.random() * 360) for _ in range(n)]


def fx_petals(uid, x, y, w, h, scale=1.0, layers=(1, 1, 1), behind=False):
    s = []
    if layers[0]:
        for px, py, k, rot in scatter(3, 26, x, y, w, h * 0.75):
            s.append(petal(px, py, (2.5 + k * 1.5) * scale, rot, '#F9A8D4', 0.85))
    if layers[1]:
        for px, py, k, rot in scatter(5, 12, x, y, w, h * 0.85):
            s.append(petal(px, py, (5 + k * 2) * scale, rot, '#F472B6', 0.95))
    if layers[2]:
        s.append(f'<g filter="{blur(uid, 2.6 * scale)}">')
        for px, py, k, rot in scatter(9, 5, x, y, w, h):
            s.append(petal(px, py, (15 + k * 8) * scale, rot, '#F472B6', 0.6))
        s.append('</g>')
    return ''.join(s)


def fx_snow(uid, x, y, w, h, scale=1.0, layers=(1, 1, 1)):
    s = []
    if layers[0]:
        for px, py, k, rot in scatter(13, 60, x, y, w, h * 0.8):
            s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{(1 + k) * scale:.1f}" fill="{WHITE}" opacity=".85"/>')
    if layers[1]:
        for px, py, k, rot in scatter(17, 16, x, y, w, h * 0.9):
            s.append(flake(px, py, (4 + k * 2) * scale, WHITE, 0.95))
    if layers[2]:
        s.append(f'<g filter="{blur(uid, 3.5 * scale)}">')
        for px, py, k, rot in scatter(19, 6, x, y, w, h):
            s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{(9 + k * 6) * scale:.1f}" fill="{WHITE}" opacity=".75"/>')
        s.append('</g>')
    return ''.join(s)


def fx_sparkles(uid, pts, color=GOLD):
    s = []
    for px, py, r in pts:
        s.append(glow_dot(uid, px, py, r * 0.6, color, r * 0.4, 0.8) + star(px, py, r, WHITE, 0.95))
    return ''.join(s)


def rim(uid, g, pose, color=GLOWB, strength=1.0, side=1):
    """剪辑在人物上的边缘光：只在人物范围内显示"""
    hh = g['hh']
    cx, top = g['cx'], g['top']
    strokes = [
        (cx + side * hh * 0.35, top + hh * 0.2, cx + side * hh * 0.45, top + hh * 1.2),   # 头发侧
        (cx + side * hh * 0.75, g['sh_y'], cx + side * hh * 0.55, g['hip'] - hh * 0.6),   # 躯干侧
        (cx + side * hh * 0.85, g['hip'], cx + side * hh * 0.4, g['feet'] - hh * 0.3),   # 裙和腿
        (g['hand'][0] - side * hh * 0.1, g['hand'][1], cx + side * hh * 0.8, g['sh_y']),   # 手臂
    ]
    s = [f'<g mask="url(#fm{uid})" style="mix-blend-mode:plus-lighter" opacity="{strength}">']
    for x1, y1, x2, y2 in strokes:
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{hh * 0.55:.1f}" stroke-linecap="round" filter="{blur(uid, hh * 0.18)}"/>')
    # 离光源近的一侧整体染一点色
    s.append(f'<ellipse cx="{g["hand"][0]:.1f}" cy="{g["hand"][1] + hh:.1f}" rx="{hh * 2.2:.1f}" ry="{hh * 3:.1f}" fill="{color}" opacity=".35" filter="{blur(uid, hh * 0.8)}"/>')
    s.append('</g>')
    return ''.join(s)


def photo(x, y, w, h, bg='night', pose='stand', fx=(), uid='a', fcx=0.48, extra='', extra_under='', pad=0):
    """一张"照片"：背景 + 人物 + 特效。返回 (svg, 几何)"""
    g = geo(x, y, w, h, fcx)
    hh = g['hh']
    s = [f'<defs><clipPath id="cp{uid}"><rect x="{x - pad}" y="{y - pad}" width="{w + 2 * pad}" height="{h + 2 * pad}"/></clipPath></defs>',
         f'<g clip-path="url(#cp{uid})">', background(bg, x - pad, y - pad, w + 2 * pad, h + 2 * pad, g, uid)]
    s.append(extra_under)
    if 'shadow' in fx:
        s.append(f'<ellipse cx="{g["cx"] - hh * 1.6:.1f}" cy="{g["feet"] - hh * 0.05:.1f}" rx="{hh * 1.9:.1f}" ry="{hh * 0.32:.1f}" fill="#000" opacity=".55" filter="{blur(uid, hh * 0.18)}" transform="rotate(-4 {g["cx"]:.1f} {g["feet"]:.1f})"/>')
    if 'circle' in fx:
        s.append(fx_circle(uid, g['cx'], g['feet'] - hh * 0.1, hh * 2.0))
    if 'contact' in fx:
        cxx = g['hand'][0] if 'saber' in fx else g['cx']
        col = GLOWB if 'saber' in fx else (FIRE if 'fire' in fx else '#C084FC')
        s.append(f'<ellipse cx="{cxx:.1f}" cy="{g["feet"]:.1f}" rx="{hh * 2.2:.1f}" ry="{hh * 0.45:.1f}" fill="{col}" opacity=".45" filter="{blur(uid, hh * 0.3)}" style="mix-blend-mode:screen"/>')
    s.append(person(g, pose))
    dim = bg in ('night',) and 'nodim' not in fx
    if dim or 'rim' in fx or 'rimp' in fx or 'rimf' in fx:
        s.append(f'<defs>{fig_mask(uid, g, pose)}</defs>')
    if dim:
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#141B38" opacity=".5" mask="url(#fm{uid})"/>')
        if 'rim' in fx:
            s.append(rim(uid, g, pose, GLOWB))
        if 'rimp' in fx:
            s.append(rim(uid, g, pose, '#C084FC', 0.8))
        if 'rimf' in fx:
            s.append(rim(uid, g, pose, FIRE, 0.9))
    if 'saber' in fx:
        s.append(fx_saber(uid, g))
    if 'flatsaber' in fx:
        s.append(fx_saber(uid, g, flat=True))
    if 'fire' in fx:
        s.append(fx_fire(uid, g['hand'][0], g['hand'][1] - hh * 0.15, hh * 0.7))
    s.append(extra)
    s.append('</g>')
    return ''.join(s), g


# ================= 界面组件（kit 里没有的） =================
_klabel = label


def label(x, y, s, fill=YEL1, size=15, anchor='start', stroke=INK):
    """同 kit.label，但不会超出 800 宽的界面图右边"""
    w = sum(1.0 if ord(c) > 255 else 0.58 for c in s) * size + 18
    if anchor == 'start' and x + w > 784:
        x = 784 - w
    return _klabel(x, y, s, fill, size, anchor, stroke)
ADJ_ITEMS = ['色相、饱和度、亮度', '颜色平衡', '曲线', '渐变映射', '高斯模糊', '动态模糊', '透视模糊', '杂色', '锐化', '泛光', '故障艺术', '半色调', '色像差', '液化', '克隆']


def adjust_menu(hl=None, pop=True, x=60, y=58, w=196):
    """调整菜单（魔棒）。hl：黄圈的项；pop：在它旁边弹出 图层 / Pencil"""
    rh = 25
    h = len(ADJ_ITEMS) * rh + 30
    s = [panel(x, y, w, h)]
    for i, it in enumerate(ADJ_ITEMS):
        yy = y + 12 + i * rh + (8 if i >= 4 else 0)
        if i == 4:
            s.append(f'<line x1="{x + 10}" y1="{yy - 6}" x2="{x + w - 10}" y2="{yy - 6}" stroke="#6B7280" stroke-width="1.5"/>')
        s.append(text(x + 16, yy + 17, it, 14, 600, UITEXT))
        if it == hl:
            s.append(ringrect(x + 5, yy + 1, w - 10, rh - 2, 6))
            if pop:
                px, py = x + w + 10, yy - 10
                s.append(f'<rect x="{px}" y="{py}" width="96" height="74" rx="10" fill="{UIPANEL}" stroke="#111827" stroke-width="1.5"/>')
                s.append(f'<rect x="{px + 6}" y="{py + 6}" width="84" height="28" rx="7" fill="{UIBLUE}"/>' + text(px + 48, py + 26, '图层', 14, 700, WHITE, 'middle'))
                s.append(text(px + 48, py + 61, 'Pencil', 14, 700, UITEXT, 'middle'))
                s.append(ringrect(px + 3, py + 3, 90, 34, 7))
    return ''.join(s)


def infobar(name, pct, x=None, y=60):
    x = x if x is not None else CX + CW / 2
    w = 190
    return (f'<rect x="{x - w / 2:.1f}" y="{y}" width="{w}" height="28" rx="8" fill="{UIBLUE}"/>'
            + text(x - w / 2 + 14, y + 19, name, 14, 800, WHITE) + text(x + w / 2 - 14, y + 19, pct, 14, 800, WHITE, 'end')
            + f'<path d="M{x - w / 2 + 22 + len(name) * 14:.1f} {y + 11} l5 6 5 -6" fill="none" stroke="{WHITE}" stroke-width="2"/>')


def filter_bar(buttons=(), active=(), sliders=(), hl=None, y=None):
    """滤镜底部工具条：上排按钮，下排滑块。sliders: [(名称, 0~1)]"""
    rows = (1 if buttons else 0) + (1 if sliders else 0)
    y = y if y is not None else SY + SH - 12 - rows * 58
    s = []
    if buttons:
        widths = [len(b) * 15 + 30 for b in buttons]
        total = sum(widths) + 6 * (len(buttons) - 1) + 16
        x = SX + SW / 2 - total / 2
        s.append(f'<rect x="{x:.1f}" y="{y}" width="{total:.1f}" height="44" rx="12" fill="{UIBAR}"/>')
        bx = x + 8
        for b, bw in zip(buttons, widths):
            s.append(f'<rect x="{bx:.1f}" y="{y + 6}" width="{bw}" height="32" rx="8" fill="{UIBLUE if b in active else UIPANEL}"/>' + text(bx + bw / 2, y + 27, b, 14, 700, UITEXT, 'middle'))
            POS[b] = (bx, y + 6, bw, 32)
            if hl == b:
                s.append(ringrect(bx - 3, y + 3, bw + 6, 38))
            bx += bw + 6
        y += 52
    if sliders:
        n = len(sliders)
        we = 110 if n <= 4 else 96
        total = n * (we + 28) + 20
        x = SX + SW / 2 - total / 2
        s.append(f'<rect x="{x:.1f}" y="{y}" width="{total:.1f}" height="58" rx="12" fill="{UIBAR}"/>')
        bx = x + 22
        for name, v in sliders:
            s.append(slider(bx, y + 36, we, name, v, hl == name))
            POS[name] = (bx, y + 36, we, 8)
            bx += we + 28
    return ''.join(s)


def lthumb(x, y, kind):
    """图层缩略图 44×34"""
    s = f'<rect x="{x}" y="{y}" width="44" height="34" rx="4" fill="{WHITE}"/>'
    if kind == 'photo':
        s += f'<rect x="{x}" y="{y}" width="44" height="34" rx="4" fill="{NIGHT}"/><path d="M{x + 22} {y + 32} q-5 -14 0 -26 q5 12 0 26" fill="{PINK}"/>'
    elif kind == 'day':
        s += f'<rect x="{x}" y="{y}" width="44" height="34" rx="4" fill="#DCEBF7"/><rect x="{x}" y="{y + 24}" width="44" height="10" fill="#CFE6C4"/><path d="M{x + 22} {y + 32} q-5 -14 0 -26 q5 12 0 26" fill="{PINK}"/>'
    elif kind == 'figure':
        s += f'<path d="M{x + 22} {y + 32} q-6 -14 0 -27 q6 12 0 27" fill="{PINK}" stroke="{INK}" stroke-width="1"/>'
        s += f'<rect x="{x}" y="{y}" width="44" height="34" rx="4" fill="url(#chk)" opacity=".25"/>'
    elif kind == 'black':
        s += f'<rect x="{x}" y="{y}" width="44" height="34" rx="4" fill="#000"/>'
    elif kind == 'glow':
        s += f'<rect x="{x}" y="{y}" width="44" height="34" rx="4" fill="#000"/><circle cx="{x + 22}" cy="{y + 17}" r="9" fill="{GLOWB2}" opacity=".8"/><circle cx="{x + 22}" cy="{y + 17}" r="4" fill="{WHITE}"/>'
    elif kind == 'line':
        s += f'<line x1="{x + 14}" y1="{y + 30}" x2="{x + 30}" y2="{y + 4}" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
    elif kind == 'blueline':
        s += f'<line x1="{x + 14}" y1="{y + 30}" x2="{x + 30}" y2="{y + 4}" stroke="{GLOWB}" stroke-width="7" stroke-linecap="round" opacity=".7"/>'
    elif kind == 'stroke':
        s += f'<path d="M{x + 30} {y + 5} q-14 10 -6 26" fill="none" stroke="{GLOWB}" stroke-width="5" stroke-linecap="round"/>'
    elif kind == 'shadow':
        s += f'<ellipse cx="{x + 18}" cy="{y + 26}" rx="14" ry="5" fill="#64748B"/>'
    elif kind == 'fire':
        s += f'<rect x="{x}" y="{y}" width="44" height="34" rx="4" fill="#000"/><path d="{flame_path(x + 22, y + 32, 12)}" fill="{FIRE}"/>'
    elif kind == 'petal':
        s += petal(x + 14, y + 12, 6, 30) + petal(x + 30, y + 22, 8, -20)
    elif kind == 'mask':
        s += f'<rect x="{x}" y="{y}" width="44" height="34" rx="4" fill="{WHITE}"/><ellipse cx="{x + 24}" cy="{y + 17}" rx="10" ry="12" fill="#000"/>'
    elif kind == 'circle':
        s += f'<rect x="{x}" y="{y}" width="44" height="34" rx="4" fill="#000"/><circle cx="{x + 22}" cy="{y + 17}" r="13" fill="none" stroke="{WHITE}" stroke-width="2"/><circle cx="{x + 22}" cy="{y + 17}" r="7" fill="none" stroke="{WHITE}" stroke-width="1.5"/>'
    elif kind == 'gray':
        s += f'<rect x="{x}" y="{y}" width="44" height="34" rx="4" fill="#6B7280"/><rect x="{x + 4}" y="{y + 4}" width="12" height="12" fill="#F3F4F6"/>'
    return s


def lpanel(layers, x=470, y=62, w=300, title='图层'):
    """自绘图层面板。layers: dict 列表，键：name, thumb, mode, sel, clip, hidden, group, hl(黄圈整行), hlmode(黄圈模式字母)"""
    rh = 50
    h = 50 + len(layers) * rh + 8
    s = [f'<defs><pattern id="chk" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="4" height="4" fill="#9CA3AF"/><rect x="4" y="4" width="4" height="4" fill="#9CA3AF"/></pattern></defs>',
         panel(x, y, w, h, title), text(x + w - 26, y + 30, '+', 24, 700, UITEXT, 'middle')]
    for i, L in enumerate(layers):
        yy = y + 44 + i * rh
        ind = 22 if L.get('clip') or L.get('child') else 0
        fill = UIBLUE if L.get('sel') else UIBAR
        if L.get('group'):
            fill = '#4B5563' if not L.get('sel') else UIBLUE
        s.append(f'<rect x="{x + 8 + ind}" y="{yy}" width="{w - 16 - ind}" height="{rh - 6}" rx="8" fill="{fill}"/>')
        if L.get('clip'):
            s.append(f'<path d="M{x + 18} {yy + 8} v18 h8" fill="none" stroke="{UITEXT}" stroke-width="2"/><path d="M{x + 24} {yy + 21} l6 5 -6 5" fill="none" stroke="{UITEXT}" stroke-width="2"/>')
        if L.get('group'):
            s.append(text(x + 20, yy + 28, '▾', 14, 800, UITEXT))
            s.append(text(x + 40, yy + 28, L['name'], 15, 800, UITEXT))
        else:
            s.append(lthumb(x + 16 + ind, yy + 5, L.get('thumb', '')))
            s.append(text(x + 70 + ind, yy + 28, L['name'], 14, 700, UITEXT))
        mode = L.get('mode', 'N')
        if mode and len(mode) > 1:
            mw = len(mode) * 12 + 10
            s.append(f'<rect x="{x + w - 38 - mw}" y="{yy + 12}" width="{mw}" height="20" rx="6" fill="{UIPANEL}"/>' + text(x + w - 38 - mw / 2, yy + 27, mode, 12, 800, UITEXT, 'middle'))
        elif mode:
            s.append(text(x + w - 46, yy + 28, mode, 14, 800, UITEXT, 'middle'))
            if L.get('hlmode'):
                s.append(ring(x + w - 46, yy + 22, 15))
        on = not L.get('hidden')
        s.append(f'<rect x="{x + w - 30}" y="{yy + 14}" width="16" height="16" rx="3" fill="{UIBLUE if on else "none"}" stroke="{UITEXT}" stroke-width="1.5"/>')
        if L.get('hl'):
            s.append(ringrect(x + 5 + ind, yy - 2, w - 10 - ind, rh - 2))
        POS['L' + str(i)] = (x + 8 + ind, yy, w - 16 - ind, rh - 6)
    return ''.join(s)


BLEND_ALL = ['正片叠底', '变暗', '颜色加深', '线性加深', '深色', '变亮', '滤色', '颜色减淡', '添加', '浅色', '覆盖', '柔光', '强光', '亮光', '线性光', '点光', '实色混合', '差值', '排除', '减去', '划分', '色相', '饱和度', '颜色', '明度']


def blend_pop(mode, opacity, x, y, w=250, show=7):
    """混合模式弹窗：顶部当前模式 + 不透明度，下面一段可滑动的模式列表"""
    i = BLEND_ALL.index(mode)
    a = max(0, min(len(BLEND_ALL) - show, i - show // 2))
    rows = BLEND_ALL[a:a + show]
    h = 92 + show * 30
    s = [panel(x, y, w, h)]
    s.append(text(x + 16, y + 28, '不透明度', 13, 700, UITEXT) + text(x + w - 16, y + 28, f'{int(opacity * 100)}%', 13, 800, UITEXT, 'end'))
    s.append(f'<rect x="{x + 16}" y="{y + 38}" width="{w - 32}" height="8" rx="4" fill="#6B7280"/><rect x="{x + 16}" y="{y + 38}" width="{(w - 32) * opacity:.1f}" height="8" rx="4" fill="{UIBLUE}"/>'
             f'<circle cx="{x + 16 + (w - 32) * opacity:.1f}" cy="{y + 42}" r="9" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>')
    s.append(f'<rect x="{x + 10}" y="{y + 56}" width="{w - 20}" height="28" rx="8" fill="{UIBAR}"/>' + text(x + w / 2, y + 76, mode + '　▾', 14, 800, WHITE, 'middle'))
    for k, r in enumerate(rows):
        yy = y + 90 + k * 30
        s.append(text(x + 20, yy + 20, r, 14, 700 if r == mode else 500, WHITE if r == mode else UIDIM))
        if r == mode:
            s.append(ringrect(x + 8, yy + 1, w - 16, 28, 6))
    return ''.join(s)


LOPTS = ['重命名', '选择', '拷贝', '填充图层', '清除', '阿尔法锁定', '蒙版', '剪辑蒙版', '绘图辅助', '反转', '参考', '向下合并', '向下组合']


def layer_opts(hl=None, x=250, y=70, w=170, rows=LOPTS):
    rh = 29
    s = [panel(x, y, w, len(rows) * rh + 14)]
    for i, r in enumerate(rows):
        yy = y + 7 + i * rh
        s.append(text(x + 16, yy + 20, r, 14, 600, UITEXT))
        if r == hl or (isinstance(hl, (list, tuple)) and r in hl):
            s.append(ringrect(x + 5, yy + 1, w - 10, rh - 2, 6))
    return ''.join(s)


def brush_lib(sets, set_hl, brushes, brush_hl=None, x=360, y=58, w=410, plus=False):
    """画笔库：左边画笔组，右边画笔（带笔划预览）"""
    rh = 34
    h = max(len(sets), len(brushes)) * rh + 60
    s = [panel(x, y, w, h), text(x + 16, y + 28, '画笔库', 17, 800, UITEXT), text(x + w - 24, y + 30, '+', 24, 700, UITEXT, 'middle')]
    if plus:
        s.append(ring(x + w - 24, y + 22, 16))
    lw = 130
    for i, st in enumerate(sets):
        yy = y + 44 + i * rh
        on = st == set_hl
        s.append(f'<rect x="{x + 8}" y="{yy}" width="{lw}" height="{rh - 4}" rx="7" fill="{UIBLUE if on else UIBAR}"/>' + text(x + 20, yy + 21, st, 14, 700, UITEXT))
        if on:
            s.append(ringrect(x + 5, yy - 3, lw + 6, rh + 2, 8))
    for i, b in enumerate(brushes):
        yy = y + 44 + i * rh
        on = b == brush_hl
        bx = x + lw + 18
        s.append(f'<rect x="{bx}" y="{yy}" width="{w - lw - 26}" height="{rh - 4}" rx="7" fill="{UIBLUE if on else UIBAR}"/>' + text(bx + 10, yy + 21, b, 14, 700, UITEXT))
        p0, p1 = bx + 100, x + w - 20
        if p1 - p0 > 40:
            q = (p1 - p0) / 4
            s.append(f'<path d="M{p0} {yy + 20} q{q:.0f} -14 {2 * q:.0f} 0 t{2 * q:.0f} -4" fill="none" stroke="{GLOWB2}" stroke-width="{3 + (i % 3)}" stroke-linecap="round" opacity=".9"/>')
        if on:
            s.append(ringrect(bx - 3, yy - 3, w - lw - 20, rh + 2, 8))
    return ''.join(s)


LUM_BRUSHES = ['闪光', '散景光', '浅色画笔', '星云', '……']
SETS = ['素描', '着墨', '气笔修饰', '涂抹', '复古', '亮度', '工业', '有机']


def copy_bar(hl, y=64, x=170):
    items = ['剪切', '拷贝', '全部拷贝', '复制', '剪切并粘贴', '粘贴']
    s = f'<rect x="{x}" y="{y}" width="460" height="46" rx="12" fill="{UIBAR}"/>'
    xx = x + 10
    for it in items:
        w = len(it) * 15 + 20
        s += f'<rect x="{xx}" y="{y + 7}" width="{w}" height="32" rx="8" fill="{UIPANEL}"/>' + text(xx + w / 2, y + 29, it, 14, 700, UITEXT, 'middle')
        POS['cp' + it] = (xx, y + 7, w, 32)
        if it == hl:
            s += ringrect(xx - 3, y + 4, w + 6, 38)
        xx += w + 6
    return s


def bbox(x, y, w, h, handles=True, color=UIBLUE):
    s = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{color}" stroke-width="2"/>'
    if handles:
        for hx, hy in [(x, y), (x + w / 2, y), (x + w, y), (x, y + h / 2), (x + w, y + h / 2), (x, y + h), (x + w / 2, y + h), (x + w, y + h)]:
            s += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="6" fill="{color}" stroke="{WHITE}" stroke-width="2"/>'
    return s


def quad(pts, handles=True):
    d = 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts) + ' Z'
    s = f'<path d="{d}" fill="none" stroke="{UIBLUE}" stroke-width="2"/>'
    if handles:
        for a, b in pts:
            s += f'<circle cx="{a:.1f}" cy="{b:.1f}" r="6" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
    return s


def eyedrop(x, y, new, cur):
    return (f'<circle cx="{x}" cy="{y}" r="34" fill="none" stroke="{WHITE}" stroke-width="14"/>'
            f'<path d="M{x - 34} {y} A34 34 0 0 1 {x + 34} {y}" fill="none" stroke="{new}" stroke-width="12"/>'
            f'<path d="M{x + 34} {y} A34 34 0 0 1 {x - 34} {y}" fill="none" stroke="{cur}" stroke-width="12"/>'
            f'<circle cx="{x}" cy="{y}" r="41" fill="none" stroke="{INK}" stroke-width="1.5"/><circle cx="{x}" cy="{y}" r="27" fill="none" stroke="{INK}" stroke-width="1.5"/>'
            f'<line x1="{x - 6}" y1="{y}" x2="{x + 6}" y2="{y}" stroke="{WHITE}" stroke-width="2"/><line x1="{x}" y1="{y - 6}" x2="{x}" y2="{y + 6}" stroke="{WHITE}" stroke-width="2"/>')


def dark_canvas(content='', x=CX, y=CY, w=CW, h=CH):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000" stroke="#94A3B8" stroke-width="1"/>' + content


def studio(props, prop_hl, rows, pad='', title='画笔工作室'):
    """画笔工作室：左边属性列表，中间设置（滑块/开关），右边绘图板。rows: [(名称, 值0~1 或 'on'/'off', 是否黄圈)]"""
    x, y, w, h = 30, 40, 740, 470
    s = [f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#000" opacity=".35"/>', panel(x, y, w, h)]
    s.append(text(x + 16, y + 28, title, 16, 800, UITEXT) + text(x + w - 18, y + 28, '完成', 15, 800, UIBLUE, 'end'))
    lw = 150
    for i, p in enumerate(props):
        yy = y + 44 + i * 30
        on = p == prop_hl
        s.append(f'<rect x="{x + 8}" y="{yy}" width="{lw}" height="26" rx="6" fill="{UIBLUE if on else UIBAR}"/>' + text(x + 18, yy + 18, p, 13, 700, UITEXT))
        if on:
            s.append(ringrect(x + 5, yy - 3, lw + 6, 32, 7))
    mx = x + lw + 22
    mw = 300
    for i, (name, v, hl) in enumerate(rows):
        yy = y + 54 + i * 44
        if isinstance(v, str) and v in ('on', 'off', 'btn'):
            s.append(text(mx, yy + 18, name, 14, 700, UITEXT))
            if v == 'btn':
                s.append(f'<rect x="{mx + mw - 70}" y="{yy}" width="70" height="26" rx="7" fill="{UIPANEL}" stroke="{UIDIM}"/>' + text(mx + mw - 35, yy + 18, '编辑', 13, 700, UITEXT, 'middle'))
            else:
                on = v == 'on'
                s.append(f'<rect x="{mx + mw - 44}" y="{yy + 2}" width="40" height="20" rx="10" fill="{UIBLUE if on else "#6B7280"}"/><circle cx="{mx + mw - (14 if on else 34)}" cy="{yy + 12}" r="8" fill="{WHITE}"/>')
            if hl:
                s.append(ringrect(mx - 8, yy - 6, mw + 16, 36))
        elif isinstance(v, str):
            s.append(text(mx, yy + 18, name, 14, 700, UITEXT) + text(mx + mw, yy + 18, v, 14, 800, UIBLUE, 'end'))
            if hl:
                s.append(ringrect(mx - 8, yy - 6, mw + 16, 36))
        else:
            s.append(slider(mx, yy + 22, mw, name, v, hl))
    px = mx + mw + 24
    s.append(f'<rect x="{px}" y="{y + 44}" width="{x + w - px - 10}" height="{h - 54}" rx="10" fill="{WHITE}"/>' + text(px + 12, y + 64, '绘图板', 13, 700, MUTED))
    s.append(pad)
    return ''.join(s), (px, y + 44, x + w - px - 10, h - 54)


STUDIO_PROPS = ['描边路径', '稳定性', '锥度', '形状', '颗粒', '渲染', '湿混', '颜色动态', '动态', 'Apple Pencil', '属性', '材质', '关于此画笔']


def hb_note(s='示意图，以实际界面为准'):
    return note(s)


# ================= 6.1 泛光、色像差、渐变映射、故障艺术 =================
def hexrgb(c):
    c = c.lstrip('#')
    return [int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def gmap_filter(fid, colors):
    rgb = [hexrgb(c) for c in colors]
    tv = [' '.join(f'{c[k]:.3f}' for c in rgb) for k in range(3)]
    return (f'<filter id="{fid}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="0.3 0.59 0.11 0 0  0.3 0.59 0.11 0 0  0.3 0.59 0.11 0 0  0 0 0 1 0"/>'
            f'<feComponentTransfer><feFuncR type="table" tableValues="{tv[0]}"/><feFuncG type="table" tableValues="{tv[1]}"/><feFuncB type="table" tableValues="{tv[2]}"/></feComponentTransfer></filter>')


def bloom_filter(fid, thr=0.7, size=8, burn=1.0):
    slope = 1 / (1 - thr)
    return (f'<filter id="{fid}" color-interpolation-filters="sRGB" x="-10%" y="-10%" width="120%" height="120%">'
            f'<feComponentTransfer in="SourceGraphic" result="hi"><feFuncR type="linear" slope="{slope:.2f}" intercept="{-thr * slope:.2f}"/><feFuncG type="linear" slope="{slope:.2f}" intercept="{-thr * slope:.2f}"/><feFuncB type="linear" slope="{slope:.2f}" intercept="{-thr * slope:.2f}"/></feComponentTransfer>'
            f'<feGaussianBlur in="hi" stdDeviation="{size}" result="bl"/>'
            f'<feComponentTransfer in="bl" result="bl2"><feFuncR type="linear" slope="{burn}"/><feFuncG type="linear" slope="{burn}"/><feFuncB type="linear" slope="{burn}"/></feComponentTransfer>'
            f'<feBlend in="bl2" in2="SourceGraphic" mode="screen"/></filter>')


def chan_filters(uid):
    m = {'R': '1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0', 'G': '0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0', 'B': '0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0'}
    return ''.join(f'<filter id="ch{k}{uid}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="{v}"/></filter>' for k, v in m.items())


def ca_radial(body, uid, fx, fy, k=0.012, box=None):
    """透视模式的色像差：红通道放大一点、蓝通道缩小一点，离焦点越远错得越多"""
    x, y, w, h = box
    s = [f'<defs>{chan_filters(uid)}</defs><g style="isolation:isolate"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000"/>']
    for ch, sc in (('R', 1 + k), ('G', 1.0), ('B', 1 - k)):
        s.append(f'<g style="mix-blend-mode:screen" filter="url(#ch{ch}{uid})"><g transform="translate({fx:.1f},{fy:.1f}) scale({sc}) translate({-fx:.1f},{-fy:.1f})">{body}</g></g>')
    s.append('</g>')
    return ''.join(s)


def ca_shift(body, uid, dx, dy=0, box=None):
    x, y, w, h = box
    s = [f'<defs>{chan_filters(uid)}</defs><g style="isolation:isolate"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000"/>']
    for ch, k in (('R', 1), ('G', 0), ('B', -1)):
        s.append(f'<g style="mix-blend-mode:screen" filter="url(#ch{ch}{uid})"><g transform="translate({dx * k},{dy * k})">{body}</g></g>')
    s.append('</g>')
    return ''.join(s)


def glitch(body, uid, box, bands, shift=5):
    """故障：几条横带左右错位 + 通道分离 + 扫描线"""
    x, y, w, h = box
    s = [ca_shift(body, uid + 'g', shift, 0, box)]
    for i, (by, bh, dx) in enumerate(bands):
        s.append(f'<defs><clipPath id="gb{uid}{i}"><rect x="{x}" y="{y + by * h:.1f}" width="{w}" height="{bh * h:.1f}"/></clipPath></defs>'
                 f'<g clip-path="url(#gb{uid}{i})"><g transform="translate({dx * w:.1f},0)">{ca_shift(body, uid + "b" + str(i), shift * 2, 0, box)}</g></g>')
    lines = ''.join(f'<rect x="{x}" y="{y + k:.1f}" width="{w}" height="1.5" fill="#000" opacity=".18"/>' for k in range(0, int(h), 5))
    s.append(lines)
    return ''.join(s)


def noise_layer(uid, box, op=0.18):
    x, y, w, h = box
    return (f'<defs><filter id="nz{uid}" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  1 0 0 0 -.5"/></filter></defs>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" filter="url(#nz{uid})" opacity="{op}"/>')


def vignette(uid, box, op=0.45):
    x, y, w, h = box
    return (f'<defs><radialGradient id="vg{uid}" cx="50%" cy="48%" r="70%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="{op}"/></radialGradient></defs>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#vg{uid})"/>')


GM_DREAM = ['#2A1B4D', '#7C4DAA', '#F2A7C9', '#FFF1F7']
GM_FILM = ['#2B1D14', '#8A5A3C', '#E8B98A', '#FFF4DE']
GM_CYBER = ['#0B1030', '#5B21B6', '#DB2777', '#5EEAD4', '#ECFEFF']


def styled(kind, x, y, w, h, uid, pose='stand', bg='flat', fx=(), base=None):
    """同一张照片的几种氛围"""
    body, g = base if base else photo(x, y, w, h, bg=bg, pose=pose, fx=fx, uid=uid + 'p', pad=int(w * 0.06))
    box = (x, y, w, h)
    res, g = _styled(kind, body, g, x, y, w, h, uid, box)
    return f'<defs><clipPath id="so{uid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#so{uid})">{res}</g>', g


def _styled(kind, body, g, x, y, w, h, uid, box):
    if kind == 'none':
        return body, g
    if kind == 'bloom':
        return f'<defs>{bloom_filter("bf" + uid, 0.6, 7, 1.2)}</defs><g filter="url(#bf{uid})">{body}</g>', g
    if kind == 'dream':
        s = (f'<defs>{gmap_filter("gm" + uid, GM_DREAM)}{bloom_filter("bf" + uid, 0.72, w * 0.02, 1.0)}</defs>'
             f'<g filter="url(#bf{uid})">{body}<g filter="url(#gm{uid})" opacity=".4">{body}</g></g>')
        return s, g
    if kind == 'film':
        fxp, fyp = g['cx'], g['top'] + g['hh'] * 0.6
        inner = f'{body}<g filter="url(#gm{uid})" opacity=".45">{body}</g>'
        s = (f'<defs>{gmap_filter("gm" + uid, GM_FILM)}</defs>' + ca_radial(inner, uid, fxp, fyp, 0.012, box)
             + noise_layer(uid, box, 0.22) + vignette(uid, box))
        return s, g
    if kind == 'cyber':
        inner = f'{body}<g filter="url(#gm{uid})" opacity=".75">{body}</g>'
        s = f'<defs>{gmap_filter("gm" + uid, GM_CYBER)}</defs>' + glitch(inner, uid, box, [(0.18, 0.05, 0.03), (0.47, 0.03, -0.04), (0.71, 0.06, 0.025)], max(2, w * 0.006))
        return s, g
    if kind == 'gmap':
        return f'<defs>{gmap_filter("gm" + uid, GM_DREAM)}</defs>{body}<g filter="url(#gm{uid})" opacity=".45">{body}</g>', g
    if kind == 'gmapfull':
        return f'<defs>{gmap_filter("gm" + uid, GM_DREAM)}</defs><g filter="url(#gm{uid})">{body}</g>', g
    if kind == 'ca':
        return ca_radial(body, uid, g['cx'], g['top'] + g['hh'] * 0.6, 0.018, box), g
    if kind == 'glitch':
        return glitch(body, uid, box, [(0.2, 0.05, 0.04), (0.55, 0.04, -0.05)], 2.5), g
    if kind == 'halftone':
        pid = 'ht' + uid
        dots = (f'<defs><pattern id="{pid}" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.6" fill="#000"/></pattern></defs>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pid})" opacity=".28"/>')
        return body + dots, g
    raise KeyError(kind)


# ---------- 原理图 ----------
@reg
def p_bloom():
    Wd, Hd = 760, 400
    s = [f'<defs><filter id="pb" filterUnits="userSpaceOnUse" x="-100" y="-100" width="1000" height="700"><feGaussianBlur stdDeviation="9"/></filter></defs>']
    tones = ['#1F2937', '#475569', '#7C8797', '#B4BCC8', '#E2E8F0', '#FFFFFF']
    for row, (title, thr, fill) in enumerate([('过渡 0%：所有亮度都发光，整张图发灰发雾', 0.0, RED1), ('过渡 70%：只有最亮的部分发光', 0.7, MINT1)]):
        oy = 20 + row * 180
        s.append(f'<rect x="20" y="{oy}" width="470" height="165" rx="16" fill="{NIGHT}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(label(36, oy + 32, title, fill, 14))
        for i, c in enumerate(tones):
            cx = 70 + i * 74
            lum = i / 5
            amt = max(0.0, (lum - thr) / (1 - thr)) if thr < 1 else 0
            if amt > 0:
                s.append(f'<circle cx="{cx}" cy="{oy + 102}" r="{22 + 14 * amt:.0f}" fill="{WHITE}" opacity="{0.15 + 0.55 * amt:.2f}" filter="url(#pb)"/>')
            s.append(f'<rect x="{cx - 20}" y="{oy + 82}" width="40" height="40" rx="6" fill="{c}" stroke="{WHITE}" stroke-width="1"/>')
        s.append(text(50, oy + 152, '暗', 13, 700, UIDIM) + text(450, oy + 152, '亮', 13, 700, UIDIM, 'end'))
    # 右边：尺寸和燃烧
    s.append(f'<rect x="505" y="20" width="235" height="345" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(label(520, 52, '尺寸：光晕散多远', VIO1, 14))
    for i, (r, b) in enumerate([(10, 4), (26, 12)]):
        cx = 570 + i * 110
        s.append(f'<rect x="{cx - 45}" y="70" width="90" height="90" rx="10" fill="{NIGHT}"/>')
        s.append(f'<circle cx="{cx}" cy="115" r="{r + 8}" fill="{WHITE}" opacity=".7" filter="url(#pb)"/><circle cx="{cx}" cy="115" r="9" fill="{WHITE}"/>')
        s.append(text(cx, 178, ['小', '大'][i], 13, 700, INK, 'middle'))
    s.append(label(520, 222, '燃烧：光晕有多强', PINK1, 14))
    for i, op in enumerate([0.3, 0.95]):
        cx = 570 + i * 110
        s.append(f'<rect x="{cx - 45}" y="240" width="90" height="90" rx="10" fill="{NIGHT}"/>')
        s.append(f'<circle cx="{cx}" cy="285" r="26" fill="{WHITE}" opacity="{op}" filter="url(#pb)"/><circle cx="{cx}" cy="285" r="9" fill="{WHITE}"/>')
        s.append(text(cx, 348, ['弱', '强'][i], 13, 700, INK, 'middle'))
    s.append(text(20, 390, '泛光只是"让亮的地方往外溢光"。过渡决定哪些亮度算"亮"，尺寸决定溢多远，燃烧决定溢多少。', 13, 600, MUTED))
    save('p-bloom', svg(Wd, Hd, ''.join(s), '泛光的三个参数：过渡、尺寸、燃烧'))


@reg
def p_ca():
    Wd, Hd = 760, 360
    s = [f'<rect x="20" y="20" width="340" height="320" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>',
         label(36, 52, '镜头把不同颜色的光折到不同位置', YEL1, 14)]
    # 透镜
    s.append(f'<ellipse cx="140" cy="190" rx="18" ry="80" fill="{VIO1}" stroke="{INK}" stroke-width="2.5"/>')
    for yy in (130, 250):
        s.append(f'<line x1="40" y1="{yy}" x2="140" y2="{yy}" stroke="{INK}" stroke-width="3"/>')
    s.append(text(40, 120, '白光', 13, 700))
    for c, fxp in ((RED, 300), ('#22C55E', 280), (UIBLUE, 260)):
        for yy in (130, 250):
            s.append(f'<line x1="140" y1="{yy}" x2="{fxp}" y2="190" stroke="{c}" stroke-width="2.5"/>')
    s.append(f'<line x1="300" y1="100" x2="300" y2="290" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    s.append(text(190, 312, '蓝光先聚焦，红光后聚焦', 13, 700, INK, 'middle'))
    s.append(text(190, 332, '合不到一个点上，边缘就出现红边、蓝边', 12, 500, MUTED, 'middle'))
    # 右：画面上的分布
    ox = 380
    s.append(f'<rect x="{ox}" y="20" width="360" height="320" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(label(ox + 16, 52, '透视模式：离焦点越远，色边越宽', YEL1, 14))
    px, py, pw, ph = ox + 30, 70, 300, 220
    s.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#F8FAFC" stroke="{INK}" stroke-width="2"/>')
    fx_, fy_ = px + pw / 2, py + ph / 2
    s.append(f'<circle cx="{fx_}" cy="{fy_}" r="48" fill="{MINT1}" stroke="{MINT7}" stroke-width="2" stroke-dasharray="5 4"/>')
    s.append(f'<circle cx="{fx_}" cy="{fy_}" r="8" fill="{INK}"/><circle cx="{fx_}" cy="{fy_}" r="3" fill="{WHITE}"/>')
    s.append(text(fx_, fy_ + 66, '焦点（放在脸上）', 12, 700, MINT7, 'middle'))
    for (bx, by) in [(px + 30, py + 30), (px + pw - 60, py + 30), (px + 30, py + ph - 60), (px + pw - 60, py + ph - 60), (px + pw / 2 - 15, py + 14)]:
        dx, dy = bx + 15 - fx_, by + 15 - fy_
        d = math.hypot(dx, dy) / 160
        ox_, oy_ = dx / math.hypot(dx, dy) * 5 * d, dy / math.hypot(dx, dy) * 5 * d
        s.append(f'<rect x="{bx + ox_:.1f}" y="{by + oy_:.1f}" width="30" height="30" fill="{RED}" opacity=".8"/>')
        s.append(f'<rect x="{bx - ox_:.1f}" y="{by - oy_:.1f}" width="30" height="30" fill="#06B6D4" opacity=".8"/>')
        s.append(f'<rect x="{bx}" y="{by}" width="30" height="30" fill="{INK}"/>')
    s.append(text(ox + 180, 312, '绿色虚线圈：「掉落」留出的不受影响范围', 12, 700, MUTED, 'middle'))
    s.append(text(ox + 180, 332, '边角的方块红蓝错开最多，中间几乎不变', 12, 500, MUTED, 'middle'))
    save('p-ca', svg(Wd, Hd, ''.join(s), '色像差：镜头把红蓝光折到不同位置，越往边缘越明显'))


@reg
def p_gmap():
    Wd, Hd = 760, 330
    s = [f'<defs><linearGradient id="gray" x1="0" x2="1"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#FFF"/></linearGradient>'
         f'<linearGradient id="gm" x1="0" x2="1">' + ''.join(f'<stop offset="{i / 3:.2f}" stop-color="{c}"/>' for i, c in enumerate(GM_DREAM)) + '</linearGradient></defs>']
    s.append(f'<rect x="20" y="20" width="720" height="290" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(label(36, 52, '第一步：只看明暗', YEL1, 14))
    s.append(f'<rect x="60" y="70" width="640" height="40" rx="6" fill="url(#gray)" stroke="{INK}" stroke-width="2"/>')
    s.append(label(170, 182, '第二步：按明暗查渐变条上的颜色', VIO1, 14))
    s.append(f'<rect x="60" y="190" width="640" height="40" rx="6" fill="url(#gm)" stroke="{INK}" stroke-width="2"/>')
    for t, name in [(0.12, '假发暗部'), (0.62, '皮肤'), (0.93, '高光')]:
        xx = 60 + 640 * t
        s.append(arrow(xx, 114, xx, 184, VIO7, 2.5, marker='arwv'))
        s.append(label(xx + 8, 142, name, WHITE, 12))
    s.append(text(60, 254, '左端', 13, 800) + text(60, 274, '决定暗部变成什么颜色', 12, 500, MUTED))
    s.append(text(700, 254, '右端', 13, 800, INK, 'end') + text(700, 274, '决定亮部变成什么颜色', 12, 500, MUTED, 'end'))
    s.append(text(380, 296, '每个像素都从同一根渐变条上取色，所以整张图的颜色一下子统一了', 13, 700, INK, 'middle'))
    save('p-gmap', svg(Wd, Hd, ''.join(s), '渐变映射：先看每个像素有多亮，再按亮度从渐变条上取色'))


@reg
def p_glitch():
    Wd, Hd = 760, 270
    s = []
    titles = [('伪影 / 信号：横向错位的块和线', YEL1), ('发散：红绿蓝三个通道错开', VIO1), ('波浪：画面横向扭动', PINK1)]
    for i, (t, f) in enumerate(titles):
        ox = 20 + i * 245
        s.append(f'<rect x="{ox}" y="20" width="230" height="230" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(label(ox + 10, 50, t, f, 12))
        bx, by = ox + 45, 80
        if i == 0:
            for k, dx in enumerate([0, 14, 0, -18, 0, 8, 0]):
                s.append(f'<rect x="{bx + dx}" y="{by + k * 20}" width="140" height="20" fill="{VIO2 if k % 2 else VIO}"/>')
            s.append(f'<rect x="{bx}" y="{by}" width="140" height="140" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="4 4"/>')
        elif i == 1:
            s.append(f'<g style="isolation:isolate"><rect x="{bx}" y="{by}" width="140" height="140" fill="#000"/>')
            for c, dx in (('#FF0000', 6), ('#00FF00', 0), ('#0000FF', -6)):
                s.append(f'<circle cx="{bx + 70 + dx}" cy="{by + 70}" r="40" fill="{c}" style="mix-blend-mode:screen"/>')
            s.append('</g>')
        else:
            pts = []
            for k in range(0, 141, 4):
                pts.append(f'{bx + 40 + 10 * math.sin(k / 12):.1f},{by + k}')
            s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="5"/>')
            pts = [f'{bx + 100 + 10 * math.sin(k / 12):.1f},{by + k}' for k in range(0, 141, 4)]
            s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="5"/>')
        s.append(text(ox + 115, 240, ['适合：背景、画面边缘', '适合：轻轻加一点，赛博感最强', '适合：大面积、强烈的崩坏感'][i], 12, 600, MUTED, 'middle'))
    save('p-glitch', svg(Wd, Hd, ''.join(s), '故障艺术的几种效果'))


@reg
def p_order():
    Wd, Hd = 760, 170
    steps = [('渐变映射', '先定颜色', VIO1), ('泛光', '按新明暗发光', YEL1), ('色像差', '镜头的色边', PINK1), ('故障 / 半色调', '最后一道效果', MINT1)]
    s = []
    for i, (a, b, f) in enumerate(steps):
        x = 20 + i * 186
        s.append(f'<rect x="{x}" y="30" width="160" height="90" rx="14" fill="{f}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(text(x + 80, 68, a, 17, 800, INK, 'middle') + text(x + 80, 96, b, 13, 600, MUTED, 'middle'))
        if i < 3:
            s.append(arrow(x + 164, 75, x + 182, 75, INK, 3))
    s.append(text(380, 152, '后面的效果建立在前面的结果上：泛光看亮度，渐变映射会改亮度；色像差、故障要在发光之后，色边才不会被糊掉', 12.5, 600, MUTED, 'middle'))
    save('p-order', svg(Wd, Hd, ''.join(s), '几种滤镜的先后顺序'))


# ---------- 界面图 ----------
def ph61(kind='none', uid='u'):
    return styled(kind, CX, CY, CW, CH, uid)


@reg
def u_layers_prep():
    ph, g = ph61('none', 'lp')
    lay = lpanel([dict(name='特效 · 泛光', thumb='day', mode='N', sel=True, hl=True), dict(name='原图（锁定）', thumb='day', mode='N')])
    s = screen(ph + lay, active='layers') + ring(*icon_pos('layers'), 18)
    s += text(470 + 170, 62 + 44 + 50 + 28, '🔒', 13) if False else ''
    s += f'<rect x="{470 + 300 - 70}" y="{62 + 44 + 50 + 14}" width="12" height="10" rx="2" fill="{UITEXT}"/><path d="M{470 + 300 - 68} {62 + 44 + 50 + 14} v-4 a4 4 0 0 1 8 0 v4" fill="none" stroke="{UITEXT}" stroke-width="2"/>'
    s += label(470, 240, '每种效果做在单独的副本上', YEL1, 14) + label(470, 272, '图层名写上用了什么', YEL1, 14)
    s += hb_note()
    save('u-layers-prep', svg(W, H, s, '复制原图，在副本上做特效'))


@reg
def u_adjust_menu():
    ph, g = ph61('none', 'am')
    s = screen(ph + adjust_menu('泛光'), active='adjust') + ring(*icon_pos('adjust'), 18)
    s += badge(icon_pos('adjust')[0] + 24, 60, 1)
    s += badge(60 + 196 - 14, 58 + 12 + 9 * 25 + 8 + 12, 2) + badge(60 + 196 + 10 + 96 + 16, 58 + 12 + 9 * 25 + 8 + 5, 3)
    s += label(560, 300, '① 魔棒图标打开「调整」', YEL1, 14)
    s += label(560, 332, '② 点「泛光」', YEL1, 14)
    s += label(560, 364, '③ 选「图层」：整层生效', YEL1, 14)
    s += label(560, 396, '　 Pencil：只在涂到处生效', WHITE, 13)
    s += hb_note('示意图：菜单项的顺序以实际界面为准')
    save('u-adjust-menu', svg(W, H, s, '调整菜单：泛光，选图层'))


@reg
def u_bloom():
    ph, g = ph61('bloom', 'bl')
    s = screen(ph + infobar('泛光', '30%') + filter_bar(sliders=[('过渡', 0.7), ('尺寸', 0.3), ('燃烧', 0.2)], hl='过渡'), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += f'<path d="M{CX + 60} {CY + 200} h150" stroke="{WHITE}" stroke-width="3" stroke-dasharray="6 5" marker-end="url(#arw)"/>'
    s += badge(CX + 40, CY + 200, 1) + label(CX + CW + 14, CY + 150, '① 一指左右滑：泛光程度', YEL1, 14)
    s += label(CX + CW + 14, CY + 180, '　 先到 20%～40%', WHITE, 13)
    s += badge(POS['过渡'][0] - 18, POS['过渡'][1] - 14, 2)
    s += label(CX + CW + 14, CY + 220, '② 过渡 60%～80%', YEL1, 14) + label(CX + CW + 14, CY + 250, '　 只让最亮处发光', WHITE, 13)
    s += label(CX + CW + 14, CY + 286, '③ 尺寸 20%～40%', YEL1, 14) + label(CX + CW + 14, CY + 316, '　 燃烧 10%～30%', YEL1, 14)
    s += hb_note()
    save('u-bloom', svg(W, H, s, '泛光：在画布上滑动调程度，再调过渡、尺寸、燃烧'))


@reg
def u_mask():
    ph, g = ph61('bloom', 'mk')
    lay = lpanel([dict(name='蒙版', thumb='mask', mode='', sel=True, child=True), dict(name='特效 · 泛光', thumb='day', mode='N'), dict(name='原图（锁定）', thumb='day', mode='N')])
    opts = layer_opts('蒙版', x=290, y=80)
    soft = f'<circle cx="{g["cx"]:.1f}" cy="{g["top"] + g["hh"] * 0.6:.1f}" r="{g["hh"] * 0.7:.1f}" fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-dasharray="5 4"/>'
    s = screen(ph + soft + opts + lay, active='layers') + ring(*icon_pos('layers'), 18)
    s += badge(290 + 170 + 14, 80 + 7 + 6 * 29 + 14, 1)
    s += label(470, 280, '① 在特效层上轻点两次 → 蒙版', YEL1, 14)
    s += label(470, 312, '② 在蒙版上用黑色软画笔', YEL1, 14)
    s += label(470, 344, '　 涂掉脸上的泛光（虚线圈）', WHITE, 13)
    s += label(470, 376, '　 黑色遮住，白色显示', WHITE, 13)
    s += hb_note()
    save('u-mask', svg(W, H, s, '给特效层加蒙版，擦掉脸上的效果'))


@reg
def u_ca():
    ph, g = ph61('ca', 'ca')
    fx_, fy_ = g['cx'], g['top'] + g['hh'] * 0.6
    disc = f'<circle cx="{fx_:.1f}" cy="{fy_:.1f}" r="16" fill="{INK}" opacity=".85"/><circle cx="{fx_:.1f}" cy="{fy_:.1f}" r="5" fill="{WHITE}"/>'
    s = screen(ph + disc + infobar('色像差', '12%') + filter_bar(buttons=['透视', '移动'], active=['透视'], sliders=[('过渡', 0.2), ('掉落', 0.6)], hl='掉落'), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += badge(fx_ - 30, fy_, 1) + label(CX + CW + 14, CY + 40, '① 拖焦点里的白点，放到脸上', YEL1, 14)
    s += label(CX + CW + 14, CY + 72, '　 再一指左右滑：程度 5%～15%', WHITE, 13)
    bx, by, bw, bh = POS['透视']
    s += badge(bx - 16, by + 16, 2) + label(CX + CW + 14, CY + 112, '② 底部选「透视」', YEL1, 14)
    s += badge(POS['掉落'][0] - 18, POS['掉落'][1] - 14, 3)
    s += label(CX + CW + 14, CY + 150, '③ 掉落 50%～70%', YEL1, 14) + label(CX + CW + 14, CY + 180, '　 脸周围不受影响', WHITE, 13)
    s += label(CX + CW + 14, CY + 214, '　 过渡低一点，色边更柔', WHITE, 13)
    s += hb_note()
    save('u-ca', svg(W, H, s, '色像差：透视模式，焦点放在脸上'))


GM_PRESETS = [('神秘', ['#1E1B4B', '#7C3AED', '#F5D0FE']), ('微风', ['#134E4A', '#5EEAD4', '#F0FDFA']), ('瞬间', ['#3F1D38', '#F472B6', '#FEF3C7']), ('威尼斯', ['#422006', '#D97706', '#FEF3C7']),
              ('火焰', ['#450A0A', '#F97316', '#FEF08A']), ('霓虹灯', ['#0B1030', '#DB2777', '#5EEAD4']), ('黑暗', ['#000000', '#334155', '#CBD5E1']), ('摩卡', ['#1C1917', '#78716C', '#F5F5F4'])]


def gm_lib(hl=None, y=380):
    x, w = 40, 720
    s = [f'<defs>' + ''.join(f'<linearGradient id="pre{i}" x1="0" x2="1">' + ''.join(f'<stop offset="{k / 2}" stop-color="{c}"/>' for k, c in enumerate(cs)) + '</linearGradient>' for i, (n, cs) in enumerate(GM_PRESETS)) + '</defs>',
         panel(x, y, w, 140), text(x + 16, y + 26, '渐变色库', 15, 800, UITEXT), text(x + w - 22, y + 28, '+', 24, 700, UITEXT, 'middle')]
    for i, (n, cs) in enumerate(GM_PRESETS):
        bx = x + 14 + i * 88
        s.append(f'<rect x="{bx}" y="{y + 44}" width="78" height="54" rx="8" fill="url(#pre{i})" stroke="{UITEXT if n == hl else "#111827"}" stroke-width="{3 if n == hl else 1}"/>')
        s.append(text(bx + 39, y + 122, n, 13, 700, UITEXT, 'middle'))
        if n == hl:
            s.append(ringrect(bx - 4, y + 40, 86, 92))
        POS['gm' + n] = (bx, y + 44)
    return ''.join(s)


@reg
def u_gmap_lib():
    ph, g = styled('gmapfull', CX, CY - 4, CW, CH - 30, 'gl')
    s = screen(ph + infobar('渐变映射', '100%', y=58) + gm_lib('神秘'), active='adjust') + ring(*icon_pos('adjust'), 18)
    s += badge(40 + 14 + 0 * 88 - 4, 380 + 44, 1)
    s += label(CX + CW + 14, CY + 60, '① 轻点一个预设，马上能看到效果', YEL1, 14)
    s += label(CX + CW + 14, CY + 92, '　 在色库里左右滑可以挨个预览', WHITE, 13)
    s += badge(40 + 720 - 48, 380 + 22, 2) + label(CX + CW + 14, CY + 124, '② 右上角「+」：自己做一个', YEL1, 14)
    s += hb_note('示意图：预设的颜色是示意')
    save('u-gmap-lib', svg(W, H, s, '渐变映射的渐变色库'))


@reg
def u_gmap_edit():
    ph, g = styled('gmapfull', CX, CY - 4, CW, CH - 30, 'ge')
    x, y, w = 40, 380, 720
    bar = (f'<defs><linearGradient id="mine" x1="0" x2="1">' + ''.join(f'<stop offset="{i / 3:.2f}" stop-color="{c}"/>' for i, c in enumerate(GM_DREAM)) + '</linearGradient></defs>'
           + panel(x, y, w, 140) + text(x + 16, y + 26, '我的渐变', 15, 800, UITEXT) + f'<rect x="{x + w - 80}" y="{y + 10}" width="64" height="26" rx="7" fill="{UIBLUE}"/>' + text(x + w - 48, y + 28, '完成', 13, 800, WHITE, 'middle')
           + f'<rect x="{x + 30}" y="{y + 60}" width="{w - 60}" height="30" rx="6" fill="url(#mine)"/>')
    dots = []
    for i, c in enumerate(GM_DREAM):
        dx = x + 30 + (w - 60) * i / 3
        dots.append(f'<circle cx="{dx:.1f}" cy="{y + 104}" r="10" fill="{c}" stroke="{WHITE}" stroke-width="3"/>')
    s = screen(ph + bar + ''.join(dots), active='adjust') + ring(*icon_pos('adjust'), 18)
    s += ring(x + 30, y + 104, 16) + badge(x + 30, y + 130, 1)
    s += ring(x + w - 30, y + 104, 16) + badge(x + w - 30, y + 130, 2)
    s += badge(x + 30 + (w - 60) * 0.5, y + 46, 3) + badge(x + w - 48, y - 6, 4)
    s += label(CX + CW + 14, CY + 40, '① 左端色点：暗部的颜色', YEL1, 14)
    s += label(CX + CW + 14, CY + 72, '　 选深紫、深蓝，别用纯黑', WHITE, 13)
    s += label(CX + CW + 14, CY + 104, '② 右端色点：亮部的颜色', YEL1, 14)
    s += label(CX + CW + 14, CY + 136, '　 选很浅的暖色，接近白', WHITE, 13)
    s += label(CX + CW + 14, CY + 168, '③ 轻点条上空白处加色点', YEL1, 14)
    s += label(CX + CW + 14, CY + 200, '④ 点名字可改名，再点「完成」', YEL1, 14)
    s += hb_note()
    save('u-gmap-edit', svg(W, H, s, '自定义渐变映射：左端暗部，右端亮部'))


@reg
def u_blend_soft():
    ph, g = ph61('gmap', 'bs')
    lay = lpanel([dict(name='渐变映射', thumb='day', mode='N', sel=True, hlmode=True), dict(name='原图（锁定）', thumb='day', mode='N')])
    pop = blend_pop('柔光', 0.35, 470 - 260, 140)
    s = screen(ph + lay + pop, active='layers') + ring(*icon_pos('layers'), 18)
    s += badge(470 + 300 - 46, 62 + 44 - 10, 1)
    s += badge(470 - 260 + 250 - 14, 140 + 30, 2) + badge(470 - 260 - 6, 140 + 90 + 3 * 30 + 15, 3)
    s += label(480, 250, '① 点图层右边的字母', YEL1, 14)
    s += label(480, 282, '② 不透明度 20%～40%', YEL1, 14)
    s += label(480, 314, '③ 模式选「柔光」或「颜色」', YEL1, 14)
    s += label(480, 346, '　 颜色：只换颜色，明暗不变', WHITE, 13)
    s += label(480, 376, '　 柔光：换颜色，也加点对比', WHITE, 13)
    s += hb_note()
    save('u-blend-soft', svg(W, H, s, '把渐变映射层改成柔光或颜色模式，降低不透明度'))


@reg
def u_glitch():
    ph, g = ph61('glitch', 'gt')
    s = screen(ph + infobar('故障艺术', '18%') + filter_bar(buttons=['伪影', '波浪', '信号', '发散'], active=['发散'], sliders=[('红移', 0.62), ('绿移', 0.5), ('蓝移', 0.38), ('缩放', 0.3)], hl='发散'), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    bx, by, bw, bh = POS['发散']
    s += badge(bx + bw + 18, by + 16, 1) + badge(POS['红移'][0] - 16, POS['红移'][1] - 14, 2)
    s += label(CX + CW + 14, CY + 40, '① 先选「发散」', YEL1, 14)
    s += label(CX + CW + 14, CY + 70, '　 只做色彩错位', WHITE, 13)
    s += label(CX + CW + 14, CY + 104, '② 红移、蓝移往两边拉', YEL1, 14)
    s += label(CX + CW + 14, CY + 134, '　 一指左右滑：10%～25%', WHITE, 13)
    s += hb_note()
    save('u-glitch', svg(W, H, s, '故障艺术：发散模式，红移、蓝移'))


@reg
def u_halftone():
    ph, g = ph61('halftone', 'ht')
    s = screen(ph + infobar('半色调', '15%') + filter_bar(buttons=['全彩', '丝印', '报纸'], active=['全彩'], hl='全彩'), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += label(CX + CW + 14, CY + 40, '一指左右滑：网点大小', YEL1, 14)
    s += label(CX + CW + 14, CY + 72, '全彩：保留原来的颜色', WHITE, 13)
    s += label(CX + CW + 14, CY + 100, '报纸：黑白网点，适合漫画风', WHITE, 13)
    s += hb_note()
    save('u-halftone', svg(W, H, s, '半色调：全彩、丝印、报纸'))


# ---------- 案例 ----------
def case61(kind, name, lab, fill):
    body, g = styled(kind, 20, 20, 600, 480, 'c' + name.replace('-', ''))
    s = body + label(34, 56, lab, fill, 16)
    save(name, svg(640, 520, s, lab))


@reg
def cases61():
    case61('none', 'case-61-before', '修之前：阴天街拍，灰、平、没有气氛', YEL1)
    case61('dream', 'case-61-dream', '梦幻：粉紫渐变映射 + 泛光', VIO1)
    case61('film', 'case-61-film', '胶片：暖色渐变映射 + 色像差 + 杂色 + 暗角', YEL1)
    case61('cyber', 'case-61-cyber', '赛博：青品渐变映射 + 故障艺术', PINK1)


# ================= 6.2 叠加光效素材 =================
def gray(v):
    v = max(0, min(255, int(v)))
    return f'#{v:02X}{v:02X}{v:02X}'


@reg
def p_blend_math():
    Wd, Hd = 760, 360
    s = [f'<rect x="20" y="20" width="720" height="320" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>']
    cols = ['光效像素', '正常', '滤色', '添加']
    xs = [250, 380, 500, 620]
    s.append(text(60, 62, '照片原来这里的亮度：120（满分 255）', 14, 800))
    s.append(f'<rect x="60" y="76" width="60" height="30" rx="5" fill="{gray(120)}" stroke="{INK}" stroke-width="1.5"/>')
    for x, c in zip(xs, cols):
        s.append(text(x + 30, 134, c, 14, 800, INK, 'middle'))
    rows = [('黑色', 0), ('暗光', 80), ('亮光', 200)]
    for i, (nm, v) in enumerate(rows):
        y = 150 + i * 58
        screen_v = 255 - (255 - 120) * (255 - v) / 255
        add_v = 120 + v
        vals = [v, v, screen_v, add_v]
        s.append(text(60, y + 30, nm, 15, 800))
        for x, val in zip(xs, vals):
            shown = min(255, val)
            s.append(f'<rect x="{x}" y="{y}" width="60" height="44" rx="6" fill="{gray(shown)}" stroke="{INK}" stroke-width="1.5"/>')
            tcol = WHITE if shown < 140 else INK
            s.append(text(x + 30, y + 28, str(int(round(val))) if val <= 255 else f'{int(val)}→255', 12 if val > 255 else 13, 800, tcol, 'middle'))
        if i == 0:
            s.append(ringrect(xs[2] - 6, y - 4, 192, 52))
    s.append(text(60, 326, '黑色那一行：滤色和添加都等于原来的 120，黑底"消失"了；正常模式会把照片盖成黑色。', 13, 700, VIO7))
    save('p-blend-math', svg(Wd, Hd, ''.join(s), '滤色和添加为什么能去掉黑底：黑色是 0，叠上去不改变原图'))


@reg
def p_core():
    Wd, Hd = 760, 330
    s = [f'<rect x="20" y="20" width="440" height="290" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>', label(36, 52, '从中心往外，光的强度怎么变', YEL1, 14)]
    ox, oy, gw, gh = 60, 92, 380, 168
    s.append(f'<line x1="{ox}" y1="{oy + gh}" x2="{ox + gw}" y2="{oy + gh}" stroke="{INK}" stroke-width="2" marker-end="url(#arw)"/>')
    s.append(f'<line x1="{ox}" y1="{oy + gh}" x2="{ox}" y2="{oy - 6}" stroke="{INK}" stroke-width="2" marker-end="url(#arw)"/>')
    s.append(f'<line x1="{ox}" y1="{oy + 30}" x2="{ox + gw}" y2="{oy + 30}" stroke="{RED}" stroke-width="2" stroke-dasharray="6 4"/>')
    s.append(text(ox + gw, oy + 22, '相机能记录的最亮（纯白）', 12, 700, RED7, 'end'))
    pts = []
    for i in range(0, 101):
        t = i / 100
        val = 1.6 * math.exp(-(t * 3.2) ** 2) + 0.35 * math.exp(-t * 2.2)
        yy = oy + gh - min(val, 1.0 / 1.0) * (gh - 30) if val < 1 else oy + 30
        pts.append(f'{ox + t * gw:.1f},{yy:.1f}')
    s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{VIO7}" stroke-width="3.5"/>')
    for a, b, nm, c in [(0, 0.17, '核心', WHITE), (0.17, 0.45, '内晕', GLOWB), (0.45, 1.0, '外晕', GLOWB2)]:
        s.append(f'<rect x="{ox + a * gw + 1:.1f}" y="{oy + gh + 8}" width="{(b - a) * gw - 2:.1f}" height="16" rx="4" fill="{c}" stroke="{INK}" stroke-width="1.5"/>')
        s.append(text(ox + (a + b) / 2 * gw, oy + gh + 42, nm, 13, 800, INK, 'middle'))
    s.append(text(ox + 8, oy + 4, '亮度', 12, 700, MUTED))
    # 右：实际的样子
    s.append(f'<rect x="480" y="20" width="260" height="290" rx="16" fill="{NIGHT}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(f'<defs><filter id="pc1" filterUnits="userSpaceOnUse" x="0" y="0" width="800" height="400"><feGaussianBlur stdDeviation="22"/></filter><filter id="pc2" filterUnits="userSpaceOnUse" x="0" y="0" width="800" height="400"><feGaussianBlur stdDeviation="7"/></filter></defs>')
    s.append(f'<circle cx="610" cy="160" r="70" fill="{GLOWB2}" opacity=".55" filter="url(#pc1)"/><circle cx="610" cy="160" r="34" fill="{GLOWB}" filter="url(#pc2)"/><circle cx="610" cy="160" r="16" fill="{WHITE}"/>')
    for (lx, ly, nm) in [(610, 160, '核心：白，过曝'), (650, 205, '内晕：最饱和的颜色'), (668, 248, '外晕：大而淡')]:
        pass
    s.append(label(494, 52, '画出来的样子', WHITE, 14))
    s.append(text(610, 268, '白色核心 → 饱和内晕 → 淡淡外晕', 13, 700, UITEXT, 'middle'))
    s.append(text(610, 292, '颜色主要出现在内晕', 12, 600, UIDIM, 'middle'))
    save('p-core', svg(Wd, Hd, ''.join(s), '光的结构：核心过曝成白色，颜色在内晕，外晕大而淡'))


@reg
def p_flare_axis():
    Wd, Hd = 760, 320
    s = [f'<rect x="20" y="20" width="360" height="280" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>', label(36, 52, '镜头光斑排在一条线上', YEL1, 14)]
    px, py, pw, ph = 50, 70, 300, 200
    s.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{NIGHT}"/>')
    lx, ly = px + 40, py + 36
    cx_, cy_ = px + pw / 2, py + ph / 2
    ex, ey = 2 * cx_ - lx, 2 * cy_ - ly
    s.append(f'<line x1="{lx}" y1="{ly}" x2="{ex}" y2="{ey}" stroke="{YEL}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    s.append(star(lx, ly, 22, WHITE) + f'<circle cx="{lx}" cy="{ly}" r="8" fill="{WHITE}"/>')
    for t, r, c in [(0.45, 9, '#A5F3FC'), (0.75, 5, GOLD), (1.2, 15, '#F0ABFC'), (1.6, 8, '#A5F3FC')]:
        s.append(f'<circle cx="{lx + (cx_ - lx) * t:.1f}" cy="{ly + (cy_ - ly) * t:.1f}" r="{r}" fill="{c}" opacity=".6"/>')
    s.append(f'<path d="M{cx_ - 8} {cy_} h16 M{cx_} {cy_ - 8} v16" stroke="{WHITE}" stroke-width="2"/>')
    s.append(text(px + 150, py + ph + 22, '光源 → 画面中心 → 对面，光斑沿这条线排', 12, 700, MUTED, 'middle'))
    # 右：光束和影子
    s.append(f'<rect x="400" y="20" width="340" height="280" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(label(416, 52, '光束和影子朝同一个方向', YEL1, 14))
    s.append(f'<rect x="420" y="70" width="300" height="200" fill="#F3E3C8"/><rect x="420" y="220" width="300" height="50" fill="#D6C3A5"/>')
    s.append(f'<rect x="436" y="84" width="60" height="70" fill="#FFF7D6" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<path d="M466 120 L640 236 L600 250 L470 140 Z" fill="{GOLD}" opacity=".55"/>')
    s.append(f'<rect x="600" y="150" width="20" height="80" rx="8" fill="{VIO2}" stroke="{INK}" stroke-width="2"/><circle cx="610" cy="140" r="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<path d="M620 230 L700 262 L690 268 L612 236 Z" fill="#000" opacity=".3"/>')
    s.append(arrow(500, 110, 560, 150, VIO7, 2.5, marker='arwv') + arrow(640, 244, 690, 262, VIO7, 2.5, marker='arwv'))
    s.append(text(570, 290, '光从窗来往右下照，影子也往右下', 12, 700, MUTED, 'middle'))
    save('p-flare-axis', svg(Wd, Hd, ''.join(s), '光效的方向：光斑沿光源和画面中心的连线排列，光束和影子同方向'))


@reg
def p_graybg():
    Wd, Hd = 760, 250
    s = []
    for i, (title, bgv, ok) in enumerate([('黑底是纯黑 0：叠上去干干净净', 0, True), ('黑底是深灰 30：整块发灰，边缘一圈框', 30, False)]):
        ox = 20 + i * 370
        s.append(f'<rect x="{ox}" y="20" width="350" height="210" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(label(ox + 14, 52, title, MINT1 if ok else RED1, 13))
        px, py = ox + 30, 70
        s.append(f'<rect x="{px}" y="{py}" width="290" height="140" fill="#3B4A6B"/><rect x="{px}" y="{py + 100}" width="290" height="40" fill="#2A3358"/>')
        s.append(f'<rect x="{px + 90}" y="{py + 20}" width="160" height="100" fill="{gray(bgv)}" style="mix-blend-mode:screen"/>')
        s.append(f'<circle cx="{px + 170}" cy="{py + 70}" r="26" fill="{GLOWB}" opacity=".7" style="mix-blend-mode:screen"/><circle cx="{px + 170}" cy="{py + 70}" r="10" fill="{WHITE}"/>')
        if not ok:
            s.append(f'<rect x="{px + 90}" y="{py + 20}" width="160" height="100" fill="none" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    save('p-graybg', svg(Wd, Hd, ''.join(s), '黑底一定要纯黑，否则滤色以后整块发灰'))


# ---------- 界面 ----------
def color_value_panel(x, y, hexv='000000'):
    s = [panel(x, y, 250, 220, '颜色')]
    tabs = ['色盘', '经典', '调和', '值', '调色板']
    for i, t in enumerate(tabs):
        bx = x + 12 + i * 46
        s.append(f'<rect x="{bx}" y="{y + 182}" width="42" height="26" rx="6" fill="{UIBLUE if t == "值" else UIBAR}"/>' + text(bx + 21, y + 200, t, 12, 700, UITEXT, 'middle'))
    for i, nm in enumerate(['H', 'S', 'B']):
        yy = y + 52 + i * 30
        s.append(text(x + 16, yy + 6, nm, 13, 800, UITEXT) + f'<rect x="{x + 40}" y="{yy}" width="190" height="8" rx="4" fill="#6B7280"/>' + f'<circle cx="{x + 40}" cy="{yy + 4}" r="8" fill="{WHITE}"/>')
    s.append(text(x + 16, y + 158, '十六进制', 13, 700, UITEXT) + f'<rect x="{x + 100}" y="{y + 140}" width="130" height="28" rx="6" fill="{UIBAR}"/>' + text(x + 112, y + 159, '# ' + hexv, 14, 800, WHITE))
    s.append(ringrect(x + 94, y + 136, 142, 36))
    POS['hex'] = (x + 100, y + 140)
    return ''.join(s)


@reg
def u_black_canvas():
    can = dark_canvas()
    lay = lpanel([dict(name='光斑', thumb='', mode='N', sel=True), dict(name='背景颜色', thumb='black', mode='', hl=True)])
    cp = color_value_panel(470, 240)
    s = screen(can + lay + cp, active='layers') + ring(*icon_pos('layers'), 18)
    s += badge(470 - 14, 62 + 44 + 50 + 22, 1) + badge(470 + 250 - 4, 240 + 154, 2)
    s += label(62, 120, '① 新画布，轻点「背景颜色」', YEL1, 14)
    s += label(62, 152, '② 在「值」里把十六进制', YEL1, 14) + label(62, 182, '　 填成 000000（纯黑）', YEL1, 14)
    s += label(62, 224, '③ 光画在上面的新图层里', WHITE, 13)
    s += hb_note()
    save('u-black-canvas', svg(W, H, s, '新建画布，把背景颜色设成纯黑'))


def lights_on_black(uid, x=CX, y=CY, w=CW, h=CH, which=('flare', 'bokeh', 'beam', 'ring')):
    s = []
    if 'flare' in which:
        s.append(glow_dot(uid, x + w * 0.3, y + h * 0.22, 26, GOLD, 14, 0.8) + star(x + w * 0.3, y + h * 0.22, 40, WHITE, 0.95, 0.07) + f'<circle cx="{x + w * 0.3:.1f}" cy="{y + h * 0.22:.1f}" r="7" fill="{WHITE}"/>')
    if 'bokeh' in which:
        for i, (bx, by, r) in enumerate([(0.7, 0.15, 14), (0.82, 0.3, 9), (0.62, 0.32, 7), (0.88, 0.12, 6)]):
            s.append(f'<circle cx="{x + w * bx:.1f}" cy="{y + h * by:.1f}" r="{r}" fill="{["#F0ABFC", GOLD, "#A5F3FC", WHITE][i]}" opacity=".55" style="mix-blend-mode:screen"/>')
    if 'beam' in which:
        s.append(fx_rays(uid, x + w * 0.1, y + h * 0.45, [20, 28], w * 0.85, [12, 20], '#FDE68A', 0.75))
    if 'ring' in which:
        cx_, cy_, r = x + w * 0.5, y + h * 0.78, w * 0.2
        s.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{r:.1f}" fill="none" stroke="{GLOWB}" stroke-width="10" opacity=".7" filter="{blur(uid, 6)}" style="mix-blend-mode:screen"/>'
                 f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="{r:.1f}" fill="none" stroke="{WHITE}" stroke-width="2.5"/>')
    return ''.join(s)


@reg
def u_lum_lib():
    can = dark_canvas(lights_on_black('ll', which=('flare',)))
    s = screen(can + brush_lib(SETS, '亮度', LUM_BRUSHES, '闪光'), active='brush') + ring(*icon_pos('brush'), 18)
    s += badge(360 - 14, 58 + 44 + 5 * 34 + 14, 1) + badge(360 + 410 - 14, 58 + 44 + 14, 2)
    s += label(62, 440, '① 画笔库左边找到「亮度」', YEL1, 14)
    s += label(62, 472, '② 先选「闪光」', YEL1, 14)
    s += hb_note('示意图：组里的画笔名称和顺序以实际为准')
    save('u-lum-lib', svg(W, H, s, '画笔库：亮度组里的闪光'))


@reg
def u_paint_lights():
    can = dark_canvas(lights_on_black('pl'))
    s = screen(can, active='brush') + ring(*icon_pos('brush'), 18)
    s += badge(CX + CW * 0.3 - 44, CY + CH * 0.22, 1) + badge(CX + CW * 0.7 + 22, CY + CH * 0.15 - 14, 2)
    s += badge(CX + 18, CY + CH * 0.45 - 16, 3) + badge(CX + CW * 0.5 - CW * 0.2 - 18, CY + CH * 0.78, 4)
    s += label(CX + CW + 14, CY + 30, '① 闪光：轻点一下', YEL1, 14) + label(CX + CW + 14, CY + 60, '　 点在哪光就在哪', WHITE, 13)
    s += label(CX + CW + 14, CY + 96, '② 散景光：拖一笔', YEL1, 14) + label(CX + CW + 14, CY + 126, '　 散出一串圆斑', WHITE, 13)
    s += label(CX + CW + 14, CY + 162, '③ 光束：软画笔', YEL1, 14) + label(CX + CW + 14, CY + 192, '　 画直线后再模糊', WHITE, 13)
    s += label(CX + CW + 14, CY + 228, '④ 光环：浅色画笔', YEL1, 14) + label(CX + CW + 14, CY + 258, '　 画圈停住变正圆', WHITE, 13)
    s += label(62, 120, '每种光一个图层', YEL1, 14)
    s += hb_note()
    save('u-paint-lights', svg(W, H, s, '在黑色画布上画光斑、散景、光束、光环'))


@reg
def u_ring_quick():
    cx_, cy_, r = CX + CW / 2, CY + CH / 2, 80
    can = dark_canvas(f'<circle cx="{cx_}" cy="{cy_}" r="{r}" fill="none" stroke="{GLOWB}" stroke-width="14" opacity=".7" filter="{blur("rq", 7)}" style="mix-blend-mode:screen"/><circle cx="{cx_}" cy="{cy_}" r="{r}" fill="none" stroke="{WHITE}" stroke-width="3"/>')
    btn = f'<rect x="{CX + CW / 2 - 50}" y="64" width="100" height="30" rx="8" fill="{UIBLUE}"/>' + text(CX + CW / 2, 85, '编辑形状', 14, 800, WHITE, 'middle')
    fing = (f'<circle cx="{cx_ + r * 0.7:.1f}" cy="{cy_ - r * 0.7:.1f}" r="7" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
            f'<ellipse cx="{cx_ - 30}" cy="{cy_ + 20}" rx="10" ry="13" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
    s = screen(can + btn + fing, active='brush')
    s += badge(cx_ + r * 0.7 + 20, cy_ - r * 0.7 - 10, 1) + badge(cx_ - 52, cy_ + 20, 2) + badge(CX + CW / 2 + 66, 79, 3)
    s += label(CX + CW + 14, CY + 60, '① 画一圈，笔尖停住不抬', YEL1, 14)
    s += label(CX + CW + 14, CY + 92, '　 自动变成椭圆', WHITE, 13)
    s += label(CX + CW + 14, CY + 128, '② 另一根手指点一下画布', YEL1, 14)
    s += label(CX + CW + 14, CY + 158, '　 椭圆变正圆', WHITE, 13)
    s += label(CX + CW + 14, CY + 194, '③ 「编辑形状」可再拖节点', YEL1, 14)
    s += hb_note('示意图：速创形状')
    save('u-ring-quick', svg(W, H, s, '速创形状：画圈停住，另一指轻点变正圆'))


@reg
def u_copy_all():
    can = dark_canvas(lights_on_black('ca2', which=('beam',)))
    s = screen(can + copy_bar('全部拷贝') + finger(CX + CW + 80, 230, 3, 40))
    s += badge(CX + CW + 28, 222, 1)
    bx, by, bw, bh = POS['cp全部拷贝']
    s += badge(bx + bw / 2, by + 50, 2)
    s += label(CX + CW + 14, 330, '① 三指在画布上往下拖', YEL1, 14)
    s += label(CX + CW + 14, 362, '② 点「全部拷贝」', YEL1, 14)
    s += label(CX + CW + 14, 394, '　 黑底和光拷成一张图', WHITE, 13)
    s += hb_note()
    save('u-copy-all', svg(W, H, s, '三指下拖，全部拷贝'))


def room_with_beam(uid, x=CX, y=CY, w=CW, h=CH, beam=True, flares=False, black=False, pad=0):
    ph, g = photo(x, y, w, h, bg='room', pose='stand', uid=uid, fcx=0.62, pad=pad)
    s = ph
    sx, sy = x + w * 0.2, y + h * 0.22
    if black:
        s += f'<rect x="{x + w * 0.1:.1f}" y="{y + h * 0.15:.1f}" width="{w * 0.85:.1f}" height="{h * 0.6:.1f}" fill="#000"/>'
    if beam:
        rays = fx_rays(uid, sx, sy, [32, 40, 48], w * 1.1, [w * 0.05, w * 0.09, w * 0.04], GOLD, 0.55)
        if flares:   # 成品：用蒙版擦掉盖在脸上的部分
            fxp, fyp = g['cx'], g['top'] + g['hh'] * 0.6
            rays = (f'<defs><mask id="bm{uid}" maskUnits="userSpaceOnUse" x="-2000" y="-2000" width="6000" height="6000"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#fff"/>'
                    f'<circle cx="{fxp:.1f}" cy="{fyp:.1f}" r="{g["hh"] * 0.75:.1f}" fill="#000" filter="{blur(uid, g["hh"] * 0.25)}"/></mask></defs><g mask="url(#bm{uid})">{rays}</g>')
        s += rays
    if flares:
        s += fx_flares(uid, sx, sy, x + w * 0.85, y + h * 0.85, w * 0.035)
    s = f'<defs><clipPath id="rb{uid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#rb{uid})">{s}</g>'
    return s, g


@reg
def u_paste_screen():
    ph, g = room_with_beam('ps')
    lay = lpanel([dict(name='光束', thumb='glow', mode='N', sel=True, hlmode=True), dict(name='人像照片', thumb='photo', mode='N')])
    pop = blend_pop('滤色', 0.8, 210, 160)
    s = screen(ph + lay + pop, active='layers') + ring(*icon_pos('layers'), 18)
    s += badge(470 + 300 - 46, 62 + 44 - 10, 1) + badge(210 - 6, 160 + 90 + 3 * 30 + 15, 2)
    s += label(480, 250, '先三指下拖 →「粘贴」', WHITE, 13)
    s += label(480, 282, '① 点光束层右边的字母', YEL1, 14)
    s += label(480, 314, '② 选「滤色」（柔和）', YEL1, 14)
    s += label(480, 346, '　 或「添加」（更亮更冲）', YEL1, 14)
    s += label(480, 378, '　 黑底立刻消失', WHITE, 13)
    s += hb_note()
    save('u-paste-screen', svg(W, H, s, '粘贴进照片后，把光效层改成滤色或添加'))


@reg
def u_distort():
    ph, g = room_with_beam('ds', beam=False)
    x, y, w, h = CX, CY, CW, CH
    sx, sy = x + w * 0.2, y + h * 0.22
    beam = fx_rays('ds', sx, sy, [32, 40, 48], w * 1.1, [w * 0.05, w * 0.09, w * 0.04], GOLD, 0.55)
    pts = [(sx - 10, sy - 30), (sx + 40, sy - 40), (x + w + 6, y + h * 0.95), (x + w * 0.45, y + h * 1.0)]
    s = screen(ph + beam + quad(pts) + bottom_bar(TF_ROWS, active=('扭曲',), hl='扭曲'), active='transform') + ring(*icon_pos('transform'), 18)
    bx, by, bw, bh = POS['扭曲']
    s += badge(bx + bw / 2, by - 12, 1) + badge(pts[0][0] - 16, pts[0][1] - 4, 2)
    s += label(62, 120, '① 变换选「扭曲」', YEL1, 14)
    s += label(62, 152, '② 拖四个角：', YEL1, 14) + label(62, 182, '　 窄头对准窗户', WHITE, 13) + label(62, 210, '　 宽头落到地上', WHITE, 13)
    s += hb_note()
    save('u-distort', svg(W, H, s, '用扭曲让光束从光源方向照过来'))


@reg
def u_mask_light():
    ph, g = room_with_beam('mlg')
    face = f'<circle cx="{g["cx"]:.1f}" cy="{g["top"] + g["hh"] * 0.6:.1f}" r="{g["hh"] * 0.8:.1f}" fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-dasharray="5 4"/>'
    lay = lpanel([dict(name='蒙版', thumb='mask', mode='', sel=True, child=True, hl=True), dict(name='光束', thumb='glow', mode='滤色'), dict(name='人像照片', thumb='photo', mode='N')])
    s = screen(ph + face + lay + tool_sliders([('尺寸', 0.35), ('不透明度', 0.5)], y=SY + SH - 74), active='brush') + ring(*icon_pos('brush'), 18)
    s += label(560, 290, '在光束层的蒙版上', YEL1, 14)
    s += label(560, 322, '黑色软画笔', YEL1, 14)
    s += label(560, 354, '不透明度 30%～60%', YEL1, 14)
    s += label(560, 386, '擦掉盖住脸的部分', WHITE, 13)
    s += label(560, 416, '擦错了换白色涂回来', WHITE, 13)
    s += hb_note()
    save('u-mask-light', svg(W, H, s, '用蒙版擦掉光效多余的部分'))


@reg
def u_hsb_light():
    ph, g = room_with_beam('hs')
    s = screen(ph + infobar('色相、饱和度、亮度', '', x=CX + CW / 2) + tool_sliders([('色相', 0.47), ('饱和度', 0.62), ('亮度', 0.5)], hl='色相'), active='adjust') + ring(*icon_pos('adjust'), 18)
    s += label(CX + CW + 14, CY + 40, '在光效层上：', YEL1, 14)
    s += label(CX + CW + 14, CY + 72, '色相：往照片里光的颜色靠', WHITE, 13)
    s += label(CX + CW + 14, CY + 102, '　 窗光偏暖，就往黄橙推', WHITE, 13)
    s += label(CX + CW + 14, CY + 136, '再用图层不透明度控制强弱', YEL1, 14)
    s += hb_note()
    save('u-hsb-light', svg(W, H, s, '调光效的颜色，让它和画面光源一致'))


# ---------- 案例 ----------
@reg
def cases62():
    for name, beam, fl, lab, f in [('case-62a-before', False, False, '修之前：窗边逆光，光感不够', YEL1), ('case-62a-after', True, True, '修之后：顺着窗户方向加光束和光斑', VIO1)]:
        body, g = room_with_beam('c' + name[-5:].replace('-', ''), 20, 20, 600, 480, beam, fl)
        save(name, svg(640, 520, body + label(34 if not beam else 606, 56, lab, f, 16, 'start' if not beam else 'end'), lab))
    # 夜景施法：光球 + 光环 + 背景散景
    for name, on, lab, f in [('case-62b-before', False, '修之前：夜景举手，手里什么都没有', YEL1), ('case-62b-after', True, '修之后：手上光球 + 手腕光环 + 背景散景', VIO1)]:
        uid = 'cb' + ('a' if on else 'b')
        extra = ''
        under = ''
        ph0, g = photo(20, 20, 600, 480, bg='night', pose='cast', uid=uid + 'g')
        if on:
            hx, hy = g['hand']
            hh = g['hh']
            extra = (glow_dot(uid, hx, hy - hh * 0.5, hh * 1.0, '#C4B5FD', hh * 0.5, 0.9) + glow_dot(uid, hx, hy - hh * 0.5, hh * 0.35, WHITE, hh * 0.12)
                     + star(hx, hy - hh * 0.5, hh * 1.1, WHITE, 0.9, 0.06)
                     + f'<ellipse cx="{hx:.1f}" cy="{hy + hh * 0.1:.1f}" rx="{hh * 0.5:.1f}" ry="{hh * 0.15:.1f}" fill="none" stroke="{WHITE}" stroke-width="2"/>'
                     + f'<ellipse cx="{hx:.1f}" cy="{hy + hh * 0.1:.1f}" rx="{hh * 0.5:.1f}" ry="{hh * 0.15:.1f}" fill="none" stroke="#C4B5FD" stroke-width="8" opacity=".7" filter="{blur(uid, 4)}" style="mix-blend-mode:screen"/>')
            under = ''.join(f'<circle cx="{20 + 600 * bx:.1f}" cy="{20 + 480 * by:.1f}" r="{r}" fill="{c}" opacity=".45" filter="{blur(uid, 1.5)}" style="mix-blend-mode:screen"/>'
                            for bx, by, r, c in [(0.1, 0.3, 18, GOLD), (0.2, 0.2, 12, '#F0ABFC'), (0.78, 0.25, 22, GOLD), (0.88, 0.4, 14, '#A5F3FC'), (0.3, 0.45, 10, GOLD), (0.7, 0.5, 9, '#F0ABFC')])
        body, g = photo(20, 20, 600, 480, bg='night', pose='cast', uid=uid, extra=extra, extra_under=under)
        save(name, svg(640, 520, body + label(34 if not on else 606, 56, lab, f, 16, 'start' if not on else 'end'), lab))


# ================= 6.3 手绘光效 =================
@reg
def p_glow_layers():
    Wd, Hd = 760, 330
    s = [f'<defs><filter id="g1" filterUnits="userSpaceOnUse" x="0" y="0" width="800" height="400"><feGaussianBlur stdDeviation="4"/></filter>'
         f'<filter id="g2" filterUnits="userSpaceOnUse" x="0" y="0" width="800" height="400"><feGaussianBlur stdDeviation="14"/></filter></defs>']
    items = [('剑芯', '白色，细，硬边', None), ('内晕', '剑的颜色，小模糊', 'g1'), ('外晕', '同色，大模糊、半透明', 'g2')]
    for i, (nm, d, f) in enumerate(items):
        ox = 20 + i * 150
        s.append(f'<rect x="{ox}" y="20" width="135" height="220" rx="14" fill="#000" stroke="{INK}" stroke-width="2.5"/>')
        if f is None:
            s.append(f'<line x1="{ox + 50}" y1="210" x2="{ox + 85}" y2="60" stroke="{WHITE}" stroke-width="5" stroke-linecap="round"/>')
        else:
            s.append(f'<line x1="{ox + 50}" y1="210" x2="{ox + 85}" y2="60" stroke="{GLOWB}" stroke-width="{10 if f == "g1" else 26}" stroke-linecap="round" filter="url(#{f})" opacity="{1 if f == "g1" else .7}"/>')
        s.append(label(ox + 8, 268, nm, VIO1, 14) + text(ox + 67, 300, d, 12, 600, MUTED, 'middle'))
        s.append(text(ox + 145, 135, '+' if i < 2 else '=', 26, 900, INK, 'middle'))
    ox = 470
    s.append(f'<rect x="{ox}" y="20" width="270" height="220" rx="14" fill="{NIGHT}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(f'<g style="isolation:isolate"><line x1="{ox + 110}" y1="210" x2="{ox + 160}" y2="60" stroke="{GLOWB}" stroke-width="26" stroke-linecap="round" filter="url(#g2)" opacity=".7" style="mix-blend-mode:screen"/>'
             f'<line x1="{ox + 110}" y1="210" x2="{ox + 160}" y2="60" stroke="{GLOWB}" stroke-width="10" stroke-linecap="round" filter="url(#g1)" style="mix-blend-mode:screen"/>'
             f'<line x1="{ox + 110}" y1="210" x2="{ox + 160}" y2="60" stroke="{WHITE}" stroke-width="5" stroke-linecap="round"/></g>')
    s.append(label(ox + 8, 268, '三层都用「添加」叠起来', MINT1, 14) + text(ox + 135, 300, '中间白、边缘蓝，光往外慢慢散开', 12, 600, MUTED, 'middle'))
    save('p-glow-layers', svg(Wd, Hd, ''.join(s), '发光的三层：剑芯、内晕、外晕'))


@reg
def p_flame():
    Wd, Hd = 760, 340
    s = [f'<defs><filter id="fl" filterUnits="userSpaceOnUse" x="0" y="0" width="800" height="400"><feGaussianBlur stdDeviation="3"/></filter></defs>',
         f'<rect x="20" y="20" width="330" height="300" rx="16" fill="{NIGHT}" stroke="{INK}" stroke-width="2.5"/>']
    x, y, sz = 150, 296, 82
    s.append(f'<path d="{flame_path(x, y, sz * 1.2)}" fill="#DC2626" filter="url(#fl)"/>')
    s.append(f'<path d="{flame_path(x, y, sz)}" fill="{FIRE}" filter="url(#fl)"/>')
    s.append(f'<path d="{flame_path(x + 6, y, sz * 0.6)}" fill="{FIRE2}" filter="url(#fl)"/>')
    s.append(f'<ellipse cx="{x + 6}" cy="{y - 26}" rx="26" ry="30" fill="#FFFBEB" filter="url(#fl)"/>')
    s.append(f'<path d="M{x + 40} {y - 225} q6 -8 3 -18 q8 6 5 18 z" fill="{FIRE}" opacity=".85"/>')
    for (lx, ly, t) in [(x + 30, y - 22, '底部：白、浅黄'), (x + 50, y - 100, '中段：橙'), (x + 52, y - 190, '尖端：红，断开')]:
        s.append(f'<line x1="{lx}" y1="{ly}" x2="{lx + 30}" y2="{ly}" stroke="{WHITE}" stroke-width="1.5"/>' + text(lx + 36, ly + 5, t, 12, 700, UITEXT))
    s.append(f'<rect x="370" y="20" width="370" height="300" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    rows = [('越靠近火源越热、越亮', '底部画白和浅黄，越往上越橙、越红'),
            ('火是往上飘的气体', '每一笔从火源往上画，走 S 形，不要直上直下'),
            ('越往上越窄、越淡', '尖端收细，有几小片脱离主体飘走'),
            ('火在不停地跳动', '几簇火舌高低不一，不要对称')]
    for i, (a, b) in enumerate(rows):
        yy = 56 + i * 64
        s.append(badge(394, yy, i + 1) + text(416, yy + 5, a, 14, 800) + text(416, yy + 28, b, 12, 600, MUTED))
    save('p-flame', svg(Wd, Hd, ''.join(s), '火焰的形状和颜色'))


@reg
def p_tyndall():
    Wd, Hd = 760, 330
    s = [f'<rect x="20" y="20" width="300" height="290" rx="16" fill="#3F362F" stroke="{INK}" stroke-width="2.5"/>',
         label(36, 52, '光路被空气里的灰尘照亮', YEL1, 14)]
    s.append(f'<rect x="40" y="76" width="70" height="80" fill="#FFF7D6" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<path d="M75 116 L300 290 L230 300 L60 140 Z" fill="{GOLD}" opacity=".35"/>')
    rnd = random.Random(2)
    for _ in range(40):
        t, u = rnd.random(), rnd.random()
        px = 70 + t * 200 + u * 40 - 20
        py = 128 + t * 165
        s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.6" fill="{WHITE}" opacity=".8"/>')
    s.append(text(170, 300, '只有亮处才有光路，方向从光源往外', 12, 700, UITEXT, 'middle'))
    steps = [('复制原图', '光只能从照片里本来亮的地方来'), ('去掉饱和度', '只留明暗'), ('曲线压暗', '只剩最亮的窗、天空'),
             ('改成「添加」', '黑色部分不起作用'), ('透视模糊', '亮块沿光源方向拉成光束')]
    for i, (a, b) in enumerate(steps):
        yy = 30 + i * 56
        s.append(f'<rect x="340" y="{yy}" width="400" height="46" rx="10" fill="{[YEL1, WHITE, VIO1, MINT1, PINK1][i]}" stroke="{INK}" stroke-width="2"/>')
        s.append(badge(362, yy + 23, i + 1) + text(384, yy + 29, a, 15, 800) + text(520, yy + 29, b, 12, 600, MUTED))
    save('p-tyndall', svg(Wd, Hd, ''.join(s), '丁达尔光：从照片的亮部提取光束'))


@reg
def p_circle_persp():
    Wd, Hd = 760, 270
    s = []
    for i, (title, sq, f) in enumerate([('画的时候：正圆，正对着你', 1.0, YEL1), ('放到地上：压扁成椭圆', 0.33, MINT1), ('镜头越高，椭圆越圆', 0.55, VIO1)]):
        ox = 20 + i * 245
        s.append(f'<rect x="{ox}" y="20" width="230" height="230" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(label(ox + 10, 50, title, f, 12))
        cy = 152 if i == 0 else 175
        if i:
            s.append(f'<line x1="{ox + 15}" y1="{cy - 40}" x2="{ox + 215}" y2="{cy - 40}" stroke="{LINE}" stroke-width="2"/>')
            s.append(f'<rect x="{ox + 103}" y="{cy - 110}" width="24" height="100" rx="10" fill="{VIO2}" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<g transform="translate({ox + 115},{cy}) scale(1,{sq})">{circle_art(0, 0, 70 if i == 0 else 90, VIO7, 2.2)}</g>')
        if i:
            s.append(f'<rect x="{ox + 103}" y="{cy - 110}" width="24" height="{110 - 0:.0f}" rx="10" fill="{VIO2}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(380, 264, '椭圆的扁度要和照片里地面的透视一致：对照脚下地砖、台阶的扁度', 12, 700, MUTED, 'middle'))
    save('p-circle-persp', svg(Wd, Hd, ''.join(s), '魔法阵放到地上要按透视压扁'))


# ---------- 光剑界面 ----------
def sword_photo(uid, fx=()):
    return photo(CX, CY, CW, CH, bg='night', pose='sword', uid=uid, fx=fx)


@reg
def u_saber_core():
    ph, g = sword_photo('sc')
    (x1, y1), (x2, y2) = g['base'], g['tip']
    line = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{WHITE}" stroke-width="{g["hh"] * 0.1:.1f}" stroke-linecap="round"/>'
    lay = lpanel([dict(name='剑芯', thumb='line', mode='N', sel=True), dict(name='人像照片', thumb='photo', mode='N')])
    s = screen(ph + line + lay, active='brush') + ring(*icon_pos('brush'), 18)
    s += badge(x2 - 22, y2 + 4, 1) + badge(x1 - 22, y1 + 6, 2)
    s += label(480, 250, '新建图层「剑芯」', YEL1, 14)
    s += label(480, 282, '着墨 › 技术笔，白色', YEL1, 14)
    s += label(480, 314, '粗细 ≈ 剑身宽度的一半', WHITE, 13)
    s += label(480, 346, '① 从剑尖画到 ② 剑柄', YEL1, 14)
    s += label(480, 378, '画到底停住，变成直线', WHITE, 13)
    s += hb_note()
    save('u-saber-core', svg(W, H, s, '光剑第一层：白色剑芯'))


@reg
def u_saber_fill():
    ph, g = sword_photo('sf')
    (x1, y1), (x2, y2) = g['base'], g['tip']
    line = f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{GLOWB}" stroke-width="{g["hh"] * 0.1:.1f}" stroke-linecap="round"/>'
    lay = lpanel([dict(name='内晕', thumb='blueline', mode='N', sel=True), dict(name='剑芯', thumb='line', mode='N'), dict(name='人像照片', thumb='photo', mode='N')])
    opts = layer_opts(['阿尔法锁定', '填充图层'], x=292, y=70)
    s = screen(ph + line + opts + lay, active='layers') + ring(*icon_pos('layers'), 18)
    s += badge(292 + 170 + 12, 70 + 7 + 5 * 29 + 14, 1) + badge(292 + 170 + 12, 70 + 7 + 3 * 29 + 14, 2)
    s += label(480, 276, '剑芯复制一层，改名「内晕」', WHITE, 13)
    s += label(480, 306, '① 打开阿尔法锁定', YEL1, 14)
    s += label(480, 338, '② 选好剑的颜色，填充图层', YEL1, 14)
    s += label(480, 370, '③ 再点一次，关掉阿尔法锁定', RED1, 14)
    s += label(480, 402, '　 不关的话，模糊散不出去', WHITE, 13)
    s += hb_note()
    save('u-saber-fill', svg(W, H, s, '把剑芯副本填成剑的颜色'))


@reg
def u_saber_blur():
    ph, g = sword_photo('sb')
    (x1, y1), (x2, y2) = g['base'], g['tip']
    hh = g['hh']
    glow = glow_line('sb', x1, y1, x2, y2, GLOWB, hh * 0.3, hh * 0.12)
    s = screen(ph + glow + infobar('高斯模糊', '10%'), active='adjust') + ring(*icon_pos('adjust'), 18)
    s += f'<path d="M{CX + 40} {CY + 300} h150" stroke="{WHITE}" stroke-width="3" stroke-dasharray="6 5" marker-end="url(#arw)"/>' + badge(CX + 22, CY + 300, 1)
    s += label(CX + CW + 14, CY + 40, '在「内晕」层上：', WHITE, 13)
    s += label(CX + CW + 14, CY + 70, '调整 › 高斯模糊 › 图层', YEL1, 14)
    s += label(CX + CW + 14, CY + 102, '① 一指右滑：8%～15%', YEL1, 14)
    s += label(CX + CW + 14, CY + 134, '② 模式改成「添加」', YEL1, 14)
    s += label(CX + CW + 14, CY + 176, '再复制一层叫「外晕」', WHITE, 13)
    s += label(CX + CW + 14, CY + 206, '模糊 25%～40%，不透明度 60%', WHITE, 13)
    s += hb_note('示意图：模糊的百分比和画布大小有关，以看到的效果为准')
    save('u-saber-blur', svg(W, H, s, '给内晕加高斯模糊'))


@reg
def u_saber_layers():
    ph, g = sword_photo('sl', fx=('saber',))
    lay = lpanel([dict(name='剑芯', thumb='line', mode='添加', sel=True), dict(name='内晕', thumb='blueline', mode='添加'), dict(name='外晕', thumb='blueline', mode='添加'),
                  dict(name='手指（蒙版）', thumb='figure', mode='N'), dict(name='人像照片', thumb='photo', mode='N')])
    s = screen(ph + lay, active='layers') + ring(*icon_pos('layers'), 18)
    s += label(480, 398, '从上到下：剑芯 › 内晕 › 外晕', YEL1, 14)
    s += label(480, 430, '三层都是「添加」', YEL1, 14)
    s += label(480, 462, '握剑的手指复制到最上面', WHITE, 13)
    s += label(480, 492, '　 光就像握在手里', WHITE, 13)
    s += hb_note('示意图：实际界面右边显示的是模式的缩写字母')
    save('u-saber-layers', svg(W, H, s, '光剑的图层顺序'))


# ---------- 魔法阵界面 ----------
def sym_guides(cx, cy, r, color=UIBLUE):
    s = []
    for k in range(4):
        a = math.radians(k * 45)
        s.append(f'<line x1="{cx - math.cos(a) * r:.1f}" y1="{cy - math.sin(a) * r:.1f}" x2="{cx + math.cos(a) * r:.1f}" y2="{cy + math.sin(a) * r:.1f}" stroke="{color}" stroke-width="1.5" opacity=".9"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/><circle cx="{cx + 40}" cy="{cy}" r="6" fill="{MINT}" stroke="{WHITE}" stroke-width="2"/>')
    return ''.join(s)


SQ = (CX - 30, CY + 10, 336, 336)


@reg
def u_sym():
    x, y, w, h = SQ
    can = dark_canvas(sym_guides(x + w / 2, y + h / 2, w / 2), x, y, w, h)
    top = f'<rect x="{SX}" y="{SY}" width="{SW}" height="42" rx="16" fill="{UIBAR}"/><rect x="{SX}" y="{SY + 26}" width="{SW}" height="16" fill="{UIBAR}"/>'
    top += text(40, 41, '取消', 15, 700, UITEXT) + text(760, 41, '完成', 15, 800, UIBLUE, 'end')
    top += f'<defs><linearGradient id="hue" x1="0" x2="1">' + ''.join(f'<stop offset="{i / 6}" stop-color="hsl({i * 60},90%,60%)"/>' for i in range(7)) + '</linearGradient></defs>'
    top += f'<rect x="250" y="26" width="300" height="10" rx="5" fill="url(#hue)"/>'
    bar = bottom_bar([['2D 网格', '等距', '透视', '对称', '选项']], active=('对称',), hl='对称')
    bx, by, bw, bh = POS['选项']
    px, py = bx - 120, by - 230
    pop = panel(px, py, 200, 220) + menu_rows(px, py + 6, 200, ['垂直', '水平', '四象限', '径向', '轴向对称', '辅助绘图'], hl='径向', toggles={'轴向对称': False, '辅助绘图': True})
    s = f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>' + can + top + bar + pop
    s += badge(POS['对称'][0] + 10, POS['对称'][1] - 4, 1) + badge(bx + bw - 6, by - 4, 2) + badge(px - 14, py + 6 + 3 * 34 + 17, 3) + badge(px + 214, py + 6 + 5 * 34 + 17, 4)
    s += badge(x + w / 2 - 22, y + h / 2 - 16, 5)
    s += label(62, 110, '先打开 操作 › 画布 ›', WHITE, 13) + label(62, 138, '绘图指引 › 编辑绘图指引', WHITE, 13)
    s += label(62, 176, '① 底部选「对称」', YEL1, 14) + label(62, 208, '② 点「选项」', YEL1, 14)
    s += label(62, 240, '③ 选「径向」：分成 8 份', YEL1, 14)
    s += label(62, 272, '④「辅助绘图」保持打开', YEL1, 14)
    s += label(62, 304, '⑤ 蓝点放在画布正中', YEL1, 14)
    s += label(62, 336, '　 绿点可以旋转', WHITE, 13)
    s += hb_note()
    save('u-sym', svg(W, H, s, '绘图指引：对称，选项里选径向'))


@reg
def u_sym_draw():
    x, y, w, h = SQ
    cx, cy = x + w / 2, y + h / 2
    pat = []
    for k in range(8):
        pat.append(f'<g transform="rotate({k * 45} {cx} {cy})"><path d="M{cx} {cy - 40} L{cx + 12} {cy - 95} L{cx} {cy - 140} L{cx - 12} {cy - 95} Z" fill="none" stroke="{WHITE}" stroke-width="2.5"/>'
                   f'<circle cx="{cx}" cy="{cy - 118}" r="4" fill="{WHITE}"/></g>')
    can = dark_canvas(sym_guides(cx, cy, w / 2) + ''.join(pat), x, y, w, h)
    lay = lpanel([dict(name='花纹 · 辅助', thumb='circle', mode='N', sel=True, hl=True), dict(name='圆环', thumb='circle', mode='N'), dict(name='背景颜色', thumb='black', mode='')], x=480, w=290)
    s = screen(can + lay, active='brush') + ring(*icon_pos('brush'), 18)
    s += f'<path d="M{cx} {cy - 40} L{cx + 12} {cy - 95}" stroke="{YEL}" stroke-width="5" stroke-linecap="round"/>' + badge(cx + 30, cy - 70, 1)
    s += label(490, 290, '① 只画黄色这一笔', YEL1, 14)
    s += label(490, 322, '　 另外 7 份自动出现', WHITE, 13)
    s += label(490, 356, '图层名下有「辅助」字样', WHITE, 13)
    s += label(490, 386, '　 才会被镜像', WHITE, 13)
    s += hb_note()
    save('u-sym-draw', svg(W, H, s, '径向对称：画一份，自动复制成八份'))


@reg
def u_circle_ring():
    x, y, w, h = SQ
    cx, cy = x + w / 2, y + h / 2
    art = f'<circle cx="{cx}" cy="{cy}" r="150" fill="none" stroke="{WHITE}" stroke-width="3"/><circle cx="{cx}" cy="{cy}" r="128" fill="none" stroke="{WHITE}" stroke-width="2"/>'
    can = dark_canvas(art + f'<path d="M{cx - 8} {cy} h16 M{cx} {cy - 8} v16" stroke="{UIBLUE}" stroke-width="2"/>', x, y, w, h)
    lay = lpanel([dict(name='圆环', thumb='circle', mode='N', sel=True), dict(name='背景颜色', thumb='black', mode='')], x=480, w=290)
    opts = layer_opts('绘图辅助', x=560, y=180, w=170, rows=['重命名', '选择', '拷贝', '填充图层', '清除', '阿尔法锁定', '蒙版', '剪辑蒙版', '绘图辅助'])
    s = screen(can + lay + opts, active='layers') + ring(*icon_pos('layers'), 18)
    s += badge(560 - 14, 180 + 7 + 8 * 29 + 14, 1)
    s += label(62, 440, '① 圆环层：关掉「绘图辅助」', YEL1, 14)
    s += label(62, 472, '② 速创形状画正圆（画圈停住，另一指轻点）', YEL1, 14)
    s += label(62, 504, '③ 变换 › 对齐 打开，拖到画布中心', YEL1, 14)
    s += hb_note()
    save('u-circle-ring', svg(W, H, s, '圆环单独一层，关掉绘图辅助，用速创形状画正圆'))


@reg
def u_rot45():
    x, y, w, h = SQ
    cx, cy = x + w / 2, y + h / 2
    runes = ''
    for k in range(8):
        a = math.radians(k * 45 - 90)
        rx, ry = cx + math.cos(a) * 139, cy + math.sin(a) * 139
        col = YEL if k == 1 else WHITE
        runes += f'<g transform="rotate({k * 45} {rx:.1f} {ry:.1f})"><path d="M{rx - 7:.1f} {ry - 5:.1f} l7 10 7 -10 M{rx:.1f} {ry - 6:.1f} v12" fill="none" stroke="{col}" stroke-width="2.5"/></g>'
    art = f'<circle cx="{cx}" cy="{cy}" r="150" fill="none" stroke="{WHITE}" stroke-width="3"/><circle cx="{cx}" cy="{cy}" r="128" fill="none" stroke="{WHITE}" stroke-width="2"/>' + runes
    can = dark_canvas(art + bbox(x + 2, y + 2, w - 4, h - 4, True), x, y, w, h)
    s = screen(can + bottom_bar(TF_ROWS, active=('自由变换',), hl='旋转45°'), active='transform') + ring(*icon_pos('transform'), 18)
    bx, by, bw, bh = POS['旋转45°']
    s += badge(bx + bw / 2, by - 12, 2)
    s += label(SQ[0] + SQ[2] + 12, 88, '符文写在「圆环」的副本上', WHITE, 13)
    s += label(SQ[0] + SQ[2] + 12, 116, '　 选框中心才是圆心', WHITE, 13)
    s += label(SQ[0] + SQ[2] + 12, 152, '① 三指下拖 › 复制', YEL1, 14)
    s += label(SQ[0] + SQ[2] + 12, 184, '② 变换 › 旋转45°', YEL1, 14)
    s += label(SQ[0] + SQ[2] + 12, 216, '　 绕画布中心转一格', WHITE, 13)
    s += label(SQ[0] + SQ[2] + 12, 248, '重复 7 次，排满一圈', YEL1, 14)
    s += label(SQ[0] + SQ[2] + 12, 280, '（文字不要开对称，会被镜像）', WHITE, 13)
    s += hb_note('示意图：旋转45°绕选框中心转，所以这一层里要有那个正圆')
    save('u-rot45', svg(W, H, s, '符文：复制后用旋转45°排满一圈'))


def cast_photo(uid, fx=(), extra=''):
    return photo(CX, CY, CW, CH, bg='day', pose='cast', uid=uid, fx=fx, extra=extra)


@reg
def u_circle_distort():
    ph, g = cast_photo('cd')
    hh = g['hh']
    cx, cy, r = g['cx'], g['feet'] - hh * 0.1, hh * 2.0
    circ = fx_circle('cd', cx, cy, r, 0.32)
    pts = [(cx - r * 1.05, cy - r * 0.38), (cx + r * 1.05, cy - r * 0.38), (cx + r * 1.12, cy + r * 0.36), (cx - r * 1.12, cy + r * 0.36)]
    s = screen(ph + circ + quad(pts) + bottom_bar(TF_ROWS, active=('扭曲',), hl='扭曲'), active='transform') + ring(*icon_pos('transform'), 18)
    s += badge(pts[1][0] + 16, pts[1][1] - 8, 1)
    s += label(CX + CW + 14, CY + 40, '粘贴进照片，模式「添加」', WHITE, 13)
    s += label(CX + CW + 14, CY + 72, '① 扭曲：上边两角往里收', YEL1, 14)
    s += label(CX + CW + 14, CY + 104, '　 压扁到和地面一样扁', WHITE, 13)
    s += label(CX + CW + 14, CY + 138, '② 中心对准两脚之间', YEL1, 14)
    s += label(CX + CW + 14, CY + 172, '③ 蒙版擦掉被脚挡住的线', YEL1, 14)
    s += hb_note()
    save('u-circle-distort', svg(W, H, s, '用扭曲把魔法阵贴到地面上'))


# ---------- 火焰界面 ----------
def palm_photo(uid, fx=(), extra=''):
    return photo(CX, CY, CW, CH, bg='night', pose='palm', uid=uid, fx=fx, extra=extra)


@reg
def u_fire_brush():
    ph, g = palm_photo('fb')
    hx, hy = g['hand']
    hh = g['hh']
    strokes = ''
    for k, (dx, ht) in enumerate([(-0.3, 1.4), (0.05, 2.0), (0.35, 1.5)]):
        x0, y0 = hx + dx * hh, hy - hh * 0.1
        strokes += f'<path d="M{x0:.1f} {y0:.1f} q{-hh * 0.35:.1f} {-ht * hh * 0.4:.1f} 0 {-ht * hh * 0.6:.1f} t{hh * 0.1:.1f} {-ht * hh * 0.5:.1f}" fill="none" stroke="{FIRE}" stroke-width="{hh * 0.2:.1f}" stroke-linecap="round" opacity=".9"/>'
        strokes += arrow(x0 + hh * 0.5, y0 - hh * 0.2, x0 + hh * 0.5, y0 - ht * hh, WHITE, 1.5) if k == 2 else ''
    s = screen(ph + strokes + brush_lib(SETS, '亮度', LUM_BRUSHES, '浅色画笔', x=470, w=300), active='brush') + ring(*icon_pos('brush'), 18)
    s += label(62, 440, '亮度 › 浅色画笔，深橙色', YEL1, 14)
    s += label(62, 472, '从掌心往上画，每笔走一点 S 形，尖端收细', YEL1, 14)
    s += hb_note('示意图：组里的画笔名称和顺序以实际为准')
    save('u-fire-brush', svg(W, H, s, '火焰：浅色画笔从火源往上画'))


@reg
def u_fire_layers():
    ph, g = palm_photo('fl', fx=('fire',))
    lay = lpanel([dict(name='火 · 白芯', thumb='fire', mode='添加', sel=True), dict(name='火 · 黄', thumb='fire', mode='添加'), dict(name='火 · 橙红', thumb='fire', mode='添加'),
                  dict(name='火 · 外晕', thumb='fire', mode='添加'), dict(name='人像照片', thumb='photo', mode='N')])
    s = screen(ph + lay, active='layers') + ring(*icon_pos('layers'), 18)
    s += label(480, 398, '橙红画大轮廓，黄色画里面一圈', YEL1, 14)
    s += label(480, 430, '白芯只在最底部一小团', YEL1, 14)
    s += label(480, 462, '外晕：复制后高斯模糊 30%', WHITE, 13)
    s += label(480, 492, '涂抹工具往上拉尖端', WHITE, 13)
    s += hb_note('示意图：实际界面右边显示的是模式的缩写字母')
    save('u-fire-layers', svg(W, H, s, '火焰分层：橙红、黄、白芯、外晕'))


# ---------- 丁达尔光界面 ----------
def room_photo(uid, kind='color', x=CX, y=CY, w=CW, h=CH):
    ph, g = photo(x, y, w, h, bg='room', pose='stand', uid=uid, fcx=0.62)
    if kind == 'gray':
        ph = f'<defs><filter id="gy{uid}"><feColorMatrix type="saturate" values="0"/></filter></defs><g filter="url(#gy{uid})">{ph}</g>'
    if kind == 'curve':
        ph = (f'<defs><filter id="gy{uid}" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="0"/><feComponentTransfer>'
              f'<feFuncR type="linear" slope="5" intercept="-4"/><feFuncG type="linear" slope="5" intercept="-4"/><feFuncB type="linear" slope="5" intercept="-4"/></feComponentTransfer></filter></defs>'
              f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000"/><g filter="url(#gy{uid})">{ph}</g>')
    return ph, g


@reg
def u_tyn_hsb():
    ph, g = room_photo('th', 'gray')
    s = screen(ph + infobar('色相、饱和度、亮度', '') + tool_sliders([('色相', 0.5), ('饱和度', 0.0), ('亮度', 0.5)], hl='饱和度'), active='adjust') + ring(*icon_pos('adjust'), 18)
    s += label(CX + CW + 14, CY + 40, '先复制原图层', WHITE, 13)
    s += label(CX + CW + 14, CY + 72, '调整 › 色相、饱和度、亮度', YEL1, 14)
    s += label(CX + CW + 14, CY + 104, '饱和度拉到最左', YEL1, 14)
    s += label(CX + CW + 14, CY + 136, '　 只剩黑白', WHITE, 13)
    s += hb_note()
    save('u-tyn-hsb', svg(W, H, s, '丁达尔光第一步：复制原图，去掉饱和度'))


def curve_panel(x, y, w=230, h=200):
    s = [panel(x, y, w, h + 60)]
    gx, gy = x + 15, y + 40
    s.append(text(x + 16, y + 26, '曲线', 15, 800, UITEXT))
    s.append(f'<rect x="{gx}" y="{gy}" width="{w - 30}" height="{h - 10}" fill="#1F2329"/>')
    for k in range(1, 4):
        s.append(f'<line x1="{gx + (w - 30) * k / 4}" y1="{gy}" x2="{gx + (w - 30) * k / 4}" y2="{gy + h - 10}" stroke="#4B5563"/>')
        s.append(f'<line x1="{gx}" y1="{gy + (h - 10) * k / 4}" x2="{gx + w - 30}" y2="{gy + (h - 10) * k / 4}" stroke="#4B5563"/>')
    gw, gh = w - 30, h - 10
    p1 = (gx + gw * 0.72, gy + gh)
    s.append(f'<path d="M{gx} {gy + gh} L{p1[0]:.1f} {p1[1]:.1f} Q{gx + gw * 0.86:.1f} {gy + gh * 0.4:.1f} {gx + gw} {gy}" fill="none" stroke="{WHITE}" stroke-width="2.5"/>')
    s.append(f'<line x1="{gx}" y1="{gy + gh}" x2="{gx + gw}" y2="{gy}" stroke="#6B7280" stroke-dasharray="4 4"/>')
    s.append(f'<circle cx="{p1[0]:.1f}" cy="{p1[1] - 2:.1f}" r="7" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>')
    tabs = ['伽玛', '红色', '绿色', '蓝色']
    for i, t in enumerate(tabs):
        s.append(f'<rect x="{x + 12 + i * 52}" y="{y + h + 22}" width="48" height="26" rx="6" fill="{UIBLUE if i == 0 else UIBAR}"/>' + text(x + 36 + i * 52, y + h + 40, t, 12, 700, UITEXT, 'middle'))
    return ''.join(s), p1


@reg
def u_tyn_curve():
    ph, g = room_photo('tc', 'curve')
    cp, p1 = curve_panel(30, 120)
    s = screen(ph + cp, active='adjust') + ring(*icon_pos('adjust'), 18)
    s += ring(p1[0], p1[1] - 2, 15) + badge(p1[0] + 4, p1[1] + 26, 1)
    s += label(CX + CW + 14, CY + 40, '调整 › 曲线', YEL1, 14)
    s += label(CX + CW + 14, CY + 72, '① 左下角的点往右拖', YEL1, 14)
    s += label(CX + CW + 14, CY + 104, '　 暗部、中间调都变黑', WHITE, 13)
    s += label(CX + CW + 14, CY + 136, '　 只剩窗户还亮', WHITE, 13)
    s += label(CX + CW + 14, CY + 170, '② 白衣服之类也亮的地方', YEL1, 14)
    s += label(CX + CW + 14, CY + 200, '　 用橡皮擦掉', WHITE, 13)
    s += hb_note('示意图：点在曲线上加节点，拖动节点调整')
    save('u-tyn-curve', svg(W, H, s, '曲线把暗部压成黑色，只留最亮的光源'))


@reg
def u_tyn_blur():
    ph, g = room_photo('tb', 'color')
    x, y, w, h = CX, CY, CW, CH
    sx, sy = x + w * 0.2, y + h * 0.22
    rays = fx_rays('tb', sx, sy, [25, 35, 45, 55], w * 1.2, [w * 0.04, w * 0.07, w * 0.08, w * 0.04], GOLD, 0.5)
    disc = f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="16" fill="{INK}" opacity=".85"/><circle cx="{sx:.1f}" cy="{sy:.1f}" r="5" fill="{WHITE}"/>'
    clip = f'<defs><clipPath id="tbc"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs>'
    s = screen(ph + clip + f'<g clip-path="url(#tbc)">{rays}</g>' + disc + infobar('透视模糊', '75%') + filter_bar(buttons=['位置', '方向'], active=['位置'], hl='位置'), active='adjust') + ring(*icon_pos('adjust'), 18)
    s += badge(sx - 26, sy, 1)
    bx, by, bw, bh = POS['位置']
    s += badge(bx - 16, by + 16, 2)
    s += label(CX + CW + 14, CY + 40, '模式先改成「添加」', WHITE, 13)
    s += label(CX + CW + 14, CY + 72, '调整 › 透视模糊', YEL1, 14)
    s += label(CX + CW + 14, CY + 104, '① 圆盘拖到窗户上', YEL1, 14)
    s += label(CX + CW + 14, CY + 136, '② 选「位置」', YEL1, 14)
    s += label(CX + CW + 14, CY + 168, '　 在圆盘外右滑：60%～90%', WHITE, 13)
    s += label(CX + CW + 14, CY + 200, '光束不够长：再做一次', WHITE, 13)
    s += hb_note()
    save('u-tyn-blur', svg(W, H, s, '透视模糊：圆盘放在光源上，拉出光束'))


# ---------- 案例 ----------
def save_case(name, body, lab, after):
    save(name, svg(640, 520, body + label(606 if after else 34, 56, lab, VIO1 if after else YEL1, 16, 'end' if after else 'start'), lab))


@reg
def cases63():
    b, g = photo(20, 20, 600, 480, bg='night', pose='sword', uid='s1')
    save_case('case-63-saber-before', b, '修之前：夜景举着道具剑，剑是灰色塑料', False)
    b, g = photo(20, 20, 600, 480, bg='night', pose='sword', uid='s2', fx=('saber',))
    save_case('case-63-saber-after', b, '修之后：剑芯 + 内晕 + 外晕', True)
    b, g = photo(20, 20, 600, 480, bg='day', pose='cast', uid='m1')
    save_case('case-63-circle-before', b, '修之前：户外施法姿势', False)
    g = geo(20, 20, 600, 480)
    hx, hy = g['hand']
    hh = g['hh']
    extra = glow_dot('m2', hx, hy - hh * 0.3, hh * 0.9, '#C084FC', hh * 0.4, 0.9) + glow_dot('m2', hx, hy - hh * 0.3, hh * 0.25, WHITE, hh * 0.1)
    b, g = photo(20, 20, 600, 480, bg='day', pose='cast', uid='m2', fx=('circle',), extra=extra)
    save_case('case-63-circle-after', b, '修之后：脚下魔法阵 + 手上光点', True)
    b, g = photo(20, 20, 600, 480, bg='night', pose='palm', uid='f1')
    save_case('case-63-fire-before', b, '修之前：夜景摊开手掌', False)
    b, g = photo(20, 20, 600, 480, bg='night', pose='palm', uid='f2', fx=('fire',))
    save_case('case-63-fire-after', b, '修之后：掌心火焰', True)
    b, g = room_photo('t1', 'color', 20, 20, 600, 480)
    save_case('case-63-tyn-before', b, '修之前：窗户很亮，空气里看不到光', False)
    body, g = room_with_beam('t2', 20, 20, 600, 480, True, False)
    save_case('case-63-tyn-after', body, '修之后：从窗户提取出的光束', True)


# ================= 6.4 粒子和飘落 =================
@reg
def p_stamp():
    Wd, Hd = 760, 330
    s = []
    panels = [('间距小：印连成一条线', 0), ('间距大：一个个分开', 1), ('加横向抖动 + 散布：散开、乱转', 2)]
    for i, (t, k) in enumerate(panels):
        ox = 20 + i * 245
        s.append(f'<rect x="{ox}" y="20" width="230" height="250" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(label(ox + 10, 50, t, [YEL1, VIO1, MINT1][i], 12))
        s.append(f'<path d="M{ox + 20} 220 Q{ox + 115} 90 {ox + 210} 180" fill="none" stroke="{LINE}" stroke-width="2" stroke-dasharray="5 4"/>')
        n = 26 if k == 0 else 7
        rnd = random.Random(i)
        for j in range(n):
            t_ = j / (n - 1)
            px = (1 - t_) ** 2 * (ox + 20) + 2 * (1 - t_) * t_ * (ox + 115) + t_ ** 2 * (ox + 210)
            py = (1 - t_) ** 2 * 220 + 2 * (1 - t_) * t_ * 90 + t_ ** 2 * 180
            rot = 0
            if k == 2:
                px += rnd.uniform(-35, 35); py += rnd.uniform(-35, 35); rot = rnd.uniform(0, 360)
            s.append(petal(px, py, 11, rot, PINK, 0.9, INK))
    s.append(text(380, 300, '笔刷就是把「形状」沿着你画的路径一个个印上去。间距管印多密，抖动管偏多远，散布管转不转。', 13, 700, MUTED, 'middle'))
    save('p-stamp', svg(Wd, Hd, ''.join(s), '笔刷是形状沿路径一个个印出来的'))


@reg
def p_shape_src():
    Wd, Hd = 760, 260
    s = []
    items = [('形状来源：黑底白花', '#000', WHITE, MINT1, '白色的地方出颜色'), ('画出来：花瓣是你选的颜色', WHITE, PINK, MINT1, '黑色的地方透明'),
             ('反了：白底黑花', WHITE, '#000', RED1, '画出来是个方块，中间挖个洞')]
    for i, (t, bg, fg, f, d) in enumerate(items):
        ox = 20 + i * 245
        s.append(f'<rect x="{ox}" y="20" width="230" height="220" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(label(ox + 10, 50, t, f, 12))
        if i == 1:
            for j, (px, py, r, rot) in enumerate([(ox + 70, 110, 22, 20), (ox + 150, 140, 28, -30), (ox + 95, 175, 16, 70)]):
                s.append(petal(px, py, r, rot, PINK))
        elif i == 2:
            for j, (px, py) in enumerate([(ox + 40, 80), (ox + 110, 115)]):
                s.append(f'<rect x="{px}" y="{py}" width="80" height="80" fill="{PINK}"/>' + petal(px + 40, py + 40, 28, 0, WHITE))
        else:
            s.append(f'<rect x="{ox + 50}" y="70" width="130" height="130" fill="{bg}"/>' + petal(ox + 115, 135, 48, 0, fg))
        s.append(text(ox + 115, 228, d, 12, 700, MUTED, 'middle'))
    save('p-shape-src', svg(Wd, Hd, ''.join(s), '形状来源：白色出颜色，黑色透明'))


@reg
def p_depth():
    Wd, Hd = 760, 340
    s = [f'<rect x="20" y="20" width="420" height="300" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>', label(36, 52, '从侧面看：三层离镜头的远近', YEL1, 14)]
    s.append(f'<rect x="40" y="170" width="34" height="24" rx="4" fill="{INK}"/><circle cx="80" cy="182" r="7" fill="{VIO2}"/>')
    s.append(f'<line x1="86" y1="182" x2="420" y2="120" stroke="{LINE}" stroke-width="1.5"/><line x1="86" y1="182" x2="420" y2="250" stroke="{LINE}" stroke-width="1.5"/>')
    s.append(f'<line x1="270" y1="80" x2="270" y2="290" stroke="{MINT}" stroke-width="2" stroke-dasharray="6 4"/>' + text(270, 304, '对焦在人物这里', 12, 700, MINT7, 'middle'))
    s.append(f'<rect x="262" y="140" width="16" height="90" rx="6" fill="{VIO2}" stroke="{INK}" stroke-width="2"/><circle cx="270" cy="130" r="10" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<defs><filter id="pdb" filterUnits="userSpaceOnUse" x="0" y="0" width="800" height="400"><feGaussianBlur stdDeviation="3"/></filter></defs>')
    for (px, py, r, b) in [(140, 150, 16, 1), (150, 215, 12, 1)]:
        s.append(f'<g filter="url(#pdb)">{petal(px, py, r, 30, PINK)}</g>')
    for (px, py) in [(250, 175), (295, 200), (285, 150)]:
        s.append(petal(px, py, 7, 60, PINK))
    for (px, py) in [(380, 140), (395, 175), (370, 205), (405, 230), (385, 160)]:
        s.append(petal(px, py, 3.5, 10, '#F9A8D4'))
    for (x, t) in [(140, '近景'), (270, '中景'), (390, '远景')]:
        s.append(text(x, 76, t, 14, 800, INK, 'middle'))
    s.append(f'<rect x="460" y="20" width="280" height="300" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    rows = [('近景', '大、少、糊', '落得快，可以加动态模糊', PINK1), ('中景', '中等大小、清楚', '和人物一样锐利', VIO1), ('远景', '小、多、密', '清晰度跟背景一致，颜色淡一点', MINT1)]
    for i, (a, b, c, f) in enumerate(rows):
        yy = 50 + i * 88
        s.append(label(476, yy + 6, a, f, 15))
        s.append(text(476, yy + 38, b, 14, 800) + text(476, yy + 60, c, 13, 600, MUTED))
    save('p-depth', svg(Wd, Hd, ''.join(s), '按景深分三层：近景大而虚，中景清楚，远景小而密'))


@reg
def u_shape_draw():
    x, y, w, h = SQ
    cx, cy = x + w / 2, y + h / 2
    flower = ''.join(petal(cx + math.cos(math.radians(k * 72 - 90)) * 58, cy + math.sin(math.radians(k * 72 - 90)) * 58, 62, k * 72 + 180, WHITE) for k in range(5))
    can = dark_canvas(flower + f'<circle cx="{cx}" cy="{cy}" r="16" fill="#000"/><circle cx="{cx}" cy="{cy}" r="16" fill="none" stroke="{WHITE}" stroke-width="2"/>', x, y, w, h)
    s = screen(can + copy_bar('全部拷贝', y=470, x=170), active='brush') + ring(*icon_pos('brush'), 18)
    s += label(SQ[0] + SQ[2] + 12, 100, '新建正方形画布', YEL1, 14)
    s += label(SQ[0] + SQ[2] + 12, 130, '　 例如 1000 × 1000 像素', WHITE, 13)
    s += label(SQ[0] + SQ[2] + 12, 164, '背景颜色设成纯黑', YEL1, 14)
    s += label(SQ[0] + SQ[2] + 12, 198, '用纯白画一朵花或一片雪', YEL1, 14)
    s += label(SQ[0] + SQ[2] + 12, 228, '　 画在正中，四周留空', WHITE, 13)
    s += label(SQ[0] + SQ[2] + 12, 262, '画完：三指下拖 › 全部拷贝', YEL1, 14)
    s += label(SQ[0] + SQ[2] + 12, 296, '雪花：开径向对称来画', WHITE, 13)
    s += hb_note()
    save('u-shape-draw', svg(W, H, s, '在黑色正方形画布上用白色画形状'))


@reg
def u_new_brush():
    ph, g = photo(CX, CY, CW, CH, bg='sakura', uid='nb')
    lib = brush_lib(SETS, '亮度', LUM_BRUSHES, None, plus=True)
    mx, my = 560, 100
    menu = panel(mx, my, 200, 120) + menu_rows(mx, my + 6, 200, ['创建新笔刷', '创建新组合', '从「文件」导入'], hl='创建新笔刷')
    s = screen(ph + lib + menu, active='brush') + ring(*icon_pos('brush'), 18)
    s += badge(360 + 410 - 50, 58 + 22, 1) + badge(mx - 14, my + 6 + 17, 2)
    s += label(62, 440, '① 画笔库右上角「+」', YEL1, 14)
    s += label(62, 472, '② 「创建新笔刷」，会打开画笔工作室', YEL1, 14)
    s += label(62, 504, '　 建议先点一个自己建的组，新笔刷放进去', WHITE, 13)
    s += hb_note()
    save('u-new-brush', svg(W, H, s, '画笔库加号：创建新笔刷'))


def petals_pad(px, py, pw, ph, mode):
    s = []
    if mode == 'shape':
        s.append(f'<rect x="{px + 30}" y="{py + 60}" width="140" height="140" fill="#000"/>' + petal(px + 100, py + 130, 50, 0, WHITE))
    else:
        rnd = random.Random({'path': 1, 'shape2': 2, 'dyn': 3}[mode])
        for j in range(14):
            t = j / 13
            x = px + 20 + t * (pw - 40)
            y = py + ph * 0.55 - math.sin(t * 3.1) * 90
            r = 9
            rot = 0
            if mode in ('shape2', 'dyn'):
                rot = rnd.uniform(0, 360)
            if mode != 'path' or True:
                x += rnd.uniform(-25, 25); y += rnd.uniform(-35, 35)
            if mode == 'dyn':
                r = rnd.uniform(5, 14)
            s.append(petal(x, y, r, rot, PINK, rnd.uniform(0.6, 1.0) if mode == 'dyn' else 1))
    return ''.join(s)


@reg
def u_shape_src():
    rows = [('形状来源', 'btn', True), ('散布', 0.0, False), ('旋转', 0.5, False), ('个数', 0.06, False)]
    st, pad = studio(STUDIO_PROPS, '形状', rows)
    s = screen('', None, side=False) + st + petals_pad(*pad, 'shape')
    s += badge(30 + 150 + 22 + 300 - 35, 40 + 54 - 16, 2) + badge(30 + 150 + 12, 40 + 44 + 3 * 30 + 13, 1)
    s += label(560, 470, '① 左边点「形状」', YEL1, 14) + label(560, 502, '② 形状来源右边「编辑」', YEL1, 14)
    s += hb_note('示意图：画笔工作室的布局以实际为准')
    save('u-shape-src', svg(W, H, s, '画笔工作室：形状，编辑形状来源'))


@reg
def u_shape_import():
    x, y, w, h = 100, 50, 600, 460
    s = screen('', None, side=False) + f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#000" opacity=".35"/>' + panel(x, y, w, h)
    s += text(x + w / 2, y + 30, '形状编辑器', 16, 800, UITEXT, 'middle') + text(x + 18, y + 30, '导入', 15, 800, UIBLUE) + text(x + w - 18, y + 30, '完成', 15, 800, UIBLUE, 'end')
    s += ring(x + 33, y + 24, 22)
    s += f'<rect x="{x + 200}" y="{y + 90}" width="320" height="320" fill="#000"/>' + petal(x + 360, y + 250, 110, 0, WHITE)
    mx, my = x + 14, y + 52
    s += panel(mx, my, 160, 150) + menu_rows(mx, my + 6, 160, ['导入照片', '导入文件', '源库', '粘贴'], hl='粘贴')
    s += badge(x + 33, y + 58, 1) if False else ''
    s += badge(x + 60, y + 24, 1) + badge(mx + 174, my + 6 + 3 * 34 + 17, 2) + badge(x + w - 60, y + 24, 3)
    s += label(x + 200, y + 440, '① 导入 › ② 粘贴刚才拷贝的图   ③ 完成', YEL1, 14)
    s += label(mx, my + 190, '看到方块里挖了个洞：', RED1, 13) + label(mx, my + 220, '两指轻点预览图反转', WHITE, 13)
    s += hb_note()
    save('u-shape-import', svg(W, H, s, '形状编辑器：导入，粘贴'))


@reg
def u_studio_path():
    rows = [('间距', 0.7, True), ('间距抖动', 0.4, False), ('横向抖动', 0.8, True), ('线性抖动', 0.3, False), ('掉落', 0.0, False)]
    st, pad = studio(STUDIO_PROPS, '描边路径', rows)
    s = screen('', None, side=False) + st + petals_pad(*pad, 'path')
    s += label(206, 340, '间距 60%～80%：一片片分开', YEL1, 14)
    s += label(206, 372, '横向抖动 60%～100%：散开', YEL1, 14)
    s += label(206, 404, '两种抖动 30%～50%', WHITE, 13)
    s += label(206, 434, '掉落 0：不会越画越淡', WHITE, 13)
    s += hb_note('示意图：数值是参考，边调边在右边绘图板上试')
    save('u-studio-path', svg(W, H, s, '描边路径：间距和抖动'))


@reg
def u_studio_shape():
    rows = [('散布', 1.0, True), ('个数', 0.06, False), ('个数抖动', 0.0, False), ('随机化', 'on', True), ('水平翻转', 'on', False), ('垂直翻转', 'on', False)]
    st, pad = studio(STUDIO_PROPS, '形状', rows)
    s = screen('', None, side=False) + st + petals_pad(*pad, 'shape2')
    s += label(206, 384, '散布拉满：每片随机转', YEL1, 14)
    s += label(206, 416, '随机化、翻转：不重样', YEL1, 14)
    s += label(206, 448, '个数 1～2：一处一两片', WHITE, 13)
    s += hb_note('示意图：数值是参考，边调边在右边绘图板上试')
    save('u-studio-shape', svg(W, H, s, '形状：散布、随机化、翻转'))


@reg
def u_studio_dyn():
    rows = [('速度 · 尺寸', '0%', False), ('速度 · 不透明度', '0%', False), ('抖动 · 尺寸', 0.5, True), ('抖动 · 不透明度', 0.3, True)]
    st, pad = studio(STUDIO_PROPS, '动态', rows)
    s = screen('', None, side=False) + st + petals_pad(*pad, 'dyn')
    s += label(206, 340, '抖动 · 尺寸 40%～60%', YEL1, 14)
    s += label(206, 372, '抖动 · 不透明度 20%～40%', YEL1, 14)
    s += label(206, 404, '速度两项保持 0', WHITE, 13)
    s += label(206, 434, '颜色动态里亮度抖动 10%', WHITE, 13)
    s += hb_note('示意图：数值是参考，边调边在右边绘图板上试')
    save('u-studio-dyn', svg(W, H, s, '动态：尺寸和不透明度抖动'))


def sakura_photo(uid, x=CX, y=CY, w=CW, h=CH, layers=(1, 1, 1), sc=None):
    ph, g = photo(x, y, w, h, bg='sakura', pose='stand', uid=uid, fcx=0.45)
    sc = sc or w / 600
    far = fx_petals(uid, x, y, w, h, sc, (1, 0, 0)) if layers[0] else ''
    # 远景花瓣在人物后面：先画远景再盖一遍人物
    g2 = g
    person_again = person(g2, 'stand') if layers[0] else ''
    mid = fx_petals(uid, x, y, w, h, sc, (0, 1, 0)) if layers[1] else ''
    near = fx_petals(uid, x, y, w, h, sc, (0, 0, 1)) if layers[2] else ''
    body = ph + f'<defs><clipPath id="sk{uid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#sk{uid})">{far}{person_again}{mid}{near}</g>'
    return body, g


@reg
def u_depth_layers():
    ph, g = sakura_photo('dl')
    lay = lpanel([dict(name='飘落', group=True), dict(name='近景（大、糊）', thumb='petal', mode='N', child=True, sel=True), dict(name='中景', thumb='petal', mode='N', child=True),
                  dict(name='人物（抠图）', thumb='figure', mode='N'), dict(name='远景（小、密）', thumb='petal', mode='N'), dict(name='原图', thumb='day', mode='N')])
    s = screen(ph + lay, active='layers') + ring(*icon_pos('layers'), 18)
    s += label(480, 434, '远景放在抠出来的人物下面', YEL1, 14)
    s += label(480, 466, '　 花瓣就在人身后', WHITE, 13)
    s += label(480, 496, '每层先画再调大小和模糊', WHITE, 13)
    s += hb_note()
    save('u-depth-layers', svg(W, H, s, '三层飘落的图层顺序'))


@reg
def u_near_blur():
    ph, g = sakura_photo('nbl')
    s = screen(ph + infobar('高斯模糊', '20%') + lpanel([dict(name='近景', thumb='petal', mode='N', sel=True), dict(name='中景', thumb='petal', mode='N')]), active='adjust') + ring(*icon_pos('adjust'), 18)
    s += label(480, 230, '近景层：笔刷尺寸开大', YEL1, 14)
    s += label(480, 262, '　 只画 3～6 片，放在边角', WHITE, 13)
    s += label(480, 294, '高斯模糊 15%～30%', YEL1, 14)
    s += label(480, 326, '想要风感：再加动态模糊', WHITE, 13)
    s += label(480, 356, '　 方向和飘落方向一致', WHITE, 13)
    s += hb_note()
    save('u-near-blur', svg(W, H, s, '近景层加高斯模糊'))


@reg
def u_sparkle():
    ph, g = photo(CX, CY, CW, CH, bg='night', pose='cast', uid='sp')
    hx, hy = g['hand']
    pts = [(hx + 20, hy - 30, 12), (hx - 30, hy - 10, 7), (hx + 5, hy - 60, 9), (hx - 50, hy - 50, 5), (hx + 40, hy + 5, 6)]
    s = screen(ph + fx_sparkles('sp', pts) + brush_lib(SETS, '亮度', LUM_BRUSHES, '闪光', x=470, w=300), active='brush') + ring(*icon_pos('brush'), 18)
    s += label(62, 440, '亮度 › 闪光，新图层「添加」', YEL1, 14)
    s += label(62, 472, '一个一个轻点，大的少、小的多，靠近光源密，远了稀', YEL1, 14)
    s += hb_note('示意图：组里的画笔名称和顺序以实际为准')
    save('u-sparkle', svg(W, H, s, '闪光笔刷：轻点出光粒子'))


@reg
def cases64():
    b, g = photo(20, 20, 600, 480, bg='sakura', uid='k1', fcx=0.45)
    save_case('case-64-sakura-before', b, '修之前：樱花树下，没有飘落的花瓣', False)
    b, g = sakura_photo('k2', 20, 20, 600, 480)
    save_case('case-64-sakura-after', b, '修之后：远、中、近三层花瓣', True)
    b, g = sakura_photo('k3', 20, 20, 600, 480, layers=(0, 1, 0))
    save_case('case-64-sakura-flat', b, '只画了一层：大小一样、都很清楚，像贴纸', False)
    b, g = photo(20, 20, 600, 480, bg='snow', uid='w1')
    save_case('case-64-snow-before', b, '修之前：雪景，但雪没拍出来', False)
    ph, g = photo(20, 20, 600, 480, bg='snow', uid='w2')
    far = fx_snow('w2', 20, 20, 600, 480, 1.0, (1, 0, 0))
    rest = fx_snow('w2', 20, 20, 600, 480, 1.0, (0, 1, 1))
    b = ph + f'<defs><clipPath id="sw2"><rect x="20" y="20" width="600" height="480"/></clipPath></defs><g clip-path="url(#sw2)">{far}{person(g)}{rest}</g>'
    save_case('case-64-snow-after', b, '修之后：远处细雪 + 中景雪花 + 近处糊雪团', True)


# ================= 6.5 环境光反射 =================
@reg
def p_falloff():
    Wd, Hd = 760, 300
    s = [f'<rect x="20" y="20" width="720" height="260" rx="16" fill="{NIGHT}" stroke="{INK}" stroke-width="2.5"/>',
         f'<defs><radialGradient id="fo" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(110 150) scale(560)">'
         + ''.join(f'<stop offset="{d / 5:.2f}" stop-color="{GLOWB2}" stop-opacity="{min(1, 0.06 / max(d / 5, 0.06) ** 2) * 0.9:.3f}"/>' for d in range(0, 6)) + '</radialGradient></defs>',
         f'<rect x="20" y="20" width="720" height="260" rx="16" fill="url(#fo)"/>']
    s.append(f'<circle cx="110" cy="150" r="16" fill="{WHITE}"/>' + text(110, 196, '光源', 13, 800, WHITE, 'middle'))
    for k, (d, v) in enumerate([(1, '1'), (2, '1/4'), (3, '1/9'), (4, '1/16')]):
        x = 110 + d * 140
        s.append(f'<line x1="{x}" y1="60" x2="{x}" y2="240" stroke="{WHITE}" stroke-width="1.5" stroke-dasharray="5 4" opacity=".7"/>')
        s.append(text(x, 56, f'{d} 倍距离', 13, 800, WHITE, 'middle') + label(x - 26, 264, f'亮度 {v}', YEL1, 12))
        s.append(f'<rect x="{x - 10}" y="130" width="20" height="40" rx="6" fill="{VIO2}" opacity="{max(0.25, 1 / d ** 2):.2f}" stroke="{WHITE}" stroke-width="1.5"/>')
    s.append(text(380, 110, '离光源远一倍，被照到的亮度只剩四分之一', 14, 800, WHITE, 'middle'))
    save('p-falloff', svg(Wd, Hd, ''.join(s), '光的衰减：距离翻倍，亮度剩四分之一'))


@reg
def p_facing():
    Wd, Hd = 760, 300
    s = [f'<defs><linearGradient id="cyl" x1="0" x2="1"><stop offset="0" stop-color="#3A3F58"/><stop offset=".55" stop-color="#4A5070"/><stop offset=".8" stop-color="{GLOWB}"/><stop offset=".93" stop-color="{WHITE}"/><stop offset="1" stop-color="{GLOWB2}"/></linearGradient></defs>']
    s.append(f'<rect x="20" y="20" width="360" height="260" rx="16" fill="{NIGHT}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(label(36, 52, '朝向光的面亮，背对的面暗', WHITE, 14))
    s.append(f'<rect x="120" y="80" width="90" height="170" rx="40" fill="url(#cyl)" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<line x1="330" y1="70" x2="330" y2="260" stroke="{WHITE}" stroke-width="7" stroke-linecap="round"/><line x1="330" y1="70" x2="330" y2="260" stroke="{GLOWB}" stroke-width="20" opacity=".35" stroke-linecap="round"/>')
    for yy in (110, 165, 220):
        s.append(arrow(318, yy, 222, yy, GLOWB2, 2.5))
    s.append(text(165, 272, '亮的是窄窄一条边：边缘光', 12, 700, UITEXT, 'middle'))
    s.append(f'<rect x="400" y="20" width="340" height="260" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(label(416, 52, '光的颜色 × 表面的颜色', YEL1, 14))
    rows = [('白衣服', '#F8FAFC', '#BAE6FD', '很明显地变蓝'), ('皮肤', SKIN, '#D9E8F0', '偏青、变冷'), ('红衣服', '#DC2626', '#7C3A6E', '几乎不变亮，发紫'), ('黑衣服', '#111827', '#1E2A3A', '只有亮边')]
    for i, (a, c1, c2, d) in enumerate(rows):
        yy = 76 + i * 50
        s.append(text(416, yy + 24, a, 13, 800) + f'<rect x="480" y="{yy + 4}" width="40" height="30" rx="5" fill="{c1}" stroke="{INK}"/>' + text(530, yy + 25, '+ 蓝光 →', 12, 700, MUTED)
                 + f'<rect x="590" y="{yy + 4}" width="40" height="30" rx="5" fill="{c2}" stroke="{INK}"/>' + text(638, yy + 25, d, 12, 700))
    save('p-facing', svg(Wd, Hd, ''.join(s), '哪里亮、亮成什么颜色'))


@reg
def p_three():
    Wd, Hd = 760, 380
    body, g = photo(20, 20, 470, 340, bg='night', pose='sword', uid='p3', fx=('saber', 'rim', 'shadow', 'contact'))
    s = [body]
    hh = g['hh']
    s.append(label(510, 70, '① 边缘光', VIO1, 15) + text(510, 98, '朝向光剑的那一侧：头发、脸、', 13, 600) + text(510, 118, '肩、手臂、腿的边缘', 13, 600))
    s.append(label(510, 170, '② 投影', VIO1, 15) + text(510, 198, '光在右上，影子落在左边地上', 13, 600) + text(510, 218, '离脚越远越淡、越糊', 13, 600))
    s.append(label(510, 270, '③ 接触光', VIO1, 15) + text(510, 298, '握剑的手、光下面的地面', 13, 600) + text(510, 318, '离光最近，最亮', 13, 600))
    s.append(badge(g['cx'] + hh * 0.9, g['top'] + hh * 2.2, 1) + badge(g['cx'] - hh * 2.2, g['feet'], 2) + badge(g['hand'][0] + hh * 1.5, g['feet'] - hh * 0.3, 3))
    save('p-three', svg(Wd, Hd, ''.join(s), '环境光的三件事：边缘光、投影、接触光'))


@reg
def p_shadow_dir():
    Wd, Hd = 760, 260
    s = []
    for i, (title, lx, ly, f) in enumerate([('光在右上：影子往左下拉长', 330, 50, YEL1), ('光在脚边（地上的魔法阵）：影子短，四周都有', 180, 205, VIO1)]):
        ox = 20 + i * 370
        s.append(f'<rect x="{ox}" y="20" width="350" height="220" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(label(ox + 12, 50, title, f, 12))
        s.append(f'<rect x="{ox + 20}" y="190" width="310" height="40" fill="{FLOOR}"/>')
        px, py = ox + 175, 190
        if i == 0:
            s.append(f'<path d="M{px - 8} {py} L{px - 150} {py + 26} L{px - 140} {py + 34} L{px + 8} {py + 4} Z" fill="#334155" opacity=".55"/>')
            s.append(f'<circle cx="{ox + lx - 20}" cy="{ly + 30}" r="14" fill="{GLOWB}"/>')
            s.append(f'<line x1="{ox + lx - 20}" y1="{ly + 30}" x2="{px - 150}" y2="{py + 30}" stroke="{GLOWB}" stroke-width="1.5" stroke-dasharray="5 4"/>')
        else:
            s.append(f'<ellipse cx="{px}" cy="{py + 14}" rx="70" ry="12" fill="#C084FC" opacity=".5"/>')
            s.append(f'<ellipse cx="{px}" cy="{py + 3}" rx="22" ry="5" fill="#334155" opacity=".6"/>')
        s.append(f'<rect x="{px - 10}" y="{py - 90}" width="20" height="90" rx="8" fill="{VIO2}" stroke="{INK}" stroke-width="2"/><circle cx="{px}" cy="{py - 100}" r="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
    save('p-shadow-dir', svg(Wd, Hd, ''.join(s), '投影的方向：从光源穿过人物往外'))


# ---------- 界面 ----------
def env_photo(uid, fx=('saber',)):
    return photo(CX, CY, CW, CH, bg='night', pose='sword', uid=uid, fx=fx)


@reg
def u_clip():
    ph, g = env_photo('cl')
    lay = lpanel([dict(name='边缘光', thumb='', mode='N', sel=True), dict(name='人物（抠图）', thumb='figure', mode='N'), dict(name='光剑（组）', thumb='blueline', mode='N'), dict(name='背景', thumb='photo', mode='N')])
    opts = layer_opts('剪辑蒙版', x=292, y=70)
    s = screen(ph + opts + lay, active='layers') + ring(*icon_pos('layers'), 18)
    s += badge(292 + 170 + 12, 70 + 7 + 7 * 29 + 14, 1)
    s += label(480, 330, '在「人物」上面新建一层', WHITE, 13)
    s += label(480, 360, '轻点两次 ›「剪辑蒙版」', YEL1, 14)
    s += label(480, 392, '再把这层模式改成「添加」', YEL1, 14)
    s += label(480, 424, '画到人物外面也不会显示', WHITE, 13)
    s += hb_note()
    save('u-clip', svg(W, H, s, '新建图层，设成剪辑蒙版'))


@reg
def u_clip_layers():
    ph, g = env_photo('cll', fx=('saber', 'rim'))
    lay = lpanel([dict(name='边缘光', thumb='stroke', mode='添加', sel=True, clip=True), dict(name='环境色', thumb='stroke', mode='覆盖', clip=True), dict(name='暗面', thumb='shadow', mode='正片叠底', clip=True),
                  dict(name='人物（抠图）', thumb='figure', mode='N'), dict(name='投影 · 接触光', thumb='shadow', mode='N'), dict(name='背景', thumb='photo', mode='N')])
    s = screen(ph + lay, active='layers') + ring(*icon_pos('layers'), 18)
    s += label(480, 420, '带箭头的三层剪辑在人物上', YEL1, 14)
    s += label(480, 452, '投影和地面的光在人物下面', YEL1, 14)
    s += label(480, 484, '　 画在背景上', WHITE, 13)
    s += hb_note('示意图：实际界面右边显示的是模式的缩写字母')
    save('u-clip-layers', svg(W, H, s, '环境光的图层结构'))


@reg
def u_pick():
    ph, g = env_photo('pk')
    (x1, y1), (x2, y2) = g['base'], g['tip']
    mx, my = (x1 + x2) / 2 + g['hh'] * 0.32, (y1 + y2) / 2
    s = screen(ph + eyedrop(mx, my, GLOWB, PINK), active='brush')
    s += label(CX + CW + 14, CY + 40, '手指在画布上长按', YEL1, 14)
    s += label(CX + CW + 14, CY + 72, '出现取色圈，拖到外晕上', YEL1, 14)
    s += label(CX + CW + 14, CY + 104, '上半圈：要取的新颜色', WHITE, 13)
    s += label(CX + CW + 14, CY + 134, '不要取白色剑芯', RED1, 14)
    s += label(CX + CW + 14, CY + 166, '　 白色没有颜色信息', WHITE, 13)
    s += hb_note()
    save('u-pick', svg(W, H, s, '长按取色：取外晕的颜色，不取白色核心'))


@reg
def u_rim():
    ph, g = env_photo('rm', fx=('saber', 'rim'))
    hh = g['hh']
    brush = f'<circle cx="{g["cx"] + hh * 0.6:.1f}" cy="{g["sh_y"] + hh * 0.6:.1f}" r="{hh * 0.45:.1f}" fill="none" stroke="{WHITE}" stroke-width="2" stroke-dasharray="4 3"/>'
    s = screen(ph + brush + tool_sliders([('尺寸', 0.12), ('不透明度', 0.45)]), active='brush') + ring(*icon_pos('brush'), 18)
    s += badge(g['cx'] + hh * 1.2, g['sh_y'] + hh * 0.3, 1)
    s += label(CX + CW + 14, CY + 30, '在「边缘光」层（添加）：', WHITE, 13)
    s += label(CX + CW + 14, CY + 60, '① 气笔修饰 › 软画笔', YEL1, 14)
    s += label(CX + CW + 14, CY + 90, '　 尺寸 5%～15%', WHITE, 13)
    s += label(CX + CW + 14, CY + 112, '　 不透明度 30%～60%', WHITE, 13)
    s += label(CX + CW + 14, CY + 142, '② 沿朝向光剑的边缘画', YEL1, 14)
    s += label(CX + CW + 14, CY + 172, '　 离剑近重画，远了轻扫', WHITE, 13)
    s += label(CX + CW + 14, CY + 206, '③ 换小一号的硬笔', YEL1, 14)
    s += label(CX + CW + 14, CY + 236, '　 在最外沿描一条细亮线', WHITE, 13)
    s += hb_note()
    save('u-rim', svg(W, H, s, '在剪辑层上沿着朝光的边缘画边缘光'))


@reg
def u_shadow():
    ph, g = env_photo('sh', fx=('saber', 'rim', 'shadow'))
    hh = g['hh']
    lx, ly = g['hand'][0] + hh * 0.3, g['hand'][1] - hh * 1.2
    sx, sy = g['cx'] - hh * 3.0, g['feet'] + hh * 0.1
    lines = f'<line x1="{lx:.1f}" y1="{ly:.1f}" x2="{sx:.1f}" y2="{sy:.1f}" stroke="{YEL}" stroke-width="2" stroke-dasharray="6 4"/>'
    s = screen(ph + lines + lpanel([dict(name='人物（抠图）', thumb='figure', mode='N'), dict(name='投影', thumb='shadow', mode='正片叠底', sel=True, hl=True), dict(name='背景', thumb='photo', mode='N')]), active='layers') + ring(*icon_pos('layers'), 18)
    s += badge(sx + 10, sy - 18, 1)
    s += label(480, 276, '人物下面新建「投影」层', WHITE, 13)
    s += label(480, 306, '模式「正片叠底」', YEL1, 14)
    s += label(480, 338, '从光源穿过脚画一条线', YEL1, 14)
    s += label(480, 370, '影子就落在这条线的方向上', WHITE, 13)
    s += label(480, 402, '深蓝灰色软画笔，靠脚处深', YEL1, 14)
    s += label(480, 434, '高斯模糊 3%～8%', WHITE, 13)
    s += label(480, 462, '不透明度 40%～60%', WHITE, 13)
    s += hb_note()
    save('u-shadow', svg(W, H, s, '画投影：方向从光源穿过人物往外'))


@reg
def u_contact():
    ph, g = env_photo('ct', fx=('saber', 'rim', 'shadow', 'contact'))
    hh = g['hh']
    s = screen(ph + lpanel([dict(name='人物（抠图）', thumb='figure', mode='N'), dict(name='地面光', thumb='glow', mode='添加', sel=True, hl=True), dict(name='投影', thumb='shadow', mode='正片叠底'), dict(name='背景', thumb='photo', mode='N')]), active='layers') + ring(*icon_pos('layers'), 18)
    s += badge(g['hand'][0] + hh * 2.4, g['feet'], 1) + badge(g['hand'][0] + 18, g['hand'][1] + 10, 2)
    s += label(480, 326, '① 地面光：「添加」，软画笔', YEL1, 14)
    s += label(480, 358, '　 画扁椭圆，扁度跟地面透视', WHITE, 13)
    s += label(480, 390, '② 握剑的手：剪辑层上', YEL1, 14)
    s += label(480, 422, '　 手指、虎口点最亮的一小块', WHITE, 13)
    s += hb_note()
    save('u-contact', svg(W, H, s, '接触光：地面和握剑的手'))


@reg
def cases65():
    b, g = photo(20, 20, 600, 480, bg='night', pose='sword', uid='e1', fx=('saber',))
    save_case('case-65-saber-before', b, '加环境光之前：剑很亮，人是暗的', False)
    b, g = photo(20, 20, 600, 480, bg='night', pose='sword', uid='e2', fx=('saber', 'rim', 'shadow', 'contact'))
    save_case('case-65-saber-after', b, '加之后：边缘光 + 投影 + 地面的光', True)
    g = geo(20, 20, 600, 480)
    hx, hy = g['hand']
    hh = g['hh']
    extra = glow_dot('e3', hx, hy - hh * 0.3, hh * 0.9, '#C084FC', hh * 0.4, 0.9) + glow_dot('e3', hx, hy - hh * 0.3, hh * 0.25, WHITE, hh * 0.1)
    b, g = photo(20, 20, 600, 480, bg='day', pose='cast', uid='e3', fx=('circle',), extra=extra)
    save_case('case-65-circle-before', b, '加环境光之前：魔法阵和人没关系', False)
    leg = (f'<g mask="url(#fme4)"><ellipse cx="{g["cx"]:.1f}" cy="{g["feet"]:.1f}" rx="{hh * 1.4:.1f}" ry="{hh * 1.8:.1f}" fill="#A855F7" opacity=".45" filter="{blur("e4", hh * 0.4)}"/></g>')
    extra4 = extra.replace('e3', 'e4') + leg
    b, g = photo(20, 20, 600, 480, bg='day', pose='cast', uid='e4', fx=('circle', 'contact', 'rimp'), extra=extra4)
    save_case('case-65-circle-after', b, '加之后：小腿、鞋被紫光染色，地面有光', True)
    b, g = photo(20, 20, 600, 480, bg='night', pose='palm', uid='e5', fx=('fire',))
    save_case('case-65-fire-before', b, '加环境光之前：火在手上，脸是暗的', False)
    face = (f'<g mask="url(#fme6)" style="mix-blend-mode:plus-lighter"><ellipse cx="{g["cx"] + hh * 0.3:.1f}" cy="{g["top"] + hh * 0.9:.1f}" rx="{hh * 0.5:.1f}" ry="{hh * 0.35:.1f}" fill="{FIRE}" opacity=".7" filter="{blur("e6", hh * 0.2)}"/></g>')
    b, g = photo(20, 20, 600, 480, bg='night', pose='palm', uid='e6', fx=('fire', 'rimf', 'contact'), extra=face)
    save_case('case-65-fire-after', b, '加之后：脸的下半边和手臂被火光照暖', True)


if __name__ == '__main__':
    for f in ALL:
        f()
    print('done', len(os.listdir(OUT)))
