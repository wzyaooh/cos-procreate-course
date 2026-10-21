"""M1 Procreate 基础操作 的示意图。运行：python tools/diagrams/m1.py"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'diagrams', 'm1')
os.makedirs(OUT, exist_ok=True)
ALL = []


def save(name, s):
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)


def reg(f):
    ALL.append(f)
    return f


CX, CY, CW, CH = 262, 66, 276, 340   # 界面里的画布（竖幅照片）
GRAY_BG = '#D7DBE0'


def photo(top=None, skirt=None, **kw):
    s, g = scene(CX, CY, CW, CH, **kw)
    if top:
        s = s.replace(VIO2, top)
    if skirt:
        s = s.replace(f'fill="{VIO}"', f'fill="{skirt}"')
    return s, g


def cbadge(x, y, n, fill=YEL):
    return badge(x, y, n, fill)


def legend(x, y, items, size=14, gap=30, w=None, fill=YEL1):
    """编号说明：[(n, 文字)]"""
    s = []
    for i, (n, t) in enumerate(items):
        yy = y + i * gap
        s.append(badge(x + 13, yy - 5, n) + text(x + 34, yy, t, size, 700, INK))
    return ''.join(s)


def dark_legend(x, y, items, size=14, gap=30):
    s = []
    for i, (n, t) in enumerate(items):
        yy = y + i * gap
        s.append(badge(x + 13, yy - 5, n) + text(x + 34, yy, t, size, 700, UITEXT))
    return ''.join(s)


def popup(x, y, w, rows, hl=None, title=None, row_h=34, toggles=()):
    h = (44 if title else 8) + len(rows) * row_h + 6
    s = panel(x, y, w, h, title)
    s += menu_rows(x, y + (40 if title else 4), w, rows, hl, row_h=row_h, toggles=toggles)
    return s


def checker(x, y, w, h, c=10, pid='chk'):
    return (f'<defs><pattern id="{pid}" width="{c * 2}" height="{c * 2}" patternUnits="userSpaceOnUse">'
            f'<rect width="{c * 2}" height="{c * 2}" fill="#FFFFFF"/><rect width="{c}" height="{c}" fill="#D1D5DB"/>'
            f'<rect x="{c}" y="{c}" width="{c}" height="{c}" fill="#D1D5DB"/></pattern></defs>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{pid})"/>')


# ---------- 图层面板（支持蒙版、剪辑、阿尔法锁定、次要图层） ----------
def thumb(kind, x, y, w=44, h=34, pid='t'):
    s = ''
    if kind == 'scene':
        s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#FFF7E6"/><rect x="{x + 2}" y="{y + h - 9}" width="{w - 4}" height="7" fill="{FLOOR}"/>'
             f'<path d="M{x + 24} {y + h - 4} q-5 -14 0 -24 q5 10 0 24" fill="{VIO2}" stroke="{INK}" stroke-width="1"/>'
             f'<rect x="{x + 5}" y="{y + 8}" width="8" height="18" fill="{YEL1}" stroke="{INK}" stroke-width="1"/>')
    elif kind.startswith('color:'):
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{kind[6:]}"/>'
    elif kind.startswith('dress:'):
        s = (checker(x, y, w, h, 5, pid) + f'<path d="M{x + 16} {y + 6} L{x + 28} {y + 6} L{x + 34} {y + h - 4} L{x + 10} {y + h - 4} Z" fill="{kind[6:]}" stroke="{INK}" stroke-width="1"/>')
    elif kind == 'mask-white':
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#FFFFFF"/>'
    elif kind == 'mask-bw':
        s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#111"/>'
             f'<path d="M{x + 16} {y + 6} L{x + 28} {y + 6} L{x + 34} {y + h - 4} L{x + 10} {y + h - 4} Z" fill="#FFF"/>')
    elif kind == 'gray':
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#808080"/>'
    elif kind == 'empty':
        s = checker(x, y, w, h, 5, pid)
    elif kind == 'stroke':
        s = checker(x, y, w, h, 5, pid) + f'<path d="M{x + 6} {y + 24} q12 -18 32 -8" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
    elif kind == 'glow':
        s = checker(x, y, w, h, 5, pid) + f'<circle cx="{x + 22}" cy="{y + 17}" r="11" fill="{YEL}" opacity=".8"/>'
    elif kind == 'poster':
        s = checker(x, y, w, h, 5, pid) + f'<rect x="{x + 12}" y="{y + 4}" width="20" height="26" fill="{PINK}" stroke="{INK}" stroke-width="1"/>'
    else:
        s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{WHITE}"/>'
    return s


def lpanel(rows, x=470, y=62, w=300, title='图层', hl_row=None, hl_mode=None, show_plus=True, row_h=52):
    """rows: dict(name, thumb, mode='N', sel=None|'p'|'s', indent=False, lock=False, alpha=False, clip=False, off=False)"""
    h = 50 + len(rows) * row_h + 8
    s = [panel(x, y, w, h, title)]
    if show_plus:
        s.append(text(x + w - 26, y + 30, '+', 24, 700, UITEXT, 'middle'))
    for i, r in enumerate(rows):
        yy = y + 44 + i * row_h
        ind = 22 if r.get('indent') else 0
        sel = r.get('sel')
        fill = UIBLUE if sel == 'p' else ('#1E3A8A' if sel == 's' else UIBAR)
        s.append(f'<rect x="{x + 8 + ind}" y="{yy}" width="{w - 16 - ind}" height="{row_h - 6}" rx="8" fill="{fill}"/>')
        if r.get('clip'):
            s.append(f'<path d="M{x + 14} {yy + 10} v18 m-5 -6 l5 7 l5 -7" fill="none" stroke="{UITEXT}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
        if r.get('indent') and not r.get('clip'):
            s.append(f'<path d="M{x + 16} {yy - 4} v{row_h * 0.55:.0f} h8" fill="none" stroke="{UIDIM}" stroke-width="2"/>')
        tx = x + 16 + ind
        s.append(thumb(r.get('thumb', 'blank'), tx, yy + 6, pid=f'lp{int(x)}{int(y)}{i}'))
        if r.get('alpha'):
            s.append(f'<rect x="{tx}" y="{yy + 6}" width="44" height="34" rx="4" fill="none" stroke="{YEL}" stroke-width="0"/>')
        name = r['name']
        s.append(text(tx + 54, yy + 29, name, 15 if len(name) < 9 else 13, 700, UITEXT))
        if r.get('lock'):
            lx = x + w - 66
            s.append(f'<rect x="{lx - 6}" y="{yy + 20}" width="12" height="10" rx="2" fill="{UITEXT}"/><path d="M{lx - 4} {yy + 20} v-4 a4 4 0 0 1 8 0 v4" fill="none" stroke="{UITEXT}" stroke-width="2"/>')
        s.append(text(x + w - 44, yy + 29, r.get('mode', 'N'), 14, 800, UITEXT, 'middle'))
        if hl_mode == i:
            s.append(ring(x + w - 44, yy + 24, 15))
        off = r.get('off')
        s.append(f'<rect x="{x + w - 30}" y="{yy + 15}" width="16" height="16" rx="3" fill="{"none" if off else UIBLUE}" stroke="{UITEXT}" stroke-width="1.5"/>')
        if hl_row == i:
            s.append(ringrect(x + 4 + ind, yy - 3, w - 8 - ind, row_h))
    return ''.join(s)


def row_y(i, y=62, row_h=52):
    return y + 44 + i * row_h + (row_h - 6) / 2


# ---------- 手势 ----------
def tap_fingers(x, y, n=2, label_txt=None):
    s = []
    for i in range(n):
        fx = x + (i - (n - 1) / 2) * 26
        s.append(f'<circle cx="{fx:.1f}" cy="{y}" r="17" fill="none" stroke="{YEL}" stroke-width="3" stroke-dasharray="4 3"/>')
        s.append(f'<ellipse cx="{fx:.1f}" cy="{y}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
    return ''.join(s)


def pinch(x, y, inward=True, spread=46, fast=False):
    s = []
    for sgn in (-1, 1):
        fx = x + sgn * spread
        s.append(f'<ellipse cx="{fx}" cy="{y}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
        if inward:
            s.append(arrow(fx - sgn * 14, y, x + sgn * 12, y, INK, 3))
        else:
            s.append(arrow(x + sgn * 10, y, fx - sgn * 14, y, INK, 3))
    if fast:
        s.append(text(x, y - 22, '快！', 14, 900, RED7, 'middle'))
    return ''.join(s)


def scrub(x, y, n=3):
    s = []
    for i in range(n):
        fx = x + (i - (n - 1) / 2) * 24
        s.append(f'<ellipse cx="{fx:.1f}" cy="{y}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<path d="M{x - 60} {y + 26} l20 -10 l20 10 l20 -10 l20 10 l20 -10 l20 10" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
    s.append(arrow(x + 62, y + 26, x + 74, y + 20, INK, 3))
    s.append(arrow(x - 62, y + 26, x - 74, y + 20, INK, 3))
    return ''.join(s)


def notice(msg, x=400, y=78):
    w = len(msg) * 15 + 36
    return (f'<rect x="{x - w / 2:.1f}" y="{y - 20}" width="{w:.1f}" height="32" rx="16" fill="{UIPANEL}" stroke="#111827"/>'
            + text(x, y + 1, msg, 15, 700, UITEXT, 'middle'))


def frame_dark(inner):
    return f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#1F2329"/>' + inner


def gallery_top(hl=None, sel_mode=False):
    s = text(SX + 26, 52, 'Procreate', 22, 800, UITEXT)
    xs = {'选择': 520, '导入': 588, '照片': 656, '+': 730}
    if sel_mode:
        xs = {'堆': 450, '预览': 510, '分享': 580, '复制': 646, '删除': 712}
    for k, x in xs.items():
        s += text(x, 52, k, 18 if k != '+' else 30, 700, UITEXT, 'middle')
        if hl == k:
            s += ringrect(x - 30, 26, 60, 38) if k != '+' else ring(x, 42, 20)
    return s, xs


def gthumb(x, y, w, h, kind=0, name='未命名作品', tick=None):
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#FFF7E6"/>'
    if kind == 0:
        s += f'<path d="M{x + w / 2} {y + h - 8} q-14 -40 0 -70 q14 30 0 70" fill="{PINK}" stroke="{INK}" stroke-width="1.5"/>'
    elif kind == 1:
        s += f'<path d="M{x + w / 2} {y + h - 8} q-14 -40 0 -70 q14 30 0 70" fill="{VIO2}" stroke="{INK}" stroke-width="1.5"/>'
    else:
        s += f'<path d="M{x + w / 2} {y + h - 8} q-14 -40 0 -70 q14 30 0 70" fill="{MINT}" stroke="{INK}" stroke-width="1.5"/>'
    s += text(x, y + h + 20, name, 13, 600, UITEXT)
    if tick is not None:
        on = tick
        s += f'<circle cx="{x + w - 14}" cy="{y + h - 14}" r="11" fill="{UIBLUE if on else "#00000055"}" stroke="{WHITE}" stroke-width="2"/>'
        if on:
            s += f'<path d="M{x + w - 19} {y + h - 14} l4 4 l7 -8" fill="none" stroke="{WHITE}" stroke-width="2.5"/>'
    return s


def card(x, y, w, h, fill=WHITE):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{INK}" stroke-width="2.5"/>'


def wrap(x, y, s, size=14, width=20, weight=600, fill=INK, lh=None):
    """按字数换行（中文）"""
    lh = lh or size + 7
    out, line, n, row = [], '', 0.0, 0
    for ch in s:
        n += 1.0 if ord(ch) > 255 else 0.55
        line += ch
        if n >= width:
            out.append(text(x, y + row * lh, line, size, weight, fill)); row += 1; line, n = '', 0.0
    if line:
        out.append(text(x, y + row * lh, line, size, weight, fill))
    return ''.join(out)


# =====================================================================
# 1.1 界面和画布
# =====================================================================
@reg
def u_interface():
    ph, g = photo()
    s = screen(ph)
    nums = [('gallery', 1), ('actions', 2), ('adjust', 3), ('select', 4), ('transform', 5),
            ('brush', 6), ('smudge', 7), ('erase', 8), ('layers', 9), ('color', 10)]
    for k, n in nums:
        x, y = icon_pos(k)
        s += badge(x + (4 if k == 'gallery' else 0), 66, n)
    # 侧栏
    for n, yy, t in [(11, 211, '画笔尺寸'), (12, 277, '修改钮'), (13, 343, '不透明度'), (14, 438, '撤销/重做')]:
        s += badge(72, yy, n) + text(92, yy + 5, t, 14, 800, INK)
    items = [(1, '图库：回到作品列表'), (2, '操作：添加、画布、分享'), (3, '调整：调色、液化、克隆'),
             (4, '选取：圈出要改的范围'), (5, '变换：移动、缩放、变形'),
             (6, '绘图：用画笔画'), (7, '涂抹：推开、融合颜色'), (8, '擦除：橡皮'),
             (9, '图层：打开图层面板'), (10, '颜色：选颜色')]
    s += f'<rect x="548" y="92" width="226" height="{len(items) * 30 + 14}" rx="12" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'
    s += legend(556, 120, items, 13, 30)
    s += note('示意图：Procreate 5 布局，细节以实际界面为准')
    save('u-interface', svg(W, H, s, 'Procreate 画布界面：左上高级功能、右上绘图工具、左边侧栏'))


@reg
def u_canvas_color():
    top, xs = gallery_top('+')
    s = top + f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#000" fill-opacity=".45"/>'
    px, py, pw, ph = 120, 74, 560, 440
    s += panel(px, py, pw, ph) + text(px + pw / 2, py + 32, '自定义画布', 18, 800, UITEXT, 'middle')
    s += text(px + pw - 24, py + 32, '创建', 16, 800, UIBLUE, 'end')
    tabs = ['尺寸', '颜色配置', '缩时视频设置', '画布属性']
    for i, t in enumerate(tabs):
        y = py + 70 + i * 44
        s += f'<rect x="{px + 12}" y="{y}" width="150" height="36" rx="8" fill="{UIBLUE if i == 1 else UIBAR}"/>' + text(px + 26, y + 24, t, 15, 700, UITEXT)
    # RGB / CMYK
    bx = px + 190
    s += f'<rect x="{bx}" y="{py + 66}" width="200" height="36" rx="10" fill="{UIBAR}"/>'
    s += f'<rect x="{bx + 4}" y="{py + 70}" width="96" height="28" rx="8" fill="{UIBLUE}"/>' + text(bx + 52, py + 90, 'RGB', 15, 800, WHITE, 'middle')
    s += text(bx + 150, py + 90, 'CMYK', 15, 800, UITEXT, 'middle')
    rows = ['Display P3', 'sRGB IEC61966-2.1', '其他 RGB 配置……']
    s += menu_rows(bx - 10, py + 118, 360, rows, hl='sRGB IEC61966-2.1', row_h=42)
    s += f'<path d="M{bx + 318} {py + 136} l6 6 l10 -12" fill="none" stroke="{UIBLUE}" stroke-width="3"/>'
    s += text(bx + 316, py + 140, '默认', 12, 700, UIDIM, 'end')
    s += badge(px + 150, py + 110, 1) + badge(bx + 212, py + 84, 2) + badge(bx + 362, py + 181, 3)
    s += label(px + 190, py + 300, '② 修照片选 RGB（CMYK 是印刷用的）', YEL1, 14)
    s += label(px + 190, py + 334, '③ 发网上的作品选 sRGB 最稳', YEL1, 14)
    s += label(px + 190, py + 368, '　 默认的 Display P3 颜色更多，但部分平台显示会偏', WHITE, 13)
    s += note('示意图：图库「+」→ 带加号的长方形图标 → 颜色配置；列表以实际为准')
    save('u-canvas-color', svg(W, H, frame_dark(s), '自定义画布：颜色配置选 RGB 里的 sRGB'))


@reg
def u_insert():
    ph, g = photo()
    menu = actions_menu('添加', rows=['插入文件', '插入照片', '拍照', '添加文本', '剪切', '拷贝', '拷贝画布', '粘贴'], hl='插入照片', toggles={})
    s = screen(ph + menu, active='actions') + ring(*icon_pos('actions'), 18)
    s += badge(icon_pos('actions')[0], 66, 1) + badge(396, 62 + 50 + 34 + 17, 2)
    s += label(552, 160, '照片会放进当前画布的', YEL1, 14)
    s += label(552, 192, '一个新图层上', YEL1, 14)
    s += label(552, 240, '比画布大的照片会被缩小', RED1, 14)
    s += label(552, 272, '放进来，像素就少了', RED1, 14)
    s += note('示意图：操作 › 添加 › 插入照片')
    save('u-insert', svg(W, H, s, '操作、添加、插入照片：把照片放进当前画布'))


@reg
def u_share_menu():
    ph, g = photo()
    rows = ['分享图像', 'Procreate', 'PSD', 'PDF', 'JPEG', 'PNG', 'TIFF', '分享图层（每层一个文件）']
    menu = actions_menu('分享', rows=rows, hl=None, toggles={}, w=330)
    # 把分组标题行涂暗
    hdr = ''
    for i in (0, 7):
        yy = 62 + 50 + i * 34
        hdr += f'<rect x="76" y="{yy + 3}" width="318" height="28" rx="6" fill="#2B2F36"/>' + text(92, yy + 22, rows[i], 13, 700, UIDIM)
    s = screen(ph + menu + hdr, active='actions') + ring(*icon_pos('actions'), 18)
    for n, i in [(1, 1), (2, 2), (3, 4), (4, 5)]:
        yy = 62 + 50 + i * 34
        s += ringrect(76, yy + 3, 318, 28) + badge(410, yy + 17, n)
    items = [(1, '备份、以后还要改'), (2, '给电脑上的 PS 接着修'), (3, '交付、发朋友圈和平台'), (4, '要透明背景、要无损')]
    s += f'<rect x="440" y="168" width="330" height="{len(items) * 34 + 16}" rx="12" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'
    s += legend(450, 198, items, 14, 34)
    s += note('示意图：操作 › 分享；选完格式后弹出系统分享菜单')
    save('u-share-menu', svg(W, H, s, '操作、分享：选择导出格式'))


@reg
def u_bg_hide():
    feet = CY + CH * 0.88; top = CY + CH * 0.06; hh = (feet - top) / 6.4
    fig = figure(CX + CW / 2, top, hh, top + hh * 3.6, feet, sw=2)
    content = checker(CX, CY, CW, CH, 12, 'bgchk') + f'<rect x="{CX}" y="{CY}" width="{CW}" height="{CH}" fill="none" stroke="#94A3B8"/>' + fig
    rows = [dict(name='人物', thumb='dress:' + VIO2, sel='p'), dict(name='背景颜色', thumb='color:#FFFFFF', mode='', off=True)]
    lay = lpanel(rows, x=550, w=224)
    s = screen(content + lay, active='layers') + ring(*icon_pos('layers'), 18)
    s += ring(550 + 224 - 22, row_y(1) + 1, 15) + badge(550 + 224 - 22, row_y(1) + 34, 1)
    s += label(552, 260, '① 点掉「背景颜色」的勾', YEL1, 14)
    s += label(552, 292, '画布上透明的地方', WHITE, 14)
    s += label(552, 324, '显示成灰白格子', WHITE, 14)
    s += label(552, 372, '再导出 PNG，透明会保留', MINT1, 14)
    s += note('示意图')
    save('u-bg-hide', svg(W, H, s, '隐藏背景颜色图层，导出透明背景的 PNG'))


@reg
def u_gallery_batch():
    top, xs = gallery_top('分享', sel_mode=True)
    s = top
    names = ['雷电_01', '雷电_02', '雷电_03', '练习稿']
    for i in range(4):
        s += gthumb(46 + i * 182, 110, 150, 200, i % 3, names[i], tick=(i < 3))
    s += badge(xs['分享'], 84, 2)
    s += badge(46 + 150 + 4, 110 + 200 - 34, 1)
    s += label(46, 380, '① 点「选择」后，轻点要导出的作品，出现蓝色小勾', YEL1, 14)
    s += label(46, 414, '② 点右上角「分享」，选 JPEG，一次导出这几张', YEL1, 14)
    s += label(46, 448, '备份时同样的方法选「Procreate」格式', WHITE, 14)
    s += note('示意图：选择模式下顶部按钮以实际为准')
    save('u-gallery-batch', svg(W, H, frame_dark(s), '图库选择模式：勾选多张作品一起分享'))


@reg
def u_files_size():
    s = f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="#F8FAFC"/>'
    s += text(SX + 26, 54, '「文件」App · 我的 iPad › cos 修图备份', 18, 800, INK)
    s += f'<rect x="40" y="80" width="720" height="34" fill="#E2E8F0"/>' + text(56, 103, '名称', 14, 800, MUTED) + text(560, 103, '大小', 14, 800, MUTED) + text(680, 103, '种类', 14, 800, MUTED)
    files = [('雷电将军_20261021_03.procreate', '? MB', 'Procreate'), ('雷电将军_20261021_03.png', '? MB', 'PNG'),
             ('雷电将军_20261021_03.jpg', '? MB', 'JPEG')]
    for i, (n, sz, k) in enumerate(files):
        y = 114 + i * 56
        s += f'<line x1="40" y1="{y + 56}" x2="760" y2="{y + 56}" stroke="{LINE}"/>'
        s += f'<rect x="56" y="{y + 12}" width="30" height="34" rx="4" fill="{[VIO2, MINT1, YEL1][i]}" stroke="{INK}" stroke-width="1.5"/>'
        s += text(100, y + 35, n, 15, 700, INK) + text(560, y + 35, sz, 14, 700, VIO7) + text(680, y + 35, k, 14, 600, MUTED)
    s += ringrect(546, 120, 100, 160)
    s += badge(560, 300, 1)
    s += label(60, 360, '在「文件」App 右上角切换成「列表」显示，就能看到「大小」这一列', YEL1, 14)
    s += label(60, 394, '看不到时，长按文件，选「显示简介」', WHITE, 14)
    s += label(60, 440, '一般规律：PNG 比 JPEG 大好几倍；.procreate 随图层数变大', MINT1, 14)
    s += note('示意图：iPadOS「文件」App，界面以你的系统版本为准')
    save('u-files-size', svg(W, H, s, '在文件 App 里比较三种格式的文件大小'))


@reg
def p_import_insert():
    Wd, Hd = 760, 360
    s = []
    for col, (title, sub, fill) in enumerate([('图库 › 照片 / 导入', '用照片新建一个画布', MINT1), ('操作 › 添加 › 插入照片', '放进已经打开的画布', YEL1)]):
        ox = 20 + col * 380
        s.append(card(ox, 10, 360, 340))
        s.append(label(ox + 16, 44, title, fill, 15))
        s.append(text(ox + 18, 78, sub, 14, 700, MUTED))
    # 左：照片 → 同尺寸画布
    s.append(f'<rect x="50" y="100" width="120" height="160" fill="#FFF7E6" stroke="{INK}" stroke-width="2.5"/>')
    s.append(text(110, 282, '照片 3000×4000', 13, 700, INK, 'middle'))
    s.append(arrow(178, 180, 222, 180, INK, 3))
    s.append(f'<rect x="230" y="100" width="120" height="160" fill="#FFF7E6" stroke="{VIO7}" stroke-width="3.5"/>')
    s.append(text(290, 282, '画布 3000×4000', 13, 800, VIO7, 'middle'))
    s.append(text(40, 318, '画布和照片一样大，一个像素都不少。', 14, 700))
    s.append(text(40, 340, '修一张照片，用这个。', 14, 800, MINT7))
    # 右：插入到小画布
    ox = 400
    s.append(f'<rect x="{ox + 30}" y="100" width="150" height="200" fill="#FFF7E6" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    s.append(text(ox + 105, 316, '照片 3000×4000', 12, 700, MUTED, 'middle'))
    s.append(arrow(ox + 186, 200, ox + 222, 200, INK, 3))
    s.append(f'<rect x="{ox + 230}" y="120" width="120" height="160" fill="{WHITE}" stroke="{VIO7}" stroke-width="3.5"/>')
    s.append(f'<rect x="{ox + 248}" y="140" width="84" height="112" fill="#FFF7E6" stroke="{INK}" stroke-width="2"/>')
    s.append(text(ox + 290, 296, '画布 1500×2000', 12, 800, VIO7, 'middle'))
    s.append(text(ox + 24, 334, '照片比画布大，会被缩到画布里，细节变少。', 13, 700, RED7))
    save('p-import-insert', svg(Wd, Hd, ''.join(s), '从图库导入会新建同尺寸画布；插入照片会放进当前画布，可能被缩小'))


@reg
def p_flatten():
    Wd, Hd = 760, 380
    s = [card(20, 10, 720, 360)]
    s.append(label(40, 46, '导出时发生了什么', YEL1, 15))
    # 左：图层叠
    names = [('光效', YEL), ('修补', MINT), ('人物', VIO2), ('背景', FLOOR)]
    for i, (n, c) in enumerate(names):
        x, y = 60 + i * 14, 80 + i * 40
        s.append(f'<path d="M{x} {y + 30} L{x + 120} {y + 30} L{x + 160} {y} L{x + 40} {y} Z" fill="{c}" fill-opacity=".85" stroke="{INK}" stroke-width="2"/>')
        s.append(text(x + 175, y + 22, n, 13, 700))
    s.append(text(60, 270, '.procreate / PSD：', 14, 800, VIO7))
    s.append(text(60, 292, '每一层都留着，能接着改', 14, 600))
    s.append(arrow(280, 160, 350, 160, INK, 3))
    s.append(text(315, 146, '压平', 14, 800, INK, 'middle'))
    # 右：一张
    s.append(f'<path d="M370 200 L520 200 L560 150 L410 150 Z" fill="{VIO1}" stroke="{INK}" stroke-width="2.5"/>')
    s.append(text(370, 240, 'PNG / JPEG / TIFF：', 14, 800, VIO7))
    s.append(text(370, 262, '所有看得见的图层合成一张', 14, 600))
    s.append(text(370, 284, '隐藏的图层不会导出', 14, 600, MUTED))
    # 透明对比
    s.append(checker(600, 70, 110, 80, 8, 'flchk'))
    s.append(f'<circle cx="655" cy="110" r="26" fill="{PINK}" stroke="{INK}" stroke-width="2"/><rect x="600" y="70" width="110" height="80" fill="none" stroke="{INK}" stroke-width="2"/>')
    s.append(text(655, 168, 'PNG：透明保留', 13, 800, MINT7, 'middle'))
    s.append(f'<rect x="600" y="190" width="110" height="80" fill="#FFFFFF" stroke="{INK}" stroke-width="2"/><circle cx="655" cy="230" r="26" fill="{PINK}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(655, 288, 'JPEG：透明变成纯色', 13, 800, RED7, 'middle'))
    s.append(text(40, 340, 'PNG 无损所以文件大；JPEG 有损压缩所以最小，但每存一次都会再损失一点。', 14, 600, MUTED))
    save('p-flatten', svg(Wd, Hd, ''.join(s), '导出 PNG、JPEG 会把可见图层压成一张；PNG 保留透明，JPEG 不保留'))


def sticker_case(png):
    Wd, Hd = 640, 520
    s = []
    if png:
        s.append(checker(20, 20, 600, 480, 16, 'stk'))
    else:
        s.append(f'<rect x="20" y="20" width="600" height="480" fill="#FFFFFF"/>')
    hh = 62; top = 70; feet = top + hh * 6.6
    s.append(figure(320, top, hh, top + hh * 3.6, feet, sw=3))
    # 贴纸白边
    s.append(f'<rect x="20" y="20" width="600" height="480" fill="none" stroke="{INK}" stroke-width="2"/>')
    lab = 'PNG：人物外面是透明的，能直接叠到别的图上' if png else 'JPEG：透明的地方被填成白色，抠好的图白抠了'
    s.append(label(606, 56, lab, VIO1, 15, 'end') if png else label(34, 56, lab, YEL1, 15))
    return svg(Wd, Hd, ''.join(s), lab)


# =====================================================================
# 1.2 手势和效率
# =====================================================================
def mini_hand(x, y, n, kind='tap'):
    s = []
    for i in range(n):
        fx = x + (i - (n - 1) / 2) * 18
        s.append(f'<ellipse cx="{fx:.1f}" cy="{y}" rx="7" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
        if kind == 'tap':
            s.append(f'<circle cx="{fx:.1f}" cy="{y}" r="13" fill="none" stroke="{YEL}" stroke-width="2.5" stroke-dasharray="3 3"/>')
        if kind == 'down':
            s.append(arrow(fx, y + 13, fx, y + 34, INK, 2.2))
    if kind == 'scrub':
        s.append(f'<path d="M{x - 28} {y + 22} l10 -7 l10 7 l10 -7 l10 7 l10 -7" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    return ''.join(s)


@reg
def p_gestures():
    Wd, Hd = 760, 560
    s = [card(10, 10, 740, 540)]
    items = [
        ('两指轻点', '撤销；按住不放连续撤销', ('tap', 2)), ('三指轻点', '重做', ('tap', 3)),
        ('两指捏合 / 张开', '缩小 / 放大画布', ('pinch', 0)), ('两指捏住转动', '旋转画布', ('rot', 0)),
        ('两指快速捏合', '画布适应屏幕', ('fast', 0)), ('三指往下滑', '打开「拷贝并粘贴」菜单', ('down', 3)),
        ('三指来回擦', '清除当前图层的内容', ('scrub', 3)), ('四指轻点', '全屏，隐藏界面', ('tap', 4)),
        ('手指按住画布', '吸管，取这里的颜色', ('hold', 1)), ('画完笔尖停住', '速创形状：变直线、正圆', ('shape', 0)),
    ]
    for i, (t, d, (k, n)) in enumerate(items):
        col, row = i % 2, i // 2
        x, y = 26 + col * 364, 26 + row * 104
        s.append(f'<rect x="{x}" y="{y}" width="348" height="92" rx="12" fill="{[VIO1, MINT1, YEL1, PINK1, WHITE][row]}" stroke="{INK}" stroke-width="2"/>')
        s.append(badge(x + 18, y + 20, i + 1))
        hx, hy = x + 64, y + 52
        if k in ('tap', 'down', 'scrub'):
            s.append(mini_hand(hx, hy - (10 if k == 'down' else 0), n, k))
        elif k == 'pinch':
            s.append(f'<ellipse cx="{hx - 26}" cy="{hy}" rx="7" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="2"/><ellipse cx="{hx + 26}" cy="{hy}" rx="7" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
            s.append(arrow(hx - 16, hy, hx - 4, hy, INK, 2.5) + arrow(hx + 16, hy, hx + 4, hy, INK, 2.5))
        elif k == 'fast':
            s.append(f'<ellipse cx="{hx - 26}" cy="{hy}" rx="7" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="2"/><ellipse cx="{hx + 26}" cy="{hy}" rx="7" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
            s.append(arrow(hx - 16, hy, hx - 4, hy, RED, 3.5, marker='arwr') + arrow(hx + 16, hy, hx + 4, hy, RED, 3.5, marker='arwr'))
            s.append(text(hx, hy - 18, '快', 13, 900, RED7, 'middle'))
        elif k == 'rot':
            s.append(f'<ellipse cx="{hx - 20}" cy="{hy + 8}" rx="7" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="2"/><ellipse cx="{hx + 20}" cy="{hy - 8}" rx="7" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
            s.append(f'<path d="M{hx - 26} {hy - 14} A28 28 0 0 1 {hx + 4} {hy - 26}" fill="none" stroke="{INK}" stroke-width="2.5" marker-end="url(#arw)"/>')
        elif k == 'hold':
            s.append(f'<ellipse cx="{hx}" cy="{hy}" rx="7" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
            s.append(f'<circle cx="{hx + 22}" cy="{hy - 14}" r="13" fill="{PINK}" stroke="{INK}" stroke-width="2"/><path d="M{hx + 9} {hy - 14} A13 13 0 0 0 {hx + 35} {hy - 14} Z" fill="{VIO}" stroke="{INK}" stroke-width="2"/>')
        elif k == 'shape':
            s.append(f'<path d="M{hx - 34} {hy + 12} q10 -14 22 -6 q12 8 24 -10" fill="none" stroke="{MUTED}" stroke-width="2.5" stroke-dasharray="4 3"/>')
            s.append(f'<line x1="{hx - 34}" y1="{hy + 18}" x2="{hx + 16}" y2="{hy - 10}" stroke="{INK}" stroke-width="3"/><circle cx="{hx + 16}" cy="{hy - 10}" r="5" fill="{YEL}" stroke="{INK}" stroke-width="2"/>')
        s.append(text(x + 120, y + 40, t, 17, 800))
        s.append(text(x + 120, y + 68, d, 14, 600, MUTED))
    save('p-gestures', svg(Wd, Hd, ''.join(s), '修图最常用的 10 个手势'))


@reg
def p_undo():
    Wd, Hd = 760, 300
    s = [card(20, 10, 720, 280)]
    s.append(label(40, 46, '撤销记录是怎么存的', YEL1, 15))
    steps = ['导入', '复制图层', '画笔', '画笔', '变换', '画笔']
    for i, t in enumerate(steps):
        x = 70 + i * 92
        fill = VIO1 if i < 4 else (MINT1 if i == 4 else WHITE)
        s.append(f'<rect x="{x - 36}" y="80" width="72" height="44" rx="10" fill="{fill}" stroke="{INK}" stroke-width="2"/>' + text(x, 108, t, 14, 700, INK, 'middle'))
        if i:
            s.append(f'<line x1="{x - 56}" y1="102" x2="{x - 38}" y2="102" stroke="{INK}" stroke-width="2.5"/>')
    s.append(f'<path d="M{70 + 5 * 92} 132 q-46 40 -92 0" fill="none" stroke="{VIO7}" stroke-width="3" marker-end="url(#arwv)"/>')
    s.append(text(70 + 4.5 * 92, 172, '两指轻点：退一步', 13, 800, VIO7, 'middle'))
    s.append(text(70 + 4 * 92, 196, '变换里拖了很多下，退出后只算一步', 12, 600, MUTED, 'middle'))
    # 回图库
    s.append(f'<rect x="618" y="74" width="104" height="56" rx="12" fill="{RED1}" stroke="{RED}" stroke-width="2.5"/>' + text(670, 98, '回到图库', 14, 800, RED7, 'middle') + text(670, 118, '或退出 App', 12, 700, RED7, 'middle'))
    s.append(f'<line x1="40" y1="230" x2="720" y2="230" stroke="{RED}" stroke-width="3" stroke-dasharray="8 6"/>')
    s.append(text(40, 258, '最多能撤销 250 步。回到图库或退出 Procreate 后，这条记录整条清空，之前的操作再也撤不回来。', 14, 700, RED7))
    s.append(text(40, 280, '所以：重要的一步之前先复制图层；擦掉、合并之前想清楚。', 14, 600, MUTED))
    save('p-undo', svg(Wd, Hd, ''.join(s), '撤销记录：最多 250 步，回到图库后清空'))


def stroke_on(ph):
    return ph + f'<path d="M{CX + 60} {CY + 120} q40 -30 80 10 q30 30 70 -5" fill="none" stroke="{RED}" stroke-width="7" stroke-linecap="round"/>'


@reg
def u_undo():
    ph, g = photo()
    s = screen(stroke_on(ph) + tap_fingers(CX + CW / 2, CY + 230, 2) + notice('撤销 ……'))
    s += badge(CX + CW / 2 + 40, CY + 210, 1)
    s += label(552, 150, '① 两根手指同时轻点画布', YEL1, 14)
    s += label(552, 182, '　 手指并拢、分开都可以', WHITE, 13)
    s += label(552, 222, '上方会提示撤销了什么', YEL1, 14)
    s += label(552, 262, '两指按住不放：一步步连续撤销', YEL1, 14)
    s += label(552, 302, '三指轻点：重做', MINT1, 14)
    s += note('示意图')
    save('u-undo', svg(W, H, s, '两指轻点撤销，三指轻点重做'))


@reg
def u_fit():
    # 放大后的画布（只露出一部分）
    big = f'<defs><clipPath id="fitclip"><rect x="{SX}" y="{SY + 42}" width="{SW}" height="{SH - 42}"/></clipPath></defs>'
    ph, g = scene(120, -40, 560, 690)
    content = big + f'<g clip-path="url(#fitclip)">{ph}</g>' + pinch(400, 300, True, 70, False)
    s = screen(content)
    s += label(470, 380, '两指快速捏合，马上松手', YEL1, 14)
    s += label(470, 412, '画布会刚好铺满屏幕，看到整张图', YEL1, 14)
    # 小图：结果
    rx, ry = 600, 90
    s += f'<rect x="{rx}" y="{ry}" width="160" height="120" rx="10" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'
    s += f'<rect x="{rx + 56}" y="{ry + 10}" width="48" height="100" fill="#FFF7E6" stroke="{INK}" stroke-width="1.5"/>' + text(rx + 80, ry + 138, '松手后', 13, 800, INK, 'middle')
    s += note('示意图：反方向快速张开，回到捏合前的大小')
    save('u-fit', svg(W, H, s, '两指快速捏合，让画布适应屏幕'))


@reg
def u_copypaste():
    ph, g = photo()
    items = ['剪切', '拷贝', '全部拷贝', '复制', '剪切并粘贴', '粘贴']
    bx, by = 150, 64
    bar = f'<rect x="{bx}" y="{by}" width="500" height="46" rx="12" fill="{UIBAR}"/>'
    xx = bx + 12
    pos = {}
    for it in items:
        w = len(it) * 15 + 22
        bar += f'<rect x="{xx}" y="{by + 7}" width="{w}" height="32" rx="8" fill="{UIPANEL}"/>' + text(xx + w / 2, by + 29, it, 14, 700, UITEXT, 'middle')
        pos[it] = xx + w / 2
        xx += w + 6
    s = screen(ph + bar + finger(CX + CW / 2, CY + 190, 3, 44))
    s += ringrect(bx - 3, by - 3, 506, 52)
    s += badge(CX + CW / 2 - 50, CY + 180, 1)
    s += label(552, 230, '① 三指放在画布上，一起往下滑', YEL1, 14)
    defs = [('拷贝', '复制到剪贴板'), ('复制', '直接复制成一个新图层'), ('剪切并粘贴', '挖出来放到新图层'), ('全部拷贝', '所有可见图层合成一张拷贝')]
    s += f'<rect x="552" y="262" width="222" height="{len(defs) * 46 + 12}" rx="12" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'
    for i, (k, d) in enumerate(defs):
        yy = 288 + i * 46
        s += text(564, yy, k, 14, 800, VIO7) + text(564, yy + 20, d, 12, 600, MUTED)
    s += note('示意图：有选区时只处理选区里的内容')
    save('u-copypaste', svg(W, H, s, '三指下滑打开拷贝并粘贴菜单'))


@reg
def u_scrub():
    ph, g = photo()
    s = screen(stroke_on(ph) + scrub(CX + CW / 2, CY + 240) + notice('清除 ……'))
    s += badge(CX + CW / 2 + 60, CY + 222, 1)
    s += label(552, 160, '① 三指贴着画布，左右来回擦', YEL1, 14)
    s += label(552, 196, '当前图层上的东西全部清空', RED1, 14)
    s += label(552, 236, '只清当前这一层，其他层不动', WHITE, 14)
    s += label(552, 276, '清错了：马上两指轻点撤销', MINT1, 14)
    s += note('示意图')
    save('u-scrub', svg(W, H, s, '三指来回擦，清除当前图层'))


@reg
def u_fullscreen():
    s = f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="{GRAY_BG}"/>'
    ph, g = scene(240, 30, 320, 500)
    s += ph + tap_fingers(400, 300, 4)
    s += f'<rect x="{SX + 12}" y="{SY + 12}" width="34" height="34" rx="8" fill="{UIBAR}"/><path d="M{SX + 20} {SY + 30} v-10 h10 M{SX + 38} {SY + 24} v10 h-10" fill="none" stroke="{UITEXT}" stroke-width="2.5"/>'
    s += ring(SX + 29, SY + 29, 22) + badge(SX + 62, SY + 30, 2)
    s += badge(400, 268, 1)
    s += label(574, 180, '① 四指同时轻点：', YEL1, 14)
    s += label(574, 212, '　 工具栏和侧栏全部藏起来', YEL1, 14)
    s += label(574, 260, '② 再四指轻点，或点', YEL1, 14)
    s += label(574, 292, '　 左上角这个小图标，退出', YEL1, 14)
    s += label(574, 340, '修完看整体效果时用', WHITE, 14)
    s += note('示意图')
    save('u-fullscreen', svg(W, H, s, '四指轻点进入全屏'))


@reg
def u_eyedrop():
    ph, g = photo()
    ex, ey = g['cx'] + 10, g['top'] + g['hh'] * 2.0
    drop = (f'<circle cx="{ex}" cy="{ey - 50}" r="34" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'
            f'<path d="M{ex - 30} {ey - 50} A30 30 0 0 1 {ex + 30} {ey - 50} Z" fill="{VIO2}"/>'
            f'<path d="M{ex - 30} {ey - 50} A30 30 0 0 0 {ex + 30} {ey - 50} Z" fill="{PINK}"/>'
            f'<circle cx="{ex}" cy="{ey - 50}" r="30" fill="none" stroke="{INK}" stroke-width="2"/>'
            f'<ellipse cx="{ex}" cy="{ey}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
    s = screen(ph + drop)
    s += badge(ex + 44, ey - 70, 1)
    s += ring(39, 277, 20) + badge(39, 316, 2)
    s += label(552, 150, '① 手指按住画布不动，出现吸管', YEL1, 14)
    s += label(552, 182, '　 上半圈：正在取的新颜色', WHITE, 13)
    s += label(552, 212, '　 下半圈：当前颜色', WHITE, 13)
    s += label(552, 244, '　 拖到要取的地方，松手就选中', YEL1, 14)
    s += label(552, 296, '② 也可以点一下侧栏的方块', YEL1, 14)
    s += label(552, 328, '　（修改钮），再点画布取色', YEL1, 14)
    s += label(552, 376, '取不到：去手势控制里看吸管设置', RED1, 13)
    s += note('示意图')
    save('u-eyedrop', svg(W, H, s, '长按画布或用修改钮取色'))


@reg
def u_gesture_ctrl():
    s = f'<rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="{GRAY_BG}"/>' + topbar('actions')
    px, py, pw, ph = 100, 62, 600, 456
    s += panel(px, py, pw, ph) + text(px + pw / 2, py + 30, '手势控制', 18, 800, UITEXT, 'middle') + text(px + pw - 20, py + 30, '完成', 16, 800, UIBLUE, 'end')
    cats = ['常规', '涂抹', '擦除', '辅助绘图', '吸管', '速创形状', '速选菜单', '全屏', '清除图层', '拷贝并粘贴', '图层选择']
    for i, t in enumerate(cats):
        y = py + 50 + i * 35
        s += f'<rect x="{px + 10}" y="{y}" width="150" height="30" rx="7" fill="{UIBLUE if t == "吸管" else UIBAR}"/>' + text(px + 22, y + 21, t, 14, 700, UITEXT)
    rows = ['轻点 □', '触摸并按住', '□ + 触摸', '□ + Apple Pencil', 'Apple Pencil 轻点两下']
    s += menu_rows(px + 170, py + 50, pw - 180, rows, row_h=44,
                   toggles={'轻点 □': True, '触摸并按住': True, '□ + 触摸': True, '□ + Apple Pencil': False, 'Apple Pencil 轻点两下': False})
    s += slider(px + 190, py + 300, 360, '延迟', 0.3)
    s += ring(*icon_pos('actions'), 18)
    s += badge(px + 146, py + 50 + 4 * 35 + 15, 1)
    s += ringrect(px + 176, py + 50 + 44 + 3, pw - 192, 38) + badge(px + pw - 4, py + 50 + 44 + 22, 2)
    s += label(px + 180, py + 360, '① 左边选一类功能，右边是能触发它的手势', YEL1, 14)
    s += label(px + 180, py + 392, '② 打开开关就能用；「□」是侧栏的修改钮', YEL1, 14)
    s += label(px + 180, py + 424, '两个功能抢同一个手势时，会出现黄色警告', RED1, 14)
    s += note('示意图：操作 › 偏好设置 › 手势控制；具体选项以实际界面为准')
    save('u-gesture-ctrl', svg(W, H, s, '手势控制：每类功能可以选用哪些手势'))


@reg
def u_slider_fine():
    ph, g = photo()
    s = screen(ph)
    # 按住尺寸滑块 → 手指往右拖开再上下
    fx, fy = 39, 205
    s += f'<ellipse cx="{fx + 120}" cy="{fy}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>'
    s += arrow(fx + 14, fy, fx + 106, fy, INK, 2.5, '5 4')
    s += arrow(fx + 120, fy - 16, fx + 120, fy - 60, INK, 3) + arrow(fx + 120, fy + 16, fx + 120, fy + 60, INK, 3)
    s += ring(fx, fy, 18) + badge(fx + 26, fy - 30, 1)
    # 预览窗
    s += f'<rect x="72" y="300" width="150" height="98" rx="12" fill="{UIPANEL}" stroke="#111827"/>' + text(88, 326, '尺寸', 14, 700, UITEXT) + text(206, 326, '12%', 14, 800, WHITE, 'end')
    s += f'<circle cx="147" cy="362" r="18" fill="{INK}" stroke="{UITEXT}" stroke-width="1.5"/>' + text(206, 352, '+', 22, 800, UITEXT, 'end')
    s += ring(200, 345, 14) + badge(234, 345, 2)
    s += label(552, 150, '① 按住滑块，手指先往旁边拖开，', YEL1, 14)
    s += label(552, 182, '　 再上下移：离得越远调得越细', YEL1, 14)
    s += label(552, 230, '② 按住时弹出预览，点「+」', YEL1, 14)
    s += label(552, 262, '　 存下这个数值，以后一点就回来', YEL1, 14)
    s += label(552, 294, '　 每支笔尺寸、不透明度各存 4 个', WHITE, 13)
    s += note('示意图')
    save('u-slider-fine', svg(W, H, s, '精准调滑块，保存常用的尺寸和不透明度'))


# =====================================================================
# 1.3 画笔、涂抹和擦除
# =====================================================================
@reg
def p_brush_edge():
    Wd, Hd = 760, 420
    s = []
    defs = ('<defs><radialGradient id="softdot"><stop offset="0" stop-color="#8B5CF6" stop-opacity="1"/>'
            '<stop offset=".45" stop-color="#8B5CF6" stop-opacity=".55"/><stop offset="1" stop-color="#8B5CF6" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="softpink"><stop offset="0" stop-color="#F472B6" stop-opacity=".55"/><stop offset="1" stop-color="#F472B6" stop-opacity="0"/></radialGradient></defs>')
    s.append(defs)
    for col, (title, soft, fill) in enumerate([('硬边笔刷：边缘一刀切', False, RED1), ('软边笔刷：边缘慢慢变淡', True, MINT1)]):
        ox = 20 + col * 380
        s.append(card(ox, 10, 360, 400))
        s.append(label(ox + 16, 44, title, fill, 15))
        # 笔触
        cx, cy = ox + 90, 130
        if soft:
            s.append(f'<circle cx="{cx}" cy="{cy}" r="46" fill="url(#softdot)"/>')
        else:
            s.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="{VIO}"/>')
        s.append(text(cx, 200, '一笔点下去', 13, 700, MUTED, 'middle'))
        # 剖面图
        gx, gy, gw, gh = ox + 170, 80, 170, 100
        s.append(f'<line x1="{gx}" y1="{gy + gh}" x2="{gx + gw}" y2="{gy + gh}" stroke="{INK}" stroke-width="2"/><line x1="{gx}" y1="{gy}" x2="{gx}" y2="{gy + gh}" stroke="{INK}" stroke-width="2"/>')
        if soft:
            pts = ' '.join(f'{gx + gw * k / 40:.1f},{gy + gh - gh * 0.95 * math.exp(-((k - 20) / 8.5) ** 2):.1f}' for k in range(41))
            s.append(f'<polyline points="{pts}" fill="none" stroke="{VIO7}" stroke-width="3"/>')
        else:
            s.append(f'<polyline points="{gx},{gy + gh} {gx + 50},{gy + gh} {gx + 50},{gy + 5} {gx + 120},{gy + 5} {gx + 120},{gy + gh} {gx + gw},{gy + gh}" fill="none" stroke="{VIO7}" stroke-width="3"/>')
        s.append(text(gx + gw / 2, gy + gh + 20, '从左到右的浓淡', 12, 700, MUTED, 'middle'))
        # 脸颊上补色
        fx, fy = ox + 180, 300
        s.append(f'<ellipse cx="{fx}" cy="{fy}" rx="150" ry="70" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
        if soft:
            for dx, dy in [(-40, -6), (0, 6), (40, -4), (14, -20)]:
                s.append(f'<circle cx="{fx + dx}" cy="{fy + dy}" r="44" fill="url(#softpink)"/>')
            s.append(text(fx, fy + 98, '叠几笔，过渡还是顺的', 14, 800, MINT7, 'middle'))
        else:
            for dx, dy in [(-40, -6), (0, 6), (40, -4), (14, -20)]:
                s.append(f'<circle cx="{fx + dx}" cy="{fy + dy}" r="28" fill="{PINK}" fill-opacity=".28"/>')
            s.append(text(fx, fy + 98, '每一笔的边都看得见，一块一块的', 14, 800, RED7, 'middle'))
    save('p-brush-edge', svg(Wd, Hd, ''.join(s), '硬边和软边笔刷的区别：软边笔刷叠几笔过渡仍然顺'))


@reg
def p_opacity_stack():
    Wd, Hd = 760, 320
    s = [card(20, 10, 720, 300)]
    s.append(label(40, 46, '同一个颜色、25% 不透明度，抬笔再叠：', YEL1, 15))
    vals = []
    for n in range(1, 5):
        vals.append(1 - (1 - 0.25) ** n)
    for i, v in enumerate(vals):
        x = 60 + i * 170
        s.append(checker(x, 80, 120, 120, 10, f'op{i}'))
        s.append(f'<rect x="{x}" y="80" width="120" height="120" fill="{VIO}" fill-opacity="{v:.3f}" stroke="{INK}" stroke-width="2"/>')
        s.append(text(x + 60, 226, f'叠 {i + 1} 笔', 15, 800, INK, 'middle'))
        s.append(text(x + 60, 250, f'≈ {v * 100:.0f}%', 18, 900, VIO7, 'middle'))
    s.append(text(40, 290, '不是 25% + 25% = 50%：每一笔只盖住剩下的 25%，越往后加得越少。所以低不透明度多叠几笔，深浅最好控制。', 13, 600, MUTED))
    save('p-opacity-stack', svg(Wd, Hd, ''.join(s), '低不透明度叠加：25% 叠两笔约 44%，不是 50%'))


@reg
def p_stabilize():
    Wd, Hd = 760, 300
    s = []
    import random
    random.seed(7)
    for col, (title, fill) in enumerate([('手画的线：有小抖动', RED1), ('开了流线：抖动被抹平', MINT1)]):
        ox = 20 + col * 380
        s.append(card(ox, 10, 360, 280))
        s.append(label(ox + 16, 44, title, fill, 15))
        pts = []
        for k in range(61):
            t = k / 60
            x = ox + 40 + t * 280
            y = 170 - math.sin(t * math.pi) * 80
            if col == 0:
                y += random.uniform(-6, 6)
            pts.append((x, y))
        s.append('<polyline points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts) + f'" fill="none" stroke="{INK}" stroke-width="3.5" stroke-linejoin="round"/>')
        if col == 1:
            # 笔尖跑在前面，线被"拉"着走
            px_, py_ = ox + 330, 120
            s.append(f'<line x1="{pts[-1][0]:.1f}" y1="{pts[-1][1]:.1f}" x2="{px_}" y2="{py_}" stroke="{VIO7}" stroke-width="2" stroke-dasharray="4 4"/>')
            s.append(f'<circle cx="{px_}" cy="{py_}" r="7" fill="{YEL}" stroke="{INK}" stroke-width="2"/>')
            s.append(text(px_ - 6, py_ - 14, '笔尖', 12, 800, INK, 'end'))
            s.append(text(ox + 30, 236, '线像被绳子拉着跟在笔尖后面，', 13, 700))
            s.append(text(ox + 30, 258, '数值越大越顺，但越"拖"、转角越圆。', 13, 700, MUTED))
        else:
            s.append(text(ox + 30, 236, '画发丝、眼线这种又细又长的线，', 13, 700))
            s.append(text(ox + 30, 258, '手抖会直接留在线上。', 13, 700, MUTED))
    save('p-stabilize', svg(Wd, Hd, ''.join(s), '流线和稳定性：把手抖平均掉，代价是线条跟得慢一点'))


def brush_lib(x, y, groups, hl_group, brushes, hl_brush, swiped=None):
    w, h = 470, 60 + max(len(groups), len(brushes)) * 44
    s = panel(x, y, w, h) + text(x + 18, y + 30, '画笔库', 17, 800, UITEXT) + text(x + w - 22, y + 30, '+', 24, 700, UITEXT, 'middle')
    for i, gname in enumerate(groups):
        yy = y + 48 + i * 40
        s += f'<rect x="{x + 10}" y="{yy}" width="150" height="34" rx="8" fill="{UIBLUE if gname == hl_group else UIBAR}"/>' + text(x + 22, yy + 23, gname, 14, 700, UITEXT)
    for i, b in enumerate(brushes):
        yy = y + 48 + i * 52
        sel = b == hl_brush
        s += f'<rect x="{x + 170}" y="{yy}" width="{w - 180}" height="46" rx="8" fill="{UIBLUE if sel else UIBAR}"/>'
        s += text(x + 184, yy + 19, b, 14, 800, UITEXT)
        soft = '软' in b or '气笔' in b
        if soft:
            s += f'<path d="M{x + 184} {yy + 34} q60 -10 130 0 t110 0" fill="none" stroke="{UITEXT}" stroke-width="9" stroke-linecap="round" stroke-opacity=".35"/>'
            s += f'<path d="M{x + 184} {yy + 34} q60 -10 130 0 t110 0" fill="none" stroke="{UITEXT}" stroke-width="4" stroke-linecap="round" stroke-opacity=".6"/>'
        else:
            s += f'<path d="M{x + 184} {yy + 34} q60 -10 130 0 t110 0" fill="none" stroke="{UITEXT}" stroke-width="5" stroke-linecap="round"/>'
        if swiped == b:
            bx = x + w - 10 - 186
            for j, (t, col) in enumerate([('分享', '#4B5563'), ('复制', '#2563EB'), ('删除', '#DC2626')]):
                s += f'<rect x="{bx + j * 62}" y="{yy}" width="62" height="46" fill="{col}"/>' + text(bx + j * 62 + 31, yy + 28, t, 14, 700, WHITE, 'middle')
            s += ringrect(bx + 64, yy + 2, 58, 42, 6)
    return s


@reg
def u_brush_lib():
    ph, g = photo()
    groups = ['最近', '素描', '着墨', '绘图', '上漆', '艺术效果', '书法', '气笔修饰']
    lib = brush_lib(300, 62, groups, '气笔修饰', ['软画笔', '中等画笔', '中等硬画笔', '硬画笔', '软气笔', '中等气笔'], '软画笔')
    s = screen(ph + lib, active='brush') + ring(*icon_pos('brush'), 18)
    s += badge(icon_pos('brush')[0], 66, 1) + badge(300 + 152, 62 + 48 + 7 * 40 + 17, 2) + badge(300 + 470 - 18, 62 + 48 + 23, 3)
    s += label(36, 520, '① 点画笔图标（已选中时再点一次）打开画笔库 ② 左边选组 ③ 右边选笔', YEL1, 14)
    s += note('示意图：新版先进「经典库」')
    save('u-brush-lib', svg(W, H, s, '画笔库：气笔修饰里的软画笔'))


@reg
def u_brush_dup():
    ph, g = photo()
    groups = ['最近', '素描', '着墨', '绘图', '上漆', '艺术效果', '书法', '气笔修饰']
    lib = brush_lib(300, 62, groups, '着墨', ['技术笔', '工作室笔', '凝胶墨水笔', '干油墨', '墨水渗流'], '工作室笔', swiped='工作室笔')
    s = screen(ph + lib, active='brush') + ring(*icon_pos('brush'), 18)
    s += label(330, 470, '在要改的笔上向左轻扫，点「复制」，只改复制出来的那支', YEL1, 14)
    s += label(330, 502, '改坏了：画笔工作室 › 关于此画笔 › 重置画笔', WHITE, 14)
    s += note('示意图：按钮顺序以实际界面为准')
    save('u-brush-dup', svg(W, H, s, '先复制一支笔，再改复制出来的那支'))


@reg
def u_sidebar_brush():
    ph, g = photo()
    strokes = (f'<path d="M{CX + 40} {CY + 300} q60 -40 120 -10 t100 -20" fill="none" stroke="{PINK}" stroke-width="16" stroke-linecap="round" stroke-opacity=".35"/>'
               f'<path d="M{CX + 40} {CY + 270} q60 -40 120 -10 t100 -20" fill="none" stroke="{PINK}" stroke-width="6" stroke-linecap="round" stroke-opacity=".9"/>')
    s = screen(ph + strokes, active='brush')
    s += ringrect(28, 160, 22, 102, 10) + badge(70, 210, 1)
    s += ringrect(28, 292, 22, 102, 10) + badge(70, 343, 2)
    s += label(86, 200, '① 尺寸：往上大，往下小', YEL1, 14)
    s += label(86, 334, '② 不透明度：往上实，往下淡', YEL1, 14)
    s += label(552, 150, '同一支笔：', WHITE, 14)
    s += label(552, 182, '轻轻画 → 细、淡', YEL1, 14)
    s += label(552, 214, '用力画 → 粗、深（有压感时）', YEL1, 14)
    s += label(552, 262, '修图常用：尺寸调大、', MINT1, 14)
    s += label(552, 294, '不透明度 5%～20%', MINT1, 14)
    s += note('示意图')
    save('u-sidebar-brush', svg(W, H, s, '侧栏的两个滑块：尺寸和不透明度'))


@reg
def u_brush_studio():
    s = f'<rect x="0" y="0" width="{W}" height="{H}" rx="30" fill="{INK}"/><rect x="{SX}" y="{SY}" width="{SW}" height="{SH}" rx="16" fill="{UIPANEL}"/>'
    s += text(SX + 20, 46, '画笔工作室', 18, 800, UITEXT) + text(SX + SW - 20, 46, '完成', 16, 800, UIBLUE, 'end') + text(SX + SW - 80, 46, '取消', 16, 700, UITEXT, 'end')
    props = ['描边路径', '稳定性', '锥度', '形状', '颗粒', '渲染', '湿混', '颜色动态', '动态', 'Apple Pencil', '属性', '材质', '关于此画笔']
    for i, p in enumerate(props):
        y = 66 + i * 35
        s += f'<rect x="{SX + 10}" y="{y}" width="150" height="30" rx="7" fill="{UIBLUE if p == "稳定性" else UIBAR}"/>' + text(SX + 22, y + 21, p, 14, 700, UITEXT)
    mx = 190
    s += text(mx, 86, '流线', 15, 800, UITEXT)
    s += slider(mx + 10, 118, 240, '数量', 0.35, hl=True) + slider(mx + 10, 168, 240, '压力', 0.2)
    s += text(mx, 214, '稳定性', 15, 800, UITEXT) + slider(mx + 10, 246, 240, '数量', 0.0)
    s += text(mx, 292, '动作过滤', 15, 800, UITEXT) + slider(mx + 10, 324, 240, '数量', 0.0) + slider(mx + 10, 374, 240, '表现', 0.0)
    # 绘图板
    s += f'<rect x="470" y="66" width="306" height="320" rx="10" fill="{WHITE}"/>' + text(484, 88, '绘图板', 13, 800, MUTED)
    s += f'<path d="M500 330 C540 150 620 120 740 110" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>'
    s += f'<path d="M520 360 C570 200 650 170 750 160" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>'
    s += ringrect(SX + 8, 66 + 35 - 2, 154, 34) + badge(SX + 172, 66 + 35 + 15, 1)
    s += badge(mx + 268, 118, 2)
    s += label(190, 440, '① 左边点「稳定性」 ② 先只调「流线」的「数量」，在右边绘图板上试画', YEL1, 14)
    s += label(190, 474, '画发丝从 30% 左右试起；觉得线"拖"、跟不上手，就往回调', WHITE, 14)
    s += note('示意图：在画笔库里点一下已选中的笔进入；属性列表以实际界面为准')
    save('u-brush-studio', svg(W, H, s, '画笔工作室：稳定性里的流线、稳定性、动作过滤'))


@reg
def u_smudge():
    content = (f'<defs><linearGradient id="smg" x1="0" x2="1"><stop offset="0" stop-color="{VIO2}"/><stop offset="1" stop-color="{PINK1}"/></linearGradient></defs>'
               f'<rect x="{CX}" y="{CY}" width="{CW / 2}" height="{CH}" fill="{VIO2}"/><rect x="{CX + CW / 2}" y="{CY}" width="{CW / 2}" height="{CH}" fill="{PINK1}"/>'
               f'<rect x="{CX + CW / 2 - 40}" y="{CY + 170}" width="80" height="{CH - 170}" fill="url(#smg)"/>'
               f'<path d="M{CX + CW / 2 - 30} {CY + 200} q30 20 60 0 M{CX + CW / 2 - 30} {CY + 240} q30 20 60 0 M{CX + CW / 2 - 30} {CY + 280} q30 20 60 0" fill="none" stroke="{INK}" stroke-width="2" stroke-dasharray="4 4"/>'
               f'<line x1="{CX + CW / 2}" y1="{CY}" x2="{CX + CW / 2}" y2="{CY + 170}" stroke="{INK}" stroke-width="1"/>')
    s = screen(content, active='smudge') + ring(*icon_pos('smudge'), 18) + badge(icon_pos('smudge')[0], 66, 1)
    s += label(CX + 8, CY + 40, '上半：两块颜色硬接在一起', WHITE, 13)
    s += label(CX + 8, CY + 160, '下半：涂抹后变成过渡', MINT1, 13)
    s += ringrect(28, 292, 22, 102, 10) + badge(70, 343, 2)
    s += label(552, 160, '① 点手指图标（涂抹）', YEL1, 14)
    s += label(552, 192, '　 笔刷也选「软画笔」', YEL1, 14)
    s += label(552, 240, '② 不透明度就是涂抹的力度', YEL1, 14)
    s += label(552, 272, '　 从 20%～40% 起', YEL1, 14)
    s += label(552, 320, '沿着交界来回轻推，', WHITE, 14)
    s += label(552, 352, '别在有纹理的皮肤上大面积推', RED1, 14)
    s += note('示意图')
    save('u-smudge', svg(W, H, s, '涂抹工具：用软画笔低力度融合交界'))


@reg
def u_erase_hold():
    ph, g = photo()
    hx, hy = icon_pos('erase')
    s = screen(ph + notice('当前画笔已用于擦除（示意）', 400, 80), active='erase')
    s += ring(hx, hy, 20) + f'<ellipse cx="{hx}" cy="{hy + 30}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>' + badge(hx - 30, hy + 32, 1)
    s += label(440, 170, '① 正在用软画笔画时，长按橡皮图标', YEL1, 14)
    s += label(440, 202, '　 橡皮就换成同一支软画笔', YEL1, 14)
    s += label(440, 250, '涂抹图标也能这样长按', WHITE, 14)
    s += label(440, 298, '这样画和擦的边缘软硬一致', MINT1, 14)
    s += note('示意图：提示文字以实际界面为准')
    save('u-erase-hold', svg(W, H, s, '长按擦除图标，让橡皮用当前画笔'))


def wig_head(after, x0=20, y0=20, w=600, h=480):
    s = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#FFF7E6"/>']
    cx, cy = 320, 300
    s.append(f'<path d="M{cx - 190} {cy + 200} Q{cx - 230} {cy - 40} {cx - 150} {cy - 170} Q{cx} {cy - 260} {cx + 150} {cy - 170} Q{cx + 230} {cy - 40} {cx + 190} {cy + 200} Z" fill="{PINK}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<ellipse cx="{cx}" cy="{cy + 20}" rx="120" ry="150" fill="{SKIN}" stroke="{INK}" stroke-width="3"/>')
    # 刘海
    s.append(f'<path d="M{cx - 135} {cy - 30} Q{cx - 120} {cy - 190} {cx} {cy - 190} Q{cx + 120} {cy - 190} {cx + 135} {cy - 30} '
             f'Q{cx + 90} {cy - 80} {cx + 60} {cy - 40} Q{cx + 40} {cy - 90} {cx + 10} {cy - 50} L{cx - 10} {cy - 50} Q{cx - 50} {cy - 100} {cx - 70} {cy - 40} Q{cx - 100} {cy - 90} {cx - 135} {cy - 30} Z" fill="{PINK}" stroke="{INK}" stroke-width="3"/>')
    # 刘海的稀疏缺口：露出网
    if not after:
        s.append(f'<path d="M{cx - 30} {cy - 50} Q{cx} {cy - 150} {cx + 30} {cy - 50} Z" fill="#E7D3C3" stroke="{INK}" stroke-width="2"/>')
        for k in range(5):
            yy = cy - 62 - k * 16
            hw = 24 - k * 5
            s.append(f'<line x1="{cx - hw}" y1="{yy}" x2="{cx + hw}" y2="{yy}" stroke="{MUTED}" stroke-width="1.5"/>')
        for k in (-12, 0, 12):
            s.append(f'<line x1="{cx + k}" y1="{cy - 52}" x2="{cx + k * 0.4:.1f}" y2="{cy - 120}" stroke="{MUTED}" stroke-width="1.5"/>')
    else:
        for dx, bend in [(-26, -8), (-16, 6), (-6, -5), (4, 7), (14, -6), (24, 5), (-20, 3), (10, -2)]:
            s.append(f'<path d="M{cx + dx * 0.5:.1f} {cy - 150} q{bend} 50 {dx:.1f} 100" fill="none" stroke="#9D174D" stroke-width="3" stroke-linecap="round"/>')
    for dx in (-45, 45):
        s.append(f'<ellipse cx="{cx + dx}" cy="{cy + 20}" rx="14" ry="18" fill="{INK}"/>')
    lab = '修之后：用工作室笔补了几根发丝，缺口被盖住' if after else '修之前：刘海中间稀了一块，看得到发网'
    s.append(f'<circle cx="{cx}" cy="{cy - 80}" r="48" fill="none" stroke="{YEL}" stroke-width="4" stroke-dasharray="8 5"/>')
    s.append(label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15))
    return svg(640, 520, ''.join(s), lab)


def cheek_case(after):
    s = ['<defs><radialGradient id="blush"><stop offset="0" stop-color="#F472B6" stop-opacity=".5"/><stop offset="1" stop-color="#F472B6" stop-opacity="0"/></radialGradient></defs>']
    s.append(f'<rect x="20" y="20" width="600" height="480" fill="#FFF7E6"/>')
    cx, cy = 320, 290
    s.append(f'<path d="M{cx - 200} {cy + 220} Q{cx - 250} {cy - 60} {cx - 160} {cy - 190} Q{cx} {cy - 280} {cx + 160} {cy - 190} Q{cx + 250} {cy - 60} {cx + 200} {cy + 220} Z" fill="{PINK}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<ellipse cx="{cx}" cy="{cy + 10}" rx="150" ry="180" fill="{SKIN}" stroke="{INK}" stroke-width="3"/>')
    for dx in (-55, 55):
        s.append(f'<ellipse cx="{cx + dx}" cy="{cy - 10}" rx="16" ry="20" fill="{INK}"/>')
        bx = cx + dx * 1.45
        if after:
            s.append(f'<ellipse cx="{bx}" cy="{cy + 60}" rx="62" ry="40" fill="url(#blush)"/>')
        else:
            for ddx, ddy in [(-18, -6), (10, 4), (22, -10)]:
                s.append(f'<circle cx="{bx + ddx}" cy="{cy + 60 + ddy}" r="22" fill="{PINK}" fill-opacity=".35"/>')
    s.append(f'<path d="M{cx - 20} {cy + 110} q20 14 40 0" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/>')
    lab = '修之后：软画笔 10% 叠几笔，腮红是散开的' if after else '修之前：用硬画笔点的腮红，一块一块的边'
    s.append(label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15))
    return svg(640, 520, ''.join(s), lab)


# =====================================================================
# 1.4 图层和混合模式
# =====================================================================
def hx2(c):
    c = c.lstrip('#')
    return [int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def rgb2hx(v):
    return '#' + ''.join(f'{max(0, min(255, round(x * 255))):02x}' for x in v)


def _lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def _clip(c):
    l = _lum(c); n = min(c); x = max(c)
    if n < 0:
        c = [l + (k - l) * l / (l - n) for k in c]
    if x > 1:
        c = [l + (k - l) * (1 - l) / (x - l) for k in c]
    return c


def _setlum(c, l):
    d = l - _lum(c)
    return _clip([k + d for k in c])


def _sat(c):
    return max(c) - min(c)


def _setsat(c, s):
    c = list(c); idx = sorted(range(3), key=lambda i: c[i]); mn, md, mx = idx
    if c[mx] > c[mn]:
        c[md] = (c[md] - c[mn]) * s / (c[mx] - c[mn]); c[mx] = s
    else:
        c[md] = c[mx] = 0
    c[mn] = 0
    return c


def blend(mode, top, base):
    a, b = hx2(top), hx2(base)
    if mode == '正常':
        r = a
    elif mode == '正片叠底':
        r = [x * y for x, y in zip(a, b)]
    elif mode == '滤色':
        r = [1 - (1 - x) * (1 - y) for x, y in zip(a, b)]
    elif mode == '添加':
        r = [min(1, x + y) for x, y in zip(a, b)]
    elif mode == '覆盖':
        r = [2 * x * y if y <= .5 else 1 - 2 * (1 - x) * (1 - y) for x, y in zip(a, b)]
    elif mode == '柔光':
        def sl(x, y):
            if x <= .5:
                return y - (1 - 2 * x) * y * (1 - y)
            d = ((16 * y - 12) * y + 4) * y if y <= .25 else math.sqrt(y)
            return y + (2 * x - 1) * (d - y)
        r = [sl(x, y) for x, y in zip(a, b)]
    elif mode == '颜色':
        r = _setlum(a, _lum(b))
    elif mode == '明度':
        r = _setlum(b, _lum(a))
    elif mode == '色相':
        r = _setlum(_setsat(a, _sat(b)), _lum(b))
    return rgb2hx(r)


def grad_bar(x, y, w, h, n, fn, stroke=True):
    s = ''
    for k in range(n):
        t = k / (n - 1)
        s += f'<rect x="{x + w * k / n:.2f}" y="{y}" width="{w / n + 0.6:.2f}" height="{h}" fill="{fn(t)}"/>'
    if stroke:
        s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="2"/>'
    return s


def gray(t):
    return rgb2hx([t, t, t])


@reg
def p_layer_stack():
    Wd, Hd = 760, 380
    s = [card(20, 10, 720, 360)]
    s.append(label(40, 46, '图层就像一叠透明胶片，从上往下看', YEL1, 15))
    layers = [('光效', 'glow'), ('阴影', 'shadow'), ('修补', 'patch'), ('原图', 'photo')]
    for i, (n, k) in enumerate(layers):
        x, y = 70 + i * 12, 78 + i * 62
        s.append(f'<path d="M{x} {y + 46} L{x + 180} {y + 46} L{x + 230} {y} L{x + 50} {y} Z" fill="{WHITE if k != "photo" else "#FFF7E6"}" fill-opacity="{1 if k == "photo" else .55}" stroke="{INK}" stroke-width="2"/>')
        if k == 'glow':
            s.append(f'<ellipse cx="{x + 150}" cy="{y + 22}" rx="26" ry="11" fill="{YEL}" opacity=".8"/>')
        if k == 'shadow':
            s.append(f'<ellipse cx="{x + 110}" cy="{y + 30}" rx="40" ry="9" fill="{VIO7}" opacity=".5"/>')
        if k == 'patch':
            s.append(f'<ellipse cx="{x + 80}" cy="{y + 20}" rx="18" ry="8" fill="{MINT}" opacity=".9"/>')
        if k == 'photo':
            s.append(f'<path d="M{x + 120} {y + 44} q-10 -20 0 -40 q10 20 0 40" fill="{VIO2}" stroke="{INK}" stroke-width="1.5"/>')
        s.append(text(x + 250, y + 30, n, 15, 800))
    s.append(arrow(420, 210, 480, 210, INK, 3))
    s.append(f'<rect x="500" y="80" width="210" height="210" rx="8" fill="#FFF7E6" stroke="{INK}" stroke-width="2.5"/>')
    s.append(f'<path d="M605 280 q-24 -60 0 -150 q24 90 0 150" fill="{VIO2}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<ellipse cx="610" cy="272" rx="70" ry="12" fill="{VIO7}" opacity=".35"/><circle cx="650" cy="120" r="26" fill="{YEL}" opacity=".7"/><ellipse cx="560" cy="190" rx="18" ry="10" fill="{MINT}" opacity=".9"/>')
    s.append(text(605, 314, '最后看到的画面', 14, 800, INK, 'middle'))
    s.append(text(40, 352, '上层有颜色的地方盖住下层，透明的地方透出下层。每层可以单独改、单独关掉、单独删除。', 13, 600, MUTED))
    save('p-layer-stack', svg(Wd, Hd, ''.join(s), '图层像一叠透明胶片'))


@reg
def p_blend_dark_light():
    Wd, Hd = 760, 520
    s = [card(20, 10, 720, 500)]
    top = '#E07A5F'
    bx, bw, bh = 180, 300, 40
    s.append(label(40, 46, '同一块颜色，放在一条从黑到白的渐变上面', YEL1, 15))
    rows = [('下层（照片）', lambda t: gray(t), ''), ('上层（色块）', lambda t: top, ''),
            ('正片叠底', lambda t: blend('正片叠底', top, gray(t)), '上 × 下：只会变暗，白色等于没画'),
            ('滤色', lambda t: blend('滤色', top, gray(t)), '反过来乘：只会变亮，黑色等于没画'),
            ('添加', lambda t: blend('添加', top, gray(t)), '上 + 下：比滤色更亮，亮部直接冲到白')]
    for i, (n, fn, note_) in enumerate(rows):
        y = 74 + i * 82
        s.append(text(40, y + 26, n, 15, 800, VIO7 if i >= 2 else INK))
        s.append(grad_bar(bx, y, bw, bh, 40, fn))
        if note_:
            s.append(wrap(bx + bw + 20, y + 16, note_, 13, 18, 700))
        if i == 1:
            s.append(f'<line x1="40" y1="{y + 62}" x2="720" y2="{y + 62}" stroke="{LINE}" stroke-width="2" stroke-dasharray="6 5"/>')
    s.append(text(40, 494, '例：下层 0.8、上层 0.5。正片叠底 0.8×0.5=0.4；滤色 1−0.2×0.5=0.9；添加 0.8+0.5→1（白）', 13, 600, MUTED))
    save('p-blend-dark-light', svg(Wd, Hd, ''.join(s), '正片叠底变暗，滤色和添加变亮'))


@reg
def p_blend_contrast():
    Wd, Hd = 760, 560
    s = [card(20, 10, 720, 540)]
    s.append(label(40, 46, '覆盖、柔光：以 50% 灰为分界，暗的压暗，亮的提亮', YEL1, 15))
    bx, bw, bh = 200, 280, 30
    s.append(text(40, 92, '下层（照片）', 14, 800))
    s.append(grad_bar(bx, 72, bw, bh, 40, gray))
    y = 120
    for mode in ('覆盖', '柔光'):
        s.append(text(40, y + 18, mode, 16, 900, VIO7))
        for j, (tv, tn) in enumerate([(0.25, '上层 25% 灰'), (0.5, '上层 50% 灰'), (0.75, '上层 75% 灰')]):
            yy = y + 30 + j * 44
            s.append(f'<rect x="120" y="{yy}" width="{bh}" height="{bh}" fill="{gray(tv)}" stroke="{INK}" stroke-width="2"/>')
            s.append(text(40, yy + 21, tn, 12, 700, MUTED))
            s.append(grad_bar(bx, yy, bw, bh, 40, lambda t, tv=tv: blend(mode, gray(tv), gray(t))))
        y += 30 + 3 * 44 + 18
    # 曲线
    gx, gy, gw, gh = 520, 120, 190, 190
    s.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<line x1="{gx}" y1="{gy + gh}" x2="{gx + gw}" y2="{gy}" stroke="{LINE}" stroke-width="2" stroke-dasharray="5 4"/>')
    for tv, col in [(0.25, VIO7), (0.75, PINK)]:
        pts = []
        for k in range(41):
            t = k / 40
            v = hx2(blend('覆盖', gray(tv), gray(t)))[0]
            pts.append(f'{gx + gw * t:.1f},{gy + gh - gh * v:.1f}')
        s.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="3"/>')
    s.append(text(gx + gw / 2, gy + gh + 22, '下层亮度 →', 12, 700, MUTED, 'middle'))
    s.append(text(gx, gy - 10, '覆盖的结果（灰虚线 = 不变）', 12, 800, INK))
    s.append(text(gx + 8, gy + 50, '75% 灰：提亮', 12, 800, PINK))
    s.append(text(gx + 70, gy + gh - 12, '25% 灰：压暗', 12, 800, VIO7))
    s.append(wrap(gx, gy + gh + 54, '两头的纯黑、纯白基本不动，变化最大的是中间调。所以用来加深减淡、加对比，不容易把高光和暗部弄脏。', 13, 14, 700))
    s.append(text(40, 536, '柔光和覆盖的规律一样，只是幅度小很多；修皮肤光影时更好控制。', 13, 600, MUTED))
    save('p-blend-contrast', svg(Wd, Hd, ''.join(s), '覆盖和柔光：50% 灰不起作用，深灰压暗、浅灰提亮'))


@reg
def p_blend_color_lum():
    Wd, Hd = 760, 520
    s = [card(20, 10, 720, 500)]
    s.append(label(40, 46, '颜色、色相、明度：把"什么颜色"和"多亮"拆开', YEL1, 15))
    bases = ['#3B1F6B', '#6D28D9', '#A78BFA', '#DDD6FE', '#E5E7EB', '#FFFFFF']
    names = ['暗部', '中间', '亮部', '高光', '浅灰布', '纯白布']
    red, mid = '#E11D48', '#9CA3AF'
    x0, cw = 200, 84
    for j, n in enumerate(names):
        s.append(text(x0 + j * cw + 35, 86, n, 12, 700, MUTED, 'middle'))
    rows = [('下层：衣服', None, lambda b: b), ('颜色（上层红）', red, lambda b: blend('颜色', red, b)),
            ('色相（上层红）', red, lambda b: blend('色相', red, b)), ('明度（上层中灰）', mid, lambda b: blend('明度', mid, b))]
    for i, (n, top, fn) in enumerate(rows):
        y = 100 + i * 88
        s.append(text(40, y + 40, n, 14, 800, VIO7 if i else INK))
        if top:
            s.append(f'<rect x="150" y="{y + 18}" width="30" height="30" fill="{top}" stroke="{INK}" stroke-width="2"/>')
        for j, b in enumerate(bases):
            s.append(f'<rect x="{x0 + j * cw}" y="{y}" width="70" height="66" rx="8" fill="{fn(b)}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(40, 470, '颜色：拿上层的色相和饱和度，留下层的明暗 → 换衣服颜色，褶皱的明暗还在。', 13, 700))
    s.append(text(40, 492, '注意最右两格：浅灰、纯白的布几乎换不上色；色相模式对没饱和度的灰白完全无效。明度则只换明暗。', 13, 600, MUTED))
    save('p-blend-color-lum', svg(Wd, Hd, ''.join(s), '颜色、色相、明度模式的效果对比'))


def layers_demo_rows(sel=1):
    return [dict(name='光效', thumb='glow', sel='p' if sel == 0 else None),
            dict(name='阴影', thumb='stroke', sel='p' if sel == 1 else None),
            dict(name='修图', thumb='scene', sel='p' if sel == 2 else None),
            dict(name='原图', thumb='scene', lock=True, sel='p' if sel == 3 else None),
            dict(name='背景颜色', thumb='color:#FFFFFF', mode='')]


@reg
def u_layers_anatomy():
    ph, g = photo()
    lay = lpanel(layers_demo_rows(1))
    s = screen(ph + lay, active='layers') + ring(*icon_pos('layers'), 18)
    x, y, w = 470, 62, 300
    s += ring(x + w - 26, y + 24, 14) + badge(x + w - 54, y + 24, 1)
    s += badge(x + 38, row_y(0) + 26, 2) + badge(x + 130, row_y(1), 3)
    s += ring(x + w - 44, row_y(2) + 1, 13) + badge(x + w - 70, row_y(2) + 1, 4)
    s += ring(x + w - 22, row_y(4) + 1, 13) + badge(x + w - 48, row_y(4) + 1, 5) + badge(x + 14, row_y(4) + 30, 6) + badge(x + 70, y + 12, 7)
    items = [(1, '新建图层'), (2, '缩略图'), (3, '当前图层：蓝色'), (4, '混合模式字母，点开'),
             (5, '勾选框：显示/隐藏'), (6, '背景颜色'), (7, '点「图层」：批量操作')]
    s += f'<rect x="60" y="80" width="186" height="{len(items) * 30 + 14}" rx="12" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>'
    s += legend(66, 108, items, 13, 30)
    s += note('示意图：锁头表示已锁定')
    save('u-layers-anatomy', svg(W, H, s, '图层面板各部分'))


@reg
def u_layer_options():
    ph, g = photo()
    lay = lpanel(layers_demo_rows(2), hl_row=2)
    rows = ['重命名', '选择', '拷贝', '填充图层', '清除', '阿尔法锁定', '蒙版', '剪辑蒙版', '辅助绘图', '反转', '参考', '向下合并', '向下组合']
    pop = popup(250, 56, 210, rows, title='图层选项', row_h=33)
    s = screen(ph + lay + pop, active='layers')
    s += badge(470 + 150, row_y(2) + 30, 1)
    s += label(470, 400, '① 点一下选中，再点一下', YEL1, 14)
    s += label(470, 432, '　 弹出「图层选项」', YEL1, 14)
    s += label(470, 474, '本模块会用到：重命名、填充图层、', WHITE, 13)
    s += label(470, 504, '阿尔法锁定、蒙版、剪辑蒙版、向下合并', WHITE, 13)
    s += note('示意图：菜单项以实际界面为准')
    save('u-layer-options', svg(W, H, s, '在图层上轻点两次打开图层选项'))


@reg
def u_blend_menu():
    ph, g = photo()
    lay = lpanel(layers_demo_rows(1), hl_mode=1)
    px, py, pw = 196, 56, 262
    s_ = panel(px, py, pw, 476)
    s_ += text(px + 16, py + 28, '不透明度', 14, 700, UITEXT) + text(px + pw - 16, py + 28, '45%', 14, 800, WHITE, 'end')
    s_ += f'<rect x="{px + 16}" y="{py + 40}" width="{pw - 32}" height="8" rx="4" fill="#6B7280"/><rect x="{px + 16}" y="{py + 40}" width="{(pw - 32) * .45:.0f}" height="8" rx="4" fill="{UIBLUE}"/><circle cx="{px + 16 + (pw - 32) * .45:.0f}" cy="{py + 44}" r="9" fill="{WHITE}"/>'
    modes = ['正片叠底', '变暗', '颜色加深', '线性加深', '变亮', '滤色', '颜色减淡', '添加', '覆盖', '柔光', '强光', '色相', '颜色', '明度']
    s_ += menu_rows(px, py + 62, pw, modes, hl='覆盖', row_h=29)
    s = screen(ph + lay + s_, active='layers')
    s += badge(470 + 300 - 44, row_y(1) - 26, 1)
    s += ringrect(px + 8, py + 30, pw - 16, 28) + badge(px - 14, py + 44, 2)
    s += badge(px - 14, py + 62 + 8 * 29 + 15, 3)
    s += label(470, 380, '① 点图层右边的字母（新图层是 N）', YEL1, 14)
    s += label(470, 412, '② 上面拖不透明度', YEL1, 14)
    s += label(470, 444, '③ 下面列表上下滑，边滑边预览', YEL1, 14)
    s += label(470, 486, '「覆盖」= PS 教程里的「叠加」', RED1, 14)
    s += note('示意图：列表只画了一部分；点列表外关闭')
    save('u-blend-menu', svg(W, H, s, '点图层右边的字母，选混合模式和不透明度'))


@reg
def u_layer_multi():
    ph, g = photo()
    rows = [dict(name='高光', thumb='glow', sel='s'), dict(name='阴影', thumb='stroke', sel='p'), dict(name='褶皱补色', thumb='stroke', sel='s'),
            dict(name='修图', thumb='scene'), dict(name='背景颜色', thumb='color:#FFFFFF', mode='')]
    lay = lpanel(rows, title='图层 ⌄')
    menu = popup(260, 70, 190, ['全选', '组合', '合并', '分享', '复制', '删除'], hl='组合', row_h=34)
    s = screen(ph + lay + menu, active='layers')
    s += f'<ellipse cx="610" cy="{row_y(0)}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>' + arrow(624, row_y(0), 680, row_y(0), INK, 3)
    s += badge(590, row_y(0) - 18, 1) + badge(470 + 86, 62 + 16, 2) + badge(250, 70 + 4 + 34 + 17, 3)
    s += label(470, 400, '① 单指向右轻滑：加选（深蓝）', YEL1, 14)
    s += label(470, 432, '② 点左上的「图层」', YEL1, 14)
    s += label(470, 464, '③ 「组合」编成一组', YEL1, 14)
    s += label(470, 506, '两指捏合两层：连同中间的全部合并', WHITE, 13)
    s += note('示意图')
    save('u-layer-multi', svg(W, H, s, '多选图层后编组'))


@reg
def u_layer_opacity():
    ph, g = photo()
    lay = lpanel(layers_demo_rows(1))
    bar = (f'<rect x="200" y="58" width="400" height="34" rx="17" fill="{UIPANEL}"/>' + text(220, 81, '不透明度', 14, 700, UITEXT)
           + f'<rect x="300" y="71" width="230" height="8" rx="4" fill="#6B7280"/><rect x="300" y="71" width="104" height="8" rx="4" fill="{UIBLUE}"/>' + text(584, 81, '45%', 14, 800, WHITE, 'end'))
    s = screen(ph + lay + bar, active='layers')
    s += tap_fingers(620, row_y(1), 2) + badge(660, row_y(1) - 20, 1)
    s += f'<ellipse cx="{CX + 140}" cy="{CY + 250}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>' + arrow(CX + 124, CY + 250, CX + 70, CY + 250, INK, 3) + arrow(CX + 156, CY + 250, CX + 210, CY + 250, INK, 3)
    s += badge(CX + 140, CY + 222, 2)
    s += label(470, 400, '① 两指在图层上轻点', YEL1, 14)
    s += label(470, 432, '② 上方出现不透明度条，', YEL1, 14)
    s += label(470, 464, '　 手指在画布上左右滑', YEL1, 14)
    s += label(470, 496, '点任意工具图标结束', WHITE, 13)
    s += note('示意图')
    save('u-layer-opacity', svg(W, H, s, '两指轻点图层，快速调不透明度'))


@reg
def u_color_value():
    ph, g = photo()
    px, py, pw = 420, 56, 360
    s_ = panel(px, py, pw, 420) + text(px + 16, py + 28, '颜色', 17, 800, UITEXT)
    s_ += f'<rect x="{px + pw - 64}" y="{py + 12}" width="48" height="24" rx="4" fill="#808080" stroke="{UITEXT}"/>'
    rows = [('H', 0.0, '0°'), ('S', 0.0, '0%'), ('B', 0.5, '50%'), ('R', 0.5, '128'), ('G', 0.5, '128'), ('B', 0.5, '128')]
    for i, (k, v, t) in enumerate(rows):
        y = py + 64 + i * 42
        s_ += text(px + 18, y + 6, k, 14, 800, UITEXT) + f'<rect x="{px + 44}" y="{y}" width="220" height="8" rx="4" fill="#6B7280"/><circle cx="{px + 44 + 220 * v:.0f}" cy="{y + 4}" r="8" fill="{WHITE}"/>' + text(px + pw - 20, y + 9, t, 13, 700, UITEXT, 'end')
    s_ += text(px + 18, py + 334, '十六进制', 14, 700, UITEXT) + f'<rect x="{px + 120}" y="{py + 312}" width="140" height="34" rx="8" fill="{UIBAR}"/>' + text(px + 136, py + 335, '808080', 16, 800, WHITE)
    tabs = ['色盘', '经典', '色彩调和', '值', '调色板']
    tx = px + 12
    for t in tabs:
        tw = len(t) * 14 + 16
        s_ += f'<rect x="{tx}" y="{py + 372}" width="{tw}" height="30" rx="8" fill="{UIBLUE if t == "值" else UIBAR}"/>' + text(tx + tw / 2, py + 392, t, 13, 700, UITEXT, 'middle')
        tx += tw + 6
    s = screen(ph + s_, active='color') + ring(*icon_pos('color'), 18)
    s += ringrect(px + 114, py + 308, 152, 42) + badge(px + 286, py + 329, 2)
    s += badge(px + 12 + 28 + 2 * 14 + 16 + 34 + 6 + 3 * 14 + 16 + 6 + 15, py + 418, 1)
    s += label(60, 160, '① 底下选「值」', YEL1, 14)
    s += label(60, 192, '② 十六进制填 808080', YEL1, 14)
    s += label(60, 224, '　 这就是 50% 灰', WHITE, 14)
    s += note('示意图')
    save('u-color-value', svg(W, H, s, '颜色面板的「值」：输入 808080 得到 50% 灰'))


def skirt_case(after):
    s = [f'<rect x="20" y="20" width="600" height="480" fill="#FFF7E6"/>']
    # 上衣 + 裙子特写
    s.append(f'<path d="M210 20 L430 20 L410 150 L230 150 Z" fill="{VIO2}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M230 150 L410 150 L560 470 L80 470 Z" fill="{VIO}" stroke="{INK}" stroke-width="3"/>')
    pleats = [(260, 130), (290, 220), (320, 320), (350, 420), (380, 510)]
    for x_top, x_bot in pleats:
        s.append(f'<line x1="{x_top}" y1="150" x2="{x_bot}" y2="470" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<rect x="226" y="140" width="188" height="16" fill="{INK}"/>')
    if after:
        s.append('<defs><linearGradient id="pl" x1="0" x2="1"><stop offset="0" stop-color="#4C1D95" stop-opacity="0"/><stop offset="1" stop-color="#4C1D95" stop-opacity=".55"/></linearGradient>'
                 '<linearGradient id="wb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4C1D95" stop-opacity=".6"/><stop offset="1" stop-color="#4C1D95" stop-opacity="0"/></linearGradient></defs>')
        prev = (230, 80)
        for x_top, x_bot in pleats:
            s.append(f'<path d="M{x_top - 18} 156 L{x_top} 156 L{x_bot} 470 L{x_bot - 60} 470 Z" fill="url(#pl)"/>')
        s.append(f'<path d="M232 156 L408 156 L420 200 L220 200 Z" fill="url(#wb)"/>')
        s.append(f'<path d="M410 150 L560 470 L500 470 L400 170 Z" fill="#4C1D95" fill-opacity=".35"/>')
    lab = '修之后：正片叠底层加了褶皱阴影，裙子有了体积' if after else '修之前：闪光灯打平了，裙子是一整块颜色'
    s.append(label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15))
    return svg(640, 520, ''.join(s), lab)


def glow_case(after):
    s = ['<defs><radialGradient id="gl"><stop offset="0" stop-color="#FDE68A" stop-opacity=".95"/><stop offset=".35" stop-color="#F59E0B" stop-opacity=".55"/><stop offset="1" stop-color="#F59E0B" stop-opacity="0"/></radialGradient>'
         '<radialGradient id="gl2"><stop offset="0" stop-color="#FFFFFF" stop-opacity="1"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient></defs>']
    s.append(f'<defs><clipPath id="gcl"><rect x="20" y="20" width="600" height="480"/></clipPath></defs><g clip-path="url(#gcl)"><rect x="20" y="20" width="600" height="480" fill="#2E2A4F"/>')
    # 法杖
    s.append(f'<line x1="300" y1="500" x2="340" y2="200" stroke="#7C5A3A" stroke-width="18" stroke-linecap="round"/>')
    s.append(f'<path d="M300 200 q40 -80 80 0" fill="none" stroke="#D4A017" stroke-width="10"/>')
    s.append(f'<circle cx="340" cy="170" r="30" fill="#F59E0B" stroke="{INK}" stroke-width="3"/>')
    if after:
        s.append(f'<circle cx="340" cy="170" r="190" fill="url(#gl)"/>')
        s.append(f'<circle cx="340" cy="170" r="26" fill="url(#gl2)"/>')
        for a in range(0, 360, 45):
            r = math.radians(a)
            s.append(f'<line x1="{340 + 40 * math.cos(r):.0f}" y1="{170 + 40 * math.sin(r):.0f}" x2="{340 + 90 * math.cos(r):.0f}" y2="{170 + 90 * math.sin(r):.0f}" stroke="#FEF3C7" stroke-width="2" stroke-opacity=".6"/>')
    s.append('</g>')
    lab = '修之后：滤色画外圈光晕，添加点亮中心' if after else '修之前：宝石是平的，不像在发光'
    s.append(label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15))
    return svg(640, 520, ''.join(s), lab)


# =====================================================================
# 1.5 蒙版、剪辑蒙版和阿尔法锁定
# =====================================================================
TEAL = '#14B8A6'


def dress_shape(x, y, w, h, fill, stroke=INK, sw=2.5):
    return f'<path d="M{x + w * .35} {y} L{x + w * .65} {y} L{x + w * .72} {y + h * .3} L{x + w} {y + h} L{x} {y + h} L{x + w * .28} {y + h * .3} Z" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


@reg
def p_three():
    Wd, Hd = 760, 600
    s = [card(10, 10, 740, 580)]
    cols = [('蒙版', VIO1), ('剪辑蒙版', MINT1), ('阿尔法锁定', YEL1)]
    for i, (t, f) in enumerate(cols):
        ox = 24 + i * 242
        s.append(f'<rect x="{ox}" y="24" width="230" height="352" rx="12" fill="{f}" stroke="{INK}" stroke-width="2"/>')
        s.append(text(ox + 115, 54, t, 18, 900, INK, 'middle'))
    # 蒙版：两层捆在一起
    ox = 24
    s.append(f'<rect x="{ox + 20}" y="72" width="80" height="60" rx="6" fill="#111" stroke="{INK}" stroke-width="2"/>' + dress_shape(ox + 35, 78, 50, 50, '#FFF', INK, 1))
    s.append(text(ox + 110, 98, '蒙版：黑白灰', 13, 800) + text(ox + 110, 118, '黑=藏 白=显', 12, 700, MUTED))
    s.append(f'<path d="M{ox + 60} 132 v14" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<rect x="{ox + 20}" y="146" width="80" height="60" rx="6" fill="{TEAL}" stroke="{INK}" stroke-width="2"/>')
    s.append(text(ox + 110, 172, '它所属的图层', 13, 800) + text(ox + 110, 192, '（整张都换了色）', 12, 700, MUTED))
    # 剪辑蒙版
    ox = 266
    s.append(f'<rect x="{ox + 20}" y="72" width="80" height="60" rx="6" fill="{TEAL}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<path d="M{ox + 12} 84 v30 m-6 -8 l6 9 l6 -9" fill="none" stroke="{INK}" stroke-width="2.5"/>')
    s.append(text(ox + 110, 98, '上：剪辑层', 13, 800) + text(ox + 110, 118, '自己是独立一层', 12, 700, MUTED))
    s.append(checker(ox + 20, 146, 80, 60, 6, 'clp3') + f'<rect x="{ox + 20}" y="146" width="80" height="60" rx="6" fill="none" stroke="{INK}" stroke-width="2"/>' + dress_shape(ox + 35, 152, 50, 50, VIO, INK, 1.5))
    s.append(text(ox + 110, 172, '下：被剪辑的层', 13, 800) + text(ox + 110, 192, '它的形状当模子', 12, 700, MUTED))
    # 阿尔法
    ox = 508
    s.append(checker(ox + 20, 72, 80, 134, 6, 'alp3') + f'<rect x="{ox + 20}" y="72" width="80" height="134" rx="6" fill="none" stroke="{INK}" stroke-width="2"/>' + dress_shape(ox + 30, 100, 60, 90, VIO, INK, 1.5))
    s.append(f'<defs><clipPath id="alpc">{dress_shape(ox + 30, 100, 60, 90, "#000")}</clipPath></defs>')
    s.append(f'<path d="M{ox + 14} 164 L{ox + 106} 116" stroke="{TEAL}" stroke-width="10" stroke-opacity=".25"/>')
    s.append(f'<path d="M{ox + 14} 164 L{ox + 106} 116" stroke="{TEAL}" stroke-width="10" clip-path="url(#alpc)"/>')
    s.append(text(ox + 108, 120, '只有这一层', 13, 800) + text(ox + 108, 140, '透明的地方', 12, 700, MUTED) + text(ox + 108, 158, '画不上去', 12, 700, MUTED))
    # 三个结果
    for i in range(3):
        ox = 24 + i * 242
        s.append(text(ox + 20, 236, '结果', 13, 800, MUTED))
        s.append(f'<rect x="{ox + 20}" y="244" width="190" height="80" rx="8" fill="#FFF7E6" stroke="{INK}" stroke-width="1.5"/>')
        s.append(dress_shape(ox + 80, 250, 70, 68, TEAL, INK, 2))
    notes = [('改的是：哪里显示', '画黑色藏、白色找回来', '原图一点没动'),
             ('改的是：上层只在模子里显示', '上层随便涂、随便换色', '可以叠好几层剪辑'),
             ('改的是：这一层自己的像素', '最快，不多占图层', '画上去就回不去了')]
    for i, (a, b, c) in enumerate(notes):
        ox = 24 + i * 242
        s.append(text(ox + 14, 346, a, 13, 800, VIO7))
        s.append(text(ox + 14, 366, b, 12, 700, INK))
    # 表格
    tx, ty = 24, 396
    head = ['', '蒙版', '剪辑蒙版', '阿尔法锁定']
    rows = [('怎么打开', '图层选项 › 蒙版', '图层选项 › 剪辑蒙版', '图层选项，或两指右滑'),
            ('多一个图层吗', '多一个蒙版', '多一个图层', '不多'),
            ('改错了能回来吗', '能：涂白就回来', '能：改上层或删掉', '只能撤销'),
            ('修图里常用来', '抠图边缘、局部效果', '换色、加阴影高光', '给已抠好的层上色')]
    cw = [150, 190, 190, 196]
    for r, row in enumerate([head] + rows):
        y = ty + r * 36
        x = tx
        for c, cell in enumerate(row):
            fill = '#F1F5F9' if r == 0 else WHITE
            s.append(f'<rect x="{x}" y="{y}" width="{cw[c]}" height="36" fill="{fill}" stroke="{LINE}"/>')
            s.append(text(x + 10, y + 23, cell, 13, 800 if (r == 0 or c == 0) else 600, INK))
            x += cw[c]
    save('p-three', svg(Wd, Hd, ''.join(s), '蒙版、剪辑蒙版、阿尔法锁定三者对比'))


@reg
def p_mask_gray():
    Wd, Hd = 760, 300
    s = [card(20, 10, 720, 280)]
    s.append(label(40, 46, '蒙版上的颜色 = 这层的可见程度', YEL1, 15))
    s.append(text(40, 100, '蒙版', 14, 800))
    s.append(grad_bar(150, 76, 540, 40, 30, gray))
    s.append(text(40, 170, '画面效果', 14, 800))
    s.append(checker(150, 146, 540, 40, 8, 'mg'))
    s.append(grad_bar(150, 146, 540, 40, 30, lambda t: TEAL, False).replace('fill="#14B8A6"', 'fill="#14B8A6" fill-opacity="X"'))
    # 用逐块透明度重画
    bars = ''
    for k in range(30):
        t = k / 29
        bars += f'<rect x="{150 + 540 * k / 30:.2f}" y="146" width="{540 / 30 + .6:.2f}" height="40" fill="{TEAL}" fill-opacity="{t:.2f}"/>'
    s[-1] = bars + f'<rect x="150" y="146" width="540" height="40" fill="none" stroke="{INK}" stroke-width="2"/>'
    for t, n in [(0, '黑：完全藏起来'), (0.5, '50% 灰：半透明'), (1, '白：完全显示')]:
        x = 150 + 540 * t
        s.append(f'<line x1="{x}" y1="120" x2="{x}" y2="142" stroke="{INK}" stroke-width="2"/>')
        s.append(text(min(max(x, 200), 640), 214, n, 13, 800, INK, 'middle'))
    s.append(text(40, 262, '在蒙版上用低不透明度的软画笔涂黑或涂白，就能做出很柔的过渡；颜色面板会自动只给黑白灰。', 13, 600, MUTED))
    save('p-mask-gray', svg(Wd, Hd, ''.join(s), '蒙版的黑白灰对应图层的可见程度'))


@reg
def p_erase_vs_mask():
    Wd, Hd = 760, 330
    s = []
    for col, (title, fill) in enumerate([('橡皮擦：像素真的没了', RED1), ('蒙版涂黑：只是藏起来', MINT1)]):
        ox = 20 + col * 380
        s.append(card(ox, 10, 360, 310))
        s.append(label(ox + 16, 44, title, fill, 15))
        # 人物轮廓 + 被擦多的一块
        s.append(f'<rect x="{ox + 30}" y="70" width="140" height="160" fill="#BAE6FD" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<path d="M{ox + 100} 228 q-46 -60 -26 -120 q26 -40 52 0 q20 60 -26 120 Z" fill="{PINK}" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<circle cx="{ox + 128}" cy="122" r="22" fill="#BAE6FD"/>')
        s.append(arrow(ox + 180, 150, ox + 214, 150, INK, 3))
        if col == 0:
            s.append(f'<rect x="{ox + 224}" y="70" width="110" height="160" fill="{RED1}" stroke="{RED}" stroke-width="2" stroke-dasharray="6 4"/>')
            s.append(wrap(ox + 232, 110, '想补回来只能撤销。回过图库，就再也找不回', 13, 7, 800, RED7))
        else:
            s.append(f'<rect x="{ox + 224}" y="70" width="110" height="160" fill="{MINT1}" stroke="{MINT7}" stroke-width="2"/>')
            s.append(wrap(ox + 232, 110, '在蒙版上涂白，这块马上回来，随时都行', 13, 7, 800, MINT7))
        s.append(text(ox + 30, 262, '红圈处被擦多了一块头发', 13, 700, MUTED))
        s.append(f'<circle cx="{ox + 128}" cy="122" r="26" fill="none" stroke="{RED}" stroke-width="3"/>')
        s.append(text(ox + 30, 290, '橡皮改的是图层本身' if col == 0 else '蒙版改的是"显示哪里"，原图层没动', 13, 800))
    save('p-erase-vs-mask', svg(Wd, Hd, ''.join(s), '橡皮擦和蒙版的区别：擦掉是删除，蒙版是隐藏'))


def dress_photo(teal=False):
    ph, g = photo(top=None)
    if teal:
        ph = ph.replace(f'fill="{VIO}"', f'fill="{TEAL}"')
    return ph, g


def skirt_poly(g):
    cx, hh, waist, hip = g['cx'], g['hh'], g['waist'], g['hip']
    return f'M{cx - hh * 0.5:.1f} {waist:.1f} L{cx + hh * 0.5:.1f} {waist:.1f} L{cx + hh * 0.9:.1f} {hip + hh * 0.1:.1f} L{cx - hh * 0.9:.1f} {hip + hh * 0.1:.1f} Z'


@reg
def u_sel_dress():
    ph, g = dress_photo()
    d = skirt_poly(g)
    sel = f'<path d="{d}" fill="{YEL}" fill-opacity=".55" stroke="{INK}" stroke-width="2" stroke-dasharray="6 5"/>'
    thr = (f'<rect x="230" y="58" width="340" height="34" rx="17" fill="{UIPANEL}"/>' + text(250, 81, '选区阈值', 14, 700, UITEXT)
           + f'<rect x="330" y="71" width="170" height="8" rx="4" fill="#6B7280"/><rect x="330" y="71" width="68" height="8" rx="4" fill="{UIBLUE}"/>' + text(552, 81, '38%', 14, 800, WHITE, 'end'))
    hand = f'<ellipse cx="{g["cx"] + 6:.0f}" cy="{g["hip"] - 6:.0f}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>' + arrow(g['cx'] + 20, g['hip'] - 6, g['cx'] + 70, g['hip'] - 6, INK, 3) + arrow(g['cx'] - 8, g['hip'] - 6, g['cx'] - 58, g['hip'] - 6, INK, 3)
    s = screen(ph + sel + thr + hand + bottom_bar(SEL_ROWS, active=('自动',), hl='拷贝并粘贴'), active='select')
    s += ring(*icon_pos('select'), 18) + badge(icon_pos('select')[0] + 26, 62, 1)
    s += badge(POS['自动'][0] + 20, POS['自动'][1] - 12, 2)
    s += badge(g['cx'] + 80, g['hip'] - 24, 3)
    px, py, pw, phh = POS['拷贝并粘贴']
    s += badge(px + pw - 4, py + 4, 4)
    s += label(552, 140, '① 选取工具 ② 选「自动」', YEL1, 14)
    s += label(552, 172, '③ 在裙子上点住，左右拖：', YEL1, 14)
    s += label(552, 204, '　 往右选得多，往左选得少', YEL1, 14)
    s += label(552, 252, '④ 选好后点「拷贝并粘贴」', YEL1, 14)
    s += label(552, 284, '　 裙子复制到新图层「从选区」', WHITE, 13)
    s += note('示意图：选中的部分显示成对比色')
    save('u-sel-dress', svg(W, H, s, '用自动选取选中裙子，再拷贝并粘贴到新图层'))


def opts_screen(name, rows_state, hl_item, hl_row, labels, title, content=None):
    ph, g = (content, None) if content else dress_photo()
    lay = lpanel(rows_state, hl_row=hl_row)
    items = ['重命名', '选择', '拷贝', '填充图层', '清除', '阿尔法锁定', '蒙版', '剪辑蒙版', '辅助绘图', '反转', '参考', '向下合并', '向下组合']
    pop = popup(250, 56, 210, items, hl=hl_item, title='图层选项', row_h=33)
    s = screen(ph + lay + pop, active='layers')
    idx = items.index(hl_item)
    s += badge(470 + 150, row_y(hl_row) + 30, 1) + badge(244, 56 + 40 + idx * 33 + 17, 2)
    for i, (t, f) in enumerate(labels):
        s += label(470, 400 + i * 32, t, f, 14 if f != WHITE else 13)
    s += note('示意图：菜单项以实际界面为准')
    save(name, svg(W, H, s, title))


@reg
def u_alpha_fill():
    rows = [dict(name='从选区', thumb='dress:' + VIO, sel='p'), dict(name='原图', thumb='scene', lock=True), dict(name='背景颜色', thumb='color:#FFFFFF', mode='')]
    opts_screen('u-alpha-fill', rows, '填充图层', 0,
                [('① 点「从选区」两下打开图层选项', YEL1), ('② 先点「阿尔法锁定」，', YEL1), ('　 再点「填充图层」', YEL1), ('只有裙子的形状被填满', WHITE)],
                '先阿尔法锁定，再填充图层，只填满已有像素的地方')


@reg
def u_alpha_swipe():
    ph, g = dress_photo(True)
    rows = [dict(name='从选区', thumb='dress:' + TEAL, sel='p', alpha=True, mode='N'), dict(name='原图', thumb='scene', lock=True), dict(name='背景颜色', thumb='color:#FFFFFF', mode='')]
    lay = lpanel(rows)
    s = screen(ph + lay, active='layers')
    y0 = row_y(0)
    s += f'<ellipse cx="560" cy="{y0 - 6}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/><ellipse cx="560" cy="{y0 + 14}" rx="9" ry="12" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>'
    s += arrow(574, y0 + 4, 640, y0 + 4, INK, 3) + badge(540, y0 - 26, 1)
    s += ringrect(484, y0 - 19, 50, 40, 6) + badge(470 + 26, y0 + 34, 2)
    s += label(470, 310, '① 两指在图层上向右轻滑：', YEL1, 14)
    s += label(470, 342, '　 开 / 关阿尔法锁定', YEL1, 14)
    s += label(470, 380, '② 开着时缩略图背后是棋盘格', YEL1, 14)
    s += label(470, 424, '之后在这层上画，', WHITE, 14)
    s += label(470, 456, '透明的地方画不上去', WHITE, 14)
    s += note('示意图')
    save('u-alpha-swipe', svg(W, H, s, '两指向右轻滑开关阿尔法锁定'))


@reg
def u_clip_create():
    rows = [dict(name='新颜色', thumb='color:' + TEAL, sel='p'), dict(name='从选区', thumb='dress:' + VIO), dict(name='原图', thumb='scene', lock=True), dict(name='背景颜色', thumb='color:#FFFFFF', mode='')]
    opts_screen('u-clip-create', rows, '剪辑蒙版', 0,
                [('① 在「从选区」上面新建一层，', YEL1), ('　 填满新颜色，点两下打开选项', YEL1), ('② 点「剪辑蒙版」', YEL1), ('新颜色只剩裙子形状那一块', WHITE)],
                '在图层选项里把新图层设为剪辑蒙版')


@reg
def u_clip_result():
    ph, g = dress_photo(True)
    rows = [dict(name='新颜色', thumb='color:' + TEAL, sel='p', indent=True, clip=True, mode='N'), dict(name='从选区', thumb='dress:' + VIO), dict(name='原图', thumb='scene', lock=True), dict(name='背景颜色', thumb='color:#FFFFFF', mode='')]
    lay = lpanel(rows, hl_mode=0)
    s = screen(ph + lay, active='layers')
    s += ring(484, row_y(0), 14) + badge(470 + 14, row_y(0) + 30, 1) + badge(470 + 300 - 70, row_y(0), 2)
    s += label(470, 360, '① 缩进 + 向下的小箭头：', YEL1, 14)
    s += label(470, 392, '　 它剪辑到下面那层', YEL1, 14)
    s += label(470, 430, '② 混合模式改成「颜色」：', YEL1, 14)
    s += label(470, 462, '　 换了颜色，褶皱明暗还在', YEL1, 14)
    s += label(470, 500, '想换别的颜色：重新填充这层', WHITE, 13)
    s += note('示意图：剪辑标记的样子以实际界面为准')
    save('u-clip-result', svg(W, H, s, '剪辑蒙版图层缩进显示，混合模式改成颜色'))


@reg
def u_mask_create():
    rows = [dict(name='换色副本', thumb='scene', sel='p'), dict(name='原图', thumb='scene', lock=True), dict(name='背景颜色', thumb='color:#FFFFFF', mode='')]
    ph, g = photo(top=None)
    ph = ph.replace(f'fill="{VIO}"', f'fill="{TEAL}"').replace(f'fill="{VIO2}"', 'fill="#99F6E4"').replace(f'fill="{YEL1}"', 'fill="#BFDBFE"').replace(f'fill="{PINK}"', 'fill="#60A5FA"')
    opts_screen('u-mask-create', rows, '蒙版', 0,
                [('副本整张都调了色，先别慌', WHITE), ('① 点「换色副本」两下', YEL1), ('② 点「蒙版」', YEL1), ('图层上方多出一个白色的「图层蒙版」', WHITE)],
                '在图层选项里给图层加蒙版', content=ph)


@reg
def u_mask_paint():
    ph, g = dress_photo(True)
    rows = [dict(name='图层蒙版', thumb='mask-bw', sel='p', indent=True, mode='N'), dict(name='换色副本', thumb='scene'), dict(name='原图', thumb='scene', lock=True), dict(name='背景颜色', thumb='color:#FFFFFF', mode='')]
    lay = lpanel(rows)
    brush = f'<circle cx="{g["cx"] + 30:.0f}" cy="{g["hip"] - 14:.0f}" r="26" fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-dasharray="5 4"/>'
    s = screen(ph + brush + lay, active='brush') + ring(*icon_pos('brush'), 18)
    s += ringrect(470 + 30, row_y(0) - 24, 262, 48) + badge(470 + 14, row_y(0) + 30, 1)
    s += ring(*icon_pos('color'), 18) + badge(icon_pos('color')[0], 66, 2)
    s += label(470, 356, '① 点「图层蒙版」让它变蓝', YEL1, 14)
    s += label(470, 386, '　 先用黑色把整个蒙版填满（全藏）', WHITE, 13)
    s += label(470, 422, '② 软画笔、白色，涂裙子：', YEL1, 14)
    s += label(470, 454, '　 涂到哪，新颜色就露到哪', YEL1, 14)
    s += label(470, 492, '涂出界：换黑色涂回去', MINT1, 14)
    s += note('示意图：选中蒙版时颜色面板只给黑白灰')
    save('u-mask-paint', svg(W, H, s, '在蒙版上用白色画出要显示的地方'))


def dress_case(after):
    parts = []
    parts.append(f'<rect x="20" y="20" width="600" height="480" fill="#FFF7E6"/>')
    g = [f'<path d="M210 20 L430 20 L410 150 L230 150 Z" fill="{VIO2}" stroke="{INK}" stroke-width="3"/>']
    sk = [f'<path d="M230 150 L410 150 L560 470 L80 470 Z" fill="{TEAL if after else VIO}" stroke="{INK}" stroke-width="3"/>']
    pleats = [(260, 130), (290, 220), (320, 320), (350, 420), (380, 510)]
    for x_top, x_bot in pleats:
        sk.append(f'<path d="M{x_top - 18} 156 L{x_top} 156 L{x_bot} 470 L{x_bot - 60} 470 Z" fill="url(#pl2)"/>')
        sk.append(f'<line x1="{x_top}" y1="150" x2="{x_bot}" y2="470" stroke="{INK}" stroke-width="2"/>')
    sk.append(f'<path d="M232 156 L408 156 L420 200 L220 200 Z" fill="url(#wb2)"/><path d="M410 150 L560 470 L500 470 L400 170 Z" fill="#000" fill-opacity=".25"/>')
    defs = ('<defs><linearGradient id="pl2" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".35"/></linearGradient>'
            '<linearGradient id="wb2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity=".4"/><stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>'
            '<filter id="toteal"><feColorMatrix type="hueRotate" values="200"/></filter></defs>')
    skirt = ''.join(sk)
    parts.append(defs + ''.join(g) + skirt + f'<rect x="226" y="140" width="188" height="16" fill="{INK}"/>')
    lab = '修之后：剪辑蒙版 + 颜色模式，裙子变成青绿，褶皱还在' if after else '修之前：紫色百褶裙，coser 想要角色设定的青绿色'
    parts.append(label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15))
    return svg(640, 520, ''.join(parts), lab)


def edge_case(after):
    s = [f'<rect x="20" y="20" width="600" height="480" fill="#BAE6FD"/>']
    s.append(f'<path d="M80 500 Q120 380 200 360 L440 360 Q520 380 560 500 Z" fill="{VIO2}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M150 380 Q120 200 200 110 Q320 40 440 110 Q520 200 490 380 Z" fill="{PINK}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<ellipse cx="320" cy="240" rx="110" ry="130" fill="{SKIN}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M210 200 Q240 100 320 100 Q400 100 430 200 Q380 160 320 170 Q260 160 210 200 Z" fill="{PINK}" stroke="{INK}" stroke-width="3"/>')
    for dx in (-40, 40):
        s.append(f'<ellipse cx="{320 + dx}" cy="250" rx="13" ry="16" fill="{INK}"/>')
    if after:
        for x0, y0, bend in [(470, 150, 30), (490, 200, 34), (480, 260, 26), (160, 160, -30), (150, 220, -34), (470, 110, 24)]:
            s.append(f'<path d="M{x0 - 20 * (1 if bend > 0 else -1)} {y0} q{bend} -6 {bend * 1.6:.0f} 14" fill="none" stroke="#DB2777" stroke-width="2.2" stroke-linecap="round"/>')
    else:
        s.append(f'<path d="M470 140 L520 170 L500 260 L470 250 Z" fill="#BAE6FD"/>')
        s.append(f'<path d="M470 140 L500 170 L490 250" fill="none" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<circle cx="490" cy="200" r="56" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="6 4"/>')
    lab = '修之后：蒙版上涂白找回头发，再用细笔补几根飞丝' if after else '修之前：用橡皮抠图，右边头发擦多了一块，边缘生硬'
    s.append(label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15))
    return svg(640, 520, ''.join(s), lab)


# =====================================================================
# 1.6 选区和变换
# =====================================================================
def quad_pt(q, u, v):
    """q = (左上, 右上, 左下, 右下)；双线性取点"""
    (x00, y00), (x10, y10), (x01, y01), (x11, y11) = q
    x = (1 - u) * (1 - v) * x00 + u * (1 - v) * x10 + (1 - u) * v * x01 + u * v * x11
    y = (1 - u) * (1 - v) * y00 + u * (1 - v) * y10 + (1 - u) * v * y01 + u * v * y11
    return x, y


def corridor(x, y, w, h, uid='c'):
    """走廊：左墙透视。返回 (svg, 墙四角)"""
    vpx, vpy = x + w * 0.78, y + h * 0.42
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#F1F5F9"/>']
    far_l, far_r, far_t, far_b = x + w * 0.62, x + w * 0.92, y + h * 0.30, y + h * 0.56
    # 地面、天花板、左墙
    s.append(f'<path d="M{x} {y + h} L{far_l} {far_b} L{far_r} {far_b} L{x + w} {y + h} Z" fill="{FLOOR}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<path d="M{x} {y} L{far_l} {far_t} L{far_r} {far_t} L{x + w} {y} Z" fill="#E2E8F0" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<path d="M{x} {y} L{far_l} {far_t} L{far_l} {far_b} L{x} {y + h} Z" fill="{YEL1}" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<rect x="{far_l}" y="{far_t}" width="{far_r - far_l}" height="{far_b - far_t}" fill="#CBD5E1" stroke="{INK}" stroke-width="2"/>')
    s.append(f'<path d="M{x + w} {y} L{far_r} {far_t} L{far_r} {far_b} L{x + w} {y + h} Z" fill="#FEF9C3" stroke="{INK}" stroke-width="2"/>')
    wall = ((x, y), (far_l, far_t), (x, y + h), (far_l, far_b))
    # 墙上的踢脚线、腰线
    for v in (0.55, 0.92):
        a = quad_pt(wall, 0, v); b = quad_pt(wall, 1, v)
        s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{MUTED}" stroke-width="2"/>')
    return ''.join(s), wall


def poster(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PINK}" stroke="{INK}" stroke-width="2"/>'
            f'<circle cx="{x + w / 2}" cy="{y + h * 0.4}" r="{w * 0.22}" fill="{YEL}" stroke="{INK}" stroke-width="1.5"/>'
            f'<rect x="{x + w * 0.15}" y="{y + h * 0.72}" width="{w * 0.7}" height="{h * 0.08}" fill="{INK}"/>')


def poster_quad(q, uid='pq'):
    """把海报画进任意四边形（近似：用四条边围出来再画内容）"""
    pts = [quad_pt(q, 0, 0), quad_pt(q, 1, 0), quad_pt(q, 1, 1), quad_pt(q, 0, 1)]
    d = 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts) + ' Z'
    s = f'<path d="{d}" fill="{PINK}" stroke="{INK}" stroke-width="2"/>'
    # 太阳：取中心
    c = quad_pt(q, .5, .4); r1 = abs(quad_pt(q, .72, .4)[0] - c[0]); r2 = abs(quad_pt(q, .5, .55)[1] - c[1])
    s += f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{r1:.1f}" ry="{r2:.1f}" fill="{YEL}" stroke="{INK}" stroke-width="1.5"/>'
    b = [quad_pt(q, .15, .72), quad_pt(q, .85, .72), quad_pt(q, .85, .8), quad_pt(q, .15, .8)]
    s += '<path d="M' + ' L'.join(f'{a:.1f} {bb:.1f}' for a, bb in b) + f' Z" fill="{INK}"/>'
    return s, pts


def sub_quad(wall, u0, u1, v0, v1):
    return (quad_pt(wall, u0, v0), quad_pt(wall, u1, v0), quad_pt(wall, u0, v1), quad_pt(wall, u1, v1))


@reg
def p_feather():
    Wd, Hd = 760, 330
    s = ['<defs><radialGradient id="fth"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".6"/><stop offset=".6" stop-color="#FFFFFF" stop-opacity=".45"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient></defs>']
    for col, (title, soft, fill) in enumerate([('羽化 0%：选区边缘一刀切', False, RED1), ('羽化后：边缘慢慢过渡', True, MINT1)]):
        ox = 20 + col * 380
        s.append(card(ox, 10, 360, 310))
        s.append(label(ox + 16, 44, title, fill, 15))
        s.append(f'<rect x="{ox + 30}" y="70" width="300" height="180" fill="#9CA3AF"/>')
        s.append(f'<ellipse cx="{ox + 180}" cy="160" rx="70" ry="80" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
        if soft:
            s.append(f'<circle cx="{ox + 180}" cy="160" r="100" fill="url(#fth)"/>')
        else:
            s.append(f'<circle cx="{ox + 180}" cy="160" r="62" fill="#FFFFFF" fill-opacity=".45"/>')
        s.append(text(ox + 30, 276, '在选区里提亮脸部：', 13, 700))
        s.append(text(ox + 30, 298, '一圈明显的亮圆边' if not soft else '看不出是从哪里开始提亮的', 13, 800, RED7 if not soft else MINT7))
    save('p-feather', svg(Wd, Hd, ''.join(s), '羽化：让选区边缘变软'))


@reg
def p_auto_threshold():
    Wd, Hd = 760, 300
    s = [card(20, 10, 720, 280)]
    s.append(label(40, 46, '自动选取：点一下，把"颜色差不多"的相连区域选进来', YEL1, 15))
    for i, (t, lvl, col) in enumerate([('阈值太低：只选到一小块', 0, RED7), ('刚好：整条裙子', 1, MINT7), ('太高：漏到背景里', 2, RED7)]):
        ox = 40 + i * 236
        s.append(f'<rect x="{ox}" y="70" width="210" height="160" fill="#D6D3F0" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<path d="M{ox + 80} 90 L{ox + 130} 90 L{ox + 170} 210 L{ox + 40} 210 Z" fill="{VIO}" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<path d="M{ox + 110} 90 L{ox + 130} 90 L{ox + 170} 210 L{ox + 130} 210 Z" fill="{VIO7}"/>')
        if lvl == 0:
            s.append(f'<path d="M{ox + 80} 90 L{ox + 110} 90 L{ox + 130} 210 L{ox + 40} 210 Z" fill="{YEL}" fill-opacity=".7" stroke="{INK}" stroke-dasharray="5 4"/>')
        elif lvl == 1:
            s.append(f'<path d="M{ox + 80} 90 L{ox + 130} 90 L{ox + 170} 210 L{ox + 40} 210 Z" fill="{YEL}" fill-opacity=".7" stroke="{INK}" stroke-dasharray="5 4"/>')
        else:
            s.append(f'<rect x="{ox}" y="70" width="210" height="160" fill="{YEL}" fill-opacity=".6" stroke="{INK}" stroke-dasharray="5 4"/>')
        s.append(f'<ellipse cx="{ox + 95}" cy="160" rx="7" ry="10" fill="{SKIN}" stroke="{INK}" stroke-width="2"/>')
        s.append(text(ox + 105, 258, t, 13, 800, col, 'middle'))
    s.append(text(40, 282, '点住不放、左右拖调阈值；一次选不全，就再点没选到的地方，会加进来。', 13, 600, MUTED))
    save('p-auto-threshold', svg(Wd, Hd, ''.join(s), '自动选取的选区阈值'))


@reg
def p_transform_modes():
    Wd, Hd = 760, 300
    s = [card(10, 10, 740, 280)]
    names = [('自由变换', '宽高分开拉，会变形'), ('等比', '宽高一起缩放，不变形'), ('扭曲', '四个角各拉各的：做透视'), ('弯曲', '网格拖成曲面：贴柱子')]
    for i, (n, d) in enumerate(names):
        ox = 26 + i * 182
        s.append(f'<rect x="{ox}" y="26" width="168" height="248" rx="12" fill="{[VIO1, MINT1, YEL1, PINK1][i]}" stroke="{INK}" stroke-width="2"/>')
        s.append(text(ox + 84, 56, n, 17, 900, INK, 'middle'))
        bx, by = ox + 44, 80
        s.append(f'<rect x="{bx}" y="{by}" width="80" height="100" fill="none" stroke="{MUTED}" stroke-width="2" stroke-dasharray="5 4"/>')
        if i == 0:
            s.append(f'<rect x="{bx - 20}" y="{by + 10}" width="120" height="80" fill="{PINK}" fill-opacity=".8" stroke="{INK}" stroke-width="2"/>')
        elif i == 1:
            s.append(f'<rect x="{bx + 12}" y="{by + 15}" width="56" height="70" fill="{PINK}" fill-opacity=".8" stroke="{INK}" stroke-width="2"/>')
        elif i == 2:
            s.append(f'<path d="M{bx - 6} {by - 4} L{bx + 86} {by + 24} L{bx + 86} {by + 82} L{bx - 6} {by + 108} Z" fill="{PINK}" fill-opacity=".8" stroke="{INK}" stroke-width="2"/>')
        else:
            s.append(f'<path d="M{bx} {by} Q{bx + 40} {by + 20} {bx + 80} {by} L{bx + 80} {by + 100} Q{bx + 40} {by + 120} {bx} {by + 100} Z" fill="{PINK}" fill-opacity=".8" stroke="{INK}" stroke-width="2"/>')
            for k in (1, 2):
                xx = bx + 80 * k / 3
                s.append(f'<path d="M{xx:.0f} {by + 9 + (2 if k else 0)} L{xx:.0f} {by + 109}" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3"/>')
            s.append(f'<path d="M{bx} {by + 50} Q{bx + 40} {by + 70} {bx + 80} {by + 50}" fill="none" stroke="{INK}" stroke-width="1" stroke-dasharray="3 3"/>')
        s.append(wrap(ox + 14, 214, d, 13, 11, 700))
    save('p-transform-modes', svg(Wd, Hd, ''.join(s), '变换的四种模式'))


@reg
def p_interp():
    Wd, Hd = 760, 340
    s = ['<defs><filter id="b1"><feGaussianBlur stdDeviation="2.2"/></filter><filter id="b2"><feGaussianBlur stdDeviation="3.2"/></filter>'
         '<clipPath id="ic0"><rect x="0" y="0" width="160" height="160"/></clipPath></defs>']
    s.append(card(10, 10, 740, 320))
    # 小图：4x4 斜边
    def blocks(ox, oy, cell, filt=None):
        g = []
        for i in range(6):
            for j in range(6):
                on = i + j < 6
                g.append(f'<rect x="{ox + i * cell}" y="{oy + j * cell}" width="{cell + .5}" height="{cell + .5}" fill="{VIO7 if on else "#FFFFFF"}"/>')
        body = ''.join(g)
        if filt:
            body = f'<g filter="url(#{filt})">{body}</g>'
        return f'<svg x="{ox}" y="{oy}" width="{cell * 6}" height="{cell * 6}" viewBox="{ox} {oy} {cell * 6} {cell * 6}" overflow="hidden">{body}</svg>' + f'<rect x="{ox}" y="{oy}" width="{cell * 6}" height="{cell * 6}" fill="none" stroke="{INK}" stroke-width="2"/>'
    s.append(text(40, 50, '把一块很小的斜边放大 4 倍：', 15, 800))
    items = [('原图（放大前）', None, 6), ('最近邻', None, 26), ('双线性', 'b1', 26), ('双立体', 'b2', 26)]
    xs = [40, 170, 360, 550]
    for (n, f, cell), x in zip(items, xs):
        if cell == 6:
            s.append(blocks(x + 40, 140, cell))
        else:
            s.append(blocks(x, 70, cell, f))
        s.append(text(x + 78, 254, n, 15, 900, VIO7 if cell != 6 else INK, 'middle'))
    s.append(text(170 + 78, 278, '边缘锯齿、一格一格', 12, 700, RED7, 'middle'))
    s.append(text(360 + 78, 278, '比较平滑（默认）', 12, 700, MUTED, 'middle'))
    s.append(text(550 + 78, 278, '最平滑，修照片用它', 12, 700, MINT7, 'middle'))
    s.append(text(40, 314, '每变换一次，像素就重新算一次。对同一块反复缩小再放大，会越来越糊——要重做就撤销回原图再变换。', 13, 600, MUTED))
    save('p-interp', svg(Wd, Hd, ''.join(s), '插值：最近邻、双线性、双立体的区别'))


@reg
def p_perspective():
    Wd, Hd = 760, 380
    s = []
    for col, (title, fit, fill) in enumerate([('直接贴：海报是正的，墙是斜的', False, RED1), ('扭曲后：四个角落在墙的透视线上', True, MINT1)]):
        ox = 20 + col * 380
        s.append(card(ox, 10, 360, 360))
        s.append(label(ox + 16, 44, title, fill, 14))
        sc, wall = corridor(ox + 20, 66, 320, 260)
        s.append(sc)
        if fit:
            q = sub_quad(wall, 0.18, 0.62, 0.2, 0.72)
            ps, pts = poster_quad(q)
            s.append(ps)
            # 延长线到消失点
            for v in (0.2, 0.72):
                a = quad_pt(wall, 0, v); b = quad_pt(wall, 1.25, v)
                s.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{VIO7}" stroke-width="2" stroke-dasharray="6 4"/>')
            s.append(text(ox + 30, 350, '海报上下边和墙的腰线、踢脚线指向同一个方向', 12, 700, MINT7))
        else:
            s.append(poster(ox + 80, 130, 90, 120))
            s.append(text(ox + 30, 350, '像浮在镜头前面，和墙没关系', 12, 700, RED7))
    save('p-perspective', svg(Wd, Hd, ''.join(s), '透视：贴到斜墙上的海报要跟着墙的透视线收窄'))


@reg
def p_cutoff():
    Wd, Hd = 760, 280
    s = [card(20, 10, 720, 260)]
    s.append(label(40, 46, '移出画布的部分，确认变换后就被裁掉了', YEL1, 15))
    for i, (t, stage) in enumerate([('拖到画布外面', 0), ('点变换图标确认', 1), ('再拖回来：缺了一块', 2)]):
        ox = 50 + i * 230
        s.append(f'<rect x="{ox}" y="70" width="150" height="150" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
        if stage == 0:
            s.append(f'<circle cx="{ox + 140}" cy="145" r="40" fill="{PINK}" stroke="{INK}" stroke-width="2"/>')
            s.append(f'<rect x="{ox}" y="70" width="150" height="150" fill="none" stroke="{INK}" stroke-width="2.5"/>')
        elif stage == 1:
            s.append(f'<path d="M{ox + 150} 105 A40 40 0 0 0 {ox + 150} 185 Z" fill="{PINK}" stroke="{INK}" stroke-width="2"/>')
            s.append(f'<path d="M{ox + 150} 105 A40 40 0 0 1 {ox + 150} 185" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>')
        else:
            s.append(f'<path d="M{ox + 115} 105 A40 40 0 0 0 {ox + 115} 185 Z" fill="{PINK}" stroke="{INK}" stroke-width="2"/>')
        s.append(text(ox + 75, 246, t, 13, 800, RED7 if stage == 2 else INK, 'middle'))
        if i < 2:
            s.append(arrow(ox + 196, 145, ox + 222, 145, INK, 3))
    save('p-cutoff', svg(Wd, Hd, ''.join(s), '变换时移出画布的部分会被裁掉'))


@reg
def u_sel_freehand():
    ph, g = photo()
    cx, t, hh = g['cx'], g['top'], g['hh']
    sx, sy = cx + hh * 0.55, t + hh * 1.3
    pts = [(sx, sy), (sx + 34, sy - 6), (sx + 42, sy + 20), (sx + 30, sy + 40), (sx + 4, sy + 34)]
    d = 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts)
    sel = f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 5"/>'
    for a, b in pts[1:]:
        sel += f'<circle cx="{a:.1f}" cy="{b:.1f}" r="4" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>'
    sel += f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="9" fill="#9CA3AF" stroke="{WHITE}" stroke-width="2.5"/>'
    s = screen(ph + sel + bottom_bar(SEL_ROWS, active=('手绘',)), active='select')
    s += ring(*icon_pos('select'), 18) + badge(POS['手绘'][0] + 20, POS['手绘'][1] - 12, 1)
    s += badge(sx - 22, sy - 14, 2)
    s += label(552, 140, '① 选「手绘」', YEL1, 14)
    s += label(552, 172, '拖着笔画：沿轮廓描', YEL1, 14)
    s += label(552, 204, '一下下轻点：连成直线（多边形）', YEL1, 14)
    s += label(552, 252, '② 点灰色的起点，闭合选区', YEL1, 14)
    s += label(552, 300, '要再加一块：点「添加」再圈', WHITE, 13)
    s += label(552, 330, '圈多了：点「移除」圈掉多的', WHITE, 13)
    s += note('示意图')
    save('u-sel-freehand', svg(W, H, s, '手绘选取：描线或轻点连成多边形'))


@reg
def u_feather():
    ph, g = photo()
    cx, t, hh = g['cx'], g['top'], g['hh']
    sel = f'<ellipse cx="{cx:.1f}" cy="{t + hh * 0.55:.1f}" rx="{hh * 0.55:.1f}" ry="{hh * 0.65:.1f}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 5"/>'
    pop = (f'<rect x="250" y="56" width="300" height="56" rx="14" fill="{UIPANEL}" stroke="#111827"/>'
           + slider(266, 92, 268, '羽化', 0.25))
    s = screen(ph + sel + pop + bottom_bar(SEL_ROWS, active=('椭圆', '羽化')), active='select')
    s += ring(*icon_pos('select'), 18)
    px, py, pw, phh = POS['羽化']
    s += badge(px + pw / 2, py - 14, 1) + badge(560, 84, 2)
    s += label(560, 160, '① 选区画好后点「羽化」', YEL1, 14)
    s += label(560, 192, '② 拖滑块，边缘越来越软', YEL1, 14)
    s += label(560, 240, '提亮、调色的局部选区：', WHITE, 13)
    s += label(560, 270, '　 从 10%～30% 试起', WHITE, 13)
    s += label(560, 300, '要剪下来贴走的东西：不羽化', RED1, 13)
    s += note('示意图')
    save('u-feather', svg(W, H, s, '选区羽化'))


@reg
def u_sel_save():
    ph, g = dress_photo()
    d = skirt_poly(g)
    sel = f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="6 5"/>'
    pnl = panel(560, 140, 210, 230) + text(576, 168, '选区', 16, 800, UITEXT) + text(750, 170, '+', 24, 800, UITEXT, 'middle')
    for i, n in enumerate(['选区 1', '选区 2']):
        y = 186 + i * 60
        pnl += f'<rect x="570" y="{y}" width="190" height="52" rx="8" fill="{UIBAR}"/><rect x="578" y="{y + 6}" width="40" height="40" fill="#111"/>' + dress_shape(586, y + 10, 24, 32, '#FFF', '#FFF', 1) + text(630, y + 32, n, 14, 700, UITEXT)
    s = screen(ph + sel + pnl + bottom_bar(SEL_ROWS, active=('自动',), hl='存储并加载'), active='select')
    s += ring(*icon_pos('select'), 18)
    px, py, pw, phh = POS['存储并加载']
    s += badge(px + pw / 2, py - 14, 1) + ring(750, 162, 14) + badge(724, 162, 2) + badge(560, 214, 3)
    s += label(62, 120, '① 点「存储并加载」', YEL1, 14)
    s += label(62, 152, '② 点「+」存下', YEL1, 14)
    s += label(62, 184, '③ 点列表一项就加载', YEL1, 14)
    s += label(62, 232, '长按选取图标：', WHITE, 13)
    s += label(62, 262, '重载上一次的选区', WHITE, 13)
    s += note('示意图')
    save('u-sel-save', svg(W, H, s, '存储并加载选区'))


def wall_canvas():
    sc, wall = corridor(CX, CY, CW, CH)
    return sc, wall


@reg
def u_distort():
    sc, wall = wall_canvas()
    q = sub_quad(wall, 0.18, 0.62, 0.2, 0.72)
    ps, pts = poster_quad(q)
    content = sc + f'<g opacity=".75">{ps}</g>'
    for (a, b) in pts:
        content += f'<circle cx="{a:.1f}" cy="{b:.1f}" r="7" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
    # 原始矩形位置
    content += f'<rect x="{pts[0][0] - 4:.1f}" y="{pts[0][1] - 20:.1f}" width="100" height="150" fill="none" stroke="{UIBLUE}" stroke-width="1.5" stroke-dasharray="5 4"/>'
    content += arrow(pts[1][0] + 30, pts[1][1] - 26, pts[1][0] + 6, pts[1][1] - 4, INK, 2.5)
    s = screen(content + bottom_bar(TF_ROWS, active=('扭曲',)), active='transform')
    s += ring(*icon_pos('transform'), 18) + badge(POS['扭曲'][0] + 20, POS['扭曲'][1] - 12, 1)
    s += badge(pts[1][0] + 40, pts[1][1] - 34, 2)
    s += label(552, 140, '① 变换工具，选「扭曲」', YEL1, 14)
    s += label(552, 172, '② 一个角一个角地拖，', YEL1, 14)
    s += label(552, 204, '　 让上下边对齐墙的透视线', YEL1, 14)
    s += label(552, 252, '海报层先调到 50%～70%', WHITE, 13)
    s += label(552, 282, '不透明度，透出墙来对位置', WHITE, 13)
    s += note('示意图')
    save('u-distort', svg(W, H, s, '扭曲：拖动四个角对齐墙面'))


@reg
def u_interp():
    sc, wall = wall_canvas()
    q = sub_quad(wall, 0.18, 0.62, 0.2, 0.72)
    ps, pts = poster_quad(q)
    bar = bottom_bar(TF_ROWS, active=('扭曲', '插值'))
    ix, iy, iw, ih = POS['插值']
    pop_x, pop_y = ix + iw - 150, iy - 128
    pop = (f'<rect x="{pop_x:.1f}" y="{pop_y:.1f}" width="150" height="112" rx="10" fill="{UIPANEL}" stroke="#111827"/>'
           + menu_rows(pop_x, pop_y + 4, 150, ['最近邻', '双线性', '双立体'], hl='双立体', row_h=34))
    s = screen(sc + ps + bar + pop, active='transform') + ring(*icon_pos('transform'), 18)
    s += badge(ix + iw / 2, iy - 12, 1) if False else ''
    s += badge(pop_x - 16, pop_y + 92, 2) + ringrect(ix - 3, iy + 2, iw + 6, ih - 4) + badge(ix - 14, iy + 20, 1)
    s += label(552, 150, '① 点底部的「插值」', YEL1, 14)
    s += label(552, 182, '② 选「双立体」', YEL1, 14)
    s += label(552, 230, '会被记住，以后不用每次改', WHITE, 13)
    s += label(552, 262, '按钮下的小字显示当前设置', WHITE, 13)
    s += note('示意图')
    save('u-interp', svg(W, H, s, '变换的插值选双立体'))


@reg
def u_snap():
    ph, g = photo()
    guides = (f'<line x1="{CX + CW / 2}" y1="{CY}" x2="{CX + CW / 2}" y2="{CY + CH}" stroke="{YEL}" stroke-width="2"/>'
              f'<line x1="{CX}" y1="{CY + CH / 2}" x2="{CX + CW}" y2="{CY + CH / 2}" stroke="{YEL}" stroke-width="2"/>')
    pnl = panel(66, 250, 190, 180)
    pnl += menu_rows(66, 256, 190, ['对齐', '磁性'], toggles={'对齐': True, '磁性': True}, row_h=40)
    pnl += slider(82, 366, 158, '距离', 0.4) + slider(82, 410, 158, '速度', 0.6)
    s = screen(ph + guides + pnl + bottom_bar(TF_ROWS, active=('等比', '对齐'), hl='对齐'), active='transform')
    s += ring(*icon_pos('transform'), 18) + badge(POS['对齐'][0] - 12, POS['对齐'][1] + 6, 1) + badge(268, 276, 2) + badge(268, 316, 3)
    s += label(552, 140, '① 点工具栏最左边的「对齐」', YEL1, 14)
    s += label(552, 172, '② 「对齐」：靠近时自动吸附，', YEL1, 14)
    s += label(552, 204, '　 黄线=画布中线，蓝线=其他内容', WHITE, 13)
    s += label(552, 244, '③ 「磁性」：只沿一条直线移动，', YEL1, 14)
    s += label(552, 276, '　 拖角时变成等比缩放', WHITE, 13)
    s += note('示意图')
    save('u-snap', svg(W, H, s, '对齐和磁性'))


@reg
def u_warp():
    sc, wall = wall_canvas()
    # 墙上一根圆柱，海报包在上面
    x0, x1, y0, y1 = CX + 40, CX + 120, CY + 80, CY + 250
    col = f'<rect x="{x0 - 10}" y="{CY}" width="{x1 - x0 + 20}" height="{CH}" fill="#E5E7EB" stroke="{INK}" stroke-width="2"/>'
    post = f'<path d="M{x0} {y0} Q{(x0 + x1) / 2} {y0 + 16} {x1} {y0} L{x1} {y1} Q{(x0 + x1) / 2} {y1 + 16} {x0} {y1} Z" fill="{PINK}" stroke="{INK}" stroke-width="2"/>'
    mesh = ''
    for k in (1, 2):
        yy = y0 + (y1 - y0) * k / 3
        mesh += f'<path d="M{x0} {yy:.0f} Q{(x0 + x1) / 2} {yy + 16:.0f} {x1} {yy:.0f}" fill="none" stroke="{UIBLUE}" stroke-width="1.5"/>'
        xx = x0 + (x1 - x0) * k / 3
        mesh += f'<line x1="{xx:.0f}" y1="{y0 + 12}" x2="{xx:.0f}" y2="{y1 + 12}" stroke="{UIBLUE}" stroke-width="1.5"/>'
    for (a, b) in [(x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, y0 + 8), ((x0 + x1) / 2, y1 + 8)]:
        mesh += f'<circle cx="{a}" cy="{b}" r="6" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
    s = screen(sc + col + post + mesh + bottom_bar(TF_ROWS, active=('弯曲',)), active='transform')
    s += ring(*icon_pos('transform'), 18) + badge(POS['弯曲'][0] + 20, POS['弯曲'][1] - 12, 1)
    s += label(552, 150, '① 选「弯曲」，出现网格', YEL1, 14)
    s += label(552, 182, '拖网格中间往下，', YEL1, 14)
    s += label(552, 214, '　 海报就顺着柱子弯过去', YEL1, 14)
    s += label(552, 262, '平的墙用扭曲；', WHITE, 13)
    s += label(552, 292, '柱子、旗子、衣服用弯曲', WHITE, 13)
    s += note('示意图')
    save('u-warp', svg(W, H, s, '弯曲：网格变形贴到曲面上'))


def poster_case(after):
    s = [f'<defs><clipPath id="pcl"><rect x="20" y="20" width="600" height="480"/></clipPath>'
         f'<linearGradient id="wshade" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".25"/></linearGradient></defs><g clip-path="url(#pcl)">']
    sc, wall = corridor(20, 20, 600, 480)
    s.append(sc)
    hh = 44; top = 150; feet = top + hh * 6.6
    s.append(figure(470, top, hh, top + hh * 3.6, feet, sw=2.5))
    if after:
        q = sub_quad(wall, 0.12, 0.6, 0.18, 0.62)
        ps, pts = poster_quad(q)
        s.append(ps)
        d = 'M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts) + ' Z'
        s.append(f'<path d="{d}" fill="url(#wshade)"/>')
    else:
        s.append(poster(120, 130, 150, 210))
    s.append('</g>')
    lab = '修之后：扭曲贴合墙面，再用正片叠底压一点远处的暗' if after else '修之前：海报正正地贴在画面上，像浮着的'
    s.append(label(606, 56, lab, VIO1, 14, 'end') if after else label(34, 56, lab, YEL1, 15))
    return svg(640, 520, ''.join(s), lab)


def badge_case(after):
    s = [f'<rect x="20" y="20" width="600" height="480" fill="#FFF7E6"/>']
    s.append(f'<rect x="290" y="60" width="60" height="70" fill="{SKIN}" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M110 160 Q320 110 530 160 L560 500 L80 500 Z" fill="#1E3A8A" stroke="{INK}" stroke-width="3"/>')
    s.append(f'<path d="M300 130 L320 200 L340 130" fill="{WHITE}" stroke="{INK}" stroke-width="2"/>')
    def epaulet(x, flip=False):
        g = (f'<rect x="{x - 60}" y="140" width="120" height="34" rx="8" fill="#D4A017" stroke="{INK}" stroke-width="2.5"/>'
             f'<path d="M{x - 50} 174 l0 30 M{x - 30} 174 l0 34 M{x - 10} 174 l0 36 M{x + 10} 174 l0 36 M{x + 30} 174 l0 34 M{x + 50} 174 l0 30" stroke="#D4A017" stroke-width="5"/>'
             f'<path d="M{x - 30} 157 l14 -6 l6 -12 l6 12 l14 6 l-14 6 l-6 12 l-6 -12 z" fill="{WHITE}" stroke="{INK}" stroke-width="1.5"/>')
        if flip:
            g = f'<g transform="translate({2 * x},0) scale(-1,1)">{g}</g>'
        return g
    s.append(epaulet(170))
    if after:
        s.append(epaulet(470, True))
    else:
        s.append(f'<rect x="410" y="140" width="120" height="70" rx="8" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="7 5"/>')
    lab = '修之后：复制左肩章、水平翻转、扭曲贴合右肩' if after else '修之前：右肩的肩章拍的时候掉了'
    s.append(label(606, 56, lab, VIO1, 15, 'end') if after else label(34, 56, lab, YEL1, 15))
    return svg(640, 520, ''.join(s), lab)


if __name__ == '__main__':
    for f in ALL:
        f()
    for n, fn in [('sticker', None), ('hair', wig_head), ('cheek', cheek_case), ('skirt', skirt_case), ('glow', glow_case),
                  ('dress', dress_case), ('edge', edge_case), ('poster', poster_case), ('badge', badge_case)]:
        if n == 'sticker':
            save('case-sticker-jpeg', sticker_case(False)); save('case-sticker-png', sticker_case(True))
            continue
        save(f'case-{n}-before', fn(False)); save(f'case-{n}-after', fn(True))
    print('done', len(os.listdir(OUT)))
