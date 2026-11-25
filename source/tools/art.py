#!/usr/bin/env python3
"""Make the image set for passyournorthcarolinacontractorexam.com from the client's logo, icon and hero photo.
python3 tools/art.py  (needs pillow, numpy, scipy, playwright with chromium)"""
import os, numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "brand"); O = os.path.join(ROOT, "assets", "img")
os.makedirs(O, exist_ok=True)


def transparent(path):
    im = Image.open(path).convert("RGBA"); a = np.array(im).astype(int)
    wh = (a[:, :, 0] > 236) & (a[:, :, 1] > 236) & (a[:, :, 2] > 236)
    lab, n = ndimage.label(wh)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    a[np.isin(lab, list(edge)), 3] = 0
    out = Image.fromarray(a.astype("uint8"))
    return out.crop(out.getbbox())


logo = transparent(os.path.join(B, "logo-source.png"))
icon = transparent(os.path.join(B, "icon-source.png"))
# header logo (2x of 50px tall)
h = 100; nav = logo.resize((int(logo.width * h / logo.height), h), Image.LANCZOS); nav.save(os.path.join(O, "logo-nav.png"), optimize=True)
# dark-background logo: dark green text and frame -> cream, keep gold and cream
a = np.array(nav).astype(int)
dark = (a[:, :, 1] < 90) & (a[:, :, 0] < 60) & (a[:, :, 3] > 0)
a[dark, 0], a[dark, 1], a[dark, 2] = 251, 244, 228
# the icon tile must stay green: restore pixels inside the icon (left square)
col = np.array(nav)[:, :, 3].sum(axis=0)
iw = next(x for x in range(int(nav.width * 0.12), nav.width) if col[x] < 600)
b = np.array(nav).astype(int); a[:, :iw] = b[:, :iw]
Image.fromarray(a.astype("uint8")).save(os.path.join(O, "logo-nav-dark.png"), optimize=True)
icon.resize((512, 512), Image.LANCZOS).save(os.path.join(O, "logo-mark.png"), optimize=True)
icon.resize((64, 64), Image.LANCZOS).save(os.path.join(O, "favicon.png"), optimize=True)
t = Image.new("RGB", (180, 180), (251, 244, 228)); ic = icon.resize((160, 160), Image.LANCZOS); t.paste(ic, (10, 10), ic); t.save(os.path.join(O, "apple-touch-icon.png"))
# hero
hero = Image.open(os.path.join(B, "hero-source.png")).convert("RGB")
w = 1600; hh = int(hero.height * w / hero.width)
h1 = hero.resize((w, hh), Image.LANCZOS); h1.save(os.path.join(O, "hero.jpg"), quality=82, optimize=True, progressive=True); h1.save(os.path.join(O, "hero.webp"), quality=80)
hero.resize((900, int(hero.height * 900 / hero.width)), Image.LANCZOS).save(os.path.join(O, "hero-800.webp"), quality=78)
print("logo, icons and hero written", nav.size, h1.size)
