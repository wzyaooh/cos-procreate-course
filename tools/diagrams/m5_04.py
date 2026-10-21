"""5.4 形体比例修正 的示意图。运行：python tools/diagrams/m5_04.py"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from kit import *

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'diagrams', 'm5-04')
os.makedirs(OUT, exist_ok=True)


def save(name, s):
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)


CX, CY, CW, CH = 262, 66, 276, 340   # 界面里的画布


def photo(**kw):
    return scene(CX, CY, CW, CH, **kw)


def ants(x, y, w, h):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{UIBLUE}" fill-opacity=".10" stroke="{WHITE}" stroke-width="2.5"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 6"/>')


def mask_outside(x, y, w, h):
    """选区外的半透明斜线遮罩"""
    pid = f'hatch{int(x)}{int(y)}'
    pat = (f'<defs><pattern id="{pid}" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
           f'<rect width="10" height="10" fill="#94A3B8" fill-opacity=".25"/><line x1="0" y1="0" x2="0" y2="10" stroke="#64748B" stroke-width="3" stroke-opacity=".35"/></pattern></defs>')
    s = pat
    for (rx, ry, rw, rh) in [(CX, CY, CW, y - CY), (CX, y + h, CW, CY + CH - (y + h))]:
        if rh > 0:
            s += f'<rect x="{rx}" y="{ry:.1f}" width="{rw}" height="{rh:.1f}" fill="url(#{pid})"/>'
    return s


def bbox(x, y, w, h, handles=True):
    s = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" stroke="{UIBLUE}" stroke-width="2"/>'
    if handles:
        for hx, hy in [(x, y), (x + w / 2, y), (x + w, y), (x, y + h / 2), (x + w, y + h / 2), (x, y + h), (x + w / 2, y + h), (x + w, y + h)]:
            s += f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="6" fill="{UIBLUE}" stroke="{WHITE}" stroke-width="2"/>'
    return s


# ---------- 界面：复制并锁定原图 ----------
def u_layers():
    ph, g = photo()
    lay = layers_panel([('图层 1（原图）', 'scene', 'N', True)], swiped=0, swipe_hl='复制')
    s = screen(ph + lay, active='layers')
    s += ring(*icon_pos('layers'), 18) + badge(icon_pos('layers')[0] - 26, 62, 1)
    s += badge(470 + 300 - 8 - 180 + 90, 62 + 44 + 60, 2)
    s += label(470, 200, '在原图层上向左轻滑', YEL1, 14)
    s += label(470, 232, '先点「复制」，再滑一次点「锁定」', YEL1, 14)
    s += note('示意图，按钮位置以实际界面为准')
    save('u-layers', svg(W, H, s, '在图层上向左轻滑，出现锁定、复制、删除'))


# ---------- 界面：画标尺 ----------
def u_ruler_draw():
    ph, g = photo()
    x = CX + CW * 0.86
    line = (f'<line x1="{x:.1f}" y1="{g["top"]:.1f}" x2="{x:.1f}" y2="{g["top"] + g["hh"]:.1f}" stroke="{MINT}" stroke-width="5" stroke-linecap="round"/>'
            f'<line x1="{g["cx"] - 30:.1f}" y1="{g["top"]:.1f}" x2="{x:.1f}" y2="{g["top"]:.1f}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="4 4"/>'
            f'<line x1="{g["cx"] - 30:.1f}" y1="{g["top"] + g["hh"]:.1f}" x2="{x:.1f}" y2="{g["top"] + g["hh"]:.1f}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="4 4"/>')
    s = screen(ph + line, active='brush')
    s += ring(*icon_pos('brush'), 18) + badge(icon_pos('brush')[0] - 26, 62, 1)
    s += label(x + 18, g['top'] + 8, '头顶（头骨顶，不算假发）', YEL1, 14)
    s += label(x + 18, g['top'] + g['hh'] + 6, '下巴', YEL1, 14)
    s += arrow(x + 16, g['top'] + 2, x + 4, g['top'] + 2, INK, 2)
    s += badge(x, g['top'] + g['hh'] / 2, 2)
    s += label(36, 520, '新建图层「标尺」，用细笔从头顶画到下巴', WHITE, 14)
    s += note('示意图')
    save('u-ruler-draw', svg(W, H, s, '用画笔在新图层上画出一个头长'))


def u_ruler_dup():
    ph, g = photo()
    x = CX + CW * 0.86
    line = f'<line x1="{x:.1f}" y1="{g["top"]:.1f}" x2="{x:.1f}" y2="{g["top"] + g["hh"]:.1f}" stroke="{MINT}" stroke-width="5" stroke-linecap="round"/>'
    bar_items = ['剪切', '拷贝', '全部拷贝', '复制', '剪切并粘贴', '粘贴']
    bx = 170; by = 64; s_bar = f'<rect x="{bx}" y="{by}" width="460" height="46" rx="12" fill="{UIBAR}"/>'
    xx = bx + 10
    for it in bar_items:
        w = len(it) * 15 + 20
        s_bar += f'<rect x="{xx}" y="{by + 7}" width="{w}" height="32" rx="8" fill="{UIPANEL}"/>' + text(xx + w / 2, by + 29, it, 14, 700, UITEXT, 'middle')
        if it == '复制':
            s_bar += ringrect(xx - 3, by + 4, w + 6, 38)
            hx = xx + w / 2
        xx += w + 6
    fx = CX + CW + 70
    s = screen(ph + line + s_bar + finger(fx, 230, 3, 40))
    s += badge(fx - 52, 222, 1) + badge(hx, by + 62, 2)
    s += label(fx - 50, 330, '三指在画布上向下拖', YEL1, 14)
    s += label(CX + CW + 14, by + 90, '② 点「复制」', YEL1, 14)
    s += label(CX + CW + 14, by + 120, '　 线会复制到一个新图层', YEL1, 14)
    s += note('示意图')
    save('u-ruler-dup', svg(W, H, s, '三指下滑打开拷贝并粘贴菜单，点复制'))


def u_ruler_snap():
    ph, g = photo()
    x = CX + CW * 0.86
    t, hh = g['top'], g['hh']
    lines = f'<line x1="{x:.1f}" y1="{t:.1f}" x2="{x:.1f}" y2="{t + hh:.1f}" stroke="{MINT}" stroke-width="5" stroke-linecap="round"/>'
    # 正在拖动的第二段
    lines += bbox(x - 6, t + hh + 3, 12, hh, False)
    lines += f'<line x1="{x:.1f}" y1="{t + hh + 3:.1f}" x2="{x:.1f}" y2="{t + 2 * hh + 3:.1f}" stroke="{MINT}" stroke-width="5" stroke-linecap="round"/>'
    lines += f'<line x1="{CX}" y1="{t + hh:.1f}" x2="{CX + CW}" y2="{t + hh:.1f}" stroke="{YEL}" stroke-width="1.5"/>'
    lines += f'<line x1="{x:.1f}" y1="{CY}" x2="{x:.1f}" y2="{CY + CH}" stroke="{UIBLUE}" stroke-width="1.5"/>'
    s = screen(ph + lines + bottom_bar(TF_ROWS, active=('自由变换',), hl='对齐'), active='transform')
    s += ring(*icon_pos('transform'), 18) + badge(icon_pos('transform')[0] + 26, 62, 1)
    s += label(x + 14, t + hh * 1.6, '拖到上一段的下端，自动吸附', YEL1, 14)
    s += badge(x - 20, t + hh * 1.5, 2)
    s += note('示意图')
    save('u-ruler-snap', svg(W, H, s, '用变换工具把复制的线段拖到上一段下面，打开对齐会自动吸附'))


def u_grid():
    ph, g = photo()
    # 网格线（每格一个头长）
    grid = ''
    y = g['top']
    while y < CY + CH:
        grid += f'<line x1="{CX}" y1="{y:.1f}" x2="{CX + CW}" y2="{y:.1f}" stroke="{UIBLUE}" stroke-width="1.5" stroke-opacity=".8"/>'
        y += g['hh']
    menu = actions_menu('画布', hl='编辑绘图指引', toggles={'动画协助': False, '页面辅助': False, '绘图指引': True, '参考': False})
    s = screen(ph + grid + menu, active='actions')
    s += ring(*icon_pos('actions'), 18)
    s += badge(400, 62 + 50 + 3 * 34 + 17, 2) + badge(400, 62 + 50 + 4 * 34 + 17, 3)
    s += label(560, 300, '网格尺寸调到一个头长', YEL1, 14)
    s += label(560, 332, '每条横线就是一格', YEL1, 14)
    s += note('示意图')
    save('u-grid', svg(W, H, s, '在操作、画布里打开绘图指引，再进编辑绘图指引选 2D 网格'))


# ---------- 界面：拉腿 ----------
def u_crop():
    ph, g = photo()
    menu = actions_menu('画布', hl='裁剪并调整大小')
    s = screen(ph + menu, active='actions') + ring(*icon_pos('actions'), 18)
    s += badge(400, 62 + 50 + 17, 1)
    s += label(560, 300, '脚贴着底边时，先把画布往下加高', YEL1, 14)
    s += note('示意图')
    save('u-crop', svg(W, H, s, '操作、画布、裁剪并调整大小'))


def u_sel_feet():
    ph, g = photo()
    ank = g['feet'] - g['hh'] * 0.18
    sel = mask_outside(CX, ank, CW, CY + CH - ank) + ants(CX + 1, ank, CW - 2, CY + CH - ank - 1)
    s = screen(ph + sel + bottom_bar(SEL_ROWS, active=('矩形',)), active='select')
    s += ring(*icon_pos('select'), 18) + badge(icon_pos('select')[0] + 26, 62, 1)
    s += label(CX + CW + 12, ank + 22, '从脚踝往下框到画布底边', YEL1, 14)
    s += label(CX + CW + 12, ank + 54, '左右拉满，地面一起选', YEL1, 14)
    s += badge(CX + CW + 2, ank + 6, 2)
    s += note('示意图')
    save('u-sel-feet', svg(W, H, s, '选取工具选矩形，框住脚踝以下的整条区域'))


def u_move_feet():
    shift = 30
    ph, g = photo()
    ank = g['feet'] - g['hh'] * 0.18
    # 下半部分整体下移：用 clipPath 复制一份往下画
    clip = f'<defs><clipPath id="lowpart"><rect x="{CX}" y="{ank:.1f}" width="{CW}" height="{CY + CH - ank:.1f}"/></clipPath></defs>'
    gap = f'<rect x="{CX}" y="{ank:.1f}" width="{CW}" height="{shift}" fill="#FFF7E6" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4"/>'
    moved = f'<g clip-path="url(#lowpart)" transform="translate(0,{shift})">{ph}</g>'
    content = ph + clip + gap + moved + bbox(CX + 1, ank + shift, CW - 2, CY + CH - ank - 1, True)
    s = screen(content + bottom_bar(TF_ROWS, active=('自由变换',)), active='transform')
    s += ring(*icon_pos('transform'), 18) + badge(icon_pos('transform')[0] + 26, 62, 1)
    s += arrow(CX + CW + 20, ank - 6, CX + CW + 20, ank + shift + 10, INK, 3)
    s += label(CX + CW + 34, ank + 16, '一指拖动，往下移', YEL1, 14)
    s += label(CX + CW + 34, ank + 48, '移多少 = 腿要拉长多少', YEL1, 14)
    s += label(CX - 12, ank + shift / 2 + 6, '露出下面原图层', WHITE, 13, 'end')
    s += note('示意图')
    save('u-move-feet', svg(W, H, s, '点变换工具，把脚和地面整体往下移'))


def u_sel_band():
    shift = 30
    ph, g = photo()
    ank = g['feet'] - g['hh'] * 0.18
    clip = f'<defs><clipPath id="lowpart2"><rect x="{CX}" y="{ank:.1f}" width="{CW}" height="{CY + CH - ank:.1f}"/></clipPath></defs>'
    gap = f'<rect x="{CX}" y="{ank:.1f}" width="{CW}" height="{shift}" fill="#FFF7E6" stroke="{INK}" stroke-width="1.5" stroke-dasharray="5 4"/>'
    moved = f'<g clip-path="url(#lowpart2)" transform="translate(0,{shift})">{ph}</g>'
    w = g['waist']
    sel = mask_outside(CX, w, CW, ank - w) + ants(CX + 1, w, CW - 2, ank - w)
    s = screen(ph + clip + gap + moved + sel + bottom_bar(SEL_ROWS, active=('矩形',)), active='select')
    s += ring(*icon_pos('select'), 18)
    s += label(CX + CW + 12, w + 24, '从腰线框到脚踝', YEL1, 14)
    s += label(CX + CW + 12, w + 56, '同样左右拉满', YEL1, 14)
    s += label(CX + CW + 12, w + 88, '上边缘别压在斜线上', RED1, 14)
    s += note('示意图')
    save('u-sel-band', svg(W, H, s, '再用矩形框住腰线到脚踝的横带'))


def u_stretch():
    shift = 30
    ph, g = photo()
    ank = g['feet'] - g['hh'] * 0.18
    w = g['waist']
    # 拉伸后的效果：用 transform scale 在 band 内
    k = (ank + shift - w) / (ank - w)
    clip_low = f'<defs><clipPath id="lp3"><rect x="{CX}" y="{ank:.1f}" width="{CW}" height="{CY + CH - ank:.1f}"/></clipPath><clipPath id="band3"><rect x="{CX}" y="{w:.1f}" width="{CW}" height="{ank - w:.1f}"/></clipPath></defs>'
    moved = f'<g clip-path="url(#lp3)" transform="translate(0,{shift})">{ph}</g>'
    band = f'<g transform="translate(0,{w:.2f}) scale(1,{k:.4f}) translate(0,{-w:.2f})"><g clip-path="url(#band3)">{ph}</g></g>'
    content = ph + clip_low + moved + band + bbox(CX + 1, w, CW - 2, ank + shift - w, True)
    # 插值弹窗
    bar = bottom_bar(TF_ROWS, active=('自由变换', '插值'))
    ix, iy, iw, ih = POS['插值']
    pop_x, pop_y = ix + iw - 150, iy - 128
    pop = (f'<rect x="{pop_x:.1f}" y="{pop_y:.1f}" width="150" height="112" rx="10" fill="{UIPANEL}" stroke="#111827"/>'
           + menu_rows(pop_x, pop_y + 4, 150, ['最近邻', '双线性', '双立体'], hl='双立体', row_h=34))
    s = screen(content + bar + pop, active='transform')
    s += ring(*icon_pos('transform'), 18)
    s += arrow(CX + CW / 2, ank - 22, CX + CW / 2, ank + shift - 4, INK, 3)
    s += badge(CX - 22, ank + shift / 2, 1)
    s += label(36, ank - 40, '① 拖选框下边中间的点，', YEL1, 14)
    s += label(36, ank - 8, '　 往下拉，接上脚', YEL1, 14)
    s += badge(pop_x - 16, pop_y + 92, 2)
    s += label(pop_x - 36, pop_y + 40, '② 插值选「双立体」', YEL1, 14, 'end')
    s += note('示意图')
    save('u-stretch', svg(W, H, s, '自由变换拖动选框下边，插值选双立体'))


# ---------- 界面：缩头 ----------
def head_outline(g):
    cx, t, hh = g['cx'], g['top'], g['hh']
    pts = []
    for a in range(0, 361, 15):
        r = math.radians(a)
        pts.append((cx + math.cos(r) * hh * 0.85, t + hh * 0.75 + math.sin(r) * hh * 1.05))
    return 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts) + ' Z'


def u_head_sel():
    ph, g = photo(wig_scale=1.25)
    d = head_outline(g)
    sel = f'<path d="{d}" fill="{UIBLUE}" fill-opacity=".12" stroke="{WHITE}" stroke-width="2.5"/><path d="{d}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 6"/>'
    bar = bottom_bar(SEL_ROWS, active=('手绘',), hl='拷贝并粘贴')
    s = screen(ph + sel + bar, active='select')
    s += ring(*icon_pos('select'), 18) + badge(icon_pos('select')[0] + 26, 62, 1)
    px, py, pw, phh = POS['拷贝并粘贴']
    s += label(g['cx'] + g['hh'] * 1.0, g['top'] + 20, '沿假发外轮廓圈，', YEL1, 14)
    s += label(g['cx'] + g['hh'] * 1.0, g['top'] + 52, '下面圈到脖子中段', YEL1, 14)
    s += badge(g['cx'] + g['hh'] * 0.9, g['top'] + g['hh'] * 1.7, 2)
    s += badge(px + pw / 2, py - 14, 3)
    s += note('示意图')
    save('u-head-sel', svg(W, H, s, '手绘选取圈出头部，点拷贝并粘贴'))


def u_head_scale():
    ph, g = photo(wig_scale=1.25)
    cx, t, hh = g['cx'], g['top'], g['hh']
    bx, by, bw, bh = cx - hh * 0.85, t - hh * 0.3, hh * 1.7, hh * 2.1
    k = 0.95
    nw, nh = bw * k, bh * k
    nx, ny = cx - nw / 2, by + bh - nh
    content = ph + f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="none" stroke="{UIBLUE}" stroke-width="1.5" stroke-dasharray="4 4"/>' + bbox(nx, ny, nw, nh)
    s = screen(content + bottom_bar(TF_ROWS, active=('等比',)), active='transform')
    s += ring(*icon_pos('transform'), 18)
    s += arrow(bx + bw + 14, by - 8, nx + nw + 6, ny + 2, INK, 2.5)
    s += label(bx + bw + 20, by + 10, '拖角上的点，先缩 3%～5%', YEL1, 14)
    s += label(bx + bw + 20, by + 42, '再往下挪，让下巴接上脖子', YEL1, 14)
    s += note('示意图')
    save('u-head-scale', svg(W, H, s, '等比模式缩小头部'))


def u_clone():
    ph, g = photo(wig_scale=1.25)
    cx, t, hh = g['cx'], g['top'], g['hh']
    # 克隆圆盘 + 正在涂的笔触
    disc_x, disc_y = cx - hh * 1.9, t + hh * 0.6
    content = ph + (f'<circle cx="{disc_x:.1f}" cy="{disc_y:.1f}" r="16" fill="none" stroke="{WHITE}" stroke-width="4"/>'
                    f'<circle cx="{disc_x:.1f}" cy="{disc_y:.1f}" r="16" fill="none" stroke="{INK}" stroke-width="2"/>'
                    f'<line x1="{disc_x - 8:.1f}" y1="{disc_y:.1f}" x2="{disc_x + 8:.1f}" y2="{disc_y:.1f}" stroke="{INK}" stroke-width="2"/>'
                    f'<line x1="{disc_x:.1f}" y1="{disc_y - 8:.1f}" x2="{disc_x:.1f}" y2="{disc_y + 8:.1f}" stroke="{INK}" stroke-width="2"/>'
                    f'<path d="{head_outline(g)}" fill="none" stroke="{PINK}" stroke-width="5" stroke-opacity=".55" transform="translate({cx:.1f},{t + hh:.1f}) scale(1.08) translate({-cx:.1f},{-(t + hh):.1f})"/>'
                    f'<path d="M{cx - hh * 0.95:.1f} {t + hh * 0.2:.1f} q-8 25 0 50" fill="none" stroke="#FFF7E6" stroke-width="12" stroke-linecap="round"/>')
    s = screen(content + tool_sliders([('画笔尺寸', 0.25), ('强度', 1.0)]), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += label(36, disc_y + 60, '圆盘放在旁边干净的背景上', YEL1, 14)
    s += label(36, disc_y + 92, '长按圆盘可以锁定取样点', YEL1, 14)
    s += label(cx + hh * 1.1, t + hh * 0.4, '粉色虚影：缩头后露出来的旧轮廓', YEL1, 14)
    s += label(cx + hh * 1.1, t + hh * 0.4 + 32, '在它上面涂，用背景盖掉', YEL1, 14)
    s += badge(disc_x, disc_y - 30, 1) + badge(cx - hh * 0.95, t + hh * 0.05, 2)
    save('u-clone', svg(W, H, s, '克隆工具：圆盘取样，在旧轮廓上涂抹盖掉'))


# ---------- 界面：液化 ----------
BONES = ['肩', '手肘', '手腕', '髋', '膝盖', '脚踝']


def bone_points(g):
    cx, t, hh, hip = g['cx'], g['top'], g['hh'], g['hip']
    ank = g['feet'] - hh * 0.18
    sh_y = t + hh * 1.35
    pts = {'肩': (cx + hh * 0.8, sh_y), '手肘': (cx + hh * 0.98, t + hh * 2.4), '手腕': (cx + hh * 0.92, hip - hh * 0.15),
           '髋': (cx + hh * 0.85, hip + hh * 0.1), '膝盖': (cx + hh * 0.17, hip + (ank - hip) * 0.5), '脚踝': (cx + hh * 0.17, ank)}
    return pts


def u_liquify():
    ph, g = photo()
    pts = bone_points(g)
    content = ph
    for name, (x, y) in pts.items():
        content += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{RED}" stroke="{WHITE}" stroke-width="2"/>'
    # 推的笔刷范围
    wx, wy = g['cx'] - g['hh'] * 0.55, g['waist'] - g['hh'] * 0.3
    content += f'<circle cx="{wx:.1f}" cy="{wy:.1f}" r="{g["hh"] * 0.8:.1f}" fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-dasharray="5 4"/>'
    content += arrow(wx - 10, wy, wx + 14, wy, VIO7, 3, marker='arwv')
    s = screen(content + tool_sliders([('尺寸', 0.6), ('压力', 0.2), ('失真', 0.0), ('动力', 0.0)], mode='推', buttons=('调整', '重置')), active='adjust')
    s += ring(*icon_pos('adjust'), 18)
    s += label(CX + CW + 10, pts['膝盖'][1] - 40, '红点：骨点，不要推平', RED1, 14)
    s += label(66, wy - 82, '笔刷要比推的部位宽', YEL1, 14)
    s += label(66, wy - 50, '压力 10%～30%', YEL1, 14)
    s += label(66, wy - 18, '一次只推一点点', YEL1, 14)
    save('u-liquify', svg(W, H, s, '液化：推模式，尺寸大、压力低，避开骨点'))


def u_flip():
    ph, g = photo()
    menu = actions_menu('画布', hl='水平翻转画布', toggles={'动画协助': False, '页面辅助': False, '绘图指引': False, '参考': True})
    s = screen(ph + menu, active='actions') + ring(*icon_pos('actions'), 18)
    s += badge(400, 62 + 50 + 6 * 34 + 17, 1) + badge(400, 62 + 50 + 5 * 34 + 17, 2)
    s += label(560, 300, '① 翻转后检查比例和歪斜', YEL1, 14)
    s += label(560, 332, '② 参考窗口：放大时也看得到全图', YEL1, 14)
    s += note('示意图')
    save('u-flip', svg(W, H, s, '操作、画布：水平翻转画布和参考'))


# ---------- 原理图 ----------
def p_camera():
    Wd, Hd = 760, 420
    s = []
    for col, (cam_h, title, fill) in enumerate([(1.9, '俯拍：镜头比头还高', RED1), (1.0, '平拍：镜头在腰部高度', MINT1)]):
        ox = 20 + col * 380
        s.append(f'<rect x="{ox}" y="10" width="360" height="400" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(label(ox + 16, 44, title, fill, 15))
        ground = 316; scale = 120   # 1 米 = 120px
        px = ox + 270
        # 人（侧面简笔）
        s.append(f'<line x1="{ox + 20}" y1="{ground}" x2="{ox + 340}" y2="{ground}" stroke="{INK}" stroke-width="2.5"/>')
        top = ground - 1.65 * scale
        s.append(f'<circle cx="{px}" cy="{top + 14}" r="14" fill="{SKIN}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(f'<line x1="{px}" y1="{top + 28}" x2="{px}" y2="{ground - 0.85 * scale}" stroke="{INK}" stroke-width="5"/>')
        s.append(f'<line x1="{px}" y1="{ground - 0.85 * scale}" x2="{px - 8}" y2="{ground}" stroke="{INK}" stroke-width="5"/><line x1="{px}" y1="{ground - 0.85 * scale}" x2="{px + 8}" y2="{ground}" stroke="{INK}" stroke-width="5"/>')
        # 相机
        cx_ = ox + 46; cy_ = ground - cam_h * scale
        s.append(f'<rect x="{cx_ - 16}" y="{cy_ - 11}" width="32" height="22" rx="4" fill="{INK}"/><circle cx="{cx_ + 6}" cy="{cy_}" r="6" fill="{VIO2}"/>')
        s.append(f'<line x1="{cx_}" y1="{cy_ + 11}" x2="{cx_}" y2="{ground}" stroke="{MUTED}" stroke-width="2" stroke-dasharray="4 4"/>')
        s.append(text(cx_ + 8, (cy_ + ground) / 2, f'{cam_h} 米', 13, 700, MUTED))
        # 到头、到脚的距离
        dist = 2.0
        dh = math.hypot(dist, cam_h - 1.6); df = math.hypot(dist, cam_h)
        s.append(f'<line x1="{cx_ + 12}" y1="{cy_}" x2="{px}" y2="{top + 14}" stroke="{VIO7}" stroke-width="2.5"/>')
        s.append(f'<line x1="{cx_ + 12}" y1="{cy_}" x2="{px}" y2="{ground - 4}" stroke="{PINK}" stroke-width="2.5"/>')
        s.append(text(ox + 20, 356, f'到头 {dh:.2f} 米，到脚 {df:.2f} 米', 14, 700))
        s.append(text(ox + 20, 382, f'头的放大比例是脚的 {df / dh:.2f} 倍', 14, 400, MUTED))
    save('p-camera', svg(Wd, Hd, ''.join(s), '镜头高度和人物比例：俯拍时头离镜头近、脚离得远'))


def p_lines():
    Wd, Hd = 760, 370
    s = []
    for col, (title, stretched) in enumerate([('原图', False), ('只把中间横带往下拉长', True)]):
        ox = 20 + col * 380
        s.append(f'<rect x="{ox}" y="10" width="360" height="350" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(label(ox + 16, 44, title, YEL1 if not stretched else VIO1, 15))
        x0, y0, w, h = ox + 30, 70, 300, 220
        b0, b1 = y0 + 70, y0 + 150      # 横带范围（原图坐标）
        k = 1.35 if stretched else 1.0
        def Y(y):
            if y <= b0: return y
            if y <= b1: return b0 + (y - b0) * k
            return b1 + (b1 - b0) * (k - 1) + (y - b1)
        # 竖线
        for vx in (x0 + 40, x0 + 260):
            s.append(f'<line x1="{vx}" y1="{Y(y0):.1f}" x2="{vx}" y2="{Y(y0 + h):.1f}" stroke="{INK}" stroke-width="3"/>')
        # 斜线（透视地砖线），按分段映射画折线
        for sx in (x0 + 90, x0 + 150, x0 + 210):
            pts = []
            for i in range(0, 41):
                yy = y0 + h * i / 40
                xx = x0 + 150 + (sx - (x0 + 150)) * (yy - y0) / h * 1.6
                pts.append((xx, Y(yy)))
            s.append('<polyline points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts) + f'" fill="none" stroke="{VIO7}" stroke-width="2.5"/>')
        # 横线
        for hy in (y0 + 30, y0 + 110, y0 + 190):
            s.append(f'<line x1="{x0}" y1="{Y(hy):.1f}" x2="{x0 + w}" y2="{Y(hy):.1f}" stroke="{MUTED}" stroke-width="2"/>')
        s.append(f'<rect x="{x0 - 8}" y="{Y(b0):.1f}" width="{w + 16}" height="{Y(b1) - Y(b0):.1f}" fill="{VIO}" fill-opacity=".1" stroke="{VIO}" stroke-width="2" stroke-dasharray="6 5"/>')
        if stretched:
            s.append(label(x0 + 150, 346, '红圈处：斜线在选区边缘折弯', RED1, 13, 'middle'))
            s.append(f'<circle cx="{x0 + 150 + (60) * (b0 - y0) / h * 1.6:.1f}" cy="{Y(b0):.1f}" r="9" fill="none" stroke="{RED}" stroke-width="3"/>')
            s.append(f'<circle cx="{x0 + 150 + (-60) * (b0 - y0) / h * 1.6:.1f}" cy="{Y(b0):.1f}" r="9" fill="none" stroke="{RED}" stroke-width="3"/>')
    save('p-lines', svg(Wd, Hd, ''.join(s), '纵向拉伸：竖线仍然笔直，横线仍然水平，斜线在选区边缘折弯'))


def p_bones():
    Wd, Hd = 760, 300
    s = []
    for col, (title, flat, fill) in enumerate([('保留骨点：膝盖有转折', False, MINT1), ('推平了：像一根面条', True, RED1)]):
        ox = 20 + col * 380
        s.append(f'<rect x="{ox}" y="10" width="360" height="280" rx="16" fill="{WHITE}" stroke="{INK}" stroke-width="2.5"/>')
        s.append(label(ox + 16, 44, title, fill, 15))
        cx = ox + 180
        if not flat:
            left = f'M{cx - 34} 70 Q{cx - 40} 120 {cx - 30} 160 Q{cx - 38} 172 {cx - 30} 186 Q{cx - 34} 230 {cx - 22} 270'
            right = f'M{cx + 34} 70 Q{cx + 32} 120 {cx + 26} 158 Q{cx + 36} 172 {cx + 26} 188 Q{cx + 30} 230 {cx + 20} 270'
        else:
            left = f'M{cx - 30} 70 Q{cx - 28} 170 {cx - 22} 270'
            right = f'M{cx + 30} 70 Q{cx + 28} 170 {cx + 20} 270'
        s.append(f'<path d="{left}" fill="none" stroke="{INK}" stroke-width="3.5"/><path d="{right}" fill="none" stroke="{INK}" stroke-width="3.5"/>')
        if not flat:
            s.append(f'<circle cx="{cx + 32}" cy="173" r="16" fill="none" stroke="{MINT}" stroke-width="3"/>')
            s.append(label(cx + 56, 178, '膝盖骨的凸起', MINT1, 13))
        else:
            s.append(f'<circle cx="{cx + 28}" cy="173" r="16" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="4 3"/>')
            s.append(label(cx + 52, 178, '转折没了', RED1, 13))
    save('p-bones', svg(Wd, Hd, ''.join(s), '骨点是轮廓上的转折，推平后会显得软、显胖'))


# ---------- 案例图 ----------
def case_wide(after):
    Wd, Hd = 640, 520
    x, y, w, h = 20, 20, 600, 480
    s = [f'<defs><clipPath id="cw{int(after)}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath></defs><g clip-path="url(#cw{int(after)})">', f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFF7E6"/>']
    # 背景竖线（立柱），广角时向外倾斜
    lean = 0 if after else 18
    for px in (60, 580):
        dx = -lean if px < 300 else lean
        s.append(f'<line x1="{px + dx}" y1="{y}" x2="{px - dx * 0.3}" y2="{y + h}" stroke="{INK}" stroke-width="6"/>')
    feet = 470
    s.append(f'<rect x="{x}" y="{feet}" width="{w}" height="{y + h - feet}" fill="{FLOOR}"/><line x1="{x}" y1="{feet}" x2="{x + w}" y2="{feet}" stroke="{INK}" stroke-width="2.5"/>')
    hh = 64
    top = 60
    s.append(figure(300, top, hh, top + hh * 3.6, top + hh * 6.6, sw=3, hand_scale=(1.0 if after else 1.9), hand_side=1, weapon=True, arm_raise=True))
    s.append('</g>')
    lab = '修之后：手和武器缩回正常大小，立柱竖直' if after else '修之前：手和剑伸向镜头，被放得很大'
    s.append(label(606, 56, lab, VIO1, 16, 'end') if after else label(34, 56, lab, YEL1, 16))
    return svg(Wd, Hd, ''.join(s), lab)


def case_hunch(after):
    Wd, Hd = 640, 520
    x, y, w, h = 20, 20, 600, 480
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFF7E6"/>', door(70, 80, 130, 470)]
    feet = 470
    s.append(f'<rect x="{x}" y="{feet}" width="{w}" height="{y + h - feet}" fill="{FLOOR}"/><line x1="{x}" y1="{feet}" x2="{x + w}" y2="{feet}" stroke="{INK}" stroke-width="2.5"/>')
    hh = 60
    top = feet - hh * 7.0 + (0 if after else 0)
    s.append(figure(360, top, hh, top + hh * 3.6, feet, sw=3, hunch=(0.25 if after else 1.0)))
    off = hh * 0.32 * (0.25 if after else 1.0)
    s.append(ruler(560, top + off, hh, (feet - top - off) / hh, numbers=False))
    lab = '修之后：肩往后收、头回正，看着高了' if after else '修之前：含胸、头前伸，看着矮'
    s.append(label(606, 56, lab, VIO1, 16, 'end') if after else label(34, 56, lab, YEL1, 16))
    return svg(Wd, Hd, ''.join(s), lab)


if __name__ == '__main__':
    for f in [u_layers, u_ruler_draw, u_ruler_dup, u_ruler_snap, u_grid, u_crop, u_sel_feet, u_move_feet, u_sel_band, u_stretch,
              u_head_sel, u_head_scale, u_clone, u_liquify, u_flip, p_camera, p_lines, p_bones]:
        f()
    save('case-wide-before', case_wide(False)); save('case-wide-after', case_wide(True))
    save('case-hunch-before', case_hunch(False)); save('case-hunch-after', case_hunch(True))
    print('done', len(os.listdir(OUT)))
