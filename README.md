# passyournorthcarolinacontractorexam.com

Design: Tar Heel Pine (forest green, mustard gold, cream; Fraunces + Inter). Built pages sit at the repo root; the generator is in `source/`.

- Rebuild: `cd source && python3 build.py` (writes the repo root, removes only files from the last build listed in `.build-manifest.json`).
- Check: `python3 tools/check_pages.py ..` grades every page against "What every page and post needs to pass".
- Products: `source/data/products-raw.json` (Shopify pull, every active product with "North Carolina" in the title; $0 demos and the North Dakota title are skipped).
- Copy and facts: `source/tools/nccopy.py`; blog: `source/tools/ncblog.py`; images: `source/tools/art.py` and `source/tools/render.py`.
- GitHub Pages: Settings > Pages > Deploy from a branch > main, / (root). Custom domain passyournorthcarolinacontractorexam.com (CNAME file included).
