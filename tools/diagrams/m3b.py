"""M3 视觉基础理论 3.5～3.7（骨点、透视、构图）的示意图。运行：python tools/diagrams/m3b.py"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'diagrams', 'm3b')
os.makedirs(OUT, exist_ok=True)
BG = '#FFF7E6'


def save(name, s):
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)


# ---------------- 通用小工具 ----------------
def catmull(pts):
    """经过各点的平滑曲线（Catmull-Rom 转三次贝塞尔），返回从 pts[0] 之后的 C 段"""
    s = ''
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[max(i - 1, 0)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += f' C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}'
    return s


def closed_smooth(pts):
    """闭合平滑曲线"""
    n = len(pts)
    ext = [pts[-1]] + pts + [pts[0], pts[1]]
    s = f'M{pts[0][0]:.1f} {pts[0][1]:.1f}'
    for i in range(1, n + 1):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        s += f' C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}'
    return s + ' Z'


def limb_path(nodes):
    """nodes: [(x, y, 半宽, 凸起)]；凸起 = (方向, 大小)，方向 +1 往 x 正方向一侧凸、-1 往 x 负方向、0 两侧都凸"""
    L, R = [], []
    n = len(nodes)
    for i, nd in enumerate(nodes):
        x, y, w = nd[:3]
        bump = nd[3] if len(nd) > 3 else None
        x0, y0 = nodes[max(i - 1, 0)][:2]; x1, y1 = nodes[min(i + 1, n - 1)][:2]
        tx, ty = x1 - x0, y1 - y0
        ln = math.hypot(tx, ty) or 1
        nx, ny = -ty / ln, tx / ln
        wa = wb = w
        if bump:
            d, b = bump
            if d == 0:
                wa += b; wb += b
            elif (nx > 0) == (d > 0):
                wa += b
            else:
                wb += b
        L.append((x + nx * wa, y + ny * wa)); R.append((x - nx * wb, y - ny * wb))
    R = R[::-1]
    return f'M{L[0][0]:.1f} {L[0][1]:.1f}' + catmull(L) + f' L{R[0][0]:.1f} {R[0][1]:.1f}' + catmull(R) + ' Z'


def union(shapes, sw):
    """shapes: [(d, fill)]，先画全部描边再画全部填色，得到一个外轮廓干净的整体"""
    a = ''.join(f'<path d="{d}" fill="{INK}" stroke="{INK}" stroke-width="{sw * 2:.1f}" stroke-linejoin="round"/>' for d, f in shapes)
    b = ''.join(f'<path d="{d}" fill="{f}"/>' for d, f in shapes)
    return a + b


def dot(x, y, r=6, fill=RED, stroke=WHITE):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'


def xmark(x, y, r=8, color=RED, w=3.5):
    return (f'<line x1="{x - r:.1f}" y1="{y - r:.1f}" x2="{x + r:.1f}" y2="{y + r:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<line x1="{x - r:.1f}" y1="{y + r:.1f}" x2="{x + r:.1f}" y2="{y - r:.1f}" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')


def check(x, y, r=8, color=MINT7, w=3.5):
    return f'<path d="M{x - r:.1f} {y:.1f} l{r * 0.7:.1f} {r * 0.7:.1f} l{r * 1.3:.1f} {-r * 1.4:.1f}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>'


def card(x, y, w, h, title=None, fill=YEL1, size=15):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>'
    if title:
        s += label(x + 16, y + 34, title, fill, size)
    return s


def line(x1, y1, x2, y2, color=INK, w=2.5, dash=None, op=None, cap='round'):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    o = f' stroke-opacity="{op}"' if op else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}"{d}{o} stroke-linecap="{cap}"/>'


def leader(x1, y1, x2, y2):
    """标签到骨点的细引线"""
    return line(x1, y1, x2, y2, INK, 1.5)


# ---------------- 正面人物（带骨点） ----------------
BONE9 = ['颧骨', '下颌角', '锁骨', '肩峰', '手肘', '手腕', '髋骨', '膝盖', '脚踝']


def mannequin(cx, top, hh, flat=(), pose='hang', waist=1.0, uid='m', sw=2.5, tilt=0.0, outfit=VIO2, hair=PINK, show_clav=True, uarm=1.0, look=0.0):
    """正面人物。flat：被液化推平的骨点名；pose：hang（手垂下）/ akimbo（双手叉腰）。
    返回 (svg, 骨点坐标 dict，左右各一个，键如 '膝盖L')"""
    f = set(flat)

    def P(x, y):
        # 肩线、胯线反向倾斜（对立式站姿）
        if 1.2 < y < 2.0:
            y += x * tilt
        elif 3.0 < y < 4.0:
            y -= x * tilt
        return (cx + x * hh, top + y * hh)

    bones = {}
    shapes = []
    # 后发
    hp = [P(-0.46, 0.35), P(-0.54, 0.9), P(-0.42, 1.2), P(0.42, 1.2), P(0.54, 0.9), P(0.46, 0.35), P(0, -0.04)]
    back_hair = f'<path d="{closed_smooth(hp)}" fill="{hair}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>'
    # 腿
    for s_ in (-1, 1):
        kb = None if '膝盖' in f else (0, 0.035 * hh)
        ab = None if '脚踝' in f else (s_, 0.035 * hh)
        kw = 0.255 if '膝盖' in f else 0.27
        aw = 0.135 if '脚踝' in f else 0.145
        legs = [(0.42, 3.5, 0.40), (0.41, 4.2, 0.35), (0.36, 4.9, 0.27), (0.33, 5.25, kw, kb), (0.32, 5.5, 0.245),
                (0.31, 5.85, 0.27), (0.30, 6.5, 0.16), (0.29, 6.85, aw, ab), (0.29, 7.0, 0.15)]
        nd = []
        for (x, y, w, *b) in legs:
            px, py = P(s_ * x, y)
            nd.append((px, py, w * hh, b[0] if b else None))
        shapes.append((limb_path(nd), SKIN))
        bones['膝盖' + ('L' if s_ < 0 else 'R')] = P(s_ * 0.33, 5.25)
        bones['脚踝' + ('L' if s_ < 0 else 'R')] = P(s_ * 0.29 + s_ * 0.18, 6.85)
    # 手臂
    hands = []
    for s_ in (-1, 1):
        eb = None if '手肘' in f else (s_, 0.09 * hh)
        wb = None if '手腕' in f else (s_, 0.03 * hh)
        if pose == 'akimbo':
            arm = [(0.62, 1.5, 0.12), (0.86, 1.68, 0.24), (1.1, 2.0, 0.22), (1.38, 2.37, 0.17), (1.5, 2.56, 0.18, eb), (1.32, 2.8, 0.2),
                   (1.0, 3.02, 0.14), (0.9, 3.08, 0.15, wb)]
            hand = (0.74, 3.12, 0.2, 0.13, s_ * 30)
            bones['手肘' + ('L' if s_ < 0 else 'R')] = P(s_ * 1.64, 2.52)
            bones['手腕' + ('L' if s_ < 0 else 'R')] = P(s_ * 0.92, 2.98)
        else:
            arm = [(0.62, 1.5, 0.12), (0.86, 1.7, 0.24), (0.95, 2.1, 0.22), (1.0, 2.6, 0.17), (1.03, 2.85, 0.18, eb), (1.06, 3.2, 0.2),
                   (1.08, 3.65, 0.14), (1.09, 3.78, 0.15, wb)]
            hand = (1.1, 4.05, 0.14, 0.27, 0)
            bones['手肘' + ('L' if s_ < 0 else 'R')] = P(s_ * 1.27, 2.85)
            bones['手腕' + ('L' if s_ < 0 else 'R')] = P(s_ * 1.27, 3.78)
        nd = []
        for i, (x, y, w, *b) in enumerate(arm):
            px, py = P(s_ * x, y)
            nd.append((px, py, w * hh * (uarm if 1 < i < 4 else 1.0), b[0] if b else None))
        shapes.append((limb_path(nd), SKIN))
        hx, hy = P(s_ * hand[0], hand[1])
        hands.append((hx, hy, hand[2] * hh, hand[3] * hh, hand[4]))
    # 躯干
    acx, acy = (0.80, 1.58) if '肩峰' in f else (0.93, 1.44)
    ilx = 0.58 if '髋骨' in f else 0.69
    trx = 0.74 if '髋骨' in f else 0.82
    wl, wr = (waist, waist) if not isinstance(waist, tuple) else waist
    def side_(wk):
        return [(0.14, 1.27), (0.55, 1.35), (acx, acy), (0.74, 1.95), (0.70, 2.3), (0.55 * wk, 2.85), (ilx, 3.2), (trx, 3.6), (0.72, 3.95)]
    pts = [P(-x, y) for x, y in side_(wl)] + [P(0, 3.9)] + [P(x, y) for x, y in side_(wr)[::-1]]
    torso = closed_smooth(pts)
    shapes.append((torso, SKIN))
    neck = f'M{P(-0.14, 0.9)[0]:.1f} {P(-0.14, 0.9)[1]:.1f} L{P(0.14, 0.9)[0]:.1f} {P(0.14, 0.9)[1]:.1f} L{P(0.15, 1.35)[0]:.1f} {P(0.15, 1.35)[1]:.1f} L{P(-0.15, 1.35)[0]:.1f} {P(-0.15, 1.35)[1]:.1f} Z'
    shapes.append((neck, SKIN))
    # 脸
    if '下颌角' in f:
        jaw = [(0.25, 0.80), (0.14, 0.93)]
    else:
        jaw = [(0.335, 0.84), (0.2, 0.96)]
    cb = (0.36, 0.56) if '颧骨' in f else (0.415, 0.56)
    fs = [(0.3, 0.08), (0.40, 0.32), cb, ((0.33 if '颧骨' in f else 0.375), 0.7)] + jaw
    face_pts = [P(0, 0.02)] + [P(-x, y) for x, y in fs] + [P(0, 1.0)] + [P(x, y) for x, y in fs[::-1]]
    face = closed_smooth(face_pts)
    shapes.append((face, SKIN))
    for s_ in (-1, 1):
        k = 'L' if s_ < 0 else 'R'
        bones['颧骨' + k] = P(s_ * 0.415, 0.56)
        bones['下颌角' + k] = P(s_ * 0.335, 0.84)
        bones['锁骨' + k] = P(s_ * 0.42, 1.43)
        bones['肩峰' + k] = P(s_ * 0.93, 1.44)
        bones['髋骨' + k] = P(s_ * 0.69, 3.2)
    out = [back_hair, union(shapes, sw)]
    # 衣服：裁在躯干里面
    out.append(f'<defs><clipPath id="{uid}tor"><path d="{torso}"/></clipPath></defs>')
    gx0, gy0 = P(-1.2, 1.78); gx1, gy1 = P(1.2, 1.78)
    out.append(f'<g clip-path="url(#{uid}tor)"><path d="M{gx0:.1f} {gy0:.1f} Q{cx:.1f} {gy0 + hh * 0.18:.1f} {gx1:.1f} {gy1:.1f} L{cx + hh * 1.2:.1f} {top + hh * 4.2:.1f} L{cx - hh * 1.2:.1f} {top + hh * 4.2:.1f} Z" '
               f'fill="{outfit}" stroke="{INK}" stroke-width="{sw}"/>'
               f'<path d="M{cx - hh * 1.2:.1f} {top + hh * 3.35:.1f} L{cx - hh * 0.25:.1f} {top + hh * 3.92:.1f} L{cx + hh * 0.25:.1f} {top + hh * 3.92:.1f} L{cx + hh * 1.2:.1f} {top + hh * 3.35:.1f} L{cx + hh * 1.2:.1f} {top + hh * 4.3:.1f} L{cx - hh * 1.2:.1f} {top + hh * 4.3:.1f} Z" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/></g>')
    # 锁骨
    if show_clav and '锁骨' not in f:
        for s_ in (-1, 1):
            a = P(s_ * 0.13, 1.38); b = P(s_ * 0.45, 1.46); c = P(s_ * 0.78, 1.42)
            out.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} Q{b[0]:.1f} {b[1]:.1f} {c[0]:.1f} {c[1]:.1f}" fill="none" stroke="{INK}" stroke-width="{sw * 0.7:.1f}" stroke-linecap="round" stroke-opacity=".7"/>')
    # 膝盖小弧线
    if '膝盖' not in f:
        for s_ in (-1, 1):
            a = P(s_ * 0.33 - 0.1, 5.3); b = P(s_ * 0.33, 5.36); c = P(s_ * 0.33 + 0.1, 5.3)
            out.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} Q{b[0]:.1f} {b[1]:.1f} {c[0]:.1f} {c[1]:.1f}" fill="none" stroke="{INK}" stroke-width="{sw * 0.7:.1f}" stroke-linecap="round" stroke-opacity=".6"/>')
    # 手
    for hx, hy, rx, ry, rot in hands:
        out.append(f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" transform="rotate({rot} {hx:.1f} {hy:.1f})" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>')
    # 鞋
    for s_ in (-1, 1):
        x, y = P(s_ * 0.33, 7.08)
        out.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{hh * 0.22:.1f}" ry="{hh * 0.11:.1f}" fill="{INK}"/>')
    # 刘海、眼睛、嘴
    fr = [P(-0.46, 0.44), P(-0.44, 0.2), P(0, -0.05), P(0.44, 0.2), P(0.46, 0.44), P(0.3, 0.3), P(0.05, 0.36), P(-0.2, 0.3)]
    out.append(f'<path d="{closed_smooth(fr)}" fill="{hair}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    for s_ in (-1, 1):
        ex, ey = P(s_ * 0.16 + look * 0.08, 0.6)
        out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{hh * 0.05:.1f}" fill="{INK}"/>')
    m0, m1 = P(-0.07, 0.83), P(0.07, 0.83)
    out.append(f'<path d="M{m0[0]:.1f} {m0[1]:.1f} Q{cx:.1f} {m0[1] + hh * 0.04:.1f} {m1[0]:.1f} {m1[1]:.1f}" fill="none" stroke="{INK}" stroke-width="{sw * 0.7:.1f}" stroke-linecap="round"/>')
    return ''.join(out), bones


def bone_dots(bones, names=BONE9, r=6, fill=RED):
    s = ''
    for k, (x, y) in bones.items():
        if k[:-1] in names:
            s += dot(x, y, r, fill)
    return s


# ---------------- 侧面人物 ----------------
def side_figure(cx, top, hh, uid='s', sw=2.5, outfit=VIO2, hair=PINK):
    def P(x, y):
        return (cx + x * hh, top + y * hh)
    shapes = []
    # 头
    head = [(-0.42, 0.45), (-0.36, 0.14), (-0.08, 0.0), (0.24, 0.07), (0.37, 0.33), (0.41, 0.5), (0.5, 0.63), (0.4, 0.7),
            (0.42, 0.8), (0.35, 0.95), (0.14, 1.0), (-0.06, 0.92), (-0.12, 0.86), (-0.22, 0.78), (-0.42, 0.75)]
    hd = closed_smooth([P(*p) for p in head])
    neck = closed_smooth([P(-0.3, 0.7), P(0.02, 0.86), P(0.2, 1.36), P(-0.26, 1.32)])
    # 躯干（前胸向右）
    tor = [(0.14, 1.3), (0.22, 1.42), (0.42, 1.8), (0.44, 2.05), (0.32, 2.35), (0.27, 2.8), (0.35, 3.22), (0.32, 3.6), (0.24, 3.95),
           (-0.34, 3.95), (-0.52, 3.55), (-0.42, 3.1), (-0.26, 2.7), (-0.34, 2.1), (-0.42, 1.65), (-0.24, 1.25)]
    td = closed_smooth([P(*p) for p in tor])
    leg = [(0.0, 3.55, 0.45), (0.05, 4.3, 0.36), (0.1, 4.95, 0.26), (0.12, 5.25, 0.25, (1, 0.05 * hh)), (0.1, 5.55, 0.22),
           (0.03, 5.9, 0.25, (-1, 0.03 * hh)), (0.0, 6.5, 0.14), (0.0, 6.85, 0.14), (0.0, 6.98, 0.15)]
    ld = limb_path([(P(x, y)[0], P(x, y)[1], w * hh, b[0] if b else None) for (x, y, w, *b) in leg])
    hair_back = closed_smooth([P(-0.1, -0.04), P(0.2, 0.0), P(0.3, 0.2), P(0.05, 0.3), P(-0.1, 0.6), P(-0.32, 1.4), P(-0.6, 1.3), P(-0.5, 0.4)])
    shapes = [(td, SKIN), (ld, SKIN), (neck, SKIN), (hd, SKIN)]
    out = [union(shapes, sw)]
    out.append(f'<defs><clipPath id="{uid}tor"><path d="{td}"/></clipPath></defs>')
    out.append(f'<g clip-path="url(#{uid}tor)"><rect x="{cx - hh}" y="{top + hh * 1.75:.1f}" width="{hh * 2}" height="{hh * 2.4:.1f}" fill="{outfit}" stroke="{INK}" stroke-width="{sw}"/></g>')
    out.append(f'<path d="{hair_back}" fill="{hair}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    ex, ey = P(0.27, 0.55)
    out.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{hh * 0.045:.1f}" fill="{INK}"/>')
    # 手臂（画在躯干前面）
    arm = [(-0.04, 1.36, 0.03), (-0.05, 1.6, 0.25), (-0.1, 2.2, 0.21), (-0.13, 2.65, 0.17), (-0.12, 2.85, 0.18, (-1, 0.06 * hh)), (0.0, 3.25, 0.19),
           (0.12, 3.62, 0.12), (0.15, 3.74, 0.13, (-1, 0.03 * hh))]
    ad = limb_path([(P(x, y)[0], P(x, y)[1], w * hh, b[0] if b else None) for (x, y, w, *b) in arm])
    hx, hy = P(0.2, 4.0)
    hand = f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{hh * 0.13:.1f}" ry="{hh * 0.26:.1f}" transform="rotate(-18 {hx:.1f} {hy:.1f})"/>'
    out.append(union([(ad, SKIN)], sw))
    out.append(f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{hh * 0.13:.1f}" ry="{hh * 0.26:.1f}" transform="rotate(-18 {hx:.1f} {hy:.1f})" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>')
    fx, fy = P(0.0, 7.0)
    out.append(f'<path d="M{fx - hh * 0.16:.1f} {fy - hh * 0.1:.1f} Q{fx - hh * 0.2:.1f} {fy + hh * 0.12:.1f} {fx:.1f} {fy + hh * 0.12:.1f} L{fx + hh * 0.55:.1f} {fy + hh * 0.12:.1f} Q{fx + hh * 0.5:.1f} {fy - hh * 0.04:.1f} {fx + hh * 0.12:.1f} {fy - hh * 0.1:.1f} Z" fill="{INK}"/>')
    # 耳朵
    ex, ey = P(-0.14, 0.58)
    out.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{hh * 0.07:.1f}" ry="{hh * 0.11:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="{sw * 0.8:.1f}"/>')
    bones = {'颧骨': P(0.25, 0.66), '下颌角': P(-0.09, 0.9), '锁骨': P(0.2, 1.42), '肩峰': P(-0.04, 1.36), '手肘': P(-0.32, 2.85),
             '手腕': P(0.0, 3.76), '髋骨': P(0.35, 3.22), '膝盖': P(0.38, 5.25), '脚踝': P(0.0, 6.88)}
    return ''.join(out), bones


def view(content, vx, vy, vw, vh, x, y, w, h, uid):
    """把 content 的一块区域 (vx,vy,vw,vh) 放大显示到 (x,y,w,h)"""
    return (f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vx} {vy} {vw} {vh}" preserveAspectRatio="xMidYMid slice">'
            f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="{BG}"/>{content}</svg>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="none" stroke="{INK}" stroke-width="2"/>')


def room(x, y, w, h, floor_frac=0.86, door_x=0.1):
    fy = y + h * floor_frac
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{BG}"/>'
    if door_x is not None:
        s += door(x + w * door_x, y + h * 0.18, w * 0.2, fy)
    s += f'<rect x="{x}" y="{fy:.1f}" width="{w}" height="{y + h - fy:.1f}" fill="{FLOOR}"/>' + line(x, fy, x + w, fy, INK, 2)
    return s, fy


# ================= 3.5 骨点和解剖 =================
FRONT_LABELS = {  # 骨点: (哪一侧, 标签 y 偏移)
    '颧骨': ('L', 0), '下颌角': ('R', 0), '锁骨': ('L', -6), '肩峰': ('R', -10), '手肘': ('L', 0),
    '手腕': ('R', 0), '髋骨': ('L', 0), '膝盖': ('R', 0), '脚踝': ('L', 0)}


def p_bones_front():
    Wd, Hd = 760, 640
    hh = 76; cx = 380; top = 40
    fig, b = mannequin(cx, top, hh, uid='pf')
    s = [fig, bone_dots(b)]
    for i, name in enumerate(BONE9):
        sd, dy = FRONT_LABELS[name]
        bx, by = b[name + sd]
        lx = 40 if sd == 'L' else Wd - 40
        s.append(leader(bx, by, lx + (150 if sd == 'L' else -150), by + dy))
        s.append(label(lx, by + dy + 6, f'{i + 1} {name}', YEL1 if i % 2 == 0 else VIO1, 15, 'start' if sd == 'L' else 'end'))
    s.append(text(Wd / 2, Hd - 14, '左右两边位置对称，图上每个骨点只标了一侧', 13, 600, MUTED, 'middle'))
    save('p-bones-front', svg(Wd, Hd, ''.join(s), '正面的 9 个骨点'))


SIDE_LABELS = {'颧骨': ('R', -14), '下颌角': ('L', 0), '锁骨': ('R', 0), '肩峰': ('L', -6), '手肘': ('L', 0),
               '手腕': ('L', 10), '髋骨': ('R', 0), '膝盖': ('R', 0), '脚踝': ('L', 0)}


def p_bones_side():
    Wd, Hd = 760, 640
    hh = 76; cx = 370; top = 40
    fig, b = side_figure(cx, top, hh, uid='ps')
    s = [fig]
    for i, name in enumerate(BONE9):
        bx, by = b[name]
        inside = name == '脚踝'
        s.append(dot(bx, by, 6, RED if not inside else PINK))
        sd, dy = SIDE_LABELS[name]
        lx = 40 if sd == 'L' else Wd - 40
        s.append(leader(bx, by, lx + (150 if sd == 'L' else -150), by + dy))
        s.append(label(lx, by + dy + 6, f'{i + 1} {name}', YEL1 if i % 2 == 0 else VIO1, 15, 'start' if sd == 'L' else 'end'))
    s.append(dot(40, Hd - 20, 6, RED) + text(54, Hd - 14, '在侧面轮廓线上', 13, 600, MUTED))
    s.append(dot(220, Hd - 20, 6, PINK) + text(234, Hd - 14, '侧面时在轮廓里面，看明暗转折（3.1 课）', 13, 600, MUTED))
    save('p-bones-side', svg(Wd, Hd, ''.join(s), '侧面的 9 个骨点'))


def p_bones_flat():
    """三处骨点：保留 vs 推平"""
    Wd, Hd = 900, 430
    s = []
    hh = 60
    good, _ = mannequin(300, 40, hh, pose='akimbo', uid='fg')
    bad, _ = mannequin(300, 40, hh, pose='akimbo', flat=BONE9, uid='fb')
    # 每组：区域 (vx, vy, vw, vh)
    groups = [('下颌角', '脸变成尖锥，像贴上去的', (300 - 0.75 * hh, 40 - 0.1 * hh, 1.5 * hh, 1.5 * hh)),
              ('肩峰', '肩膀变成斜坡（溜肩）', (300 + 0.1 * hh, 40 + 0.9 * hh, 1.6 * hh, 1.6 * hh)),
              ('手肘', '手臂像一根弯面条', (300 + 0.75 * hh, 40 + 1.75 * hh, 1.3 * hh, 1.3 * hh))]
    for i, (name, bad_txt, (vx, vy, vw, vh)) in enumerate(groups):
        ox = 20 + i * 293
        s.append(card(ox, 10, 277, 410, name, YEL1))
        s.append(view(good, vx, vy, vw, vh, ox + 14, 62, 120, 120, f'g{i}'))
        s.append(view(bad, vx, vy, vw, vh, ox + 143, 62, 120, 120, f'b{i}'))
        s.append(text(ox + 74, 204, '保留', 14, 800, MINT7, 'middle') + text(ox + 203, 204, '推平', 14, 800, RED7, 'middle'))
        s.append(label(ox + 14, 246, '推平后：', RED1, 13))
        s.append(text(ox + 14, 278, bad_txt, 14, 700))
    tips = [('眼睛把它读成：', '脸没有骨架，只剩软肉'), ('眼睛把它读成：', '肩膀塌了，人没精神'), ('眼睛把它读成：', '手臂没有骨头，又软又肿')]
    for i, (a, b2) in enumerate(tips):
        ox = 20 + i * 293
        s.append(text(ox + 14, 320, a, 13, 600, MUTED) + text(ox + 14, 346, b2, 14, 700))
        s.append(text(ox + 14, 392, '修法：推骨点之间，骨点只轻带', 13, 700, VIO7))
    save('p-bones-flat', svg(Wd, Hd, ''.join(s), '下颌角、肩峰、手肘被推平以后的样子'))


def p_blocks():
    Wd, Hd = 860, 600
    s = []
    hh = 66
    for col, (title, tilt) in enumerate([('三个体块：头、胸腔、骨盆', 0.0), ('重心放在一条腿上：两条线反向倾斜', 0.16)]):
        ox = 20 + col * 420
        s.append(card(ox, 10, 400, 580, title, YEL1 if col == 0 else VIO1, 15))
        cx = ox + 200; top = 70
        fig, b = mannequin(cx, top, hh, uid=f'bk{col}', tilt=tilt)
        s.append(f'<g opacity=".35">{fig}</g>')
        def P(x, y):
            if 1.2 < y < 2.0: y += x * tilt
            elif 3.0 < y < 4.0: y -= x * tilt
            return (cx + x * hh, top + y * hh)
        # 头：蛋形
        s.append(f'<ellipse cx="{cx}" cy="{top + 0.5 * hh:.1f}" rx="{0.45 * hh:.1f}" ry="{0.56 * hh:.1f}" fill="{PINK}" fill-opacity=".35" stroke="{INK}" stroke-width="3"/>')
        # 胸腔：倒梯形盒子
        c = [P(-0.82, 1.45), P(0.82, 1.45), P(0.6, 2.55), P(-0.6, 2.55)]
        s.append(f'<path d="M{c[0][0]:.1f} {c[0][1]:.1f} L{c[1][0]:.1f} {c[1][1]:.1f} L{c[2][0]:.1f} {c[2][1]:.1f} L{c[3][0]:.1f} {c[3][1]:.1f} Z" fill="{VIO}" fill-opacity=".35" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
        # 骨盆：正梯形盒子
        p = [P(-0.62, 3.1), P(0.62, 3.1), P(0.78, 3.85), P(-0.78, 3.85)]
        s.append(f'<path d="M{p[0][0]:.1f} {p[0][1]:.1f} L{p[1][0]:.1f} {p[1][1]:.1f} L{p[2][0]:.1f} {p[2][1]:.1f} L{p[3][0]:.1f} {p[3][1]:.1f} Z" fill="{MINT}" fill-opacity=".4" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
        # 脊柱
        a = (cx, top + 1.0 * hh); m = ((c[2][0] + c[3][0]) / 2, (c[2][1] + p[0][1]) / 2 + 0.0); e = ((p[0][0] + p[1][0]) / 2, (p[0][1] + p[1][1]) / 2)
        s.append(f'<path d="M{a[0]:.1f} {a[1]:.1f} Q{m[0] + tilt * 120:.1f} {m[1]:.1f} {e[0]:.1f} {e[1]:.1f}" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="6 5"/>')
        # 肩线和胯线
        sl = (P(-0.95, 1.44), P(0.95, 1.44)); hl = (P(-0.75, 3.2), P(0.75, 3.2))
        for (p1, p2), col_ in ((sl, VIO7), (hl, MINT7)):
            ex = 0.25
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            s.append(line(p1[0] - dx * ex, p1[1] - dy * ex, p2[0] + dx * ex, p2[1] + dy * ex, col_, 3.5))
        if col == 0:
            s.append(label(ox + 230, top + 0.25 * hh, '头：蛋形', PINK1, 13))
            s.append(label(ox + 268, top + 2.2 * hh, '胸腔', VIO1, 13))
            s.append(label(ox + 268, top + 3.6 * hh, '骨盆', MINT1, 13))
            s.append(label(ox + 14, top + 2.85 * hh, '腰：软的连接', WHITE, 13))
            s.append(label(ox + 14, top + 5.2 * hh, '四肢：一节节圆柱', WHITE, 13))
        else:
            s.append(label(ox + 268, sl[1][1] - 18, '肩线', VIO1, 13))
            s.append(label(ox + 268, hl[1][1] + 34, '胯线', MINT1, 13))
            s.append(text(ox + 200, 560, '肩线往一边斜，胯线就往另一边斜', 14, 700, INK, 'middle'))
    save('p-blocks', svg(Wd, Hd, ''.join(s), '体块：头、胸腔、骨盆三个硬块，中间用脊柱连接'))


def p_local_global():
    Wd, Hd = 900, 560
    s = []
    hh = 58
    items = [('原图', dict(), MINT1, ['']),
             ('只看局部：每处都"修好了"', dict(waist=(0.66, 0.9), uarm=0.6, flat=('髋骨',)), RED1, []),
             ('从整体修：骨点间少量收', dict(waist=0.9, uarm=0.93), VIO1, [])]
    for i, (title, kw, fill, _) in enumerate(items):
        ox = 20 + i * 293
        s.append(card(ox, 10, 277, 540, title, fill, 14))
        fig, b = mannequin(ox + 138, 66, hh, uid=f'lg{i}', **kw)
        s.append(fig)
    # 问题标注（中间）
    ox = 313; cx = ox + 138; top = 66
    marks = [((cx - 0.4 * hh, top + 2.85 * hh), '①', '左腰收得比右边多'), ((cx + 0.95 * hh, top + 2.1 * hh), '②', '上臂比小臂还细'),
             ((cx - 0.62 * hh, top + 3.25 * hh), '③', '胯推平，骨盆变窄')]
    for (x, y), n, t in marks:
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="none" stroke="{RED}" stroke-width="3"/>')
    s.append(badge(cx - 0.4 * hh - 26, top + 2.85 * hh, 1, RED1) + badge(cx + 0.95 * hh + 24, top + 2.1 * hh - 10, 2, RED1) + badge(cx - 0.62 * hh - 26, top + 3.35 * hh + 14, 3, RED1))
    ty = 500
    s.append(text(ox + 14, top + 7.55 * hh, '① 左右腰不一样　② 上臂比小臂细', 13, 700, RED7))
    s.append(text(ox + 14, top + 7.55 * hh + 22, '③ 骨盆比胸腔窄太多，下半身接不上', 13, 700, RED7))
    s.append(text(20 + 14, top + 7.55 * hh, '胸腔、骨盆、四肢的宽窄', 13, 700, MINT7))
    s.append(text(20 + 14, top + 7.55 * hh + 22, '有固定的节奏', 13, 700, MINT7))
    s.append(text(606 + 14, top + 7.55 * hh, '左右收一样多，上粗下细的', 13, 700, VIO7))
    s.append(text(606 + 14, top + 7.55 * hh + 22, '节奏不变，骨点都还在', 13, 700, VIO7))
    save('p-local-global', svg(Wd, Hd, ''.join(s), '局部都对、整体难看：左右不一致、粗细节奏断了、体块关系乱了'))




# ---------------- 界面里的"照片" ----------------
CX, CY, CW, CH = 262, 66, 276, 340


def photo_pose(flat=(), waist=1.0, uid='ph', hh=None, x=CX, y=CY, w=CW, h=CH, tilt=0.1):
    rm, fy = room(x, y, w, h, 0.9, 0.06)
    hh = hh or (fy - (y + h * 0.04)) / 7.25
    fig, b = mannequin(x + w * 0.56, y + h * 0.04, hh, flat=flat, pose='akimbo', waist=waist, uid=uid, sw=2, tilt=tilt)
    return rm + fig, b


def lock_icon(x, y, c=UITEXT):
    return (f'<rect x="{x - 6}" y="{y - 2}" width="12" height="10" rx="2" fill="{c}"/>'
            f'<path d="M{x - 4} {y - 2} v-3 a4 4 0 0 1 8 0 v3" fill="none" stroke="{c}" stroke-width="2"/>')


def u_bones_layer():
    ph, b = photo_pose(uid='ubl')
    lay = layers_panel([('骨点', None, 'N', True), ('原图', 'scene', 'N', False)], x=556, y=84, w=220)
    s = screen(ph + bone_dots(b, r=5) + lay, active='layers')
    s += lock_icon(556 + 220 - 70, 84 + 44 + 52 + 22)
    s += ring(556 + 220 - 26, 84 + 24, 16) + badge(556 + 220 - 52, 84 + 22, 1)
    s += ring(*icon_pos('brush'), 18) + badge(icon_pos('brush')[0] - 26, 62, 2)
    s += label(556, 250, '① 点「+」新建一层，', YEL1, 14)
    s += label(556, 280, '　 改名「骨点」', YEL1, 14)
    s += label(556, 316, '② 技术笔，选红色，', YEL1, 14)
    s += label(556, 346, '　 在每个骨点上点一下', YEL1, 14)
    s += label(70, 500, '原图层锁着，骨点画在上面那层', WHITE, 14)
    s += note('示意图，按钮位置以实际界面为准')
    save('u-bones-layer', svg(W, H, s, '新建骨点图层，用红色在骨点上点点'))


def u_blocks_draw():
    ph, b = photo_pose(uid='ubd')
    hh = (CY + CH * 0.9 - (CY + CH * 0.04)) / 7.25
    cx = CX + CW * 0.56; top = CY + CH * 0.04; t = 0.1
    def P(x, y):
        if 1.2 < y < 2.0: y += x * t
        elif 3.0 < y < 4.0: y -= x * t
        return (cx + x * hh, top + y * hh)
    g = ''
    sl = (P(-1.1, 1.44), P(1.1, 1.44)); hl = (P(-0.95, 3.2), P(0.95, 3.2))
    g += line(*sl[0], *sl[1], MINT, 4) + line(*hl[0], *hl[1], MINT, 4)
    c = [P(-0.82, 1.45), P(0.82, 1.45), P(0.6, 2.55), P(-0.6, 2.55)]
    p = [P(-0.62, 3.1), P(0.62, 3.1), P(0.78, 3.85), P(-0.78, 3.85)]
    for q in (c, p):
        g += f'<path d="M{q[0][0]:.1f} {q[0][1]:.1f} L{q[1][0]:.1f} {q[1][1]:.1f} L{q[2][0]:.1f} {q[2][1]:.1f} L{q[3][0]:.1f} {q[3][1]:.1f} Z" fill="none" stroke="{MINT}" stroke-width="3.5" stroke-linejoin="round"/>'
    # 速创形状提示条
    tip = f'<rect x="100" y="72" width="120" height="34" rx="10" fill="{UIBAR}"/>' + text(160, 95, '编辑形状', 15, 700, UITEXT, 'middle')
    s = screen(ph + g + tip, active='brush')
    s += ring(*icon_pos('brush'), 18)
    s += badge(sl[1][0] + 18, sl[1][1] - 4, 1) + badge(hl[1][0] + 18, hl[1][1] + 4, 2) + badge(c[0][0] - 40, (c[0][1] + c[3][1]) / 2, 3)
    s += label(560, 200, '① 沿两边肩峰画肩线', YEL1, 14)
    s += label(560, 232, '② 沿两边髋骨画胯线', YEL1, 14)
    s += label(560, 264, '③ 框出胸腔和骨盆两个盒子', YEL1, 14)
    s += label(560, 316, '画完笔不抬，停一下就变直线', WHITE, 14)
    s += label(560, 348, '（速创形状）', WHITE, 14)
    s += note('示意图')
    save('u-blocks-draw', svg(W, H, s, '在新图层上用速创形状画肩线、胯线和体块'))


def u_bones_liquify():
    ph, b = photo_pose(uid='ubq')
    hh = (CY + CH * 0.9 - (CY + CH * 0.04)) / 7.25
    cx = CX + CW * 0.56; top = CY + CH * 0.04
    bx, by = cx - 0.66 * hh, top + 2.75 * hh
    brush = f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{hh * 0.55:.1f}" fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-dasharray="5 4"/>' + arrow(bx - 12, by, bx + 12, by, VIO7, 3, marker='arwv')
    s = screen(ph + bone_dots(b, r=5) + brush + tool_sliders([('尺寸', 0.45), ('压力', 0.2), ('失真', 0.0), ('动力', 0.0)], mode='推', buttons=('调整', '重置')), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += label(66, 120, '骨点层放在最上面', YEL1, 14)
    s += label(66, 152, '液化只改当前层', YEL1, 14)
    s += label(66, 184, '红点不会跟着动', YEL1, 14)
    s += label(66, 300, '笔刷放在两个', WHITE, 14)
    s += label(66, 332, '骨点之间推', WHITE, 14)
    s += label(560, 200, '推完看：轮廓还贴着红点吗？', YEL1, 14)
    s += label(560, 232, '离开红点 = 骨点被推动了', RED1, 14)
    s += note('示意图')
    save('u-bones-liquify', svg(W, H, s, '液化时把骨点层开在上面当参照'))


# ---------------- 3.5 案例 ----------------
def mk_pose(kind):
    Wd, Hd = 640, 560
    x, y, w, h = 20, 20, 600, 520
    flat = ('手肘', '下颌角', '膝盖', '髋骨') if kind != 'fixed' else ()
    waist = 0.78 if kind != 'fixed' else 0.9
    ph, b = photo_pose(flat=flat, waist=waist, uid='cp' + kind, x=x, y=y, w=w, h=h, tilt=0.1)
    s = [f'<defs><clipPath id="cpc{kind}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#cpc{kind})">', ph, '</g>']
    if kind == 'marked':
        _, b0 = photo_pose(uid='cpm0', x=x, y=y, w=w, h=h, tilt=0.1)
        s.append(bone_dots(b0, r=6))
        bad = [('手肘R', '手肘被磨圆', 1), ('手肘L', '', 0), ('下颌角R', '下颌角没了', 1), ('膝盖R', '膝盖成了直管', 1), ('髋骨L', '髋骨推进去了', -1)]
        for k, t, sd in bad:
            bx, by = b0[k]
            s.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="16" fill="none" stroke="{RED}" stroke-width="3"/>')
            if t:
                lx = bx + 26 if sd > 0 else bx - 26
                s.append(label(lx, by + 6, t, RED1, 14, 'start' if sd > 0 else 'end'))
        s.append(label(34, 528, '红点：在原图上标的骨点。红圈：修完后轮廓离开了红点', WHITE, 14))
        title = '诊断：把原图的骨点层盖在修过的图上'
    elif kind == 'bad':
        title = '修之前（别人推过的版本）：手肘、下颌角、膝盖被推平'
    else:
        title = '重修后：骨点都在，只收了骨点之间'
    s.append(label(34, 56, title, YEL1 if kind != 'fixed' else VIO1, 15))
    return svg(Wd, Hd, ''.join(s), title)


def case_pose_bad():
    save('case-pose-bad', mk_pose('bad'))


def case_pose_fixed():
    save('case-pose-fixed', mk_pose('fixed'))


def case_pose_marked():
    save('case-pose-marked', mk_pose('marked'))


def mk_face(kind):
    Wd, Hd = 640, 520
    hh = 230
    cx = 320; top = 40
    flat = ('下颌角', '颧骨', '肩峰') if kind == 'bad' else ()
    fig, b = mannequin(cx, top, hh, flat=flat, uid='cf' + kind, sw=4)
    s = [f'<rect width="{Wd}" height="{Hd}" fill="#E9E3F5"/>', fig]
    if kind == 'bad':
        title = '修之前：瘦脸推掉了下颌角和颧骨，肩也推塌了'
    else:
        title = '修之后：下颌角、颧骨、肩峰都留着'
    s.append(label(24, Hd - 18, title, YEL1 if kind == 'bad' else VIO1, 15))
    return svg(Wd, Hd, ''.join(s), title)


def case_face_bad():
    save('case-face-bad', mk_face('bad'))


def case_face_fixed():
    save('case-face-fixed', mk_face('fixed'))


# ================= 3.6 透视和镜头畸变 =================
def inter(p1, p2, p3, p4):
    """两条直线 p1p2、p3p4 的交点"""
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    a = x1 * y2 - y1 * x2; b = x3 * y4 - y3 * x4
    return ((a * (x3 - x4) - (x1 - x2) * b) / d, (a * (y3 - y4) - (y1 - y2) * b) / d)


def poly(pts, fill='none', stroke=INK, w=2.5, op=None, extra=''):
    o = f' fill-opacity="{op}"' if op else ''
    return f'<path d="M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + f' Z" fill="{fill}"{o} stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round" {extra}/>'


def vp_mark(x, y, name='消失点', anchor='middle', dy=-14, fill=RED1):
    return dot(x, y, 7, RED) + label(x, y + dy, name, fill, 13, anchor)


def horizon(x1, x2, y, txt='视平线', tx=None, dy=-10, anchor='end'):
    s = line(x1, y, x2, y, VIO7, 3, '10 6')
    s += label(tx if tx is not None else x2 - 8, y + dy, txt, VIO1, 13, anchor)
    return s


def p_persp_points():
    Wd, Hd = 960, 420
    s = []
    titles = [('一点透视', '正对着走廊、墙面拍', YEL1), ('两点透视', '斜对着建筑的一角拍', VIO1), ('三点透视', '仰拍或俯拍高的东西', MINT1)]
    for i, (t, sub, fill) in enumerate(titles):
        ox = 20 + i * 315
        s.append(card(ox, 10, 300, 400, t, fill))
        s.append(text(ox + 150, 392, sub, 14, 700, MUTED, 'middle'))
    # 一点：走廊
    ox = 20; x0, y0, x1, y1 = ox + 15, 60, ox + 285, 360
    vp = (ox + 150, 190)
    k = 0.28
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    back = [(vp[0] + (cx_ - vp[0]) * k, vp[1] + (cy_ - vp[1]) * k) for cx_, cy_ in corners]
    s.append(f'<defs><clipPath id="pp1"><rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}"/></clipPath></defs><g clip-path="url(#pp1)">')
    s.append(poly([corners[3], corners[2], back[2], back[3]], FLOOR, INK, 2))
    s.append(poly([corners[0], corners[3], back[3], back[0]], YEL1, INK, 2))
    s.append(poly([corners[1], corners[2], back[2], back[1]], YEL1, INK, 2))
    s.append(poly(back, WHITE, INK, 2.5))
    for fx in (x0 + 70, x0 + 135, x0 + 200):
        bx = vp[0] + (fx - vp[0]) * k; by = vp[1] + (y1 - vp[1]) * k
        s.append(line(fx, y1, bx, by, MUTED, 1.5))
    for kk in (0.8, 0.6, 0.45, 0.35):
        a = (vp[0] + (x0 - vp[0]) * kk, vp[1] + (y1 - vp[1]) * kk); b = (vp[0] + (x1 - vp[0]) * kk, a[1])
        s.append(line(a[0], a[1], b[0], b[1], MUTED, 1.5))
    for c_ in corners:
        s.append(line(c_[0], c_[1], vp[0], vp[1], RED, 1.5, '5 4'))
    s.append('</g>')
    s.append(horizon(x0, x1, vp[1]) + vp_mark(*vp, '消失点', dy=-16))
    # 两点：盒子
    ox = 335
    hz = 180; v1 = (ox + 18, hz); v2 = (ox + 282, hz)
    T = (ox + 150, 110); B = (ox + 150, 300)
    def at_x(p, v, x):
        t = (x - p[0]) / (v[0] - p[0]); return (x, p[1] + (v[1] - p[1]) * t)
    TL = at_x(T, v1, ox + 75); BL = at_x(B, v1, ox + 75); TR = at_x(T, v2, ox + 235); BR = at_x(B, v2, ox + 235)
    s.append(poly([T, B, BL, TL], YEL1))
    s.append(poly([T, B, BR, TR], VIO1))
    for p_, v_ in ((T, v1), (B, v1), (T, v2), (B, v2)):
        s.append(line(p_[0], p_[1], v_[0], v_[1], RED, 1.5, '5 4'))
    s.append(horizon(ox + 15, ox + 285, hz, '视平线', ox + 150, -60, 'middle'))
    s.append(vp_mark(*v1, '消失点 1', 'start', dy=34) + vp_mark(*v2, '消失点 2', 'end', dy=34))
    s.append(label(ox + 150, 344, '竖线仍然竖直', WHITE, 13, 'middle'))
    # 三点：仰拍高楼
    ox = 650
    hz = 330; v1 = (ox + 14, hz); v2 = (ox + 286, hz); v3 = (ox + 150, -420)
    B = (ox + 150, 318); T = (B[0], 100)
    BL = inter(B, v1, (ox + 80, 0), (ox + 80, 400)); BR = inter(B, v2, (ox + 225, 0), (ox + 225, 400))
    TL = inter(BL, v3, T, v1); TR = inter(BR, v3, T, v2)
    s.append(poly([T, B, BL, TL], YEL1))
    s.append(poly([T, B, BR, TR], VIO1))
    for r in range(1, 5):
        a = (B[0] + (T[0] - B[0]) * r / 5, B[1] + (T[1] - B[1]) * r / 5)
        s.append(line(a[0], a[1], *inter(a, v1, BL, TL), INK, 1.2) + line(a[0], a[1], *inter(a, v2, BR, TR), INK, 1.2))
    for p_ in (TL, T, TR):
        e = (p_[0] + (v3[0] - p_[0]) * 0.07, p_[1] + (v3[1] - p_[1]) * 0.07)
        s.append(line(p_[0], p_[1], e[0], e[1], RED, 1.5, '5 4'))
    for p_, v_ in ((T, v1), (T, v2)):
        s.append(line(p_[0], p_[1], v_[0], v_[1], RED, 1.5, '5 4'))
    s.append(horizon(ox + 15, ox + 285, hz, '视平线', ox + 150, 30, 'middle'))
    s.append(vp_mark(*v1, '1', 'start', dy=-14) + vp_mark(*v2, '2', 'end', dy=-14) + label(ox + 150, 82, '↑ 竖线聚向上方很远的消失点 3', RED1, 12, 'middle'))
    save('p-persp-points', svg(Wd, Hd, ''.join(s), '一点、两点、三点透视'))


def person(cx, feet, hp, fill=VIO2):
    """简笔人：hp 为身高像素"""
    hr = hp * 0.07
    return (f'<rect x="{cx - hp * 0.11:.1f}" y="{feet - hp * 0.84:.1f}" width="{hp * 0.22:.1f}" height="{hp * 0.84:.1f}" rx="{hp * 0.08:.1f}" fill="{fill}" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="{cx:.1f}" cy="{feet - hp + hr:.1f}" r="{hr:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')


def camera_icon(x, y, s=1.0):
    return (f'<rect x="{x - 16 * s:.1f}" y="{y - 11 * s:.1f}" width="{32 * s:.1f}" height="{22 * s:.1f}" rx="4" fill="{INK}"/>'
            f'<circle cx="{x + 5 * s:.1f}" cy="{y:.1f}" r="{6 * s:.1f}" fill="{VIO2}"/>')


def p_horizon():
    Wd, Hd = 960, 440
    s = []
    cases = [('相机在膝盖高度', 0.28, 250, '视平线穿过每个人的膝盖', YEL1), ('相机在胸口高度', 0.72, 175, '视平线穿过每个人的胸口', MINT1),
             ('相机举过头顶', 1.18, 92, '视平线在所有人头顶上方', RED1)]
    for i, (t, c, hz, sub, fill) in enumerate(cases):
        ox = 20 + i * 315
        s.append(card(ox, 10, 300, 420, t, fill))
        x0, x1 = ox + 12, ox + 288
        s.append(f'<defs><clipPath id="hz{i}"><rect x="{x0}" y="56" width="{x1 - x0}" height="320"/></clipPath></defs><g clip-path="url(#hz{i})">')
        s.append(f'<rect x="{x0}" y="{hz}" width="{x1 - x0}" height="{376 - hz}" fill="{FLOOR}"/>')
        vpx = ox + 150
        for gx in range(-6, 7):
            s.append(line(vpx + gx * 60, 380, vpx, hz, '#CBD5E1', 1.2))
        s.append('</g>')
        for px_, hp in ((ox + 70, 150), (ox + 170, 95), (ox + 240, 55)):
            feet = hz + c * hp
            s.append(person(px_, feet, hp, [VIO2, PINK, MINT][int(hp) % 3]))
            s.append(dot(px_, hz, 4, VIO7, WHITE))
        s.append(horizon(x0, x1, hz, '视平线', x1 - 6))
        s.append(camera_icon(x0 + 22, hz - 26, 0.8))
        s.append(text(ox + 150, 404, sub, 14, 700, INK, 'middle'))
    save('p-horizon', svg(Wd, Hd, ''.join(s), '视平线就在相机的高度：它穿过人的哪里，相机就在哪个高度'))


def face_front(cx, cy, r, nose=1.0, ear=1.0, width=1.0, sw=2.5):
    s = ''
    for sg in (-1, 1):
        s += f'<ellipse cx="{cx + sg * r * 0.86 * width:.1f}" cy="{cy + r * 0.05:.1f}" rx="{r * 0.14 * ear:.1f}" ry="{r * 0.24 * ear:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>'
    s += f'<ellipse cx="{cx}" cy="{cy}" rx="{r * 0.82 * width:.1f}" ry="{r:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>'
    s += f'<path d="M{cx - r * 0.85 * width:.1f} {cy - r * 0.2:.1f} Q{cx - r * 0.8:.1f} {cy - r * 1.15:.1f} {cx:.1f} {cy - r * 1.08:.1f} Q{cx + r * 0.8:.1f} {cy - r * 1.15:.1f} {cx + r * 0.85 * width:.1f} {cy - r * 0.2:.1f} Q{cx + r * 0.3:.1f} {cy - r * 0.6:.1f} {cx:.1f} {cy - r * 0.55:.1f} Q{cx - r * 0.3:.1f} {cy - r * 0.6:.1f} {cx - r * 0.85 * width:.1f} {cy - r * 0.2:.1f} Z" fill="{PINK}" stroke="{INK}" stroke-width="{sw}"/>'
    for sg in (-1, 1):
        s += f'<circle cx="{cx + sg * r * 0.32 * width:.1f}" cy="{cy - r * 0.08:.1f}" r="{r * 0.07:.1f}" fill="{INK}"/>'
    s += f'<ellipse cx="{cx}" cy="{cy + r * 0.22:.1f}" rx="{r * 0.1 * nose:.1f}" ry="{r * 0.16 * nose:.1f}" fill="{PINK1}" stroke="{INK}" stroke-width="{sw * 0.8:.1f}"/>'
    s += f'<path d="M{cx - r * 0.18:.1f} {cy + r * 0.55:.1f} Q{cx} {cy + r * 0.65:.1f} {cx + r * 0.18:.1f} {cy + r * 0.55:.1f}" fill="none" stroke="{INK}" stroke-width="{sw * 0.8:.1f}" stroke-linecap="round"/>'
    return s


def head_top(cx, cy, r):
    """俯视的头：圆 + 鼻子 + 两只耳朵（鼻子朝左，朝向相机）"""
    return (f'<ellipse cx="{cx}" cy="{cy - r * 0.95:.1f}" rx="{r * 0.18:.1f}" ry="{r * 0.12:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>'
            f'<ellipse cx="{cx}" cy="{cy + r * 0.95:.1f}" rx="{r * 0.18:.1f}" ry="{r * 0.12:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>'
            f'<path d="M{cx - r * 0.9:.1f} {cy - r * 0.18:.1f} L{cx - r * 1.25:.1f} {cy:.1f} L{cx - r * 0.9:.1f} {cy + r * 0.18:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')


def p_distance():
    Wd, Hd = 900, 470
    s = [card(20, 10, 560, 450, '俯视图：同样拍满一张脸', YEL1), card(600, 10, 280, 450, '拍出来', VIO1)]
    rows = [('近：0.5 米，只能用广角', 380, 150, 1.5, 0.45, 0.86, '鼻子大、耳朵小，脸变窄'), ('远：2 米，要用 2× 或 3×', 70, 330, 1.0, 1.0, 1.0, '和眼睛看到的差不多')]
    for t, camx, cy, nose, ear, wid, res in rows:
        hx = 500; r = 34
        s.append(head_top(hx, cy, r))
        s.append(camera_icon(camx, cy, 1.0))
        # 视角：到头两侧的切线
        d = hx - camx
        a = math.asin(r * 1.15 / d)
        L = d + 20
        for sg in (-1, 1):
            s.append(line(camx + 16, cy, camx + 16 + L * math.cos(a), cy + sg * L * math.sin(a), VIO7, 2, '6 4'))
        s.append(label(40, cy - 58, t, WHITE, 14))
        s.append(face_front(740, cy, 56, nose, ear, wid))
        s.append(text(740, cy + 82, res, 14, 700, INK, 'middle'))
        s.append(line(camx, cy + 52, hx, cy + 52, MUTED, 1.5) + text((camx + hx) / 2, cy + 72, '拍摄距离', 13, 600, MUTED, 'middle'))
    s.append(text(40, 438, '鼻尖比耳朵离镜头近约 10 厘米：0.5 米时鼻子被多放大 20%，2 米时只多 5%', 13, 700, INK))
    save('p-distance', svg(Wd, Hd, ''.join(s), '脸变不变形，看拍摄距离：离得近才不得不用广角'))


def warp_pts(pts, cx, cy, R, k):
    out = []
    for x, y in pts:
        dx, dy = (x - cx) / R, (y - cy) / R
        r2 = dx * dx + dy * dy
        f = 1 + k * r2
        out.append((cx + dx * f * R, cy + dy * f * R))
    return out


def pl(pts, color=INK, w=2.5, fill='none'):
    return f'<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="{fill}" stroke="{color}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"/>'


def grid_scene(x0, y0, w, h, k):
    """一个有门框和地砖的方格场景，按桶形 / 枕形系数 k 变形"""
    cx, cy = x0 + w / 2, y0 + h / 2; R = math.hypot(w, h) / 2
    s = ''
    n = 40
    for i in range(7):
        X = x0 + w * i / 6
        s += pl(warp_pts([(X, y0 + h * j / n) for j in range(n + 1)], cx, cy, R, k), MUTED if 0 < i < 6 else INK, 1.5 if 0 < i < 6 else 2.5)
    for i in range(6):
        Y = y0 + h * i / 5
        s += pl(warp_pts([(x0 + w * j / n, Y) for j in range(n + 1)], cx, cy, R, k), MUTED, 1.5)
    s += pl(warp_pts([(x0 + w * j / n, y0 + h) for j in range(n + 1)], cx, cy, R, k), INK, 2.5)
    # 两根柱子
    for px in (x0 + w * 0.12, x0 + w * 0.88):
        s += pl(warp_pts([(px, y0 + h * j / n) for j in range(n + 1)], cx, cy, R, k), VIO7, 6)
    return s


def p_distort_lens():
    Wd, Hd = 960, 420
    s = []
    items = [('原样', 0.0, '直线都是直的', YEL1), ('桶形畸变', -0.16, '直线往外鼓，越靠边越弯', RED1), ('枕形畸变', 0.12, '直线往里凹（长焦偶尔有）', VIO1)]
    for i, (t, k, sub, fill) in enumerate(items):
        ox = 20 + i * 315
        s.append(card(ox, 10, 300, 400, t, fill))
        x0, y0, w, h = ox + 40, 70, 220, 260
        s.append(f'<defs><clipPath id="dl{i}"><rect x="{ox + 10}" y="56" width="280" height="300"/></clipPath></defs><g clip-path="url(#dl{i})">')
        s.append(grid_scene(x0, y0, w, h, k))
        s.append('</g>')
        s.append(text(ox + 150, 384, sub, 14, 700, INK, 'middle'))
    save('p-distort-lens', svg(Wd, Hd, ''.join(s), '镜头畸变：整张画面一起弯，直线变成弧线'))


def p_distort_persp():
    Wd, Hd = 900, 430
    s = [card(20, 10, 540, 410, '侧视图：手离镜头 0.4 米，脸 0.8 米', YEL1), card(580, 10, 300, 410, '拍出来', VIO1)]
    camx, camy = 60, 220
    s.append(camera_icon(camx, camy, 1.1))
    sc = 400  # 1 米 = 400 px
    hx = camx + 0.4 * sc; fx = camx + 0.8 * sc
    # 人（侧面简笔，脸在 fx，手伸到 hx）
    s.append(f'<circle cx="{fx + 30:.1f}" cy="{camy - 10}" r="36" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(f'<path d="M{fx - 4:.1f} {camy - 18} l-12 10 l12 6" fill="{SKIN}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
    s.append(f'<path d="M{fx + 10:.1f} {camy + 40} Q{fx - 40:.1f} {camy + 50} {hx + 20:.1f} {camy + 20}" fill="none" stroke="{INK}" stroke-width="22" stroke-linecap="round"/>'
             f'<path d="M{fx + 10:.1f} {camy + 40} Q{fx - 40:.1f} {camy + 50} {hx + 20:.1f} {camy + 20}" fill="none" stroke="{SKIN}" stroke-width="16" stroke-linecap="round"/>')
    s.append(f'<ellipse cx="{hx:.1f}" cy="{camy + 16}" rx="20" ry="28" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(f'<rect x="{fx + 4:.1f}" y="{camy + 26}" width="60" height="150" rx="18" fill="{VIO2}" stroke="{INK}" stroke-width="2.5"/>')
    for (tx, ty, col) in ((hx, camy - 12, PINK), (hx, camy + 44, PINK), (fx + 30, camy - 46, VIO7), (fx + 30, camy + 26, VIO7)):
        s.append(line(camx + 18, camy, tx, ty, col, 2, '6 4'))
    s.append(line(camx, 330, hx, 330, PINK, 3) + text((camx + hx) / 2, 352, '0.4 米', 14, 800, PINK, 'middle'))
    s.append(line(camx, 372, fx, 372, VIO7, 3) + text((camx + fx) / 2, 394, '0.8 米', 14, 800, VIO7, 'middle'))
    s.append(label(300, 92, '手的放大倍数是脸的 2 倍', RED1, 14))
    # 拍出来
    s.append(f'<rect x="600" y="60" width="260" height="290" rx="6" fill="{BG}" stroke="{INK}" stroke-width="2"/>')
    s.append(face_front(700, 150, 40))
    s.append(f'<rect x="666" y="196" width="68" height="150" rx="20" fill="{VIO2}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(f'<ellipse cx="790" cy="230" rx="44" ry="60" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(text(730, 378, '手和脸差不多大，甚至更大', 14, 700, INK, 'middle'))
    s.append(text(730, 402, '退到 2.4 米：差距只剩 1.2 倍', 13, 700, MINT7, 'middle'))
    save('p-distort-persp', svg(Wd, Hd, ''.join(s), '透视畸变：离镜头近的部位被放大，倍数只看距离之比'))


def p_distort_edge():
    Wd, Hd = 940, 450
    s = [card(20, 10, 470, 430, '俯视图：同样大的头，放在画面不同位置', YEL1), card(510, 10, 410, 430, '拍出来（超广角）', VIO1)]
    camx, camy = 255, 410; f = 100; D = 262; r = 30
    py = camy - f
    s.append(line(40, py, 470, py, INK, 3) + text(468, py + 22, '成像平面（照片）', 13, 700, MUTED, 'end'))
    s.append(camera_icon(camx, camy + 4, 0.9))
    res = []
    for th in (-46, -25, 0, 25, 46):
        t = math.radians(th)
        hx, hy = camx + D * math.sin(t), camy - D * math.cos(t)
        dlt = math.asin(r / D)
        xs = [camx + f * math.tan(t + sg * dlt) for sg in (-1, 1)]
        col = RED if abs(th) == 46 else (YEL if abs(th) == 25 else MINT7)
        for sg, xx in zip((-1, 1), xs):
            ang = t + sg * dlt
            s.append(line(camx, camy - 8, camx + (D + 10) * math.sin(ang), camy - (D + 10) * math.cos(ang), col, 1.3, '4 4'))
        s.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{r}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(line(xs[0], py, xs[1], py, col, 7, cap='butt'))
        res.append((th, (xs[0] + xs[1]) / 2, xs[1] - xs[0]))
    s.append(text(40, 425, '五个头离相机一样远', 13, 700, MUTED))
    s.append(label(40, py + 48, '粗色线：在照片上占多宽', WHITE, 13))
    # 拍出来
    x0, y0, w, h = 526, 60, 378, 300
    s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="6" fill="{BG}" stroke="{INK}" stroke-width="2"/>')
    s.append(line(x0 + 8, y0 + 40, x0 + 8, y0 + h - 10, VIO7, 5) + line(x0 + w - 8, y0 + 40, x0 + w - 8, y0 + h - 10, VIO7, 5))
    sc = (w - 30) / (res[-1][1] + res[-1][2] / 2 - (res[0][1] - res[0][2] / 2))
    mid = x0 + w / 2
    for th, cxp, wp in res:
        X = mid + (cxp - camx) * sc
        rx = wp * sc / 2; ry = 30 * sc * 2 * f / D / 2 / math.cos(math.radians(th)) ** 0.5
        ry = max(ry, 22)
        s.append(f'<rect x="{X - rx * 0.8:.1f}" y="{y0 + 170}" width="{rx * 1.6:.1f}" height="110" rx="{rx * 0.5:.1f}" fill="{VIO2}" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<ellipse cx="{X:.1f}" cy="{y0 + 130}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(f'<circle cx="{X - rx * 0.35:.1f}" cy="{y0 + 128}" r="3" fill="{INK}"/><circle cx="{X + rx * 0.35:.1f}" cy="{y0 + 128}" r="3" fill="{INK}"/>')
    s.append(text(x0 + w / 2, 390, '两边的人被横向拉宽，柱子还是直的', 14, 700, INK, 'middle'))
    s.append(text(x0 + w / 2, 414, '人站在画面中间就不会被拉', 13, 700, MINT7, 'middle'))
    save('p-distort-edge', svg(Wd, Hd, ''.join(s), '广角边缘拉伸：画面边上的立体物体被往外拉宽'))


# ---------- 3.6 界面 ----------
def corridor(x, y, w, h, vp, uid, people=True):
    """一点透视走廊照片，返回 svg"""
    x1, y1 = x + w, y + h
    k = 0.22
    corners = [(x, y), (x1, y), (x1, y1), (x, y1)]
    back = [(vp[0] + (cx_ - vp[0]) * k, vp[1] + (cy_ - vp[1]) * k) for cx_, cy_ in corners]
    s = [f'<defs><clipPath id="{uid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#{uid})">']
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{BG}"/>')
    s.append(poly([corners[3], corners[2], back[2], back[3]], FLOOR, INK, 2))
    s.append(poly([corners[0], corners[1], back[1], back[0]], '#F1F5F9', INK, 2))
    s.append(poly([corners[0], corners[3], back[3], back[0]], YEL1, INK, 2))
    s.append(poly([corners[1], corners[2], back[2], back[1]], YEL1, INK, 2))
    s.append(poly(back, WHITE, INK, 2))
    # 地砖
    for i in range(-4, 5):
        fx = vp[0] + i * w * 0.18
        s.append(line(fx, y1, vp[0] + (fx - vp[0]) * k, vp[1] + (y1 - vp[1]) * k, '#94A3B8', 1.2))
    # 侧墙上的门
    for kk, kk2 in ((0.75, 0.6), (0.48, 0.4)):
        for side_x in (x, x1):
            a = vp[0] + (side_x - vp[0]) * kk; b = vp[0] + (side_x - vp[0]) * kk2
            top_a = vp[1] + (y + h * 0.28 - vp[1]) * kk; top_b = vp[1] + (y + h * 0.28 - vp[1]) * kk2
            bot_a = vp[1] + (y1 - vp[1]) * kk; bot_b = vp[1] + (y1 - vp[1]) * kk2
            s.append(poly([(a, top_a), (b, top_b), (b, bot_b), (a, bot_a)], VIO1, INK, 1.8))
    # 顶灯
    for kk in (0.8, 0.55, 0.38):
        cx_ = vp[0]; cy_ = vp[1] + (y - vp[1]) * kk
        s.append(f'<rect x="{cx_ - 30 * kk:.1f}" y="{cy_ - 3:.1f}" width="{60 * kk:.1f}" height="6" rx="3" fill="{YEL}"/>')
    s.append('</g>')
    return ''.join(s)


def u_persp_lines():
    vp = (CX + CW * 0.55, CY + CH * 0.42)
    ph = corridor(CX, CY, CW, CH, vp, 'upl')
    k = 0.22
    g = ''
    for c_ in [(CX, CY + CH), (CX + CW, CY + CH), (CX, CY), (CX + CW, CY)]:
        a = (vp[0] + (c_[0] - vp[0]) * 0.95, vp[1] + (c_[1] - vp[1]) * 0.95)
        g += line(a[0], a[1], vp[0], vp[1], MINT, 4)
    s = screen(ph + g, active='brush')
    s += ring(*icon_pos('brush'), 18) + badge(icon_pos('brush')[0] - 26, 62, 1)
    s += ring(vp[0], vp[1], 14) + badge(vp[0] + 26, vp[1] - 18, 2)
    s += label(560, 180, '① 新建一层「透视线」', YEL1, 14)
    s += label(560, 212, '　 技术笔，选亮绿色', YEL1, 14)
    s += label(560, 250, '② 沿墙角、地脚线描直线，', YEL1, 14)
    s += label(560, 282, '　 笔停住变直线，往里延长', YEL1, 14)
    s += label(560, 330, '几条线交在一点 = 消失点', MINT1, 14)
    s += note('示意图')
    save('u-persp-lines', svg(W, H, s, '新建图层，沿照片里的直线画线，找到它们的交点'))


def guide_editor(content, mode='透视', hl=None, sliders=(('不透明度', 0.7), ('粗细度', 0.3))):
    """绘图指引编辑界面（示意）"""
    s = [f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#4B5058"/>', content]
    s.append(f'<rect x="{SX}" y="{SY}" width="{SW}" height="44" rx="16" fill="{UIBAR}"/><rect x="{SX}" y="{SY + 28}" width="{SW}" height="16" fill="{UIBAR}"/>')
    s.append(text(40, 42, '取消', 15, 700, UITEXT) + text(760, 42, '完成', 15, 800, UIBLUE, 'end'))
    hue = ''.join(f'<rect x="{220 + i * 9}" y="28" width="9" height="12" fill="hsl({i * 9},80%,55%)"/>' for i in range(40))
    s.append(hue + f'<rect x="220" y="28" width="360" height="12" rx="3" fill="none" stroke="{UITEXT}" stroke-width="1"/>')
    # 滑块行
    y = SY + SH - 130
    s.append(f'<rect x="150" y="{y}" width="500" height="44" rx="12" fill="{UIBAR}"/>')
    bx = 166
    for n, v in sliders:
        s.append(slider(bx, y + 28, 120, n, v, hl == n)); bx += 150
    s.append(text(bx + 6, y + 30, '辅助绘图', 13, 700, UITEXT) + f'<rect x="{bx + 72}" y="{y + 14}" width="40" height="20" rx="10" fill="#6B7280"/><circle cx="{bx + 82}" cy="{y + 24}" r="8" fill="{WHITE}"/>')
    POS['辅助绘图'] = (bx, y, 120, 44)
    s.append(bottom_bar([['2D 网格', '等距', '透视', '对称']], active=(mode,), hl=hl if hl in ('2D 网格', '等距', '透视', '对称') else None))
    return ''.join(s)


def u_persp_guide():
    vp = (CX + CW * 0.55, CY + CH * 0.42)
    ph = corridor(CX, CY, CW, CH, vp, 'upg')
    ph += f'<rect x="{CX}" y="{CY}" width="{CW}" height="{CH}" fill="none" stroke="#94A3B8"/>'
    g = f'<defs><clipPath id="upgc"><rect x="{CX}" y="{CY}" width="{CW}" height="{CH}"/></clipPath></defs><g clip-path="url(#upgc)">'
    for a in range(0, 360, 15):
        r_ = math.radians(a)
        g += line(vp[0], vp[1], vp[0] + 400 * math.cos(r_), vp[1] + 400 * math.sin(r_), UIBLUE, 1.3, op='.8')
    g += line(CX, vp[1], CX + CW, vp[1], UIBLUE, 2.5)
    g += '</g>'
    g += f'<circle cx="{vp[0]:.1f}" cy="{vp[1]:.1f}" r="9" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2.5"/>'
    s = guide_editor(ph + g, '透视', hl='透视')
    px, py, pw, phh = POS['透视']
    s += badge(px + pw / 2, py - 14, 1)
    s += ring(vp[0], vp[1], 18) + badge(vp[0] + 30, vp[1] - 22, 2)
    s += badge(702, 42, 3) + ringrect(720, 22, 56, 32)
    s += label(560, 170, '① 底部选「透视」', YEL1, 14)
    s += label(560, 202, '② 在交点上轻点一下，', YEL1, 14)
    s += label(560, 234, '　 加一个消失点，拖准它', YEL1, 14)
    s += label(560, 266, '　（再点一下加第二个点）', WHITE, 14)
    s += label(560, 304, '③ 点「完成」', YEL1, 14)
    s += label(36, 170, '横贯的那条线', VIO1, 14) + label(36, 200, '就是视平线', VIO1, 14)
    s += note('示意图，按钮位置以实际界面为准')
    save('u-persp-guide', svg(W, H, s, '编辑绘图指引：选透视，在交点上轻点添加消失点'))


# ---------- 3.6 案例 ----------
def photo_frame(x, y, w, h, uid, body):
    return (f'<defs><clipPath id="{uid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs>'
            f'<g clip-path="url(#{uid})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{BG}"/>{body}</g>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="none" stroke="{INK}" stroke-width="2"/>')


def group_photo(x, y, w, h, stretch=True, uid='gp'):
    b = ''
    q = min(h / 220, w / 270) * 0.85
    b += line(x + 14 * q, y + 10, x + 14 * q, y + h, VIO7, 5 * q) + line(x + w - 14 * q, y + 10, x + w - 14 * q, y + h, VIO7, 5 * q)
    b += f'<rect x="{x}" y="{y + h * 0.8:.1f}" width="{w}" height="{h * 0.2:.1f}" fill="{FLOOR}"/>'
    n = 5
    for i in range(n):
        u = (i - (n - 1) / 2) / ((n - 1) / 2)  # -1..1
        X = x + w / 2 + u * w * 0.38
        k = 1 + (0.55 * u * u if stretch else 0)
        rx = 19 * k * q; ry = 23 * q
        b += f'<rect x="{X - 22 * k * q:.1f}" y="{y + h * 0.5:.1f}" width="{44 * k * q:.1f}" height="{h * 0.45:.1f}" rx="{14 * k * q:.1f}" fill="{[VIO2, PINK1, MINT1, YEL1, VIO1][i]}" stroke="{INK}" stroke-width="2"/>'
        b += f'<ellipse cx="{X:.1f}" cy="{y + h * 0.38:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>'
        b += f'<path d="M{X - rx:.1f} {y + h * 0.36:.1f} Q{X:.1f} {y + h * 0.38 - ry * 1.6:.1f} {X + rx:.1f} {y + h * 0.36:.1f} Z" fill="{PINK}" stroke="{INK}" stroke-width="2"/>'
        b += f'<circle cx="{X - rx * 0.35:.1f}" cy="{y + h * 0.39:.1f}" r="{2.5 * q:.1f}" fill="{INK}"/><circle cx="{X + rx * 0.35:.1f}" cy="{y + h * 0.39:.1f}" r="{2.5 * q:.1f}" fill="{INK}"/>'
    return photo_frame(x, y, w, h, uid, b)


def bent_hall(x, y, w, h, k, uid):
    m = 0.16 if k < 0 else 0.03
    b = grid_scene(x - w * m, y - h * m, w * (1 + 2 * m), h * (1 + 2 * m), k)
    fig, _ = mannequin(x + w / 2, y + h * 0.3, h * 0.085, uid=uid + 'f', sw=1.8)
    return photo_frame(x, y, w, h, uid, b + fig)


def case_three():
    Wd, Hd = 960, 420
    s = []
    for i, n in enumerate('ABC'):
        ox = 20 + i * 315
        s.append(card(ox, 10, 300, 400, f'照片 {n}', [YEL1, VIO1, MINT1][i]))
    # A：广角近拍的脸
    body = line(40 + 10, 60, 40 + 10, 360, VIO7, 5) + line(40 + 250, 60, 40 + 250, 360, VIO7, 5) + face_front(170, 210, 95, nose=1.7, ear=0.5, width=0.86)
    s.append(photo_frame(40, 60, 260, 300, 'cta', body))
    s.append(group_photo(355, 100, 270, 220, True, 'ctb'))
    s.append(bent_hall(670, 60, 270, 300, -0.2, 'ctc'))
    s.append(text(170, 392, '鼻子大、耳朵几乎看不见', 13, 600, MUTED, 'middle'))
    s.append(text(490, 392, '两边的人特别胖', 13, 600, MUTED, 'middle'))
    s.append(text(805, 392, '柱子和地砖线都弯了', 13, 600, MUTED, 'middle'))
    save('case-three', svg(Wd, Hd, ''.join(s), '判断练习：三张照片分别是哪种变形'))


def case_lens_before():
    s = bent_hall(20, 20, 600, 460, -0.2, 'clb') + label(36, 54, '修之前：柱子往外鼓', YEL1, 16)
    save('case-lens-before', svg(640, 500, s, '修之前：桶形畸变，柱子往外鼓'))


def case_lens_after():
    s = bent_hall(20, 20, 600, 460, 0.0, 'cla') + label(604, 54, '修之后：镜头校正后柱子直了', VIO1, 16, 'end')
    save('case-lens-after', svg(640, 500, s, '修之后：镜头校正后柱子变直'))


def case_edge_before():
    s = group_photo(20, 20, 600, 460, True, 'ceb') + label(36, 54, '修之前：两边的人被拉宽', YEL1, 16)
    save('case-edge-before', svg(640, 500, s, '修之前：合影两边的人被拉宽'))


def case_edge_after():
    body_s = group_photo(20, 20, 600, 460, False, 'cea') + label(604, 54, '修之后：边上的人横向收窄', VIO1, 16, 'end')
    save('case-edge-after', svg(640, 500, body_s, '修之后：边上的人横向收窄'))


def case_horizon():
    Wd, Hd = 640, 520
    x, y, w, h = 20, 20, 600, 480
    hz = y + 40
    vp = (x + w * 0.5, hz)
    b = f'<rect x="{x}" y="{hz}" width="{w}" height="{h}" fill="{FLOOR}"/>'
    for i in range(-10, 11):
        b += line(vp[0] + i * 90, y + h, vp[0], vp[1], '#94A3B8', 1.3)
    for kk in (0.2, 0.35, 0.55, 0.8):
        yy = hz + (y + h - hz) * kk
        b += line(x, yy, x + w, yy, '#94A3B8', 1.3)
    # 竖线往下收（俯拍）
    for px in (x + 60, x + w - 60):
        b += line(px, y, px + (vp[0] - px) * 0.18, y + h, VIO7, 6)
    fig, _ = mannequin(x + w * 0.52, y + 140, 44, uid='chf', sw=2, flat=())
    b += fig
    s = photo_frame(x, y, w, h, 'chz', b)
    # 指引线
    for a in range(10, 171, 16):
        r_ = math.radians(a)
        s += line(vp[0], vp[1], vp[0] + 700 * math.cos(r_), vp[1] + 700 * math.sin(r_), UIBLUE, 1.2, op='.6')
    s += line(x, hz, x + w, hz, UIBLUE, 3) + dot(*vp, 7, UIBLUE)
    s += label(x + 16, hz + 34, '透视指引：视平线在头顶上方', YEL1, 15)
    s += label(x + 16, y + h - 20, '→ 相机比头高，是俯拍 → 头大腿短，按 5.4 课修', RED1, 15)
    save('case-horizon', svg(Wd, Hd, s, '用透视指引找到视平线，判断这张是俯拍'))


# ================= 3.7 构图 =================
S_W, S_H = 1600, 900
HERO = dict(cx=760, top=150, hh=66)


def venue():
    """横幅漫展场景（原始照片），坐标 1600 × 900"""
    s = [f'<rect width="{S_W}" height="{S_H}" fill="{BG}"/>']
    fy = 640
    s.append(f'<rect x="0" y="{fy}" width="{S_W}" height="{S_H - fy}" fill="{FLOOR}"/>' + line(0, fy, S_W, fy, INK, 2.5))
    vp = (HERO['cx'] + 40, 330)
    for i in range(-12, 13):
        s.append(line(vp[0] + i * 140, S_H, vp[0] + (i * 140) * 0.0 + (vp[0] + i * 140 - vp[0]) * 0.0, fy, '#94A3B8', 1.5) if False else '')
    for i in range(-14, 15):
        x_bot = vp[0] + i * 160
        t = (fy - S_H) / (vp[1] - S_H)
        s.append(line(x_bot, S_H, x_bot + (vp[0] - x_bot) * t, fy, '#94A3B8', 1.5))
    # 柱子、横幅
    for px in (150, 1420):
        s.append(f'<rect x="{px}" y="0" width="70" height="{fy}" fill="{VIO1}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<rect x="1080" y="90" width="260" height="120" rx="8" fill="{PINK1}" stroke="{INK}" stroke-width="3"/>' + ''.join(line(1110, 125 + i * 28, 1310 - i * 40, 125 + i * 28, PINK, 8) for i in range(3)))
    # 楼梯扶手（斜线，指向人物）
    s.append(line(1600, 820, 1000, 470, INK, 6) + line(1600, 870, 1010, 520, INK, 3))
    for i in range(6):
        x = 1580 - i * 110; y = 820 - i * 64
        s.append(line(x, y, x, y + 160 - i * 10, INK, 3))
    # 路人（被切在画面右边）
    s.append(person(1585, 650, 300, MINT1))
    # 桌子
    s.append(f'<rect x="230" y="520" width="300" height="20" fill="{YEL1}" stroke="{INK}" stroke-width="3"/>' + line(250, 540, 250, 650, INK, 4) + line(510, 540, 510, 650, INK, 4))
    s.append(f'<rect x="270" y="480" width="70" height="40" fill="{VIO2}" stroke="{INK}" stroke-width="2.5"/><rect x="370" y="470" width="50" height="50" fill="{MINT1}" stroke="{INK}" stroke-width="2.5"/>')
    # 主角 + 法杖
    cx, top, hh = HERO['cx'], HERO['top'], HERO['hh']
    fig, b = mannequin(cx, top, hh, uid='ven', look=1.0)
    hx, hy = cx + 1.1 * hh, top + 4.05 * hh
    staff = line(hx - 0.4 * hh, hy + 1.4 * hh, hx + 1.4 * hh, top - 0.4 * hh, INK, 11) + line(hx - 0.4 * hh, hy + 1.4 * hh, hx + 1.4 * hh, top - 0.4 * hh, YEL, 6)
    gem = f'<circle cx="{hx + 1.4 * hh:.1f}" cy="{top - 0.4 * hh:.1f}" r="20" fill="{PINK}" stroke="{INK}" stroke-width="3"/>'
    s.append(fig + staff + gem + f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{0.15 * hh:.1f}" ry="{0.27 * hh:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
    return ''.join(s), b


CROPS = {  # x, y, w, h
    'A': (570, 60, 570, 760),
    'B': (630, 55, 324, 405),
    'C': (340, 100, 1200, 675),
    'bad': (676, 136, 288, 360),
}


def crop_svg(name, key, out_w, title, overlay='', thirds=False):
    body, _ = venue()
    x, y, w, h = CROPS[key]
    sc = out_w / w
    out_h = h * sc
    s = f'<g transform="scale({sc:.4f}) translate({-x},{-y})">{body}</g>'
    if thirds:
        for i in (1, 2):
            s += line(out_w * i / 3, 0, out_w * i / 3, out_h, YEL, 2.5, '8 6') + line(0, out_h * i / 3, out_w, out_h * i / 3, YEL, 2.5, '8 6')
    s += overlay
    save(name, svg(int(out_w), int(out_h), s, title))


def case_crop_orig():
    body, _ = venue()
    sc = 0.5
    s = f'<g transform="scale({sc})">{body}</g>'
    for k, col, lab in (('C', VIO7, 'C 横幅 16:9'), ('A', MINT7, 'A 竖幅 3:4'), ('B', RED, 'B 半身 4:5')):
        x, y, w, h = [v * sc for v in CROPS[k]]
        s += f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{col}" stroke-width="4" stroke-dasharray="10 6"/>'
        ly = y + h - 12 if k == 'A' else y + 26
        s += label(x + 8, ly, lab, WHITE, 14, stroke=col)
    save('case-crop-orig', svg(800, 450, s, '原图：横幅全身照，三个裁切框'))


def case_crop_a():
    crop_svg('case-crop-a', 'A', 480, '裁法 A：竖幅 3:4 全身，人在左三分线，视线前方留白', thirds=True)


def case_crop_b():
    crop_svg('case-crop-b', 'B', 480, '裁法 B：半身 4:5，眼睛在上三分线，切在大腿中段', thirds=True)


def case_crop_c():
    crop_svg('case-crop-c', 'C', 800, '裁法 C：横幅 16:9，扶手引导线指向人物', thirds=True)


def case_crop_bad():
    x, y, w, h = CROPS['bad']
    sc = 480 / w
    ov = label(14, 34, '切在膝盖、手腕，头顶顶边', RED1, 16)
    crop_svg('case-crop-bad', 'bad', 480, '不好的裁法：切在膝盖和手腕上，头顶顶着边', overlay=ov)


def case_crop_good():
    ov = label(14, 34, '切在大腿中段，头顶留出空间', MINT1, 16)
    crop_svg('case-crop-good', 'B', 480, '好的裁法：切在大腿中段，头顶留空间', overlay=ov)


def p_thirds():
    Wd, Hd = 900, 450
    s = []
    # 左：半身
    s.append(card(20, 10, 420, 430, '半身：眼睛放在上三分线', YEL1))
    body, _ = venue()
    def mini(key, x, y, w, uid):
        cx_, cy_, cw, ch = CROPS[key]
        sc = w / cw
        h = ch * sc
        g = f'<svg x="{x}" y="{y}" width="{w}" height="{h:.1f}" viewBox="{cx_} {cy_} {cw} {ch}">{body}</svg>'
        for i in (1, 2):
            g += line(x + w * i / 3, y, x + w * i / 3, y + h, YEL, 3, '8 6') + line(x, y + h * i / 3, x + w, y + h * i / 3, YEL, 3, '8 6')
        g += f'<rect x="{x}" y="{y}" width="{w}" height="{h:.1f}" fill="none" stroke="{INK}" stroke-width="2"/>'
        return g, h
    g, h = mini('B', 110, 60, 240, 'tb')
    s.append(g)
    # 眼睛位置
    ex = 110 + (HERO['cx'] - CROPS['B'][0]) * 240 / CROPS['B'][2]
    ey = 60 + (HERO['top'] + 0.6 * HERO['hh'] - CROPS['B'][1]) * 240 / CROPS['B'][2]
    s.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="16" fill="none" stroke="{RED}" stroke-width="3"/>')
    s.append(text(230, 60 + h + 30, '眼睛贴着上面那条线', 14, 700, INK, 'middle'))
    s.append(text(230, 60 + h + 54, '离交点越近越稳', 13, 600, MUTED, 'middle'))
    s.append(card(460, 10, 420, 430, '全身：人放在一条竖线上', VIO1))
    g, h2 = mini('A', 560, 60, 240, 'ta')
    s.append(g)
    s.append(arrow(560 + 95, 60 + 52, 560 + 180, 60 + 52, VIO7, 3, marker='arwv'))
    s.append(label(560 + 190, 60 + 58, '视线方向', VIO1, 12))
    s.append(text(680, 60 + h2 + 30, '视线朝右，右边就多留空', 14, 700, INK, 'middle'))
    save('p-thirds', svg(Wd, Hd, ''.join(s), '三分法：把画面横竖各分三份，主体放在线上或交点附近'))


def p_lead():
    Wd, Hd = 900, 440
    s = [card(20, 10, 420, 420, '环境里的线：地砖、扶手、走廊', YEL1), card(460, 10, 420, 420, '身上和道具的线：武器、手臂', VIO1)]
    vp = (230, 200)
    s.append(corridor(40, 56, 380, 300, vp, 'pl1'))
    fig, _ = mannequin(vp[0], vp[1] - 52, 14, uid='plf', sw=1.2)
    s.append(fig)
    for c_ in ((40, 356), (420, 356), (40, 56), (420, 56)):
        s.append(arrow(c_[0] + (vp[0] - c_[0]) * 0.1, c_[1] + (vp[1] - c_[1]) * 0.1, c_[0] + (vp[0] - c_[0]) * 0.7, c_[1] + (vp[1] - c_[1]) * 0.7, RED, 3, marker='arwr'))
    s.append(f'<rect x="40" y="56" width="380" height="300" fill="none" stroke="{INK}" stroke-width="2"/>')
    s.append(text(230, 396, '所有线都汇到人身上，眼睛跟着走过去', 14, 700, INK, 'middle'))
    # 右：法杖
    body, _ = venue()
    s.append(f'<svg x="480" y="56" width="380" height="300" viewBox="560 40 480 379">{body}</svg><rect x="480" y="56" width="380" height="300" fill="none" stroke="{INK}" stroke-width="2"/>')
    s.append(arrow(780, 330, 700, 120, RED, 3, marker='arwr'))
    s.append(text(670, 396, '法杖从画面下方斜着指向脸', 14, 700, INK, 'middle'))
    save('p-lead', svg(Wd, Hd, ''.join(s), '引导线：画面里的线把视线带到主体上'))


def p_space():
    Wd, Hd = 900, 420
    s = []
    body, _ = venue()
    for i, (title, vx, fill, ok, sub) in enumerate([('视线前面留空', 612, MINT1, True, '朝右看，右边留空：画面往前延伸'),
                                                  ('视线撞到边', 350, RED1, False, '朝右看却贴着右边：像被挡住')]):
        ox = 20 + i * 440
        s.append(card(ox, 10, 420, 400, title, fill))
        # 视线方向箭头 + 取景
        vw, vh = 380, 285
        src_w = 380 * 1.3; src_h = 285 * 1.3
        s.append(f'<svg x="{ox + 20}" y="56" width="{vw}" height="{vh}" viewBox="{vx} 100 {src_w:.0f} {src_h:.0f}">{body}</svg>'
                 f'<rect x="{ox + 20}" y="56" width="{vw}" height="{vh}" fill="none" stroke="{INK}" stroke-width="2"/>')
        fx = ox + 20 + (HERO['cx'] - vx) / 1.3
        fy = 56 + (HERO['top'] + 0.6 * HERO['hh'] - 100) / 1.3
        s.append(arrow(fx + 30, fy, min(fx + 130, ox + 20 + vw - 10), fy, VIO7, 3, '6 5', marker='arwv'))
        s.append(check(ox + 390, 34, 9) if ok else xmark(ox + 390, 30, 9))
        s.append(text(ox + 210, 380, sub, 14, 700, INK, 'middle'))
    save('p-space', svg(Wd, Hd, ''.join(s), '留白：在人物看的方向、走的方向多留空间'))


def p_joints():
    Wd, Hd = 760, 640
    hh = 76; cx = 380; top = 40
    fig, b = mannequin(cx, top, hh, uid='pj')
    s = [fig]
    bad = [(1.08, '脖子 / 下巴'), (2.85, '手肘、腰'), (3.8, '手腕'), (5.25, '膝盖'), (6.85, '脚踝')]
    good = [(2.2, '胸口下方'), (4.55, '大腿中段'), (6.05, '小腿中段')]
    for y, t in bad:
        yy = top + y * hh
        s.append(line(cx - 170, yy, cx + 170, yy, RED, 3, '9 6'))
        s.append(label(cx + 180, yy + 6, '别切：' + t, RED1, 14))
    for y, t in good:
        yy = top + y * hh
        s.append(line(cx - 170, yy, cx + 170, yy, MINT7, 3.5))
        s.append(label(cx - 180, yy + 6, '可以切：' + t, MINT1, 14, 'end'))
    s.append(text(Wd / 2, Hd - 14, '能弯的地方别切，切在两个关节中间', 14, 700, INK, 'middle'))
    save('p-joints', svg(Wd, Hd, ''.join(s), '裁切位置：红线是关节，别切；绿线在关节之间，可以切'))


def p_orient():
    Wd, Hd = 900, 520
    s = [card(20, 10, 330, 500, '竖构图', YEL1), card(370, 10, 510, 500, '横构图', VIO1)]
    body, _ = venue()
    x, y, w, h = CROPS['A']
    s.append(f'<svg x="50" y="60" width="270" height="{270 * h / w:.0f}" viewBox="{x} {y} {w} {h}">{body}</svg><rect x="50" y="60" width="270" height="{270 * h / w:.0f}" fill="none" stroke="{INK}" stroke-width="2"/>')
    s.append(text(185, 450, '强调人：身高、全身造型', 14, 700, INK, 'middle'))
    s.append(text(185, 476, '手机上刷图时占满屏幕', 13, 600, MUTED, 'middle'))
    x, y, w, h = CROPS['C']
    s.append(f'<svg x="390" y="60" width="470" height="{470 * h / w:.0f}" viewBox="{x} {y} {w} {h}">{body}</svg><rect x="390" y="60" width="470" height="{470 * h / w:.0f}" fill="none" stroke="{INK}" stroke-width="2"/>')
    s.append(text(625, 450, '强调人和环境：场景、氛围、动作方向', 14, 700, INK, 'middle'))
    s.append(text(625, 476, '适合做视频封面、电脑壁纸', 13, 600, MUTED, 'middle'))
    save('p-orient', svg(Wd, Hd, ''.join(s), '横构图和竖构图'))


# ---------- 3.7 界面 ----------
def gal_frame(inner):
    return f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#1F2329"/>' + inner


def u_gallery_dup():
    body, _ = venue()
    s = text(SX + 26, 52, 'Procreate', 22, 800, UITEXT)
    for k, x in {'选择': 520, '导入': 588, '照片': 656}.items():
        s += text(x, 52, k, 18, 700, UITEXT, 'middle')
    s += text(730, 56, '+', 30, 700, UITEXT, 'middle')
    # 缩略图（被左滑的那个）
    tx, ty, tw, th = 60, 110, 320, 180
    s += f'<svg x="{tx - 120}" y="{ty}" width="{tw}" height="{th}" viewBox="0 0 1600 900">{body}</svg>'
    bx = tx - 120 + tw
    for j, (b_, col) in enumerate([('分享', '#4B5563'), ('复制', '#2563EB'), ('删除', '#DC2626')]):
        s += f'<rect x="{bx + j * 70}" y="{ty}" width="70" height="{th}" fill="{col}"/>' + text(bx + j * 70 + 35, ty + th / 2 + 6, b_, 16, 700, WHITE, 'middle')
    s += ringrect(bx + 72, ty + 4, 66, th - 8) + badge(bx + 105, ty - 16, 2)
    s += arrow(tx + 160, ty + th + 34, tx + 40, ty + th + 34, RED, 3, marker='arwr') + badge(tx + 180, ty + th + 34, 1)
    s += text(40, ty + th + 70, '漫展_返图_07', 14, 600, UITEXT)
    s += f'<rect x="480" y="110" width="250" height="180" rx="6" fill="{BG}"/>' + text(480, 312, '漫展_返图_07（副本）', 14, 600, UITEXT)
    s += f'<svg x="480" y="110" width="250" height="180" viewBox="200 0 1200 900" preserveAspectRatio="xMidYMid slice">{body}</svg>'
    s += label(300, 430, '① 在作品缩略图上向左轻滑　② 点「复制」', YEL1, 15)
    s += label(300, 466, '每种裁法用一份副本，原图那份不动', WHITE, 15)
    s += note('示意图')
    save('u-gallery-dup', svg(W, H, gal_frame(s), '在图库里向左轻滑作品，点复制'))


def u_crop_ratio():
    body, _ = venue()
    # 画布显示区
    px, py, pw = 120, 110, 560
    ph = pw * 900 / 1600
    sc = pw / 1600
    cx_, cy_, cw, ch = CROPS['A']
    bx, by, bw, bh = px + cx_ * sc, py + cy_ * sc, cw * sc, ch * sc
    s = [f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#2B2F36"/>']
    s.append(f'<svg x="{px}" y="{py}" width="{pw}" height="{ph:.1f}" viewBox="0 0 1600 900">{body}</svg>')
    s.append(f'<path d="M{px} {py} h{pw} v{ph:.1f} h{-pw} Z M{bx:.1f} {by:.1f} v{bh:.1f} h{bw:.1f} v{-bh:.1f} Z" fill="#000" fill-opacity=".55" fill-rule="evenodd"/>')
    s.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="none" stroke="{WHITE}" stroke-width="3"/>')
    for i in (1, 2):
        s.append(line(bx + bw * i / 3, by, bx + bw * i / 3, by + bh, WHITE, 1, op='.6') + line(bx, by + bh * i / 3, bx + bw, by + bh * i / 3, WHITE, 1, op='.6'))
    s.append(arrow(bx + bw / 2 - 40, by + bh / 2 + 70, bx + bw / 2 + 30, by + bh / 2 + 70, WHITE, 3))
    # 顶部
    s.append(f'<rect x="{SX}" y="{SY}" width="{SW}" height="44" rx="16" fill="{UIBAR}"/><rect x="{SX}" y="{SY + 28}" width="{SW}" height="16" fill="{UIBAR}"/>')
    s.append(text(40, 42, '取消', 15, 700, UITEXT) + text(400, 42, '裁剪并调整大小', 15, 800, UITEXT, 'middle') + text(650, 42, '设置', 15, 700, UITEXT, 'end') + text(760, 42, '完成', 15, 800, UIBLUE, 'end'))
    s.append(ringrect(608, 22, 50, 32) + badge(590, 42, 1))
    # 设置面板
    sx_, sy_ = 440, 70
    s.append(panel(sx_, sy_, 300, 150))
    s.append(text(sx_ + 16, sy_ + 30, '宽度', 13, 700, UIDIM) + f'<rect x="{sx_ + 16}" y="{sy_ + 38}" width="100" height="32" rx="6" fill="{UIBAR}"/>' + text(sx_ + 66, sy_ + 60, '3000 px', 14, 700, UITEXT, 'middle'))
    s.append(text(sx_ + 176, sy_ + 30, '高度', 13, 700, UIDIM) + f'<rect x="{sx_ + 176}" y="{sy_ + 38}" width="100" height="32" rx="6" fill="{UIBAR}"/>' + text(sx_ + 226, sy_ + 60, '4000 px', 14, 700, UITEXT, 'middle'))
    s.append(f'<g transform="translate({sx_ + 146},{sy_ + 54})"><rect x="-12" y="-6" width="12" height="12" rx="5" fill="none" stroke="{UITEXT}" stroke-width="2"/><rect x="0" y="-6" width="12" height="12" rx="5" fill="none" stroke="{UITEXT}" stroke-width="2"/></g>')
    s.append(menu_rows(sx_, sy_ + 86, 300, ['画布重新取样'], toggles={'画布重新取样': False}))
    s.append(ringrect(sx_ + 10, sy_ + 34, 272, 40) + badge(sx_ - 14, sy_ + 54, 2))
    s.append(ringrect(sx_ + 6, sy_ + 89, 288, 30) + badge(sx_ - 14, sy_ + 104, 3))
    s.append(badge(bx + bw / 2 + 50, by + bh / 2 + 70, 4))
    s.append(ringrect(722, 22, 56, 32) + badge(704, 70, 5))
    s.append(label(60, 470, '① 点「设置」　② 解开链条，输入宽高（例：3000 × 4000，3:4）', YEL1, 14))
    s.append(label(60, 504, '③「画布重新取样」保持关闭　④ 在框里拖动定位置　⑤ 完成', YEL1, 14))
    s.append(note('示意图，设置面板的位置以实际界面为准'))
    save('u-crop-ratio', svg(W, H, ''.join(s), '裁剪并调整大小：输入宽高、拖动裁剪框'))


def u_thirds_grid():
    body, _ = venue()
    cx_, cy_, cw, ch = CROPS['A']
    x0, y0, w0 = 290, 70, 220
    h0 = w0 * ch / cw
    c = f'<svg x="{x0}" y="{y0}" width="{w0}" height="{h0:.1f}" viewBox="{cx_} {cy_} {cw} {ch}">{body}</svg>'
    c += f'<rect x="{x0}" y="{y0}" width="{w0}" height="{h0:.1f}" fill="none" stroke="#94A3B8"/>'
    cell = w0 / 3
    g = ''
    xx = x0
    while xx <= x0 + w0 + 1:
        g += line(xx, y0, xx, y0 + h0, UIBLUE, 2); xx += cell
    yy = y0
    while yy <= y0 + h0 + 1:
        g += line(x0, yy, x0 + w0, yy, UIBLUE, 2); yy += cell
    g += f'<circle cx="{x0}" cy="{y0}" r="8" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
    s = guide_editor(c + g, '2D 网格', sliders=(('不透明度', 0.7), ('粗细度', 0.3)))
    # 网格尺寸数值
    s += f'<rect x="560" y="300" width="200" height="70" rx="12" fill="{UIBAR}"/>' + text(576, 326, '网格尺寸', 13, 700, UITEXT)
    s += f'<rect x="652" y="310" width="96" height="24" rx="6" fill="{UIPANEL}"/>' + text(700, 327, '1000 px', 13, 700, UITEXT, 'middle')
    s += f'<rect x="576" y="350" width="168" height="8" rx="4" fill="#6B7280"/><rect x="576" y="350" width="60" height="8" rx="4" fill="{UIBLUE}"/><circle cx="636" cy="354" r="9" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
    s += ringrect(654, 305, 100, 34) + badge(770, 322, 2)
    px, py, pw, phh = POS['2D 网格']
    s += badge(px + pw / 2, py - 14, 1)
    s += badge(x0 - 18, y0 - 6, 3)
    s += label(560, 160, '① 选「2D 网格」', YEL1, 14)
    s += label(560, 192, '② 轻点数值，输入：宽 ÷ 3', YEL1, 14)
    s += label(560, 224, '③ 拖蓝点贴住左上角', YEL1, 14)
    s += label(36, 120, '竖线正好三等分', MINT1, 13) + label(36, 150, '横线要另算', RED1, 13)
    s += note('示意图，按钮位置以实际界面为准')
    save('u-thirds-grid', svg(W, H, s, '2D 网格：网格尺寸设成画布宽度的三分之一'))


def u_thirds_layer():
    body, _ = venue()
    cx_, cy_, cw, ch = CROPS['A']
    x0, y0, w0 = 290, 66, 230
    h0 = w0 * ch / cw
    c = f'<svg x="{x0}" y="{y0}" width="{w0}" height="{h0:.1f}" viewBox="{cx_} {cy_} {cw} {ch}">{body}</svg>'
    for i in (1, 2):
        c += line(x0 + w0 * i / 3, y0, x0 + w0 * i / 3, y0 + h0, YEL, 3) + line(x0, y0 + h0 * i / 3, x0 + w0, y0 + h0 * i / 3, YEL, 3)
    lay = layers_panel([('三分线', None, 'N', True), ('图层 1', 'scene', 'N', False)], x=556, y=84, w=220)
    s = screen(c + lay, active='layers')
    s += label(556, 290, '新建一层「三分线」，', YEL1, 14)
    s += label(556, 320, '照网格描 4 条直线', YEL1, 14)
    s += label(556, 360, '不用时点勾选框关掉；', WHITE, 14)
    s += label(556, 390, '导出前关掉或删掉', WHITE, 14)
    s += note('示意图')
    save('u-thirds-layer', svg(W, H, s, '把三分线画在单独的图层上，随时开关'))


if __name__ == '__main__':
    import inspect
    fns = [f for n, f in list(globals().items()) if n.startswith(('p_', 'u_', 'case_')) and inspect.isfunction(f)]
    for f in fns:
        f()
    print('done', len(os.listdir(OUT)))
