"""示意图工具包：贴纸风格的人物、场景，以及 Procreate 界面示意（不是真实截图）。"""
import math

INK = '#1E293B'; CREAM = '#FFFDF5'; WHITE = '#FFFFFF'
VIO = '#8B5CF6'; VIO1 = '#EDE9FE'; VIO2 = '#C4B5FD'; VIO7 = '#6D28D9'
PINK = '#F472B6'; PINK1 = '#FCE7F3'
MINT = '#34D399'; MINT1 = '#D1FAE5'; MINT7 = '#047857'
YEL = '#FBBF24'; YEL1 = '#FEF3C7'
RED = '#EF4444'; RED1 = '#FEE2E2'; RED7 = '#B91C1C'
SKIN = '#FDE2CF'; MUTED = '#64748B'; LINE = '#CBD5E1'; FLOOR = '#E2E8F0'
UIBAR = '#2B2F36'; UIPANEL = '#3A3F47'; UITEXT = '#E5E7EB'; UIBLUE = '#2563EB'; UIDIM = '#9CA3AF'
FONT = 'system-ui,-apple-system,&quot;PingFang SC&quot;,&quot;Microsoft YaHei&quot;,&quot;Noto Sans CJK SC&quot;,sans-serif'


def svg(w, h, body, title, bg=CREAM):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{title}" font-family="{FONT}"><title>{title}</title>'
            f'<defs><marker id="arw" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{INK}"/></marker>'
            f'<marker id="arwr" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{RED}"/></marker>'
            f'<marker id="arwv" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0 0 L10 5 L0 10 z" fill="{VIO7}"/></marker></defs>'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>{body}</svg>')


def text(x, y, s, size=16, weight=400, fill=INK, anchor='start', extra=''):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" {extra}>{s}</text>'


def label(x, y, s, fill=YEL1, size=15, anchor='start', stroke=INK):
    """贴纸标签：圆角底 + 文字。x,y 为文字基线起点。"""
    w = sum(1.0 if ord(c) > 255 else 0.58 for c in s) * size + 18
    x0 = x - (w / 2 if anchor == 'middle' else (w if anchor == 'end' else 0))
    return (f'<rect x="{x0:.1f}" y="{y - size - 5:.1f}" width="{w:.1f}" height="{size + 13}" rx="{(size + 13) / 2:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>' + text(x0 + 9, y + 1, s, size, 700))


def badge(x, y, n, fill=YEL):
    return (f'<circle cx="{x}" cy="{y}" r="13" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'
            + text(x, y + 5.5, str(n), 15, 900, INK, 'middle'))


def ring(x, y, r=20):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{YEL}" stroke-width="4.5"/>'


def ringrect(x, y, w, h, r=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{YEL}" stroke-width="4"/>'


def arrow(x1, y1, x2, y2, color=INK, w=3, dash=None, marker='arw'):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{marker})"/>'


# ---------------- 人物 ----------------
def figure(cx, top, h, hip_y, feet_y, sw=3, head_h=None, head_top=None, shoes=True, ankle_y=None,
           hunch=0.0, wig_scale=1.0, hand_scale=1.0, hand_side=1, weapon=False, arm_raise=False):
    """简化人物。h：躯干基准头长；hunch：含胸驼背程度 0~1；wig_scale：假发蓬松度；hand_scale：一只手放大倍数。"""
    hh = head_h or h
    ht = head_top if head_top is not None else top
    hx = cx + hunch * h * 0.55          # 驼背时头往前伸
    ht = ht + hunch * h * 0.32
    s = []
    # 后发
    ws = wig_scale
    s.append(f'<path d="M{hx - hh * 0.62 * ws:.1f} {ht + hh * 0.45:.1f} Q{hx - hh * 0.78 * ws:.1f} {ht + hh * 1.6:.1f} {hx - hh * 0.5:.1f} {ht + hh * 1.95:.1f} '
             f'L{hx + hh * 0.5:.1f} {ht + hh * 1.95:.1f} Q{hx + hh * 0.78 * ws:.1f} {ht + hh * 1.6:.1f} {hx + hh * 0.62 * ws:.1f} {ht + hh * 0.45:.1f} Z" '
             f'fill="{PINK}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    chin = ht + hh
    sh_y = top + h * 1.35 + hunch * h * 0.22
    waist_y = top + h * 2.9
    s.append(f'<rect x="{hx - h * 0.13:.1f}" y="{chin - 4:.1f}" width="{h * 0.26:.1f}" height="{sh_y - chin + 8:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>')
    leg_w = h * 0.3
    ankle = ankle_y if ankle_y is not None else feet_y - h * 0.18
    knee_bend = hunch * h * 0.12
    for dx in (-h * 0.28, h * 0.02):
        if knee_bend:
            ky = hip_y + (ankle - hip_y) * 0.5
            s.append(f'<path d="M{cx + dx + leg_w / 2:.1f} {hip_y:.1f} L{cx + dx + leg_w / 2 + knee_bend:.1f} {ky:.1f} L{cx + dx + leg_w / 2:.1f} {ankle:.1f}" '
                     f'fill="none" stroke="{INK}" stroke-width="{leg_w:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
            s.append(f'<path d="M{cx + dx + leg_w / 2:.1f} {hip_y:.1f} L{cx + dx + leg_w / 2 + knee_bend:.1f} {ky:.1f} L{cx + dx + leg_w / 2:.1f} {ankle:.1f}" '
                     f'fill="none" stroke="{SKIN}" stroke-width="{leg_w - 2 * sw:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
        else:
            s.append(f'<rect x="{cx + dx:.1f}" y="{hip_y - 6:.1f}" width="{leg_w:.1f}" height="{ankle - hip_y + 6:.1f}" rx="{leg_w * 0.4:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>')
            ky = hip_y + (ankle - hip_y) * 0.5
            s.append(f'<path d="M{cx + dx + leg_w * 0.25:.1f} {ky:.1f} q{leg_w * 0.25:.1f} 5 {leg_w * 0.5:.1f} 0" fill="none" stroke="{INK}" stroke-width="{sw * 0.7:.1f}" stroke-linecap="round"/>')
    if shoes:
        for dx in (-h * 0.13, h * 0.17):
            s.append(f'<ellipse cx="{cx + dx:.1f}" cy="{feet_y - h * 0.09:.1f}" rx="{h * 0.24:.1f}" ry="{h * 0.11:.1f}" fill="{INK}"/>')
    # 躯干（驼背时肩线前倾、胸口塌）
    sh_l = cx - h * 0.8 + hunch * h * 0.25
    sh_r = cx + h * 0.8 + hunch * h * 0.25
    s.append(f'<path d="M{sh_l:.1f} {sh_y:.1f} Q{cx + hunch * h * 0.3:.1f} {sh_y - 6 + hunch * h * 0.25:.1f} {sh_r:.1f} {sh_y:.1f} '
             f'L{cx + h * 0.5:.1f} {waist_y:.1f} L{cx - h * 0.5:.1f} {waist_y:.1f} Z" fill="{VIO2}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    # 手臂
    for sgn in (-1, 1):
        sx = (sh_l if sgn < 0 else sh_r) + (-sgn) * h * 0.02
        if arm_raise and sgn == hand_side:
            path = f'M{sx:.1f} {sh_y + 4:.1f} Q{sx + sgn * h * 0.7:.1f} {sh_y - h * 0.1:.1f} {sx + sgn * h * 1.1:.1f} {sh_y - h * 0.7:.1f}'
            hand_xy = (sx + sgn * h * 1.1, sh_y - h * 0.7)
        else:
            path = f'M{sx:.1f} {sh_y + 4:.1f} Q{cx + sgn * h * 1.0:.1f} {waist_y - h * 0.4:.1f} {cx + sgn * h * 0.92:.1f} {hip_y - h * 0.15:.1f}'
            hand_xy = (cx + sgn * h * 0.92, hip_y - h * 0.15)
        s.append(f'<path d="{path}" fill="none" stroke="{INK}" stroke-width="{h * 0.24:.1f}" stroke-linecap="round"/>')
        s.append(f'<path d="{path}" fill="none" stroke="{SKIN}" stroke-width="{h * 0.24 - 2 * sw:.1f}" stroke-linecap="round"/>')
        if sgn == hand_side and (hand_scale != 1.0 or weapon):
            r = h * 0.17 * hand_scale
            if weapon:
                L = h * 2.6 * hand_scale
                s.append(f'<line x1="{hand_xy[0]:.1f}" y1="{hand_xy[1] + r:.1f}" x2="{hand_xy[0] + sgn * L * 0.25:.1f}" y2="{hand_xy[1] - L:.1f}" stroke="{INK}" stroke-width="{h * 0.16 * hand_scale + 2 * sw:.1f}" stroke-linecap="round"/>')
                s.append(f'<line x1="{hand_xy[0]:.1f}" y1="{hand_xy[1] + r:.1f}" x2="{hand_xy[0] + sgn * L * 0.25:.1f}" y2="{hand_xy[1] - L:.1f}" stroke="#E2E8F0" stroke-width="{h * 0.16 * hand_scale:.1f}" stroke-linecap="round"/>')
            s.append(f'<circle cx="{hand_xy[0]:.1f}" cy="{hand_xy[1]:.1f}" r="{r:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>')
    # 裙
    s.append(f'<path d="M{cx - h * 0.5:.1f} {waist_y:.1f} L{cx + h * 0.5:.1f} {waist_y:.1f} L{cx + h * 0.9:.1f} {hip_y + h * 0.1:.1f} L{cx - h * 0.9:.1f} {hip_y + h * 0.1:.1f} Z" fill="{VIO}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    s.append(f'<line x1="{cx - h * 0.5:.1f}" y1="{waist_y:.1f}" x2="{cx + h * 0.5:.1f}" y2="{waist_y:.1f}" stroke="{INK}" stroke-width="{sw * 2}"/>')
    # 头
    s.append(f'<ellipse cx="{hx:.1f}" cy="{ht + hh * 0.55:.1f}" rx="{hh * 0.4:.1f}" ry="{hh * 0.47:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>')
    s.append(f'<path d="M{hx - hh * 0.55 * ws:.1f} {ht + hh * 0.55:.1f} Q{hx - hh * 0.5 * ws:.1f} {ht - hh * 0.08 * ws:.1f} {hx:.1f} {ht - hh * 0.02 * ws:.1f} '
             f'Q{hx + hh * 0.5 * ws:.1f} {ht - hh * 0.08 * ws:.1f} {hx + hh * 0.55 * ws:.1f} {ht + hh * 0.55:.1f} Q{hx + hh * 0.2:.1f} {ht + hh * 0.2:.1f} {hx - hh * 0.1:.1f} {ht + hh * 0.32:.1f} '
             f'Q{hx - hh * 0.3:.1f} {ht + hh * 0.25:.1f} {hx - hh * 0.55 * ws:.1f} {ht + hh * 0.55:.1f} Z" fill="{PINK}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    for dx in (-hh * 0.16, hh * 0.16):
        s.append(f'<circle cx="{hx + dx:.1f}" cy="{ht + hh * 0.62:.1f}" r="{hh * 0.05:.1f}" fill="{INK}"/>')
    return ''.join(s)


def ruler(x, top, unit, total, w=22, sw=2.5, numbers=True, size=18):
    s = []
    n = int(total + 1e-6)
    for i in range(n):
        y = top + i * unit
        s.append(f'<rect x="{x}" y="{y:.1f}" width="{w}" height="{unit:.1f}" fill="{MINT if i % 2 == 0 else WHITE}" stroke="{INK}" stroke-width="{sw}"/>')
        if numbers:
            s.append(text(x + w + 10, y + unit / 2 + 6, str(i + 1), size, 800))
    rem = total - n
    if rem > 0.02:
        y = top + n * unit
        s.append(f'<rect x="{x}" y="{y:.1f}" width="{w}" height="{rem * unit:.1f}" fill="{MINT if n % 2 == 0 else WHITE}" stroke="{INK}" stroke-width="{sw}" stroke-dasharray="5 4"/>')
    return ''.join(s)


def door(x, y, w, bottom):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{bottom - y:.1f}" fill="{YEL1}" stroke="{INK}" stroke-width="3"/>'
            f'<rect x="{x + w * 0.12:.1f}" y="{y + w * 0.12:.1f}" width="{w * 0.76:.1f}" height="{bottom - y - w * 0.12:.1f}" fill="none" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="{x + w * 0.78:.1f}" cy="{(y + bottom) / 2 + 20:.1f}" r="5" fill="{INK}"/>')


# ---------------- Procreate 界面示意 ----------------
W, H = 800, 560
SX, SY, SW, SH = 14, 14, 772, 532


def device(inner):
    return (f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/>'
            f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>' + inner)


ICONS_L = [('gallery', 40), ('actions', 96), ('adjust', 136), ('select', 176), ('transform', 216)]
ICONS_R = [('brush', 596), ('smudge', 636), ('erase', 676), ('layers', 716), ('color', 756)]
TOP_Y = 34


def icon(kind, x, y, active=False):
    c = UIBLUE if active else UITEXT
    if kind == 'gallery':
        return text(x - 6, y + 6, '图库', 15, 700, c)
    if kind == 'actions':   # 扳手：手柄 + 开口的扳手头
        return (f'<g transform="translate({x},{y}) rotate(45)"><rect x="-2.5" y="-1" width="5" height="13" rx="2" fill="{c}"/>'
                f'<path d="M-7 -4 A7 7 0 1 0 7 -4 L3 -4 L3 -10 L-3 -10 L-3 -4 Z" fill="{c}" transform="translate(0,-2)"/></g>')
    if kind == 'adjust':    # 魔棒
        return (f'<line x1="{x - 8}" y1="{y + 8}" x2="{x + 4}" y2="{y - 4}" stroke="{c}" stroke-width="3" stroke-linecap="round"/>'
                f'<path d="M{x + 6} {y - 10} l2 4 4 2 -4 2 -2 4 -2 -4 -4 -2 4 -2z" fill="{c}"/>')
    if kind == 'select':    # S 缎带
        return text(x, y + 7, 'S', 21, 900, c, 'middle', 'font-style="italic"')
    if kind == 'transform':  # 箭头
        return f'<path d="M{x - 6} {y - 9} L{x + 8} {y + 1} L{x + 1} {y + 2} L{x + 4} {y + 9} L{x + 1} {y + 10} L{x - 2} {y + 4} L{x - 6} {y + 8} Z" fill="{c}"/>'
    if kind == 'brush':
        return (f'<line x1="{x - 7}" y1="{y + 9}" x2="{x + 7}" y2="{y - 9}" stroke="{c}" stroke-width="3" stroke-linecap="round"/>'
                f'<circle cx="{x - 7}" cy="{y + 9}" r="3" fill="{c}"/>')
    if kind == 'smudge':
        return f'<path d="M{x - 3} {y + 10} L{x - 3} {y - 6} Q{x} {y - 11} {x + 3} {y - 6} L{x + 3} {y + 10}" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round"/>'
    if kind == 'erase':
        return f'<g transform="translate({x},{y}) rotate(-35)"><rect x="-5" y="-10" width="10" height="20" rx="2" fill="none" stroke="{c}" stroke-width="2.5"/><line x1="-5" y1="3" x2="5" y2="3" stroke="{c}" stroke-width="2.5"/></g>'
    if kind == 'layers':
        return (f'<rect x="{x - 9}" y="{y - 5}" width="12" height="12" rx="2" fill="none" stroke="{c}" stroke-width="2.5"/>'
                f'<rect x="{x - 3}" y="{y - 10}" width="12" height="12" rx="2" fill="{UIBAR}" stroke="{c}" stroke-width="2.5"/>')
    if kind == 'color':
        return f'<circle cx="{x}" cy="{y}" r="10" fill="{PINK}" stroke="{UITEXT}" stroke-width="2.5"/>'
    return ''


def topbar(active=None):
    s = [f'<rect x="{SX}" y="{SY}" width="{SW}" height="42" rx="16" fill="{UIBAR}"/><rect x="{SX}" y="{SY + 26}" width="{SW}" height="16" fill="{UIBAR}"/>']
    for k, x in ICONS_L + ICONS_R:
        s.append(icon(k, x, TOP_Y, active == k))
    return ''.join(s)


def icon_pos(kind):
    for k, x in ICONS_L + ICONS_R:
        if k == kind:
            return x, TOP_Y
    raise KeyError(kind)


def sidebar():
    x = 24
    return (f'<rect x="{x}" y="150" width="30" height="250" rx="15" fill="{UIBAR}"/>'
            f'<rect x="{x + 11}" y="166" width="8" height="90" rx="4" fill="{UIPANEL}"/><rect x="{x + 6}" y="200" width="18" height="10" rx="4" fill="{UITEXT}"/>'
            f'<rect x="{x + 6}" y="268" width="18" height="18" rx="4" fill="none" stroke="{UITEXT}" stroke-width="2"/>'
            f'<rect x="{x + 11}" y="298" width="8" height="90" rx="4" fill="{UIPANEL}"/><rect x="{x + 6}" y="300" width="18" height="10" rx="4" fill="{UITEXT}"/>'
            f'<path d="M{x + 8} 425 q7 -10 14 0" fill="none" stroke="{INK}" stroke-width="2.5" marker-end="url(#arw)"/>'
            f'<path d="M{x + 22} 452 q-7 10 -14 0" fill="none" stroke="{INK}" stroke-width="2.5" marker-end="url(#arw)"/>')


CAN = (250, 70, 300, 410)   # 画布区域 x, y, w, h（竖幅照片）


def canvas(content='', x=None, y=None, w=None, h=None, bg=WHITE):
    cx, cy, cw, ch = CAN
    x = cx if x is None else x; y = cy if y is None else y; w = cw if w is None else w; h = ch if h is None else h
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}" stroke="#94A3B8" stroke-width="1"/>' + content


def scene(x, y, w, h, feet_frac=0.88, door_x=0.08, top_frac=0.06, head=None, heads=6.4, **fig):
    """画布里的一张"照片"：门框、地面、人物。返回 (svg, 几何信息)"""
    feet = y + h * feet_frac
    top = y + h * top_frac
    hh = head or (feet - top) / heads
    hip = top + hh * 3.6
    cx = x + w * 0.58
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFF7E6"/>']
    s.append(door(x + w * door_x, y + h * 0.16, w * 0.24, feet))
    s.append(f'<rect x="{x}" y="{feet:.1f}" width="{w}" height="{y + h - feet:.1f}" fill="{FLOOR}"/>')
    s.append(f'<line x1="{x}" y1="{feet:.1f}" x2="{x + w}" y2="{feet:.1f}" stroke="{INK}" stroke-width="2"/>')
    s.append(figure(cx, top, hh, hip, feet, sw=2, **fig))
    return ''.join(s), dict(top=top, feet=feet, hh=hh, hip=hip, cx=cx, waist=top + hh * 2.9)


def panel(x, y, w, h, title=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{UIPANEL}" stroke="#111827" stroke-width="1.5"/>'
    if title:
        s += text(x + 16, y + 28, title, 17, 800, UITEXT)
    return s


def menu_rows(x, y, w, rows, hl=None, row_h=34, toggles=()):
    s = []
    for i, r in enumerate(rows):
        yy = y + i * row_h
        if i:
            s.append(f'<line x1="{x + 12}" y1="{yy:.1f}" x2="{x + w - 12}" y2="{yy:.1f}" stroke="#4B5563" stroke-width="1"/>')
        s.append(text(x + 16, yy + 22, r, 15, 600, UITEXT))
        if r in toggles:
            on = toggles[r] if isinstance(toggles, dict) else False
            s.append(f'<rect x="{x + w - 58}" y="{yy + 8}" width="40" height="20" rx="10" fill="{UIBLUE if on else "#6B7280"}"/>'
                     f'<circle cx="{x + w - (28 if on else 48)}" cy="{yy + 18}" r="8" fill="{WHITE}"/>')
        if hl == r:
            s.append(ringrect(x + 6, yy + 3, w - 12, row_h - 6))
    return ''.join(s)


def actions_menu(tab='画布', rows=None, hl=None, x=70, y=62, w=310, toggles=None):
    tabs = ['添加', '画布', '分享', '视频', '偏好设置', '帮助']
    rows = rows or ['裁剪并调整大小', '动画协助', '页面辅助', '绘图指引', '编辑绘图指引', '参考', '水平翻转画布', '垂直翻转画布', '画布信息']
    toggles = toggles if toggles is not None else {'动画协助': False, '页面辅助': False, '绘图指引': False, '参考': False}
    h = 60 + len(rows) * 34 + 10
    s = [panel(x, y, w, h)]
    tx = x + 10
    for t in tabs:
        tw = len(t) * 13 + 12
        s.append(f'<rect x="{tx}" y="{y + 12}" width="{tw}" height="26" rx="8" fill="{UIBLUE if t == tab else UIBAR}"/>')
        s.append(text(tx + tw / 2, y + 30, t, 13, 700, UITEXT, 'middle'))
        tx += tw + 4
    s.append(menu_rows(x, y + 50, w, rows, hl, toggles=toggles))
    return ''.join(s)


def layers_panel(layers, x=470, y=62, w=300, hl=None, swiped=None, swipe_hl=None):
    """layers: [(名称, 缩略图类型, 混合模式字母, 选中?)]，从上到下"""
    row_h = 52
    h = 50 + len(layers) * row_h + 8
    s = [panel(x, y, w, h, '图层'), text(x + w - 26, y + 30, '+', 24, 700, UITEXT, 'middle')]
    for i, (name, thumb, mode, sel) in enumerate(layers):
        yy = y + 44 + i * row_h
        fill = UIBLUE if sel else UIBAR
        s.append(f'<rect x="{x + 8}" y="{yy}" width="{w - 16}" height="{row_h - 6}" rx="8" fill="{fill}"/>')
        s.append(f'<rect x="{x + 16}" y="{yy + 6}" width="44" height="34" rx="4" fill="{WHITE}"/>')
        if thumb == 'figure':
            s.append(f'<path d="M{x + 38} {yy + 36} q-5 -14 0 -24 q5 10 0 24" fill="{PINK}" stroke="{INK}" stroke-width="1"/>')
        elif thumb == 'scene':
            s.append(f'<rect x="{x + 18}" y="{yy + 29}" width="40" height="9" fill="{FLOOR}"/><path d="M{x + 40} {yy + 36} q-5 -14 0 -24 q5 10 0 24" fill="{VIO2}" stroke="{INK}" stroke-width="1"/>'
                     f'<rect x="{x + 21}" y="{yy + 12}" width="8" height="18" fill="{YEL1}" stroke="{INK}" stroke-width="1"/>')
        elif thumb == 'ruler':
            s.append(f'<line x1="{x + 50}" y1="{yy + 9}" x2="{x + 50}" y2="{yy + 37}" stroke="{MINT}" stroke-width="3"/>')
        elif thumb == 'bg':
            s.append(f'<rect x="{x + 18}" y="{yy + 29}" width="40" height="9" fill="{FLOOR}"/><rect x="{x + 21}" y="{yy + 12}" width="8" height="18" fill="{YEL1}" stroke="{INK}" stroke-width="1"/>')
        s.append(text(x + 70, yy + 29, name, 15, 700, UITEXT))
        if swiped == i:
            bx = x + w - 8 - 180
            for j, (b, col) in enumerate([('锁定', '#4B5563'), ('复制', '#2563EB'), ('删除', '#DC2626')]):
                s.append(f'<rect x="{bx + j * 60}" y="{yy}" width="60" height="{row_h - 6}" fill="{col}"/>')
                s.append(text(bx + j * 60 + 30, yy + 29, b, 14, 700, WHITE, 'middle'))
                if swipe_hl == b:
                    s.append(ringrect(bx + j * 60 + 2, yy + 2, 56, row_h - 10, 6))
        else:
            s.append(text(x + w - 44, yy + 29, mode, 14, 800, UITEXT, 'middle'))
            s.append(f'<rect x="{x + w - 30}" y="{yy + 15}" width="16" height="16" rx="3" fill="{UIBLUE if True else "none"}" stroke="{UITEXT}" stroke-width="1.5"/>')
    return ''.join(s)


POS = {}


def bottom_bar(rows, active=(), hl=None, y=None):
    """rows: [[按钮...], [按钮...]]，从上到下。active：高亮成蓝色的按钮；hl：黄圈的按钮"""
    n = len(rows)
    bh = 40
    y = y if y is not None else SY + SH - 12 - n * (bh + 6)
    s = []
    for r, btns in enumerate(rows):
        widths = [len(b) * 15 + 26 for b in btns]
        total = sum(widths) + 6 * (len(btns) - 1) + 16
        x = SX + SW / 2 - total / 2
        yy = y + r * (bh + 6)
        s.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{total:.1f}" height="{bh}" rx="12" fill="{UIBAR}"/>')
        bx = x + 8
        for b, bw in zip(btns, widths):
            on = b in active
            s.append(f'<rect x="{bx:.1f}" y="{yy + 5:.1f}" width="{bw}" height="{bh - 10}" rx="8" fill="{UIBLUE if on else UIPANEL}"/>')
            s.append(text(bx + bw / 2, yy + 26, b, 14, 700, UITEXT, 'middle'))
            POS[b] = (bx, yy, bw, bh)
            if hl == b:
                s.append(ringrect(bx - 3, yy + 2, bw + 6, bh - 4))
            bx += bw + 6
    return ''.join(s)


SEL_ROWS = [['自动', '手绘', '矩形', '椭圆'], ['添加', '移除', '反转', '拷贝并粘贴', '羽化', '存储并加载', '颜色填充', '清除']]
TF_ROWS = [['自由变换', '等比', '扭曲', '弯曲'], ['对齐', '水平翻转', '垂直翻转', '旋转45°', '符合画布', '插值', '重置']]


def slider(x, y, w, name, frac, hl=False):
    s = (text(x, y - 8, name, 13, 700, UITEXT) + f'<rect x="{x}" y="{y}" width="{w}" height="8" rx="4" fill="#6B7280"/>'
         f'<rect x="{x}" y="{y}" width="{w * frac:.1f}" height="8" rx="4" fill="{UIBLUE}"/>'
         f'<circle cx="{x + w * frac:.1f}" cy="{y + 4}" r="9" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
         + text(x + w, y - 8, f'{int(frac * 100)}%', 13, 700, UITEXT, 'end'))
    if hl:
        s += ringrect(x - 8, y - 26, w + 16, 44)
    return s


def tool_sliders(names_vals, mode=None, buttons=(), hl=None, y=None):
    n = len(names_vals)
    y = y if y is not None else SY + SH - 74
    w_each = 92
    total = (90 if mode else 0) + len(buttons) * 70 + n * (w_each + 24) + 24
    x = SX + SW / 2 - total / 2
    s = [f'<rect x="{x:.1f}" y="{y}" width="{total:.1f}" height="62" rx="14" fill="{UIBAR}"/>']
    bx = x + 12
    if mode:
        s.append(f'<rect x="{bx:.1f}" y="{y + 12}" width="80" height="38" rx="10" fill="{UIBLUE}"/>' + text(bx + 40, y + 37, mode + ' ▾', 15, 800, WHITE, 'middle'))
        if hl == 'mode':
            s.append(ringrect(bx - 3, y + 9, 86, 44))
        bx += 90
    for b in buttons:
        s.append(f'<rect x="{bx:.1f}" y="{y + 12}" width="62" height="38" rx="10" fill="{UIPANEL}"/>' + text(bx + 31, y + 37, b, 14, 700, UITEXT, 'middle'))
        POS[b] = (bx, y + 12, 62, 38)
        if hl == b:
            s.append(ringrect(bx - 3, y + 9, 68, 44))
        bx += 70
    for name, val in names_vals:
        s.append(slider(bx + 12, y + 38, w_each, name, val, hl == name))
        bx += w_each + 24
    return ''.join(s)


def finger(x, y, n=3, dy=40):
    """多指下滑手势示意"""
    s = []
    for i in range(n):
        fx = x + (i - (n - 1) / 2) * 22
        s.append(f'<ellipse cx="{fx:.1f}" cy="{y}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
        s.append(arrow(fx, y + 16, fx, y + 16 + dy, INK, 2.5))
    return ''.join(s)


def ui(inner, active=None, side=True, title='Procreate 界面示意'):
    body = device(canvas() if inner is None else inner)
    return body


def screen(content, active=None, side=True):
    """完整屏幕：底色 + 画布内容 + 顶栏 + 侧栏。content 画在画布区。"""
    s = [f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#D7DBE0"/>', content, topbar(active)]
    if side:
        s.append(sidebar())
    return f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/>' + ''.join(s)


def note(s):
    """右下角"示意图"说明"""
    return text(SX + SW - 12, SY + SH - 10, s, 12, 600, MUTED, 'end')
