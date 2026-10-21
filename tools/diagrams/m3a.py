"""M3 视觉基础理论 3.1～3.4 的示意图。运行：python tools/diagrams/m3a.py"""
import colorsys, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'diagrams', 'm3a')
os.makedirs(OUT, exist_ok=True)


def save(name, s):
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)


def lbl(x, y, s, fill=YEL1, size=15, anchor='start', stroke=INK):
    """和 kit.label 一样，只是数字、字母的宽度估得宽一点，避免文字出框"""
    w = sum(1.0 if ord(c) > 255 else 0.68 for c in s) * size + 18
    x0 = x - (w / 2 if anchor == 'middle' else (w if anchor == 'end' else 0))
    return (f'<rect x="{x0:.1f}" y="{y - size - 5:.1f}" width="{w:.1f}" height="{size + 13}" rx="{(size + 13) / 2:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>' + text(x0 + 9, y + 1, s, size, 700))


# ---------------- 颜色工具 ----------------
def hsv(h, s, v):
    """h 0~360，s、v 0~100（和 Procreate「值」面板的 HSB 一样）"""
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360, s / 100, v / 100)
    return '#%02X%02X%02X' % (round(r * 255), round(g * 255), round(b * 255))


def rgb_of(hexc):
    hexc = hexc.lstrip('#')
    return tuple(int(hexc[i:i + 2], 16) for i in (0, 2, 4))


def to_hsb(hexc):
    r, g, b = rgb_of(hexc)
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return round(h * 360), round(s * 100), round(v * 100)


def mix(c1, c2, t):
    a, b = rgb_of(c1), rgb_of(c2)
    return '#%02X%02X%02X' % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gray(c):
    r, g, b = rgb_of(c)
    y = round(0.299 * r + 0.587 * g + 0.114 * b)
    return '#%02X%02X%02X' % (y, y, y)


def box(x, y, w, h, title=None, fill=WHITE, tfill=YEL1):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'
    if title:
        s += lbl(x + 16, y + 34, title, tfill, 15)
    return s


def swatch(x, y, c, w=56, h=40, cap=None, sub=None, size=12):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{c}" stroke="{INK}" stroke-width="2"/>'
    if cap:
        s += text(x + w / 2, y + h + 16, cap, size, 700, INK, 'middle')
    if sub:
        s += text(x + w / 2, y + h + 31, sub, size - 1, 400, MUTED, 'middle')
    return s


def hsb_cap(c):
    h, s_, v = to_hsb(c)
    return f'H{h} S{s_} B{v}'


GRAY_FILTER = '<defs><filter id="gs"><feColorMatrix type="saturate" values="0"/></filter></defs>'


def blur_def(i, sd):
    return f'<defs><filter id="bl{i}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{sd}"/></filter></defs>'


def lamp(x, y, size=14, soft=False):
    """光源图标：小灯泡（硬光）或大柔光箱（软光）"""
    if soft:
        return (f'<rect x="{x - size * 2.4:.1f}" y="{y - size * 1.6:.1f}" width="{size * 4.8:.1f}" height="{size * 3.2:.1f}" rx="8" fill="{YEL1}" stroke="{INK}" stroke-width="2.5"/>'
                f'<rect x="{x - size * 2:.1f}" y="{y - size * 1.2:.1f}" width="{size * 4:.1f}" height="{size * 2.4:.1f}" rx="5" fill="{WHITE}" stroke="{YEL}" stroke-width="2"/>')
    rays = ''.join(f'<line x1="{x + math.cos(a) * (size + 4):.1f}" y1="{y + math.sin(a) * (size + 4):.1f}" x2="{x + math.cos(a) * (size + 11):.1f}" y2="{y + math.sin(a) * (size + 11):.1f}" stroke="{YEL}" stroke-width="3" stroke-linecap="round"/>'
                   for a in [i * math.pi / 4 for i in range(8)])
    return rays + f'<circle cx="{x}" cy="{y}" r="{size}" fill="{YEL}" stroke="{INK}" stroke-width="2.5"/>'


# ---------------- 立体：球、立方体、圆柱 ----------------
def sphere(cx, cy, r, gid, lx=-0.42, ly=-0.42, hard=False, soft=False, base=None, reflect=True):
    """光从左上来。gid 必须唯一。base：固有色（默认中性灰，便于看调子）"""
    fx, fy = cx + lx * r, cy + ly * r
    if base is None:
        stops = [(0, '#FFFFFF'), (0.1, '#F3F3F3'), (0.38, '#CFCFCF'), (0.56, '#A5A5A5'), (0.66, '#505050'), (0.8, '#5C5C5C'), (0.95, '#7C7C7C' if reflect else '#505050'), (1, '#808080' if reflect else '#505050')]
        if hard:
            stops = [(0, '#FFFFFF'), (0.08, '#F6F6F6'), (0.4, '#D2D2D2'), (0.6, '#BDBDBD'), (0.625, '#3A3A3A'), (0.85, '#454545'), (1, '#666666')]
        if soft:
            stops = [(0, '#EEEEEE'), (0.3, '#D2D2D2'), (0.6, '#9E9E9E'), (0.85, '#7A7A7A'), (1, '#858585')]
    else:
        stops = base
    st = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return (f'<defs><radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{fx:.1f}" cy="{fy:.1f}" r="{r * 1.62:.1f}" fx="{fx:.1f}" fy="{fy:.1f}">{st}</radialGradient></defs>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})" stroke="{INK}" stroke-width="2.5"/>')


def cast_shadow(cx, gy, r, gid, dx=0.55, hard=False, soft=False, k=1.0):
    """地面投影：光在左上，影子往右后方拉长"""
    rx, ry = r * 1.25 * k, r * 0.32
    x = cx + r * dx
    if soft:
        return (blur_def(gid, r * 0.16) + f'<ellipse cx="{x:.1f}" cy="{gy:.1f}" rx="{rx * 1.1:.1f}" ry="{ry * 1.2:.1f}" fill="#555" fill-opacity=".45" filter="url(#bl{gid})"/>')
    if hard:
        return f'<ellipse cx="{x:.1f}" cy="{gy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#333" fill-opacity=".85"/>'
    return (f'<defs><radialGradient id="cs{gid}" cx="0.3" cy="0.5" r="0.75"><stop offset="0" stop-color="#2A2A2A"/><stop offset="0.7" stop-color="#555"/><stop offset="1" stop-color="#777" stop-opacity="0.2"/></radialGradient></defs>'
            f'<ellipse cx="{x:.1f}" cy="{gy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="url(#cs{gid})"/>')


def ground(x, y, w):
    return f'<rect x="{x}" y="{y}" width="{w}" height="40" fill="#EDEAE2"/><line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{INK}" stroke-width="2"/>'


def cube(cx, by, a):
    """简单的等轴立方体：顶面亮、左前面灰、右前面暗。by 为底部前角的 y"""
    dx, dy = a * 0.866, a * 0.5
    top0 = (cx, by - a)                      # 前上角
    pts_top = [(cx, by - a), (cx - dx, by - a - dy), (cx, by - a - 2 * dy), (cx + dx, by - a - dy)]
    pts_l = [(cx, by), (cx - dx, by - dy), (cx - dx, by - a - dy), (cx, by - a)]
    pts_r = [(cx, by), (cx + dx, by - dy), (cx + dx, by - a - dy), (cx, by - a)]
    P = lambda ps: ' '.join(f'{x:.1f},{y:.1f}' for x, y in ps)
    sh = [(cx, by), (cx + dx, by - dy), (cx + dx + a * 0.75, by - dy + a * 0.1), (cx + a * 0.75, by + a * 0.25)]
    return (f'<polygon points="{P(sh)}" fill="#3A3A3A" fill-opacity=".8"/>'
            f'<polygon points="{P(pts_top)}" fill="#F4F4F4" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<polygon points="{P(pts_l)}" fill="#B8B8B8" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<polygon points="{P(pts_r)}" fill="#5A5A5A" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'), dict(top=(cx, by - a - dy), left=(cx - dx / 2, by - a / 2 - dy / 2), right=(cx + dx / 2, by - a / 2 - dy / 2), shadow=(cx + a * 1.0, by - a * 0.05))


def cylinder(cx, top, w, h, gid):
    stops = [(0, '#C9C9C9'), (0.18, '#F2F2F2'), (0.26, '#FFFFFF'), (0.34, '#EEEEEE'), (0.55, '#BDBDBD'), (0.68, '#8E8E8E'), (0.76, '#454545'), (0.88, '#585858'), (1, '#777777')]
    st = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    x0 = cx - w / 2
    ry = w * 0.18
    return (f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">{st}</linearGradient></defs>'
            f'<path d="M{x0:.1f} {top:.1f} L{x0:.1f} {top + h:.1f} A{w / 2:.1f} {ry:.1f} 0 0 0 {x0 + w:.1f} {top + h:.1f} L{x0 + w:.1f} {top:.1f} Z" fill="url(#{gid})" stroke="{INK}" stroke-width="2.5"/>'
            f'<ellipse cx="{cx}" cy="{top:.1f}" rx="{w / 2:.1f}" ry="{ry:.1f}" fill="#F7F7F7" stroke="{INK}" stroke-width="2.5"/>')


def leader(x1, y1, x2, y2, color=INK):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="2"/><circle cx="{x1:.1f}" cy="{y1:.1f}" r="4" fill="{color}"/>'


# ---------------- 人脸（正面简笔） ----------------
def face_geom(cx, cy, w, h):
    top, chin = cy - h / 2, cy + h / 2
    return dict(cx=cx, cy=cy, w=w, h=h, top=top, chin=chin, eye=cy - h * 0.02, nose=cy + h * 0.2, mouth=cy + h * 0.33)


def face_path(g):
    cx, cy, w, h, top = g['cx'], g['cy'], g['w'], g['h'], g['top']
    return (f'M{cx:.1f} {top:.1f} C{cx + w * 0.56:.1f} {top:.1f} {cx + w * 0.54:.1f} {cy + h * 0.12:.1f} {cx + w * 0.34:.1f} {cy + h * 0.36:.1f} '
            f'Q{cx + w * 0.16:.1f} {cy + h * 0.52:.1f} {cx:.1f} {cy + h * 0.5:.1f} Q{cx - w * 0.16:.1f} {cy + h * 0.52:.1f} {cx - w * 0.34:.1f} {cy + h * 0.36:.1f} '
            f'C{cx - w * 0.54:.1f} {cy + h * 0.12:.1f} {cx - w * 0.56:.1f} {top:.1f} {cx:.1f} {top:.1f} Z')


def P(g, u, v):
    """脸部坐标：u 横向（-1 左 ~ 1 右，按半宽），v 纵向（-1 头顶 ~ 1 下巴）"""
    return g['cx'] + u * g['w'] / 2, g['cy'] + v * g['h'] / 2


def poly(g, pts):
    return 'M' + ' L'.join('%.1f %.1f' % P(g, u, v) for u, v in pts) + ' Z'


def smooth(g, pts, close=True):
    """经过各点的平滑曲线（Catmull-Rom 转贝塞尔）"""
    q = [P(g, u, v) for u, v in pts]
    n = len(q)
    d = 'M%.1f %.1f' % q[0]
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0, p1, p2, p3 = q[(i - 1) % n] if close or i > 0 else q[0], q[i], q[(i + 1) % n], q[(i + 2) % n] if close or i + 2 < n else q[-1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += ' C%.1f %.1f %.1f %.1f %.1f %.1f' % (c1 + c2 + p2)
    return d + (' Z' if close else '')


SHADES = {
    # 侧光（光从画面左上方来）：明暗交界线沿额头、鼻侧、颧骨外缘走
    'side': dict(dark=[(0.26, -1.2), (0.2, -0.6), (0.1, -0.25), (0.12, 0.2), (0.3, 0.45), (0.45, 0.62), (0.3, 0.86), (0.12, 1.04), (1.3, 1.1), (1.3, -1.2)],
                 nose=[(0.04, 0.2), (0.3, 0.3), (0.22, 0.44), (0.04, 0.42)], hl=[(-0.4, -0.55, 0.16), (-0.06, -0.05, 0.05), (-0.04, 0.33, 0.06), (-0.5, 0.15, 0.1), (-0.2, 0.88, 0.07)]),
    'butterfly': dict(dark=[(0.92, -0.2), (0.8, 0.5), (0.4, 0.9), (1.3, 1.1), (1.3, -0.2)], dark2=[(-0.92, -0.2), (-0.8, 0.5), (-0.4, 0.9), (-1.3, 1.1), (-1.3, -0.2)],
                      nose=[(-0.08, 0.44), (0.08, 0.44), (0.0, 0.53)], hl=[(0, -0.55, 0.14), (0, 0.0, 0.05), (0, 0.33, 0.06), (-0.45, 0.12, 0.09), (0.45, 0.12, 0.09)]),
    'loop': dict(dark=[(0.7, -1.2), (0.62, -0.2), (0.64, 0.4), (0.4, 0.88), (1.3, 1.1), (1.3, -1.2)],
                 nose=[(0.05, 0.4), (0.22, 0.46), (0.2, 0.56), (0.06, 0.48)], hl=[(-0.25, -0.55, 0.15), (-0.03, 0.0, 0.05), (-0.03, 0.33, 0.06), (-0.45, 0.12, 0.1)]),
    'rembrandt': dict(dark=[(0.2, -1.2), (0.14, -0.55), (0.1, -0.25), (0.42, -0.12), (0.62, -0.1), (0.62, 0.0), (0.18, 0.3), (0.4, 0.38), (0.52, 0.5), (0.34, 0.76), (0.12, 1.02), (1.3, 1.1), (1.3, -1.2)],
                      tri=[(0.18, 0.0), (0.5, 0.02), (0.22, 0.24)],
                      nose=[], hl=[(-0.38, -0.55, 0.15), (-0.06, -0.05, 0.05), (-0.04, 0.33, 0.06), (-0.5, 0.15, 0.1)]),
    'split': dict(dark=[(0.02, -1.2), (0.02, -0.3), (0.0, 0.4), (0.0, 1.2), (1.3, 1.2), (1.3, -1.2)], nose=[], hl=[(-0.4, -0.55, 0.15), (-0.08, -0.05, 0.05), (-0.5, 0.15, 0.1)]),
    'flat': dict(dark=[], nose=[(-0.06, 0.44), (0.06, 0.44), (0.0, 0.48)], hl=[(0, -0.55, 0.16), (0, 0.02, 0.06), (0, 0.34, 0.08), (-0.45, 0.12, 0.12), (0.45, 0.12, 0.12), (0, 0.85, 0.08)]),
}


def face(cx, cy, w, h, fid, skin='#F3D5C2', dark='#B88D78', hair=PINK, mode='side', marks=False, reflect=True,
         extra_dark=None, gray_mode=False, neck=True, under='#000000', sw=2.5, blush=None):
    """正面人脸。mode：side/butterfly/loop/rembrandt/split/flat。extra_dark：额外的暗色区域列表 [(路径点, 颜色, 不透明度)]"""
    g = face_geom(cx, cy, w, h)
    fp = face_path(g)
    sh = SHADES[mode]
    s = [f'<defs><clipPath id="fc{fid}"><path d="{fp}"/></clipPath>{blur_def(fid, w * 0.035)}{blur_def(str(fid) + "b", w * 0.012)}</defs>']
    # 脖子和后发
    s.append(f'<path d="M{cx - w * 0.62:.1f} {g["top"] + h * 0.22:.1f} Q{cx - w * 0.7:.1f} {g["chin"] + h * 0.1:.1f} {cx - w * 0.5:.1f} {g["chin"] + h * 0.18:.1f} L{cx + w * 0.5:.1f} {g["chin"] + h * 0.18:.1f} Q{cx + w * 0.7:.1f} {g["chin"] + h * 0.1:.1f} {cx + w * 0.62:.1f} {g["top"] + h * 0.22:.1f} Z" fill="{hair}" stroke="{INK}" stroke-width="{sw}"/>')
    if neck:
        nk_dark = mix(skin, dark, 0.8)
        s.append(f'<rect x="{cx - w * 0.2:.1f}" y="{g["chin"] - h * 0.12:.1f}" width="{w * 0.4:.1f}" height="{h * 0.36:.1f}" fill="{skin}" stroke="{INK}" stroke-width="{sw}"/>')
        nx = cx - w * 0.2 if mode in ('butterfly', 'flat') else cx - w * 0.05
        s.append(f'<rect x="{nx:.1f}" y="{g["chin"] - h * 0.05:.1f}" width="{cx + w * 0.2 - nx:.1f}" height="{h * 0.29:.1f}" fill="{nk_dark}" fill-opacity="{0.55 if mode == "flat" else 0.85}"/>')
    # 耳朵
    for sg in (-1, 1):
        ex = cx + sg * w * 0.5
        ec = dark if (sg > 0 and mode in ('side', 'split', 'rembrandt', 'loop')) else skin
        s.append(f'<ellipse cx="{ex:.1f}" cy="{g["eye"] + h * 0.08:.1f}" rx="{w * 0.07:.1f}" ry="{h * 0.1:.1f}" fill="{ec}" stroke="{INK}" stroke-width="{sw}"/>')
    s.append(f'<path d="{fp}" fill="{skin}"/>')
    inner = []
    # 眼窝（光从上方来时总会暗一点）
    for sg in (-1, 1):
        ex, ey = P(g, sg * 0.4, -0.1)
        inner.append(f'<ellipse cx="{ex:.1f}" cy="{ey:.1f}" rx="{w * 0.17:.1f}" ry="{h * 0.07:.1f}" fill="{dark}" fill-opacity="{0.15 if mode == "flat" else 0.35}" filter="url(#bl{fid})"/>')
    if sh['dark']:
        inner.append(f'<path d="{smooth(g, sh["dark"])}" fill="{dark}" filter="url(#bl{str(fid) + "b"})"/>')
    if sh.get('dark2'):
        inner.append(f'<path d="{smooth(g, sh["dark2"])}" fill="{dark}" filter="url(#bl{str(fid) + "b"})"/>')
    if mode == 'rembrandt':
        inner.append(f'<path d="{poly(g, sh["tri"])}" fill="{skin}" filter="url(#bl{str(fid) + "b"})"/>')
    if reflect and mode in ('side', 'split', 'rembrandt'):
        rp = smooth(g, [(0.86, -0.3), (0.94, 0.1), (0.78, 0.55), (0.55, 0.85), (0.5, 0.78), (0.72, 0.48), (0.82, 0.1), (0.78, -0.3)])
        inner.append(f'<path d="{rp}" fill="{mix(dark, skin, 0.35)}" filter="url(#bl{fid})"/>')
    if extra_dark:
        for pts, col, op in extra_dark:
            inner.append(f'<path d="{smooth(g, pts)}" fill="{col}" fill-opacity="{op}" filter="url(#bl{fid})"/>')
    if blush:
        for sg in (-1, 1):
            bx, by = P(g, sg * 0.5, 0.25)
            inner.append(f'<ellipse cx="{bx:.1f}" cy="{by:.1f}" rx="{w * 0.12:.1f}" ry="{h * 0.05:.1f}" fill="{blush}" fill-opacity=".55" filter="url(#bl{fid})"/>')
    # 鼻影、唇下影
    if sh['nose']:
        inner.append(f'<path d="{smooth(g, sh["nose"])}" fill="{mix(dark, under, 0.25)}" fill-opacity=".9" filter="url(#bl{str(fid) + "b"})"/>')
    lx, ly = P(g, 0.0 if mode in ('butterfly', 'flat') else 0.06, 0.73)
    inner.append(f'<ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="{w * 0.1:.1f}" ry="{h * 0.025:.1f}" fill="{dark}" fill-opacity=".7" filter="url(#bl{str(fid) + "b"})"/>')
    for (u, v, r) in sh['hl']:
        hx, hy = P(g, u, v)
        inner.append(f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="{w * r:.1f}" ry="{w * r * 0.7:.1f}" fill="#FFFFFF" fill-opacity=".55" filter="url(#bl{fid})"/>')
    s.append(f'<g clip-path="url(#fc{fid})">' + ''.join(inner) + '</g>')
    s.append(f'<path d="{fp}" fill="none" stroke="{INK}" stroke-width="{sw}"/>')
    # 五官线条
    for sg in (-1, 1):
        ex, ey = P(g, sg * 0.4, -0.04)
        s.append(f'<path d="M{ex - w * 0.11:.1f} {ey:.1f} Q{ex:.1f} {ey - h * 0.05:.1f} {ex + w * 0.11:.1f} {ey:.1f}" fill="none" stroke="{INK}" stroke-width="{sw}" stroke-linecap="round"/>')
        s.append(f'<circle cx="{ex:.1f}" cy="{ey + h * 0.012:.1f}" r="{w * 0.04:.1f}" fill="{INK}"/>')
        bx, by = P(g, sg * 0.4, -0.22)
        s.append(f'<path d="M{bx - w * 0.12:.1f} {by + h * 0.01:.1f} Q{bx:.1f} {by - h * 0.03:.1f} {bx + w * 0.12:.1f} {by + h * 0.01:.1f}" fill="none" stroke="{INK}" stroke-width="{sw * 1.1}" stroke-linecap="round"/>')
    nx, ny = P(g, 0.0, 0.4)
    s.append(f'<path d="M{nx - w * 0.07:.1f} {ny:.1f} Q{nx:.1f} {ny + h * 0.03:.1f} {nx + w * 0.07:.1f} {ny:.1f}" fill="none" stroke="{INK}" stroke-width="{sw * 0.9}" stroke-linecap="round"/>')
    mx, my = P(g, 0.0, 0.64)
    s.append(f'<path d="M{mx - w * 0.12:.1f} {my:.1f} Q{mx:.1f} {my + h * 0.035:.1f} {mx + w * 0.12:.1f} {my:.1f}" fill="none" stroke="{INK}" stroke-width="{sw}" stroke-linecap="round"/>')
    # 刘海
    s.append(f'<path d="M{cx - w * 0.58:.1f} {g["top"] + h * 0.3:.1f} Q{cx - w * 0.6:.1f} {g["top"] - h * 0.06:.1f} {cx:.1f} {g["top"] - h * 0.05:.1f} Q{cx + w * 0.6:.1f} {g["top"] - h * 0.06:.1f} {cx + w * 0.58:.1f} {g["top"] + h * 0.3:.1f} '
             f'Q{cx + w * 0.3:.1f} {g["top"] + h * 0.12:.1f} {cx + w * 0.05:.1f} {g["top"] + h * 0.2:.1f} Q{cx - w * 0.25:.1f} {g["top"] + h * 0.1:.1f} {cx - w * 0.58:.1f} {g["top"] + h * 0.3:.1f} Z" fill="{hair}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    body = ''.join(s)
    if gray_mode:
        body = f'<g filter="url(#gs)">{body}</g>'
    return body, g


# =====================================================================
# 3.1 光影
# =====================================================================
def p_three_planes():
    Wd, Hd = 760, 400
    s = [box(20, 10, 360, 380, '立方体：三个面一眼分开'), box(400, 10, 340, 380, '球：三个面连成渐变')]
    s.append(ground(40, 320, 320))
    cb, pos = cube(190, 300, 120)
    s.append(lamp(70, 80))
    s.append(arrow(92, 98, 140, 140, YEL, 3))
    s.append(cb)
    s.append(leader(pos['top'][0], pos['top'][1] + 4, 290, 92) + lbl(296, 98, '亮面', WHITE, 14))
    s.append(leader(pos['left'][0], pos['left'][1], 60, 250) + lbl(40, 286, '灰面', '#E5E5E5', 14))
    s.append(leader(pos['right'][0], pos['right'][1], 316, 196) + lbl(296, 186, '暗面', '#9CA3AF', 14))
    s.append(text(200, 372, '朝着光的面最亮，侧着的面居中，背着的面最暗', 13, 600, MUTED, 'middle'))
    # 球
    s.append(ground(420, 320, 300))
    s.append(lamp(450, 80))
    s.append(cast_shadow(570, 318, 80, 'tp'))
    s.append(sphere(570, 225, 80, 'tps'))
    s.append(leader(538, 192, 650, 82) + lbl(656, 88, '亮面', WHITE, 14))
    s.append(leader(590, 235, 668, 150) + lbl(672, 156, '灰面', '#E5E5E5', 14))
    s.append(leader(622, 268, 676, 222) + lbl(670, 228, '暗面', '#9CA3AF', 14))
    s.append(text(580, 372, '圆的东西没有棱，三个面是慢慢过渡的', 13, 600, MUTED, 'middle'))
    save('p-three-planes', svg(Wd, Hd, ''.join(s), '三大面：亮面、灰面、暗面'))


def p_five_tones():
    Wd, Hd = 760, 430
    s = [box(20, 10, 720, 410, '五大调：从亮到暗依次是高光、灰面、明暗交界线、反光、投影')]
    s.append(ground(40, 330, 680))
    s.append(lamp(80, 90))
    s.append(arrow(100, 108, 160, 150, YEL, 3))
    cx, cy, r = 250, 228, 100
    s.append(cast_shadow(cx, 328, r, 'ft'))
    s.append(sphere(cx, cy, r, 'fts'))
    s.append(f'<path d="M{cx - 92:.1f} {cy + 40:.1f} Q{cx + 4:.1f} {cy + 66:.1f} {cx + 44:.1f} {cy - 90:.1f}" fill="none" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6 5" transform="rotate(-12 {cx} {cy})"/>')
    items = [('① 高光', (cx - 42, cy - 42), (440, 92), WHITE, '正对光源，最亮的一小块'),
             ('② 灰面', (cx - 6, cy + 0), (440, 140), '#E5E5E5', '受光的大面积中间调'),
             ('③ 明暗交界线', (cx + 36, cy + 46), (440, 188), RED1, '亮暗分界，最暗的一条带'),
             ('④ 反光', (cx + 80, cy + 50), (440, 236), '#D1D5DB', '暗部边缘被环境照亮'),
             ('⑤ 投影', (cx + 150, 334), (440, 284), '#9CA3AF', '物体挡住光落下的影子')]
    for name, (px, py), (lx, ly), fill, desc in items:
        s.append(leader(px, py, lx - 8, ly - 6))
        s.append(lbl(lx, ly, name, fill, 14))
        s.append(text(lx + 130, ly, desc, 13, 600, MUTED))
    s.append(text(40, 400, '亮部：高光 > 灰面　　暗部：反光 < 灰面，交界线最暗　　投影：贴着物体的地方最深', 13, 700, INK))
    save('p-five-tones', svg(Wd, Hd, ''.join(s), '五大调在球上的位置'))


def p_forms():
    Wd, Hd = 760, 380
    s = [box(20, 10, 720, 360, '同一束光打在三种形状上：交界线的样子不一样')]
    s.append(ground(40, 290, 680))
    s.append(lamp(70, 70))
    # 球
    s.append(cast_shadow(150, 288, 62, 'fm1'))
    s.append(sphere(150, 216, 62, 'fm1s'))
    s.append(text(150, 330, '球：交界线是一条弧', 14, 700, INK, 'middle'))
    # 立方体
    cb, pos = cube(375, 280, 96)
    s.append(cb)
    s.append(text(380, 330, '立方体：交界线就是棱', 14, 700, INK, 'middle'))
    s.append(f'<line x1="375" y1="280" x2="375" y2="184" stroke="{RED}" stroke-width="3" stroke-dasharray="6 4"/>')
    # 圆柱
    s.append(f'<polygon points="610,298 660,280 715,276 728,290 640,304" fill="#3A3A3A" fill-opacity=".75"/>')
    s.append(cylinder(610, 130, 100, 150, 'fm3'))
    s.append(f'<line x1="636" y1="132" x2="636" y2="296" stroke="{RED}" stroke-width="3" stroke-dasharray="6 4"/>')
    s.append(text(610, 330, '圆柱：交界线是一条竖线', 14, 700, INK, 'middle'))
    s.append(lbl(450, 70, '红色虚线：明暗交界线', RED1, 13))
    s.append(text(380, 356, '人的脸颊、手臂、腿接近圆柱，额头、头顶接近球，鼻梁、下巴的侧面接近立方体', 12.5, 600, MUTED, 'middle'))
    save('p-forms', svg(Wd, Hd, ''.join(s), '球、立方体、圆柱上的明暗分布'))


def p_hard_soft():
    Wd, Hd = 760, 400
    s = [box(20, 10, 360, 380, '硬光：光源小、离得远', YEL1), box(400, 10, 340, 380, '软光：光源大、离得近', MINT1)]
    s.append(ground(40, 300, 320) + ground(420, 300, 300))
    s.append(lamp(80, 92, 11))
    s.append(cast_shadow(200, 298, 72, 'hs1', hard=True))
    s.append(sphere(200, 220, 72, 'hs1s', hard=True))
    s.append(lamp(470, 100, 18, soft=True))
    s.append(cast_shadow(580, 298, 72, 'hs2', soft=True))
    s.append(sphere(580, 220, 72, 'hs2s', soft=True))
    s.append(text(200, 336, '交界线窄、边缘清楚', 14, 700, INK, 'middle'))
    s.append(text(200, 358, '影子轮廓锐利，对比强', 13, 400, MUTED, 'middle'))
    s.append(text(580, 336, '交界线宽、过渡慢', 14, 700, INK, 'middle'))
    s.append(text(580, 358, '影子边缘虚，对比弱', 13, 400, MUTED, 'middle'))
    s.append(text(200, 380, '例：晴天正午太阳、裸闪、射灯', 12, 600, MUTED, 'middle'))
    s.append(text(580, 380, '例：阴天、窗边散射光、柔光箱', 12, 600, MUTED, 'middle'))
    save('p-hard-soft', svg(Wd, Hd, ''.join(s), '硬光和软光的对比'))


def p_light_dir():
    Wd, Hd = 760, 380
    s = [box(20, 10, 720, 360, '判断光从哪来：看三个线索')]
    # 线索 1：投影方向
    s.append(ground(40, 280, 220))
    s.append(cast_shadow(120, 278, 40, 'ld1', dx=0.9, k=1.3))
    s.append(sphere(120, 236, 40, 'ld1s'))
    s.append(arrow(214, 300, 70, 210, YEL, 3, '6 5'))
    s.append(text(150, 330, '① 影子朝哪边倒', 14, 800, INK, 'middle'))
    s.append(text(150, 350, '光就在反方向', 12.5, 600, MUTED, 'middle'))
    # 线索 2：高光位置
    s.append(sphere(380, 200, 60, 'ld2s'))
    s.append(ring(354, 174, 14))
    s.append(arrow(330, 120, 352, 158, YEL, 3))
    s.append(text(380, 330, '② 高光在哪', 14, 800, INK, 'middle'))
    s.append(text(380, 350, '高光那一侧就是光来的方向', 12.5, 600, MUTED, 'middle'))
    # 线索 3：鼻子和眼窝的影子
    fb, g = face(610, 190, 110, 150, 'ld3', mode='loop')
    s.append(fb)
    s.append(ring(*P(g, 0.15, 0.48), 16))
    s.append(text(610, 330, '③ 鼻子的影子', 14, 800, INK, 'middle'))
    s.append(text(610, 350, '影子往右下 → 光在左上', 12.5, 600, MUTED, 'middle'))
    save('p-light-dir', svg(Wd, Hd, ''.join(s), '判断光源方向的三个线索'))


def p_face_zones():
    Wd, Hd = 760, 470
    s = [box(20, 10, 720, 450, '侧光人像：脸上哪里亮、哪里暗（光从画面左上方来）')]
    fb, g = face(220, 236, 200, 262, 'fz', mode='side')
    s.append(fb)
    # 交界线
    tl = smooth(g, [(0.25, -1.0), (0.2, -0.6), (0.1, -0.25), (0.12, 0.2), (0.3, 0.45), (0.45, 0.62), (0.3, 0.86), (0.12, 1.0)], close=False)
    s.append(f'<path d="{tl}" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="7 5"/>')
    s.append(lamp(70, 70))
    L = [('高光区：额头、鼻梁、颧骨上沿、下巴尖', (-0.4, -0.55), 92, WHITE),
         ('灰面：亮侧的脸颊大面积', (-0.55, 0.3), 140, '#F3E3D7'),
         ('明暗交界线：额头→鼻侧→脸颊→下巴', (0.3, 0.45), 188, RED1),
         ('暗部：远离光的半张脸、眼窝', (0.6, -0.2), 236, '#D6BFB2'),
         ('反光：暗侧下颌边缘被衣服、地面照亮', (0.8, 0.5), 284, '#E9D6CB'),
         ('投影：鼻子下、下唇下、下巴下的脖子', (0.16, 0.4), 332, '#C9A999')]
    for name, (u, v), ly, fill in L:
        px, py = P(g, u, v)
        s.append(leader(px, py, 372, ly - 6))
        s.append(lbl(380, ly, name, fill, 13.5))
    s.append(text(380, 392, '人脸的五大调和球一样，只是形状更复杂：', 13, 700, INK))
    s.append(text(380, 414, '额头像球、鼻子像立方体、脸颊像圆柱', 13, 600, MUTED))
    save('p-face-zones', svg(Wd, Hd, ''.join(s), '侧光人像的高光区、暗区和明暗交界线'))


def p_face_patterns():
    Wd, Hd = 760, 360
    s = [box(20, 10, 720, 340, '四种常见人像光：灯从正面往侧面移')]
    items = [('butterfly', '蝴蝶光', '灯在正前上方', '鼻子下有对称的小影子'), ('loop', '环形光', '灯偏 30°～45°', '鼻影斜向下，不连脸颊'),
             ('rembrandt', '伦勃朗光', '灯偏约 45°、更高', '暗侧脸颊留一块三角亮区'), ('split', '分割光（侧光）', '灯在 90° 正侧面', '脸一半亮一半暗')]
    for i, (m, name, a, b) in enumerate(items):
        cx = 110 + i * 180
        fb, g = face(cx, 150, 92, 122, 'pt' + m, mode=m)
        s.append(fb)
        s.append(text(cx, 284, name, 15, 800, INK, 'middle'))
        s.append(text(cx, 306, a, 12.5, 600, MUTED, 'middle'))
        s.append(text(cx, 326, b, 12.5, 600, MUTED, 'middle'))
    save('p-face-patterns', svg(Wd, Hd, ''.join(s), '蝴蝶光、环形光、伦勃朗光、分割光'))


def p_reflect_wrong():
    Wd, Hd = 760, 360
    s = [box(20, 10, 360, 340, '对：反光比灰面暗', MINT1), box(400, 10, 340, 340, '错：反光比灰面还亮', RED1)]
    s.append(ground(40, 270, 320) + ground(420, 270, 300))
    s.append(cast_shadow(200, 268, 74, 'rw1'))
    s.append(sphere(200, 190, 74, 'rw1s'))
    bad = [(0, '#FFFFFF'), (0.1, '#F3F3F3'), (0.38, '#CFCFCF'), (0.56, '#A5A5A5'), (0.66, '#505050'), (0.8, '#8A8A8A'), (0.92, '#E0E0E0'), (1, '#F4F4F4')]
    s.append(cast_shadow(580, 268, 74, 'rw2'))
    s.append(sphere(580, 190, 74, 'rw2s', base=bad))
    s.append(ring(258, 236, 13) + ring(152, 168, 13))
    s.append(ring(638, 236, 13) + ring(532, 168, 13))
    s.append(text(200, 306, '暗部整体是一块，球是"实"的', 14, 700, INK, 'middle'))
    s.append(text(200, 328, '黄圈：反光（右下）比灰面（左上）暗', 12.5, 600, MUTED, 'middle'))
    s.append(text(580, 306, '边缘发白，像一个空心的泡泡', 14, 700, INK, 'middle'))
    s.append(text(580, 328, '修图时把下颌、脸侧提得太亮就会这样', 12.5, 600, MUTED, 'middle'))
    save('p-reflect-wrong', svg(Wd, Hd, ''.join(s), '反光不能比灰面亮'))


# ---------- 3.1 界面 ----------
def photo_face(x, y, w, h, fid, mode='side', **kw):
    """画布里的一张人像照片"""
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#E8E1D6"/>'
    fb, g = face(x + w / 2, y + h * 0.42, w * 0.55, h * 0.52, fid, mode=mode, **kw)
    s += fb + f'<path d="M{x + w * 0.08:.1f} {y + h:.1f} Q{x + w * 0.2:.1f} {y + h * 0.8:.1f} {x + w * 0.5:.1f} {y + h * 0.8:.1f} Q{x + w * 0.8:.1f} {y + h * 0.8:.1f} {x + w * 0.92:.1f} {y + h:.1f} Z" fill="{VIO2}" stroke="{INK}" stroke-width="2.5"/>'
    return f'<g>{s}</g>', g


CX, CY, CW, CH = 262, 66, 276, 360


def blend_menu(x, y, w, current, modes, op=1.0):
    s = [panel(x, y, w, 70 + len(modes) * 32)]
    s.append(text(x + 16, y + 28, '不透明度', 13, 700, UITEXT))
    s.append(f'<rect x="{x + 90}" y="{y + 20}" width="{w - 150}" height="8" rx="4" fill="{UIBLUE}"/>')
    s.append(f'<circle cx="{x + 90 + (w - 150) * op:.1f}" cy="{y + 24}" r="8" fill="{WHITE}"/>' + text(x + w - 16, y + 30, f'{int(op * 100)}%', 13, 700, UITEXT, 'end'))
    for i, m in enumerate(modes):
        yy = y + 48 + i * 32
        on = m == current
        if on:
            s.append(f'<rect x="{x + 8}" y="{yy}" width="{w - 16}" height="28" rx="7" fill="{UIBLUE}"/>')
        s.append(text(x + 20, yy + 20, m, 14, 700, UITEXT))
    return ''.join(s)


def layer_rows(x, y, w, rows, title='图层'):
    """rows: [(名字, 缩略图颜色, 模式字母, 选中)]"""
    rh = 52
    s = [panel(x, y, w, 50 + len(rows) * rh + 8, title), text(x + w - 26, y + 30, '+', 24, 700, UITEXT, 'middle')]
    for i, (name, tc, mode, sel) in enumerate(rows):
        yy = y + 44 + i * rh
        s.append(f'<rect x="{x + 8}" y="{yy}" width="{w - 16}" height="{rh - 6}" rx="8" fill="{UIBLUE if sel else UIBAR}"/>')
        s.append(f'<rect x="{x + 16}" y="{yy + 6}" width="44" height="34" rx="4" fill="{tc}" stroke="{WHITE}" stroke-width="1"/>')
        s.append(text(x + 70, yy + 29, name, 15, 700, UITEXT))
        s.append(text(x + w - 46, yy + 29, mode, 14, 800, UITEXT, 'middle'))
        s.append(f'<rect x="{x + w - 30}" y="{yy + 15}" width="16" height="16" rx="3" fill="{UIBLUE}" stroke="{UITEXT}" stroke-width="1.5"/>')
        POS['row:' + name] = (x + 8, yy, w - 16, rh - 6)
    return ''.join(s)


def u_fill_black():
    ph, g = photo_face(CX, CY, CW, CH, 'ufb')
    rows = [('灰度观察', '#111111', 'N', True), ('图层 1（原图）', '#E8D5C4', 'N', False)]
    lay = layer_rows(470, 62, 300, rows)
    ox, oy = 210, 150
    opts = ['重命名', '选择', '拷贝', '填充图层', '清除', '阿尔法锁定', '蒙版', '剪辑蒙版']
    menu = panel(ox, oy, 200, 16 + len(opts) * 34) + menu_rows(ox, oy + 8, 200, opts, hl='填充图层')
    s = screen(ph + lay + menu, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += ring(756, 34, 17)
    s += badge(730, 62, 1)
    s += badge(486, 62 + 44 + 23, 2) + badge(ox + 186, oy + 8 + 3 * 34 + 17, 3)
    s += lbl(36, 520, '① 当前颜色先选纯黑　② 新建图层，轻点两次打开图层选项　③ 点「填充图层」', WHITE, 13)
    s += note('示意图，以实际界面为准')
    save('u-fill-black', svg(W, H, s, '新建图层，用图层选项里的填充图层填满黑色'))


def u_gray_mode():
    ph, g = photo_face(CX, CY, CW, CH, 'ugm')
    ph = f'<g filter="url(#gs)">{ph}</g>'
    rows = [('灰度观察', '#111111', 'Co', True), ('图层 1（原图）', '#E8D5C4', 'N', False)]
    lay = layer_rows(470, 62, 300, rows)
    menu = blend_menu(470, 186, 300, '颜色', ['差值', '排除', '减去', '划分', '色相', '饱和度', '颜色', '明度'])
    s = screen(GRAY_FILTER + ph + lay + menu, active='layers')
    s += ring(470 + 300 - 46, 62 + 44 + 23, 16) + badge(470 + 300 - 46, 62 + 44 - 6, 1)
    s += badge(470 + 300 - 26, 186 + 48 + 6 * 32 + 14, 2)
    s += lbl(36, 486, '① 轻点图层右边的字母 N，打开混合模式', WHITE, 13)
    s += lbl(36, 520, '② 往下滑到「颜色」：画面变成黑白，只剩明暗', WHITE, 13)
    s += note('示意图，字母和列表顺序以实际界面为准')
    save('u-gray-mode', svg(W, H, s, '黑色图层设成颜色混合模式，画面只剩明暗'))


def value_panel(x, y, c, hl=None, w=330):
    """色彩面板「值」页"""
    h_, s_, b_ = to_hsb(c)
    r, g_, b2 = rgb_of(c)
    s = [panel(x, y, w, 330), text(x + 16, y + 28, '颜色', 17, 800, UITEXT)]
    s.append(f'<rect x="{x + w - 84}" y="{y + 12}" width="34" height="22" rx="4" fill="{c}" stroke="{WHITE}"/><rect x="{x + w - 50}" y="{y + 12}" width="34" height="22" rx="4" fill="#000" stroke="{WHITE}"/>')
    rows = [('色相', h_ / 360, f'{h_}°', 'hue'), ('饱和度', s_ / 100, f'{s_}%', None), ('亮度', b_ / 100, f'{b_}%', None),
            ('红', r / 255, str(r), None), ('绿', g_ / 255, str(g_), None), ('蓝', b2 / 255, str(b2), None)]
    for i, (nm, f, val, kind) in enumerate(rows):
        yy = y + 60 + i * 34 + (10 if i >= 3 else 0)
        s.append(text(x + 16, yy + 6, nm, 13, 700, UITEXT))
        bx, bw = x + 66, w - 150
        if kind == 'hue':
            st = ''.join(f'<stop offset="{k / 6:.3f}" stop-color="{hsv(k * 60, 100, 100)}"/>' for k in range(7))
            s.append(f'<defs><linearGradient id="hueg{x}{y}">{st}</linearGradient></defs><rect x="{bx}" y="{yy - 4}" width="{bw}" height="12" rx="6" fill="url(#hueg{x}{y})"/>')
        else:
            s.append(f'<rect x="{bx}" y="{yy - 4}" width="{bw}" height="12" rx="6" fill="#6B7280"/><rect x="{bx}" y="{yy - 4}" width="{bw * f:.1f}" height="12" rx="6" fill="{UIBLUE}"/>')
        s.append(f'<circle cx="{bx + bw * f:.1f}" cy="{yy + 2}" r="8" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>')
        s.append(f'<rect x="{x + w - 74}" y="{yy - 10}" width="58" height="24" rx="5" fill="{UIBAR}"/>' + text(x + w - 45, yy + 7, val, 13, 700, UITEXT, 'middle'))
        POS['val:' + nm] = (x + 8, yy - 14, w - 16, 32)
    yy = y + 60 + 6 * 34 + 14
    s.append(text(x + 16, yy + 6, '十六进制', 13, 700, UITEXT) + f'<rect x="{x + 90}" y="{yy - 10}" width="110" height="24" rx="5" fill="{UIBAR}"/>' + text(x + 145, yy + 7, c.lstrip('#'), 13, 700, UITEXT, 'middle'))
    tabs = ['色盘', '经典', '色彩调和', '值', '调色板']
    tx = x + 12
    ch, pad = (13, 14) if w >= 300 else (11, 8)
    for t in tabs:
        tw = len(t) * ch + pad
        s.append(f'<rect x="{tx}" y="{y + 296}" width="{tw}" height="24" rx="6" fill="{UIBLUE if t == "值" else UIBAR}"/>' + text(tx + tw / 2, y + 313, t, 12, 700, UITEXT, 'middle'))
        POS['tab:' + t] = (tx, y + 296, tw, 24)
        tx += tw + 6
    if hl:
        for k in hl:
            s.append(ringrect(*POS[k]))
    return ''.join(s)


def eyedrop(x, y, new, cur, r=30):
    """长按出现的取色圆环：上半圈是正在取的颜色，下半圈是当前颜色"""
    return (f'<path d="M{x - r} {y} A{r} {r} 0 0 1 {x + r} {y} L{x + r - 10} {y} A{r - 10} {r - 10} 0 0 0 {x - r + 10} {y} Z" fill="{new}" stroke="{WHITE}" stroke-width="2"/>'
            f'<path d="M{x - r} {y} A{r} {r} 0 0 0 {x + r} {y} L{x + r - 10} {y} A{r - 10} {r - 10} 0 0 1 {x - r + 10} {y} Z" fill="{cur}" stroke="{WHITE}" stroke-width="2"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{INK}" stroke-width="2"/><circle cx="{x}" cy="{y}" r="3" fill="{INK}"/>')


def u_tone_value():
    """在灰度画面上取色比较灰面和反光"""
    ph, g = photo_face(CX, CY, CW, CH, 'utv')
    ph = f'<g filter="url(#gs)">{ph}</g>'
    gx, gy = P(g, -0.5, 0.3)
    rx, ry = P(g, 0.78, 0.45)
    s = screen(GRAY_FILTER + ph + eyedrop(rx, ry, '#8A8A8A', '#C4C4C4', 26), active='color')
    s += f'<circle cx="{gx:.1f}" cy="{gy:.1f}" r="7" fill="none" stroke="{YEL}" stroke-width="3"/>' + badge(gx - 18, gy - 18, 1)
    s += badge(rx + 30, ry - 26, 2)
    vp = value_panel(546, 100, '#8A8A8A', hl=['val:亮度'], w=232)
    s += vp
    s += lbl(36, 486, '① 长按灰面取色，看「值」里的亮度，记下来（例：77%）', WHITE, 13)
    s += lbl(36, 520, '② 再长按反光处取色：亮度应该比①低（例：54%），比交界线高', WHITE, 13)
    s += note('示意图，以实际界面为准')
    save('u-tone-value', svg(W, H, s, '用取色和值面板的亮度数字比较灰面和反光'))


def egg_photo(x, y, w, h, gid):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#D9D4CA"/><rect x="{x}" y="{y + h * 0.66:.1f}" width="{w}" height="{h * 0.34:.1f}" fill="#BDB6A8"/>'
    ex, ey, r = x + w * 0.46, y + h * 0.42, w * 0.26
    s += cast_shadow(ex, ey + r * 1.42, r, gid + 'c', dx=0.75, k=1.2)
    stops = [(0, '#FFFFFF'), (0.12, '#F3F0EA'), (0.45, '#D6D0C4'), (0.68, '#A8A296'), (0.78, '#6E685E'), (0.88, '#7E786E'), (1, '#958F84')]
    st = ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    fx, fy = ex - r * 0.45, ey - r * 0.55
    s += (f'<defs><radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{fx:.1f}" cy="{fy:.1f}" r="{r * 1.75:.1f}" fx="{fx:.1f}" fy="{fy:.1f}">{st}</radialGradient></defs>'
          f'<ellipse cx="{ex:.1f}" cy="{ey + r * 0.2:.1f}" rx="{r:.1f}" ry="{r * 1.28:.1f}" fill="url(#{gid})"/>')
    return s, (ex, ey + r * 0.2, r)


def u_mark_tones():
    ph, (ex, ey, r) = egg_photo(CX, CY, CW, CH, 'umt')
    marks = []
    pts = {'1': (ex - r * 0.42, ey - r * 0.62), '2': (ex - r * 0.1, ey - r * 0.1), '3': (ex + r * 0.38, ey + r * 0.62), '4': (ex + r * 0.86, ey + r * 0.62), '5': (ex + r * 1.45, ey + r * 1.25)}
    # 交界线
    marks.append(f'<path d="M{ex - r * 0.6:.1f} {ey + r * 1.15:.1f} Q{ex + r * 0.65:.1f} {ey + r * 0.9:.1f} {ex + r * 0.85:.1f} {ey - r * 0.6:.1f}" fill="none" stroke="{MINT}" stroke-width="4" stroke-linecap="round"/>')
    for k, (x_, y_) in pts.items():
        marks.append(f'<circle cx="{x_:.1f}" cy="{y_:.1f}" r="11" fill="{MINT}" stroke="{INK}" stroke-width="2"/>' + text(x_, y_ + 5, k, 13, 900, INK, 'middle'))
    lay = layer_rows(560, 300, 210, [('五大调标注', MINT, 'N', True), ('鸡蛋照片', '#D9D4CA', 'N', False)])
    s = screen(ph + ''.join(marks) + lay, active='brush')
    s += ring(*icon_pos('brush'), 18) + badge(icon_pos('brush')[0] - 26, 62, 1)
    legend = ['1 高光', '2 灰面', '3 明暗交界线', '4 反光', '5 投影']
    for i, t in enumerate(legend):
        s += lbl(560, 92 + i * 34, t, YEL1 if i != 2 else MINT1, 13)
    s += lbl(36, 520, '新建图层「五大调标注」，技术笔写编号，交界线用一条线描出来', WHITE, 13)
    s += note('示意图')
    save('u-mark-tones', svg(W, H, s, '在鸡蛋照片上新建图层标出五大调'))


# ---------- 3.1 案例 ----------
def case_side(after):
    Wd, Hd = 640, 520
    s = [f'<rect x="20" y="20" width="600" height="480" fill="#D8D2C8"/>']
    fb, g = face(320, 250, 250, 320, 'cs' + str(int(after)), mode='side', hair='#3B3F58')
    s.append(fb)
    s.append(f'<path d="M80 500 Q140 420 320 420 Q500 420 560 500 Z" fill="#4C5578" stroke="{INK}" stroke-width="2.5"/>')
    if after:
        tl = smooth(g, [(0.25, -1.0), (0.2, -0.6), (0.1, -0.25), (0.12, 0.2), (0.3, 0.45), (0.45, 0.62), (0.3, 0.86), (0.12, 1.0)], close=False)
        s.append(f'<path d="{tl}" fill="none" stroke="{MINT}" stroke-width="4" stroke-linecap="round"/>')
        for k, (u, v) in {'高光': (-0.4, -0.55), '灰面': (-0.55, 0.32), '反光': (0.8, 0.5), '投影': (0.17, 0.42)}.items():
            x, y = P(g, u, v)
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{MINT}" stroke="{INK}" stroke-width="2"/>')
        s.append(lbl(40, 470, '绿线：明暗交界线（额头 → 鼻侧 → 颧骨下方的脸颊 → 下巴）', MINT1, 14))
        s.append(lamp(70, 110, 14) + arrow(92, 128, 150, 170, YEL, 4))
        s.append(lbl(40, 56, '主光从左上方来（看鼻影朝右下、高光在左侧）', YEL1, 14))
    else:
        s.append(lbl(40, 56, '侧光人像原片', YEL1, 15))
    return svg(Wd, Hd, ''.join(s), '侧光人像标注' if after else '侧光人像原片')


def case_flat(after):
    Wd, Hd = 640, 520
    s = [f'<rect x="20" y="20" width="600" height="480" fill="#2E3142"/>']
    fb, g = face(320, 250, 250, 320, 'cf' + str(int(after)), mode='butterfly' if after else 'flat',
                 skin='#F6DCCB' if not after else '#F1D2BE', dark='#C99D86' if not after else '#B98972', hair='#E8E8F0')
    s.append(fb)
    s.append(f'<path d="M80 500 Q140 420 320 420 Q500 420 560 500 Z" fill="#7A2D3A" stroke="{INK}" stroke-width="2.5"/>')
    if after:
        s.append(lbl(40, 56, '目标：两侧脸颊、鼻侧、下颌下加出暗部', VIO1, 14))
        s.append(lbl(40, 470, '额头、鼻梁、颧骨上沿保持亮，脸就"立"起来了', VIO1, 14))
    else:
        s.append(lbl(40, 56, '漫展正面闪光：几乎没有暗部，脸是平的', YEL1, 14))
    return svg(Wd, Hd, ''.join(s), '正面闪光平脸')


def part1():
    for f in [p_three_planes, p_five_tones, p_forms, p_hard_soft, p_light_dir, p_face_zones, p_face_patterns, p_reflect_wrong,
              u_fill_black, u_gray_mode, u_tone_value, u_mark_tones]:
        f()
    save('case-side-before', case_side(False)); save('case-side-after', case_side(True))
    save('case-flat-before', case_flat(False)); save('case-flat-after', case_flat(True))


def part2():
    for f in [p_hsb, p_wheel, p_mix_gray, p_warm_cool, p_harmony, p_area, u_eyedrop, u_value, u_harmony, u_palette, case_palette_a, case_palette_b]:
        f()
    save('case-wig-before', case_wig(False)); save('case-wig-after', case_wig(True))


def part3():
    for f in [p_skin_hue, p_skin_sb, p_dirty, p_fix_paths, p_unify, u_blur_sample, u_skin_value, u_sat_check, u_color_balance, u_hsb_adjust, u_mask_skin, u_color_layer]:
        f()
    for k in ('yellow', 'cyan'):
        save(f'case-{k}-before', case_skin(k, False)); save(f'case-{k}-after', case_skin(k, True))


# =====================================================================
# 3.2 色彩
# =====================================================================
def wheel(cx, cy, r0, r1, n=72, s_=100, v=100, start=-90):
    """色相环：0° 红在正上方，顺时针 红→黄→绿→青→蓝→品红（和 Procreate 色盘方向可能不同，只看相对位置）"""
    out = []
    for i in range(n):
        a0 = math.radians(start + i * 360 / n); a1 = math.radians(start + (i + 1) * 360 / n + 0.6)
        p = lambda r, a: (cx + r * math.cos(a), cy + r * math.sin(a))
        x0, y0 = p(r1, a0); x1, y1 = p(r1, a1); x2, y2 = p(r0, a1); x3, y3 = p(r0, a0)
        out.append(f'<path d="M{x0:.1f} {y0:.1f} A{r1} {r1} 0 0 1 {x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} A{r0} {r0} 0 0 0 {x3:.1f} {y3:.1f} Z" fill="{hsv(i * 360 / n, s_, v)}"/>')
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r1}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    if r0 > 0:
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r0}" fill="none" stroke="{INK}" stroke-width="2"/>')
    return ''.join(out)


def wpos(cx, cy, r, hdeg, start=-90):
    a = math.radians(start + hdeg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def p_hsb():
    Wd, Hd = 760, 400
    s = [box(20, 10, 720, 380, '一个颜色 = 色相 H + 饱和度 S + 亮度 B')]
    rows = [('色相 H（0°～360°）', '是什么颜色：红、橙、黄、绿……转一圈回到红', [hsv(h, 85, 95) for h in range(0, 360, 30)], [f'{h}°' for h in range(0, 360, 30)]),
            ('饱和度 S（0%～100%）', '有多浓：0% 是灰，100% 最鲜艳', [hsv(25, s_, 92) for s_ in range(0, 101, 10)], [f'{s_}%' for s_ in range(0, 101, 10)]),
            ('亮度 B（0%～100%）', '有多亮：0% 是黑，100% 最亮', [hsv(25, 60, b) for b in range(0, 101, 10)], [f'{b}%' for b in range(0, 101, 10)])]
    for i, (t, d, cols, caps) in enumerate(rows):
        y = 70 + i * 104
        s.append(text(44, y + 4, t, 15, 800, INK) + text(250, y + 4, d, 13, 600, MUTED))
        n = len(cols); w = 640 / n
        for j, (c, cap) in enumerate(zip(cols, caps)):
            s.append(f'<rect x="{44 + j * w:.1f}" y="{y + 16}" width="{w - 4:.1f}" height="40" rx="5" fill="{c}" stroke="{INK}" stroke-width="1.5"/>')
            s.append(text(44 + j * w + w / 2 - 2, y + 74, cap, 11.5, 600, MUTED, 'middle'))
    s.append(text(44, 376, '中间一行固定 H25、B92，只改 S；下面一行固定 H25、S60，只改 B。肤色就在这个橙色附近。', 12.5, 700, INK))
    save('p-hsb', svg(Wd, Hd, ''.join(s), '色相、饱和度、亮度'))


def p_wheel():
    Wd, Hd = 760, 440
    s = [box(20, 10, 720, 420, '色相环和三对互补色（屏幕上的 RGB 色相环）')]
    cx, cy = 230, 250
    s.append(wheel(cx, cy, 80, 140))
    names = [(0, '红 0°'), (60, '黄 60°'), (120, '绿 120°'), (180, '青 180°'), (240, '蓝 240°'), (300, '品红 300°')]
    for hdeg, nm in names:
        x, y = wpos(cx, cy, 164, hdeg)
        s.append(text(x, y + 5, nm, 13, 800, INK, 'middle'))
    for h1, col in [(0, RED7), (60, '#A16207'), (120, MINT7)]:
        x1, y1 = wpos(cx, cy, 110, h1); x2, y2 = wpos(cx, cy, 110, h1 + 180)
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 4"/>')
        s.append(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="7" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/><circle cx="{x2:.1f}" cy="{y2:.1f}" r="7" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="78" fill="{WHITE}"/>' + text(cx, cy - 4, '对面的颜色', 14, 800, INK, 'middle') + text(cx, cy + 16, '= 互补色', 14, 800, INK, 'middle'))
    pairs = [((0, 180), '红 ↔ 青'), ((300, 120), '品红 ↔ 绿'), ((60, 240), '黄 ↔ 蓝')]
    for i, ((a, b), nm) in enumerate(pairs):
        y = 90 + i * 70
        s.append(swatch(470, y, hsv(a, 90, 95), 50, 40) + swatch(526, y, hsv(b, 90, 95), 50, 40))
        s.append(text(592, y + 26, nm, 15, 800, INK))
    s.append(text(470, 316, '修图里最常用的就是这三对：', 13, 700, INK))
    s.append(text(470, 338, '偏黄就往蓝那边拉，偏绿就往品红拉，', 13, 600, MUTED))
    s.append(text(470, 360, '偏红就往青那边拉。', 13, 600, MUTED))
    s.append(text(470, 392, '美术课的颜料色环（红↔绿、黄↔紫）是另一套，', 12, 600, MUTED))
    s.append(text(470, 410, '在 iPad 上调色以这张图为准。', 12, 600, MUTED))
    save('p-wheel', svg(Wd, Hd, ''.join(s), '色相环和互补色'))


def p_mix_gray():
    Wd, Hd = 760, 330
    s = [box(20, 10, 720, 310, '互补色混在一起会变灰：这是"抵消偏色"和"颜色变脏"的共同原理')]
    for i, (a, b, nm) in enumerate([(hsv(30, 85, 95), hsv(210, 85, 95), '橙 + 蓝'), (hsv(0, 80, 90), hsv(180, 80, 90), '红 + 青')]):
        y = 74 + i * 110
        s.append(text(44, y + 26, nm, 15, 800, INK))
        for j in range(11):
            t = j / 10
            c = mix(a, b, t)
            s.append(f'<rect x="{140 + j * 52}" y="{y}" width="48" height="44" rx="6" fill="{c}" stroke="{INK}" stroke-width="1.5"/>')
            s.append(text(140 + j * 52 + 24, y + 62, f'{int(t * 100)}%', 11.5, 600, MUTED, 'middle'))
        s.append(lbl(140 + 5 * 52 + 24, y - 8, '一半一半：几乎是灰的', WHITE, 12, 'middle'))
    s.append(text(44, 300, '少量：去掉偏色（偏黄的照片加一点蓝）　　过量：颜色发灰、发脏（肤色里混进蓝紫）', 13, 700, INK))
    save('p-mix-gray', svg(Wd, Hd, ''.join(s), '互补色混合变灰'))


def p_warm_cool():
    Wd, Hd = 760, 380
    s = [box(20, 10, 720, 360, '冷暖：色相环一半偏暖、一半偏冷')]
    cx, cy = 180, 192
    s.append(wheel(cx, cy, 0, 122, n=72, s_=80, v=95))
    s.append(f'<line x1="{wpos(cx, cy, 140, 120)[0]:.1f}" y1="{wpos(cx, cy, 140, 120)[1]:.1f}" x2="{wpos(cx, cy, 140, 300)[0]:.1f}" y2="{wpos(cx, cy, 140, 300)[1]:.1f}" stroke="{INK}" stroke-width="3" stroke-dasharray="8 5"/>')
    s.append(lbl(256, 74, '暖：红、橙、黄', '#FED7AA', 14) + lbl(36, 344, '冷：青、蓝、蓝紫', '#BFDBFE', 14))
    s.append(text(300, 362, '虚线两端的绿和品红：看旁边配什么', 12, 600, MUTED, 'middle'))
    # 右侧：冷暖在照片里
    s.append(text(400, 70, '在 cos 照片里冷暖是"比出来的"：', 14, 800, INK))
    for i, (sk, bg, cap) in enumerate([(hsv(25, 38, 92), hsv(215, 45, 55), '暖肤色 + 冷背景：人跳出来'), (hsv(25, 38, 92), hsv(35, 50, 80), '暖肤色 + 暖背景：糊成一片'),
                                        (hsv(210, 18, 85), hsv(215, 45, 55), '肤色被调冷：发青、像生病')]):
        y = 96 + i * 88
        s.append(f'<rect x="400" y="{y}" width="110" height="72" rx="8" fill="{bg}" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<ellipse cx="455" cy="{y + 38}" rx="24" ry="30" fill="{sk}" stroke="{INK}" stroke-width="2"/>')
        s.append(text(526, y + 42, cap, 13.5, 700, INK))
    save('p-warm-cool', svg(Wd, Hd, ''.join(s), '冷暖色'))


def harmony_mini(cx, cy, r, marks, title, desc):
    s = [wheel(cx, cy, 0, r, n=48, s_=75, v=95)]
    pts = [wpos(cx, cy, r * 0.8, m) for m in marks]
    if len(pts) > 1:
        s.append(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    for i, (x, y) in enumerate(pts):
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{8 if i == 0 else 6}" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(text(cx, cy + r + 26, title, 14, 800, INK, 'middle'))
    s.append(text(cx, cy + r + 46, desc, 12, 600, MUTED, 'middle'))
    return ''.join(s)


def p_harmony():
    Wd, Hd = 760, 300
    s = [box(20, 10, 720, 280, 'Procreate「色彩调和」里的五种配色关系（白点：大圆点是主色）')]
    items = [([20, 200], '互补', '对比最强'), ([20, 170, 230], '补色分割', '对比强但更柔和'), ([20, 50, 350], '近似', '同一个色系，最安全'),
             ([20, 140, 260], '三等分', '三色都抢眼'), ([20, 110, 200, 290], '矩形', '四色，最难控制')]
    for i, (m, t, d) in enumerate(items):
        s.append(harmony_mini(94 + i * 143, 140, 58, m, t, d))
    save('p-harmony', svg(Wd, Hd, ''.join(s), '五种配色关系'))


def p_area():
    Wd, Hd = 760, 380
    s = [box(20, 10, 720, 360, '配色三条法则：面积有主次、互补要平衡、冷暖要有主调')]
    # 1 面积
    s.append(text(44, 80, '① 面积：主色约 70%，辅色约 25%，点缀约 5%', 14, 800, INK))
    cols = [(hsv(225, 55, 45), 0.7), (hsv(220, 8, 92), 0.25), (hsv(45, 85, 95), 0.05)]
    x = 44
    for c, f in cols:
        w = 660 * f
        s.append(f'<rect x="{x:.1f}" y="92" width="{w:.1f}" height="44" fill="{c}" stroke="{INK}" stroke-width="2"/>')
        x += w
    s.append(text(44 + 231, 156, '主色：深蓝（制服）', 12.5, 700, INK, 'middle') + text(44 + 462 + 82, 156, '辅色：白', 12.5, 700, INK, 'middle') + text(704 - 16, 156, '点缀：金', 12.5, 700, INK, 'end'))
    # 2 互补平衡
    s.append(text(44, 196, '② 互补平衡：一对互补色，一个面积大就降饱和，一个面积小可以很鲜艳', 14, 800, INK))
    s.append(f'<rect x="44" y="210" width="300" height="56" fill="{hsv(215, 40, 50)}" stroke="{INK}" stroke-width="2"/><rect x="300" y="224" width="30" height="28" fill="{hsv(30, 95, 98)}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(194, 286, '对：大面积灰蓝 + 小块亮橙', 12.5, 700, MINT7, 'middle'))
    s.append(f'<rect x="404" y="210" width="150" height="56" fill="{hsv(215, 95, 90)}" stroke="{INK}" stroke-width="2"/><rect x="554" y="210" width="150" height="56" fill="{hsv(30, 95, 98)}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(554, 286, '刺眼：两个都满饱和、面积一样', 12.5, 700, RED7, 'middle'))
    # 3 冷暖
    s.append(text(44, 326, '③ 冷暖主调：整张图要么偏冷要么偏暖，另一边只占小面积。肤色属于暖色，冷调照片里也要留住它的暖', 13, 700, INK))
    save('p-area', svg(Wd, Hd, ''.join(s), '配色的面积、互补平衡和冷暖主调'))


# ---------- 3.2 界面 ----------
def char_photo(x, y, w, h, fid, wig, outfit, acc, eye=None, bg='#E8E1D6', skin='#F3D5C2'):
    """角色设定图 / 照片的简笔版：头 + 上身"""
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>'
    fb, g = face(x + w / 2, y + h * 0.36, w * 0.42, h * 0.4, fid, mode='loop', hair=wig, skin=skin, dark=mix(skin, '#8A5A44', 0.35))
    s += fb
    s += (f'<path d="M{x + w * 0.06:.1f} {y + h:.1f} Q{x + w * 0.14:.1f} {y + h * 0.7:.1f} {x + w * 0.5:.1f} {y + h * 0.68:.1f} Q{x + w * 0.86:.1f} {y + h * 0.7:.1f} {x + w * 0.94:.1f} {y + h:.1f} Z" fill="{outfit}" stroke="{INK}" stroke-width="2.5"/>'
          f'<path d="M{x + w * 0.4:.1f} {y + h * 0.69:.1f} L{x + w * 0.5:.1f} {y + h * 0.82:.1f} L{x + w * 0.6:.1f} {y + h * 0.69:.1f}" fill="none" stroke="{acc}" stroke-width="7"/>'
          f'<circle cx="{x + w * 0.5:.1f}" cy="{y + h * 0.86:.1f}" r="{w * 0.04:.1f}" fill="{acc}" stroke="{INK}" stroke-width="2"/>')
    if eye:
        for sg in (-1, 1):
            ex, ey = P(g, sg * 0.4, -0.02)
            s += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{w * 0.022:.1f}" fill="{eye}"/>'
    return s, g


def u_eyedrop():
    WIG, OUT_, ACC = hsv(215, 12, 92), hsv(225, 60, 42), hsv(45, 80, 92)
    ph, g = char_photo(CX, CY, CW, CH, 'ued', WIG, OUT_, ACC, eye=hsv(350, 80, 80))
    px, py = CX + CW * 0.3, CY + CH * 0.85
    s = screen(ph + eyedrop(px, py, OUT_, '#F472B6', 30), active='color')
    s += f'<ellipse cx="{px:.1f}" cy="{py + 44:.1f}" rx="10" ry="13" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>'
    s += badge(px - 46, py - 30, 1)
    s += lbl(CX + CW + 14, py - 50, '手指长按画面，出现取色圆环', YEL1, 13)
    s += lbl(CX + CW + 14, py - 18, '上半圈：正在取的颜色', YEL1, 13)
    s += lbl(CX + CW + 14, py + 14, '下半圈：原来的当前颜色', YEL1, 13)
    s += lbl(CX + CW + 14, py + 46, '松手就选中了', YEL1, 13)
    s += ringrect(28, 262, 22, 24, 5) + badge(64, 274, 2)
    s += lbl(36, 520, '② 长按没反应：点侧栏中间的小方块（修改），再点画面', WHITE, 13)
    s += note('示意图，以实际界面为准')
    save('u-eyedrop', svg(W, H, s, '长按画面取色'))


def u_value():
    c = hsv(225, 60, 42)
    ph, g = char_photo(CX, CY, CW, CH, 'uva', hsv(215, 12, 92), c, hsv(45, 80, 92), eye=hsv(350, 80, 80))
    s = screen(ph, active='color')
    s += value_panel(440, 62, c, hl=['val:色相', 'val:饱和度', 'val:亮度', 'tab:值'])
    s += ring(756, 34, 17) + badge(726, 62, 1)
    s += badge(426, 62 + 60 + 34, 2)
    s += lbl(36, 486, '① 轻点右上角的当前颜色，打开色彩面板', WHITE, 13)
    s += lbl(36, 520, '② 底部选「值」，读出色相、饱和度、亮度三个数', WHITE, 13)
    s += note('示意图，以实际界面为准')
    save('u-value', svg(W, H, s, '色彩面板的值：读 HSB 数值'))


def harmony_panel(x, y, w, base_h, mode='互补', sat=60):
    s = [panel(x, y, w, 360), text(x + 16, y + 28, '颜色', 17, 800, UITEXT)]
    s.append(f'<rect x="{x + 14}" y="{y + 44}" width="70" height="26" rx="6" fill="{UIBAR}"/>' + text(x + 49, y + 62, mode + ' ▾', 13, 800, UITEXT, 'middle'))
    POS['harm:mode'] = (x + 14, y + 44, 70, 26)
    cx, cy, r = x + w / 2, y + 180, 100
    # 色盘：外圈色相、中间往白过渡（饱和度）
    out = []
    n = 72
    for i in range(n):
        for k, (r0, r1, ss) in enumerate([(0, 34, 15), (34, 67, 50), (67, 100, 95)]):
            a0 = math.radians(-90 + i * 5); a1 = math.radians(-90 + (i + 1) * 5 + 0.6)
            pp = lambda rr, a: (cx + rr * math.cos(a), cy + rr * math.sin(a))
            x0, y0 = pp(r1, a0); x1, y1 = pp(r1, a1); x2, y2 = pp(r0, a1); x3, y3 = pp(r0, a0)
            out.append(f'<path d="M{x0:.1f} {y0:.1f} A{r1} {r1} 0 0 1 {x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} A{r0} {r0} 0 0 0 {x3:.1f} {y3:.1f} Z" fill="{hsv(i * 5, ss, 95)}"/>')
    s.append(''.join(out) + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#111" stroke-width="2"/>')
    rr = r * sat / 100
    for i, hd in enumerate([base_h, base_h + 180]):
        mx, my = wpos(cx, cy, rr, hd)
        s.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{12 if i == 0 else 9}" fill="{hsv(hd, sat, 95)}" stroke="{WHITE}" stroke-width="3"/><circle cx="{mx:.1f}" cy="{my:.1f}" r="{12 if i == 0 else 9}" fill="none" stroke="{INK}" stroke-width="1.5"/>')
        POS[f'harm:m{i}'] = (mx, my)
    s.append(f'<defs><linearGradient id="bw{x}"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#FFF"/></linearGradient></defs><rect x="{x + 30}" y="{y + 296}" width="{w - 60}" height="12" rx="6" fill="url(#bw{x})"/><circle cx="{x + w - 50}" cy="{y + 302}" r="8" fill="{WHITE}" stroke="{INK}"/>')
    tabs = ['色盘', '经典', '色彩调和', '值', '调色板']
    tx = x + 12
    for t in tabs:
        tw = len(t) * 13 + 14
        s.append(f'<rect x="{tx}" y="{y + 324}" width="{tw}" height="24" rx="6" fill="{UIBLUE if t == "色彩调和" else UIBAR}"/>' + text(tx + tw / 2, y + 341, t, 12, 700, UITEXT, 'middle'))
        POS['tab:' + t] = (tx, y + 324, tw, 24)
        tx += tw + 6
    return ''.join(s)


def u_harmony():
    c = hsv(225, 60, 42)
    ph, g = char_photo(CX, CY, CW, CH, 'uha', hsv(215, 12, 92), c, hsv(45, 80, 92))
    s = screen(ph, active='color')
    s += harmony_panel(440, 62, 330, 225, sat=60)
    s += ringrect(*POS['tab:色彩调和']) + badge(POS['tab:色彩调和'][0] + 30, 62 + 324 - 14, 1)
    s += ringrect(*POS['harm:mode']) + badge(440 + 100, 62 + 57, 2)
    mx, my = POS['harm:m1']
    s += ring(mx, my, 16) + badge(mx + 24, my + 20, 3)
    s += lbl(36, 452, '① 底部选「色彩调和」', WHITE, 13)
    s += lbl(36, 486, '② 左上角选模式（默认「互补」）', WHITE, 13)
    s += lbl(36, 520, '③ 拖动大圈到主色，小圈自动停在它的互补色上', WHITE, 13)
    s += note('示意图，以实际界面为准')
    save('u-harmony', svg(W, H, s, '色彩调和：看一个颜色的互补色在哪'))


def u_palette():
    cols = [hsv(225, 60, 42), hsv(215, 12, 92), hsv(45, 80, 92), hsv(350, 80, 80), hsv(24, 30, 94)]
    ph, g = char_photo(CX, CY, CW, CH, 'upa', cols[1], cols[0], cols[2], eye=cols[3])
    x, y, w = 440, 62, 330
    s_ = [panel(x, y, w, 200), text(x + 16, y + 28, '调色板', 17, 800, UITEXT), text(x + w - 24, y + 31, '+', 26, 700, UITEXT, 'middle')]
    s_.append(f'<rect x="{x + 110}" y="{y + 12}" width="60" height="24" rx="6" fill="{UIBLUE}"/>' + text(x + 140, y + 29, '紧凑', 12, 700, UITEXT, 'middle'))
    s_.append(f'<rect x="{x + 176}" y="{y + 12}" width="70" height="24" rx="6" fill="{UIBAR}"/>' + text(x + 211, y + 29, '大调色板', 12, 700, UITEXT, 'middle'))
    s_.append(text(x + 16, y + 70, '角色 A 配色', 14, 800, UITEXT) + f'<circle cx="{x + 120}" cy="{y + 65}" r="7" fill="{UIBLUE}"/>' + text(x + w - 20, y + 70, '···', 16, 800, UITEXT, 'end'))
    for i in range(10):
        c = cols[i] if i < len(cols) else None
        bx = x + 16 + i * 30
        s_.append(f'<rect x="{bx}" y="{y + 82}" width="26" height="26" rx="4" fill="{c or UIBAR}" stroke="#6B7280"/>')
    s_.append(text(x + 16, y + 140, '默认调色板', 14, 700, UITEXT))
    for i in range(10):
        s_.append(f'<rect x="{x + 16 + i * 30}" y="{y + 152}" width="26" height="26" rx="4" fill="{hsv(i * 36, 70, 90)}"/>')
    s = screen(ph + ''.join(s_), active='color')
    s += ring(x + w - 24, y + 24, 16) + badge(x + w - 50, y + 24, 1)
    s += ringrect(x + 16 + 5 * 30 - 3, y + 79, 32, 32, 5) + badge(x + 16 + 5 * 30 + 13, y + 128, 2)
    s += lbl(x, y + 236, '① 「+」新建调色板，改名为角色名', YEL1, 13)
    s += lbl(x, y + 270, '② 取色后，轻点空白色卡就存进去', YEL1, 13)
    s += lbl(x, y + 304, '长按色卡可以删除', WHITE, 13)
    s += note('示意图，以实际界面为准')
    save('u-palette', svg(W, H, s, '新建调色板，把取到的颜色存成色卡'))


# ---------- 3.2 案例 ----------
def palette_card(x, y, cols, names, title, rel, wheel_marks):
    s = [box(x, y, 720, 250, title)]
    for i, (c, nm) in enumerate(zip(cols, names)):
        s.append(swatch(x + 24 + i * 96, y + 60, c, 80, 64, nm, hsb_cap(c), 12))
    s.append(wheel(x + 610, y + 120, 0, 70, n=48, s_=75, v=95))
    for i, hd in enumerate(wheel_marks):
        mx, my = wpos(x + 610, y + 120, 56, hd)
        s.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{8 if i == 0 else 6}" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(text(x + 24, y + 200, rel[0], 13.5, 800, INK))
    s.append(text(x + 24, y + 224, rel[1], 13, 600, MUTED))
    return ''.join(s)


def case_palette_a():
    cols = [hsv(225, 60, 42), hsv(215, 12, 92), hsv(45, 80, 92), hsv(350, 80, 80), hsv(24, 30, 94)]
    names = ['制服 深蓝', '假发 银白', '饰边 金', '瞳色 红', '肤色']
    s = palette_card(20, 10, cols, names, '角色 A：深蓝制服 + 金饰边（示例角色）',
                     ('关系：互补（蓝 225° ↔ 金 45°，正好相差 180°）；银白几乎没有颜色，夹在中间做缓冲', '面积：深蓝 70% 主色，白 20%，金和红瞳只占小块 → 互补色一大一小，不刺眼'), [225, 45, 350])
    save('case-palette-a', svg(760, 270, s, '角色 A 的配色提取'))


def case_palette_b():
    cols = [hsv(330, 35, 95), hsv(285, 40, 80), hsv(345, 55, 90), hsv(40, 30, 98), hsv(20, 28, 95)]
    names = ['假发 樱粉', '裙子 浅紫', '蝴蝶结 玫红', '花边 奶白', '肤色']
    s = palette_card(20, 10, cols, names, '角色 B：粉紫系少女（示例角色）',
                     ('关系：近似（紫 285°、粉 330°、玫红 345° 都在品红附近，跨度只有 60°）', '饱和度都在 30%～55%，没有一块特别跳 → 整体柔和；要强调就提高蝴蝶结的饱和度'), [330, 285, 345])
    save('case-palette-b', svg(760, 270, s, '角色 B 的配色提取'))


def case_wig(after):
    """照片里的假发颜色 vs 设定：同一个角色 A"""
    Wd, Hd = 640, 520
    wig = hsv(215, 12, 92) if after else hsv(35, 22, 88)
    outfit = hsv(225, 60, 42) if after else hsv(235, 45, 36)
    bg = '#3A3F52'
    ph, g = char_photo(20, 20, 600, 480, 'cw' + str(int(after)), wig, outfit, hsv(45, 80, 92), bg=bg)
    s = [ph]
    s.append(swatch(470, 380, wig, 60, 40) + swatch(540, 380, outfit, 60, 40))
    s.append(text(535, 446, '假发　制服', 12, 800, WHITE, 'middle'))
    s.append(text(535, 466, hsb_cap(wig), 11, 600, WHITE, 'middle') + text(535, 484, hsb_cap(outfit), 11, 600, WHITE, 'middle'))
    lab = '对照设定修正后：银白偏冷、制服回到深蓝' if after else '照片取色：暖灯下假发发黄，制服发紫发暗'
    s.append(lbl(40, 56, lab, VIO1 if after else YEL1, 14))
    return svg(Wd, Hd, ''.join(s), lab)


# =====================================================================
# 3.3 肤色
# =====================================================================
SKIN_OK = hsv(24, 34, 88)
SKIN_YG = hsv(37, 21, 76)     # 偏黄发灰
SKIN_REF = [('白皙', (18, 28), (18, 30), (88, 96)), ('自然', (18, 30), (28, 42), (78, 90)),
            ('小麦', (20, 32), (38, 52), (62, 80)), ('深肤色', (15, 30), (45, 65), (30, 60))]


def p_skin_hue():
    Wd, Hd = 760, 330
    s = [box(20, 10, 720, 310, '肤色的色相几乎都落在橙色这一小段（0°～60° 放大）')]
    x0, x1, y = 60, 700, 150
    k = (x1 - x0) / 60
    for h in range(60):
        s.append(f'<rect x="{x0 + h * k:.1f}" y="{y}" width="{k + 0.6:.1f}" height="44" fill="{hsv(h, 45, 90)}"/>')
    s.append(f'<rect x="{x0}" y="{y}" width="{x1 - x0}" height="44" fill="none" stroke="{INK}" stroke-width="2"/>')
    for h in range(0, 61, 10):
        s.append(f'<line x1="{x0 + h * k:.1f}" y1="{y + 44}" x2="{x0 + h * k:.1f}" y2="{y + 54}" stroke="{INK}" stroke-width="2"/>' + text(x0 + h * k, y + 72, f'{h}°', 12.5, 700, INK, 'middle'))
    # 区段
    zones = [(0, 12, RED1, '偏红、偏品红', RED7), (18, 30, MINT1, '常见落点', MINT7), (32, 60, YEL1, '偏黄、蜡黄', '#A16207')]
    for a, b, fill, nm, col in zones:
        s.append(f'<rect x="{x0 + a * k:.1f}" y="{y - 34}" width="{(b - a) * k:.1f}" height="26" rx="6" fill="{fill}" stroke="{col}" stroke-width="2"/>' + text(x0 + (a + b) / 2 * k, y - 16, nm, 13, 800, col, 'middle'))
    for i, h in enumerate([8, 15, 22, 28, 36, 44]):
        cx = 110 + i * 108
        s.append(f'<ellipse cx="{cx}" cy="262" rx="28" ry="34" fill="{hsv(h, 34, 88)}" stroke="{INK}" stroke-width="2"/>' + text(cx + 38, 268, f'H{h}', 12.5, 800, INK))
    s.append(text(380, 312, '下面一排：S34、B88 不变，只改色相。同样亮、同样浓，色相往黄那边走 10° 左右就显得蜡黄', 12.5, 700, MUTED, 'middle'))
    save('p-skin-hue', svg(Wd, Hd, ''.join(s), '肤色的色相范围'))


def p_skin_sb():
    Wd, Hd = 760, 440
    s = [box(20, 10, 720, 420, '色相固定 24°：饱和度和亮度怎样组合才"干净"')]
    gx, gy, cw, ch = 110, 60, 52, 32
    Ss = list(range(0, 75, 7))[:11]
    Bs = [100, 92, 84, 76, 68, 60, 52, 44, 36]
    for j, b in enumerate(Bs):
        s.append(text(gx - 10, gy + j * ch + ch / 2 + 5, f'B{b}', 12, 700, INK, 'end'))
        for i, sv in enumerate(Ss):
            s.append(f'<rect x="{gx + i * cw}" y="{gy + j * ch}" width="{cw}" height="{ch}" fill="{hsv(24, sv, b)}"/>')
    for i, sv in enumerate(Ss):
        s.append(text(gx + i * cw + cw / 2, gy + len(Bs) * ch + 18, f'S{sv}', 12, 700, INK, 'middle'))
    s.append(f'<rect x="{gx}" y="{gy}" width="{len(Ss) * cw}" height="{len(Bs) * ch}" fill="none" stroke="{INK}" stroke-width="2"/>')

    def region(s0, s1, b0, b1, col, nm, dy=0):
        x_a = gx + (s0 / 7) * cw; x_b = gx + (s1 / 7) * cw + cw * 0
        y_a = gy + (100 - b1) / 8 * ch; y_b = gy + (100 - b0) / 8 * ch + ch * 0
        return (f'<rect x="{x_a:.1f}" y="{y_a:.1f}" width="{x_b - x_a:.1f}" height="{y_b - y_a:.1f}" fill="none" stroke="{col}" stroke-width="3.5" rx="6"/>'
                + lbl(x_b + 6, y_a + 20 + dy, nm, WHITE, 12, stroke=col))
    s.append(region(18, 30, 88, 96, VIO7, '白皙'))
    s.append(region(28, 42, 78, 90, MINT7, '自然', 12))
    s.append(region(38, 52, 62, 80, '#B45309', '小麦', 10))
    s.append(region(45, 65, 30, 60, INK, '深肤色', 30))
    s.append(f'<rect x="{gx}" y="{gy}" width="{cw * 2.5:.1f}" height="{ch * 5:.1f}" fill="#64748B" fill-opacity=".25" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    s.append(lbl(gx + 6, gy + ch * 5 - 10, 'S 低于 18：发灰', RED1, 12))
    s.append(text(gx - 60, 418, '框是常见落点（脸颊中间调处取样），仅供参考、不是修图目标；红色虚线区在亮处也显得灰、没血色', 12, 700, MUTED))
    save('p-skin-sb', svg(Wd, Hd, ''.join(s), '肤色的饱和度和亮度范围'))


def p_dirty():
    Wd, Hd = 760, 400
    s = [box(20, 10, 720, 380, '肤色为什么会"脏"：往橙色里混进了它的对面色')]
    blue = hsv(220, 45, 62)
    s.append(text(44, 80, '肤色 + 蓝紫（冷色补光、蓝背景反光、调冷过头）', 14, 800, INK))
    for j in range(6):
        t = j * 0.1
        c = mix(SKIN_OK, blue, t)
        s.append(swatch(44 + j * 112, 92, c, 92, 50, f'混入 {int(t * 100)}%', hsb_cap(c), 12))
    gray50 = '#8C8C8C'
    s.append(text(44, 216, '肤色 + 灰（用灰色/黑色画笔压暗、降饱和过头）', 14, 800, INK))
    for j in range(6):
        t = j * 0.1
        c = mix(SKIN_OK, gray50, t)
        s.append(swatch(44 + j * 112, 228, c, 92, 50, f'混入 {int(t * 100)}%', hsb_cap(c), 12))
    s.append(text(44, 352, '两种情况都是饱和度先掉下来：S 从 34 掉到 20 以下，皮肤就发灰；', 13.5, 700, INK))
    s.append(text(44, 374, '混蓝紫时色相还会往 0° 以下（品红那边）跑，于是又灰又紫，看起来像冻着了或者没洗干净', 13, 600, MUTED))
    save('p-dirty', svg(Wd, Hd, ''.join(s), '往肤色里混入互补色和灰色'))


def rgb_hex(r, g, b):
    c = lambda v: max(0, min(255, round(v)))
    return '#%02X%02X%02X' % (c(r), c(g), c(b))


def p_fix_paths():
    Wd, Hd = 760, 360
    s = [box(20, 10, 720, 340, '偏黄发灰的肤色：先往哪个方向拉')]
    r, g, b = rgb_of(SKIN_YG)
    s.append(swatch(60, 150, SKIN_YG, 110, 80, '原来：偏黄发灰', hsb_cap(SKIN_YG), 13))
    opts = [('颜色平衡往「蓝色」拉', rgb_hex(r, g, b + 12), '色相回来了，但饱和度掉了 → 更灰', RED7),
            ('颜色平衡往「紫红色」拉', rgb_hex(r, g - 7, b), '色相回到橙色，饱和度不变', MINT7),
            ('再用「色相、饱和度和亮度」加饱和度', hsv(26, 33, 84), '色相不动，饱和度、亮度回来 → 干净', MINT7)]
    for i, (nm, c, d, col) in enumerate(opts):
        y = 64 + i * 92
        s.append(arrow(184, 190, 290, y + 30, col, 2.5))
        s.append(swatch(300, y, c, 90, 60) + text(404, y + 20, nm, 14, 800, col) + text(404, y + 42, hsb_cap(c), 13, 700, INK) + text(404, y + 62, d, 12.5, 600, MUTED))
    s.append(text(44, 340, '红绿太接近（绿多了）的蜡黄：只加蓝等于往橙色里加互补色，越修越灰。先往紫红拉回色相，再单独补饱和度。', 12.5, 700, INK))
    save('p-fix-paths', svg(Wd, Hd, ''.join(s), '去黄的三个方向'))


def skin_face(cx, cy, w, h, fid, skin, patches=(), **kw):
    """带局部偏色块的人脸。patches: [(点列, 颜色, 不透明度)]"""
    dark = mix(skin, '#6B3B2A', 0.32)
    return face(cx, cy, w, h, fid, skin=skin, dark=dark, mode='loop', extra_dark=list(patches), **kw)


def p_unify():
    Wd, Hd = 760, 450
    s = [box(20, 10, 360, 430, '不统一：同一张脸四五种颜色', RED1), box(400, 10, 340, 430, '统一：色相一致，明暗自然过渡', MINT1)]
    forehead = [(-0.6, -0.75), (0.6, -0.75), (0.5, -0.45), (-0.5, -0.45)]
    nose = [(-0.12, 0.1), (0.12, 0.1), (0.16, 0.45), (-0.16, 0.45)]
    under = [(-0.62, -0.02), (-0.2, -0.02), (-0.25, 0.1), (-0.6, 0.1)]
    jaw = [(-0.55, 0.55), (0.55, 0.55), (0.3, 0.9), (-0.3, 0.9)]
    pats = [(forehead, hsv(38, 30, 85), 0.85), (nose, hsv(6, 45, 85), 0.85), (under, hsv(300, 12, 62), 0.75), (jaw, hsv(40, 32, 66), 0.8)]
    fb, g = skin_face(200, 205, 170, 220, 'un1', SKIN_OK, pats, hair='#3B3F58')
    s.append(fb)
    for (pts, c, _), (u, v), nm in zip(pats, [(0.6, -0.6), (0.14, 0.3), (-0.5, 0.05), (0.4, 0.75)], ['额头偏黄', '鼻头偏红', '眼下发青紫', '下巴暗黄']):
        x, y = P(g, u, v)
        tx = 300 if u > 0 else 44
        s.append(leader(x, y, tx + (0 if u > 0 else 70), y + 2))
    labs = [('额头偏黄 H38', 300, 92), ('鼻头偏红 H6', 300, 196), ('眼下发青紫 H300', 44, 396), ('下巴暗黄 H40', 300, 396)]
    for t, x, y in labs:
        s.append(lbl(x - (40 if x > 200 else 0), y, t, WHITE, 12))
    fb2, g2 = skin_face(570, 205, 170, 220, 'un2', SKIN_OK, hair='#3B3F58')
    s.append(fb2)
    for (u, v), c in [((-0.4, -0.6), hsv(24, 26, 94)), ((-0.5, 0.25), SKIN_OK), ((0.55, 0.3), mix(SKIN_OK, '#6B3B2A', 0.32))]:
        x, y = P(g2, u, v)
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(570, 382, '亮处 H24 S26 B94 → 中间 H24 S34 B88', 12, 700, INK, 'middle'))
    s.append(text(570, 400, '→ 暗处 H22 S48 B60', 12, 700, INK, 'middle'))
    s.append(text(570, 418, '越暗饱和度越高，色相只差几度', 12, 600, MUTED, 'middle'))
    save('p-unify', svg(Wd, Hd, ''.join(s), '肤色的色相、饱和度、亮度统一'))


# ---------- 3.3 界面 ----------
def photo_skin(x, y, w, h, fid, skin, patches=(), bg='#4B5563', **kw):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>'
    fb, g = skin_face(x + w / 2, y + h * 0.42, w * 0.55, h * 0.52, fid, skin, patches, hair='#2F3347', **kw)
    s += fb + f'<path d="M{x + w * 0.08:.1f} {y + h:.1f} Q{x + w * 0.2:.1f} {y + h * 0.8:.1f} {x + w * 0.5:.1f} {y + h * 0.8:.1f} Q{x + w * 0.8:.1f} {y + h * 0.8:.1f} {x + w * 0.92:.1f} {y + h:.1f} Z" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>'
    return s, g


def top_banner(txt, pct=None):
    w = 260
    x = SX + SW / 2 - w / 2
    s = f'<rect x="{x}" y="66" width="{w}" height="30" rx="8" fill="{UIBLUE}"/>' + text(x + w / 2, 87, txt + (f'  {pct}' if pct else ''), 14, 800, WHITE, 'middle')
    return s


def u_blur_sample():
    ph, g = photo_skin(CX, CY, CW, CH, 'ubs', SKIN_YG)
    ph = f'<defs><filter id="bsoft"><feGaussianBlur stdDeviation="3"/></filter></defs><g filter="url(#bsoft)">{ph}</g>'
    lay = layer_rows(560, 300, 210, [('取样用', SKIN_YG, 'N', True), ('原图', SKIN_YG, 'N', False)])
    s = screen(ph + lay + top_banner('高斯模糊', '6%'), active='adjust')
    s += ring(*icon_pos('adjust'), 18) + badge(icon_pos('adjust')[0] - 26, 62, 1)
    s += arrow(300, 470, 380, 470, INK, 3) + text(300, 500, '一指在画面上左右滑：往右更糊', 13, 700, INK)
    s += badge(400 - 130 - 16, 81, 2)
    s += lbl(560, 290, '复制一层再模糊，只用来取色', YEL1, 12)
    s += note('示意图，以实际界面为准')
    save('u-blur-sample', svg(W, H, s, '复制一层做高斯模糊，取色时数值更稳'))


def u_skin_value():
    ph, g = photo_skin(CX, CY, CW, CH, 'usv', SKIN_YG)
    ph = f'<defs><filter id="bsoft2"><feGaussianBlur stdDeviation="3"/></filter></defs><g filter="url(#bsoft2)">{ph}</g>'
    px, py = P(g, -0.5, 0.22)
    s = screen(ph + eyedrop(px, py, SKIN_YG, '#F472B6', 26), active='color')
    s += badge(px - 40, py - 26, 1)
    s += value_panel(546, 100, SKIN_YG, hl=['val:色相', 'val:饱和度', 'val:亮度'], w=232)
    s += badge(536, 100 + 60 + 34, 2)
    s += lbl(36, 486, '① 长按左脸颊中间（避开高光、腮红、阴影）', WHITE, 13)
    s += lbl(36, 520, '② 打开色彩面板 › 值，记下 H、S、B。例：H37 S21 B76 → 偏黄、发灰', WHITE, 13)
    s += note('示意图，以实际界面为准')
    save('u-skin-value', svg(W, H, s, '在脸颊取色，读出肤色的 HSB 数值'))


def u_sat_check():
    pats = [([(-0.6, -0.75), (0.6, -0.75), (0.5, -0.45), (-0.5, -0.45)], hsv(40, 85, 95), 0.8),
            ([(-0.12, 0.1), (0.12, 0.1), (0.16, 0.45), (-0.16, 0.45)], hsv(2, 90, 95), 0.8),
            ([(-0.62, -0.02), (-0.2, -0.02), (-0.25, 0.1), (-0.6, 0.1)], hsv(285, 60, 70), 0.8)]
    ph, g = photo_skin(CX, CY, CW, CH, 'usc', hsv(24, 70, 95), pats)
    lay = layer_rows(560, 300, 210, [('观察用', hsv(24, 70, 95), 'N', True), ('原图', SKIN_OK, 'N', False)])
    sl = tool_sliders([('色相', 0.5), ('饱和度', 0.95), ('亮度', 0.5)], hl='饱和度')
    s = screen(ph + lay + sl, active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += lbl(560, 92, '饱和度拉到很高：', YEL1, 13)
    s += lbl(560, 124, '偏黄、偏红、发紫的地方', YEL1, 13)
    s += lbl(560, 156, '会变成明显的色块', YEL1, 13)
    s += lbl(560, 200, '看清位置就删掉这一层', WHITE, 13)
    s += note('示意图，滑块数值以实际界面为准')
    save('u-sat-check', svg(W, H, s, '复制一层把饱和度拉满，看清哪里偏色'))


def cb_slider(x, y, w, left, right, frac, hl=False):
    s = (text(x, y - 8, left, 12, 700, UITEXT) + text(x + w, y - 8, right, 12, 700, UITEXT, 'end')
         + f'<rect x="{x}" y="{y}" width="{w}" height="8" rx="4" fill="#6B7280"/><line x1="{x + w / 2}" y1="{y - 3}" x2="{x + w / 2}" y2="{y + 11}" stroke="{UITEXT}" stroke-width="2"/>'
         f'<circle cx="{x + w * frac:.1f}" cy="{y + 4}" r="9" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>')
    if hl:
        s += ringrect(x - 8, y - 26, w + 16, 44)
    return s


def u_color_balance():
    ph, g = photo_skin(CX, CY, CW, CH, 'ucb', SKIN_YG)
    y = SY + SH - 96
    x0 = 70
    bar = f'<rect x="{x0}" y="{y}" width="660" height="68" rx="14" fill="{UIBAR}"/>'
    bar += cb_slider(x0 + 20, y + 42, 120, '青色', '红色', 0.5)
    bar += cb_slider(x0 + 166, y + 42, 120, '紫红色', '绿色', 0.42, True)
    bar += cb_slider(x0 + 312, y + 42, 120, '黄色', '蓝色', 0.5)
    for i, b in enumerate(['阴影', '中间调', '高亮区域']):
        bw = 52 if i < 2 else 72
        bx = x0 + 452 + [0, 58, 116][i]
        bar += f'<rect x="{bx}" y="{y + 16}" width="{bw}" height="36" rx="8" fill="{UIBLUE if b == "中间调" else UIPANEL}"/>' + text(bx + bw / 2, y + 39, b, 12.5, 700, UITEXT, 'middle')
    bar += ringrect(x0 + 452 + 58 - 3, y + 13, 58, 42)
    s = screen(ph + bar, active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += badge(x0 + 452 + 58 + 26, y - 10, 1) + badge(x0 + 166 + 60, y - 30, 2)
    s += lbl(560, 110, '① 先选「中间调」', YEL1, 13)
    s += lbl(560, 142, '② 往紫红色那边拉一点点', YEL1, 13)
    s += lbl(560, 174, '黄色—蓝色：别往蓝拉', RED1, 13)
    s += lbl(560, 206, '拉完取色看色相回到 24～28', YEL1, 13)
    s += note('示意图，滑块名称和位置以实际界面为准')
    save('u-color-balance', svg(W, H, s, '颜色平衡：中间调，往紫红和红的方向拉'))


def u_hsb_adjust():
    ph, g = photo_skin(CX, CY, CW, CH, 'uhb', hsv(26, 33, 84))
    s = screen(ph + tool_sliders([('色相', 0.5), ('饱和度', 0.56), ('亮度', 0.53)], hl='饱和度'), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += lbl(560, 110, '饱和度：从中间往右一点点', YEL1, 13)
    s += lbl(560, 142, '亮度：需要时再往右一点', YEL1, 13)
    s += lbl(560, 174, '色相：一般不动', WHITE, 13)
    s += lbl(560, 218, '每拉一次就取色复查', YEL1, 13)
    s += note('示意图，滑块数值以实际界面为准')
    save('u-hsb-adjust', svg(W, H, s, '色相、饱和度和亮度：补回饱和度'))


def u_mask_skin():
    ph, g = photo_skin(CX, CY, CW, CH, 'ums', hsv(25, 33, 86))
    fp = face_path(g)
    hint = f'<path d="{fp}" fill="none" stroke="{WHITE}" stroke-width="3" stroke-dasharray="6 5"/>'
    rows = [('图层蒙版', '#FFFFFF', 'N', True), ('肤色调整', hsv(25, 33, 86), 'N', False), ('原图', SKIN_YG, 'N', False)]
    lay = layer_rows(560, 220, 210, rows)
    s = screen(ph + hint + lay, active='brush')
    s += ring(*icon_pos('brush'), 18) + badge(icon_pos('brush')[0] - 26, 62, 2)
    s += badge(560 + 24, 220 + 44 + 8, 1)
    s += lbl(560, 110, '① 图层选项里点「蒙版」', YEL1, 12)
    s += lbl(560, 142, '② 蒙版先填满黑色（全藏）', YEL1, 12)
    s += lbl(560, 174, '③ 白色软画笔只涂皮肤', YEL1, 12)
    s += lbl(36, 520, '白色虚线：涂的范围（脸、脖子、手），头发、衣服、背景不涂', WHITE, 13)
    s += note('示意图')
    save('u-mask-skin', svg(W, H, s, '用蒙版让调整只作用在皮肤上'))


def u_color_layer():
    pats = [([(-0.62, -0.02), (-0.2, -0.02), (-0.25, 0.1), (-0.6, 0.1)], hsv(290, 14, 60), 0.8), ([(0.6, -0.02), (0.2, -0.02), (0.25, 0.1), (0.6, 0.1)], hsv(290, 14, 55), 0.8)]
    ph, g = photo_skin(CX, CY, CW, CH, 'ucl', SKIN_OK, pats)
    rows = [('肤色统一', hsv(22, 45, 70), 'Co', True), ('原图', SKIN_OK, 'N', False)]
    lay = layer_rows(560, 300, 210, rows)
    bx, by = P(g, -0.4, 0.04)
    brush = f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="16" fill="none" stroke="{WHITE}" stroke-width="2.5"/><circle cx="{bx:.1f}" cy="{by:.1f}" r="16" fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3"/>'
    s = screen(ph + lay + brush, active='brush')
    s += ring(*icon_pos('brush'), 18) + ring(756, 34, 17)
    s += ring(560 + 210 - 46, 300 + 44 + 23, 15) + badge(560 + 210 - 46, 300 + 44 - 8, 1)
    s += ringrect(28, 298, 22, 92, 6) + badge(64, 344, 3)
    s += badge(756 - 26, 62, 2)
    s += lbl(560, 110, '① 新图层，混合模式「颜色」', YEL1, 12)
    s += lbl(560, 142, '② 当前颜色：在干净的暗部取色', YEL1, 12)
    s += lbl(560, 174, '③ 软画笔，不透明度 20%～40%', YEL1, 12)
    s += lbl(560, 206, '在发青的地方轻轻涂', YEL1, 12)
    s += note('示意图，以实际界面为准')
    save('u-color-layer', svg(W, H, s, '颜色混合模式图层：只换颜色，不改明暗'))


# ---------- 3.3 案例 ----------
def case_skin(kind, after):
    Wd, Hd = 640, 520
    if kind == 'yellow':
        sk = SKIN_OK if after else SKIN_YG
        pats = ()
        bg = '#5B6170'
        cap = '修之后：H24 S34 B88，干净、有血色' if after else '修之前：H37 S21 B76，偏黄发灰'
        tagc = sk
    else:
        sk = SKIN_OK
        under_c = hsv(20, 40, 66) if after else hsv(290, 14, 58)
        jaw_c = hsv(22, 46, 62) if after else hsv(250, 12, 56)
        pats = [([(-0.62, -0.02), (-0.2, -0.02), (-0.25, 0.12), (-0.6, 0.12)], under_c, 0.75), ([(0.62, -0.02), (0.2, -0.02), (0.25, 0.12), (0.6, 0.12)], under_c, 0.75),
                ([(0.5, 0.35), (0.85, 0.25), (0.6, 0.85), (0.25, 0.92)], jaw_c, 0.75)]
        bg = '#1E3A5F'
        cap = '修之后：暗部回到 H20 左右，青紫消失' if after else '修之前：蓝色背景灯反到脸上，眼下和下颌发青紫'
        tagc = under_c
    s = [f'<rect x="20" y="20" width="600" height="480" fill="{bg}"/>']
    fb, g = skin_face(320, 250, 250, 320, f'ck{kind}{int(after)}', sk, pats, hair='#2F3347')
    s.append(fb)
    s.append(f'<path d="M80 500 Q140 420 320 420 Q500 420 560 500 Z" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
    if kind == 'yellow':
        x, y = P(g, -0.5, 0.22)
    else:
        x, y = P(g, -0.42, 0.1)
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="none" stroke="{WHITE}" stroke-width="3"/>')
    s.append(swatch(540, 400, tagc, 60, 40))
    s.append(text(570, 462, hsb_cap(tagc), 11.5, 800, WHITE, 'middle'))
    s.append(lbl(40, 56, cap, VIO1 if after else YEL1, 14))
    return svg(Wd, Hd, ''.join(s), cap)



def part4():
    for f in [p_heads, p_male_female, p_real_anime, p_limit, case_angles, case_pitfall, u_guide_edit, u_landmarks]:
        f()
    save('case-target-before', case_target(False)); save('case-target-after', case_target(True))



# =====================================================================
# 3.4 人体比例
# =====================================================================
def proportions(n, gender='f', style='real', crotch=None):
    """返回关键分界点（单位：头长，从头顶算起）和宽度"""
    if style == 'anime':
        crotch = {6: 3.0, 9: 4.1}.get(n, n * 0.46)
    elif crotch is None:
        crotch = n * 0.5
    chest = 2.0 if n >= 7 else 1.8
    navel = crotch - (0.78 if n >= 7 else 0.6)
    L = dict(chin=1.0, shoulder=1.33 if n >= 7 else 1.25, chest=chest, navel=navel, waist=navel - 0.15, crotch=crotch,
             knee=crotch + (n - crotch) * 0.5, ankle=n - 0.22, sole=n, elbow=navel - 0.05, wrist=crotch, finger=crotch + 0.72)
    if gender == 'm':
        L.update(sh_w=1.9, waist_w=1.12, hip_w=1.3, neck_w=0.46, head_w=0.8, thigh=0.62, calf=0.36)
    else:
        L.update(sh_w=1.55, waist_w=0.92, hip_w=1.52, neck_w=0.32, head_w=0.74, thigh=0.62, calf=0.33)
        L['waist'] = navel - 0.3   # 女性腰线略高
    if style == 'anime' and n < 7:
        L.update(sh_w=L['sh_w'] * 0.85, waist_w=L['waist_w'] * 0.85, hip_w=L['hip_w'] * 0.85)
    if style == 'anime':
        L.update(head_w=0.82, neck_w=L['neck_w'] * 0.8, calf=L['calf'] * 0.85, thigh=L['thigh'] * 0.9)
    return L


def body(cx, top, hl, n, gender='f', style='real', warp=None, fill=SKIN, sw=2.5, cloth=None, crotch=None):
    """简笔人体。warp(u, v) -> (x, y)，u 横向头长（以中线为 0），v 纵向头长。默认是正常比例。"""
    L = proportions(n, gender, style, crotch)
    if warp is None:
        warp = lambda u, v: (cx + u * hl, top + v * hl)
    W_ = lambda pts: ' '.join('%.1f,%.1f' % warp(u, v) for u, v in pts)
    s = []
    sh, ws, hp = L['sh_w'] / 2, L['waist_w'] / 2, L['hip_w'] / 2
    # 腿
    for sg in (-1, 1):
        th, cf = L['thigh'], L['calf']
        leg = [(sg * 0.04, L['crotch']), (sg * (hp - 0.02), L['crotch'] - 0.3), (sg * (hp - 0.06), L['crotch'] + 0.25),
               (sg * (cf + 0.1), L['knee']), (sg * (cf + 0.12), L['knee'] + 0.6), (sg * 0.26, L['ankle']),
               (sg * 0.12, L['ankle']), (sg * 0.08, L['knee'] + 0.5), (sg * 0.06, L['knee']), (sg * 0.06, L['crotch'] + 0.2)]
        s.append(f'<polygon points="{W_(leg)}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
        foot = [(sg * 0.1, L['ankle']), (sg * 0.3, L['ankle']), (sg * 0.46, L['sole']), (sg * 0.06, L['sole'])]
        s.append(f'<polygon points="{W_(foot)}" fill="{INK}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    # 躯干
    torso = [(-L['neck_w'] / 2, L['chin'] + 0.12), (-sh, L['shoulder']), (-sh + 0.08, L['chest']), (-ws, L['waist']), (-hp, L['crotch'] - 0.3),
             (-0.04, L['crotch']), (0.04, L['crotch']), (hp, L['crotch'] - 0.3), (ws, L['waist']), (sh - 0.08, L['chest']), (sh, L['shoulder']), (L['neck_w'] / 2, L['chin'] + 0.12)]
    s.append(f'<polygon points="{W_(torso)}" fill="{cloth or fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    # 手臂
    for sg in (-1, 1):
        arm = [(sg * (sh - 0.02), L['shoulder'] - 0.02), (sg * (sh + 0.2), L['shoulder'] + 0.25), (sg * (sh + 0.12), L['elbow']), (sg * (sh + 0.04), L['wrist']),
               (sg * (sh - 0.06), L['finger']), (sg * (sh - 0.2), L['wrist']), (sg * (sh - 0.08), L['elbow']), (sg * (sh - 0.12), L['shoulder'] + 0.4)]
        s.append(f'<polygon points="{W_(arm)}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    # 脖子和头
    nk = [(-L['neck_w'] / 2, L['chin'] - 0.1), (L['neck_w'] / 2, L['chin'] - 0.1), (L['neck_w'] / 2, L['shoulder'] - 0.08), (-L['neck_w'] / 2, L['shoulder'] - 0.08)]
    s.append(f'<polygon points="{W_(nk)}" fill="{fill}" stroke="{INK}" stroke-width="{sw}"/>')
    head = [(math.cos(a) * L['head_w'] / 2, 0.5 + math.sin(a) * 0.5 * (1 if math.sin(a) < 0 else 1)) for a in [i * math.pi / 18 for i in range(36)]]
    head = [(u * (0.82 if v > 0.75 else 1), v) for u, v in head]
    s.append(f'<polygon points="{W_(head)}" fill="{fill}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    hair = [(-L['head_w'] / 2 - 0.04, 0.55), (-L['head_w'] / 2, 0.15), (0, -0.04), (L['head_w'] / 2, 0.15), (L['head_w'] / 2 + 0.04, 0.55), (0.1, 0.25), (-0.2, 0.3)]
    if gender == 'f':
        hair = [(-L['head_w'] / 2 - 0.06, 1.15), (-L['head_w'] / 2 - 0.04, 0.2), (0, -0.05), (L['head_w'] / 2 + 0.04, 0.2), (L['head_w'] / 2 + 0.06, 1.15), (L['head_w'] / 2 - 0.06, 0.6), (0.1, 0.25), (-L['head_w'] / 2 + 0.06, 0.6)]
    s.append(f'<polygon points="{W_(hair)}" fill="{PINK if gender == "f" else "#475569"}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    return ''.join(s), L


def head_lines(x0, x1, top, hl, n, color=MUTED, numbers=True, nx=None, warpy=None):
    s = []
    k = 0
    while k <= n + 1e-6:
        y = warpy(k) if warpy else top + k * hl
        s.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{color}" stroke-width="1.5" stroke-dasharray="5 5"/>')
        if numbers and k + 1 <= n + 1e-6:
            y2 = warpy(k + 0.5) if warpy else top + (k + 0.5) * hl
            s.append(text(nx if nx is not None else x0 - 12, y2 + 5, str(k + 1), 13, 800, INK, 'end'))
        k += 1
    return ''.join(s)


def p_heads():
    Wd, Hd = 760, 640
    s = [box(20, 10, 720, 620, '成年女性约 7.5 头身：身体上的分界点')]
    hl, top, cx = 66, 66, 400
    n = 7.5
    s.append(head_lines(170, 548, top, hl, n, nx=160))
    fig, L = body(cx, top, hl, n, 'f', cloth=VIO2)
    s.append(fig)
    marks = [('下巴', 'chin', '1 头'), ('胸线', 'chest', '2 头'), ('肚脐', 'navel', '约 3 头'), ('腿根', 'crotch', '约 3.75 头（身高一半）'), ('膝盖', 'knee', '约 5.6 头'), ('脚底', 'sole', '7.5 头')]
    for nm, k, d in marks:
        y = top + L[k] * hl
        s.append(f'<line x1="{cx + 30}" y1="{y:.1f}" x2="{552}" y2="{y:.1f}" stroke="{RED}" stroke-width="2.5"/>')
        s.append(lbl(558, y + 6, nm, RED1, 13) + text(606, y + 6, d, 12, 700, MUTED))
    arms = [('手肘 ≈ 腰', 'elbow'), ('手腕 ≈ 腿根', 'wrist'), ('指尖 ≈ 大腿中段', 'finger')]
    for nm, k in arms:
        y = top + L[k] * hl
        x = cx - (L['sh_w'] / 2 + 0.1) * hl
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{VIO7}"/>' + f'<line x1="{x:.1f}" y1="{y:.1f}" x2="306" y2="{y:.1f}" stroke="{VIO7}" stroke-width="2"/>')
        s.append(lbl(302, y + 6, nm, VIO1, 13, 'end'))
    s.append(text(40, 610, '数字是平均值，每个人会差 0.2～0.3 头；衣服挡住时，用手肘、手腕的位置帮忙找腰和腿根', 12.5, 700, INK))
    save('p-heads', svg(Wd, Hd, ''.join(s), '7.5 头身和身体分界点'))


def width_arrow(x1, x2, y, lab, col=INK):
    return (f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{col}" stroke-width="2.5" marker-start="url(#arw)" marker-end="url(#arw)"/>'
            + text((x1 + x2) / 2, y - 8, lab, 12, 800, col, 'middle'))


def p_male_female():
    Wd, Hd = 760, 640
    s = [box(20, 10, 360, 620, '女性：约 7～7.5 头', PINK1), box(400, 10, 340, 620, '男性：约 7.5～8 头', '#E0E7FF')]
    hlf, hlm = 64, 60
    for cx, hl, n, g_ in [(200, hlf, 7.5, 'f'), (570, hlm, 8, 'm')]:
        top = 62
        s.append(head_lines(cx - 140, cx + 140, top, hl, n, nx=cx - 146))
        fig, L = body(cx, top, hl, n, g_, cloth=VIO2 if g_ == 'f' else '#A5B4FC')
        s.append(fig)
        sh = L['sh_w'] / 2 * hl; hp = L['hip_w'] / 2 * hl; ws = L['waist_w'] / 2 * hl
        ya = top + L['shoulder'] * hl - 6
        s.append(f'<line x1="{cx - sh:.1f}" y1="{ya:.1f}" x2="{cx + sh:.1f}" y2="{ya:.1f}" stroke="{INK}" stroke-width="2.5" marker-start="url(#arw)" marker-end="url(#arw)"/>' + text(cx + sh + 10, ya + 5, f'肩宽 {L["sh_w"]} 头', 12, 800, INK))
        s.append(width_arrow(cx - ws, cx + ws, top + L['waist'] * hl, f'腰 {L["waist_w"]}', VIO7))
        s.append(width_arrow(cx - hp, cx + hp, top + (L['crotch'] - 0.3) * hl + 4, f'胯 {L["hip_w"]}', RED7))
    s.append(text(40, 596, '肩和胯差不多宽，腰细、腰线高', 13, 800, INK) + text(40, 616, '脖子细长，大腿外侧更圆', 12.5, 600, MUTED))
    s.append(text(420, 596, '肩明显比胯宽，像倒三角', 13, 800, INK) + text(420, 616, '脖子粗，腰线低一点，上半身略长', 12.5, 600, MUTED))
    save('p-male-female', svg(Wd, Hd, ''.join(s), '男女比例的区别'))


def p_real_anime():
    Wd, Hd = 760, 600
    s = [box(20, 10, 720, 580, '同样身高画出来：二次元多出来的长度几乎都加在腿上')]
    H_ = 420; top = 70
    items = [(7, 'f', 'real', '真人常见', '7 头'), (8, 'f', 'real', '真人模特', '8 头'), (6, 'f', 'anime', '二次元少女', '6 头'), (9, 'f', 'anime', '二次元成人', '9 头')]
    for i, (n, g_, st, nm, hh) in enumerate(items):
        cx = 120 + i * 172
        hl = H_ / n
        fig, L = body(cx, top, hl, n, g_, st, cloth=VIO2 if st == 'real' else '#F9A8D4')
        s.append(fig)
        yc = top + L['crotch'] * hl
        s.append(f'<line x1="{cx - 60}" y1="{yc:.1f}" x2="{cx + 60}" y2="{yc:.1f}" stroke="{RED}" stroke-width="2.5" stroke-dasharray="6 4"/>')
        leg = (n - L['crotch']) / n * 100
        s.append(text(cx, top + H_ + 34, f'{nm}  {hh}', 14, 800, INK, 'middle'))
        s.append(text(cx, top + H_ + 56, f'腿长占身高 {leg:.0f}%', 12.5, 700, RED7, 'middle'))
        s.append(text(cx, top + H_ + 76, f'头占身高 {100 / n:.0f}%', 12.5, 600, MUTED, 'middle'))
    s.append(f'<line x1="40" y1="{top}" x2="720" y2="{top}" stroke="{MUTED}" stroke-width="1.5"/><line x1="40" y1="{top + H_}" x2="720" y2="{top + H_}" stroke="{MUTED}" stroke-width="1.5"/>')
    s.append(lbl(708, top - 8, '红虚线：腿根', RED1, 12, 'end'))
    save('p-real-anime', svg(Wd, Hd, ''.join(s), '真人比例和二次元比例'))


def p_limit():
    Wd, Hd = 760, 250
    s = [box(20, 10, 720, 230, 'cos 后期往角色比例靠：能走多远')]
    x0, x1, y = 70, 690, 130
    lo, hi = 6, 9.5
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    s.append(f'<rect x="{X(7.5):.1f}" y="{y - 14}" width="{X(8.2) - X(7.5):.1f}" height="28" rx="6" fill="{MINT1}" stroke="{MINT7}" stroke-width="2"/>')
    s.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{INK}" stroke-width="3"/>')
    for v in [6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5]:
        s.append(f'<line x1="{X(v):.1f}" y1="{y - 8}" x2="{X(v):.1f}" y2="{y + 8}" stroke="{INK}" stroke-width="2"/>' + text(X(v), y + 30, f'{v:g}', 13, 800, INK, 'middle'))
    s.append(f'<circle cx="{X(6.9):.1f}" cy="{y}" r="9" fill="{YEL}" stroke="{INK}" stroke-width="2.5"/>' + lbl(X(6.9), y - 24, '原片 6.9', YEL1, 12, 'middle'))
    s.append(arrow(X(6.9) + 10, y + 50, X(7.5) - 4, y + 50, MINT7, 3))
    s.append(text((X(6.9) + X(7.5)) / 2, y + 72, '后期最多 +0.5～0.7 头', 12.5, 800, MINT7, 'middle'))
    s.append(lbl(X(7.85), y - 24, '真人好看的区间', MINT1, 12, 'middle'))
    s.append(f'<circle cx="{X(9):.1f}" cy="{y}" r="9" fill="{PINK}" stroke="{INK}" stroke-width="2.5"/>' + lbl(X(9), y - 24, '角色设定 9', PINK1, 12, 'middle'))
    s.append(text(X(9), y + 56, '靠不到，也不用靠', 12.5, 700, RED7, 'middle'))
    s.append(text(40, 228, '来源：腿拉长 15% 约 +0.4 头，头缩小 5% 约 +0.3 头（见 5.4 课）。再多膝盖位置、上下身比例就会露馅。', 12, 600, MUTED))
    save('p-limit', svg(Wd, Hd, ''.join(s), '后期往角色比例靠的上限'))


def angle_warp(cx, top, hl, kind):
    """俯拍：上大下小；仰拍：上小下大。返回 warp 和 y 映射（头长 → 像素）"""
    a = {'flat': 0.0, 'high': 0.036, 'low': -0.03}[kind]   # 每往下一头，尺寸变化的比例
    sc = lambda v: 1 - a * v
    Y = lambda v: top + hl * (v - a * v * v / 2)
    return (lambda u, v: (cx + u * hl * sc(v), Y(v))), Y


def angle_photo(x, y, w, h, kind, cid, show=True):
    n = 7.4
    a = {'flat': 0.0, 'high': 0.036, 'low': -0.03}[kind]
    hl = (h - 40) / (n - a * n * n / 2)
    top = y + 20
    warp, Y = angle_warp(x + w / 2 - 10, top, hl, kind)
    fig, L = body(x + w / 2 - 10, top, hl, n, 'f', warp=warp, cloth=VIO2)
    feet = Y(n)
    s = [f'<defs><clipPath id="ap{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#ap{cid})">',
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFF7E6"/>', f'<rect x="{x}" y="{feet:.1f}" width="{w}" height="{y + h - feet:.1f}" fill="{FLOOR}"/>']
    for sg in (-1, 1):
        u = sg * 1.75
        x_t, y_t = warp(u, -1.0); x_b, y_b = warp(u, n)
        s.append(f'<line x1="{x_t:.1f}" y1="{y_t:.1f}" x2="{x_b:.1f}" y2="{y_b:.1f}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<line x1="{x}" y1="{feet:.1f}" x2="{x + w}" y2="{feet:.1f}" stroke="{INK}" stroke-width="2"/>')
    s.append(fig)
    head_px = Y(1) - Y(0)
    ratio = (feet - top) / head_px
    if show:
        s.append(ruler(x + w - 26, top, head_px, ratio, w=14, numbers=False))
    s.append('</g>' + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>')
    return ''.join(s), ratio


def case_angles():
    Wd, Hd = 760, 560
    s = [box(20, 10, 720, 540, '同一个人、同一身衣服，三个角度量出来的头身比')]
    caps = [('high', '俯拍（镜头举过头顶）'), ('flat', '平拍（镜头在腰部）'), ('low', '仰拍（镜头在膝盖）')]
    for i, (k, nm) in enumerate(caps):
        x = 40 + i * 232
        ph, r = angle_photo(x, 54, 216, 400, k, k)
        s.append(ph)
        s.append(text(x + 108, 478, nm, 13.5, 800, INK, 'middle'))
        s.append(text(x + 108, 502, f'量出来约 {r:.1f} 头', 14, 800, RED7 if k == 'high' else (MINT7 if k == 'flat' else VIO7), 'middle'))
    s.append(text(40, 532, '俯拍：头大、脚小、竖线往下收　平拍：最接近真实　仰拍：腿长头小，竖线往上收，下巴、鼻孔显眼', 12.5, 700, MUTED))
    save('case-angles', svg(Wd, Hd, ''.join(s), '俯拍、平拍、仰拍量出的头身比'))


def case_target(after):
    Wd, Hd = 640, 520
    s = [f'<rect x="20" y="20" width="600" height="480" fill="#FFF7E6"/>', door(60, 70, 120, 470)]
    s.append(f'<rect x="20" y="470" width="600" height="30" fill="{FLOOR}"/><line x1="20" y1="470" x2="620" y2="470" stroke="{INK}" stroke-width="2.5"/>')
    hl0 = 390 / 6.9
    torso, legs = 3.55, 3.35            # 修之前：单位是原来的头长
    if after:
        legs *= 1.1                     # 腿拉长 10%
        hl = hl0 * 0.97                 # 头缩 3%
    else:
        hl = hl0
    total_px = (torso + legs) * hl0
    n = total_px / hl
    top = 470 - total_px
    fig, L = body(360, top, hl, n, 'f', cloth=VIO2, crotch=torso * hl0 / hl)
    s.append(fig)
    s.append(ruler(540, top, hl, n, numbers=False))
    lab = '修之后：腿拉长约 10%、头缩 3%，约 7.5 头' if after else '修之前：平拍，约 6.9 头，角色设定是 9 头'
    s.append(lbl(34, 494, lab, VIO1 if after else YEL1, 14))
    return svg(Wd, Hd, ''.join(s), lab)


def case_pitfall():
    Wd, Hd = 760, 570
    s = [box(20, 10, 720, 550, '假发蓬、穿厚底鞋时怎么量')]
    hl = 50; top = 112; cx = 380; n = 7.2
    fig, L = body(cx, top, hl, n, 'f', cloth=VIO2)
    s.append(f'<ellipse cx="{cx}" cy="{top + hl * 0.35:.1f}" rx="{hl * 0.75:.1f}" ry="{hl * 0.62:.1f}" fill="{PINK}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(fig)
    for sg in (-1, 1):
        s.append(f'<rect x="{cx + sg * 0.27 * hl - 0.24 * hl:.1f}" y="{top + n * hl - 2:.1f}" width="{0.48 * hl:.1f}" height="{0.3 * hl:.1f}" rx="4" fill="{INK}"/>')
    sole = top + (n + 0.3) * hl
    s.append(f'<line x1="60" y1="{sole:.1f}" x2="700" y2="{sole:.1f}" stroke="{INK}" stroke-width="2"/>')
    wig_top = top + hl * 0.35 - hl * 0.62
    wrong_h = (top + hl) - wig_top
    s.append(f'<line x1="200" y1="{wig_top:.1f}" x2="{cx}" y2="{wig_top:.1f}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>')
    s.append(ruler(200, wig_top, wrong_h, (sole - wig_top) / wrong_h, w=16, numbers=False))
    s.append(lbl(60, wig_top - 14, f'错：从假发顶量 → {(sole - wig_top) / wrong_h:.1f} 头', RED1, 12.5))
    s.append(f'<line x1="{cx}" y1="{top:.1f}" x2="560" y2="{top:.1f}" stroke="{MINT7}" stroke-width="2" stroke-dasharray="5 4"/>')
    s.append(ruler(560, top, hl, (sole - top) / hl, w=16, numbers=False))
    s.append(lbl(470, top - 30, f'对：从头骨顶量 → {(sole - top) / hl:.1f} 头', MINT1, 12.5))
    s.append(lbl(cx + 40, sole - 4, '厚底约 0.3 头', YEL1, 12))
    s.append(text(40, 528, '头顶：按头骨找（发际线往上约一个额头高），蓬起来的假发、头饰、呆毛都不算', 12.5, 700, INK))
    s.append(text(40, 548, '脚底：量到鞋底，但记住厚底鞋让数字多了 0.2～0.4 头，和光脚的比例比较时要减掉', 12.5, 600, MUTED))
    save('case-pitfall', svg(Wd, Hd, ''.join(s), '假发和厚底鞋对头身比测量的影响'))


# ---------- 3.4 界面 ----------
def u_guide_edit():
    x, y, w, h = 262, 66, 276, 380
    top = y + 20
    hl = 44
    ph = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFF7E6"/>'
    fig, L = body(x + w / 2, top, hl, 7.4, 'f', cloth=VIO2)
    ph += fig + f'<line x1="{x}" y1="{top + 7.4 * hl:.1f}" x2="{x + w}" y2="{top + 7.4 * hl:.1f}" stroke="{INK}" stroke-width="2"/>'
    grid = ''
    yy = top
    while yy < y + h:
        grid += f'<line x1="{x}" y1="{yy:.1f}" x2="{x + w}" y2="{yy:.1f}" stroke="{UIBLUE}" stroke-width="1.5"/>'
        yy += hl
    xx = x + w / 2 - hl * 3
    while xx < x + w:
        if xx > x:
            grid += f'<line x1="{xx:.1f}" y1="{y}" x2="{xx:.1f}" y2="{y + h}" stroke="{UIBLUE}" stroke-width="1.5" stroke-opacity=".6"/>'
        xx += hl
    node = f'<circle cx="{x + w / 2:.1f}" cy="{top:.1f}" r="8" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2.5"/><circle cx="{x + w / 2 + hl:.1f}" cy="{top:.1f}" r="7" fill="{MINT}" stroke="{WHITE}" stroke-width="2.5"/>'
    s = [f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>', ph, grid, node]
    s.append(f'<rect x="{SX}" y="{SY}" width="{SW}" height="42" rx="16" fill="{UIBAR}"/>' + text(40, 42, '取消', 15, 700, UITEXT) + text(SX + SW - 24, 42, '完成', 15, 800, UIBLUE, 'end'))
    st = ''.join(f'<stop offset="{k / 6:.3f}" stop-color="{hsv(k * 60, 100, 100)}"/>' for k in range(7))
    s.append(f'<defs><linearGradient id="gdh">{st}</linearGradient></defs><rect x="250" y="28" width="300" height="12" rx="6" fill="url(#gdh)"/>')
    by = SY + SH - 122
    s.append(f'<rect x="60" y="{by}" width="680" height="94" rx="14" fill="{UIBAR}"/>')
    sl = [('不透明度', 0.7), ('粗细度', 0.3), ('网格尺寸', 0.45)]
    for i, (nm, f) in enumerate(sl):
        sx = 84 + i * 160
        s.append(slider(sx, by + 34, 130, nm, f, hl=(nm == '网格尺寸')))
    s.append(f'<rect x="{84 + 2 * 160 + 40}" y="{by + 48}" width="70" height="22" rx="5" fill="{UIPANEL}"/>' + text(84 + 2 * 160 + 75, by + 64, '206 px', 12, 700, UITEXT, 'middle'))
    s.append(text(580, by + 30, '辅助绘图', 13, 700, UITEXT) + f'<rect x="660" y="{by + 16}" width="40" height="20" rx="10" fill="#6B7280"/><circle cx="672" cy="{by + 26}" r="8" fill="{WHITE}"/>')
    modes = ['2D 网格', '等距', '透视', '对称']
    mx = 160
    for m in modes:
        mw = len(m) * 15 + 20
        s.append(f'<rect x="{mx}" y="{by + 60}" width="{mw}" height="28" rx="8" fill="{UIBLUE if m == "2D 网格" else UIPANEL}"/>' + text(mx + mw / 2, by + 79, m, 13, 700, UITEXT, 'middle'))
        if m == '2D 网格':
            s.append(ringrect(mx - 3, by + 57, mw + 6, 34))
            bx2 = mx
        mx += mw + 8
    s.append(badge(bx2 - 14, by + 74, 1) + badge(84 + 2 * 160 + 140, by + 10, 2) + badge(x + w / 2 - 24, top - 4, 3))
    s.append(ring(SX + SW - 40, 36, 22) + badge(SX + SW - 76, 62, 4))
    s.append(lbl(560, 120, '① 底部选「2D 网格」', YEL1, 13))
    s.append(lbl(560, 152, '② 网格尺寸调到一格＝一个头长', YEL1, 13))
    s.append(lbl(560, 184, '③ 拖蓝色节点，让横线对齐头顶', YEL1, 13))
    s.append(lbl(560, 216, '④ 点「完成」', YEL1, 13))
    s.append(note('示意图，按钮位置以实际界面为准'))
    save('u-guide-edit', svg(W, H, ''.join(s), '编辑绘图指引：2D 网格，一格一个头长'))


def u_landmarks():
    x, y, w, h = 262, 66, 276, 400
    top = y + 20; hl = 46; n = 7.4
    ph = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFF7E6"/>'
    fig, L = body(x + w / 2 - 20, top, hl, n, 'f', cloth=VIO2)
    ph += fig
    lines = ''
    for nm, k in [('下巴', 'chin'), ('胸线', 'chest'), ('肚脐', 'navel'), ('腿根', 'crotch'), ('膝盖', 'knee'), ('脚底', 'sole')]:
        yy = top + L[k] * hl
        lines += f'<line x1="{x + 30}" y1="{yy:.1f}" x2="{x + w - 10}" y2="{yy:.1f}" stroke="{MINT}" stroke-width="3"/>' + text(x + w - 12, yy - 5, nm, 12, 800, MINT7, 'end')
    mid = top + n * hl / 2
    lines += f'<line x1="{x + 10}" y1="{mid:.1f}" x2="{x + w - 10}" y2="{mid:.1f}" stroke="{RED}" stroke-width="2" stroke-dasharray="6 4"/>' + text(x + 14, mid - 6, '身高一半', 12, 800, RED7)
    lay = layer_rows(560, 300, 210, [('分界点', MINT, 'N', True), ('头身标尺', MINT1, 'N', False), ('原图', '#FFF7E6', 'N', False)])
    s = screen(ph + lines + lay, active='brush')
    s += ring(*icon_pos('brush'), 18) + badge(icon_pos('brush')[0] - 26, 62, 1)
    s += lbl(560, 96, '① 新图层「分界点」，技术笔', YEL1, 12)
    s += lbl(560, 128, '② 在每个分界点画一条横线', YEL1, 12)
    s += lbl(560, 160, '   画完停住，自动拉直', WHITE, 12)
    s += lbl(560, 192, '③ 再画一条"身高一半"', YEL1, 12)
    s += lbl(560, 224, '   看腿根在它上面还是下面', WHITE, 12)
    s += note('示意图')
    save('u-landmarks', svg(W, H, s, '在新图层上画出身体分界点'))


if __name__ == '__main__':
    parts = [a for a in sys.argv[1:]] or ['part1', 'part2', 'part3', 'part4']
    for p_ in parts:
        globals()[p_]()
    print('done', len(os.listdir(OUT)))
