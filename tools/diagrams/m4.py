"""M4 人像基础修图 的示意图。运行：python tools/diagrams/m4.py
人物和界面都是简笔示意，不是真实截图。"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'diagrams', 'm4')
os.makedirs(OUT, exist_ok=True)


_LABELS = []
_kit_label = label


def label(x, y, s, fill=YEL1, size=15, anchor='start', stroke=INK):
    w = sum(1.0 if ord(c) > 255 else 0.58 for c in s) * size + 18
    x0 = x - (w / 2 if anchor == 'middle' else (w if anchor == 'end' else 0))
    _LABELS.append((x0, x0 + w, s))
    return _kit_label(x, y, s, fill, size, anchor, stroke)


def save(name, s):
    import re as _re
    vw = float(_re.search(r'viewBox="0 0 ([\d.]+)', s).group(1))
    lim = vw - 22 if vw == W else vw - 4
    for a, b, t in _LABELS:
        if b > lim or a < 4:
            print('OVERFLOW', name, round(a), round(b), t)
    _LABELS.clear()
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)


HAIR = '#F472B6'; HAIR7 = '#DB2777'; BROW = '#8A4B5C'; LIP = '#E0607A'; LIPPALE = '#E8B4AE'
SKIN2 = '#E9B99C'; SKIN3 = '#D79C7E'; ACNE = '#E0645A'; MARK = '#C98A7A'
NS = 'vector-effect="non-scaling-stroke"'


def E(cx, cy, rx, ry, fill, op=1.0, rot=0, extra=''):
    r = f' transform="rotate({rot} {cx} {cy})"' if rot else ''
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" fill-opacity="{op}"{r} {extra}/>'


def P(d, fill='none', stroke=INK, sw=2, op=1.0, extra=''):
    return f'<path d="{d}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {NS} {extra}/>'


FACE = ('M0,-1.25 C0.6,-1.25 0.98,-0.9 0.98,-0.3 C0.98,0.25 0.85,0.6 0.5,0.88 C0.3,1.0 0.12,1.03 0,1.03 '
        'C-0.12,1.03 -0.3,1.0 -0.5,0.88 C-0.85,0.6 -0.98,0.25 -0.98,-0.3 C-0.98,-0.9 -0.6,-1.25 0,-1.25 Z')
BANGS = ('M-1.02,-0.25 C-1.12,-1.3 -0.3,-1.48 0.2,-1.34 C0.9,-1.26 1.16,-0.8 1.02,-0.2 C0.92,-0.55 0.72,-0.72 0.47,-0.64 '
         'C0.3,-0.78 0.1,-0.8 -0.05,-0.64 C-0.3,-0.78 -0.6,-0.72 -0.76,-0.52 C-0.86,-0.46 -0.95,-0.36 -1.02,-0.25 Z')
EYE = 'M0.2,-0.15 Q0.39,-0.31 0.6,-0.17 Q0.4,-0.03 0.2,-0.15 Z'


def eye(side, uid, s, dy=0.0, sc=1.0, liner=True, liner_bad=False, iris=VIO):
    """side=1 画面右边那只眼，-1 左边。单位坐标。"""
    cx, cy = 0.395, -0.16
    tf = f'translate({side * cx},{cy + dy}) scale({side * sc},{sc}) translate({-cx},{-cy})'
    cid = f'{uid}-e{side + 1}'
    lw = (3.6 if liner else 2.2) * s / 60
    o = [f'<g transform="{tf}"><clipPath id="{cid}"><path d="{EYE}"/></clipPath>',
         f'<path d="{EYE}" fill="{WHITE}"/>',
         f'<g clip-path="url(#{cid})"><circle cx="{cx}" cy="{cy}" r="0.088" fill="{iris}"/><circle cx="{cx}" cy="{cy}" r="0.042" fill="{INK}"/>'
         f'<circle cx="{cx + 0.03}" cy="{cy - 0.03}" r="0.022" fill="{WHITE}"/></g>',
         P('M0.19,-0.15 Q0.39,-0.32 0.61,-0.18', stroke=INK, sw=lw)]
    if liner and not liner_bad:
        o.append(P('M0.58,-0.19 L0.7,-0.25', stroke=INK, sw=lw * 0.8))
    if liner_bad:
        o.append(E(0.6, -0.08, 0.07, 0.035, '#6B5B6B', 0.45))
    o.append(P('M0.24,-0.1 Q0.4,-0.04 0.56,-0.12', stroke=SKIN3, sw=1.2 * s / 60))
    o.append('</g>')
    return ''.join(o)


def portrait(x, y, w, h, uid='p', bg='venue', shade='3d', tilt=0, eye_dy=0.0, eye_sc=1.0, liner=True, liner_bad=False,
             lip=LIP, blush=False, contour=False, brows='full', blem=False, red=False, shine=False, pores=False,
             gray=False, flip=False, crowd=False, stray=False, bangs=True, cast=None, cast_t=0.0, expo=0.0,
             fx=None, fy=None, s=None, frame=True, iris=VIO, bgdark=False, skin=SKIN):
    """半身人像简笔画。返回 (svg, 几何)。几何：fx, fy 脸中心；s 半个脸宽（像素）。"""
    fx = x + w * 0.5 if fx is None else fx
    fy = y + h * 0.42 if fy is None else fy
    s = min(w * 0.2, h * 0.16) if s is None else s
    o = [f'<defs><clipPath id="{uid}-clip"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
         f'<filter id="{uid}-g"><feColorMatrix type="saturate" values="0"/></filter></defs>']
    gattr = f'clip-path="url(#{uid}-clip)"'
    o.append(f'<g {gattr}>')
    inner = f' filter="url(#{uid}-g)"' if gray else ''
    flipt = f' transform="translate({2 * x + w},0) scale(-1,1)"' if flip else ''
    o.append(f'<g{inner}><g{flipt}>')
    # 背景
    if bg == 'venue':
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{"#5B4B6B" if bgdark else "#F3E8D2"}"/>')
        o.append(f'<rect x="{x + w * 0.04:.1f}" y="{y + h * 0.08:.1f}" width="{w * 0.24:.1f}" height="{h * 0.5:.1f}" fill="{VIO1}" stroke="{INK}" stroke-width="1.5"/>')
        o.append(f'<rect x="{x + w * 0.74:.1f}" y="{y + h * 0.14:.1f}" width="{w * 0.24:.1f}" height="{h * 0.42:.1f}" fill="{MINT1}" stroke="{INK}" stroke-width="1.5"/>')
        for i in range(4):
            o.append(f'<circle cx="{x + w * (0.12 + i * 0.25):.1f}" cy="{y + h * 0.04:.1f}" r="{w * 0.025:.1f}" fill="{YEL}"/>')
    elif bg == 'outdoor':
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#CFEAF8"/>')
        for i, (a, b, r) in enumerate([(0.1, 0.62, 0.16), (0.3, 0.66, 0.14), (0.82, 0.6, 0.18), (0.98, 0.66, 0.14)]):
            o.append(f'<circle cx="{x + w * a:.1f}" cy="{y + h * b:.1f}" r="{w * r:.1f}" fill="#A7D9A2" stroke="{INK}" stroke-width="1.5"/>')
        o.append(f'<rect x="{x}" y="{y + h * 0.7:.1f}" width="{w}" height="{h * 0.3:.1f}" fill="#E7E1C8"/>')
    else:
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#EDE7F6"/>')
    if crowd:
        for a, b in [(0.12, 0.6), (0.9, 0.56)]:
            px, py = x + w * a, y + h * b
            o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{w * 0.06:.1f}" fill="#94A3B8"/>'
                     f'<rect x="{px - w * 0.1:.1f}" y="{py + w * 0.06:.1f}" width="{w * 0.2:.1f}" height="{h * 0.4:.1f}" rx="{w * 0.06:.1f}" fill="#94A3B8"/>')
    # 人物：单位坐标
    sk, sk2, sk3 = skin, SKIN2, SKIN3
    o.append(f'<g transform="translate({fx:.1f},{fy:.1f}) scale({s:.2f})">')
    head_rot = f'rotate({tilt} 0 1.0)'
    o.append(f'<g transform="{head_rot}">' + P('M-1.25,-0.3 C-1.42,-1.62 1.42,-1.62 1.25,-0.3 L1.38,1.95 L-1.38,1.95 Z', fill=HAIR, stroke=INK, sw=2) + '</g>')
    o.append(P('M-2.7,3.4 L-2.45,2.0 Q-1.6,1.58 -0.45,1.52 L0.45,1.52 Q1.6,1.58 2.45,2.0 L2.7,3.4 Z', fill=VIO2, stroke=INK, sw=2))
    o.append(P('M-0.36,0.7 L-0.36,1.56 Q0,1.78 0.36,1.56 L0.36,0.7 Z', fill=sk, stroke=INK, sw=2))
    o.append(P('M-0.45,1.52 L0,2.05 L0.45,1.52', fill=sk, stroke=INK, sw=2))
    if shade != 'flat':
        o.append(E(0, 0.98, 0.42, 0.2, INK, 0.2))
    o.append(f'<g transform="{head_rot}"><clipPath id="{uid}-face"><path d="{FACE}"/></clipPath>')
    o.append(P(FACE, fill=sk, stroke=INK, sw=2))
    o.append(f'<g clip-path="url(#{uid}-face)">')
    if shade == '3d':
        for a in (1, -1):
            o.append(E(a * 0.92, -0.55, 0.16, 0.32, INK, 0.12))
            o.append(E(a * 0.7, 0.32, 0.26, 0.09, INK, 0.12, rot=a * 28))
            o.append(E(a * 0.13, 0.08, 0.05, 0.22, INK, 0.1))
            o.append(E(a * 0.5, -0.02, 0.2, 0.07, WHITE, 0.5))
        o.append(E(0, -0.85, 0.32, 0.14, WHITE, 0.45))
        o.append(E(0.02, 0.05, 0.05, 0.26, WHITE, 0.55))
        o.append(E(0, 0.86, 0.15, 0.07, WHITE, 0.45))
        o.append(E(0, 1.05, 0.7, 0.1, INK, 0.12))
    elif shade == 'messy':
        o.append(f'<path d="M0.05,-1.4 L1.2,-1.4 L1.2,1.2 L0.05,1.2 Q0.18,0.5 0.05,-1.4 Z" fill="{INK}" fill-opacity="0.26"/>')
    elif shade == 'flash':
        o.append(E(0, -0.1, 0.8, 0.95, WHITE, 0.22))
    if pores:
        rnd = random.Random(7)
        for _ in range(70):
            a = rnd.uniform(-0.85, 0.85); b = rnd.uniform(-0.05, 0.65)
            if abs(a) < 0.25 and b < 0.5:
                continue
            o.append(f'<circle cx="{a:.3f}" cy="{b:.3f}" r="0.011" fill="{sk3}" fill-opacity=".55"/>')
    if red:
        for a in (1, -1):
            o.append(E(a * 0.2, 0.3, 0.13, 0.08, '#F08080', 0.4))
            o.append(E(a * 0.55, 0.18, 0.2, 0.12, '#F08080', 0.2))
    if blush:
        for a in (1, -1):
            o.append(E(a * 0.6, 0.2, 0.25, 0.13, PINK, 0.32))
    if contour:
        for a in (1, -1):
            o.append(E(a * 0.8, 0.34, 0.22, 0.09, '#8B5E4A', 0.25, rot=a * 28))
    if shine:
        o.append(E(0.12, -0.86, 0.13, 0.05, WHITE, 0.9))
        o.append(E(0.05, 0.24, 0.05, 0.035, WHITE, 0.9))
        for a in (1, -1):
            o.append(E(a * 0.48, 0.06, 0.07, 0.03, WHITE, 0.8))
    if blem:
        for (a, b) in [(0.48, 0.34), (0.62, 0.12), (-0.52, 0.42), (-0.3, -0.7), (0.22, 0.8), (-0.64, 0.06)]:
            o.append(f'<circle cx="{a}" cy="{b}" r="0.034" fill="{ACNE}"/><circle cx="{a - 0.01}" cy="{b - 0.01}" r="0.01" fill="{WHITE}" fill-opacity=".8"/>')
        for (a, b) in [(0.35, 0.5), (-0.4, 0.28), (0.7, 0.3)]:
            o.append(f'<circle cx="{a}" cy="{b}" r="0.04" fill="{MARK}" fill-opacity=".7"/>')
    o.append('</g>')
    # 五官
    bw = s * 0.075
    if brows != 'none':
        for a in (1, -1):
            d = f'M{a * 0.2},-0.36 Q{a * 0.48},-0.52 {a * 0.74},-0.41'
            if brows == 'sparse' and a == -1:
                o.append(P(d, stroke=BROW, sw=bw * 0.6, op=1, extra='stroke-dasharray="0.08 0.07" stroke-opacity=".55"'.replace('0.08 0.07', f'{s*0.05:.1f} {s*0.06:.1f}')))
            else:
                o.append(P(d, stroke=BROW, sw=bw))
    o.append(eye(1, uid, s, liner=liner, iris=iris))
    o.append(eye(-1, uid, s, dy=eye_dy, sc=eye_sc, liner=liner, liner_bad=liner_bad, iris=iris))
    o.append(P('M0.03,-0.05 L0.08,0.25', stroke=sk3, sw=s * 0.03))
    o.append(P('M-0.13,0.33 Q-0.06,0.39 0,0.36 Q0.06,0.39 0.13,0.33', stroke=sk3, sw=s * 0.03))
    o.append(P('M-0.24,0.6 Q-0.12,0.52 0,0.57 Q0.12,0.52 0.24,0.6 Q0,0.64 -0.24,0.6 Z', fill=lip, stroke=INK, sw=1.5))
    o.append(P('M-0.24,0.6 Q0,0.64 0.24,0.6 Q0.12,0.75 0,0.75 Q-0.12,0.75 -0.24,0.6 Z', fill=lip, stroke=INK, sw=1.5))
    if bangs:
        o.append(P(BANGS, fill=HAIR, stroke=INK, sw=2))
    if stray:
        for d in ['M-1.2,-0.9 Q-1.5,-1.1 -1.55,-1.45', 'M1.1,-1.0 Q1.45,-1.2 1.4,-1.6', 'M0.3,-1.48 Q0.4,-1.75 0.7,-1.8', 'M-1.3,0.6 Q-1.6,0.7 -1.7,1.0']:
            o.append(P(d, stroke=HAIR7, sw=1.6))
    o.append('</g></g>')   # head, unit
    o.append('</g>')       # flip
    if cast and cast_t:
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{cast}" fill-opacity="{cast_t}"/>')
    if expo > 0:
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{WHITE}" fill-opacity="{expo}"/>')
    elif expo < 0:
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#0B1020" fill-opacity="{-expo}"/>')
    o.append('</g></g>')   # filter, clip
    if frame:
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#94A3B8" stroke-width="1"/>')
    return ''.join(o), dict(fx=fx, fy=fy, s=s)


def F(g, a, b):
    """单位坐标 → 像素（不考虑倾斜和翻转）"""
    return g['fx'] + a * g['s'], g['fy'] + b * g['s']


# ---------------- Procreate 界面里的画布 ----------------
CX, CY, CW, CH = 250, 66, 300, 396


def photo(uid='c', **kw):
    return portrait(CX, CY, CW, CH, uid=uid, **kw)


def closeup(uid='cu', **kw):
    """放大到脸部的画布"""
    return portrait(CX, CY, CW, CH, uid=uid, fx=CX + CW / 2, fy=CY + CH * 0.5, s=CW * 0.42, **kw)


def side_bar(size=0.5, op=0.9, hl=None):
    x = 24
    def knob(top, frac):
        return top + (1 - frac) * 80
    ys, yo = knob(166, size), knob(298, op)
    s = (f'<rect x="{x}" y="150" width="30" height="250" rx="15" fill="{UIBAR}"/>'
         f'<rect x="{x + 11}" y="166" width="8" height="90" rx="4" fill="{UIPANEL}"/><rect x="{x + 6}" y="{ys:.0f}" width="18" height="10" rx="4" fill="{UITEXT}"/>'
         f'<rect x="{x + 6}" y="268" width="18" height="18" rx="4" fill="none" stroke="{UITEXT}" stroke-width="2"/>'
         f'<rect x="{x + 11}" y="298" width="8" height="90" rx="4" fill="{UIPANEL}"/><rect x="{x + 6}" y="{yo:.0f}" width="18" height="10" rx="4" fill="{UITEXT}"/>')
    if hl == 'op':
        s += ringrect(x - 4, 292, 38, 102, 12)
    if hl == 'size':
        s += ringrect(x - 4, 160, 38, 102, 12)
    return s


def scr(content, active=None, size=0.5, op=0.9, hl=None, side=True):
    s = screen(content, active=active, side=False)
    if side:
        s += side_bar(size, op, hl)
    return s


def cur_color(c):
    x, y = icon_pos('color')
    return f'<circle cx="{x}" cy="{y}" r="10" fill="{c}" stroke="{UITEXT}" stroke-width="2.5"/>'


def checker(x, y, w, h, n=4):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{WHITE}"/>'
    cw, ch = w / n, h / 3
    for i in range(n):
        for j in range(3):
            if (i + j) % 2:
                s += f'<rect x="{x + i * cw:.1f}" y="{y + j * ch:.1f}" width="{cw:.1f}" height="{ch:.1f}" fill="#D1D5DB"/>'
    return s


def lpanel(rows, x=470, y=62, w=300, hl=None, title='图层'):
    """rows: [dict(name, sub, mode, thumb, sel, lock)]，从上到下。thumb: photo / black / gray / blank / skin / mark"""
    row_h = 52
    h = 50 + len(rows) * row_h + 8
    s = [panel(x, y, w, h, title), text(x + w - 26, y + 30, '+', 24, 700, UITEXT, 'middle')]
    for i, r in enumerate(rows):
        yy = y + 44 + i * row_h
        s.append(f'<rect x="{x + 8}" y="{yy}" width="{w - 16}" height="{row_h - 6}" rx="8" fill="{UIBLUE if r.get("sel") else UIBAR}"/>')
        tx, ty, tw, th = x + 16, yy + 6, 44, 34
        t = r.get('thumb', 'blank')
        if t == 'photo':
            s.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="4" fill="#F3E8D2"/><circle cx="{tx + 22}" cy="{ty + 15}" r="9" fill="{SKIN}" stroke="{INK}" stroke-width="1"/>'
                     f'<path d="M{tx + 10} {ty + 34} q12 -12 24 0" fill="{VIO2}" stroke="{INK}" stroke-width="1"/><path d="M{tx + 13} {ty + 14} q9 -12 18 0" fill="{HAIR}" stroke="{INK}" stroke-width="1"/>')
        elif t == 'black':
            s.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="4" fill="#000"/>')
        elif t == 'gray':
            s.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="4" fill="#808080"/>')
        elif t == 'noise':
            s.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="4" fill="#808080"/>')
            rnd = random.Random(3)
            for _ in range(40):
                v = rnd.choice(['#6B6B6B', '#999999'])
                s.append(f'<rect x="{tx + rnd.uniform(1, tw - 3):.1f}" y="{ty + rnd.uniform(1, th - 3):.1f}" width="2" height="2" fill="{v}"/>')
        elif t in ('skin', 'mark', 'blank', 'pinkmark', 'darkmark'):
            s.append(checker(tx, ty, tw, th))
            c = {'skin': SKIN2, 'mark': SKIN3, 'pinkmark': PINK, 'darkmark': '#5B4B5B'}.get(t)
            if c:
                s.append(f'<ellipse cx="{tx + 16}" cy="{ty + 18}" rx="8" ry="5" fill="{c}"/><ellipse cx="{tx + 30}" cy="{ty + 16}" rx="6" ry="4" fill="{c}"/>')
        s.append(text(x + 70, yy + (22 if r.get('sub') else 29), r['name'], 15, 700, UITEXT))
        if r.get('sub'):
            s.append(text(x + 70, yy + 40, r['sub'], 12, 600, '#CBD5E1' if r.get('sel') else UIDIM))
        if r.get('lock'):
            s.append(f'<rect x="{x + w - 72}" y="{yy + 20}" width="12" height="10" rx="2" fill="{UITEXT}"/><path d="M{x + w - 69} {yy + 20} v-4 a3 3 0 0 1 6 0 v4" fill="none" stroke="{UITEXT}" stroke-width="2"/>')
        s.append(text(x + w - 44, yy + 29, r.get('mode', 'N'), 14, 800, UITEXT, 'middle'))
        s.append(f'<rect x="{x + w - 30}" y="{yy + 15}" width="16" height="16" rx="3" fill="{UIBLUE if r.get("vis", True) else UIBAR}" stroke="{UITEXT}" stroke-width="1.5"/>')
        if hl == i:
            s.append(ringrect(x + 4, yy - 3, w - 8, row_h))
        if hl == f'mode{i}':
            s.append(ring(x + w - 44, yy + 24, 15))
    return ''.join(s), (x, y, w, h, row_h)


def blend_pop(x, y, w, modes, sel, op=100, hl_op=False):
    """混合模式弹出菜单：上面是不透明度，下面是可滑动的模式列表"""
    row = 30
    h = 64 + len(modes) * row + 8
    s = [panel(x, y, w, h)]
    s.append(text(x + 14, y + 26, '不透明度', 13, 700, UITEXT) + text(x + w - 14, y + 26, f'{op}%', 13, 800, UITEXT, 'end'))
    s.append(f'<rect x="{x + 14}" y="{y + 36}" width="{w - 28}" height="8" rx="4" fill="#6B7280"/><rect x="{x + 14}" y="{y + 36}" width="{(w - 28) * op / 100:.1f}" height="8" rx="4" fill="{UIBLUE}"/>'
             f'<circle cx="{x + 14 + (w - 28) * op / 100:.1f}" cy="{y + 40}" r="8" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>')
    if hl_op:
        s.append(ringrect(x + 4, y + 8, w - 8, 46))
    for i, m in enumerate(modes):
        yy = y + 60 + i * row
        on = m == sel
        s.append(f'<rect x="{x + 8}" y="{yy}" width="{w - 16}" height="{row - 4}" rx="6" fill="{UIBLUE if on else UIBAR}"/>')
        s.append(text(x + 20, yy + 19, m, 14, 700, UITEXT))
        if on:
            s.append(ringrect(x + 4, yy - 3, w - 8, row + 2))
    return ''.join(s)


def brush_lib(x, y, groups, gsel, brushes, bsel, w=360):
    h = 52 + max(len(groups), len(brushes)) * 36 + 10
    s = [panel(x, y, w, h, '画笔库')]
    for i, gname in enumerate(groups):
        yy = y + 44 + i * 36
        s.append(f'<rect x="{x + 8}" y="{yy}" width="130" height="30" rx="7" fill="{UIBLUE if gname == gsel else UIBAR}"/>' + text(x + 20, yy + 21, gname, 14, 700, UITEXT))
        if gname == gsel:
            s.append(ringrect(x + 4, yy - 3, 138, 36))
    for i, b in enumerate(brushes):
        yy = y + 44 + i * 36
        s.append(f'<rect x="{x + 148}" y="{yy}" width="{w - 158}" height="30" rx="7" fill="{UIBLUE if b == bsel else UIBAR}"/>' + text(x + 160, yy + 21, b, 14, 700, UITEXT))
        s.append(f'<path d="M{x + w - 80} {yy + 18} q14 -10 28 0 t28 0" fill="none" stroke="{UIDIM}" stroke-width="{4 if b == bsel else 2}" stroke-linecap="round"/>')
        if b == bsel:
            s.append(ringrect(x + 144, yy - 3, w - 150, 36))
    return ''.join(s)


def options_menu(x, y, w, rows, hl=None):
    h = len(rows) * 32 + 16
    s = [panel(x, y, w, h)]
    for i, r in enumerate(rows):
        yy = y + 8 + i * 32
        if i:
            s.append(f'<line x1="{x + 10}" y1="{yy}" x2="{x + w - 10}" y2="{yy}" stroke="#4B5563"/>')
        s.append(text(x + 16, yy + 22, r, 14, 700, UITEXT))
        if r == hl:
            s.append(ringrect(x + 4, yy + 2, w - 8, 28))
    return ''.join(s)


def topinfo(t, x=400):
    """画布上方的提示条（例如「杂色 12%」）"""
    wd = len(t) * 13 + 40
    return f'<rect x="{x - wd / 2:.0f}" y="62" width="{wd:.0f}" height="28" rx="14" fill="{UIBLUE}"/>' + text(x, 81, t, 14, 800, WHITE, 'middle')


def soft_strokes(pts, r, color, op):
    return ''.join(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{r}" fill="{color}" fill-opacity="{op}" filter="url(#blur6)"/>' for a, b in pts)


BLUR = '<defs><filter id="blur6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter><filter id="blur3"><feGaussianBlur stdDeviation="3"/></filter></defs>'


def eyedrop(x, y, new, cur, r=26):
    return (f'<path d="M{x - r} {y} A{r} {r} 0 0 1 {x + r} {y} Z" fill="{new}"/><path d="M{x - r} {y} A{r} {r} 0 0 0 {x + r} {y} Z" fill="{cur}"/>'
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{WHITE}" stroke-width="5"/><circle cx="{x}" cy="{y}" r="{r + 3}" fill="none" stroke="{INK}" stroke-width="1.5"/>'
            f'<circle cx="{x}" cy="{y}" r="3" fill="none" stroke="{INK}" stroke-width="1.5"/>')


def clone_disc(x, y, r=16):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{WHITE}" stroke-width="4"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{INK}" stroke-width="2"/>'
            f'<line x1="{x - 8:.1f}" y1="{y:.1f}" x2="{x + 8:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="2"/><line x1="{x:.1f}" y1="{y - 8:.1f}" x2="{x:.1f}" y2="{y + 8:.1f}" stroke="{INK}" stroke-width="2"/>')


def card(x, y, w, h, fill=WHITE):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'


# ======================= 4.1 修图前的四步诊断 =======================
def setting_card(x, y, w, h, uid='set'):
    """角色设定图（简笔）：纯色底 + 人物 + 色票"""
    ph, g = portrait(x, y, w, h * 0.78, uid=uid, bg='plain', shade='3d', iris='#7C3AED', lip='#E11D48', blush=True)
    s = ph + f'<rect x="{x}" y="{y + h * 0.78:.1f}" width="{w}" height="{h * 0.22:.1f}" fill="{WHITE}" stroke="#94A3B8"/>'
    for i, c in enumerate([HAIR, '#7C3AED', '#E11D48', VIO2]):
        s += f'<rect x="{x + 8 + i * (w - 16) / 4:.1f}" y="{y + h * 0.82:.1f}" width="{(w - 16) / 4 - 6:.1f}" height="{h * 0.12:.1f}" rx="3" fill="{c}" stroke="{INK}" stroke-width="1"/>'
    return s


def p_four_checks():
    Wd, Hd = 780, 430
    s = [card(10, 10, 760, 410)]
    cols = [('① 缩小看全图', '第一眼哪里不对', MINT1), ('② 水平翻转画布', '看惯的歪斜露出来', YEL1),
            ('③ 灰度观察层', '只剩明暗：脸平、脏', VIO1), ('④ 对照设定图', '颜色、妆面对不对', PINK1)]
    for i, (t, d, fill) in enumerate(cols):
        x = 26 + i * 186
        s.append(label(x, 46, t, fill, 14))
        if i == 0:
            ph, _ = portrait(x + 60, 120, 60, 80, uid='f0', tilt=-6, cast='#F59E0B', cast_t=0.18, shade='flat')
            s.append(f'<rect x="{x}" y="66" width="170" height="250" rx="10" fill="#F1F5F9" stroke="{INK}" stroke-width="1.5"/>' + ph)
            s.append(text(x + 85, 240, '缩到手机屏幕大小', 12, 700, MUTED, 'middle'))
        elif i == 1:
            ph, _ = portrait(x, 66, 170, 250, uid='f1', tilt=-6, flip=True, cast='#F59E0B', cast_t=0.18, shade='flat')
            s.append(ph + f'<line x1="{x + 85}" y1="70" x2="{x + 85}" y2="312" stroke="{RED}" stroke-width="2" stroke-dasharray="6 5"/>')
            s.append(arrow(x + 60, 100, x + 30, 92, RED, 2.5, marker='arwr'))
        elif i == 2:
            ph, _ = portrait(x, 66, 170, 250, uid='f2', tilt=-6, gray=True, shade='flat')
            s.append(ph)
        else:
            ph, _ = portrait(x + 88, 66, 82, 250, uid='f3', fx=x + 129, fy=150, s=28, shade='flat', lip=LIPPALE, iris='#38BDF8', cast='#F59E0B', cast_t=0.18)
            s.append(ph + setting_card(x, 66, 82, 250, 'f3s'))
            s.append(text(x + 41, 330 - 4, '设定图', 12, 700, MUTED, 'middle') + text(x + 129, 326, '照片', 12, 700, MUTED, 'middle'))
        s.append(text(x + 85, 356, d, 14, 700, INK, 'middle'))
    s.append(text(26, 398, '四步各管一类问题，顺序固定：先整体，再翻转找歪斜，再看明暗，最后对颜色和细节。', 14, 600, MUTED))
    save('p-four-checks', svg(Wd, Hd, ''.join(s), '四步诊断各自能发现什么问题'))


def u_fit():
    ph, g = portrait(330, 150, 140, 185, uid='fit', tilt=-6, cast='#F59E0B', cast_t=0.18, shade='flat')
    hand = ''
    for (a, b, c, d) in [(300, 120, 330, 150), (500, 365, 470, 335)]:
        hand += f'<ellipse cx="{a}" cy="{b}" rx="10" ry="13" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>' + arrow(a + (8 if a < 400 else -8), b + (8 if a < 400 else -8), c, d, INK, 3)
    s = scr(ph + hand, side=True)
    s += label(520, 150, '两指快速捏合，画布适应屏幕', YEL1, 14)
    s += label(520, 182, '再慢慢捏小，到手机屏幕那么大', YEL1, 14)
    s += label(520, 230, '只看 3 秒：先注意到哪里？', WHITE, 14)
    s += badge(296, 98, 1) + badge(400, 128, 2)
    s += note('示意图')
    save('u-fit', svg(W, H, s, '两指快速捏合让画布适应屏幕，再缩小到手机大小看'))


def u_flip41():
    ph, g = photo('fl', tilt=-6, flip=True, cast='#F59E0B', cast_t=0.18, shade='flat')
    menu = actions_menu('画布', hl='水平翻转画布')
    s = scr(ph + menu, active='actions')
    s += ring(*icon_pos('actions'), 18) + badge(icon_pos('actions')[0] + 24, 60, 1)
    s += badge(400, 62 + 50 + 6 * 34 + 17, 2)
    s += label(560, 300, '翻过来以后，头往一边歪、', YEL1, 14)
    s += label(560, 332, '脸左右不对称会一下变明显', YEL1, 14)
    s += label(560, 372, '检查完再点一次翻回来', WHITE, 14)
    s += note('示意图：操作 › 画布 › 水平翻转画布')
    save('u-flip', svg(W, H, s, '操作、画布：水平翻转画布'))


LAYER_OPTS = ['重命名', '选择', '拷贝', '填充图层', '清除', '阿尔法锁定', '蒙版', '剪辑蒙版', '反转', '参考', '向下合并', '向下组合']


def u_gray_fill():
    ph, g = photo('gf', cast='#F59E0B', cast_t=0.18, shade='flat')
    lp, (lx, ly, lw, lh, rh) = lpanel([dict(name='灰度观察', thumb='blank', sel=True), dict(name='图层 1', thumb='photo')], hl=0)
    menu = options_menu(lx - 150, ly + 44, 140, LAYER_OPTS, hl='填充图层')
    s = scr(ph + lp + menu, active='layers')
    s += cur_color('#000000') + ring(*icon_pos('color'), 18) + ring(*icon_pos('layers'), 18)
    s += badge(lx + lw - 52, ly + 26, 1) + badge(lx - 160, ly + 44 + 8 + 3 * 32 + 16, 3)
    s += label(lx, ly + lh + 36, '① 点「+」新建一层，改名「灰度观察」', YEL1, 13)
    s += label(lx, ly + lh + 68, '② 右上角颜色选纯黑', YEL1, 13)
    s += label(lx, ly + lh + 100, '③ 点这一层两次 → 填充图层', YEL1, 13)
    s += note('示意图，菜单项以实际界面为准')
    save('u-gray-fill', svg(W, H, s, '新建图层，选黑色，在图层选项里点填充图层'))


def u_gray_mode():
    ph, g = photo('gm', cast='#F59E0B', cast_t=0.18, shade='flat', gray=True)
    lp, (lx, ly, lw, lh, rh) = lpanel([dict(name='灰度观察', sub='颜色', thumb='black', sel=True, mode='N'), dict(name='图层 1', thumb='photo')], hl='mode0')
    pop = blend_pop(lx - 10, ly + lh + 10, 200, ['色相', '饱和度', '颜色', '明度'], '颜色')
    s = scr(ph + lp + pop, active='layers')
    s += badge(lx + lw - 72, ly + 44 + 10, 1) + badge(lx + 210, ly + lh + 10 + 60 + 2 * 30 + 13, 2)
    s += label(36, 520, '① 点图层右边的字母  ② 往下滑到「颜色」：画面马上变成黑白', WHITE, 14)
    s += note('示意图')
    save('u-gray-mode', svg(W, H, s, '把黑色图层的混合模式改成颜色，画面变成灰度'))


def u_reference():
    ph, g = photo('rf', cast='#F59E0B', cast_t=0.18, shade='flat', lip=LIPPALE, iris='#38BDF8')
    menu = actions_menu('画布', hl='参考', toggles={'动画协助': False, '页面辅助': False, '绘图指引': False, '参考': True})
    rx, ry, rw, rh = 564, 276, 200, 228
    win = (f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="12" fill="{UIPANEL}" stroke="#111827" stroke-width="1.5"/>'
           f'<rect x="{rx + rw / 2 - 20}" y="{ry + 6}" width="40" height="5" rx="2.5" fill="{UIDIM}"/>'
           + setting_card(rx + 40, ry + 18, 120, 160, 'rfs'))
    for i, b in enumerate(['画布', '图像', '面容']):
        bx = rx + 12 + i * 62
        win += f'<rect x="{bx}" y="{ry + rh - 40}" width="54" height="28" rx="8" fill="{UIBLUE if b == "图像" else UIBAR}"/>' + text(bx + 27, ry + rh - 21, b, 13, 700, UITEXT, 'middle')
    win += ringrect(rx + 72, ry + rh - 43, 60, 34)
    s = scr(ph + menu + win, active='actions')
    s += ring(*icon_pos('actions'), 18)
    s += badge(400, 62 + 50 + 5 * 34 + 17, 1) + badge(rx + 102, ry + rh - 58, 2)
    s += label(560, 262, '② 点「图像」，载入设定图', YEL1, 13)
    s += note('示意图：操作 › 画布 › 参考')
    save('u-reference', svg(W, H, s, '打开参考窗口，用图像模式放角色设定图'))


def case_venue(kind):
    """漫展室内场照：kind = color / gray / mark"""
    Wd, Hd = 640, 520
    ph, g = portrait(20, 20, 600, 480, uid='cv' + kind, bg='venue', shade='flat', tilt=-6, blem=True, red=True, crowd=True, stray=True,
                     cast='#F59E0B', cast_t=0.2, gray=(kind == 'gray'), lip=LIPPALE, iris='#38BDF8', s=92, fy=200)
    s = ph
    if kind == 'mark':
        pts = [(1, g['fx'] + 150, 60, '整体偏黄'), (2, g['fx'] - 60, g['fy'] + 30, '脸很平'), (3, g['fx'] + 60, g['fy'] + 40, '痘和泛红'),
               (4, 70, 320, '背景路人'), (5, g['fx'] - 140, 80, '假发杂毛'), (6, g['fx'], g['fy'] - 150, '头往左歪')]
        for n, a, b, t in pts:
            s += badge(a, b, n) + label(a + 18, b + 6, t, YEL1, 13)
    lab = {'color': '原图：漫展室内场照', 'gray': '打开灰度观察层：脸几乎没有明暗起伏', 'mark': '诊断标记'}[kind]
    s += label(34, 490, lab, YEL1 if kind != 'gray' else WHITE, 15)
    save(f'case-venue-{kind}', svg(Wd, Hd, s, lab))


def case_backlit(kind):
    Wd, Hd = 640, 520
    ph, g = portrait(20, 20, 600, 480, uid='cb' + kind, bg='outdoor', shade='messy', s=92, fy=200, gray=(kind == 'gray'),
                     liner_bad=True, eye_dy=0.04, lip=LIP)
    s = ph
    lab = {'color': '原图：外景逆光', 'gray': '灰度：右半边脸比左半边暗一大截'}[kind]
    s += label(34, 490, lab, YEL1 if kind == 'color' else WHITE, 15)
    save(f'case-backlit-{kind}', svg(Wd, Hd, s, lab))


# ======================= 4.2 Lightroom 手机版 =======================
LRBG = '#141416'; LRPAN = '#1E1E21'; LRTXT = '#ECECEE'; LRDIM = '#8E8E93'; LRBLUE = '#3B9CFF'
PHX, PHY, PHW, PHH = 30, 10, 300, 540           # 手机外框
SX2, SY2, SW2, SH2 = 40, 22, 280, 516            # 屏幕
PX0, PW0 = 50, 260                               # 面板内容区
LR_TABS = ['自动', '亮度', '颜色', '效果', '细节', '光学', '几何']
LR_TOOLS = ['预设', '裁切', '编辑', '蒙版', '移除']
LR_PHOTO = (40, 60, 280, 228)


def lr_photo(uid, **kw):
    x, y, w, h = LR_PHOTO
    ph, g = portrait(x + 52, y, 176, h, uid=uid, frame=False, **kw)
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#0B0B0D"/>' + ph, g


def lr_hist(x, y, w=96, h=42, shape='ok'):
    pts = []
    for k in range(41):
        t = k / 40
        if shape == 'dark':
            v = 0.9 * math.exp(-((t - 0.2) / 0.12) ** 2) + 0.3 * math.exp(-((t - 0.45) / 0.1) ** 2)
        elif shape == 'clip':
            v = 0.5 * math.exp(-((t - 0.3) / 0.12) ** 2) + 0.3 * math.exp(-((t - 0.6) / 0.1) ** 2) + (1.0 if t > 0.96 else 0)
        else:
            v = 0.35 * math.exp(-((t - 0.25) / 0.12) ** 2) + 0.8 * math.exp(-((t - 0.58) / 0.1) ** 2) + 0.25 * math.exp(-((t - 0.82) / 0.08) ** 2)
        pts.append((x + t * w, y + h - min(v, 1) * (h - 4)))
    d = f'M{x} {y + h} ' + ' '.join(f'L{a:.1f} {b:.1f}' for a, b in pts) + f' L{x + w} {y + h} Z'
    return f'<rect x="{x - 4}" y="{y - 4}" width="{w + 8}" height="{h + 8}" rx="6" fill="#000" fill-opacity=".55"/><path d="{d}" fill="#D1D5DB" fill-opacity=".85"/>'


def lr_phone(photo_svg, panel_svg, tab='亮度', tool='编辑', hl_tab=False, hl_tool=False):
    s = [f'<rect x="{PHX}" y="{PHY}" width="{PHW}" height="{PHH}" rx="38" fill="{INK}"/>',
         f'<rect x="{SX2}" y="{SY2}" width="{SW2}" height="{SH2}" rx="28" fill="{LRBG}"/>']
    # 顶栏
    s.append(text(56, 50, '‹', 26, 700, LRTXT))
    s.append(f'<path d="M208 44 a8 8 0 1 1 8 8" fill="none" stroke="{LRTXT}" stroke-width="2"/><path d="M205 40 l3 5 5 -3" fill="none" stroke="{LRTXT}" stroke-width="2"/>')
    s.append(f'<path d="M260 44 a8 8 0 1 0 -8 8" fill="none" stroke="{LRTXT}" stroke-width="2"/><path d="M263 40 l-3 5 -5 -3" fill="none" stroke="{LRTXT}" stroke-width="2"/>')
    s.append(text(288, 48, '···', 16, 900, LRTXT, 'middle'))
    s.append(photo_svg)
    s.append(f'<rect x="{SX2}" y="292" width="{SW2}" height="178" fill="{LRPAN}"/>')
    s.append(panel_svg)
    # 面板名称一排
    tw = SW2 / len(LR_TABS)
    for i, t in enumerate(LR_TABS):
        cx = SX2 + tw * (i + 0.5)
        on = t == tab
        s.append(text(cx, 492, t, 12, 800 if on else 600, LRBLUE if on else LRTXT, 'middle'))
        if on:
            s.append(f'<rect x="{cx - 13:.1f}" y="497" width="26" height="3" rx="1.5" fill="{LRBLUE}"/>')
            if hl_tab:
                s.append(ringrect(cx - 19, 474, 38, 30))
    # 底部工具
    s.append(f'<line x1="{SX2 + 10}" y1="506" x2="{SX2 + SW2 - 10}" y2="506" stroke="#2C2C30"/>')
    tw2 = SW2 / len(LR_TOOLS)
    for i, t in enumerate(LR_TOOLS):
        cx = SX2 + tw2 * (i + 0.5)
        on = t == tool
        s.append(text(cx, 526, t, 12, 800 if on else 600, LRBLUE if on else LRDIM, 'middle'))
        if on and hl_tool:
            s.append(ringrect(cx - 22, 510, 44, 24))
    return ''.join(s)


def lr_slider(y, name, frac, val, hl=False, x=None, w=None, grad=None):
    x = PX0 + 6 if x is None else x
    w = PW0 - 12 if w is None else w
    s = text(x, y, name, 12, 700, LRTXT) + text(x + w, y, val, 12, 700, LRTXT, 'end')
    ty = y + 9
    if grad:
        gid = 'lg' + name.encode().hex()[:8]
        s += (f'<defs><linearGradient id="{gid}"><stop offset="0" stop-color="{grad[0]}"/><stop offset="1" stop-color="{grad[1]}"/></linearGradient></defs>'
              f'<rect x="{x}" y="{ty - 2}" width="{w}" height="4" rx="2" fill="url(#{gid})"/>')
    else:
        s += f'<rect x="{x}" y="{ty - 1}" width="{w}" height="2" rx="1" fill="#4B4B50"/>'
        cx = x + w / 2
        kx = cx + frac * w / 2
        s += f'<line x1="{min(cx, kx):.1f}" y1="{ty}" x2="{max(cx, kx):.1f}" y2="{ty}" stroke="{LRTXT}" stroke-width="2"/>'
    s += f'<line x1="{x + w / 2}" y1="{ty - 4}" x2="{x + w / 2}" y2="{ty + 4}" stroke="{LRDIM}" stroke-width="1.5"/>'
    s += f'<circle cx="{x + w / 2 + frac * w / 2:.1f}" cy="{ty}" r="6" fill="{WHITE}"/>'
    if hl:
        s += ringrect(x - 6, y - 15, w + 12, 30, 8)
    return s


def anno(x, y, lines, fill=YEL1, size=14, gap=32):
    return ''.join(label(x, y + i * gap, t, fill if not t.startswith('·') else WHITE, size) for i, t in enumerate(lines))


LIGHT_ROWS = [('曝光度', 0.08, '+0.40'), ('对比度', 0.08, '+8'), ('高光', -0.35, '-35'), ('阴影', 0.3, '+30'), ('白色色阶', 0.12, '+12'), ('黑色色阶', -0.06, '-6')]


def u_lr_light():
    ph, g = lr_photo('lrl', bg='venue', shade='flat', cast='#F59E0B', cast_t=0.12)
    pan = ''.join(lr_slider(312 + i * 27, n, f, v) for i, (n, f, v) in enumerate(LIGHT_ROWS)) + ringrect(PX0, 312 + 2 * 27 - 15, PW0, 57, 8)
    s = lr_phone(ph + lr_hist(52, 70), pan, '亮度', hl_tab=True, hl_tool=True)
    s += badge(SX2 + SW2 / 7 * 2.5, 466, 1) + badge(SX2 + SW2 / 5 * 2.5 + 28, 522, 2)
    s += badge(PX0 + PW0 + 8, 368, 3)
    s += anno(350, 70, ['① 底部点「编辑」', '② 选「亮度」面板（部分版本叫「光效」）', '③ 曝光度定好脸的亮度，再调高光、阴影'])
    s += anno(350, 190, ['· 曝光度：整张一起变亮或变暗', '· 高光 / 阴影：只动亮部 / 暗部', '· 白色 / 黑色色阶：管直方图两端', '· 对比度：亮的更亮、暗的更暗'], size=13, gap=30)
    s += anno(350, 330, ['左上角是直方图（两指点按照片显示）'], WHITE, 13)
    s += text(784, 540, '示意图，面板名称和位置以 App 实际显示为准', 12, 600, MUTED, 'end')
    save('u-lr-light', svg(W, H, s, 'Lightroom 手机版：编辑 › 亮度面板的六个滑块'))


def wb_picker(x, y):
    return (f'<circle cx="{x}" cy="{y}" r="20" fill="none" stroke="{WHITE}" stroke-width="3"/><circle cx="{x}" cy="{y}" r="20" fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3"/>'
            f'<line x1="{x - 6}" y1="{y}" x2="{x + 6}" y2="{y}" stroke="{WHITE}" stroke-width="2"/><line x1="{x}" y1="{y - 6}" x2="{x}" y2="{y + 6}" stroke="{WHITE}" stroke-width="2"/>')


def u_lr_color():
    ph, g = lr_photo('lrc', bg='venue', shade='flat', cast='#F59E0B', cast_t=0.22)
    pan = text(PX0 + 6, 312, '白平衡', 12, 700, LRTXT)
    pan += f'<rect x="{PX0 + 60}" y="298" width="96" height="22" rx="6" fill="#2C2C30"/>' + text(PX0 + 108, 313, '自定义 ▾', 12, 700, LRTXT, 'middle')
    pan += f'<path d="M{PX0 + 232} 316 l10 -10 4 4 -10 10 z" fill="{LRTXT}"/><circle cx="{PX0 + 247}" cy="303" r="4" fill="{LRTXT}"/>'
    pan += ring(PX0 + 240, 309, 14)
    rows = [('色温', -0.22, '-22', ('#4F8DF5', '#F5C542')), ('色调', 0.04, '+4', ('#4CC27A', '#D24CC2')), ('自然饱和度', 0.1, '+10', None), ('饱和度', -0.05, '-5', None)]
    pan += ''.join(lr_slider(342 + i * 27, n, f, v, hl=(i == 0), grad=gr) for i, (n, f, v, gr) in enumerate(rows))
    for i, b in enumerate(['混合', '分级']):
        pan += f'<rect x="{PX0 + 6 + i * 70}" y="446" width="62" height="20" rx="6" fill="#2C2C30"/>' + text(PX0 + 37 + i * 70, 460, b, 12, 700, LRTXT, 'middle')
    ph += wb_picker(92 + 28, 60 + 70)
    s = lr_phone(ph, pan, '颜色', hl_tab=True)
    s += badge(SX2 + SW2 / 7 * 3.5, 466, 1) + badge(PX0 + 222, 296, 2) + badge(98, 104, 3) + badge(PX0 + PW0 + 8, 342, 4)
    s += anno(350, 70, ['① 选「颜色」面板', '② 点白平衡选择器（吸管）', '③ 把圆圈拖到本来该是白色或灰色的地方', '④ 再用色温、色调微调'])
    s += anno(350, 222, ['· 色温：往左偏蓝，往右偏黄', '· 色调：往左偏绿，往右偏洋红', '· 肤色怪先别动饱和度，去「混合」里调橙色'], size=13, gap=30)
    s += text(784, 540, '示意图，面板名称和位置以 App 实际显示为准', 12, 600, MUTED, 'end')
    save('u-lr-color', svg(W, H, s, 'Lightroom 手机版：颜色面板，白平衡选择器和色温色调'))


MIX_COLORS = [('红色', '#EF4444'), ('橙色', '#F97316'), ('黄色', '#EAB308'), ('绿色', '#22C55E'), ('浅绿色', '#14B8A6'), ('蓝色', '#3B82F6'), ('紫色', '#8B5CF6'), ('洋红', '#D946EF')]


def u_lr_mix():
    ph, g = lr_photo('lrm', bg='venue', shade='flat', skin='#F7C6A0', red=True)
    pan = text(PX0 + 80, 312, '颜色混合', 12, 800, LRTXT) + text(PX0 + PW0 - 6, 312, '完成', 12, 800, LRBLUE, 'end')
    for i, (n, c) in enumerate(MIX_COLORS):
        cx = PX0 + 20 + i * 31
        pan += f'<circle cx="{cx}" cy="336" r="10" fill="{c}"/>'
        if n == '橙色':
            pan += f'<circle cx="{cx}" cy="336" r="14" fill="none" stroke="{WHITE}" stroke-width="2"/>' + ring(cx, 336, 18)
    pan += f'<circle cx="{PX0 + 20 + 8 * 31 - 6}" cy="312" r="0" fill="none"/>'
    rows = [('色相', 0.06, '+6', ('#F87171', '#FACC15')), ('饱和度', -0.12, '-12', ('#A8A29E', '#F97316')), ('明亮度', 0.1, '+10', ('#7C2D12', '#FED7AA'))]
    pan += ''.join(lr_slider(374 + i * 30, n, f, v, grad=gr) for i, (n, f, v, gr) in enumerate(rows))
    s = lr_phone(ph, pan, '颜色')
    s += badge(PX0 + 51, 308, 1) + badge(PX0 + PW0 + 8, 404, 2)
    s += anno(350, 70, ['在颜色面板里点「混合」（部分版本叫「混色」）', '① 选橙色：皮肤主要在这一格', '② 三个滑块各管一件事'])
    s += anno(350, 190, ['· 色相：往左偏红、偏粉，往右偏黄', '· 饱和度：往左淡，往右浓', '· 明亮度：往右提亮皮肤，往左压暗', '· 红色格管嘴唇和泛红，一起看'], size=13, gap=30)
    s += anno(350, 330, ['色块名称以 App 为准，一般是 8 个颜色'], WHITE, 13)
    s += text(784, 540, '示意图，面板名称和位置以 App 实际显示为准', 12, 600, MUTED, 'end')
    save('u-lr-mix', svg(W, H, s, 'Lightroom 手机版：颜色混合，橙色管肤色'))


def u_lr_curve():
    ph, g = lr_photo('lrcv', bg='venue', shade='flat')
    x0, y0, w0, h0 = 70, 78, 220, 192
    cv = f'<rect x="{x0}" y="{y0}" width="{w0}" height="{h0}" fill="#000" fill-opacity=".45" stroke="{LRDIM}"/>'
    for i in range(1, 4):
        cv += f'<line x1="{x0 + w0 * i / 4}" y1="{y0}" x2="{x0 + w0 * i / 4}" y2="{y0 + h0}" stroke="{LRDIM}" stroke-opacity=".5"/><line x1="{x0}" y1="{y0 + h0 * i / 4}" x2="{x0 + w0}" y2="{y0 + h0 * i / 4}" stroke="{LRDIM}" stroke-opacity=".5"/>'
    cv += f'<line x1="{x0}" y1="{y0 + h0}" x2="{x0 + w0}" y2="{y0}" stroke="{LRDIM}" stroke-dasharray="4 4"/>'
    p1 = (x0 + w0 * 0.25, y0 + h0 * 0.81); p2 = (x0 + w0 * 0.75, y0 + h0 * 0.19)
    cv += f'<path d="M{x0} {y0 + h0} C{x0 + w0 * 0.18} {y0 + h0 * 0.95} {p1[0] - 10} {p1[1] + 4} {p1[0]} {p1[1]} S{p2[0] - 40} {p2[1] + 20} {p2[0]} {p2[1]} S{x0 + w0 - 10} {y0 + 4} {x0 + w0} {y0}" fill="none" stroke="{WHITE}" stroke-width="2.5"/>'
    for p in (p1, p2):
        cv += f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="5" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
    pan = text(PX0 + 6, 314, '曲线', 12, 800, LRTXT)
    for i, (n, c) in enumerate([('白色通道', '#F5F5F5'), ('红色通道', '#EF4444'), ('绿色通道', '#22C55E'), ('蓝色通道', '#3B82F6')]):
        cx = PX0 + 30 + i * 58
        pan += f'<circle cx="{cx}" cy="346" r="11" fill="{c}"/>' + text(cx, 376, n[:2], 11, 700, LRDIM, 'middle')
    pan += ring(PX0 + 30, 346, 16)
    pan += text(PX0 + 6, 410, '在曲线上点一下加点，拖动调整', 12, 600, LRDIM) + text(PX0 + 6, 430, '双击点可以删除', 12, 600, LRDIM)
    s = lr_phone(ph + cv, pan, '亮度')
    s += badge(p1[0] - 18, p1[1] + 4, 1) + badge(p2[0] + 18, p2[1] - 4, 2) + badge(PX0 + 30 - 24, 334, 3)
    s += anno(350, 70, ['在「亮度」面板里找「曲线」', '① 暗部的点往下压一点', '② 亮部的点往上提一点', '   = 轻微的 S 形，加一点对比', '③ 先用白色通道（三色一起调）'])
    s += anno(350, 252, ['· 弯得越多越硬，人像轻轻一点就够', '· 单独拉红、绿、蓝通道会偏色，新手先别碰'], size=13, gap=30)
    s += text(784, 540, '示意图，面板名称和位置以 App 实际显示为准', 12, 600, MUTED, 'end')
    save('u-lr-curve', svg(W, H, s, 'Lightroom 手机版：曲线，轻微 S 形'))


def u_lr_mask():
    ph, g = lr_photo('lrmk', bg='outdoor', shade='messy', expo=-0.15)
    x, y, w, h = LR_PHOTO
    ph += f'<path d="M{g["fx"] - g["s"] * 0.98:.1f} {g["fy"]:.1f} a{g["s"] * 0.98:.1f} {g["s"] * 1.15:.1f} 0 1 0 {g["s"] * 1.96:.1f} 0 a{g["s"] * 0.98:.1f} {g["s"] * 1.15:.1f} 0 1 0 {-g["s"] * 1.96:.1f} 0" fill="#EF4444" fill-opacity=".35"/>'
    items = ['选择主体', '选择背景', '选择天空', '画笔', '线性渐变', '径向渐变', '颜色范围', '明亮度范围']
    pan = text(PX0 + 6, 312, '创建新蒙版', 12, 800, LRTXT) + f'<rect x="{PX0 + PW0 - 56}" y="300" width="50" height="18" rx="9" fill="{YEL}"/>' + text(PX0 + PW0 - 31, 313, '高级版', 11, 800, INK, 'middle')
    for i, it in enumerate(items):
        cx = PX0 + 6 + (i % 2) * 128; cy = 328 + (i // 2) * 34
        pan += f'<rect x="{cx}" y="{cy}" width="120" height="28" rx="7" fill="#2C2C30"/>' + text(cx + 12, cy + 19, it, 12, 700, LRTXT)
        if it == '选择主体':
            pan += ringrect(cx - 3, cy - 3, 126, 34)
    s = lr_phone(ph, pan, '亮度', tool='蒙版', hl_tool=True)
    s += badge(SX2 + SW2 / 5 * 3.5, 504, 1) + badge(PX0 - 2, 342, 2)
    s += anno(350, 70, ['① 底部点「蒙版」', '② 选「选择主体」或用「画笔」涂脸', '③ 红色区域就是只会被调整的地方', '   再在这个蒙版里提亮、调色'])
    s += anno(350, 222, ['· 蒙版属于高级版功能（需要订阅）', '· 免费替代：Snapseed 的「局部」或「画笔」', '· 或者导进 Procreate 后，在 4.4 课里提亮'], size=13, gap=30)
    s += text(784, 540, '示意图，菜单项以 App 实际显示为准', 12, 600, MUTED, 'end')
    save('u-lr-mask', svg(W, H, s, 'Lightroom 手机版：蒙版（高级版功能）'))


def u_lr_export():
    ph, g = lr_photo('lrex', bg='venue', shade='3d')
    menu = [('保存副本到设备', True), ('视图选项', False), ('复制设置', False), ('粘贴设置', False), ('创建预设', False)]
    pop = f'<rect x="150" y="56" width="164" height="{len(menu) * 32 + 12}" rx="12" fill="#2C2C30" stroke="#3F3F46"/>'
    for i, (m, on) in enumerate(menu):
        pop += text(164, 80 + i * 32, m, 13, 700, LRTXT)
        if on:
            pop += ringrect(154, 60 + i * 32, 156, 30)
    pan = text(PX0 + 6, 314, '导出设置（在保存或共享时出现）', 12, 800, LRTXT)
    for i, (k, v) in enumerate([('文件类型', 'JPG'), ('尺寸', '最大可用'), ('品质', '100%')]):
        yy = 336 + i * 30
        pan += text(PX0 + 6, yy + 4, k, 12, 700, LRDIM) + text(PX0 + PW0 - 6, yy + 4, v, 12, 800, LRTXT, 'end') + f'<line x1="{PX0 + 6}" y1="{yy + 14}" x2="{PX0 + PW0 - 6}" y2="{yy + 14}" stroke="#2C2C30"/>'
    s = lr_phone(ph + pop, pan, '亮度')
    s += ring(288, 44, 14) + badge(342, 30, 1) + badge(PX0 + PW0 + 8, 350, 2)
    s += anno(350, 70, ['① 右上角「···」→「保存副本到设备」', '   或者点共享，选导出', '② 文件类型 JPG，尺寸选最大，品质拉满'])
    s += anno(350, 190, ['· 选项的名字和位置以 App 为准', '· 导出后在 Procreate 图库里点「照片」导入', '· 有色彩空间选项时选 sRGB'], size=13, gap=30)
    s += text(784, 540, '示意图，菜单项以 App 实际显示为准', 12, 600, MUTED, 'end')
    save('u-lr-export', svg(W, H, s, 'Lightroom 手机版：保存副本到设备，再导入 Procreate'))


# ---------- 原理图 ----------
def hist_shape(t):
    return 0.3 * math.exp(-((t - 0.22) / 0.1) ** 2) + 0.9 * math.exp(-((t - 0.56) / 0.09) ** 2) + 0.35 * math.exp(-((t - 0.8) / 0.08) ** 2) + 0.04


def p_lr_zones():
    Wd, Hd = 780, 470
    s = [card(10, 10, 760, 450)]
    x0, y0, w, h = 60, 150, 660, 150
    zones = [('黑', 0, 0.06), ('暗部', 0.06, 0.32), ('中间调', 0.32, 0.68), ('亮部', 0.68, 0.94), ('白', 0.94, 1)]
    for n, a, b in zones:
        v = int(30 + (a + b) / 2 * 210)
        s.append(f'<rect x="{x0 + w * a:.1f}" y="{y0 + h + 6}" width="{w * (b - a):.1f}" height="22" fill="#{v:02x}{v:02x}{v:02x}" stroke="{INK}" stroke-width="1.5"/>')
        s.append(text(x0 + w * (a + b) / 2, y0 + h + 48, n, 13, 800, INK, 'middle'))
    pts = [(x0 + k / 100 * w, y0 + h - hist_shape(k / 100) * (h - 10)) for k in range(101)]
    d = f'M{x0} {y0 + h} ' + ' '.join(f'L{a:.1f} {b:.1f}' for a, b in pts) + f' L{x0 + w} {y0 + h} Z'
    s.append(f'<path d="{d}" fill="{VIO2}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>')
    # 滑块管的范围
    def bracket(a, b, yy, name, fill, note_):
        xa, xb = x0 + w * a, x0 + w * b
        return (f'<path d="M{xa:.1f} {yy + 10} v-10 h{xb - xa:.1f} v10" fill="none" stroke="{INK}" stroke-width="2.5"/>'
                + label((xa + xb) / 2, yy - 10, name, fill, 13, 'middle') + text((xa + xb) / 2, yy - 34, note_, 12, 600, MUTED, 'middle'))
    s.append(bracket(0.0, 1.0, 76, '曝光度：整座山一起左右移', YEL1, ''))
    s.append(bracket(0.06, 0.4, 132, '阴影', MINT1, ''))
    s.append(bracket(0.62, 0.94, 132, '高光', PINK1, ''))
    s.append(label(x0 - 6, 128, '黑色色阶', WHITE, 12) if False else '')
    s.append(arrow(x0 + 18, y0 + 60, x0 + 2, y0 + 60, INK, 2.5) + text(x0 + 22, y0 + 64, '黑色色阶', 12, 800))
    s.append(arrow(x0 + w - 18, y0 + 60, x0 + w - 2, y0 + 60, INK, 2.5) + text(x0 + w - 22, y0 + 64, '白色色阶', 12, 800, INK, 'end'))
    s.append(text(x0, 50, '每个滑块只管直方图的一段：', 16, 800))
    s.append(text(x0, y0 + h + 82, '对比度：把山往两边拉开（亮的更亮、暗的更暗）。往左拉会让整张图发灰。', 13, 600, MUTED))
    s.append(text(x0, y0 + h + 104, '顺序：曝光度先把脸调到合适 → 高光救亮部 → 阴影补暗部 → 白色/黑色色阶收两端 → 最后对比度。', 13, 600, MUTED))
    s.append(text(x0, y0 + h + 126, '直方图怎么读，见 0.2 课。', 13, 600, MUTED))
    save('p-lr-zones', svg(Wd, Hd, ''.join(s), '亮度面板的滑块各管直方图哪一段'))


def p_wb():
    Wd, Hd = 780, 420
    s = [card(10, 10, 760, 400)]
    s.append(text(40, 50, '照片里本来是白色、灰色的东西，R、G、B 应该一样多。偏了哪边，就往反方向推。', 15, 800))
    defs = (f'<defs><linearGradient id="wbT"><stop offset="0" stop-color="#4F8DF5"/><stop offset="1" stop-color="#F5C542"/></linearGradient>'
            f'<linearGradient id="wbG"><stop offset="0" stop-color="#4CC27A"/><stop offset="1" stop-color="#D24CC2"/></linearGradient></defs>')
    s.append(defs)
    for i, (gid, name, l, r) in enumerate([('wbT', '色温', '偏蓝（冷）', '偏黄（暖）'), ('wbG', '色调', '偏绿', '偏洋红')]):
        y = 90 + i * 70
        s.append(text(40, y + 16, name, 15, 800) + f'<rect x="110" y="{y}" width="420" height="22" rx="11" fill="url(#{gid})" stroke="{INK}" stroke-width="2"/>')
        s.append(text(110, y + 42, l, 12, 700, MUTED) + text(530, y + 42, r, 12, 700, MUTED, 'end') + f'<line x1="320" y1="{y - 4}" x2="320" y2="{y + 26}" stroke="{INK}" stroke-width="2"/>')
    # 三个例子
    ex = [('漫展暖光：白墙发黄', '#F7E3A6', '色温往左（蓝）', '#F8F8F6'), ('阴天、屏幕光：发蓝', '#C9DDF7', '色温往右（黄）', '#F8F8F6'), ('LED 灯：发紫发粉', '#EFC9EA', '色调往左（绿）', '#F8F8F6')]
    for i, (t, c1, act, c2) in enumerate(ex):
        x = 40 + i * 246
        s.append(f'<rect x="{x}" y="250" width="70" height="70" rx="8" fill="{c1}" stroke="{INK}" stroke-width="2"/>' + arrow(x + 78, 285, x + 118, 285, INK, 2.5)
                 + f'<rect x="{x + 124}" y="250" width="70" height="70" rx="8" fill="{c2}" stroke="{INK}" stroke-width="2"/>')
        s.append(text(x, 344, t, 13, 800) + text(x, 366, act, 13, 700, VIO7))
    s.append(text(560, 106, '白平衡选择器（吸管）', 13, 800) + text(560, 128, '= 告诉软件"这里应该是灰色"，', 12, 600, MUTED) + text(560, 148, '它自动把色温、色调推回去。', 12, 600, MUTED))
    s.append(text(560, 178, '吸在白衬衫、白墙、灰地面上；', 12, 600, MUTED) + text(560, 198, '别吸皮肤、假发和彩色灯牌。', 12, 600, MUTED))
    s.append(text(40, 396, 'RAW 照片的色温显示开尔文数值（K），JPG 显示 -100～+100，方向是一样的。', 12, 600, MUTED))
    save('p-wb', svg(Wd, Hd, ''.join(s), '白平衡：色温管蓝黄，色调管绿和洋红，偏哪边往反方向推'))


def p_hsl():
    Wd, Hd = 780, 400
    s = [card(10, 10, 760, 380)]
    cx, cy, R, r = 190, 200, 140, 80
    n = len(MIX_COLORS)
    labs = []
    for i, (name, c) in enumerate(MIX_COLORS):
        a0 = -90 + i * 360 / n - 360 / n / 2; a1 = a0 + 360 / n
        def pt(a, rr):
            return cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a))
        p0, p1, p2, p3 = pt(a0, R), pt(a1, R), pt(a1, r), pt(a0, r)
        s.append(f'<path d="M{p0[0]:.1f} {p0[1]:.1f} A{R} {R} 0 0 1 {p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f} A{r} {r} 0 0 0 {p3[0]:.1f} {p3[1]:.1f} Z" fill="{c}" stroke="{WHITE}" stroke-width="2"/>')
        m = pt((a0 + a1) / 2, (R + r) / 2 + (22 if name == '橙色' else 0))
        labs.append(text(m[0], m[1] + 5, name, 12, 800, WHITE, 'middle', 'stroke="%s" stroke-width="3" paint-order="stroke"' % c))
    # 肤色点
    rnd = random.Random(2)
    for _ in range(18):
        a = math.radians(-90 + 360 / n * 1 + rnd.uniform(-22, 16)); rr = rnd.uniform(r + 6, (r + R) / 2 + 4)
        s.append(f'<circle cx="{cx + rr * math.cos(a):.1f}" cy="{cy + rr * math.sin(a):.1f}" r="5" fill="{SKIN}" stroke="{INK}" stroke-width="1.5"/>')
    s.extend(labs)
    s.append(text(cx, cy + 5, '肤色', 15, 800, INK, 'middle') + text(cx, cy + 25, '挤在橙色', 12, 700, MUTED, 'middle'))
    x = 380
    s.append(text(x, 60, '选中「橙色」以后：', 16, 800))
    rows = [('色相', '往左：偏红、偏粉（健康）', '往右：偏黄（容易蜡黄）'), ('饱和度', '往左：淡、苍白', '往右：浓、像晒伤'), ('明亮度', '往左：暗、脏', '往右：透亮（别超过 +20）')]
    for i, (k, a, b) in enumerate(rows):
        y = 100 + i * 70
        s.append(label(x, y, k, YEL1, 14) + text(x + 90, y - 2, a, 13, 700) + text(x + 90, y + 20, b, 13, 700))
    s.append(text(x, 320, '为什么不直接调「饱和度」：它会让假发、衣服、', 13, 600, MUTED))
    s.append(text(x, 342, '背景一起变。混合只动这一格颜色，别的不受影响。', 13, 600, MUTED))
    save('p-hsl', svg(Wd, Hd, ''.join(s), '颜色混合：肤色主要落在橙色，三个滑块各管色相、饱和度、明亮度'))


# ---------- 案例 ----------
def case_lr(name, lab, fill, **kw):
    Wd, Hd = 640, 520
    ph, g = portrait(20, 20, 600, 480, uid='cl' + name, s=92, fy=200, **kw)
    extra = ''
    if kw.pop('_sky', False):
        pass
    save(name, svg(Wd, Hd, ph + extra + label(34, 490, lab, fill, 15) if fill != 'end' else ph + label(606, 490, lab, VIO1, 15, 'end'), lab))


def case_sky(name, lab, after):
    Wd, Hd = 640, 520
    ph, g = portrait(20, 20, 600, 480, uid='cs' + name, s=92, fy=200, bg='outdoor', shade='3d' if after else 'flat', expo=0 if after else -0.32)
    sky = ('<defs><linearGradient id="sk%s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF" stop-opacity="%s"/><stop offset="1" stop-color="#FFF" stop-opacity="0"/></linearGradient></defs>'
           % (name, '.35' if after else '.95')) + f'<rect x="20" y="20" width="600" height="220" fill="url(#sk{name})"/>'
    s = ph + sky + (label(606, 490, lab, VIO1, 15, 'end') if after else label(34, 490, lab, YEL1, 15))
    save(name, svg(Wd, Hd, s, lab))


def lr_cases():
    case_lr('case-lr-venue-before', '修之前：偏黄、偏暗', YEL1, bg='venue', shade='flat', cast='#F59E0B', cast_t=0.26, expo=-0.22, crowd=True)
    case_lr('case-lr-venue-after', '修之后：白墙回到白色，脸亮了', 'end', bg='venue', shade='flat', crowd=True)
    case_sky('case-lr-sky-before', '修之前：天空一片白，脸很暗', False)
    case_sky('case-lr-sky-after', '修之后：天空有颜色，脸提亮', True)
    case_lr('case-lr-stage-before', '修之前：舞台灯，皮肤发紫', YEL1, bg='venue', bgdark=True, shade='3d', cast='#C026D3', cast_t=0.24)
    case_lr('case-lr-stage-after', '修之后：肤色回正，灯光氛围留一点', 'end', bg='venue', bgdark=True, shade='3d', cast='#C026D3', cast_t=0.06)


# ======================= 4.3 皮肤处理 =======================
def skin_patch(x, y, w, h, uid, pores=True, acne=False, smooth=False, mottled=False):
    s = f'<defs><clipPath id="sp{uid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/></clipPath></defs><g clip-path="url(#sp{uid})">'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{SKIN}"/>'
    s += f'<rect x="{x}" y="{y + h * 0.55}" width="{w}" height="{h * 0.45}" fill="{SKIN2}" fill-opacity=".5"/>' if not smooth else f'<rect x="{x}" y="{y + h * 0.5}" width="{w}" height="{h * 0.5}" fill="{SKIN2}" fill-opacity=".35" filter="url(#blur6)"/>'
    if mottled:
        s += E(x + w * 0.3, y + h * 0.4, w * 0.18, h * 0.25, '#F08080', 0.35) + E(x + w * 0.75, y + h * 0.6, w * 0.14, h * 0.2, MARK, 0.35)
    if pores:
        rnd = random.Random(11)
        for _ in range(int(w * h / 90)):
            s += f'<circle cx="{x + rnd.uniform(2, w - 2):.1f}" cy="{y + rnd.uniform(2, h - 2):.1f}" r="{rnd.uniform(0.8, 1.6):.1f}" fill="{SKIN3}" fill-opacity=".6"/>'
    if acne:
        for a, b in [(0.25, 0.35), (0.62, 0.6), (0.82, 0.3)]:
            s += f'<circle cx="{x + w * a:.1f}" cy="{y + h * b:.1f}" r="5" fill="{ACNE}"/><circle cx="{x + w * a - 1.5:.1f}" cy="{y + h * b - 1.5:.1f}" r="1.5" fill="{WHITE}"/>'
    s += '</g>' + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="{INK}" stroke-width="2"/>'
    return s


def wave(x, y, w, amp, kind):
    pts = []
    for k in range(241):
        t = k / 240
        v = math.sin(t * math.pi * 2) * 0.6
        if kind in ('orig', 'fixed'):
            v += 0.18 * math.sin(t * 90) + 0.1 * math.sin(t * 157)
        if kind == 'orig':
            for c in (0.2, 0.58, 0.83):
                v += 0.9 * math.exp(-((t - c) / 0.012) ** 2)
        pts.append((x + t * w, y - v * amp))
    return f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{VIO7}" stroke-width="2.2"/>'


def p_freq():
    Wd, Hd = 780, 470
    s = [BLUR, card(10, 10, 760, 450)]
    s.append(text(30, 46, '把皮肤的明暗画成一条线：大的起伏是脸的立体（低频），细碎的抖动是毛孔和细纹（高频），尖刺是痘。', 14, 800))
    rows = [('原皮肤', '起伏 + 细纹 + 痘', 'orig', dict(pores=True, acne=True, mottled=True), YEL1),
            ('整片模糊磨皮', '痘没了，细纹也没了 → 塑料脸', 'blur', dict(pores=False, smooth=True), RED1),
            ('本课做法', '克隆去掉尖刺，喷枪抹匀色块，细纹留着', 'fixed', dict(pores=True), MINT1)]
    for i, (t, d, k, kw, fill) in enumerate(rows):
        y = 80 + i * 124
        s.append(label(30, y + 20, t, fill, 14))
        s.append(text(30, y + 50, d, 12, 700, MUTED))
        s.append(f'<line x1="260" y1="{y + 52}" x2="600" y2="{y + 52}" stroke="{LINE}" stroke-width="1.5"/>')
        s.append(wave(260, y + 52, 340, 38, k))
        s.append(skin_patch(620, y + 6, 130, 92, f'f{i}', **kw))
    s.append(text(30, 446, 'PS 的高低频把这两种分到两层分开修。Procreate 没有这个功能，所以本课分成三步手动做。', 13, 600, MUTED))
    save('p-freq', svg(Wd, Hd, ''.join(s), '皮肤的低频和高频：模糊磨皮把细纹一起抹掉，所以像塑料'))


def u_skin_layers():
    ph, g = closeup('sl', blem=True, red=True, pores=True, shade='flat')
    rows = [dict(name='质感', sub='覆盖 · 最后再加', thumb='noise', mode=''), dict(name='补色', sub='正常 · 喷枪补肤色', thumb='skin'),
            dict(name='去瑕疵', sub='原图的副本 · 克隆在这层', thumb='photo', sel=True), dict(name='原图', thumb='photo', lock=True)]
    lp, (lx, ly, lw, lh, rh) = lpanel(rows, hl=2)
    s = scr(ph + lp, active='layers')
    s += ring(*icon_pos('layers'), 18)
    s += badge(lx - 14, ly + 44 + 2 * 52 + 23, 1) + badge(lx - 14, ly + 44 + 1 * 52 + 23, 2) + badge(lx - 14, ly + 44 + 23, 3)
    s += label(lx, ly + lh + 36, '① 克隆去痘：直接改「去瑕疵」层的像素', YEL1, 13)
    s += label(lx, ly + lh + 68, '② 补色：新的空图层，随时能擦、能降不透明度', YEL1, 13)
    s += label(lx, ly + lh + 100, '③ 质感：磨过头的地方补颗粒', YEL1, 13)
    s += note('示意图')
    save('u-skin-layers', svg(W, H, s, '皮肤处理的图层：原图锁定，去瑕疵、补色、质感分开'))


def u_clone_skin():
    ph, g = closeup('cs', blem=True, pores=True, shade='flat')
    dx, dy = F(g, 0.42, 0.62)
    tx, ty = F(g, 0.48, 0.34)
    content = ph + clone_disc(dx, dy) + f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="10" fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-dasharray="4 3"/>'
    content += f'<line x1="{dx:.1f}" y1="{dy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" stroke="{WHITE}" stroke-width="1.5" stroke-dasharray="3 4"/>'
    s = scr(content + tool_sliders([('画笔尺寸', 0.06), ('强度', 0.85)]), active='adjust')
    s += ring(*icon_pos('adjust'), 18) + ring(*icon_pos('brush'), 18)
    s += badge(dx + 24, dy + 20, 1) + badge(tx + 22, ty - 10, 2) + badge(icon_pos('brush')[0] - 24, 60, 3)
    s += label(64, 120, '① 圆盘放在痘旁边干净的皮肤上', YEL1, 13)
    s += label(64, 152, '   亮度、毛孔方向要接近；长按锁定', WHITE, 13)
    s += label(64, 184, '② 笔刷比痘大一圈，点一两下', YEL1, 13)
    s += label(560, 120, '③ 点画笔图标，换成「软画笔」', YEL1, 13)
    s += label(560, 152, '   克隆的边缘就是软的', WHITE, 13)
    s += note('示意图：调整 › 克隆')
    save('u-clone-skin', svg(W, H, s, '克隆去痘：圆盘取样旁边的皮肤，用软画笔点在痘上'))


def u_soft_brush():
    ph, g = closeup('sb', red=True, pores=True, shade='flat')
    lib = brush_lib(400, 62, ['最近', '素描', '着墨', '绘图', '上漆', '气笔修饰', '纹理'], '气笔修饰', ['软画笔', '中等画笔', '硬画笔', '软混合'], '软画笔', w=380)
    s = scr(ph + lib, active='brush', op=0.08, hl='op')
    s += ring(*icon_pos('brush'), 18)
    s += badge(icon_pos('brush')[0] - 24, 60, 1) + badge(392, 62 + 44 + 5 * 36 + 15, 2) + badge(66, 340, 3)
    s += label(400, 410, '② 「气笔修饰」→「软画笔」', YEL1, 13)
    s += label(400, 442, '   （找不到这组时，在画笔库里切到「经典库」）', WHITE, 13)
    s += label(80, 470, '③ 不透明度拉到 5%～10%', YEL1, 13)
    s += note('示意图，画笔名称以实际界面为准')
    save('u-soft-brush', svg(W, H, s, '选气笔修饰里的软画笔，不透明度降到 5%～10%'))


def u_skin_paint():
    BL = BLUR
    ph, g = closeup('spn', red=True, pores=True, shade='flat')
    ex, ey = F(g, 0.62, 0.55)
    rx_, ry_ = F(g, 0.2, 0.3)
    strokes = ''.join(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="22" fill="{SKIN}" fill-opacity=".35" filter="url(#blur6)"/>' for a, b in [F(g, 0.2, 0.28), F(g, 0.25, 0.32), F(g, 0.16, 0.34)])
    content = BL + ph + strokes + eyedrop(ex, ey, SKIN, '#FFFFFF')
    lp, (lx, ly, lw, lh, rh) = lpanel([dict(name='补色', sub='正常 · 100%', thumb='skin', sel=True), dict(name='去瑕疵', thumb='photo')], x=560, w=210)
    s = scr(content + lp, active='brush', op=0.08, hl='op')
    s += cur_color(SKIN)
    s += badge(ex + 34, ey - 20, 1) + badge(rx_ - 40, ry_ - 30, 2)
    s += label(64, 112, '① 在泛红旁边正常的皮肤上长按，吸取颜色', YEL1, 13)
    s += label(64, 144, '② 在「补色」层上轻轻扫过泛红，一笔一笔叠', YEL1, 13)
    s += label(64, 176, '   每换一个区域重新吸一次色', WHITE, 13)
    s += note('示意图')
    save('u-skin-paint', svg(W, H, s, '长按吸取旁边的肤色，在补色层上用低透明度软画笔扫过'))


def u_noise():
    ph, g = closeup('nz', pores=False, shade='flat')
    rnd = random.Random(5)
    grain = ''.join(f'<rect x="{CX + rnd.uniform(0, CW):.1f}" y="{CY + rnd.uniform(0, CH):.1f}" width="1.6" height="1.6" fill="{rnd.choice(["#000", "#FFF"])}" fill-opacity=".18"/>' for _ in range(1600))
    lp, (lx, ly, lw, lh, rh) = lpanel([dict(name='质感', sub='覆盖 · 30%', thumb='noise', sel=True, mode=''), dict(name='补色', thumb='skin')], x=560, w=210)
    s = scr(ph + grain + topinfo('杂色 12%') + lp + tool_sliders([('比例', 0.1), ('倍频', 0.3), ('湍流', 0.0)], buttons=('云', '巨浪', '背脊'), hl='背脊'), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += badge(400 - 70, 76, 1) + badge(POS['背脊'][0] + 31, POS['背脊'][1] - 12, 2)
    s += label(64, 112, '新建图层填 50% 灰，模式「覆盖」', YEL1, 13)
    s += label(64, 144, '① 调整 › 杂色，手指左右滑调强弱', YEL1, 13)
    s += label(64, 176, '② 选「背脊」，比例调小，颗粒最细', YEL1, 13)
    s += label(64, 208, '再把图层不透明度降到 20%～40%', WHITE, 13)
    save('u-noise', svg(W, H, s, '用杂色在覆盖图层上补回皮肤颗粒'))


def case_face(name, lab, after, blur=False, **kw):
    Wd, Hd = 640, 520
    ph, g = portrait(20, 20, 600, 480, uid='cf' + name, fx=320, fy=262, s=188, **kw)
    if blur:
        ph = BLUR + f'<g filter="url(#blur3)">' + ph + '</g>'
    s = ph + (label(606, 490, lab, VIO1, 15, 'end') if after else label(34, 490, lab, YEL1, 15))
    save(name, svg(Wd, Hd, s, lab))


def skin_cases():
    case_face('case-acne-before', '修之前：痘、痘印、鼻翼泛红', False, bg='plain', blem=True, red=True, pores=True)
    case_face('case-acne-after', '修之后：痘没了，毛孔还在', True, bg='plain', pores=True)
    case_face('case-shine-before', '修之前：额头、鼻尖油光，脸颊泛红', False, bg='venue', shine=True, red=True, pores=True, shade='flat')
    case_face('case-shine-after', '修之后：油光压下去，留一点自然高光', True, bg='venue', pores=True, shade='flat')
    case_face('case-plastic-before', '修之前：美颜 App 磨过，像塑料', False, bg='plain', blur=True, shade='flat')
    case_face('case-plastic-after', '修之后：补回颗粒，光影加回来', True, bg='plain', pores=True, shade='3d')


# ======================= 4.4 光影重塑 =======================
def softlight(a, b):
    if b <= 0.5:
        return a - (1 - 2 * b) * a * (1 - a)
    d = ((16 * a - 12) * a + 4) * a if a <= 0.25 else math.sqrt(a)
    return a + (2 * b - 1) * (d - a)


def sl_rgb(base, b, op=1.0):
    r, g_, bl = (int(base[i:i + 2], 16) / 255 for i in (1, 3, 5))
    out = []
    for a in (r, g_, bl):
        v = softlight(a, b) * op + a * (1 - op)
        out.append(int(round(max(0, min(1, v)) * 255)))
    return '#%02X%02X%02X' % tuple(out)


def p_overlay():
    Wd, Hd = 780, 440
    s = [card(10, 10, 760, 420)]
    x0, y0, w, h = 70, 70, 280, 280
    s.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>')
    for i in range(1, 4):
        s.append(f'<line x1="{x0 + w * i / 4}" y1="{y0}" x2="{x0 + w * i / 4}" y2="{y0 + h}" stroke="{LINE}"/><line x1="{x0}" y1="{y0 + h * i / 4}" x2="{x0 + w}" y2="{y0 + h * i / 4}" stroke="{LINE}"/>')
    curves = [(1.0, PINK, '涂纯白', 3), (0.55, PINK, '50% 灰上涂 10% 白', 2), (0.5, INK, '中性灰：不变', 3), (0.45, VIO, '50% 灰上涂 10% 黑', 2), (0.0, VIO, '涂纯黑', 3)]
    for b, c, n, sw in curves:
        pts = ' '.join(f'{x0 + k / 50 * w:.1f},{y0 + h - softlight(k / 50, b) * h:.1f}' for k in range(51))
        dash = '' if b in (0, 0.5, 1) else 'stroke-dasharray="6 4"'
        s.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{sw}" {dash}/>')
    s.append(text(x0 + w / 2, y0 + h + 30, '底下照片的亮度 →', 13, 700, INK, 'middle'))
    s.append(f'<text x="{x0 - 22}" y="{y0 + h / 2}" font-size="13" font-weight="700" fill="{INK}" text-anchor="middle" transform="rotate(-90 {x0 - 22} {y0 + h / 2})">叠加后的亮度 →</text>')
    s.append(label(x0 + 10, y0 + 30, '涂白：整条线往上', PINK1, 12) + label(x0 + w - 10, y0 + h - 16, '涂黑：往下', VIO1, 12, 'end'))
    s.append(text(x0, 46, '「柔光」模式：图层颜色和 50% 灰比', 15, 800))
    # 右边：皮肤色块实际效果
    x1 = 420
    s.append(text(x1, 80, '同一块皮肤，上面叠一层「柔光」：', 14, 800))
    rows = [('中性灰（50%）', 0.5, 1.0, '看不出来，等于没涂'), ('10% 的白', 1.0, 0.1, '亮了一点点'), ('10% 的黑', 0.0, 0.1, '暗了一点点'), ('100% 的黑', 0.0, 1.0, '暗得发脏，所以要低透明度')]
    for i, (n, b, op, d) in enumerate(rows):
        y = 104 + i * 70
        s.append(f'<rect x="{x1}" y="{y}" width="60" height="48" rx="6" fill="{SKIN}" stroke="{INK}" stroke-width="1.5"/>')
        s.append(arrow(x1 + 66, y + 24, x1 + 96, y + 24, INK, 2))
        s.append(f'<rect x="{x1 + 102}" y="{y}" width="60" height="48" rx="6" fill="{sl_rgb(SKIN, b, op)}" stroke="{INK}" stroke-width="1.5"/>')
        s.append(text(x1 + 176, y + 20, n, 13, 800) + text(x1 + 176, y + 40, d, 12, 600, MUTED))
    s.append(text(x1, 398, '「覆盖」原理一样，只是同样的笔画效果更强、更容易变脏。', 12, 600, MUTED))
    save('p-overlay', svg(Wd, Hd, ''.join(s), '柔光模式：中性灰不改变画面，比灰亮的变亮，比灰暗的变暗'))


HI_ZONES = [('额头中间', 0, -0.82, 0.3, 0.14, 0), ('鼻梁', 0.02, 0.0, 0.07, 0.3, 0), ('颧骨上方', 0.5, -0.03, 0.2, 0.07, -8), ('颧骨上方', -0.5, -0.03, 0.2, 0.07, 8), ('下巴', 0, 0.86, 0.15, 0.08, 0)]
LO_ZONES = [('太阳穴', 0.88, -0.55, 0.12, 0.28, 0), ('太阳穴', -0.88, -0.55, 0.12, 0.28, 0), ('颧骨下方', 0.68, 0.33, 0.25, 0.09, 28), ('颧骨下方', -0.68, 0.33, 0.25, 0.09, -28),
            ('鼻侧', 0.14, 0.08, 0.05, 0.22, 0), ('鼻侧', -0.14, 0.08, 0.05, 0.22, 0), ('下颌下方', 0, 1.1, 0.6, 0.12, 0)]


def zones_svg(g, op=0.6):
    s = f'<g transform="translate({g["fx"]:.1f},{g["fy"]:.1f}) scale({g["s"]:.2f})">'
    for _, a, b, rx, ry, rot in HI_ZONES:
        s += E(a, b, rx, ry, YEL, op, rot, f'stroke="{INK}" stroke-width="1.5" {NS}')
    for _, a, b, rx, ry, rot in LO_ZONES:
        s += E(a, b, rx, ry, VIO, op, rot, f'stroke="{INK}" stroke-width="1.5" {NS}')
    return s + '</g>'


def p_light_map():
    Wd, Hd = 780, 500
    s = [card(10, 10, 760, 480)]
    ph, g = portrait(30, 30, 380, 450, uid='lm', bg='plain', shade='flat', bangs=False, fx=220, fy=240, s=130, frame=False)
    s.append(ph + zones_svg(g))
    s.append(arrow(70, 60, 120, 110, INK, 3) + text(40, 54, '主光', 13, 800))
    x = 440
    s.append(label(x, 60, '高光区：用白色提亮', YEL1, 14))
    for i, t in enumerate(['额头中间', '鼻梁（一条细线，别涂宽）', '颧骨上方', '下巴']):
        s.append(text(x + 10, 92 + i * 24, '· ' + t, 13, 700))
    s.append(label(x, 214, '暗区：用黑色压暗', VIO1, 14))
    for i, t in enumerate(['太阳穴', '颧骨下方（斜着往嘴角方向）', '鼻侧', '下颌下方（脸和脖子分开）']):
        s.append(text(x + 10, 246 + i * 24, '· ' + t, 13, 700))
    s.append(text(x, 372, '光从哪边来，那一侧的高光可以再亮一点，', 13, 600, MUTED))
    s.append(text(x, 394, '背光一侧的暗区可以再深一点。', 13, 600, MUTED))
    s.append(text(x, 430, '这张图是正面平光的通用位置，', 13, 600, MUTED))
    s.append(text(x, 452, '实际照片要先看原本的光在哪（3.1 课）。', 13, 600, MUTED))
    save('p-light-map', svg(Wd, Hd, ''.join(s), '面部光影地图：黄色是高光区，紫色是暗区'))


def value_panel(x, y):
    s = panel(x, y, 220, 196, '颜色 · 值')
    rows = [('色相', '0°', 0.0), ('饱和度', '0%', 0.0), ('亮度', '50%', 0.5)]
    for i, (k, v, f) in enumerate(rows):
        yy = y + 60 + i * 38
        s += text(x + 14, yy, k, 12, 700, UITEXT) + text(x + 206, yy, v, 12, 800, UITEXT, 'end')
        s += f'<rect x="{x + 14}" y="{yy + 8}" width="192" height="6" rx="3" fill="#6B7280"/><circle cx="{x + 14 + 192 * f:.1f}" cy="{yy + 11}" r="7" fill="{WHITE}" stroke="{INK}"/>'
    s += text(x + 14, y + 182, '十六进制', 12, 700, UITEXT) + f'<rect x="{x + 100}" y="{y + 166}" width="106" height="24" rx="6" fill="{UIBAR}"/>' + text(x + 153, y + 183, '808080', 13, 800, WHITE, 'middle')
    s += ringrect(x + 94, y + 162, 118, 32)
    return s


def u_db_fill():
    ph, g = closeup('dbf', shade='flat', pores=True)
    lp, (lx, ly, lw, lh, rh) = lpanel([dict(name='光影', thumb='blank', sel=True), dict(name='补色', thumb='skin'), dict(name='去瑕疵', thumb='photo')], hl=0)
    menu = options_menu(lx - 150, ly + 44, 140, LAYER_OPTS[:6], hl='填充图层')
    s = scr(ph + value_panel(70, 300) + lp + menu, active='layers')
    s += cur_color('#808080') + ring(*icon_pos('color'), 18)
    s += badge(60, 466, 1) + badge(lx - 160, ly + 44 + 8 + 3 * 32 + 16, 2)
    s += label(lx, ly + lh + 36, '① 颜色设成 50% 灰（808080）', YEL1, 13)
    s += label(lx, ly + lh + 68, '② 新建「光影」层，点两次 → 填充图层', YEL1, 13)
    s += note('示意图，菜单项以实际界面为准')
    save('u-db-fill', svg(W, H, s, '颜色选 50% 灰，新建图层并填充'))


def u_db_mode():
    ph, g = closeup('dbm', shade='flat', pores=True)
    lp, (lx, ly, lw, lh, rh) = lpanel([dict(name='光影', sub='柔光', thumb='gray', sel=True, mode=''), dict(name='补色', thumb='skin'), dict(name='去瑕疵', thumb='photo')], hl='mode0')
    pop = blend_pop(lx + 40, ly + lh + 10, 200, ['覆盖', '柔光', '强光', '亮光'], '柔光')
    s = scr(ph + lp + pop, active='layers')
    s += badge(lx + lw - 72, ly + 54, 1) + badge(lx + 254, ly + lh + 10 + 60 + 30 + 13, 2)
    s += label(36, 486, '① 点字母  ② 选「柔光」（想要更强选「覆盖」）：灰色马上消失', WHITE, 14)
    s += note('示意图')
    save('u-db-mode', svg(W, H, s, '把灰色图层的混合模式改成柔光，灰色看不见了'))


def u_db_paint(kind):
    ph, g = closeup('dbp' + kind, shade='flat', pores=True)
    zones = HI_ZONES if kind == 'dodge' else LO_ZONES
    col = WHITE if kind == 'dodge' else '#000000'
    marks = BLUR + f'<g transform="translate({g["fx"]:.1f},{g["fy"]:.1f}) scale({g["s"]:.2f})">'
    for _, a, b, rx, ry, rot in zones:
        marks += E(a, b, rx, ry, col, 0.35, rot, 'filter="url(#blur3)"')
        marks += E(a, b, rx * 1.15, ry * 1.25, 'none', 1, rot, f'stroke="{YEL}" stroke-width="2" stroke-dasharray="5 4" {NS}')
    marks += '</g>'
    s = scr(ph + marks, active='brush', op=0.08, hl='op')
    s += cur_color(col) + ring(*icon_pos('color'), 18)
    s += badge(66, 340, 1) + badge(icon_pos('color')[0] - 24, 60, 2)
    if kind == 'dodge':
        s += label(560, 120, '② 颜色选纯白', YEL1, 13)
        s += label(560, 152, '在虚线框里来回轻扫', YEL1, 13)
        s += label(560, 184, '一个地方扫 3～5 遍', WHITE, 13)
    else:
        s += label(560, 120, '② 颜色换成纯黑', YEL1, 13)
        s += label(560, 152, '涂暗区，比高光再轻一点', YEL1, 13)
        s += label(560, 184, '颧骨下方顺着骨头斜着扫', WHITE, 13)
    s += label(80, 470, '① 软画笔，不透明度 5%～10%，尺寸比要涂的区域稍大', YEL1, 13)
    s += note('示意图（虚线框只是提示位置）')
    save('u-db-' + kind, svg(W, H, s, '在柔光图层上用低透明度软画笔涂' + ('白色提亮高光区' if kind == 'dodge' else '黑色压暗暗区')))


def u_db_check():
    ph, g = closeup('dbc', shade='3d', pores=True, gray=True)
    rows = [dict(name='灰度观察', sub='颜色', thumb='black', mode='', vis=True), dict(name='光影', sub='柔光', thumb='gray', sel=True, mode=''),
            dict(name='补色', thumb='skin'), dict(name='去瑕疵', thumb='photo'), dict(name='原图', thumb='photo', lock=True)]
    lp, (lx, ly, lw, lh, rh) = lpanel(rows, hl=0)
    s = scr(ph + lp, active='layers')
    s += badge(lx + lw - 22, ly + 44 + 4, 1)
    s += label(lx, ly + lh + 36, '① 勾上「灰度观察」：只看明暗', YEL1, 13)
    s += label(lx, ly + lh + 68, '   涂完再关掉，看彩色有没有发脏', WHITE, 13)
    s += label(36, 520, '灰度里检查：脸有没有分出亮面和暗面；有没有一块块的脏斑；下颌和脖子分开了没有', WHITE, 13)
    s += note('示意图')
    save('u-db-check', svg(W, H, s, '打开灰度观察层检查光影'))


def db_cases():
    case_face('case-flat-before', '修之前：阴天平光，脸像一张纸', False, bg='outdoor', shade='flat', pores=True)
    case_face('case-flat-after', '修之后：额头、鼻梁、颧骨亮起来，轮廓出来了', True, bg='outdoor', shade='3d', pores=True)
    case_face('case-flash-before', '修之前：正面闪光，中间一片亮，四周发灰', False, bg='venue', shade='flash', pores=True)
    case_face('case-flash-after', '修之后：中间收亮，两侧和下颌加暗', True, bg='venue', shade='3d', pores=True)
    case_face('case-messy-before', '修之前：阴阳脸，右半边暗一大截', False, bg='outdoor', shade='messy', pores=True)
    case_face('case-messy-after', '修之后：暗的一侧提亮，保留方向感', True, bg='outdoor', shade='3d', pores=True)


# ======================= 4.5 五官和妆面 =======================
def hairline_cap():
    return P('M-0.98,-0.3 C-1.0,-1.0 -0.6,-1.3 0,-1.3 C0.6,-1.3 1.0,-1.0 0.98,-0.3 C0.9,-0.75 0.6,-1.02 0,-1.05 C-0.6,-1.02 -0.9,-0.75 -0.98,-0.3 Z', fill=HAIR, stroke=INK, sw=2)


def p_face_ratio():
    Wd, Hd = 780, 520
    s = [card(10, 10, 760, 500)]
    ph, g = portrait(30, 30, 420, 470, uid='fr', bg='plain', shade='flat', bangs=False, fx=240, fy=250, s=140, frame=False)
    s.append(ph)
    s.append(f'<g transform="translate({g["fx"]},{g["fy"]}) scale({g["s"]})">' + hairline_cap() + '</g>')
    fx, fy, k = g['fx'], g['fy'], g['s']
    for yy, n in [(-1.05, '发际线'), (-0.38, '眉毛'), (0.35, '鼻底'), (1.03, '下巴')]:
        Y = fy + yy * k
        s.append(f'<line x1="{fx - 1.25 * k:.0f}" y1="{Y:.0f}" x2="{fx + 1.35 * k:.0f}" y2="{Y:.0f}" stroke="{MINT7}" stroke-width="2.5" stroke-dasharray="7 5"/>')
        s.append(text(fx + 1.4 * k, Y + 5, n, 12, 800, MINT7))
    for (a, b, n) in [(-1.05, -0.38, '上庭'), (-0.38, 0.35, '中庭'), (0.35, 1.03, '下庭')]:
        s.append(label(fx - 1.3 * k, fy + (a + b) / 2 * k + 6, n, MINT1, 12, 'middle'))
    xs = [-0.98, -0.6, -0.2, 0.2, 0.6, 0.98]
    for a in xs:
        X = fx + a * k
        s.append(f'<line x1="{X:.0f}" y1="{fy - 0.3 * k:.0f}" x2="{X:.0f}" y2="{fy + 0.02 * k:.0f}" stroke="{VIO7}" stroke-width="2.5"/>')
    for i in range(5):
        X = fx + (xs[i] + xs[i + 1]) / 2 * k
        s.append(text(X, fy + 0.15 * k, str(i + 1), 13, 900, VIO7, 'middle'))
    x = 480
    s.append(label(x, 60, '三庭：竖着三段差不多长', MINT1, 14))
    s.append(text(x, 94, '发际线→眉毛→鼻底→下巴', 13, 700))
    s.append(text(x, 118, '下庭稍长一点（约 1 : 1 : 1.1）更上镜', 13, 600, MUTED))
    s.append(label(x, 166, '五眼：横着五个眼睛宽', VIO1, 14))
    s.append(text(x, 200, '两眼中间正好放下一只眼', 13, 700))
    s.append(text(x, 224, '眼尾到脸边各一只眼', 13, 700))
    s.append(label(x, 278, '修图时只用来找"哪里偏了"', YEL1, 14))
    s.append(text(x, 312, '真人脸不会完全标准，标准反而没特点。', 13, 600, MUTED))
    s.append(text(x, 336, '只修明显的不对称：一只眼小一圈、', 13, 600, MUTED))
    s.append(text(x, 360, '一边嘴角低、一边下颌宽。', 13, 600, MUTED))
    s.append(text(x, 394, '每次改动不超过一个眼睛宽的 1/10，', 13, 600, MUTED))
    s.append(text(x, 418, '改完和原图来回对比，还认得出是本人。', 13, 600, MUTED))
    s.append(text(x, 460, '修脸型之前先问 coser（0.3 课沟通表）。', 13, 700, RED7))
    save('p-face-ratio', svg(Wd, Hd, ''.join(s), '三庭五眼：竖向三段、横向五个眼宽'))


def u_guides():
    ph, g = closeup('gd', shade='3d', eye_dy=0.05, eye_sc=0.9)
    fx, fy, k = g['fx'], g['fy'], g['s']
    lines = ''
    for yy in (-0.16,):
        lines += f'<line x1="{CX + 10}" y1="{fy + yy * k:.0f}" x2="{CX + CW - 10}" y2="{fy + yy * k:.0f}" stroke="{MINT}" stroke-width="3"/>'
    lines += f'<line x1="{fx:.0f}" y1="{CY + 10}" x2="{fx:.0f}" y2="{CY + CH - 10}" stroke="{MINT}" stroke-width="3"/>'
    for yy in (0.35, 0.6):
        lines += f'<line x1="{CX + 10}" y1="{fy + yy * k:.0f}" x2="{CX + CW - 10}" y2="{fy + yy * k:.0f}" stroke="{MINT}" stroke-width="2" stroke-dasharray="6 5"/>'
    lp, (lx, ly, lw, lh, rh) = lpanel([dict(name='辅助线', thumb='blank', sel=True), dict(name='五官', thumb='photo')], x=560, w=210)
    s = scr(ph + lines + lp, active='brush')
    s += ring(*icon_pos('brush'), 18)
    s += badge(fx + 14, CY + 30, 1) + badge(CX + CW - 24, fy - 0.16 * k - 16, 2)
    s += label(560, 230, '① 画一条竖线过鼻梁和人中', YEL1, 13)
    s += label(560, 262, '② 横线贴着右眼的眼角', YEL1, 13)
    s += label(560, 294, '左眼明显低、小一圈', WHITE, 13)
    s += label(560, 326, '画完停住，线会变直', WHITE, 13)
    s += note('示意图')
    save('u-guides', svg(W, H, s, '新建辅助线图层，用速创形状画中线和眼角线'))


def u_eye_sel():
    ph, g = closeup('es', shade='3d', eye_dy=0.05, eye_sc=0.9)
    cx, cy = F(g, -0.395, -0.11)
    k = g['s']
    pts = [(cx - 0.3 * k, cy - 0.05 * k), (cx - 0.15 * k, cy - 0.2 * k), (cx + 0.15 * k, cy - 0.2 * k), (cx + 0.28 * k, cy - 0.03 * k), (cx + 0.12 * k, cy + 0.12 * k), (cx - 0.2 * k, cy + 0.1 * k)]
    d = 'M' + ' L'.join(f'{a:.0f} {b:.0f}' for a, b in pts) + ' Z'
    sel = f'<path d="{d}" fill="{UIBLUE}" fill-opacity=".1" stroke="{WHITE}" stroke-width="2.5"/><path d="{d}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 6"/>'
    s = scr(ph + sel + bottom_bar(SEL_ROWS, active=('手绘',), hl='羽化'), active='select', side=False)
    s += ring(*icon_pos('select'), 18) + badge(icon_pos('select')[0] + 24, 60, 1)
    bx, by, bw, bh = POS['羽化']
    s += badge(bx + bw + 10, by + 20, 3) + badge(POS['手绘'][0] + 20, POS['手绘'][1] - 14, 2)
    s += badge(cx + 0.32 * k, cy - 0.2 * k, 4)
    s += label(560, 120, '② 手绘：沿眉毛下方到', YEL1, 13) + label(560, 152, '   眼袋下方圈一圈，留点皮肤', WHITE, 13)
    s += label(560, 184, '③ 羽化：边缘变软，接缝不明显', YEL1, 13)
    s += label(560, 216, '④ 再点「拷贝并粘贴」，', YEL1, 13) + label(560, 248, '   用变换往上挪、稍微放大', WHITE, 13)
    s += note('示意图')
    save('u-eye-sel', svg(W, H, s, '手绘选取眼睛，羽化后拷贝并粘贴，再用变换微调'))


def u_liquify_face():
    ph, g = closeup('lf', shade='3d')
    jx, jy = F(g, 0.75, 0.6)
    content = ph + f'<circle cx="{jx:.0f}" cy="{jy:.0f}" r="42" fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-dasharray="5 4"/>' + arrow(jx + 30, jy, jx - 6, jy - 4, VIO7, 3, marker='arwv')
    s = scr(content + tool_sliders([('尺寸', 0.2), ('压力', 0.12), ('失真', 0.0), ('动力', 0.0)], mode='推', buttons=('调整', '重置')), active='adjust', side=False)
    s += ring(*icon_pos('adjust'), 18)
    s += badge(jx + 50, jy - 40, 1)
    s += label(560, 120, '尺寸：比要推的地方稍大', YEL1, 13)
    s += label(560, 152, '压力：10%～15%，比推身体还轻', YEL1, 13)
    s += label(560, 184, '① 从外往里，一下只推一点', YEL1, 13)
    s += label(560, 230, '五官本身（眼睛、嘴）尽量不推，', WHITE, 13)
    s += label(560, 262, '要移动用上一步的选区 + 变换', WHITE, 13)
    s += note('示意图：调整 › 液化')
    save('u-liquify-face', svg(W, H, s, '液化推模式：小压力修下颌、脸颊轮廓'))


def eye_zoom(uid, liner=True, bad=False):
    """放大到左眼的画布"""
    k = 620
    fx = CX + CW / 2 + 0.395 * k
    fy = CY + CH / 2 + 0.16 * k
    return portrait(CX, CY, CW, CH, uid=uid, fx=fx, fy=fy, s=k, shade='flat', liner=liner, liner_bad=bad, pores=True)


def u_liner():
    ph, g = eye_zoom('ln', liner=False, bad=True)
    k = g['s']
    # 新画的眼线（左眼，单位坐标 x 取负）
    def U(a, b):
        return F(g, a, b)
    p0, p1, p2 = U(-0.2, -0.16), U(-0.45, -0.3), U(-0.62, -0.19)
    tip = U(-0.72, -0.26)
    liner = (f'<path d="M{p0[0]:.0f} {p0[1]:.0f} Q{p1[0]:.0f} {p1[1]:.0f} {p2[0]:.0f} {p2[1]:.0f} L{tip[0]:.0f} {tip[1]:.0f}" fill="none" stroke="#3B2A33" stroke-width="9" stroke-linecap="round" stroke-opacity=".85"/>')
    lp, (lx, ly, lw, lh, rh) = lpanel([dict(name='眼线', sub='正片叠底 · 80%', thumb='darkmark', sel=True, mode=''), dict(name='五官', thumb='photo')], x=560, w=210)
    s = scr(ph + liner + lp + eyedrop(*U(-0.3, -0.27), '#3B2A33', '#3B2A33', r=18), active='brush', size=0.04, op=0.8, hl='size')
    s += cur_color('#3B2A33')
    s += badge(tip[0] + 18, tip[1] - 14, 2) + badge(66, 160, 1)
    s += label(64, 430, '① 尺寸 1%～3%，不透明度 70%～90%', YEL1, 13)
    s += label(560, 230, '吸睫毛根部的深棕色，不用纯黑', YEL1, 13)
    s += label(560, 262, '② 从内眼角贴睫毛根画到眼尾', YEL1, 13)
    s += label(560, 294, '   眼尾顺下眼睑延长线上挑', WHITE, 13)
    s += label(560, 326, '晕开的旧眼线先用克隆盖掉', WHITE, 13)
    s += note('示意图')
    save('u-liner', svg(W, H, s, '在正片叠底图层上补眼线'))


def mouth_zoom(uid, lip):
    k = 640
    fx = CX + CW / 2
    fy = CY + CH / 2 - 0.66 * k
    return portrait(CX, CY, CW, CH, uid=uid, fx=fx, fy=fy, s=k, shade='flat', lip=lip, pores=True)


def u_lip():
    ph, g = mouth_zoom('lp', LIPPALE)
    k = g['s']
    # 选区：嘴唇外轮廓
    d = (f'M{F(g, -0.26, 0.6)[0]:.0f} {F(g, -0.26, 0.6)[1]:.0f} Q{F(g, -0.12, 0.5)[0]:.0f} {F(g, -0.12, 0.5)[1]:.0f} {F(g, 0, 0.555)[0]:.0f} {F(g, 0, 0.555)[1]:.0f} '
         f'Q{F(g, 0.12, 0.5)[0]:.0f} {F(g, 0.12, 0.5)[1]:.0f} {F(g, 0.26, 0.6)[0]:.0f} {F(g, 0.26, 0.6)[1]:.0f} Q{F(g, 0.12, 0.77)[0]:.0f} {F(g, 0.12, 0.77)[1]:.0f} {F(g, 0, 0.77)[0]:.0f} {F(g, 0, 0.77)[1]:.0f} '
         f'Q{F(g, -0.12, 0.77)[0]:.0f} {F(g, -0.12, 0.77)[1]:.0f} {F(g, -0.26, 0.6)[0]:.0f} {F(g, -0.26, 0.6)[1]:.0f} Z')
    tint = f'<path d="{d}" fill="#E11D48" fill-opacity=".45"/>'
    sel = f'<path d="{d}" fill="none" stroke="{WHITE}" stroke-width="2.5"/><path d="{d}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 6"/>'
    lp, (lx, ly, lw, lh, rh) = lpanel([dict(name='唇色', sub='颜色 · 50%', thumb='pinkmark', sel=True, mode=''), dict(name='五官', thumb='photo')], x=560, w=210)
    s = scr(ph + tint + sel + lp, active='brush', size=0.5, op=0.6)
    s += cur_color('#E11D48')
    s += badge(F(g, -0.28, 0.55)[0] - 4, F(g, -0.28, 0.55)[1] - 24, 1) + badge(lx - 14, ly + 44 + 23, 2)
    s += label(560, 230, '① 手绘选取圈住嘴唇，羽化一点', YEL1, 13)
    s += label(560, 262, '② 新图层，模式设「颜色」', YEL1, 13)
    s += label(560, 294, '   选设定图的唇色，软画笔涂满', WHITE, 13)
    s += label(560, 326, '颜色模式只换色相，唇纹留着', WHITE, 13)
    s += label(560, 358, '想更深：加一层正片叠底', WHITE, 13)
    s += label(560, 390, '   不透明度 10%～20%', WHITE, 13)
    s += note('示意图')
    save('u-lip', svg(W, H, s, '选区圈住嘴唇，在颜色模式图层上换唇色'))


def u_blush():
    ph, g = closeup('bl', shade='3d', blush=False)
    strokes = BLUR + ''.join(f'<ellipse cx="{F(g, a * 0.6, 0.2)[0]:.0f}" cy="{F(g, a * 0.6, 0.2)[1]:.0f}" rx="{0.26 * g["s"]:.0f}" ry="{0.14 * g["s"]:.0f}" fill="{PINK}" fill-opacity=".35" filter="url(#blur6)"/>' for a in (1, -1))
    strokes += ''.join(f'<ellipse cx="{F(g, a * 0.8, 0.36)[0]:.0f}" cy="{F(g, a * 0.8, 0.36)[1]:.0f}" rx="{0.22 * g["s"]:.0f}" ry="{0.08 * g["s"]:.0f}" fill="#8B5E4A" fill-opacity=".25" filter="url(#blur6)" transform="rotate({a * 28} {F(g, a * 0.8, 0.36)[0]:.0f} {F(g, a * 0.8, 0.36)[1]:.0f})"/>' for a in (1, -1))
    lp, (lx, ly, lw, lh, rh) = lpanel([dict(name='腮红', sub='正片叠底 · 25%', thumb='pinkmark', sel=True, mode=''), dict(name='修容', sub='正片叠底 · 15%', thumb='mark', mode=''), dict(name='五官', thumb='photo')], x=560, w=210)
    s = scr(ph + strokes + lp, active='brush', size=0.9, op=0.3, hl='size')
    s += cur_color(PINK)
    s += badge(F(g, 0.6, 0.2)[0], F(g, 0.6, 0.2)[1] - 34, 1) + badge(F(g, -0.85, 0.36)[0] - 10, F(g, -0.85, 0.36)[1] + 30, 2) + badge(66, 140, 3)
    s += label(560, 290, '① 腮红：笑肌最高点往斜上扫', YEL1, 13)
    s += label(560, 322, '② 修容：颧骨下方', YEL1, 13)
    s += label(560, 354, '③ 画笔要大，一笔带过', YEL1, 13)
    s += label(560, 386, '边缘看不出来就对了', WHITE, 13)
    s += note('示意图')
    save('u-blush', svg(W, H, s, '腮红和修容：大号软画笔，正片叠底低不透明度'))


def u_brow():
    k = 560
    fx = CX + CW / 2 + 0.47 * k
    fy = CY + CH / 2 + 0.44 * k
    ph, g = portrait(CX, CY, CW, CH, uid='bw', fx=fx, fy=fy, s=k, shade='flat', brows='sparse', pores=True)
    rnd = random.Random(4)
    hairs = ''
    for i in range(16):
        t = i / 15
        a = -0.22 - t * 0.5
        b = -0.37 - math.sin(t * math.pi * 0.85) * 0.12
        x0, y0 = F(g, a, b + 0.03)
        ang = -60 + t * 75
        L = 18 + rnd.uniform(-3, 5)
        hairs += f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x0 + L * math.cos(math.radians(ang + 180)):.1f}" y2="{y0 + L * math.sin(math.radians(ang + 180)):.1f}" stroke="{BROW}" stroke-width="2.5" stroke-linecap="round"/>'
    lp, (lx, ly, lw, lh, rh) = lpanel([dict(name='眉毛', sub='正常 · 70%', thumb='mark', sel=True), dict(name='五官', thumb='photo')], x=560, w=210)
    s = scr(ph + hairs + lp, active='brush', size=0.03, op=0.7, hl='size')
    s += cur_color(BROW)
    s += label(560, 230, '眉头往上竖，眉尾往外斜着倒', YEL1, 13)
    s += label(560, 262, '一根一根画，别画成一整条', YEL1, 13)
    s += label(560, 294, '颜色吸原来眉毛最深处', WHITE, 13)
    s += label(560, 326, '画完整层高斯模糊 1%～2%', WHITE, 13)
    s += label(560, 358, '和照片的清晰度对上', WHITE, 13)
    s += note('示意图')
    save('u-brow', svg(W, H, s, '补画眉毛：细画笔按毛流一根根画'))


def mk_cases():
    case_face('case-makeup-before', '修之前：眼线晕开、唇色被灯吃掉、左眉缺', False, bg='venue', shade='3d', liner=False, liner_bad=True, lip=LIPPALE, brows='sparse', pores=True)
    case_face('case-makeup-after', '修之后：补眼线、唇色、眉毛和腮红', True, bg='venue', shade='3d', lip='#E11D48', blush=True, pores=True)
    case_face('case-asym-before', '修之前：左眼低、小一圈，头微歪', False, bg='outdoor', shade='3d', eye_dy=0.05, eye_sc=0.88, tilt=-3, pores=True)
    case_face('case-asym-after', '修之后：眼睛对齐，头回正', True, bg='outdoor', shade='3d', pores=True)


ALL = [p_four_checks, u_fit, u_flip41, u_gray_fill, u_gray_mode, u_reference,
       lambda: [case_venue(k) for k in ('color', 'gray', 'mark')], lambda: [case_backlit(k) for k in ('color', 'gray')],
       u_lr_light, u_lr_color, u_lr_mix, u_lr_curve, u_lr_mask, u_lr_export, p_lr_zones, p_wb, p_hsl, lr_cases,
       p_freq, u_skin_layers, u_clone_skin, u_soft_brush, u_skin_paint, u_noise, skin_cases,
       p_overlay, p_light_map, u_db_fill, u_db_mode, lambda: u_db_paint('dodge'), lambda: u_db_paint('burn'), u_db_check, db_cases,
       p_face_ratio, u_guides, u_eye_sel, u_liquify_face, u_liner, u_lip, u_blush, u_brow, mk_cases]

if __name__ == '__main__':
    for f in OUT and os.listdir(OUT):
        if f.endswith('.svg'):
            os.remove(os.path.join(OUT, f))
    for f in ALL:
        f()
    print('done', len(os.listdir(OUT)))
