INK='#1E293B'; CREAM='#FFFDF5'; VIO='#8B5CF6'; VIO1='#EDE9FE'; VIO2='#C4B5FD'; PINK='#F472B6'; PINK1='#FCE7F3'; MINT='#34D399'; MINT1='#D1FAE5'; YEL='#FBBF24'; YEL1='#FEF3C7'; SKIN='#FDE2CF'; MUTED='#64748B'
FONT='system-ui,-apple-system,&quot;PingFang SC&quot;,&quot;Microsoft YaHei&quot;,sans-serif'
import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','static','diagrams')+'/'
def svg(w,h,body,title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}" font-family="{FONT}"><title>{title}</title><rect width="{w}" height="{h}" fill="{CREAM}"/>{body}</svg>'
def figure(cx, top, h, hip_y, feet_y, scale=1.0, head_h=None, head_top=None, shoes=True, ankle_y=None):
    """简化人物：头/假发、躯干、裙、腿、鞋。h=上半身基准头长；head_h/head_top 允许单独缩头"""
    hh = head_h or h; ht = head_top if head_top is not None else top
    s=[]
    sw=3*scale
    # 假发后发
    s.append(f'<path d="M{cx-hh*0.62} {ht+hh*0.45} Q{cx-hh*0.75} {ht+hh*1.6} {cx-hh*0.5} {ht+hh*1.95} L{cx+hh*0.5} {ht+hh*1.95} Q{cx+hh*0.75} {ht+hh*1.6} {cx+hh*0.62} {ht+hh*0.45} Z" fill="{PINK}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    chin = ht+hh
    sh_y = top + h*1.35
    waist_y = top + h*2.9
    # 脖子
    s.append(f'<rect x="{cx-h*0.13}" y="{chin-4}" width="{h*0.26}" height="{sh_y-chin+8}" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>')
    # 腿
    leg_w=h*0.3; ankle=ankle_y if ankle_y is not None else feet_y-h*0.18
    for dx in (-h*0.28, h*0.02):
        s.append(f'<rect x="{cx+dx}" y="{hip_y-6}" width="{leg_w}" height="{ankle-hip_y+6}" rx="{leg_w*0.4}" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>')
        ky = hip_y + (ankle-hip_y)*0.5
        s.append(f'<path d="M{cx+dx+leg_w*0.25} {ky} q{leg_w*0.25} 5 {leg_w*0.5} 0" fill="none" stroke="{INK}" stroke-width="{sw*0.7}" stroke-linecap="round"/>')
    # 鞋（尺寸固定，不随拉伸变化）
    for dx in ((-h*0.13, h*0.17) if shoes else ()):
        s.append(f'<ellipse cx="{cx+dx}" cy="{feet_y-h*0.09}" rx="{h*0.24}" ry="{h*0.11}" fill="{INK}"/>')
    # 躯干
    s.append(f'<path d="M{cx-h*0.8} {sh_y} L{cx+h*0.8} {sh_y} L{cx+h*0.5} {waist_y} L{cx-h*0.5} {waist_y} Z" fill="{VIO2}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    # 手臂
    for sgn in (-1,1):
        s.append(f'<path d="M{cx+sgn*h*0.78} {sh_y+4} Q{cx+sgn*h*1.0} {waist_y-h*0.4} {cx+sgn*h*0.92} {hip_y-h*0.15}" fill="none" stroke="{INK}" stroke-width="{h*0.24}" stroke-linecap="round"/>')
        s.append(f'<path d="M{cx+sgn*h*0.78} {sh_y+4} Q{cx+sgn*h*1.0} {waist_y-h*0.4} {cx+sgn*h*0.92} {hip_y-h*0.15}" fill="none" stroke="{SKIN}" stroke-width="{h*0.24-2*sw}" stroke-linecap="round"/>')
    # 裙
    s.append(f'<path d="M{cx-h*0.5} {waist_y} L{cx+h*0.5} {waist_y} L{cx+h*0.9} {hip_y+h*0.1} L{cx-h*0.9} {hip_y+h*0.1} Z" fill="{VIO}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    s.append(f'<line x1="{cx-h*0.5}" y1="{waist_y}" x2="{cx+h*0.5}" y2="{waist_y}" stroke="{INK}" stroke-width="{sw*2}"/>')
    # 头
    s.append(f'<ellipse cx="{cx}" cy="{ht+hh*0.55}" rx="{hh*0.4}" ry="{hh*0.47}" fill="{SKIN}" stroke="{INK}" stroke-width="{sw}"/>')
    # 刘海
    s.append(f'<path d="M{cx-hh*0.55} {ht+hh*0.55} Q{cx-hh*0.5} {ht-hh*0.08} {cx} {ht-hh*0.02} Q{cx+hh*0.5} {ht-hh*0.08} {cx+hh*0.55} {ht+hh*0.55} Q{cx+hh*0.2} {ht+hh*0.2} {cx-hh*0.1} {ht+hh*0.32} Q{cx-hh*0.3} {ht+hh*0.25} {cx-hh*0.55} {ht+hh*0.55} Z" fill="{PINK}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>')
    # 眼
    for dx in (-hh*0.16, hh*0.16):
        s.append(f'<circle cx="{cx+dx}" cy="{ht+hh*0.62}" r="{hh*0.05}" fill="{INK}"/>')
    return ''.join(s)

def ratio(after):
    W,H=640,560
    top=40; h=64
    hip=top+h*3.6
    feet_before=top+6.4*h
    if after:
        stretch=(feet_before-hip)*0.12
        feet=feet_before+stretch
        hh=h*0.96; ht=top+(h-hh)
        heads=(feet-ht)/hh
    else:
        feet=feet_before; hh=h; ht=top; heads=6.4
    b=[]
    # 门框与墙
    b.append(f'<rect x="60" y="70" width="120" height="{feet-70}" fill="{YEL1}" stroke="{INK}" stroke-width="3"/>')
    b.append(f'<rect x="74" y="84" width="92" height="{feet-84}" fill="none" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<circle cx="154" cy="{(70+feet)/2+20}" r="5" fill="{INK}"/>')
    # 地面
    b.append(f'<rect x="0" y="{feet}" width="{W}" height="{H-feet}" fill="#E2E8F0"/>')
    b.append(f'<line x1="0" y1="{feet}" x2="{W}" y2="{feet}" stroke="{INK}" stroke-width="3"/>')
    b.append(figure(320, top, h, hip, feet, head_h=hh, head_top=ht))
    # 标尺
    rx=500; n=int(heads); 
    for i in range(n):
        y=ht+i*hh
        b.append(f'<rect x="{rx}" y="{y}" width="26" height="{hh}" fill="{MINT if i%2==0 else "#fff"}" stroke="{INK}" stroke-width="2.5"/>')
        b.append(f'<text x="{rx+40}" y="{y+hh/2+7}" font-size="20" font-weight="800" fill="{INK}">{i+1}</text>')
    rem=heads-n
    y=ht+n*hh
    b.append(f'<rect x="{rx}" y="{y}" width="26" height="{rem*hh}" fill="{MINT if n%2==0 else "#fff"}" stroke="{INK}" stroke-width="2.5" stroke-dasharray="5 4"/>')
    b.append(f'<line x1="{rx-14}" y1="{ht}" x2="{rx+26}" y2="{ht}" stroke="{INK}" stroke-width="2" stroke-dasharray="4 4"/>')
    # 标签
    lab = f'修之后：约 {heads:.1f} 头身' if after else f'修之前：约 {heads:.1f} 头身'
    lw=len(lab)*19+28; lx = (W-20-lw) if after else 20
    b.append(f'<rect x="{lx}" y="16" width="{lw}" height="40" rx="20" fill="{VIO1 if after else YEL1}" stroke="{INK}" stroke-width="2.5"/>')
    b.append(f'<text x="{lx+14}" y="43" font-size="20" font-weight="800" fill="{INK}">{lab}</text>')
    return svg(W,H,''.join(b), lab), heads

for after, name in ((False,'ratio-before'),(True,'ratio-after')):
    s, hd = ratio(after); open(OUT+name+'.svg','w').write(s); print(name, round(hd,2))

# 液化图层结构
def layers():
    W,H=640,380; b=[]
    items=[('人物','只在这一层液化',VIO1,VIO),('背景修补','用克隆盖掉露出来的旧轮廓',MINT1,MINT),('原图','锁定，不动',YEL1,YEL)]
    for i,(name,desc,fill,acc) in enumerate(items):
        y=40+i*105; x=40+i*24
        b.append(f'<rect x="{x+6}" y="{y+6}" width="330" height="86" rx="14" fill="{INK}"/>')
        b.append(f'<rect x="{x}" y="{y}" width="330" height="86" rx="14" fill="{fill}" stroke="{INK}" stroke-width="3"/>')
        # 缩略图
        b.append(f'<rect x="{x+14}" y="{y+13}" width="80" height="60" rx="6" fill="#fff" stroke="{INK}" stroke-width="2"/>')
        if i!=1: b.append(f'<path d="M{x+44} {y+68} q-4 -22 6 -36 q4 -10 10 0 q10 14 6 36 z" fill="{PINK if i==0 else VIO2}" stroke="{INK}" stroke-width="1.5"/>')
        if i>=1:
            b.append(f'<line x1="{x+30}" y1="{y+16}" x2="{x+30}" y2="{y+70}" stroke="{INK}" stroke-width="2"/>')
            b.append(f'<line x1="{x+78}" y1="{y+16}" x2="{x+78}" y2="{y+70}" stroke="{INK}" stroke-width="2"/>')
        b.append(f'<text x="{x+112}" y="{y+38}" font-size="22" font-weight="800" fill="{INK}">{name}</text>')
        b.append(f'<text x="{x+112}" y="{y+66}" font-size="16" fill="{INK}">{desc}</text>')
        if i==2:
            b.append(f'<g transform="translate({x+296},{y+16})"><rect x="0" y="10" width="20" height="16" rx="3" fill="{INK}"/><path d="M4 10 v-4 a6 6 0 0 1 12 0 v4" fill="none" stroke="{INK}" stroke-width="3"/></g>')
    b.append(f'<text x="460" y="70" font-size="16" font-weight="700" fill="{MUTED}">上</text><line x1="468" y1="80" x2="468" y2="300" stroke="{MUTED}" stroke-width="2.5" marker-end="url(#ar2)"/><text x="460" y="325" font-size="16" font-weight="700" fill="{MUTED}">下</text>')
    defs=f'<defs><marker id="ar2" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker></defs>'
    return svg(W,H,defs+''.join(b),'液化时的图层结构')
open(OUT+'liquify-layers.svg','w').write(layers())

# 直方图
import math
def hist():
    W,H=720,270; b=[]; pw=210; gap=30
    shapes=[('欠曝',lambda t: 0.95*math.exp(-((t-0.12)/0.11)**2)+0.25*math.exp(-((t-0.35)/0.12)**2), None),
            ('正常',lambda t: 0.55*math.exp(-((t-0.35)/0.16)**2)+0.7*math.exp(-((t-0.62)/0.14)**2)+0.15, None),
            ('过曝',lambda t: 0.3*math.exp(-((t-0.5)/0.18)**2)+0.55*math.exp(-((t-0.82)/0.1)**2), 1.0)]
    for i,(name,f,spike) in enumerate(shapes):
        x0=15+i*(pw+gap); y0=20; ph=170
        b.append(f'<rect x="{x0}" y="{y0}" width="{pw}" height="{ph}" rx="10" fill="#fff" stroke="{INK}" stroke-width="2.5"/>')
        pts=[]
        for k in range(101):
            t=k/100; v=f(t)
            if t<0.02 and name=='欠曝': v=1.0
            pts.append((x0+8+t*(pw-16), y0+ph-10-min(v,1.0)*(ph-30)))
        d=f'M{x0+8} {y0+ph-10} '+' '.join(f'L{x:.1f} {y:.1f}' for x,y in pts)+f' L{x0+pw-8} {y0+ph-10} Z'
        b.append(f'<path d="{d}" fill="{VIO2}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>')
        if spike:
            b.append(f'<rect x="{x0+pw-16}" y="{y0+18}" width="8" height="{ph-28}" fill="{INK}"/>')
            b.append(f'<text x="{x0+pw-22}" y="{y0+40}" text-anchor="end" font-size="14" font-weight="800" fill="#B91C1C">贴墙</text>')
        if name=='欠曝':
            b.append(f'<rect x="{x0+8}" y="{y0+20}" width="7" height="{ph-30}" fill="{INK}"/>')
        b.append(f'<text x="{x0+8}" y="{y0+ph+22}" font-size="14" fill="{MUTED}">暗</text><text x="{x0+pw-8}" y="{y0+ph+22}" text-anchor="end" font-size="14" fill="{MUTED}">亮</text>')
        col={'欠曝':YEL1,'正常':MINT1,'过曝':'#FEE2E2'}[name]
        b.append(f'<rect x="{x0+pw/2-40}" y="{y0+ph+30}" width="80" height="32" rx="16" fill="{col}" stroke="{INK}" stroke-width="2"/>')
        b.append(f'<text x="{x0+pw/2}" y="{y0+ph+52}" text-anchor="middle" font-size="17" font-weight="800" fill="{INK}">{name}</text>')
    return svg(W,H,''.join(b),'三种常见直方图')
open(OUT+'histogram.svg','w').write(hist())
print('ok')
