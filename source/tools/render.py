#!/usr/bin/env python3
"""Render the category icons and the social card with headless Chromium (playwright).
python3 tools/render.py"""
import os, base64
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O = os.path.join(ROOT, "assets", "img")
G, Y, C = "#0B3D26", "#D4A12A", "#FBF4E4"
ST = f'fill="none" stroke="{Y}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"'
SC = f'fill="none" stroke="{C}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"'
ICONS = {
    "building": f'<path {ST} d="M40 92 96 50l56 42"/><path {SC} d="M58 84v62h76V84"/><path {SC} d="M86 146v-30h20v30"/><path {ST} d="M126 56v18"/>',
    "sitework": f'<path {SC} d="M44 146 80 50M148 146 112 50"/><path {ST} d="M96 58v14M96 92v16M96 128v16"/><path {SC} d="M36 146h120"/>',
    "specialty": f'<path {SC} d="M46 138h100M46 112h100M46 86h100"/><path {SC} d="M70 86v26M120 86v26M96 112v26"/><path {ST} d="M118 40l34 34-16 6-24-24z"/>',
    "electrical": f'<path {ST} d="M106 36 62 104h34l-10 52 44-70H96z"/>',
    "plumbing": f'<path {SC} d="M40 70h52a18 18 0 0 1 18 18v30"/><path {SC} d="M40 92h44v26"/><path {ST} d="M110 132c0 12-8 18-16 18s-16-6-16-18c0-10 16-26 16-26s16 16 16 26z"/><path {SC} d="M132 52h20"/>',
    "local": f'<path {SC} d="M52 112a44 44 0 0 1 88 0"/><path {ST} d="M40 116h112"/><path {SC} d="M96 68v18"/><path {SC} d="M70 140h52"/>',
    "business": f'<path {SC} d="M48 70h96v74H48z"/><path {ST} d="M78 70V56h36v14"/><path {SC} d="M48 100h96"/><path {ST} d="M90 100v12h12v-12"/>',
    "services": f'<path {SC} d="M62 40h50l22 22v90H62z"/><path {SC} d="M112 40v22h22"/><path {ST} d="M78 108l14 14 26-30"/>',
}


def tile(svg):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192"><rect width="192" height="192" rx="44" fill="{G}"/>{svg}</svg>'


def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 192, "height": 192}, device_scale_factor=1)
        for k, v in ICONS.items():
            pg.set_content(f'<html><body style="margin:0;background:transparent">{tile(v)}</body></html>')
            fp = os.path.join(O, f"cat-{k}.png")
            pg.screenshot(path=fp, omit_background=True, clip={"x": 0, "y": 0, "width": 192, "height": 192})
            Image.open(fp).save(fp.replace(".png", ".webp"), quality=90)
        hero = base64.b64encode(open(os.path.join(O, "hero.jpg"), "rb").read()).decode()
        logo = base64.b64encode(open(os.path.join(O, "logo-nav-dark.png"), "rb").read()).decode()
        og = f'''<html><head><link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700&family=Inter:wght@500;600&display=swap" rel="stylesheet"></head>
<body style="margin:0;width:1200px;height:630px;position:relative;overflow:hidden;background:#0A3A22;font-family:Inter,sans-serif">
<img src="data:image/jpeg;base64,{hero}" style="position:absolute;inset:0;width:1200px;height:630px;object-fit:cover;object-position:80% center">
<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(6,46,28,.92) 0%,rgba(6,46,28,.7) 40%,rgba(6,46,28,0) 62%)"></div>
<div style="position:absolute;left:64px;top:60px;width:600px">
<img src="data:image/png;base64,{logo}" style="height:84px">
<div style="font-family:Fraunces,serif;font-weight:700;font-size:62px;line-height:1.02;color:#FBF4E4;margin-top:56px">Pass your North Carolina contractor exam.</div>
<div style="font-size:24px;color:#E7B940;margin-top:22px;font-weight:600">Books, tabs and courses for every NC board</div>
<div style="font-size:20px;color:#E9E1CB;margin-top:10px">(877) 775-9400</div></div></body></html>'''
        pg2 = b.new_page(viewport={"width": 1200, "height": 630})
        pg2.set_content(og); pg2.wait_for_timeout(1200)
        pg2.screenshot(path=os.path.join(O, "og.png"))
        Image.open(os.path.join(O, "og.png")).convert("RGB").save(os.path.join(O, "og.jpg"), quality=86)
        b.close()
    print("icons and og written")


if __name__ == "__main__":
    main()
