#!/usr/bin/env python3
"""生成网站图标和分享卡片（PNG）。改了样式后手动运行一次，生成的文件放在 static/icons/ 里随项目一起提交（Docker 构建时不运行，镜像里没有中文字体）。"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "icons"
INK, CREAM, PINK, VIO, YEL = (30, 41, 59), (255, 253, 245), (244, 114, 182), (124, 58, 237), (251, 191, 36)
FONTS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
         "/System/Library/Fonts/PingFang.ttc", "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"]


def font(size):
    for f in FONTS:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size)
            except OSError:
                pass
    return ImageFont.load_default()


def icon(n, maskable=False, bg=CREAM):
    im = Image.new("RGB", (n, n), bg)
    d = ImageDraw.Draw(im)
    pad = n * (0.22 if maskable else 0.12)
    r = (n - 2 * pad) / 2
    cx = cy = n / 2
    w = max(3, int(n * 0.05))
    d.ellipse([cx - r + w, cy - r + w * 2, cx + r + w, cy + r + w * 2], fill=INK)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PINK, outline=INK, width=w)
    sr = r * 0.3
    sx, sy = cx + r * 0.62, cy - r * 0.62
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 255), outline=INK, width=max(2, w * 2 // 3))
    return im


def card():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60 + 10, 60 + 10, W - 60 + 10, H - 60 + 10], 36, fill=VIO)
    d.rounded_rectangle([60, 60, W - 60, H - 60], 36, fill=(255, 255, 255), outline=INK, width=6)
    ic = icon(150, bg=(255, 255, 255))
    im.paste(ic, (110, 110))
    d.text((290, 120), "张宇涵的cos后期", font=font(64), fill=INK)
    d.text((290, 200), "Procreate 自学站", font=font(48), fill=INK)
    d.text((110, 330), "从零开始，用 iPad 修好一张 cos 片", font=font(44), fill=INK)
    d.text((110, 410), "46 节课 · 原理 + 分步操作 + 完整案例", font=font(34), fill=(71, 85, 105))
    d.rounded_rectangle([110, 480, 420, 540], 30, fill=YEL, outline=INK, width=4)
    d.text((140, 488), "免费 · 不用注册", font=font(32), fill=INK)
    return im


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    icon(180).save(OUT / "apple-touch-icon.png")
    icon(192).save(OUT / "icon-192.png")
    icon(512).save(OUT / "icon-512.png")
    icon(512, maskable=True).save(OUT / "icon-maskable-512.png")
    icon(32).save(OUT / "favicon-32.png")
    card().save(OUT / "share-card.png", optimize=True)


if __name__ == "__main__":
    main()
