"""M2 Procreate 修图工具 的示意图。运行：python tools/diagrams/m2.py"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'diagrams', 'm2')
os.makedirs(OUT, exist_ok=True)
DONE = []


def save(name, s):
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)
    DONE.append(name)


_uid = [0]


def uid(p='u'):
    _uid[0] += 1
    return f'{p}{_uid[0]}'


CX, CY, CW, CH = 262, 66, 276, 340      # 默认画布位置（界面中间）
LX = 70                                   # 画布靠左时的 x


def tw(s, size):
    return sum(1.0 if ord(c) > 255 else 0.58 for c in s) * size


# ---------------- 滤镜：模拟偏色、偏暗、模糊 ----------------
def f_matrix(fid, vals):
    return f'<filter id="{fid}" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="{vals}"/></filter>'


TINT = {
    'warm': '1.02 0 0 0 0.05  0 0.97 0 0 0.03  0 0 0.70 0 0  0 0 0 1 0',
    'green': '0.86 0 0 0 0  0 1.0 0 0 0.05  0 0 0.90 0 0.02  0 0 0 1 0',
    'dark': '0.55 0 0 0 0  0 0.55 0 0 0  0 0 0.58 0 0  0 0 0 1 0',
    'gray': '0.3 0.59 0.11 0 0  0.3 0.59 0.11 0 0  0.3 0.59 0.11 0 0  0 0 0 1 0',
}


def tinted(content, kind):
    fid = uid('t')
    return f'<defs>{f_matrix(fid, TINT[kind])}</defs><g filter="url(#{fid})">{content}</g>'


def blurred(content, sd):
    fid = uid('b')
    return (f'<defs><filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="{sd}"/></filter></defs>'
            f'<g filter="url(#{fid})">{content}</g>')


def mblur(content, sd):
    fid = uid('m')
    return (f'<defs><filter id="{fid}" x="-30%" y="-10%" width="160%" height="120%"><feGaussianBlur stdDeviation="{sd} 0"/></filter></defs>'
            f'<g filter="url(#{fid})">{content}</g>')


def clip(content, x, y, w, h, rx=0):
    cid = uid('c')
    return (f'<defs><clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath></defs>'
            f'<g clip-path="url(#{cid})">{content}</g>')


def checker(x, y, w, h, n=8):
    pid = uid('k')
    return (f'<defs><pattern id="{pid}" width="{n * 2}" height="{n * 2}" patternUnits="userSpaceOnUse" x="{x}" y="{y}">'
            f'<rect width="{n * 2}" height="{n * 2}" fill="#FFFFFF"/><rect width="{n}" height="{n}" fill="#D1D5DB"/><rect x="{n}" y="{n}" width="{n}" height="{n}" fill="#D1D5DB"/></pattern></defs>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pid})"/>')


def noise_dots(x, y, w, h, n=400, seed=1, op=.35, r=0.9):
    rnd = random.Random(seed)
    s = []
    for _ in range(n):
        c = rnd.choice(['#000', '#fff'])
        s.append(f'<circle cx="{x + rnd.random() * w:.1f}" cy="{y + rnd.random() * h:.1f}" r="{r}" fill="{c}" fill-opacity="{op}"/>')
    return ''.join(s)


# ---------------- 照片内容 ----------------
def room(x, y, w, h, **fig):
    sc, g = scene(x, y, w, h, **fig)
    return clip(sc, x, y, w, h), g


def face_photo(x, y, w, h, spots=(), wig=PINK, bg='#EDE7F6', marks=False, stain_free=False):
    """近景大头：脸、假发、眼睛，spots=[(dx,dy,r)] 相对脸中心的痘痘位置（单位：脸宽比例）"""
    cx, cy = x + w * 0.5, y + h * 0.52
    fw = w * 0.30
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>']
    # 后发
    s.append(f'<path d="M{cx - fw * 1.55:.1f} {cy - fw * 0.6:.1f} Q{cx - fw * 1.9:.1f} {cy + fw * 1.6:.1f} {cx - fw * 1.3:.1f} {y + h:.1f} L{cx + fw * 1.3:.1f} {y + h:.1f} '
             f'Q{cx + fw * 1.9:.1f} {cy + fw * 1.6:.1f} {cx + fw * 1.55:.1f} {cy - fw * 0.6:.1f} Z" fill="{wig}" stroke="{INK}" stroke-width="3"/>')
    # 脖子和肩
    s.append(f'<rect x="{cx - fw * 0.35:.1f}" y="{cy + fw * 1.0:.1f}" width="{fw * 0.7:.1f}" height="{fw * 0.8:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M{x - 10} {y + h + 5} Q{cx - fw * 1.5:.1f} {cy + fw * 1.55:.1f} {cx:.1f} {cy + fw * 1.62:.1f} Q{cx + fw * 1.5:.1f} {cy + fw * 1.55:.1f} {x + w + 10} {y + h + 5} Z" fill="{VIO2}" stroke="{INK}" stroke-width="3"/>')
    # 脸
    s.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{fw:.1f}" ry="{fw * 1.22:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="3"/>')
    # 刘海
    s.append(f'<path d="M{cx - fw * 1.25:.1f} {cy - fw * 0.1:.1f} Q{cx - fw * 1.3:.1f} {cy - fw * 1.75:.1f} {cx:.1f} {cy - fw * 1.6:.1f} Q{cx + fw * 1.3:.1f} {cy - fw * 1.75:.1f} {cx + fw * 1.25:.1f} {cy - fw * 0.1:.1f} '
             f'Q{cx + fw * 0.7:.1f} {cy - fw * 0.95:.1f} {cx + fw * 0.15:.1f} {cy - fw * 0.55:.1f} Q{cx - fw * 0.3:.1f} {cy - fw * 0.95:.1f} {cx - fw * 1.25:.1f} {cy - fw * 0.1:.1f} Z" fill="{wig}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
    # 眼、嘴
    for dx in (-0.42, 0.42):
        s.append(f'<ellipse cx="{cx + dx * fw:.1f}" cy="{cy + fw * 0.05:.1f}" rx="{fw * 0.16:.1f}" ry="{fw * 0.2:.1f}" fill="{INK}"/>'
                 f'<circle cx="{cx + dx * fw + fw * 0.05:.1f}" cy="{cy - fw * 0.03:.1f}" r="{fw * 0.05:.1f}" fill="{WHITE}"/>')
    s.append(f'<path d="M{cx - fw * 0.18:.1f} {cy + fw * 0.68:.1f} q{fw * 0.18:.1f} {fw * 0.12:.1f} {fw * 0.36:.1f} 0" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    s.append(f'<ellipse cx="{cx - fw * 0.55:.1f}" cy="{cy + fw * 0.42:.1f}" rx="{fw * 0.17:.1f}" ry="{fw * 0.08:.1f}" fill="{PINK}" fill-opacity=".35"/>'
             f'<ellipse cx="{cx + fw * 0.55:.1f}" cy="{cy + fw * 0.42:.1f}" rx="{fw * 0.17:.1f}" ry="{fw * 0.08:.1f}" fill="{PINK}" fill-opacity=".35"/>')
    for (dx, dy, r) in spots:
        s.append(f'<circle cx="{cx + dx * fw:.1f}" cy="{cy + dy * fw:.1f}" r="{r * fw:.1f}" fill="#C2410C" fill-opacity=".75"/>'
                 f'<circle cx="{cx + dx * fw:.1f}" cy="{cy + dy * fw:.1f}" r="{r * fw * 1.9:.1f}" fill="#F87171" fill-opacity=".25"/>')
    return clip(''.join(s), x, y, w, h), dict(cx=cx, cy=cy, fw=fw)


def spot_pos(g, dx, dy):
    return g['cx'] + dx * g['fw'], g['cy'] + dy * g['fw']


# ---------------- 界面组件 ----------------
ADJ_TOP = ['色相、饱和度、亮度', '颜色平衡', '曲线', '渐变映射']
ADJ_BOT = ['高斯模糊', '动态模糊', '透视模糊', '杂色', '锐化', '泛光', '故障艺术', '半色调', '色像差', '液化', '克隆']


def adjust_menu(hl=None, x=72, y=60, w=230, row_h=27):
    rows = ADJ_TOP + ADJ_BOT
    h = 16 + len(rows) * row_h + 14
    s = [panel(x, y, w, h)]
    yy = y + 10
    for i, r in enumerate(rows):
        if i == len(ADJ_TOP):
            s.append(f'<line x1="{x + 10}" y1="{yy + 5}" x2="{x + w - 10}" y2="{yy + 5}" stroke="#6B7280" stroke-width="2"/>')
            yy += 10
        s.append(text(x + 16, yy + 19, r, 14, 600, UITEXT))
        if hl and r in (hl if isinstance(hl, (list, tuple)) else [hl]):
            s.append(ringrect(x + 5, yy + 1, w - 10, row_h - 2))
        yy += row_h
    return ''.join(s)


def adj_row_y(name, y=60, row_h=27):
    rows = ADJ_TOP + ADJ_BOT
    i = rows.index(name)
    return y + 10 + i * row_h + (10 if i >= len(ADJ_TOP) else 0) + row_h / 2


def info_pill(label_s, pct=None, dropdown=False, hl=None, cx=400, y=64):
    t = label_s + (f'  {pct}' if pct is not None else '') + ('  ▾' if dropdown else '')
    w = tw(t, 15) + 30
    s = [f'<rect x="{cx - w / 2:.1f}" y="{y}" width="{w:.1f}" height="30" rx="15" fill="{UIBLUE}"/>', text(cx, y + 21, t, 15, 700, WHITE, 'middle')]
    if pct is not None:
        s.append(f'<rect x="{cx - w / 2 + 10:.1f}" y="{y + 26}" width="{(w - 20) * 0.35:.1f}" height="3" rx="1.5" fill="{WHITE}" fill-opacity=".8"/>')
    if hl == 'pill':
        s.append(ringrect(cx - w / 2 - 4, y - 4, w + 8, 38, 18))
    return ''.join(s), (cx - w / 2, y, w, 30)


def mode_dropdown(cx=400, y=100, active='图层', hl=None):
    s = [f'<rect x="{cx - 80}" y="{y}" width="160" height="44" rx="12" fill="{UIBAR}"/>']
    for i, b in enumerate(['图层', 'Pencil']):
        bx = cx - 74 + i * 76
        s.append(f'<rect x="{bx}" y="{y + 6}" width="72" height="32" rx="8" fill="{UIBLUE if b == active else UIPANEL}"/>' + text(bx + 36, y + 27, b, 14, 700, UITEXT, 'middle'))
        if hl == b:
            s.append(ringrect(bx - 3, y + 3, 78, 38))
    return ''.join(s)


def L(name, thumb='scene', mode='N', sel=False, sec=False, lock=False, alpha=False, indent=0, group=False, hidden=False, hl=False, open_=True):
    return dict(name=name, thumb=thumb, mode=mode, sel=sel, sec=sec, lock=lock, alpha=alpha, indent=indent, group=group, hidden=hidden, hl=hl, open_=open_)


def thumb_img(kind, x, y, w=40, h=30, alpha=False):
    s = []
    if alpha or kind in ('figure', 'check', 'hairfig'):
        s.append(checker(x, y, w, h, 5))
    else:
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{WHITE}"/>')
    if kind == 'scene':
        s.append(f'<rect x="{x + 1}" y="{y + h - 8}" width="{w - 2}" height="7" fill="{FLOOR}"/><rect x="{x + 4}" y="{y + 6}" width="7" height="{h - 13}" fill="{YEL1}" stroke="{INK}" stroke-width="1"/>'
                 f'<path d="M{x + w * 0.6} {y + h - 3} q-5 -13 0 -23 q5 10 0 23" fill="{VIO2}" stroke="{INK}" stroke-width="1"/><circle cx="{x + w * 0.6}" cy="{y + 6}" r="3.5" fill="{PINK}" stroke="{INK}" stroke-width="1"/>')
    elif kind in ('figure', 'hairfig'):
        s.append(f'<path d="M{x + w * 0.5} {y + h - 2} q-6 -14 0 -22 q6 8 0 22" fill="{VIO2}" stroke="{INK}" stroke-width="1"/><circle cx="{x + w * 0.5}" cy="{y + 7}" r="5" fill="{PINK}" stroke="{INK}" stroke-width="1"/>')
    elif kind == 'face':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#EDE7F6"/><ellipse cx="{x + w / 2}" cy="{y + h / 2 + 2}" rx="8" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="1"/>'
                 f'<path d="M{x + w / 2 - 10} {y + h / 2} q2 -12 10 -12 q8 0 10 12" fill="{PINK}" stroke="{INK}" stroke-width="1"/>')
    elif kind == 'gray':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#808080"/>')
    elif kind == 'grain':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#808080"/>' + noise_dots(x, y, w, h, 60, 3, .6, .9))
    elif kind == 'mask':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#111"/><path d="M{x + w * 0.5} {y + h - 2} q-7 -14 0 -22 q7 8 0 22" fill="#FFF"/><circle cx="{x + w * 0.5}" cy="{y + 7}" r="5" fill="#FFF"/>')
    elif kind == 'dark':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#1E293B"/>')
    elif kind == 'blur':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#C7D2FE"/><circle cx="{x + 12}" cy="{y + 12}" r="8" fill="{MINT}" fill-opacity=".6"/><circle cx="{x + 30}" cy="{y + 16}" r="7" fill="{MINT}" fill-opacity=".5"/>')
    elif kind == 'paint':
        s.append(f'<path d="M{x + 8} {y + 20} q8 -10 14 -2 t14 -4" fill="none" stroke="{PINK}" stroke-width="3" stroke-linecap="round"/>')
    elif kind == 'merged':
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#FFF7E6"/><path d="M{x + w * 0.6} {y + h - 3} q-5 -13 0 -23 q5 10 0 23" fill="{VIO2}" stroke="{INK}" stroke-width="1"/><circle cx="{x + w * 0.6}" cy="{y + 6}" r="3.5" fill="{PINK}" stroke="{INK}" stroke-width="1"/>')
    return ''.join(s)


def lock_icon(x, y, c=UITEXT):
    return (f'<rect x="{x - 6}" y="{y - 2}" width="12" height="10" rx="2" fill="{c}"/>'
            f'<path d="M{x - 4} {y - 2} v-3 a4 4 0 0 1 8 0 v3" fill="none" stroke="{c}" stroke-width="2"/>')


def layers2(rows, x=470, y=62, w=300, row_h=44, title='图层', top_btns=None, hl_btn=None):
    h = 48 + len(rows) * row_h + 8
    s = [panel(x, y, w, h, title), text(x + w - 24, y + 30, '+', 24, 700, UITEXT, 'middle')]
    pos = {}
    if top_btns:
        bx = x + w - 52
        for b in reversed(top_btns):
            bw = tw(b, 13) + 16
            bx -= bw + 6
            s.append(f'<rect x="{bx:.1f}" y="{y + 12}" width="{bw:.1f}" height="24" rx="7" fill="{UIBLUE}"/>' + text(bx + bw / 2, y + 29, b, 13, 700, WHITE, 'middle'))
            if hl_btn == b:
                s.append(ringrect(bx - 3, y + 9, bw + 6, 30))
            pos['btn:' + b] = (bx + bw / 2, y + 24)
    for i, r in enumerate(rows):
        yy = y + 44 + i * row_h
        ind = r['indent'] * 18
        fill = UIBLUE if r['sel'] else ('#1E3A8A' if r['sec'] else UIBAR)
        s.append(f'<rect x="{x + 8 + ind}" y="{yy}" width="{w - 16 - ind}" height="{row_h - 6}" rx="8" fill="{fill}"/>')
        tx = x + 16 + ind
        if r['group']:
            s.append(text(tx + 2, yy + 25, '▾' if r['open_'] else '▸', 14, 800, UITEXT))
            s.append(f'<path d="M{tx + 18} {yy + 10} h10 l3 3 h14 v16 h-27 z" fill="none" stroke="{UITEXT}" stroke-width="2"/>')
            s.append(text(tx + 54, yy + 25, r['name'], 15, 800, UITEXT))
        else:
            s.append(thumb_img(r['thumb'], tx, yy + 4, 40, row_h - 14, r['alpha']))
            s.append(text(tx + 50, yy + 25, r['name'], 14, 700, UITEXT))
        if r['lock']:
            s.append(lock_icon(x + w - 66, yy + 18))
        s.append(text(x + w - 44, yy + 25, r['mode'], 13, 800, UITEXT, 'middle'))
        on = not r['hidden']
        s.append(f'<rect x="{x + w - 30}" y="{yy + 12}" width="15" height="15" rx="3" fill="{UIBLUE if on else "none"}" stroke="{UITEXT}" stroke-width="1.5"/>')
        if on:
            s.append(f'<path d="M{x + w - 27} {yy + 19} l3 3 l6 -6" fill="none" stroke="{WHITE}" stroke-width="2"/>')
        if r['hl']:
            s.append(ringrect(x + 5 + ind, yy - 3, w - 10 - ind, row_h))
        pos[r['name']] = (x + 8 + ind, yy, w - 16 - ind, row_h - 6)
    return ''.join(s), pos


LAYER_OPTS = ['重命名', '选择', '拷贝', '填充图层', '清除', '阿尔法锁定', '蒙版', '剪辑蒙版', '辅助绘图', '反转', '参考', '向下合并', '向下组合']


def layer_options(x, y, hl=None, w=150, row_h=27, rows=None):
    rows = rows or LAYER_OPTS
    h = len(rows) * row_h + 12
    s = [panel(x, y, w, h)]
    for i, r in enumerate(rows):
        yy = y + 6 + i * row_h
        if i:
            s.append(f'<line x1="{x + 10}" y1="{yy}" x2="{x + w - 10}" y2="{yy}" stroke="#4B5563"/>')
        s.append(text(x + 14, yy + 19, r, 14, 600, UITEXT))
        if hl == r:
            s.append(ringrect(x + 4, yy + 1, w - 8, row_h - 2))
    return ''.join(s)


def opt_y(name, y, row_h=27, rows=None):
    rows = rows or LAYER_OPTS
    return y + 6 + rows.index(name) * row_h + row_h / 2


def blend_popup(x, y, mode='正常', op=0.6, hl='op', w=250):
    s = [panel(x, y, w, 92)]
    s.append(text(x + 16, y + 28, mode, 15, 800, UITEXT) + text(x + w - 16, y + 28, '▾', 14, 800, UITEXT, 'end'))
    s.append(slider(x + 16, y + 66, w - 32, '不透明度', op, hl == 'op'))
    if hl == 'mode':
        s.append(ringrect(x + 6, y + 8, w - 12, 30))
    return ''.join(s)


def brush_icon_star(x, y):
    """Pencil 模式时画笔图标上的星标"""
    return f'<path d="M{x + 10} {y - 16} l2.5 5 5.5 .8 -4 3.9 1 5.5 -5 -2.6 -5 2.6 1 -5.5 -4 -3.9 5.5 -.8z" fill="{YEL}" stroke="{INK}" stroke-width="1"/>'


def soft_stroke(d, color=WHITE, w=26, op=.45):
    fid = uid('s')
    return (f'<defs><filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="4"/></filter></defs>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-opacity="{op}" filter="url(#{fid})"/>')


def ants_path(d):
    return (f'<path d="{d}" fill="{UIBLUE}" fill-opacity=".10" stroke="{WHITE}" stroke-width="2.5"/>'
            f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 6"/>')


def disc(x, y, r=16, locked=False):
    rr = r * (1.3 if locked else 1)
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="none" stroke="{WHITE}" stroke-width="4.5"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}" fill="none" stroke="{INK}" stroke-width="2"/>'
            f'<line x1="{x - 7:.1f}" y1="{y:.1f}" x2="{x + 7:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-width="2"/>'
            f'<line x1="{x:.1f}" y1="{y - 7:.1f}" x2="{x:.1f}" y2="{y + 7:.1f}" stroke="{INK}" stroke-width="2"/>')


def pencil(x, y, ang=-35):
    """Apple Pencil 简笔，笔尖在 (x,y)"""
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({ang})"><path d="M0 0 L8 -14 L8 -120 L-8 -120 L-8 -14 Z" fill="{WHITE}" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>'
            f'<path d="M0 0 L8 -14 L-8 -14 Z" fill="{INK}"/></g>')


def fingertip(x, y):
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="11" ry="14" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>'


def side_note(x, y, lines, fill=YEL1, size=14, gap=32, anchor='start'):
    return ''.join(label(x, y + i * gap, t, fill, size, anchor) for i, t in enumerate(lines))


def panel_box(ox, oy, w, h, title=None, fill=WHITE, tfill=YEL1):
    s = f'<rect x="{ox}" y="{oy}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'
    if title:
        s += label(ox + 14, oy + 34, title, tfill, 15)
    return s


# ======================= 2.1 调整菜单 =======================
def bottom_panel(y, w, sliders=(), buttons=(), active_btn=None, hl=None, bipolar=False):
    """自绘底部工具条：sliders=[(名称, 值0~1)]；bipolar=True 时每个滑块 sliders=[(左名, 右名, 值)]"""
    x = SX + SW / 2 - w / 2
    rows = (1 if buttons else 0) + len(sliders)
    h = 22 + rows * 44
    y = min(y, SY + SH - 22)
    y0 = y - h
    s = [f'<rect x="{x:.1f}" y="{y0:.1f}" width="{w}" height="{h}" rx="14" fill="{UIBAR}"/>']
    yy = y0 + 14
    pos = {}
    if buttons:
        bw = 92
        bx = x + w / 2 - (len(buttons) * (bw + 8) - 8) / 2
        for b in buttons:
            s.append(f'<rect x="{bx:.1f}" y="{yy}" width="{bw}" height="32" rx="8" fill="{UIBLUE if b == active_btn else UIPANEL}"/>' + text(bx + bw / 2, yy + 22, b, 14, 700, UITEXT, 'middle'))
            if hl == b:
                s.append(ringrect(bx - 3, yy - 3, bw + 6, 38))
            pos[b] = (bx + bw / 2, yy + 16)
            bx += bw + 8
        yy += 44
    for sl in sliders:
        if bipolar:
            ln, rn, v = sl
            sx0, sw_ = x + 90, w - 180
            s.append(text(x + 80, yy + 18, ln, 14, 700, UITEXT, 'end') + text(x + w - 80, yy + 18, rn, 14, 700, UITEXT))
            s.append(f'<rect x="{sx0:.1f}" y="{yy + 9}" width="{sw_:.1f}" height="8" rx="4" fill="#6B7280"/>')
            mid = sx0 + sw_ / 2
            kx = sx0 + sw_ * v
            s.append(f'<rect x="{min(mid, kx):.1f}" y="{yy + 9}" width="{abs(kx - mid):.1f}" height="8" fill="{UIBLUE}"/>')
            s.append(f'<line x1="{mid:.1f}" y1="{yy + 3}" x2="{mid:.1f}" y2="{yy + 23}" stroke="{UITEXT}" stroke-width="2"/>')
            s.append(f'<circle cx="{kx:.1f}" cy="{yy + 13}" r="10" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>')
            if hl == ln:
                s.append(ringrect(x + 8, yy - 5, w - 16, 36))
            pos[ln] = (kx, yy + 13)
        else:
            n, v = sl
            sx0, sw_ = x + 110, w - 190
            s.append(text(x + 20, yy + 18, n, 14, 700, UITEXT))
            s.append(f'<rect x="{sx0:.1f}" y="{yy + 9}" width="{sw_:.1f}" height="8" rx="4" fill="#6B7280"/><rect x="{sx0:.1f}" y="{yy + 9}" width="{sw_ * v:.1f}" height="8" rx="4" fill="{UIBLUE}"/>')
            s.append(f'<circle cx="{sx0 + sw_ * v:.1f}" cy="{yy + 13}" r="10" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>' + text(x + w - 20, yy + 18, f'{int(v * 100)}%', 14, 700, UITEXT, 'end'))
            if hl == n:
                s.append(ringrect(x + 8, yy - 5, w - 16, 36))
            pos[n] = (sx0 + sw_ * v, yy + 13)
        yy += 44
    return ''.join(s), pos, y0


def gray_board(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#9CA3AF" stroke="{INK}" stroke-width="2.5"/>'
            f'<rect x="{x + w * 0.15:.1f}" y="{y + h * 0.12:.1f}" width="{w * 0.7:.1f}" height="{h * 0.16:.1f}" fill="#D1D5DB"/>'
            f'<line x1="{x + w / 2:.1f}" y1="{y + h}" x2="{x + w / 2:.1f}" y2="{y + h + 30}" stroke="{INK}" stroke-width="4"/>')


def hall(x, y, w, h, board=True, hh=None, fig_dx=0.6):
    """漫展室内场照：墙、灰色展板、地面、人物"""
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#F5F1E8"/>']
    floor = y + h * 0.82
    for i in range(1, 4):
        s.append(f'<line x1="{x + w * i / 4:.1f}" y1="{y}" x2="{x + w * i / 4:.1f}" y2="{floor:.1f}" stroke="#E5DED0" stroke-width="3"/>')
    s.append(f'<rect x="{x}" y="{floor:.1f}" width="{w}" height="{y + h - floor:.1f}" fill="#D6D3D1"/><line x1="{x}" y1="{floor:.1f}" x2="{x + w}" y2="{floor:.1f}" stroke="{INK}" stroke-width="2.5"/>')
    if board:
        s.append(gray_board(x + w * 0.07, y + h * 0.36, w * 0.24, h * 0.3))
    hh = hh or h * 0.115
    top = y + h * 0.1
    s.append(figure(x + w * fig_dx, top, hh, top + hh * 3.6, floor + hh * 0.35, sw=max(2, hh / 22)))
    return clip(''.join(s), x, y, w, h), dict(board=(x + w * 0.19, y + h * 0.5), floor=floor, top=top, hh=hh)


def u_adj_menu():
    ph, g = hall(510, 66, 250, 340)
    s = screen(ph + adjust_menu(), active='adjust')
    s += ring(*icon_pos('adjust'), 18) + badge(icon_pos('adjust')[0] + 26, 62, 1)
    y1, y2 = adj_row_y('色相、饱和度、亮度') - 13, adj_row_y('渐变映射') + 13
    s += ringrect(76, y1 - 2, 222, y2 - y1 + 4)
    s += badge(316, (y1 + y2) / 2, 2)
    s += f'<line x1="304" y1="{adj_row_y("高斯模糊") - 13:.1f}" x2="304" y2="{adj_row_y("克隆") + 13:.1f}" stroke="{YEL}" stroke-width="4"/>' + badge(316, adj_row_y('杂色'), 3)
    s += label(334, (y1 + y2) / 2 + 6, '调整：改颜色', YEL1, 14)
    s += label(334, adj_row_y('杂色') + 6, '滤镜：模糊、锐化、', YEL1, 14) + label(334, adj_row_y('杂色') + 38, '液化、克隆等', YEL1, 14)
    s += note('示意图，菜单顺序和文字以实际界面为准')
    save('u-adj-menu', svg(W, H, s, '调整菜单：上半部分是 4 个色彩调整，下半部分是滤镜'))


def u_adj_mode():
    ph, g = hall(CX, CY + 40, CW, CH - 40)
    cx_, top, hh = CX + CW * 0.6, g['top'], g['hh']
    # Pencil 模式：只涂到的假发变色
    painted = soft_stroke(f'M{cx_ - hh * 0.5:.1f} {top + hh * 0.1:.1f} q{hh * 0.5:.1f} -{hh * 0.3:.1f} {hh:.1f} 0', VIO, hh * 0.5, .55)
    pill, (px, py, pw, phh) = info_pill('色相、饱和度、亮度', dropdown=True, hl='pill')
    s = screen(ph + painted + pill + mode_dropdown(400, 102, 'Pencil', 'Pencil'), active='brush')
    s += brush_icon_star(*icon_pos('brush'))
    s += badge(px + pw + 18, py + 15, 1) + badge(400 + 100, 124, 2)
    s += side_note(64, 200, ['① 点顶部的小三角', '② 选图层或 Pencil'], YEL1, 14)
    s += side_note(64, 290, ['图层：整层一起变', 'Pencil：涂到哪里，', '　　　哪里才变'], WHITE, 14)
    s += label(CX + CW + 10, top + 30, '画笔图标上出现星标', YEL1, 13)
    s += arrow(CX + CW + 60, top + 8, icon_pos('brush')[0] - 4, 52, INK, 2)
    s += note('示意图，以实际界面为准')
    save('u-adj-mode', svg(W, H, s, '顶部提示栏的下拉菜单里选图层或 Pencil'))


def u_adj_actions():
    ph, g = hall(CX, CY, CW, CH)
    fx, fy = CX + 90, CY + 200
    menu = panel(fx + 26, fy - 70, 120, 5 * 30 + 12)
    for i, r in enumerate(['预览', '应用', '重置', '撤销', '取消']):
        yy = fy - 64 + i * 30
        menu += text(fx + 42, yy + 20, r, 14, 700, UITEXT)
        if r == '应用':
            menu += ringrect(fx + 30, yy, 112, 28)
    s = screen(ph + menu + fingertip(fx, fy), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += badge(fx - 22, fy - 18, 1) + badge(fx + 160, fy - 34 + 30, 2)
    s += side_note(CX + CW + 14, 150, ['① 调整界面里一指轻点画布', '② 弹出「调整操作」菜单'], YEL1, 14)
    s += side_note(CX + CW + 14, 250, ['预览：按住看调整前后', '应用：确认，留在这个调整里', '取消：全部不要，退出'], WHITE, 13, 30)
    s += side_note(70, 470, ['直接点魔棒图标 = 应用并退出'], YEL1, 14)
    s += note('示意图')
    save('u-adj-actions', svg(W, H, s, '在调整界面轻点画布，打开调整操作菜单'))


def u_dup_opacity():
    ph, g = hall(LX + 10, CY, 300, CH)
    lay, pos = layers2([L('曲线 校正', 'merged', sel=True, hl=False), L('原图', 'scene', lock=True)], x=440, y=62)
    nx, ny = 440 + 300 - 44, 62 + 44 + 19
    s = screen(ph + lay + blend_popup(440, 180, '正常', 0.6, 'op'), active='layers')
    s += ring(nx, ny, 15) + badge(nx - 36, ny - 30, 1)
    s += badge(440 + 264, 180 + 106, 2)
    s += side_note(440, 330, ['① 点调好的那层右边的字母 N', '② 拖「不透明度」，效果就减弱', '③ 点勾选框开关这层，和原图对比'], YEL1, 13, 30)
    s += ring(440 + 300 - 22, ny, 13) + badge(440 + 300 + 16, ny, 3)
    s += note('示意图')
    save('u-dup-opacity', svg(W, H, s, '复制一层再调整，用不透明度控制强弱'))


def u_hsb():
    ph, g = hall(CX, CY, CW, CH)
    bp, pos, y0 = bottom_panel(SY + SH - 12, 560, [('色相', .5), ('饱和度', .38), ('亮度', .5)], hl='饱和度')
    pill, _ = info_pill('色相、饱和度、亮度', dropdown=True)
    s = screen(tinted(ph, 'warm') + pill + bp, active='adjust') + ring(*icon_pos('adjust'), 18)
    s += badge(SX + SW / 2 - 280 - 2, y0 + 14 + 44 + 13, 1)
    s += side_note(64, 120, ['色相：所有颜色一起转', '饱和度：往左变灰，往右变艳', '亮度：整体变亮或变暗'], YEL1, 13, 30)
    s += side_note(CX + CW + 12, 160, ['修整张场照时，', '主要用「饱和度」：', '舞台灯太艳，往左拉一点'], WHITE, 13, 30)
    s += note('示意图')
    save('u-hsb', svg(W, H, s, '色相、饱和度、亮度：三个滑块'))


def u_balance():
    ph, g = hall(CX, CY, CW, CH - 40)
    bp, pos, y0 = bottom_panel(SY + SH - 12, 600, [('青色', '红色', .5), ('紫红色', '绿色', .5), ('黄色', '蓝色', .64)],
                               buttons=['阴影', '中间调', '高亮区域'], active_btn='中间调', hl='黄色', bipolar=True)
    pill, _ = info_pill('颜色平衡', dropdown=True)
    s = screen(tinted(ph, 'warm') + pill + bp, active='adjust') + ring(*icon_pos('adjust'), 18)
    s += badge(pos['中间调'][0], y0 + 2, 1)
    s += badge(pos['黄色'][0] + 22, pos['黄色'][1] - 20, 2)
    s += side_note(64, 120, ['① 先选明暗范围', '　 默认是「中间调」', '② 偏黄：第三条往蓝色拉'], YEL1, 13, 30)
    s += side_note(CX + CW + 12, 130, ['每条滑块两头是一对互补色', '往一头拉，另一头的颜色就少'], WHITE, 13, 30)
    s += note('示意图，滑块两端的字以实际界面为准')
    save('u-balance', svg(W, H, s, '颜色平衡：三条滑块和阴影、中间调、高亮区域按钮'))


def curve_graph(x, y, w, h, pts, color=WHITE, hist=True, grid=True, nodes=True, line_w=3):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#1F2329" stroke="#4B5563"/>']
    if grid:
        for i in range(1, 4):
            s.append(f'<line x1="{x + w * i / 4:.1f}" y1="{y}" x2="{x + w * i / 4:.1f}" y2="{y + h}" stroke="#374151"/>'
                     f'<line x1="{x}" y1="{y + h * i / 4:.1f}" x2="{x + w}" y2="{y + h * i / 4:.1f}" stroke="#374151"/>')
    if hist:
        d = f'M{x} {y + h}'
        for i in range(0, 41):
            t = i / 40
            v = 0.15 + 0.6 * math.exp(-((t - 0.38) / 0.18) ** 2) + 0.25 * math.exp(-((t - 0.75) / 0.08) ** 2)
            d += f' L{x + w * t:.1f} {y + h - h * 0.8 * v:.1f}'
        d += f' L{x + w} {y + h} Z'
        s.append(f'<path d="{d}" fill="#6B7280" fill-opacity=".7"/>')
    s.append(f'<line x1="{x}" y1="{y + h}" x2="{x + w}" y2="{y}" stroke="#6B7280" stroke-width="1.5" stroke-dasharray="4 4"/>')
    P = [(x + w * a, y + h - h * b) for a, b in pts]
    d = f'M{P[0][0]:.1f} {P[0][1]:.1f}'
    # 用 Catmull-Rom 画平滑曲线
    for i in range(len(P) - 1):
        p0 = P[i - 1] if i else P[i]; p1 = P[i]; p2 = P[i + 1]; p3 = P[i + 2] if i + 2 < len(P) else P[i + 1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f' C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}'
    s.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{line_w}"/>')
    if nodes:
        for px_, py_ in P[1:-1]:
            s.append(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="7" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>')
    return ''.join(s), P


def u_curves():
    ph, g = hall(300, 66, 200, 220)
    px, py, pw, phh = 150, 300, 500, 236
    s_panel = panel(px, py, pw, phh)
    tabs = ['伽玛', '红色', '绿色', '蓝色']
    tpos = {}
    for i, t in enumerate(tabs):
        bx = px + 20 + i * 86
        s_panel += f'<rect x="{bx}" y="{py + 12}" width="78" height="30" rx="8" fill="{UIBLUE if t == "绿色" else UIBAR}"/>' + text(bx + 39, py + 32, t, 14, 700, UITEXT, 'middle')
        tpos[t] = (bx, py + 12)
    gr, P = curve_graph(px + 20, py + 52, 300, 170, [(0, 0), (0.5, 0.44), (1, 1)], MINT)
    s_panel += gr
    pill, _ = info_pill('曲线', dropdown=True)
    s = screen(tinted(ph, 'green') + pill + s_panel, active='adjust') + ring(*icon_pos('adjust'), 18)
    s += ringrect(tpos['绿色'][0] - 3, tpos['绿色'][1] - 3, 84, 36) + badge(tpos['绿色'][0] + 39, py - 4, 1)
    s += badge(P[1][0] + 22, P[1][1] + 22, 2)
    s += text(px + 336, py + 76, '横轴：原来的亮度', 13, 700, UITEXT)
    s += text(px + 336, py + 100, '纵轴：调完的亮度', 13, 700, UITEXT)
    s += text(px + 336, py + 136, '在线上点一下加节点', 13, 600, UIDIM)
    s += text(px + 336, py + 160, '最多 11 个节点', 13, 600, UIDIM)
    s += text(px + 336, py + 184, '点节点再点「删除」', 13, 600, UIDIM)
    s += side_note(64, 120, ['① 选「绿色」通道', '② 中间点往下拖一点：', '　 中间调的绿色变少'], YEL1, 13, 30)
    s += note('示意图')
    save('u-curves', svg(W, H, s, '曲线：选通道，拖动节点'))


GRADS = [('神秘', ['#1E1B4B', '#7C3AED', '#FDE68A']), ('微风', ['#0F766E', '#5EEAD4', '#F0FDFA']), ('瞬间', ['#7F1D1D', '#F97316', '#FEF3C7']),
         ('威尼斯', ['#1E3A8A', '#F472B6', '#FEF9C3']), ('火焰', ['#450A0A', '#DC2626', '#FDE047']), ('霓虹灯', ['#2E1065', '#EC4899', '#67E8F9']),
         ('黑暗', ['#000000', '#374151', '#E5E7EB']), ('摩卡', ['#3B2416', '#A47551', '#F5E6D3'])]


def grad_bar(x, y, w, h, cols, rx=4):
    gid = uid('g')
    stops = ''.join(f'<stop offset="{i / (len(cols) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(cols))
    return (f'<defs><linearGradient id="{gid}">{stops}</linearGradient></defs>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="url(#{gid})" stroke="{INK}" stroke-width="1.5"/>')


def u_gradmap():
    ph, g = hall(300, 66, 200, 220)
    px, py, pw, phh = 130, 296, 540, 222
    s_panel = panel(px, py, pw, phh, '渐变色库') + text(px + pw - 24, py + 30, '+', 24, 700, UITEXT, 'middle')
    for i, (n, cols) in enumerate(GRADS):
        cx_ = px + 20 + (i % 4) * 128
        cy_ = py + 50 + (i // 4) * 84
        s_panel += grad_bar(cx_, cy_, 116, 34, cols) + text(cx_ + 58, cy_ + 56, n, 14, 700, UITEXT, 'middle')
        if n == '黑暗':
            s_panel += ringrect(cx_ - 5, cy_ - 5, 126, 70)
            hx, hy = cx_ + 58, cy_
    pill, _ = info_pill('渐变映射', dropdown=True)
    s = screen(tinted(ph, 'gray') + pill + s_panel, active='adjust') + ring(*icon_pos('adjust'), 18)
    s += badge(hx + 70, hy - 6, 1)
    s += badge(px + pw - 24, py - 6, 2)
    s += side_note(64, 120, ['① 点一个预设，马上套用', '　 「黑暗」接近黑白，', '　 可以拿来检查明暗'], YEL1, 13, 30)
    s += side_note(520, 120, ['② 点「+」自己做渐变：', '左端管暗部，右端管亮部'], WHITE, 13, 30)
    s += note('示意图，预设的颜色以实际界面为准')
    save('u-gradmap', svg(W, H, s, '渐变映射：渐变色库里点预设或新建'))


def color_value_panel(x, y, rgb, hl=True, w=300):
    s = [panel(x, y, w, 250, '颜色')]
    s.append(f'<rect x="{x + w - 70}" y="{y + 12}" width="54" height="24" rx="6" fill="rgb({rgb[0]},{rgb[1]},{rgb[2]})" stroke="{UITEXT}" stroke-width="1.5"/>')
    names = ['红', '绿', '蓝']
    cols = ['#EF4444', '#22C55E', '#3B82F6']
    for i in range(3):
        yy = y + 70 + i * 46
        s.append(text(x + 18, yy + 5, names[i], 14, 700, UITEXT))
        s.append(f'<rect x="{x + 46}" y="{yy - 4}" width="170" height="8" rx="4" fill="#6B7280"/><rect x="{x + 46}" y="{yy - 4}" width="{170 * rgb[i] / 255:.1f}" height="8" rx="4" fill="{cols[i]}"/>')
        s.append(f'<rect x="{x + 228}" y="{yy - 14}" width="56" height="28" rx="6" fill="{UIBAR}"/>' + text(x + 256, yy + 6, str(rgb[i]), 15, 800, WHITE, 'middle'))
    if hl:
        s.append(ringrect(x + 222, y + 50, 68, 136))
    tabs = ['色盘', '经典', '色彩调和', '值', '调色板']
    tx = x + 10
    for t in tabs:
        tw_ = tw(t, 13) + 14
        s.append(f'<rect x="{tx:.1f}" y="{y + 212}" width="{tw_:.1f}" height="26" rx="7" fill="{UIBLUE if t == "值" else UIBAR}"/>' + text(tx + tw_ / 2, y + 230, t, 13, 700, UITEXT, 'middle'))
        tx += tw_ + 5
    return ''.join(s)


def u_eyedrop():
    ph, g = hall(LX + 20, CY, 300, CH)
    bx, by = g['board']
    s = screen(tinted(ph, 'warm') + pencil(bx, by, -30) + f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="20" fill="none" stroke="{WHITE}" stroke-width="4"/>'
               + color_value_panel(470, 62, (176, 164, 128)), active='color')
    s += ring(39, 277, 17) + badge(39, 312, 1)
    s += badge(bx + 30, by + 26, 2)
    s += badge(470 + 300 + 0, 62 + 120, 3)
    s += side_note(64, 470, ['① 按住侧栏的方形按钮　② 笔点灰色的展板　③ 在「值」里看红绿蓝'], YEL1, 13)
    s += side_note(470, 350, ['红 176 > 绿 164 > 蓝 128', '红绿多、蓝少 → 偏黄', '调到三个数接近就是中性灰'], WHITE, 13, 30)
    s += note('示意图')
    save('u-eyedrop', svg(W, H, s, '用吸管吸取灰色物体，在颜色面板的值里看红绿蓝数值'))


# ---------- 2.1 原理图 ----------
def p_adj_destructive():
    Wd, Hd = 760, 340
    s = []
    for col, (title, fill) in enumerate([('直接在原图层上调', RED1), ('先复制一层，在副本上调', MINT1)]):
        ox = 20 + col * 380
        s.append(panel_box(ox, 10, 360, 320, title, WHITE, fill))
        if col == 0:
            s.append(thumb_big(ox + 40, 70, 'warm', '原图'))
            s.append(arrow(ox + 150, 120, ox + 200, 120, INK, 3))
            s.append(thumb_big(ox + 210, 70, None, '调过的原图'))
            s.append(text(ox + 30, 252, '像素被改掉了，原来的颜色没了', 14, 700))
            s.append(text(ox + 30, 278, '退出以后不能再打开刚才的曲线微调', 14, 400, MUTED))
            s.append(text(ox + 30, 304, '只能撤销，或者在这个基础上再调一次', 14, 400, MUTED))
        else:
            s.append(thumb_big(ox + 40, 70, 'warm', '原图（锁定）'))
            s.append(thumb_big(ox + 210, 70, None, '副本：已调'))
            s.append(text(ox + 30, 252, '原图还在下面，随时能对比、能重来', 14, 700))
            s.append(text(ox + 30, 278, '副本的不透明度 = 事后还能调的"强度"', 14, 400, MUTED))
            s.append(text(ox + 30, 304, '例：调过头了，不透明度拉到 60%', 14, 400, MUTED))
    save('p-adj-destructive', svg(Wd, Hd, ''.join(s), '调整直接改像素，所以先复制一层再调'))


def thumb_big(x, y, tint, cap, w=110, h=130):
    ph, g = hall(x, y, w, h, board=True)
    body = tinted(ph, tint) if tint else ph
    return (body + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
            + text(x + w / 2, y + h + 20, cap, 13, 700, INK, 'middle'))


def p_adj_scope():
    Wd, Hd = 760, 300
    s = []
    titles = [('图层：整层一起变', YEL1), ('Pencil：涂到哪里变哪里', VIO1), ('先建选区：只变选区里', MINT1)]
    for col, (t, f) in enumerate(titles):
        ox = 14 + col * 250
        s.append(panel_box(ox, 10, 236, 280, t, WHITE, f))
        x, y, w, h = ox + 28, 60, 180, 180
        ph, g = hall(x, y, w, h)
        if col == 0:
            s.append(tinted(ph, 'gray'))
        elif col == 1:
            cid = uid('pc')
            s.append(ph + f'<defs><clipPath id="{cid}"><path d="M{x + 80} {y + 20} q30 -10 60 10 q10 40 -20 60 q-30 10 -45 -20 z"/></clipPath></defs>'
                     f'<g clip-path="url(#{cid})">{tinted(ph, "gray")}</g>')
            s.append(f'<path d="M{x + 80} {y + 20} q30 -10 60 10 q10 40 -20 60 q-30 10 -45 -20 z" fill="none" stroke="{VIO7}" stroke-width="2" stroke-dasharray="4 3"/>')
        else:
            s.append(ph + clip(tinted(ph, 'gray'), x, y + 120, w, 60))
            s.append(f'<rect x="{x}" y="{y + 120}" width="{w}" height="60" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="6 5"/>')
        s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>')
        s.append(text(ox + 118, 272, ['适合：整体校色', '适合：只改假发、只压一块亮', '适合：边界清楚的一块（地面）'][col], 13, 600, MUTED, 'middle'))
    save('p-adj-scope', svg(Wd, Hd, ''.join(s), '同一个调整（这里是去色）的三种作用范围'))


def p_balance():
    Wd, Hd = 760, 360
    s = [panel_box(20, 10, 720, 340, '颜色平衡：三对互补色，往哪头拉就加哪种颜色', WHITE, YEL1)]
    pairs = [('青色', '红色', '#06B6D4', '#EF4444', '偏红（脸太红）→ 往青色拉'),
             ('紫红色', '绿色', '#D946EF', '#22C55E', '偏绿（日光灯）→ 往紫红色拉'),
             ('黄色', '蓝色', '#EAB308', '#3B82F6', '偏黄（室内暖光）→ 往蓝色拉')]
    for i, (a, b, ca, cb, tip) in enumerate(pairs):
        y = 80 + i * 66
        s.append(text(150, y + 6, a, 16, 800, INK, 'end') + text(470, y + 6, b, 16, 800))
        s.append(grad_bar(162, y - 10, 296, 22, [ca, '#E5E7EB', cb], 11))
        s.append(f'<line x1="310" y1="{y - 16}" x2="310" y2="{y + 18}" stroke="{INK}" stroke-width="2"/>')
        s.append(label(530, y + 6, tip, [RED1, MINT1, YEL1][i] if i != 1 else MINT1, 13))
    y = 290
    s.append(grad_bar(60, y - 14, 330, 26, ['#111827', '#9CA3AF', '#F9FAFB'], 6))
    for j, (n, x0) in enumerate([('阴影', 60), ('中间调', 170), ('高亮区域', 280)]):
        s.append(f'<rect x="{x0}" y="{y - 14}" width="110" height="26" fill="none" stroke="{INK}" stroke-width="2"/>')
        s.append(text(x0 + 55, y + 34, n, 14, 700, INK, 'middle'))
    s.append(text(420, y + 4, '三个按钮决定改哪一段明暗。', 14, 700))
    s.append(text(420, y + 30, '偏色多半整张都偏，先改「中间调」。', 14, 400, MUTED))
    save('p-balance', svg(Wd, Hd, ''.join(s), '颜色平衡的三对互补色和三个明暗范围'))


def p_curve():
    Wd, Hd = 760, 330
    s = []
    items = [('提亮中间调', [(0, 0), (0.5, 0.62), (1, 1)], WHITE, '暗部和亮部两头基本不动，\n不会把黑色提成灰色'),
             ('S 形：加对比', [(0, 0), (0.27, 0.2), (0.73, 0.82), (1, 1)], WHITE, '暗的更暗、亮的更亮，\n中间的坡更陡'),
             ('绿色通道往下：去绿', [(0, 0), (0.5, 0.44), (1, 1)], MINT, '只减中间调的绿色，\n画面往紫红色偏一点')]
    for col, (t, pts, c, note_) in enumerate(items):
        ox = 14 + col * 250
        s.append(panel_box(ox, 10, 236, 310, t, WHITE, [YEL1, VIO1, MINT1][col]))
        gr, P = curve_graph(ox + 28, 60, 180, 160, pts, c, hist=False)
        s.append(gr)
        for k, ln in enumerate(note_.split('\n')):
            s.append(text(ox + 118, 252 + k * 24, ln, 13, 600, INK if k == 0 else MUTED, 'middle'))
    s.append(text(380, Hd - 4, '', 1))
    save('p-curve', svg(Wd, Hd, ''.join(s), '曲线的三种常见用法'))


def p_gradmap():
    Wd, Hd = 760, 300
    s = [panel_box(20, 10, 720, 280, '渐变映射：按亮度换颜色', WHITE, YEL1)]
    s.append(text(60, 84, '照片里每个点的亮度', 14, 700))
    s.append(grad_bar(60, 96, 640, 30, ['#000000', '#808080', '#FFFFFF']))
    for i, t in enumerate([0.1, 0.35, 0.6, 0.9]):
        x = 60 + 640 * t
        s.append(arrow(x, 132, x, 168, INK, 2.5))
    s.append(grad_bar(60, 176, 640, 30, ['#3B2416', '#A47551', '#F5E6D3']))
    s.append(text(60, 230, '换成渐变上同一位置的颜色（这里是一条棕色调的渐变）', 14, 700))
    s.append(text(60, 258, '左端管最暗的地方，右端管最亮的地方。直接套用会很重，修图里一般把这层的不透明度降到 10%～30%。', 13, 400, MUTED))
    save('p-gradmap', svg(Wd, Hd, ''.join(s), '渐变映射把亮度换成渐变上的颜色'))


def p_gray():
    Wd, Hd = 760, 260
    s = []
    data = [('偏黄（室内暖光）', (176, 164, 128), RED1), ('偏绿（日光灯）', (150, 172, 152), RED1), ('校正后', (160, 160, 158), MINT1)]
    for col, (t, rgb, f) in enumerate(data):
        ox = 14 + col * 250
        s.append(panel_box(ox, 10, 236, 240, t, WHITE, f))
        s.append(f'<rect x="{ox + 28}" y="62" width="180" height="90" rx="8" fill="rgb{rgb}" stroke="{INK}" stroke-width="2.5"/>')
        for k, (n, v, c) in enumerate(zip('红绿蓝', rgb, ['#EF4444', '#22C55E', '#3B82F6'])):
            y = 178 + k * 22
            s.append(text(ox + 30, y, n, 13, 700) + f'<rect x="{ox + 52}" y="{y - 10}" width="{v * 0.55:.1f}" height="12" rx="3" fill="{c}"/>' + text(ox + 60 + v * 0.55, y, str(v), 13, 800))
    save('p-gray', svg(Wd, Hd, ''.join(s), '灰色物体的红绿蓝数值：偏色时三个数差得多，校正后接近相等'))


# ---------- 2.1 案例 ----------
def case_hall(kind, after, cap):
    Wd, Hd = 640, 520
    ph, g = hall(20, 20, 600, 480)
    body = ph if after else tinted(ph, kind)
    s = [body, f'<rect x="20" y="20" width="600" height="480" fill="none" stroke="{INK}" stroke-width="2"/>']
    s.append(label(606, 56, cap, VIO1, 16, 'end') if after else label(34, 56, cap, YEL1, 16))
    return svg(Wd, Hd, ''.join(s), cap)


def run_m201():
    for f in [u_adj_menu, u_adj_mode, u_adj_actions, u_dup_opacity, u_hsb, u_balance, u_curves, u_gradmap, u_eyedrop,
              p_adj_destructive, p_adj_scope, p_balance, p_curve, p_gradmap, p_gray]:
        f()
    save('case-warm-before', case_hall('warm', False, '修之前：室内暖光，整张偏黄'))
    save('case-warm-after', case_hall('warm', True, '修之后：展板回到中性灰'))
    save('case-green-before', case_hall('green', False, '修之前：日光灯下偏绿'))
    save('case-green-after', case_hall('green', True, '修之后：肤色和展板正常'))
    save('case-dark-before', case_hall('dark', False, '修之前：场馆太暗'))
    save('case-dark-after', case_hall('dark', True, '修之后：中间调提亮，黑白两头还在'))



# ======================= 2.2 克隆 =======================
SPOTS = [(-0.62, 0.55, 0.07), (-0.45, 0.85, 0.055), (0.58, 0.62, 0.07), (0.2, -0.75, 0.06), (0.72, 0.3, 0.05)]


def brush_lib(x, y, sel_group='气笔修饰', sel='软画笔', w=300):
    s = [panel(x, y, w, 300, '画笔库') + text(x + w - 24, y + 30, '+', 24, 700, UITEXT, 'middle')]
    groups = ['…', '着墨', '…', '气笔修饰', '…']
    for i, gname in enumerate(groups):
        yy = y + 48 + i * 40
        on = gname == sel_group
        s.append(f'<rect x="{x + 10}" y="{yy}" width="110" height="34" rx="8" fill="{UIBLUE if on else UIBAR}"/>' + text(x + 22, yy + 23, gname, 14, 700, UITEXT))
    brushes = [sel, None, None, None]
    for i, b in enumerate(brushes):
        yy = y + 48 + i * 60
        s.append(f'<rect x="{x + 130}" y="{yy}" width="{w - 140}" height="52" rx="8" fill="{UIBLUE if b else UIBAR}"/>')
        if b:
            s.append(text(x + 142, yy + 20, b, 14, 700, WHITE))
            s.append(soft_stroke(f'M{x + 146} {yy + 38} q40 -10 80 0 t60 0', WHITE, 10, .8))
            s.append(ringrect(x + 126, yy - 4, w - 132, 60))
        else:
            s.append(f'<path d="M{x + 146} {yy + 30} q40 -10 80 0 t60 0" fill="none" stroke="#6B7280" stroke-width="4" stroke-linecap="round"/>')
    return ''.join(s)


def u_clone_layer():
    ph, g = face_photo(LX + 10, CY, 300, CH, SPOTS)
    lay, pos = layers2([L('去瑕疵', 'face', sel=True, hl=True), L('原图', 'face', lock=True)], x=440, y=62)
    s = screen(ph + lay, active='layers') + ring(*icon_pos('layers'), 18)
    s += badge(440 - 18, 62 + 44 + 19, 1)
    s += side_note(440, 210, ['① 复制原图，改名「去瑕疵」，', '　 原图锁定', '克隆只在当前图层里取样和涂，', '空白新图层上用不了'], YEL1, 13, 30)
    s += note('示意图')
    save('u-clone-layer', svg(W, H, s, '在原图的副本上做克隆'))


def u_clone_disc():
    ph, g = face_photo(CX, CY, CW, CH, SPOTS)
    sx, sy = spot_pos(g, -0.62, 0.55)
    dx, dy = spot_pos(g, -0.22, 0.78)   # 旁边干净的皮肤
    body = ph + disc(dx, dy, 13) + f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="12" fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-dasharray="4 3"/>' + pencil(sx - 2, sy + 4, 215)
    s = screen(body + tool_sliders([('画笔尺寸', 0.12), ('强度', 1.0)]), active='adjust') + ring(*icon_pos('adjust'), 18)
    s += badge(dx + 26, dy + 10, 1) + badge(sx - 4, sy - 26, 2)
    bx = SX + SW / 2 - ((2 * (92 + 24) + 24) / 2) + 12
    s += ringrect(bx - 2, SY + SH - 74 + 6, 2 * (92 + 24) + 4, 52) + badge(bx - 18, SY + SH - 44, 3)
    s += side_note(64, 140, ['① 把圆盘拖到旁边', '　 干净的皮肤上', '② 笔涂在痘痘上', '③ 尺寸比痘痘大一圈，', '　 强度先用 100%'], YEL1, 13, 30)
    s += side_note(CX + CW + 12, 160, ['圆盘里的皮肤', '会被复制到', '笔尖涂的地方'], WHITE, 13, 30)
    save('u-clone-disc', svg(W, H, s, '克隆：圆盘放在干净皮肤上取样，在痘痘上涂'))


def u_clone_lock():
    ph, g = face_photo(CX, CY, CW, CH, SPOTS)
    dx, dy = spot_pos(g, -0.22, 0.78)
    pill, (px, py, pw, phh) = info_pill('克隆锁定')
    s = screen(ph + disc(dx, dy, 13, locked=True) + fingertip(dx + 8, dy + 22) + pill + tool_sliders([('画笔尺寸', 0.12), ('强度', 1.0)]), active='adjust')
    s += badge(dx + 32, dy - 16, 1) + badge(px + pw + 18, py + 15, 2)
    s += side_note(64, 150, ['① 手指按住圆盘不放，', '　 等它放大一下', '② 顶部提示已锁定', '再长按一次就解锁', '（提示文字以实际界面为准）'], YEL1, 13, 30)
    s += side_note(CX + CW + 12, 160, ['锁定后：每一笔', '都从这里开始取样'], WHITE, 13, 30)
    save('u-clone-lock', svg(W, H, s, '长按圆盘锁定取样点'))


def u_clone_brush():
    ph, g = face_photo(LX + 10, CY, 300, CH, SPOTS)
    dx, dy = spot_pos(g, -0.62, 0.22)
    s = screen(ph + disc(dx, dy, 13) + brush_lib(440, 62), active='brush')
    s += ring(*icon_pos('brush'), 18) + badge(icon_pos('brush')[0] - 26, 62, 1)
    s += badge(440 + 300 + 14, 62 + 48 + 26, 2)
    s += side_note(440, 400, ['① 克隆界面里点画笔图标', '② 气笔修饰 › 软画笔：边缘柔，', '　 修皮肤接缝看不出', '布料、地面换硬边的笔'], YEL1, 13, 30)
    s += note('示意图，画笔库只画了用到的分组')
    save('u-clone-brush', svg(W, H, s, '克隆笔刷选气笔修饰里的软画笔'))


def p_clone_offset():
    Wd, Hd = 760, 320
    s = [panel_box(20, 10, 720, 300, '取样原理：圆盘跟着笔走，两者的距离和方向一直不变', WHITE, YEL1)]
    # 皮肤纹理块
    s.append(f'<rect x="60" y="70" width="640" height="200" rx="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
    rnd = random.Random(4)
    for _ in range(120):
        s.append(f'<circle cx="{70 + rnd.random() * 620:.1f}" cy="{80 + rnd.random() * 180:.1f}" r="{1 + rnd.random() * 1.5:.1f}" fill="#E8B9A0"/>')
    path_b = 'M380 210 q60 -40 120 -10 t120 -20'
    path_d = 'M180 150 q60 -40 120 -10 t120 -20'
    s.append(f'<path d="{path_d}" fill="none" stroke="{VIO7}" stroke-width="4" stroke-dasharray="7 6"/>')
    s.append(f'<path d="{path_b}" fill="none" stroke="{PINK}" stroke-width="14" stroke-linecap="round" stroke-opacity=".55"/>')
    s.append(disc(180, 150, 16) + pencil(380, 210, -30))
    s.append(arrow(196, 156, 366, 206, INK, 2.5, '6 5'))
    s.append(label(232, 140, '取样圆盘', VIO1, 13) + label(410, 252, '笔尖：画在这里', PINK1, 13))
    s.append(label(250, 228, '这段距离不变', YEL1, 13))
    s.append(disc(420, 120, 16) + f'<path d="M620 180 l0 0" />')
    s.append(text(440, 112, '笔走到右边，圆盘也平移到右边', 13, 700, VIO7))
    save('p-clone-offset', svg(Wd, Hd, ''.join(s), '克隆的取样原理：圆盘和笔尖保持固定的距离一起移动'))


def p_clone_near():
    Wd, Hd = 760, 330
    s = []
    titles = [('太近：同一块纹理重复', RED1), ('合适：隔开 2～4 个瑕疵宽', MINT1), ('太远：明暗、颜色对不上', RED1)]
    for col, (t, f) in enumerate(titles):
        ox = 14 + col * 250
        s.append(panel_box(ox, 10, 236, 310, t, WHITE, f))
        x, y, w, h = ox + 18, 56, 200, 200
        gid = uid('sh')
        s.append(f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FCD9C2"/><stop offset="1" stop-color="#D9A48A"/></linearGradient></defs>'
                 f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="url(#{gid})" stroke="{INK}" stroke-width="2"/>')
        rnd = random.Random(7)
        for _ in range(70):
            s.append(f'<circle cx="{x + 6 + rnd.random() * (w - 12):.1f}" cy="{y + 6 + rnd.random() * (h - 12):.1f}" r="{1 + rnd.random() * 1.4:.1f}" fill="#C58C73" fill-opacity=".7"/>')
        tx, ty = x + 70, y + 110
        if col == 0:
            for k in range(3):
                s.append(f'<g transform="translate({k * 22},{k * 4})"><circle cx="{tx}" cy="{ty}" r="12" fill="none" stroke="{RED}" stroke-width="2.5"/>'
                         f'<circle cx="{tx - 4}" cy="{ty - 3}" r="2" fill="#9A5B45"/><circle cx="{tx + 4}" cy="{ty + 3}" r="2" fill="#9A5B45"/></g>')
            s.append(disc(tx + 30, ty - 20, 12))
            s.append(text(ox + 118, 280, '笔涂进了刚补过的地方，', 13, 600, INK, 'middle') + text(ox + 118, 302, '同一个图案一排排出现', 13, 400, MUTED, 'middle'))
        elif col == 1:
            s.append(f'<circle cx="{tx}" cy="{ty}" r="12" fill="none" stroke="{MINT7}" stroke-width="2.5"/>' + disc(tx, ty - 62, 12))
            s.append(f'<line x1="{tx}" y1="{ty - 48}" x2="{tx}" y2="{ty - 14}" stroke="{INK}" stroke-width="2" stroke-dasharray="4 3"/>')
            s.append(text(ox + 118, 280, '沿着同一条明暗带取样', 13, 600, INK, 'middle') + text(ox + 118, 302, '（离光一样远的地方）', 13, 400, MUTED, 'middle'))
        else:
            s.append(f'<circle cx="{x + 40}" cy="{ty}" r="12" fill="#C58C73" stroke="{RED}" stroke-width="2.5"/>' + disc(x + 170, ty, 12))
            s.append(arrow(x + 154, ty, x + 56, ty, INK, 2, '4 3'))
            s.append(text(ox + 118, 280, '从暗面取样补到亮面，', 13, 600, INK, 'middle') + text(ox + 118, 302, '补出一块深色的斑', 13, 400, MUTED, 'middle'))
    save('p-clone-near', svg(Wd, Hd, ''.join(s), '取样点离修补处多远合适'))


def p_clone_lift():
    Wd, Hd = 760, 300
    s = []
    titles = [('没锁定：抬笔再落笔，圆盘停在上一笔的终点', YEL1), ('锁定：每一笔都从同一个点开始', VIO1)]
    for col, (t, f) in enumerate(titles):
        ox = 20 + col * 380
        s.append(panel_box(ox, 10, 360, 280, t, WHITE, f))
        x, y = ox + 30, 60
        # 条纹布料纹理
        s.append(f'<rect x="{x}" y="{y}" width="300" height="160" rx="10" fill="{VIO1}" stroke="{INK}" stroke-width="2"/>')
        for k in range(0, 300, 18):
            s.append(f'<line x1="{x + k}" y1="{y}" x2="{x + k}" y2="{y + 160}" stroke="{VIO2}" stroke-width="6"/>')
        if col == 0:
            s.append(disc(x + 60, y + 50, 12) + f'<path d="M{x + 150} {y + 110} h50" stroke="{PINK}" stroke-width="12" stroke-linecap="round" stroke-opacity=".6"/>')
            s.append(disc(x + 110, y + 50, 12))
            s.append(arrow(x + 72, y + 50, x + 96, y + 50, INK, 2))
            s.append(f'<path d="M{x + 214} {y + 112} h40" stroke="{RED}" stroke-width="12" stroke-linecap="round" stroke-opacity=".5"/>')
            s.append(text(ox + 30, 246, '第二笔从别处开始，取样位置跟着变了，', 13, 600))
            s.append(text(ox + 30, 268, '条纹接不上。一段纹理尽量一笔涂完。', 13, 400, MUTED))
        else:
            s.append(disc(x + 60, y + 50, 15, locked=True))
            for k in range(3):
                s.append(f'<circle cx="{x + 150 + k * 50}" cy="{y + 110}" r="12" fill="none" stroke="{VIO7}" stroke-width="2.5"/>')
            s.append(text(ox + 30, 246, '适合点修很多个小瑕疵：每次都用同一块干净皮肤。', 13, 600))
            s.append(text(ox + 30, 268, '大面积用锁定会印出一模一样的图案。', 13, 400, MUTED))
    save('p-clone-lift', svg(Wd, Hd, ''.join(s), '锁定与不锁定的区别'))


def case_acne(after):
    Wd, Hd = 640, 520
    ph, g = face_photo(20, 20, 600, 480, () if after else SPOTS + [(-0.3, 0.95, 0.03), (0.35, 0.9, 0.035), (-0.1, -0.85, 0.04)])
    s = [ph, f'<rect x="20" y="20" width="600" height="480" fill="none" stroke="{INK}" stroke-width="2"/>']
    cap = '修之后：痘痘去掉，脸颊的纹理还在' if after else '修之前：脸颊和额头有 8 处痘痘'
    if after:
        rnd = random.Random(2)
        cx, cy, fw = g['cx'], g['cy'], g['fw']
        for _ in range(140):
            a = rnd.random() * 6.28; r = rnd.random() ** .5
            s.append(f'<circle cx="{cx + math.cos(a) * r * fw * 0.9:.1f}" cy="{cy + 0.3 * fw + math.sin(a) * r * fw * 0.7:.1f}" r="1.2" fill="#E8B9A0" fill-opacity=".8"/>')
    s.append(label(606, 56, cap, VIO1, 16, 'end') if after else label(34, 56, cap, YEL1, 16))
    return svg(Wd, Hd, ''.join(s), cap)


def cloak_scene(after, x=20, y=20, w=600, h=480):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#E0E7FF"/>']
    # 白色披风，三道褶
    s.append(f'<path d="M{x + 120} {y + 40} Q{x + 300} {y + 10} {x + 480} {y + 40} L{x + 560} {y + h} L{x + 40} {y + h} Z" fill="#F8FAFC" stroke="{INK}" stroke-width="3"/>')
    for k, fx in enumerate([200, 300, 400]):
        s.append(f'<path d="M{x + fx} {y + 60} Q{x + fx - 20 + k * 20} {y + 250} {x + fx - 40 + k * 40} {y + h}" fill="none" stroke="#CBD5E1" stroke-width="22" stroke-linecap="round"/>')
        s.append(f'<path d="M{x + fx + 12} {y + 60} Q{x + fx - 8 + k * 20} {y + 250} {x + fx - 28 + k * 40} {y + h}" fill="none" stroke="#94A3B8" stroke-width="3"/>')
    if not after:
        s.append(f'<path d="M{x + 270} {y + 270} q30 -14 52 6 q14 22 -12 34 q-30 10 -44 -12 z" fill="#A16207" fill-opacity=".45"/>')
        s.append(f'<circle cx="{x + 340}" cy="{y + 330}" r="8" fill="#A16207" fill-opacity=".4"/>')
        s.append(f'<circle cx="{x + 230}" cy="{y + 380}" r="6" fill="#A16207" fill-opacity=".35"/>')
    return clip(''.join(s), x, y, w, h)


def case_stain(after):
    cap = '修之后：污渍去掉，褶皱的明暗连着' if after else '修之前：白披风上有一块饮料渍'
    s = [cloak_scene(after), f'<rect x="20" y="20" width="600" height="480" fill="none" stroke="{INK}" stroke-width="2"/>']
    s.append(label(606, 56, cap, VIO1, 16, 'end') if after else label(34, 56, cap, YEL1, 16))
    return svg(640, 520, ''.join(s), cap)


def floor_scene(after, x=20, y=20, w=600, h=480):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#F5F1E8"/>']
    fy = y + h * 0.55
    s.append(f'<rect x="{x}" y="{fy}" width="{w}" height="{y + h - fy}" fill="#D6D3D1"/>')
    # 透视地砖缝
    vx = x + w / 2
    for k in range(-6, 7):
        s.append(f'<line x1="{vx + k * 30}" y1="{fy}" x2="{vx + k * 150}" y2="{y + h}" stroke="#A8A29E" stroke-width="2"/>')
    yy, step = fy, 14
    while yy < y + h:
        s.append(f'<line x1="{x}" y1="{yy:.1f}" x2="{x + w}" y2="{yy:.1f}" stroke="#A8A29E" stroke-width="2"/>')
        step *= 1.35; yy += step
    s.append(figure(x + w * 0.5, y + 30, 46, y + 30 + 46 * 3.6, fy + 120, sw=2.5))
    if not after:
        s.append(f'<rect x="{x + 80}" y="{y + h - 70}" width="90" height="16" fill="#FDE047" stroke="{INK}" stroke-width="1.5" transform="rotate(-8 {x + 120} {y + h - 60})"/>')
        s.append(f'<path d="M{x + 450} {y + h - 110} l26 -6 l8 18 l-28 8 z" fill="#FFFFFF" stroke="{INK}" stroke-width="1.5"/>')
        s.append(f'<circle cx="{x + 500}" cy="{y + h - 60}" r="7" fill="#57534E"/>')
    return clip(''.join(s), x, y, w, h)


def case_floor(after):
    cap = '修之后：胶带和纸屑去掉，地砖缝还是直的' if after else '修之前：地上有地标胶带和纸屑'
    s = [floor_scene(after), f'<rect x="20" y="20" width="600" height="480" fill="none" stroke="{INK}" stroke-width="2"/>']
    s.append(label(606, 56, cap, VIO1, 16, 'end') if after else label(34, 56, cap, YEL1, 16))
    return svg(640, 520, ''.join(s), cap)


def u_clone_texture():
    kx, ky = CW / 600, CH / 480
    ph = clip(f'<g transform="translate({CX},{CY}) scale({kx:.4f},{ky:.4f})">{cloak_scene(False, 0, 0, 600, 480)}</g>', CX, CY, CW, CH)
    sx, sy = CX + 296 * kx, CY + 292 * ky
    dx, dy = CX + 300 * kx, CY + 150 * ky
    path = f'M{sx - 4:.1f} {sy - 30:.1f} Q{sx - 8:.1f} {sy:.1f} {sx - 12:.1f} {sy + 34:.1f}'
    body = ph + disc(dx, dy, 13) + f'<path d="{path}" fill="none" stroke="{PINK}" stroke-width="14" stroke-linecap="round" stroke-opacity=".5"/>' + pencil(sx - 12, sy + 34, 215)
    body += arrow(dx + 22, dy, dx + 22, dy + 60, VIO7, 2.5, '5 4', 'arwv')
    s = screen(body + tool_sliders([('画笔尺寸', 0.18), ('强度', 1.0)]), active='adjust') + ring(*icon_pos('adjust'), 18)
    s += badge(dx - 28, dy, 1) + badge(sx + 24, sy, 2)
    s += side_note(64, 130, ['① 圆盘放在同一道褶皱上，', '　 不锁定', '② 从污渍一头落笔，', '　 顺着褶皱一笔涂到另一头'], YEL1, 13, 30)
    s += side_note(CX + CW + 12, 150, ['中途不抬笔：', '圆盘跟着笔往下走，', '褶皱的明暗就连着'], WHITE, 13, 30)
    save('u-clone-texture', svg(W, H, s, '修纹理：圆盘放在同一道褶皱上，顺着褶皱一笔涂完'))


def run_m202():
    for f in [u_clone_layer, u_clone_disc, u_clone_lock, u_clone_brush, u_clone_texture, p_clone_offset, p_clone_near, p_clone_lift]:
        f()
    save('case-acne-before', case_acne(False)); save('case-acne-after', case_acne(True))
    save('case-stain-before', case_stain(False)); save('case-stain-after', case_stain(True))
    save('case-floor-before', case_floor(False)); save('case-floor-after', case_floor(True))



# ======================= 2.3 液化 =======================
def halfbody(x, y, w, h, arm=1.0, grid=False, push=None, bend=0.0):
    """半身照：门框竖线、墙裙横线、人物（左臂粗细 arm）。bend>0 时背景直线被推弯（演示错误）"""
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFF7E6"/>']
    lx = x + w * 0.16
    if bend:
        s.append(f'<path d="M{lx:.1f} {y} L{lx:.1f} {y + h * 0.45:.1f} Q{lx + w * bend:.1f} {y + h * 0.58:.1f} {lx:.1f} {y + h * 0.72:.1f} L{lx:.1f} {y + h}" fill="none" stroke="{INK}" stroke-width="5"/>')
    else:
        s.append(f'<line x1="{lx:.1f}" y1="{y}" x2="{lx:.1f}" y2="{y + h}" stroke="{INK}" stroke-width="5"/>')
    s.append(f'<line x1="{x + w * 0.9:.1f}" y1="{y}" x2="{x + w * 0.9:.1f}" y2="{y + h}" stroke="{INK}" stroke-width="5"/>')
    s.append(f'<line x1="{x}" y1="{y + h * 0.7:.1f}" x2="{x + w}" y2="{y + h * 0.7:.1f}" stroke="#D6CBB5" stroke-width="4"/>')
    cx = x + w * 0.52
    u = w / 6.0
    hy = y + h * 0.08
    # 头发、头
    s.append(f'<path d="M{cx - u * 0.95:.1f} {hy + u * 0.7:.1f} Q{cx - u * 1.1:.1f} {hy + u * 2.6:.1f} {cx - u * 0.8:.1f} {hy + u * 3.0:.1f} L{cx + u * 0.8:.1f} {hy + u * 3.0:.1f} Q{cx + u * 1.1:.1f} {hy + u * 2.6:.1f} {cx + u * 0.95:.1f} {hy + u * 0.7:.1f} Z" fill="{PINK}" stroke="{INK}" stroke-width="3"/>')
    neck_y = hy + u * 1.7
    sh_y = hy + u * 2.3
    s.append(f'<rect x="{cx - u * 0.22:.1f}" y="{neck_y:.1f}" width="{u * 0.44:.1f}" height="{u * 0.75:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M{cx - u * 1.35:.1f} {sh_y:.1f} Q{cx:.1f} {sh_y - u * 0.2:.1f} {cx + u * 1.35:.1f} {sh_y:.1f} L{cx + u * 1.05:.1f} {y + h + 5:.1f} L{cx - u * 1.05:.1f} {y + h + 5:.1f} Z" fill="{VIO2}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
    # 手臂（左臂可变粗）
    for sgn in (-1, 1):
        aw = u * 0.42 * (arm if sgn < 0 else 1.0)
        ax = cx + sgn * u * 1.42
        d = f'M{ax:.1f} {sh_y + u * 0.2:.1f} Q{ax + sgn * u * 0.25:.1f} {sh_y + u * 1.6:.1f} {ax + sgn * u * 0.1:.1f} {y + h + 10:.1f}'
        s.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{aw + 6:.1f}" stroke-linecap="round"/><path d="{d}" fill="none" stroke="{SKIN}" stroke-width="{aw:.1f}" stroke-linecap="round"/>')
        # 手肘骨点
        s.append(f'<path d="M{ax + sgn * u * 0.2 + sgn * aw / 2:.1f} {sh_y + u * 1.9:.1f} q{sgn * 4} 6 0 12" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    s.append(f'<ellipse cx="{cx:.1f}" cy="{hy + u * 1.0:.1f}" rx="{u * 0.62:.1f}" ry="{u * 0.75:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M{cx - u * 0.85:.1f} {hy + u * 1.0:.1f} Q{cx - u * 0.8:.1f} {hy - u * 0.05:.1f} {cx:.1f} {hy:.1f} Q{cx + u * 0.8:.1f} {hy - u * 0.05:.1f} {cx + u * 0.85:.1f} {hy + u * 1.0:.1f} Q{cx + u * 0.3:.1f} {hy + u * 0.45:.1f} {cx - u * 0.1:.1f} {hy + u * 0.6:.1f} Q{cx - u * 0.45:.1f} {hy + u * 0.45:.1f} {cx - u * 0.85:.1f} {hy + u * 1.0:.1f} Z" fill="{PINK}" stroke="{INK}" stroke-width="3"/>')
    for dx in (-0.25, 0.25):
        s.append(f'<circle cx="{cx + dx * u:.1f}" cy="{hy + u * 1.1:.1f}" r="{u * 0.07:.1f}" fill="{INK}"/>')
    if grid:
        gs = u * 0.7
        gx = x
        while gx <= x + w:
            s.append(f'<line x1="{gx:.1f}" y1="{y}" x2="{gx:.1f}" y2="{y + h}" stroke="{UIBLUE}" stroke-width="1.2" stroke-opacity=".7"/>'); gx += gs
        gy = y
        while gy <= y + h:
            s.append(f'<line x1="{x}" y1="{gy:.1f}" x2="{x + w}" y2="{gy:.1f}" stroke="{UIBLUE}" stroke-width="1.2" stroke-opacity=".7"/>'); gy += gs
    geo = dict(cx=cx, u=u, sh_y=sh_y, arm_x=cx - u * 1.42, lx=lx)
    return clip(''.join(s), x, y, w, h), geo


LIQ_MODES = ['推', '顺时针转动', '逆时针转动', '捏合', '展开', '水晶', '边缘', '重建']


def u_liq_modes():
    ph, g = halfbody(CX, CY, CW, CH)
    bar = tool_sliders([('尺寸', 0.6), ('压力', 0.2), ('失真', 0.0), ('动力', 0.0)], mode='推', buttons=('调整', '重置'))
    n = 4 * (92 + 24) + 90 + 2 * 70 + 24
    bx = SX + SW / 2 - n / 2 + 12
    py = SY + SH - 74 - len(LIQ_MODES) * 30 - 18
    pop = panel(bx, py, 150, len(LIQ_MODES) * 30 + 12)
    for k, m in enumerate(LIQ_MODES):
        yy = py + 6 + k * 30
        pop += text(bx + 16, yy + 21, m, 14, 700, UITEXT)
        if m == '推':
            pop += ringrect(bx + 4, yy + 1, 142, 28)
    s = screen(ph + bar + pop, active='adjust') + ring(*icon_pos('adjust'), 18)
    s += badge(bx - 16, SY + SH - 74 + 31, 1) + badge(bx + 166, py + 21, 2)
    s += side_note(CX + CW + 12, 140, ['① 点底部最左边的模式按钮', '② 在列表里选模式', '修人像大多数时候用「推」'], YEL1, 13, 30)
    save('u-liq-modes', svg(W, H, s, '液化：点最左边的按钮选模式'))


def u_liq_sliders():
    ph, g = halfbody(CX, CY, CW, CH)
    s = screen(ph + tool_sliders([('尺寸', 0.6), ('压力', 0.2), ('失真', 0.0), ('动力', 0.0)], mode='推', buttons=('调整', '重置')), active='adjust')
    n = 4 * (92 + 24) + 90 + 2 * 70 + 24
    x0 = SX + SW / 2 - n / 2 + 12 + 90 + 140
    for k, (nm, tip) in enumerate([('尺寸', '比要推的部位宽'), ('压力', '10%～30%'), ('失真', '0%'), ('动力', '0%')]):
        sx_ = x0 + k * 116 + 12
        s += badge(sx_ + 46, SY + SH - 88, k + 1)
    s += side_note(64, 130, ['① 尺寸：比要推的部位宽', '② 压力：10%～30%', '③ 失真：0%', '④ 动力：0%'], YEL1, 13, 30)
    s += side_note(CX + CW + 12, 130, ['用手指推时，没有压感，', '效果总是按「压力」', '设的最大值来'], WHITE, 13, 30)
    save('u-liq-sliders', svg(W, H, s, '液化底部的四个滑块：修人像的起步设置'))


def u_liq_adjust():
    ph, g = halfbody(CX, CY, CW, CH, arm=0.8)
    bar = tool_sliders([('尺寸', 0.6), ('压力', 0.2), ('失真', 0.0), ('动力', 0.0)], mode='推', buttons=('调整', '重置'), hl='调整')
    ax, ay, aw, ah = POS['调整']
    pop = panel(ax - 60, ay - 84, 220, 66) + slider(ax - 44, ay - 40, 188, '强度', 0.6, True)
    s = screen(ph + bar + pop, active='adjust') + ring(*icon_pos('adjust'), 18)
    s += badge(ax + 31, ay + 52, 1) + badge(ax + 174, ay - 52, 2)
    s += side_note(CX + CW + 12, 130, ['① 推完一笔，点「调整」', '② 往左拖「强度」：', '　 刚才的效果整体减弱'], YEL1, 13, 30)
    s += side_note(CX + CW + 12, 240, ['「重置」：撤掉这次液化的全部变形，', '留在液化界面里'], WHITE, 12, 28)
    save('u-liq-adjust', svg(W, H, s, '液化的调整按钮：强度滑块'))


def u_liq_push():
    ph, g = halfbody(CX, CY, CW, CH, arm=1.45, grid=True)
    ax = g['arm_x'] - g['u'] * 0.35
    ay = g['sh_y'] + g['u'] * 1.2
    r = g['u'] * 0.75
    body = ph + f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="{r:.1f}" fill="none" stroke="{WHITE}" stroke-width="3" stroke-dasharray="6 4"/>' + arrow(ax - r * 0.6, ay, ax + r * 0.4, ay, VIO7, 3.5, marker='arwv')
    s = screen(body + tool_sliders([('尺寸', 0.6), ('压力', 0.2), ('失真', 0.0), ('动力', 0.0)], mode='推', buttons=('调整', '重置')), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += badge(ax - r - 16, ay - r, 1)
    s += side_note(64, 130, ['① 笔刷中心放在', '　 手臂轮廓外面一点点', '② 往手臂里面推一小段，', '　 抬笔，看一眼再推'], YEL1, 13, 30)
    s += side_note(CX + CW + 12, 130, ['蓝色网格：绘图指引的 2D 网格', '推完看门框还和网格平行吗'], WHITE, 13, 30)
    s += badge(g['lx'] + 18, CY + 40, 2)
    save('u-liq-push', svg(W, H, s, '推模式收手臂，打开 2D 网格检查背景直线'))


def warp_panel(fn, title, fill, sub, sub2='', Wd=360, Hd=350, brush=True, extra=''):
    ox, oy, gw = 30, 54, 300
    s = [panel_box(10, 10, Wd - 20, Hd - 20, title, WHITE, fill)]
    s.append(f'<rect x="{ox}" y="{oy}" width="{gw}" height="{gw * 0.7:.0f}" rx="6" fill="{VIO1}"/>')
    gh = gw * 0.7
    N = 14
    for k in range(N + 1):
        for vertical in (True, False):
            pts = []
            for j in range(61):
                if vertical:
                    u_, v_ = k / N, j / 60
                else:
                    u_, v_ = j / 60, k / N
                a, b = fn(u_, v_ * 0.7)
                pts.append((ox + a * gw, oy + b * gw))
            s.append('<polyline points="' + ' '.join(f'{p[0]:.1f},{p[1]:.1f}' for p in pts) + f'" fill="none" stroke="{VIO7}" stroke-width="1.6"/>')
    if brush:
        s.append(f'<circle cx="{ox + gw * 0.5}" cy="{oy + gh * 0.5:.1f}" r="{gw * 0.2:.1f}" fill="none" stroke="{PINK}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    s.append(extra)
    s.append(text(30, oy + gh + 34, sub, 14, 700))
    if sub2:
        s.append(text(30, oy + gh + 58, sub2, 13, 400, MUTED))
    return svg(Wd, Hd, ''.join(s), title)


def fall(u_, v_, cx=0.5, cy=0.35, r=0.2):
    d2 = ((u_ - cx) ** 2 + (v_ - cy) ** 2) / r ** 2
    return math.exp(-d2), u_ - cx, v_ - cy


def p_liq_all():
    def push(u_, v_):
        f, dx, dy = fall(u_, v_)
        return u_ + 0.16 * f, v_
    ex = arrow(30 + 300 * 0.36, 54 + 105, 30 + 300 * 0.66, 54 + 105, PINK, 3, marker='arwr')
    save('p-liq-push', warp_panel(push, '推：顺着笔的方向推走像素', YEL1, '修图用得最多：收手臂、腰线，补假发轮廓', '笔画方向就是像素移动的方向', extra=ex))

    def twirl(u_, v_):
        f, dx, dy = fall(u_, v_, r=0.22)
        a = 1.6 * f
        return 0.5 + dx * math.cos(a) - dy * math.sin(a), 0.35 + dx * math.sin(a) + dy * math.cos(a)
    save('p-liq-twirl', warp_panel(twirl, '转动：绕着笔尖旋转', VIO1, '修图里很少用；做发梢卷曲、漩涡特效', '分顺时针、逆时针两个方向'))

    def pinch(u_, v_):
        f, dx, dy = fall(u_, v_, r=0.24)
        k = 1 - 0.45 * f
        return 0.5 + dx * k, 0.35 + dy * k
    save('p-liq-pinch', warp_panel(pinch, '捏合：往笔尖中心吸', MINT1, '局部缩小：鼻头、太大的饰品', '中心缩小，边缘被拉开'))

    def expand(u_, v_):
        f, dx, dy = fall(u_, v_, r=0.16)
        k = 1 + 0.55 * f
        return 0.5 + dx * k, 0.35 + dy * k
    save('p-liq-expand', warp_panel(expand, '展开：从笔尖往外鼓', PINK1, '局部放大，像吹气球：轻轻放大眼睛', '压力要很低，否则像鱼眼'))

    rnd = random.Random(9)
    spikes = [rnd.random() for _ in range(24)]

    def crystal(u_, v_):
        f, dx, dy = fall(u_, v_, r=0.2)
        ang = math.atan2(dy, dx)
        idx = int(((ang + math.pi) / (2 * math.pi)) * 24) % 24
        k = 1 + 0.6 * f * spikes[idx]
        return 0.5 + dx * k, 0.35 + dy * k
    save('p-liq-crystal', warp_panel(crystal, '水晶：不均匀地往外推，像碎片', YEL1, '修人像用不上；做冰晶、碎裂特效', '每个方向推出去的距离不一样'))

    def edge(u_, v_):
        fy = math.exp(-((v_ - 0.35) / 0.2) ** 2)
        fx = math.exp(-((u_ - 0.5) / 0.18) ** 2)
        return u_ - (u_ - 0.5) * 0.65 * fx * fy, v_
    ex2 = f'<line x1="{30 + 150}" y1="{54 + 40}" x2="{30 + 150}" y2="{54 + 170}" stroke="{PINK}" stroke-width="2.5" stroke-dasharray="6 4"/>'
    save('p-liq-edge', warp_panel(edge, '边缘：往一条线上吸，像对折', VIO1, '往笔画经过的那条线收，不是往一个点', '修图里偶尔用来收紧一道布料边', brush=False, extra=ex2))

    def rebuild(u_, v_):
        f, dx, dy = fall(u_, v_, cx=0.5, cy=0.35, r=0.22)
        w_ = 1.0 if u_ < 0.5 else 0.25
        return u_ + 0.15 * f * w_, v_
    ex3 = (f'<rect x="{30 + 150}" y="54" width="150" height="210" fill="{MINT}" fill-opacity=".15"/>'
           + label(30 + 160, 54 + 200, '刷过「重建」', MINT1, 12))
    save('p-liq-rebuild', warp_panel(rebuild, '重建：刷到哪里，哪里慢慢变回原样', MINT1, '只修推过头的那一块，别处的效果不动', '只在还没退出液化时有效', brush=False, extra=ex3))


def p_liq_sliders():
    Wd, Hd = 760, 330
    s = []
    items = [('尺寸', '影响的范围'), ('压力', '一笔推动多少'), ('失真', '加入乱七八糟的扭曲'), ('动力', '抬笔后还继续变形')]
    for col, (t, sub) in enumerate(items):
        ox = 10 + col * 187
        s.append(panel_box(ox, 10, 180, 310, t, WHITE, [YEL1, VIO1, PINK1, MINT1][col]))
        s.append(text(ox + 90, 70, sub, 13, 700, INK, 'middle'))
        # 两条轮廓：上 = 值小，下 = 值大
        for row, lab in enumerate(['小', '大']):
            y0 = 120 + row * 110
            s.append(text(ox + 14, y0 - 22, lab, 13, 800, MUTED))
            if col == 0:
                r = 14 if row == 0 else 40
                d = f'M{ox + 14} {y0} L{ox + 90 - r} {y0} Q{ox + 90} {y0 + (8 if row == 0 else 18)} {ox + 90 + r} {y0} L{ox + 166} {y0}'
                s.append(f'<circle cx="{ox + 90}" cy="{y0}" r="{r}" fill="none" stroke="{PINK}" stroke-width="2" stroke-dasharray="4 3"/>')
            elif col == 1:
                dd = 6 if row == 0 else 26
                d = f'M{ox + 14} {y0} C{ox + 60} {y0} {ox + 70} {y0 + dd} {ox + 90} {y0 + dd} S{ox + 120} {y0} {ox + 166} {y0}'
            elif col == 2:
                if row == 0:
                    d = f'M{ox + 14} {y0} C{ox + 60} {y0} {ox + 70} {y0 + 14} {ox + 90} {y0 + 14} S{ox + 120} {y0} {ox + 166} {y0}'
                else:
                    d = f'M{ox + 14} {y0} L{ox + 50} {y0 + 2} L{ox + 60} {y0 + 16} L{ox + 70} {y0 + 4} L{ox + 82} {y0 + 22} L{ox + 94} {y0 + 6} L{ox + 106} {y0 + 20} L{ox + 120} {y0 + 3} L{ox + 166} {y0}'
            else:
                if row == 0:
                    d = f'M{ox + 14} {y0} C{ox + 50} {y0} {ox + 60} {y0 + 14} {ox + 75} {y0 + 14} S{ox + 95} {y0} {ox + 166} {y0}'
                    s.append(f'<circle cx="{ox + 75}" cy="{y0 + 30}" r="4" fill="{INK}"/>' + text(ox + 82, y0 + 34, '抬笔', 11, 700))
                else:
                    d = f'M{ox + 14} {y0} C{ox + 50} {y0} {ox + 60} {y0 + 14} {ox + 75} {y0 + 14} C{ox + 100} {y0 + 14} {ox + 120} {y0 + 24} {ox + 140} {y0 + 24} S{ox + 160} {y0} {ox + 170} {y0}'
                    s.append(f'<circle cx="{ox + 75}" cy="{y0 + 34}" r="4" fill="{INK}"/>' + text(ox + 82, y0 + 38, '抬笔后还在动', 11, 700, RED7))
            s.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="3"/>')
        s.append(text(ox + 90, 304, ['修人像：比部位宽', '修人像：10%～30%', '修人像：0%', '修人像：0%'][col], 13, 700, VIO7, 'middle'))
    save('p-liq-sliders', svg(Wd, Hd, ''.join(s), '液化四个滑块各管什么'))


def p_liq_rules():
    Wd, Hd = 760, 300
    s = []
    for col, (t, f, good) in enumerate([('小笔刷、高压力', RED1, False), ('大笔刷、低压力、少量多次', MINT1, True)]):
        ox = 20 + col * 380
        s.append(panel_box(ox, 10, 360, 280, t, WHITE, f))
        y0 = 90
        # 原轮廓（虚线）和推完的轮廓
        s.append(f'<path d="M{ox + 30} {y0} C{ox + 120} {y0 + 10} {ox + 240} {y0 + 10} {ox + 330} {y0}" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="5 4"/>')
        if good:
            d = f'M{ox + 30} {y0} C{ox + 110} {y0 + 30} {ox + 250} {y0 + 30} {ox + 330} {y0}'
            for k in range(4):
                s.append(f'<circle cx="{ox + 110 + k * 45}" cy="{y0 + 20}" r="48" fill="none" stroke="{PINK}" stroke-width="1.5" stroke-dasharray="4 3" stroke-opacity=".7"/>')
        else:
            d = (f'M{ox + 30} {y0} L{ox + 90} {y0 + 4} Q{ox + 105} {y0 + 30} {ox + 120} {y0 + 6} Q{ox + 140} {y0 + 32} {ox + 160} {y0 + 6} '
                 f'Q{ox + 185} {y0 + 36} {ox + 205} {y0 + 8} Q{ox + 225} {y0 + 30} {ox + 245} {y0 + 6} L{ox + 330} {y0}')
            for k in range(4):
                s.append(f'<circle cx="{ox + 105 + k * 45}" cy="{y0 + 16}" r="12" fill="none" stroke="{PINK}" stroke-width="1.5" stroke-dasharray="3 3"/>')
        s.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="3.5"/>')
        s.append(f'<path d="{d} L{ox + 330} {y0 + 90} L{ox + 30} {y0 + 90} Z" fill="{SKIN}" fill-opacity=".6"/>')
        lines = (['一下一个坑，轮廓坑坑洼洼', '推多了还会把皮肤纹理扯花'] if not good else
                 ['每笔只动一点，几笔叠起来', '轮廓是一条顺滑的弧线'])
        s.append(text(ox + 30, 236, lines[0], 14, 700) + text(ox + 30, 262, lines[1], 13, 400, MUTED))
    save('p-liq-rules', svg(Wd, Hd, ''.join(s), '液化三原则：大笔刷、低压力、少量多次'))


def case_arm(after):
    cap = '修之后：手臂收细，门框还是直的' if after else '修之前：手臂贴着身体，被压扁显粗'
    ph, g = halfbody(20, 20, 600, 480, arm=(1.0 if after else 1.9))
    s = [ph, f'<rect x="20" y="20" width="600" height="480" fill="none" stroke="{INK}" stroke-width="2"/>']
    s.append(label(606, 56, cap, VIO1, 16, 'end') if after else label(34, 56, cap, YEL1, 16))
    return svg(640, 520, ''.join(s), cap)


def wig_head(x, y, w, h, dent):
    cx, cy = x + w / 2, y + h * 0.56
    r = w * 0.22
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#E0F2FE"/>']
    s.append(f'<path d="M{x + w * 0.1} {y + h} Q{cx} {cy + r * 1.5} {x + w * 0.9} {y + h} Z" fill="{VIO2}" stroke="{INK}" stroke-width="3"/>')
    # 假发外轮廓：顶部 dent>0 时塌下去一块
    top = cy - r * 1.55
    d = (f'M{cx - r * 1.55:.1f} {cy + r * 1.3:.1f} Q{cx - r * 1.75:.1f} {cy - r * 0.4:.1f} {cx - r * 1.2:.1f} {top + r * 0.35:.1f} '
         f'Q{cx - r * 0.6:.1f} {top - r * 0.05:.1f} {cx - r * 0.35:.1f} {top + dent * r:.1f} '
         f'Q{cx:.1f} {top + dent * r * 1.25:.1f} {cx + r * 0.35:.1f} {top + dent * r:.1f} '
         f'Q{cx + r * 0.6:.1f} {top - r * 0.05:.1f} {cx + r * 1.2:.1f} {top + r * 0.35:.1f} '
         f'Q{cx + r * 1.75:.1f} {cy - r * 0.4:.1f} {cx + r * 1.55:.1f} {cy + r * 1.3:.1f} Z')
    s.append(f'<path d="{d}" fill="{PINK}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<ellipse cx="{cx:.1f}" cy="{cy + r * 0.2:.1f}" rx="{r * 0.85:.1f}" ry="{r * 1.05:.1f}" fill="{SKIN}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M{cx - r * 1.1:.1f} {cy:.1f} Q{cx - r * 1.0:.1f} {top + r * 0.5 + dent * r * 0.6:.1f} {cx:.1f} {top + r * 0.55 + dent * r * 0.6:.1f} Q{cx + r * 1.0:.1f} {top + r * 0.5 + dent * r * 0.6:.1f} {cx + r * 1.1:.1f} {cy:.1f} Q{cx + r * 0.4:.1f} {cy - r * 0.7:.1f} {cx:.1f} {cy - r * 0.45:.1f} Q{cx - r * 0.4:.1f} {cy - r * 0.7:.1f} {cx - r * 1.1:.1f} {cy:.1f} Z" fill="{PINK}" stroke="{INK}" stroke-width="3"/>')
    for dx in (-0.35, 0.35):
        s.append(f'<circle cx="{cx + dx * r:.1f}" cy="{cy + r * 0.3:.1f}" r="{r * 0.09:.1f}" fill="{INK}"/>')
    return clip(''.join(s), x, y, w, h)


def case_wig(after):
    cap = '修之后：头顶补圆，脸没有动' if after else '修之前：假发头顶被压塌一块'
    s = [wig_head(20, 20, 600, 480, 0.0 if after else 0.45), f'<rect x="20" y="20" width="600" height="480" fill="none" stroke="{INK}" stroke-width="2"/>']
    s.append(label(606, 56, cap, VIO1, 16, 'end') if after else label(34, 56, cap, YEL1, 16))
    return svg(640, 520, ''.join(s), cap)


def run_m203():
    for f in [u_liq_modes, u_liq_sliders, u_liq_adjust, u_liq_push, p_liq_all, p_liq_sliders, p_liq_rules]:
        f()
    save('case-arm-before', case_arm(False)); save('case-arm-after', case_arm(True))
    save('case-wig-before', case_wig(False)); save('case-wig-after', case_wig(True))



# ======================= 2.4 模糊、锐化、杂色 =======================
def outdoor(x, y, w, h, bg_blur=0, fg_blur=0, mid_blur=0, person=True, weapon=False):
    sk = uid('sky')
    s = [f'<defs><linearGradient id="{sk}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#BFDBFE"/><stop offset="1" stop-color="#FEF3C7"/></linearGradient></defs>',
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{sk})"/>']
    hz = y + h * 0.55
    far = []
    for k, (bx, bw, bh, c) in enumerate([(0.0, 0.18, 0.28, '#94A3B8'), (0.16, 0.14, 0.38, '#A5B4FC'), (0.32, 0.2, 0.22, '#CBD5E1'), (0.62, 0.16, 0.34, '#94A3B8'), (0.8, 0.22, 0.26, '#C4B5FD')]):
        far.append(f'<rect x="{x + w * bx:.1f}" y="{hz - h * bh:.1f}" width="{w * bw:.1f}" height="{h * bh:.1f}" fill="{c}" stroke="{INK}" stroke-width="2"/>')
        for wy in range(3):
            for wx in range(2):
                far.append(f'<rect x="{x + w * (bx + 0.03 + wx * 0.06):.1f}" y="{hz - h * bh + h * (0.04 + wy * 0.07):.1f}" width="{w * 0.03:.1f}" height="{h * 0.035:.1f}" fill="#F8FAFC"/>')
    for tx in (0.1, 0.45, 0.9):
        far.append(f'<line x1="{x + w * tx:.1f}" y1="{hz:.1f}" x2="{x + w * tx:.1f}" y2="{hz - h * 0.12:.1f}" stroke="#78350F" stroke-width="4"/><circle cx="{x + w * tx:.1f}" cy="{hz - h * 0.16:.1f}" r="{w * 0.06:.1f}" fill="#86EFAC" stroke="{INK}" stroke-width="2"/>')
    far_s = ''.join(far)
    s.append(blurred(far_s, bg_blur) if bg_blur else far_s)
    ground = f'<rect x="{x}" y="{hz:.1f}" width="{w}" height="{y + h - hz:.1f}" fill="#E7E5E4"/><path d="M{x + w * 0.42} {hz:.1f} L{x + w * 0.58} {hz:.1f} L{x + w * 0.85} {y + h} L{x + w * 0.15} {y + h} Z" fill="#D6D3D1"/>'
    mid = ground + ''.join(f'<line x1="{x + w * lx:.1f}" y1="{hz - h * 0.05:.1f}" x2="{x + w * lx:.1f}" y2="{hz + h * 0.06:.1f}" stroke="{INK}" stroke-width="3"/><circle cx="{x + w * lx:.1f}" cy="{hz - h * 0.06:.1f}" r="5" fill="{YEL}" stroke="{INK}" stroke-width="2"/>' for lx in (0.3, 0.72))
    s.append(blurred(mid, mid_blur) if mid_blur else mid)
    g = {}
    if person:
        hh = h * 0.1
        top = y + h * 0.18
        feet = y + h * 0.86
        s.append(figure(x + w * 0.5, top, hh, top + hh * 3.6, feet, sw=max(2, hh / 20), weapon=weapon, arm_raise=weapon, hand_side=1))
        g = dict(top=top, hh=hh, cx=x + w * 0.5, feet=feet)
    fg = (f'<ellipse cx="{x + w * 0.06:.1f}" cy="{y + h * 0.98:.1f}" rx="{w * 0.2:.1f}" ry="{h * 0.16:.1f}" fill="#4ADE80" stroke="{INK}" stroke-width="3"/>'
          + ''.join(f'<circle cx="{x + w * (0.02 + k * 0.05):.1f}" cy="{y + h * (0.88 + (k % 2) * 0.04):.1f}" r="{w * 0.018:.1f}" fill="{PINK}" stroke="{INK}" stroke-width="1.5"/>' for k in range(5)))
    s.append(blurred(fg, fg_blur) if fg_blur else fg)
    return clip(''.join(s), x, y, w, h), g


def u_gauss():
    ph, g = outdoor(CX, CY, CW, CH, bg_blur=4, mid_blur=4, fg_blur=4)
    pill, (px, py, pw, phh) = info_pill('高斯模糊', '20%', dropdown=True)
    fx, fy = CX + 80, CY + 270
    s = screen(ph + pill + fingertip(fx, fy) + arrow(fx + 16, fy, fx + 120, fy, INK, 3), active='adjust') + ring(*icon_pos('adjust'), 18)
    lay, pos = layers2([L('背景虚化', 'blur', sel=True), L('原图', 'scene', lock=True)], x=560, y=200, w=210)
    s += lay
    s += badge(fx - 24, fy - 22, 1) + badge(px + pw + 18, py + 15, 2)
    s += side_note(64, 130, ['① 一指在画布上', '　 往右拖：越拖越糊', '② 顶部显示模糊程度'], YEL1, 13, 30)
    s += side_note(560, 360, ['整层都糊了，人也糊了：', '下一步用蒙版把人露出来'], WHITE, 13, 30)
    s += note('示意图')
    save('u-gauss', svg(W, H, s, '高斯模糊：在画布上左右拖动调程度'))


def u_dof_mask():
    sharp, g = outdoor(LX + 10, CY, 300, CH)
    blur_, _ = outdoor(LX + 10, CY, 300, CH, bg_blur=4, mid_blur=4, fg_blur=4)
    cid = uid('dm')
    # 人物区域露出清楚的原图
    reveal = (f'<defs><clipPath id="{cid}"><ellipse cx="{g["cx"]:.1f}" cy="{(g["top"] + g["feet"]) / 2:.1f}" rx="{g["hh"] * 1.4:.1f}" ry="{(g["feet"] - g["top"]) / 2 + 8:.1f}"/></clipPath></defs>'
              f'<g clip-path="url(#{cid})">{sharp}</g>')
    body = blur_ + reveal + pencil(g['cx'] + g['hh'] * 1.2, g['top'] + g['hh'] * 3, -30)
    lay, pos = layers2([L('图层蒙版', 'mask', sel=True, indent=1, hl=True), L('背景虚化', 'blur'), L('原图', 'scene', lock=True)], x=440, y=62)
    s = screen(body + lay, active='brush') + ring(*icon_pos('brush'), 18)
    s += badge(440 - 16, 62 + 44 + 19, 1) + badge(g['cx'] + g['hh'] * 1.6, g['top'] + g['hh'] * 2.2, 2)
    s += side_note(440, 250, ['① 在「背景虚化」上加蒙版，', '　 点蒙版那一行', '② 软画笔、黑色，涂人物：', '　 下面清楚的原图露出来', '人脚下的地面用 30%～50%', '不透明度的黑色轻涂，', '让清楚到模糊有个过渡'], YEL1, 13, 30)
    s += note('示意图')
    save('u-dof-mask', svg(W, H, s, '在模糊层的蒙版上用黑色涂出人物'))


def u_motion():
    ph, g = outdoor(CX, CY, CW, CH, person=True, weapon=True)
    pill, (px, py, pw, phh) = info_pill('动态模糊', '15%', dropdown=True)
    fx, fy = CX + 60, CY + 300
    s = screen(ph + pill + fingertip(fx, fy) + arrow(fx + 14, fy - 6, fx + 130, fy - 40, INK, 3), active='adjust') + ring(*icon_pos('adjust'), 18)
    lay, pos = layers2([L('人物', 'figure'), L('拖影', 'figure', sel=True), L('原图', 'scene', lock=True)], x=560, y=200, w=210)
    s += lay
    s += badge(fx - 24, fy - 22, 1)
    s += side_note(64, 130, ['① 一指顺着动作的方向拖：', '　 往哪个方向拖，', '　 就往哪个方向拉出线条'], YEL1, 13, 30)
    s += side_note(560, 390, ['只在「拖影」层上做，', '上面的「人物」保持清楚'], WHITE, 13, 30)
    s += note('示意图')
    save('u-motion', svg(W, H, s, '动态模糊：顺着动作方向拖动'))


def u_persp():
    ph, g = outdoor(CX, CY, CW, CH)
    blur_ = outdoor(CX, CY, CW, CH)[0]
    dx, dy = g['cx'], g['top'] + g['hh'] * 2
    rays = ''.join(f'<line x1="{dx + math.cos(a) * 40:.1f}" y1="{dy + math.sin(a) * 40:.1f}" x2="{dx + math.cos(a) * 170:.1f}" y2="{dy + math.sin(a) * 170:.1f}" stroke="{WHITE}" stroke-width="2" stroke-opacity=".7"/>' for a in [k * math.pi / 9 for k in range(18)])
    pill, (px, py, pw, phh) = info_pill('透视模糊', '12%', dropdown=True)
    bp, pos, y0 = bottom_panel(SY + SH - 12, 260, buttons=['位置', '方向'], active_btn='位置', hl='位置')
    s = screen(clip(blur_ + rays, CX, CY, CW, CH) + disc(dx, dy, 16) + pill + bp, active='adjust') + ring(*icon_pos('adjust'), 18)
    s += badge(dx + 30, dy - 20, 1) + badge(pos['位置'][0] - 60, pos['位置'][1], 2)
    s += side_note(64, 130, ['① 把圆盘拖到放射中心', '② 位置：往四周放射', '　 方向：只往一边放射', '在圆盘外面左右拖，', '调模糊程度'], YEL1, 13, 30)
    s += note('示意图')
    save('u-persp', svg(W, H, s, '透视模糊：圆盘是放射中心，位置和方向两种模式'))


def u_copyall():
    ph, g = outdoor(CX, CY, CW, CH)
    bar_items = ['剪切', '拷贝', '全部拷贝', '复制', '剪切并粘贴', '粘贴']
    bx, by = 160, 64
    sb = f'<rect x="{bx}" y="{by}" width="480" height="46" rx="12" fill="{UIBAR}"/>'
    xx = bx + 10
    hx = {}
    for it in bar_items:
        w_ = len(it) * 15 + 20
        sb += f'<rect x="{xx}" y="{by + 7}" width="{w_}" height="32" rx="8" fill="{UIPANEL}"/>' + text(xx + w_ / 2, by + 29, it, 14, 700, UITEXT, 'middle')
        if it in ('全部拷贝', '粘贴'):
            sb += ringrect(xx - 3, by + 4, w_ + 6, 38)
        hx[it] = xx + w_ / 2
        xx += w_ + 6
    fx = CX + CW + 70
    s = screen(ph + sb + finger(fx, 230, 3, 40))
    s += badge(hx['全部拷贝'], by + 62, 1) + badge(hx['粘贴'], by + 62, 2)
    s += side_note(CX + CW + 14, 330, ['三指下拖打开菜单', '① 全部拷贝：所有看得见的', '　 图层合成一张，拷进剪贴板', '② 再下拖一次，点粘贴：', '　 变成最上面的一个新图层'], YEL1, 13, 30)
    s += note('示意图')
    save('u-copyall', svg(W, H, s, '全部拷贝再粘贴，得到一张合并后的副本'))


def u_sharpen():
    ph, g = face_photo(CX, CY, CW, CH)
    pill, (px, py, pw, phh) = info_pill('锐化', '20%', dropdown=True)
    ex, ey = g['cx'] - g['fw'] * 0.42, g['cy'] + g['fw'] * 0.05
    painted = f'<ellipse cx="{g["cx"]:.1f}" cy="{ey:.1f}" rx="{g["fw"] * 0.75:.1f}" ry="{g["fw"] * 0.3:.1f}" fill="none" stroke="{YEL}" stroke-width="2.5" stroke-dasharray="6 4"/>'
    s = screen(ph + painted + pencil(ex + g['fw'] * 0.95, ey + 6, 30) + pill + mode_dropdown(400, 102, 'Pencil', 'Pencil'), active='brush')
    s += brush_icon_star(*icon_pos('brush'))
    s += badge(400 + 100, 124, 1) + badge(g['cx'] - g['fw'] * 0.9, ey - 24, 2)
    s += side_note(64, 200, ['① 切到 Pencil', '② 只涂眼睛、发丝边、', '　 服装花纹、道具边缘', '皮肤和背景不涂'], YEL1, 13, 30)
    s += side_note(CX + CW + 12, 200, ['放大到 100% 检查：', '边缘出现白边、黑边', '就是锐化过头了'], WHITE, 13, 30)
    s += note('示意图')
    save('u-sharpen', svg(W, H, s, '锐化用 Pencil 模式只涂主体的细节'))


def u_noise():
    ph, g = outdoor(CX, CY, CW, CH, bg_blur=4, mid_blur=4, fg_blur=4)
    ph += noise_dots(CX, CY, CW, CH, 900, 5, .3, .9)
    pill, (px, py, pw, phh) = info_pill('杂色', '8%', dropdown=True)
    bar_y = SY + SH - 12
    bp, pos, y0 = bottom_panel(bar_y, 640, [('比例', .1), ('倍频', .3), ('湍流', .2)], buttons=['云', '巨浪', '背脊'], active_btn='巨浪')
    # 通道图标和弹出菜单
    chx, chy = SX + SW / 2 + 290, y0 + 30
    ch = f'<circle cx="{chx}" cy="{chy}" r="15" fill="{UIPANEL}" stroke="{UITEXT}" stroke-width="2"/>' + text(chx, chy + 5, 'RGB', 9, 800, UITEXT, 'middle')
    pop = panel(chx - 160, chy - 128, 170, 108)
    for k, (r, on) in enumerate([('单一', True), ('多个', False), ('叠加', True)]):
        yy = chy - 120 + k * 34
        pop += text(chx - 146, yy + 22, r, 14, 700, UITEXT)
        if r == '叠加':
            pop += f'<rect x="{chx - 58}" y="{yy + 8}" width="40" height="20" rx="10" fill="{UIBLUE}"/><circle cx="{chx - 28}" cy="{yy + 18}" r="8" fill="{WHITE}"/>'
        elif on:
            pop += text(chx - 30, yy + 22, '✓', 16, 800, UIBLUE, 'middle')
    s = screen(ph + pill + bp + ch + pop, active='adjust') + ring(*icon_pos('adjust'), 18)
    s += ring(chx, chy, 19) + badge(chx + 30, chy - 2, 1)
    s += badge(pos['云'][0] - 60, pos['云'][1], 2)
    s += side_note(64, 120, ['① 通道：选「单一」（黑白颗粒），', '　 打开「叠加」', '② 模式：云最粗，背脊最细', '比例往左：颗粒更小', '在画布上左右拖：颗粒多少'], YEL1, 13, 30)
    save('u-noise', svg(W, H, s, '杂色界面：模式、比例、倍频、湍流和通道'))


def u_grain_layer():
    ph, g = outdoor(LX + 10, CY, 300, CH, bg_blur=4, mid_blur=4, fg_blur=4)
    ph += noise_dots(LX + 10, CY, 300, CH, 1100, 6, .28, .9)
    lay, pos = layers2([L('颗粒', 'grain', mode='O', sel=True), L('人物', 'figure'), L('背景虚化', 'blur'), L('原图', 'scene', lock=True)], x=440, y=62)
    s = screen(ph + lay + blend_popup(440, 300, '覆盖', 0.5, 'mode'), active='layers')
    nx, ny = 440 + 300 - 44, 62 + 44 + 19
    s += ring(nx, ny, 15) + badge(nx - 36, ny - 30, 1) + badge(440 + 264, 300 - 4, 2)
    s += side_note(440, 420, ['灰色层 + 杂色 + 混合模式「覆盖」：', '50% 灰在「覆盖」下看不见，只剩颗粒', '不透明度控制颗粒的强弱'], YEL1, 13, 30)
    s += note('示意图')
    save('u-grain-layer', svg(W, H, s, '单独一层颗粒：50% 灰加杂色，混合模式设成覆盖'))


def p_dof():
    Wd, Hd = 760, 340
    s = [panel_box(20, 10, 720, 320, '景深：离对焦的位置越远，越模糊', WHITE, YEL1)]
    gy = 230
    s.append(f'<line x1="50" y1="{gy}" x2="720" y2="{gy}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(f'<rect x="56" y="{gy - 60}" width="40" height="28" rx="5" fill="{INK}"/><circle cx="100" cy="{gy - 46}" r="9" fill="{VIO2}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(76, gy + 26, '相机', 13, 700, INK, 'middle'))
    items = [(200, '前景花丛', 3.5, '#4ADE80'), (380, '人物（对焦）', 0, PINK), (560, '路灯', 3.5, YEL), (680, '远处楼房', 7, '#A5B4FC')]
    s.append(f'<line x1="380" y1="70" x2="380" y2="{gy}" stroke="{PINK}" stroke-width="2" stroke-dasharray="6 5"/>' + label(388, 86, '对焦平面', PINK1, 12))
    for x, n, b, c in items:
        shape = f'<circle cx="{x}" cy="{gy - 40}" r="22" fill="{c}" stroke="{INK}" stroke-width="2.5"/>'
        s.append(blurred(shape, b) if b else shape)
        s.append(text(x, gy + 26, n, 13, 700, INK, 'middle'))
        r = 4 + abs(x - 380) / 22
        s.append(f'<circle cx="{x}" cy="{gy - 110}" r="{r:.1f}" fill="none" stroke="{VIO7}" stroke-width="2"/>')
    s.append(text(720, gy - 150, '紫圈：一个光点在照片里被摊成多大', 12, 600, VIO7, 'end'))
    s.append(text(50, 290, '眼睛先看清楚、对比强的地方。背景糊掉以后，里面的路人、海报、灯架不再抢眼，人物自然跳出来。', 13, 700))
    s.append(text(50, 314, '后期模仿时也照这个规律：离人物越远的地方糊得越多，人物脚下的地面和人一样清楚。', 13, 400, MUTED))
    save('p-dof', svg(Wd, Hd, ''.join(s), '景深原理：离对焦平面越远越模糊'))


def p_motion():
    Wd, Hd = 760, 300
    s = [panel_box(20, 10, 720, 280, '动态模糊：快门打开的那一瞬间，东西在动', WHITE, YEL1)]
    for k in range(7):
        s.append(f'<circle cx="{140 + k * 40}" cy="140" r="34" fill="{PINK}" fill-opacity="{0.12 + k * 0.06:.2f}"/>')
    s.append(f'<circle cx="380" cy="140" r="34" fill="{PINK}" stroke="{INK}" stroke-width="3"/>')
    s.append(arrow(130, 200, 420, 200, INK, 3))
    s.append(text(140, 230, '快门开', 13, 700) + text(380, 230, '快门关', 13, 700, INK, 'middle'))
    s.append(text(470, 110, '每个位置都留下了一点颜色，', 14, 700))
    s.append(text(470, 136, '叠起来就是顺着运动方向的拖影。', 14, 700))
    s.append(text(470, 172, '后期做法：复制一层做动态模糊，', 13, 400, MUTED))
    s.append(text(470, 196, '往运动的反方向挪一点放在人物后面，', 13, 400, MUTED))
    s.append(text(470, 220, '人物本身保持清楚，读得出是谁。', 13, 400, MUTED))
    save('p-motion', svg(Wd, Hd, ''.join(s), '动态模糊原理：曝光期间物体移动留下拖影'))


def p_persp():
    Wd, Hd = 760, 300
    s = []
    for col, (t, f) in enumerate([('位置：从圆盘往四周放射', YEL1), ('方向：只往箭头一边放射', VIO1)]):
        ox = 20 + col * 380
        s.append(panel_box(ox, 10, 360, 280, t, WHITE, f))
        cx, cy = ox + 180, 150
        for k in range(24):
            a = k * math.pi / 12
            if col == 1 and not (-0.6 < math.atan2(math.sin(a), math.cos(a)) < 0.6):
                continue
            s.append(f'<line x1="{cx + math.cos(a) * 30:.1f}" y1="{cy + math.sin(a) * 30:.1f}" x2="{cx + math.cos(a) * 130:.1f}" y2="{cy + math.sin(a) * 80:.1f}" stroke="{VIO2 if col == 0 else PINK}" stroke-width="4" stroke-linecap="round"/>')
        s.append(disc(cx, cy, 14))
        if col == 1:
            s.append(arrow(cx + 18, cy, cx + 60, cy, INK, 3))
        s.append(text(ox + 24, 262, ['适合：放大招、冲向镜头的冲击感' , '适合：一束光从一边打进来'][col], 13, 700))
    save('p-persp', svg(Wd, Hd, ''.join(s), '透视模糊的两种模式'))


def p_sharpen():
    Wd, Hd = 760, 330
    s = []
    items = [('原图：边缘有一点软', 0), ('锐化适量：边缘更利落', 0.25), ('锐化过头：出现白边黑边', 0.8)]
    for col, (t, k) in enumerate(items):
        ox = 14 + col * 250
        s.append(panel_box(ox, 10, 236, 310, t, WHITE, [YEL1, MINT1, RED1][col]))
        x0, y0, w0, h0 = ox + 22, 60, 192, 90
        # 色块示意
        steps = 24
        for i in range(steps):
            t_ = i / (steps - 1)
            v = 1 / (1 + math.exp(-(t_ - 0.5) * 18))
            v += k * (-math.exp(-((t_ - 0.4) / 0.06) ** 2) + math.exp(-((t_ - 0.6) / 0.06) ** 2))
            c = int(max(0, min(1, 0.15 + 0.7 * v)) * 255)
            s.append(f'<rect x="{x0 + i * w0 / steps:.1f}" y="{y0}" width="{w0 / steps + 0.5:.1f}" height="{h0}" fill="rgb({c},{c},{c})"/>')
        s.append(f'<rect x="{x0}" y="{y0}" width="{w0}" height="{h0}" fill="none" stroke="{INK}" stroke-width="2"/>')
        # 亮度曲线
        pts = []
        for i in range(80):
            t_ = i / 79
            v = 1 / (1 + math.exp(-(t_ - 0.5) * 18)) + k * (-math.exp(-((t_ - 0.4) / 0.06) ** 2) + math.exp(-((t_ - 0.6) / 0.06) ** 2))
            pts.append((x0 + t_ * w0, 284 - v * 72))
        s.append(f'<line x1="{x0}" y1="284" x2="{x0 + w0}" y2="284" stroke="{LINE}" stroke-width="1.5"/>')
        s.append('<polyline points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts) + f'" fill="none" stroke="{VIO7}" stroke-width="3"/>')
        s.append(text(x0, 172, '下面是这一行的亮度', 12, 600, MUTED))
    save('p-sharpen', svg(Wd, Hd, ''.join(s), '锐化原理：加大边缘两侧的明暗差'))


def p_grain():
    Wd, Hd = 760, 300
    s = []
    items = [('照片原有的颗粒', 'grain'), ('模糊后：颗粒没了，像塑料', 'smooth'), ('加回颗粒：和清楚的地方一致', 'fixed')]
    for col, (t, k) in enumerate(items):
        ox = 14 + col * 250
        s.append(panel_box(ox, 10, 236, 280, t, WHITE, [YEL1, RED1, MINT1][col]))
        x0, y0 = ox + 22, 56
        base = f'<rect x="{x0}" y="{y0}" width="192" height="170" fill="#A5B4FC"/><circle cx="{x0 + 70}" cy="{y0 + 80}" r="40" fill="#C4B5FD"/><rect x="{x0 + 110}" y="{y0 + 30}" width="60" height="110" fill="#94A3B8"/>'
        if k == 'grain':
            s.append(base + noise_dots(x0, y0, 192, 170, 900, 11, .35, 1))
        elif k == 'smooth':
            s.append(clip(blurred(base, 6), x0, y0, 192, 170))
        else:
            s.append(clip(blurred(base, 6), x0, y0, 192, 170) + noise_dots(x0, y0, 192, 170, 900, 12, .35, 1))
        s.append(f'<rect x="{x0}" y="{y0}" width="192" height="170" fill="none" stroke="{INK}" stroke-width="2"/>')
        s.append(text(ox + 118, 260, ['手机、相机在暗处都会有', '模糊、补画、贴素材都会', '合成和虚化后都要补'][col], 13, 600, MUTED, 'middle'))
    save('p-grain', svg(Wd, Hd, ''.join(s), '为什么要统一颗粒'))


def case_dof(after):
    cap = '修之后：背景虚化，人物跳出来' if after else '修之前：前景、背景都一样清楚'
    b = 5 if after else 0
    ph, g = outdoor(20, 20, 600, 480, bg_blur=b * 1.4, mid_blur=b * 0.6, fg_blur=b)
    s = [ph, f'<rect x="20" y="20" width="600" height="480" fill="none" stroke="{INK}" stroke-width="2"/>']
    s.append(label(606, 56, cap, VIO1, 16, 'end') if after else label(34, 56, cap, YEL1, 16))
    return svg(640, 520, ''.join(s), cap)


def case_motion(after):
    cap = '修之后：剑和手臂后面有一道拖影' if after else '修之前：挥剑的瞬间，看着像摆拍'
    ph, g = outdoor(20, 20, 600, 480, bg_blur=3, mid_blur=2, fg_blur=3, person=False)
    hh = 48; top = 20 + 480 * 0.18
    fig = figure(320, top, hh, top + hh * 3.6, 20 + 480 * 0.86, sw=2.5, weapon=True, arm_raise=True, hand_side=1)
    s = [ph]
    if after:
        trail = ''.join(f'<g transform="translate({-k * 14},{k * 5})" opacity="{0.35 - k * 0.07:.2f}">{fig}</g>' for k in range(1, 5))
        s.append(clip(mblur(trail, 6), 20, 20, 600, 480))
    s.append(fig)
    s.append(f'<rect x="20" y="20" width="600" height="480" fill="none" stroke="{INK}" stroke-width="2"/>')
    s.append(label(606, 56, cap, VIO1, 16, 'end') if after else label(34, 56, cap, YEL1, 16))
    return svg(640, 520, ''.join(s), cap)


def run_m204():
    for f in [u_gauss, u_dof_mask, u_motion, u_persp, u_copyall, u_sharpen, u_noise, u_grain_layer, p_dof, p_motion, p_persp, p_sharpen, p_grain]:
        f()
    save('case-dof-before', case_dof(False)); save('case-dof-after', case_dof(True))
    save('case-motion-before', case_motion(False)); save('case-motion-after', case_motion(True))



# ======================= 2.5 抠图 =======================
def hair_person(cx, top, hh, sw=3, strands=True, rim=None):
    """带飞散发丝的人物（半身）。rim：轮廓外加一圈颜色（白边演示）"""
    fig = figure(cx, top, hh, top + hh * 3.6, top + hh * 7, sw=sw)
    st = ''
    if strands:
        rnd = random.Random(3)
        for sgn in (-1, 1):
            for k in range(5):
                by = top + hh * (0.35 + k * 0.28)
                bx = cx + sgn * hh * (0.6 + 0.06 * math.sin(k))
                ex = bx + sgn * hh * (0.18 + rnd.random() * 0.14)
                ey = by + hh * (0.25 + rnd.random() * 0.2)
                st += f'<path d="M{bx:.1f} {by:.1f} Q{ex:.1f} {by + hh * 0.02:.1f} {ex:.1f} {ey:.1f}" fill="none" stroke="{PINK}" stroke-width="1.6" stroke-linecap="round"/>'
        for k in range(3):
            bx = cx + (k - 1) * hh * 0.25
            st += f'<path d="M{bx:.1f} {top + hh * 0.02:.1f} q{(k - 1) * 6 + 3:.1f} -{hh * 0.12:.1f} {(k - 1) * 10 + 8:.1f} -{hh * 0.1:.1f}" fill="none" stroke="{PINK}" stroke-width="1.6" stroke-linecap="round"/>'
    out = ''
    if rim:
        fid = uid('rim')
        out = (f'<defs><filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%"><feMorphology operator="dilate" radius="3" in="SourceAlpha" result="d"/>'
               f'<feFlood flood-color="{rim}"/><feComposite in2="d" operator="in"/></filter></defs><g filter="url(#{fid})">{fig}{st}</g>')
    return out + fig + st


def studio(x, y, w, h, bg='#F1F5F9', rim=None, person=True, strands=True):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}"/>']
    hh = h * 0.2
    top = y + h * 0.1
    if person:
        s.append(hair_person(x + w * 0.5, top, hh, sw=max(2, hh / 22), strands=strands, rim=rim))
    return clip(''.join(s), x, y, w, h), dict(cx=x + w * 0.5, top=top, hh=hh)


def sel_overlay(x, y, w, h, color='#FDE68A', holes=()):
    """自动选取：被选中的区域以相对色显示（这里背景是浅灰，用黄色示意）"""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" fill-opacity=".55"/>'


def u_auto_sel():
    ph, g = studio(CX, CY, CW, CH)
    person = hair_person(g['cx'], g['top'], g['hh'], sw=2.5)
    body = ph + clip(sel_overlay(CX, CY, CW, CH) + person, CX, CY, CW, CH)
    pill, (px, py, pw, phh) = info_pill('选区阈值', '45%')
    fx, fy = CX + 40, CY + 60
    s = screen(body + pill + fingertip(fx, fy) + arrow(fx + 14, fy + 20, fx + 90, fy + 20, INK, 3) + bottom_bar(SEL_ROWS, active=('自动',)), active='select')
    s += ring(*icon_pos('select'), 18) + badge(icon_pos('select')[0] + 26, 62, 1)
    s += badge(fx - 24, fy - 18, 2) + badge(px + pw + 18, py + 15, 3)
    s += side_note(CX + CW + 12, 130, ['① 选取 › 自动', '② 点一下背景，手指别抬，', '　 左右拖调阈值', '③ 背景刚好选满、', '　 没漏进头发就停'], YEL1, 13, 30)
    s += side_note(64, 130, ['选中的部分', '会变成反差色'], WHITE, 13, 30)
    save('u-auto-sel', svg(W, H, s, '自动选取：点背景，按住左右拖动调选区阈值'))


def u_sel_fix():
    ph, g = studio(CX, CY, CW, CH)
    person = hair_person(g['cx'], g['top'], g['hh'], sw=2.5)
    # 胳膊和身体之间漏选的一块背景
    hx, hy = g['cx'] - g['hh'] * 0.72, g['top'] + g['hh'] * 2.9
    gap = f'<ellipse cx="{hx:.1f}" cy="{hy:.1f}" rx="7" ry="22" fill="#F1F5F9"/>'
    d = f'M{hx - 12:.1f} {hy - 28:.1f} L{hx + 10:.1f} {hy - 30:.1f} L{hx + 12:.1f} {hy + 28:.1f} L{hx - 10:.1f} {hy + 30:.1f} Z'
    body = ph + clip(sel_overlay(CX, CY, CW, CH) + person, CX, CY, CW, CH) + gap + ants_path(d)
    bar = bottom_bar(SEL_ROWS, active=('手绘',), hl='添加')
    s = screen(body + bar, active='select') + ring(*icon_pos('select'), 18)
    ax, ay, aw, ah = POS['添加']
    s += badge(POS['手绘'][0] + POS['手绘'][2] / 2, POS['手绘'][1] - 12, 1) + badge(hx + 30, hy, 2) + badge(ax + aw / 2, ay - 12, 3)
    s += side_note(CX + CW + 12, 130, ['① 换成「手绘」', '② 放大，把漏掉的那块', '　 背景圈出来', '③ 点「添加」：加进选区', '多选了就圈出来点「移除」'], YEL1, 13, 30)
    s += side_note(64, 130, ['手臂和身体之间', '那块背景没选上'], WHITE, 13, 30)
    save('u-sel-fix', svg(W, H, s, '换手绘模式，把漏选或多选的地方补上或去掉'))


def u_invert_copy():
    ph, g = studio(CX, CY, CW, CH)
    hatch = uid('h')
    body = ph + (f'<defs><pattern id="{hatch}" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="10" height="10" fill="#94A3B8" fill-opacity=".25"/>'
                 f'<line x1="0" y1="0" x2="0" y2="10" stroke="#64748B" stroke-width="3" stroke-opacity=".35"/></pattern></defs>')
    body += clip(f'<rect x="{CX}" y="{CY}" width="{CW}" height="{CH}" fill="url(#{hatch})"/>' + hair_person(g['cx'], g['top'], g['hh'], sw=2.5), CX, CY, CW, CH)
    bar = bottom_bar(SEL_ROWS, active=('自动', '反转'), hl='拷贝并粘贴')
    s = screen(body + bar, active='select') + ring(*icon_pos('select'), 18)
    rx, ry, rw, rh = POS['反转']
    cx_, cy_, cw_, ch_ = POS['拷贝并粘贴']
    s += ringrect(rx - 3, ry + 2, rw + 6, rh - 4) + badge(rx + rw / 2, ry - 12, 1) + badge(cx_ + cw_ / 2, cy_ - 12, 2)
    s += side_note(CX + CW + 12, 130, ['① 反转：选区从背景', '　 换成人物', '② 拷贝并粘贴：人物', '　 复制到新图层「从选区」', '　 改名「人物」'], YEL1, 13, 30)
    save('u-invert-copy', svg(W, H, s, '反转选区，再拷贝并粘贴到新图层'))


def u_check_bg():
    ph, g = studio(LX + 10, CY, 300, CH, bg='#1E293B', rim='#F8FAFC')
    lay, pos = layers2([L('人物', 'figure', alpha=False), L('检查底色', 'dark', sel=True), L('原图', 'scene', lock=True, hidden=True)], x=440, y=62)
    s = screen(ph + lay, active='layers') + ring(*icon_pos('layers'), 18)
    s += badge(440 - 16, 62 + 44 + 44 + 19, 1) + ring(440 + 300 - 22, 62 + 44 + 88 + 19, 13) + badge(440 + 300 + 14, 62 + 44 + 88 + 19, 2)
    s += side_note(440, 250, ['① 人物下面新建一层，', '　 图层选项 › 填充图层，', '　 先填深色，再换浅色看', '② 关掉原图'], YEL1, 13, 30)
    s += side_note(64, 470, ['深色底上一圈发亮的边 = 白边'], RED1, 13)
    s += note('示意图')
    save('u-check-bg', svg(W, H, s, '在人物下面垫一层深色，检查白边'))


def u_mask_add():
    ph, g = studio(LX + 10, CY, 300, CH, bg='#1E293B')
    lay, pos = layers2([L('人物', 'figure', sel=True), L('检查底色', 'dark'), L('原图', 'scene', lock=True, hidden=True)], x=470, y=62)
    oy = 120
    s = screen(ph + lay + layer_options(310, oy, '蒙版'), active='layers')
    s += badge(470 + 150, 62 + 44 + 19, 1) + badge(310 - 16, opt_y('蒙版', oy), 2)
    s += side_note(470, 260, ['① 点一下「人物」，', '　 再点一次打开图层选项', '② 点「蒙版」：人物上方', '　 多出一层「图层蒙版」'], YEL1, 13, 30)
    s += note('示意图')
    save('u-mask-add', svg(W, H, s, '图层选项里点蒙版'))


def u_mask_hair():
    x0, y0, w0, h0 = LX + 10, CY, 300, CH
    ph, g = studio(x0, y0, w0, h0, bg='#1E293B')
    # 放大看头发边：画几条发丝和一笔顺着发丝的笔触
    zx, zy = g['cx'] - g['hh'] * 0.95, g['top'] + g['hh'] * 0.3
    stroke = f'<path d="M{zx - 4:.1f} {zy + 40:.1f} q-6 -24 6 -48" fill="none" stroke="#000" stroke-width="7" stroke-opacity=".55" stroke-linecap="round"/>'
    body = ph + stroke + pencil(zx - 2, zy + 44, 215)
    lay, pos = layers2([L('图层蒙版', 'mask', sel=True, indent=1, hl=True), L('人物', 'figure'), L('检查底色', 'dark')], x=440, y=62)
    s = screen(body + lay, active='brush') + ring(*icon_pos('brush'), 18)
    s += badge(440 - 16, 62 + 44 + 19, 1) + badge(zx - 26, zy + 10, 2)
    s += side_note(440, 250, ['① 点蒙版那一行（不是人物）', '② 细笔、黑色、不透明度 30%～60%，', '　 顺着发丝方向画，', '　 把发丝之间的背景压暗', '画错了换白色涂回来'], YEL1, 13, 30)
    s += note('示意图')
    save('u-mask-hair', svg(W, H, s, '在蒙版上顺着发丝方向画'))


def u_mask_merge():
    ph, g = studio(LX + 10, CY, 300, CH, bg='#1E293B')
    lay, pos = layers2([L('图层蒙版', 'mask', sel=True, indent=1), L('人物', 'figure'), L('人物 备份', 'figure', hidden=True), L('检查底色', 'dark')], x=470, y=62)
    oy = 100
    s = screen(ph + lay + layer_options(310, oy, '向下合并'), active='layers')
    s += badge(310 - 16, opt_y('向下合并', oy), 2) + badge(470 + 150, 62 + 44 + 44 + 44 + 19, 1)
    s += side_note(470, 300, ['① 先复制一份「人物」当备份，', '　 关掉不看', '② 点蒙版，打开图层选项，', '　 「向下合并」：蒙版变成', '　 人物层自己的透明度'], YEL1, 13, 30)
    s += note('示意图，菜单项以实际界面为准')
    save('u-mask-merge', svg(W, H, s, '把蒙版向下合并到人物层'))


def u_alpha():
    ph, g = studio(LX + 10, CY, 300, CH, bg='#1E293B', rim='#E2E8F0')
    zx, zy = g['cx'] + g['hh'] * 0.75, g['top'] + g['hh'] * 0.9
    body = ph + soft_stroke(f'M{zx:.1f} {zy - 40:.1f} q14 30 6 70', PINK, 14, .85) + pencil(zx + 8, zy + 32, 25)
    lay, pos = layers2([L('人物', 'figure', alpha=True, sel=True, hl=True), L('检查底色', 'dark')], x=440, y=62)
    rx, ry, rw, rh = pos['人物']
    fingers = ''.join(f'<ellipse cx="{rx + 110 + k * 22}" cy="{ry + 19}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>' for k in range(2)) + arrow(rx + 156, ry + 19, rx + 210, ry + 19, INK, 2.5)
    s = screen(body + lay + fingers, active='brush')
    s += badge(rx - 16, ry + 19, 1) + badge(zx - 24, zy - 30, 2)
    s += side_note(440, 200, ['① 两指在「人物」上向右滑：', '　 阿尔法锁定，缩略图出现棋盘格', '② 吸取旁边发丝的颜色，', '　 软画笔 10%～20% 沿边缘涂', '白边变成头发色，透明度不变'], YEL1, 13, 30)
    s += note('示意图')
    save('u-alpha', svg(W, H, s, '阿尔法锁定后给边缘重新上色'))


def p_threshold():
    Wd, Hd = 760, 300
    s = []
    items = [('阈值太低：背景没选满', RED1), ('合适：背景刚好选满', MINT1), ('太高：漏进了头发和衣服', RED1)]
    for col, (t, f) in enumerate(items):
        ox = 14 + col * 250
        s.append(panel_box(ox, 10, 236, 280, t, WHITE, f))
        x, y, w, h = ox + 28, 56, 180, 180
        ph, g = studio(x, y, w, h, bg='#E2E8F0')
        person = hair_person(g['cx'], g['top'], g['hh'], sw=2)
        if col == 0:
            ov = clip(f'<rect x="{x}" y="{y}" width="{w}" height="{h * 0.55}" fill="#FDE68A" fill-opacity=".7"/>' + person, x, y, w, h)
        elif col == 1:
            ov = clip(sel_overlay(x, y, w, h) + person, x, y, w, h)
        else:
            ov = clip(sel_overlay(x, y, w, h) + person + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FDE68A" fill-opacity=".45"/>', x, y, w, h)
        s.append(ph + ov + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>')
        s.append(text(ox + 118, 262, ['往右拖，增大阈值', '再往右一点就会漏', '往左拖回来'][col], 13, 600, MUTED, 'middle'))
    save('p-threshold', svg(Wd, Hd, ''.join(s), '选区阈值：和点的那个颜色差多少以内的才算进来'))


def p_edge():
    Wd, Hd = 760, 340
    s = [panel_box(20, 10, 720, 320, '白边从哪来：边缘的像素是头发和背景混出来的颜色', WHITE, YEL1)]
    cols_ = ['#F472B6', '#F472B6', '#F7A1CF', '#FAD1E7', '#F1F5F9', '#F1F5F9']
    for k, c in enumerate(cols_):
        s.append(f'<rect x="{60 + k * 44}" y="70" width="44" height="44" fill="{c}" stroke="{INK}" stroke-width="1.5"/>')
    s.append(text(60, 136, '头发', 13, 700) + text(148, 136, '边缘：一半头发一半白墙', 13, 700, VIO7) + text(236 + 30, 136, '', 13))
    s.append(text(60, 160, '抠图时边缘这两格保留了下来（还带着白墙的颜色）', 13, 400, MUTED))
    labels_ = [('放到深色背景上', '#1E293B', ['#F472B6', '#F472B6', '#F7A1CF', '#FAD1E7']), ('阿尔法锁定重新上色后', '#1E293B', ['#F472B6', '#F472B6', '#F472B6', '#F472B6'])]
    for j, (t, bg, cs) in enumerate(labels_):
        ox = 60 + j * 340
        s.append(text(ox, 200, t, 14, 800))
        s.append(f'<rect x="{ox}" y="212" width="264" height="44" fill="{bg}"/>')
        for k, c in enumerate(cs):
            op = [1, 1, 0.7, 0.4][k]
            s.append(f'<rect x="{ox + k * 44}" y="212" width="44" height="44" fill="{c}" fill-opacity="{op}" stroke="{INK}" stroke-width="1.5"/>')
        s.append(text(ox, 284, ['边缘两格偏白，在深色上就是一圈亮边' , '透明度没变，颜色换成了头发色'][j], 13, 700, [RED7, MINT7][j]))
    s.append(text(60, 312, '所以去白边不是把边"擦掉"，而是把边缘的颜色换掉，半透明保留，发丝才不会变硬。', 13, 400, MUTED))
    save('p-edge', svg(Wd, Hd, ''.join(s), '白边原理：边缘像素混进了原背景的颜色'))


def p_mask():
    Wd, Hd = 760, 260
    s = [panel_box(20, 10, 720, 240, '蒙版：黑色遮住，白色显示，灰色半透明', WHITE, YEL1)]
    for k, (c, t) in enumerate([('#000000', '黑：这里看不见'), ('#808080', '灰：半透明'), ('#FFFFFF', '白：完全显示')]):
        x = 60 + k * 230
        s.append(f'<rect x="{x}" y="64" width="80" height="80" fill="{c}" stroke="{INK}" stroke-width="2"/>')
        s.append(arrow(x + 90, 104, x + 120, 104, INK, 2.5))
        s.append(checker(x + 130, 64, 80, 80, 8) + f'<rect x="{x + 130}" y="64" width="80" height="80" fill="{PINK}" fill-opacity="{[0, .5, 1][k]}" stroke="{INK}" stroke-width="2"/>')
        s.append(text(x, 172, t, 14, 700))
    s.append(text(60, 214, '蒙版只是"遮"，没有删掉像素：涂错了用白色涂回来就行。这是它比橡皮擦好的地方。', 13, 400, MUTED))
    save('p-mask', svg(Wd, Hd, ''.join(s), '蒙版的黑白灰'))


def p_hair():
    Wd, Hd = 760, 300
    s = []
    for col, (t, f, good) in enumerate([('横着一刀切过发丝', RED1, False), ('顺着发丝的方向画', MINT1, True)]):
        ox = 20 + col * 380
        s.append(panel_box(ox, 10, 360, 280, t, WHITE, f))
        x, y = ox + 30, 56
        s.append(f'<rect x="{x}" y="{y}" width="300" height="170" fill="#1E293B"/>')
        rnd = random.Random(5)
        for k in range(14):
            bx = x + 30 + k * 18
            ex = bx + rnd.uniform(-20, 20)
            ey = y + 30 + rnd.uniform(0, 40)
            if not good:
                ey = max(ey, y + 100)
                s.append(f'<path d="M{bx} {y + 170} Q{bx + 4} {y + 130} {ex:.1f} {ey:.1f}" fill="none" stroke="{PINK}" stroke-width="2"/>')
            else:
                s.append(f'<path d="M{bx} {y + 170} Q{bx + 4} {y + 100} {ex:.1f} {ey:.1f}" fill="none" stroke="{PINK}" stroke-width="2" stroke-opacity=".9"/>')
        if not good:
            s.append(f'<line x1="{x}" y1="{y + 100}" x2="{x + 300}" y2="{y + 100}" stroke="{RED}" stroke-width="2" stroke-dasharray="6 4"/>')
            s.append(text(ox + 30, 252, '发丝全断在一条线上，像剪过的', 13, 700) + text(ox + 30, 274, '一眼就看出是抠出来的', 13, 400, MUTED))
        else:
            for k in range(4):
                s.append(f'<path d="M{x + 40 + k * 60} {y + 130} q4 -50 -6 -90" fill="none" stroke="{WHITE}" stroke-width="5" stroke-opacity=".35" stroke-linecap="round" stroke-dasharray="2 6"/>')
            s.append(text(ox + 30, 252, '每根发丝的长短不一样，末梢半透明', 13, 700) + text(ox + 30, 274, '白色虚线：蒙版笔触的方向', 13, 400, MUTED))
    save('p-hair', svg(Wd, Hd, ''.join(s), '处理发丝：顺着发丝方向，保留半透明'))


def case_halo(after):
    cap = '修之后：边缘干净，发丝半透明' if after else '修之前：换到深色背景，一圈白边'
    ph, g = studio(20, 20, 600, 480, bg='#312E81', rim=None if after else '#F8FAFC')
    s = [ph, f'<rect x="20" y="20" width="600" height="480" fill="none" stroke="{INK}" stroke-width="2"/>']
    s.append(label(606, 56, cap, VIO1, 16, 'end') if after else label(34, 56, cap, YEL1, 16))
    return svg(640, 520, ''.join(s), cap)


def run_m205():
    for f in [u_auto_sel, u_sel_fix, u_invert_copy, u_check_bg, u_mask_add, u_mask_hair, u_mask_merge, u_alpha, p_threshold, p_edge, p_mask, p_hair]:
        f()
    save('case-halo-before', case_halo(False)); save('case-halo-after', case_halo(True))



# ======================= 2.6 工作习惯 =======================
def u_rename():
    ph, g = hall(LX + 10, CY, 300, CH)
    lay, pos = layers2([L('图层 3', 'paint', sel=True), L('图层 2', 'face'), L('原图', 'scene', lock=True)], x=470, y=62)
    oy = 120
    s = screen(ph + lay + layer_options(310, oy, '重命名'), active='layers')
    s += badge(470 + 150, 62 + 44 + 19, 1) + badge(310 - 16, opt_y('重命名', oy), 2)
    s += side_note(470, 260, ['① 点当前图层，再点一次', '② 重命名，按做了什么起名：', '　 「02 克隆 去痘」', '　 「05 光影 柔光」'], YEL1, 13, 30)
    s += note('示意图')
    save('u-rename', svg(W, H, s, '图层选项里重命名'))


def u_group():
    ph, g = hall(LX + 10, CY, 300, CH)
    rows = [L('04 液化 人物', 'figure', sel=True), L('03 克隆 背景', 'scene', sec=True), L('02 克隆 去痘', 'face', sec=True), L('原图', 'scene', lock=True)]
    lay, pos = layers2(rows, x=440, y=62, top_btns=['删除', '组'], hl_btn='组')
    rx, ry, rw, rh = pos['03 克隆 背景']
    fing = fingertip(rx + 150, ry + 19) + arrow(rx + 166, ry + 19, rx + 220, ry + 19, INK, 2.5)
    s = screen(ph + lay + fing, active='layers')
    s += badge(rx - 16, ry + 19, 1) + badge(pos['btn:组'][0], pos['btn:组'][1] + 26, 2)
    s += side_note(440, 300, ['① 在其他要编组的图层上', '　 一指向右滑：变成深蓝（次要选中）', '② 点右上角「组」', '③ 点组名，重命名为「基础」'], YEL1, 13, 30)
    s += note('示意图')
    save('u-group', svg(W, H, s, '向右滑多选图层，点组'))


def gallery_frame(inner):
    return f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#1F2329"/>' + inner


def gthumb(x, y, w, h, name, kind='scene'):
    ph, g = hall(x, y, w, h)
    return ph + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="none" stroke="#4B5563"/>' + text(x, y + h + 20, name, 13, 600, UITEXT)


def u_gallery_dup():
    s = text(SX + 26, 52, 'Procreate', 22, 800, UITEXT)
    for k, (x, txt) in enumerate([(520, '选择'), (588, '导入'), (656, '照片')]):
        s += text(x, 52, txt, 18, 700, UITEXT, 'middle')
    s += text(730, 52, '+', 30, 700, UITEXT, 'middle')
    s += gthumb(60, 100, 170, 220, '雷电将军_03_v1')
    # 被左滑的作品
    x, y = 290, 100
    s += gthumb(x - 90, y, 170, 220, '').replace('', '') if False else ''
    s += f'<g>{hall(x - 60, y, 170, 220)[0]}</g>'
    for j, (b, col) in enumerate([('分享', '#4B5563'), ('复制', '#2563EB'), ('删除', '#DC2626')]):
        bx = x + 110 + j * 60
        s += f'<rect x="{bx}" y="{y}" width="60" height="220" fill="{col}"/>' + text(bx + 30, y + 116, b, 15, 800, WHITE, 'middle')
        if b == '复制':
            s += ringrect(bx + 3, y + 4, 54, 212, 6)
    s += text(x - 60, y + 240, '雷电将军_03_v2', 13, 600, UITEXT)
    s += badge(x + 60, y + 110, 1) + badge(x + 170, y - 14, 2)
    s += label(60, 400, '① 在作品上向左轻滑　② 点「复制」：整个作品连图层一起复制一份', YEL1, 14)
    s += label(60, 436, '点作品名字可以改名，比如把旧的那份改成 v1，继续在新的上面修', WHITE, 14)
    s += label(60, 472, '把同一张图的几个版本拖到一起，会叠成一个「堆」', WHITE, 14)
    s += note('示意图')
    save('u-gallery-dup', svg(W, H, gallery_frame(s), '在图库里向左滑动作品，点复制'))


def u_merge():
    ph, g = face_photo(LX + 10, CY, 300, CH)
    rows = [L('03 补肤色', 'paint'), L('02 克隆 去痘 b', 'face', sel=True), L('02 克隆 去痘 a', 'face'), L('原图', 'face', lock=True)]
    lay, pos = layers2(rows, x=440, y=62)
    a = pos['02 克隆 去痘 b']; b = pos['02 克隆 去痘 a']
    fx = a[0] + 200
    fing = (fingertip(fx, a[1] - 4) + fingertip(fx, b[1] + b[3] + 4) + arrow(fx, a[1] + 12, fx, a[1] + 30, INK, 2.5) + arrow(fx, b[1] + b[3] - 12, fx, b[1] + b[3] - 30, INK, 2.5))
    s = screen(ph + lay + fing, active='layers')
    s += badge(a[0] - 16, a[1] + 40, 1)
    s += side_note(440, 300, ['① 两指分别按住上下两层，往中间捏：', '　 这两层和中间的层合成一层', '合并后名字用最下面那层的', '合并前先在图库里复制一份作品'], YEL1, 13, 30)
    s += note('示意图')
    save('u-merge', svg(W, H, s, '两指捏合合并图层'))


def u_export():
    ph, g = hall(470, 70, 280, 400)
    rows = ['Procreate', 'PSD', 'PDF', 'JPEG', 'PNG', 'TIFF']
    menu = actions_menu('分享', rows=rows, hl='JPEG', toggles={})
    s = screen(ph + menu, active='actions') + ring(*icon_pos('actions'), 18)
    s += badge(400, 62 + 50 + 3 * 34 + 17, 1) + badge(400, 62 + 50 + 4 * 34 + 17, 2) + badge(400, 62 + 50 + 17, 3)
    s += side_note(64, 400, ['① JPEG：发平台、交给 coser', '② PNG：无损，要再进别的 App 时用', '③ Procreate：备份，保留全部图层'], YEL1, 13, 30)
    s += note('示意图')
    save('u-export', svg(W, H, s, '操作 › 分享：选导出格式'))


def u_resample():
    ph, g = hall(250, 70, 300, 300)
    grid = ''.join(f'<line x1="{250 + k * 50}" y1="70" x2="{250 + k * 50}" y2="370" stroke="{WHITE}" stroke-width="1" stroke-opacity=".7"/>' for k in range(1, 6))
    grid += ''.join(f'<line x1="250" y1="{70 + k * 50}" x2="550" y2="{70 + k * 50}" stroke="{WHITE}" stroke-width="1" stroke-opacity=".7"/>' for k in range(1, 6))
    px, py, pw, phh = 150, 390, 500, 140
    pan = panel(px, py, pw, phh)
    pan += text(px + 20, py + 34, '画布重新取样', 15, 700, UITEXT) + f'<rect x="{px + 150}" y="{py + 18}" width="44" height="22" rx="11" fill="{UIBLUE}"/><circle cx="{px + 183}" cy="{py + 29}" r="9" fill="{WHITE}"/>'
    for k, (n, v) in enumerate([('宽度', '2250 px'), ('高度', '3000 px')]):
        bx = px + 20 + k * 240
        pan += text(bx, py + 84, n, 14, 700, UITEXT) + f'<rect x="{bx + 44}" y="{py + 62}" width="150" height="34" rx="8" fill="{UIBAR}"/>' + text(bx + 60, py + 85, v, 15, 800, WHITE)
    pan += text(px + 232, py + 85, '🔗', 14, 400, UITEXT, 'middle') if False else f'<path d="M{px + 222} {py + 80} h20" stroke="{UITEXT}" stroke-width="3"/>'
    s = screen(ph + grid + pan, active='actions')
    s += ringrect(px + 10, py + 12, 194, 36) + badge(px + 220, py + 30, 2)
    s += ringrect(px + 300, py + 58, 160, 42) + badge(px + 476, py + 79, 3)
    s += side_note(570, 110, ['① 先在图库复制作品，', '　 在副本上：操作 › 画布', '　 › 裁剪并调整大小', '② 打开「画布重新取样」', '③ 输入长边的像素数，', '　 另一边按比例自动算'], YEL1, 13, 30)
    s += note('示意图，界面以实际为准')
    save('u-resample', svg(W, H, s, '裁剪并调整大小里打开画布重新取样，输入新尺寸'))


def p_structure():
    Wd, Hd = 760, 530
    s = [panel_box(20, 10, 720, 510, '推荐的图层结构（从下往上做）', WHITE, YEL1)]
    rows = [L('调色', group=True), L('渐变映射 副本 20%', 'merged', indent=1), L('特效', group=True), L('光效 添加', 'paint', 'A', indent=1),
            L('精修', group=True), L('光影 柔光', 'gray', 'Sl', indent=1), L('补肤色', 'paint', indent=1),
            L('基础', group=True), L('液化 人物', 'figure', indent=1), L('克隆 去瑕疵', 'face', indent=1), L('原图', 'scene', lock=True, sel=True)]
    lay, pos = layers2(rows, x=50, y=56, w=330, row_h=36)
    s.append(lay)
    notes = [('调色', '最后统一颜色：全部拷贝后调整，或者用混合模式色层'), ('特效', '新建空图层画：光效、粒子、魔法阵'),
             ('精修', '新建空图层画：补肤色、光影、妆面'), ('基础', '必须在原图的副本上做：克隆、液化、调整'), ('原图', '锁定，永远不动')]
    for k, (nm, t) in enumerate(notes):
        x0, y0, w0, h0 = pos[nm]
        s.append(f'<line x1="{x0 + w0 + 6}" y1="{y0 + 17}" x2="410" y2="{y0 + 17}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="4 3"/>')
        s.append(label(416, y0 + 23, t, [VIO1, PINK1, MINT1, YEL1, WHITE][k], 13))
    save('p-structure', svg(Wd, Hd, ''.join(s), '推荐的图层结构：原图、基础、精修、特效、调色'))


def p_merge():
    Wd, Hd = 760, 330
    s = [panel_box(20, 10, 720, 310, '图层快不够了：先合并什么', WHITE, YEL1)]
    items = [(MINT1, '可以合', ['同一步拆成的好几层（去痘 a、b、c）', '确定不再改的补画层', '已经关掉、不打算用的试验层 → 直接删']),
             (YEL1, '先存版本再合', ['一整个组都修完了：先在图库复制作品', '再把这个组合成一层', '想改时回到旧版本拿']),
             (RED1, '不要合', ['原图', '还要来回调强弱的层（光影、颗粒、调色）', '带蒙版、还没定稿的人物层'])]
    for k, (f, t, lines) in enumerate(items):
        ox = 40 + k * 232
        s.append(f'<rect x="{ox}" y="60" width="216" height="240" rx="12" fill="{f}" stroke="{INK}" stroke-width="2"/>')
        s.append(text(ox + 16, 92, t, 16, 800))
        for j, ln in enumerate(lines):
            for m, part in enumerate([ln[i:i + 13] for i in range(0, len(ln), 13)]):
                s.append(text(ox + 16, 126 + j * 58 + m * 20, ('· ' if m == 0 else '  ') + part, 13, 600 if m == 0 else 500))
    save('p-merge', svg(Wd, Hd, ''.join(s), '图层快不够时，按这个顺序合并'))


def layer_shot(rows, title, cap, fill):
    Wd, Hd = 640, 520
    s = [f'<rect x="20" y="20" width="600" height="480" rx="16" fill="#D7DBE0"/>']
    lay, pos = layers2(rows, x=150, y=40, w=340, row_h=34)
    s.append(lay)
    s.append(label(34, 488, cap, fill, 15))
    return svg(Wd, Hd, ''.join(s), cap)


def case_layers(after):
    if not after:
        rows = [L(f'图层 {n}', k) for n, k in [(14, 'paint'), (13, 'paint'), (12, 'figure'), (11, 'paint'), (10, 'face'), (9, 'gray'), (8, 'paint'), (7, 'face'), (6, 'scene'), (5, 'face')]] + [L('图层 1', 'scene', sel=True)]
        return layer_shot(rows, '', '修之前：14 层都叫「图层 X」，原图没锁', YEL1)
    rows = [L('调色', group=True), L('特效', group=True, open_=False), L('精修', group=True), L('05 光影 柔光', 'gray', 'Sl', indent=1), L('04 补肤色', 'paint', indent=1),
            L('基础', group=True), L('03 液化 人物', 'figure', indent=1), L('02 克隆 背景', 'scene', indent=1), L('01 克隆 去痘', 'face', indent=1), L('原图', 'scene', lock=True, sel=True)]
    return layer_shot(rows, '', '修之后：分了组、都有名字', VIO1)


def run_m206():
    for f in [u_rename, u_group, u_gallery_dup, u_merge, u_export, u_resample, p_structure, p_merge]:
        f()
    save('case-layers-before', case_layers(False)); save('case-layers-after', case_layers(True))


if __name__ == '__main__':
    import shutil
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    for k, v in list(globals().items()):
        if k.startswith('run_m2') and callable(v):
            v()
    print('done', len(DONE))
