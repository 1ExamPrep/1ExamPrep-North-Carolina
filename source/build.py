#!/usr/bin/env python3
"""Build passyournorthcarolinacontractorexam.com (design: Tar Heel Pine).

python3 build.py   -> writes the static site into ./site
Products come from data/products-raw.json (Shopify pull). Copy and facts live in tools/nccopy.py.
"""
import html, json, os, re, shutil, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from nccopy import *  # noqa
from ncblog import POSTS, AUTHOR, BSRC
SRC.update(BSRC)

# In the GitHub repo the scripts live in source/ and the site is written to the repo root.
OUT = os.path.dirname(ROOT) if os.path.basename(ROOT) == "source" else os.path.join(ROOT, "site")
MANIFEST = os.path.join(OUT, ".build-manifest.json")
SITE = "https://passyournorthcarolinacontractorexam.com"
BRAND = "Pass Your North Carolina Contractor Exam"
SHORT = "Pass Your NC Exam"
PHONE = "(877) 775-9400"; TEL = "+18777759400"; EMAIL = "sales@1examprep.com"
FORM_ID = "1jGx4TPpXO5C3XkV5vuq"
LAUNCHED = "2026-11-24"
CART = "https://1examprep.com/cart/{}:1"
REFUND = "https://1examprep.com/policies/refund-policy"
E = html.escape

STOP = {"a", "an", "and", "the", "of", "for", "to", "in", "on", "with", "by", "or", "at", "from", "based", "includes", "&", "+", "-"}


def slugify(s, maxw=8):
    s = s.lower().replace("&", " ").replace("'", "")
    w = [x for x in re.split(r"[^a-z0-9]+", s) if x and x not in STOP]
    return "-".join(w[:maxw])


def money(x):
    x = float(x)
    return f"${x:,.2f}" if x % 1 else f"${x:,.0f}"


def wc(s):
    return len(re.sub(r"<[^>]+>", " ", s).split())


def fit(req, opts, lo=42, hi=58):
    """Opening paragraph: required sentence(s) plus optional ones until 42 to 58 words."""
    out = req
    for o in opts:
        if wc(out) >= lo:
            break
        if wc(out + " " + o) <= hi:
            out += " " + o
    for o in opts:
        if wc(out) >= lo:
            break
        if o not in out and wc(out + " " + o) <= 60:
            out += " " + o
    return out


# ---------------------------------------------------------------- products
BANNED_START = re.compile(r"^(this|that|these|those|it|they|he|she|such|here|above|below|as mentioned|as noted|as discussed|as we saw)\b", re.I)
BAD = re.compile(r"(\(?\d{3}\)?[\s.-]\d{3}-\d{4}|@|https?://|www\.|\.com\b|\.org\b)", re.I)
OTHER = re.compile(r"\b(" + "|".join(re.escape(s) for s in STATES) + r")\b")


def sentences(p):
    t = re.sub(r"\s+", " ", p["description"]).strip()
    title = p["title"].strip()
    if t.startswith(title):
        t = t[len(title):].strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"“])", t)
    out = []
    for s in parts:
        s = s.strip()
        if not s or len(s.split()) > 38 or len(s.split()) < 5:
            continue
        if BAD.search(s) or OTHER.search(s.replace("North Carolina", "")):
            continue
        if s in out:
            continue
        out.append(s)
    return out


def take(sents, start, target):
    """Take sentences from index start until ~target words; first one must not open with a back-reference."""
    i = start
    while i < len(sents) and BANNED_START.match(sents[i]):
        i += 1
    chunk, n = [], 0
    while i < len(sents) and n < target:
        chunk.append(sents[i]); n += len(sents[i].split()); i += 1
    return chunk, i


def short_name(title, lic):
    t = title
    t = re.sub(r"\(Based on the (\d{4}) NEC\)", r"(\1 NEC)", t)
    t = re.sub(r"^North Carolina\s*-\s*", "", t)
    t = t.replace("North Carolina ", "").replace(" North Carolina", "")
    m = re.match(r"(?i)the 1 package:\s*all-inclusive\s*(.*)", t)
    if m:
        rest = re.sub(r"(?i)\s*(exam,\s*)?licensing\s*&.*$", "", m.group(1)).strip(" ,")
        t = f"The 1 Package: {rest}"
    else:
        t = re.sub(r":.*$", "", t)
    t = re.sub(r"\s+", " ", t).strip(" -,;")
    return t


def load_products():
    raw = json.load(open(os.path.join(ROOT, "data", "products-raw.json")))
    prods, used = [], set()
    for p in raw:
        lic = classify(p["title"])
        if not lic or lic == "unmatched":
            continue
        if max(float(v["price"]) for v in p["variants"]["nodes"]) <= 0:
            continue
        typ, rank = ptype(p["title"])
        prices = [float(v["price"]) for v in p["variants"]["nodes"]]
        vid = p["variants"]["nodes"][0]["id"].rsplit("/", 1)[1]
        img = ((p.get("featuredMedia") or {}).get("preview") or {}).get("image") or {}
        year = re.search(r"\b(20\d\d)\b", p["title"])
        year = int(year.group(1)) if year else None
        old = bool(year and lic in ("journeyman-electrician", "master-electrician") and year < 2026) or ("13th edition" in p["title"].lower())
        slug = slugify(re.sub(r"(?i)north carolina", "", p["title"]), 9) or p["handle"]
        base = slug; k = 2
        while slug in used:
            slug = f"{base}-{k}"; k += 1
        used.add(slug)
        prods.append(dict(
            id=p["id"], title=p["title"].strip(), short=short_name(p["title"], lic), lic=lic, type=typ, rank=rank,
            price=min(prices), pmax=max(prices), vid=vid, img=img.get("url"), alt=img.get("altText") or p["title"],
            year=year, old=old, slug=slug, sents=sentences(p), online=typ in ONLINE_TYPES,
        ))
    for p in prods:
        p["url"] = f"/{p['lic']}/{p['slug']}/"
    return prods


# ---------------------------------------------------------------- layout
NAV = [("/licenses/", "Licenses"), ("/how-to-get-licensed/", "How to get licensed"), ("/blog/", "Blog"), ("/faq/", "FAQ"), ("/contact/", "Contact")]
HERO_ALT = "A North Carolina contractor in a white hard hat and safety vest holds rolled blueprints at a brick home build site at golden hour"


def ld_org():
    return {"@type": "Organization", "@id": SITE + "/#org", "name": BRAND, "url": SITE + "/",
            "logo": SITE + "/assets/img/logo-mark.png", "image": SITE + "/assets/img/og.jpg",
            "telephone": PHONE, "email": EMAIL, "parentOrganization": {"@type": "Organization", "name": "1 Exam Prep", "url": "https://1examprep.com"},
            "contactPoint": {"@type": "ContactPoint", "telephone": TEL, "email": EMAIL, "contactType": "customer service", "areaServed": "US-NC", "availableLanguage": "English"},
            "areaServed": {"@type": "State", "name": "North Carolina"}}


def publisher():
    return {"@type": "Organization", "name": BRAND, "url": SITE + "/", "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/logo-mark.png"}}


def crumbs_ld(crumbs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (u, n) in enumerate(crumbs)]}


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in faq]}


def webpage_ld(path, title, desc, typ="WebPage"):
    return {"@type": typ, "@id": SITE + path + "#page", "url": SITE + path, "name": title, "description": desc,
            "inLanguage": "en-US", "isPartOf": {"@id": SITE + "/#website"}, "publisher": publisher(),
            "datePublished": LAUNCHED, "dateModified": CHECKED, "primaryImageOfPage": {"@type": "ImageObject", "url": SITE + "/assets/img/og.jpg"}}


def head(p):
    title, desc, path = p["title"], p["desc"], p["path"]
    assert 30 <= len(title) <= 60, (len(title), title)
    assert 70 <= len(desc) <= 160, (len(desc), desc)
    lds = "".join(f'\n<script type="application/ld+json">{json.dumps(dict({"@context": "https://schema.org"}, **x), ensure_ascii=False)}</script>' for x in p["ld"])
    img = p.get("ogimg") or SITE + "/assets/img/og.jpg"
    pre = '\n<link rel="preload" as="image" href="/assets/img/hero.webp" type="image/webp">' if p.get("home") else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="{'product' if p.get('product') else ('article' if p.get('article') else 'website')}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="article:published_time" content="{p.get('published', LAUNCHED)}">
<meta property="article:modified_time" content="{p.get('modified', CHECKED)}">
<meta property="og:image" content="{E(img)}">
<meta property="og:image:alt" content="{E(p.get('ogalt') or 'Pass Your North Carolina Contractor Exam: a contractor with blueprints at a North Carolina home build')}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{E(img)}">
<meta name="theme-color" content="#0B3D26">
<link rel="icon" type="image/png" href="/assets/img/favicon.png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">{pre}
<link rel="stylesheet" href="/assets/site.css?v=1">
<script src="/assets/site.js?v=1" defer></script>{lds}
</head>'''


def header():
    nav = "".join(f'<a href="{u}">{n}</a>' for u, n in NAV)
    return f'''<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap"><span>Exam prep for every North Carolina contractor board, fulfilled by 1 Exam Prep</span><span class="tb-contact"><a href="tel:{TEL}">{PHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a></span></div></div>
<header class="site-header"><div class="wrap hdr">
<a class="logo" href="/"><img src="/assets/img/logo-nav.png" width="153" height="50" alt="Pass Your North Carolina Contractor Exam logo: North Carolina map, house and open book with a gold check"></a>
<nav class="nav" id="nav" aria-label="Main">{nav}</nav>
<a class="btn btn-call" href="/licenses/">Shop exam prep</a>
<button class="menu" type="button" aria-controls="nav" aria-expanded="false" aria-label="Open menu"><span></span><span></span></button>
</div></header>'''


def footer():
    pop = ["building-contractor", "residential-contractor", "unlimited-electrical", "plumbing-class-i", "heating-group-3-class-1", "business-and-law", "roofing-contractor", "limited-electrical"]
    links = "".join(f'<li><a href="/{l}/">{E(BY_SLUG[l]["name"])}</a></li>' for l in pop)
    return f'''<footer class="site-footer"><div class="wrap fgrid">
<div><img src="/assets/img/logo-nav-dark.png" width="183" height="60" alt="Pass Your North Carolina Contractor Exam logo on dark green" loading="lazy">
<p>Exam prep books, tabs, courses and licensing help for North Carolina contractors. Orders are fulfilled by 1 Exam Prep.</p>
<p class="fcontact"><a href="tel:{TEL}">{PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
<div><p class="fh">Popular licenses</p><ul>{links}</ul></div>
<div><p class="fh">Site</p><ul><li><a href="/licenses/">All licenses</a></li><li><a href="/how-to-get-licensed/">How to get licensed</a></li><li><a href="/blog/">Blog</a></li><li><a href="/faq/">FAQ</a></li><li><a href="/contact/">Contact</a></li><li><a href="/sitemap.xml">Sitemap</a></li></ul>
<p class="fh">Official sources</p><ul><li><a href="https://www.nclbgc.org/" rel="noopener">NC Licensing Board for General Contractors</a></li><li><a href="https://www.ncbeec.org/" rel="noopener">NC Board of Examiners of Electrical Contractors</a></li><li><a href="https://nclicensing.org/" rel="noopener">NC Plumbing, Heating and Fire Sprinkler Board</a></li></ul></div>
</div><div class="wrap fbase"><p>&copy; 2026 {BRAND}. Not affiliated with any North Carolina licensing board or PSI. Prices in US dollars.</p></div></footer>
</body>
</html>'''


def breadcrumb(crumbs):
    items = []
    for i, (u, n) in enumerate(crumbs):
        items.append(f'<li><a href="{u}">{E(n)}</a></li>' if i < len(crumbs) - 1 else f'<li aria-current="page">{E(n)}</li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'


def takeaways_html(items):
    lis = "".join(f"<li>{x}</li>" for x in items)
    return f'<aside class="takeaways"><h2 id="key-takeaways">Key takeaways</h2><ul>{lis}</ul></aside>'


def faq_html(faq):
    items = "".join(f'<div class="qa"><dt>{E(q)}</dt><dd>{a}</dd></div>' for q, a in faq)
    return f'<section class="faq" id="faq"><h2 id="frequently-asked-questions">Frequently asked questions</h2><p>Short answers to the questions North Carolina candidates ask us most, checked against the state boards and statutes on {CHECKED_TEXT}.</p><dl>{items}</dl></section>'


def sources_html(keys):
    lis = "".join(f'<li><a href="{SRC[k][1]}" rel="noopener">{E(SRC[k][0])}</a></li>' for k in keys)
    return f'<section class="sources" id="sources"><h2 id="sources-h">Sources</h2><p>Licensing facts on this page come from the North Carolina General Statutes, the NC Administrative Code and the state licensing boards.</p><ul>{lis}</ul></section>'


def help_card():
    return f'''<div class="help"><p class="side-h">Questions before you buy?</p><p>Call or email the 1 Exam Prep team and we will match you with the right books.</p>
<a class="btn btn-gold" href="tel:{TEL}">{PHONE}</a><a class="help-mail" href="mailto:{EMAIL}">{EMAIL}</a><a class="help-link" href="/contact/">Contact page</a></div>'''


def render(p):
    sec = "".join(f'<section id="s-{sid}"><h2 id="{sid}">{E(h)}</h2>{body}</section>' for sid, h, body in p["sections"])
    side = f'<aside class="sidebar">{p.get("side", "")}{help_card()}</aside>' if p.get("sidebar", True) else ""
    updated = f'<p class="updated">Last updated <time datetime="{CHECKED}">{CHECKED_TEXT}</time></p>'
    hero = p.get("hero_html") or f'''<div class="page-hero"><div class="wrap">{breadcrumb(p["crumbs"])}<div class="ph-row">{p.get("hero_img", "")}<div><p class="eyebrow">{E(p.get("eyebrow", "North Carolina"))}</p><h1>{E(p["h1"])}</h1>{p.get("byline", "")}</div></div></div></div>'''
    pre = p.get("pre", "")
    body = f'''{header()}
<main id="main">{hero}
<div class="wrap {'layout' if side else 'single'}"><article class="content">
<p class="lead">{p["lead"]}</p>{updated}
{takeaways_html(p["takeaways"])}{pre}{sec}{faq_html(p["faq"])}{sources_html(p["sources"])}
</article>{side}</div>{p.get("post", "")}
</main>
{footer()}'''
    return head(p) + "\n" + body


def write(path, s):
    fp = os.path.join(OUT, path.strip("/"), "index.html") if path.endswith("/") else os.path.join(OUT, path.strip("/"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w").write(s)


# ---------------------------------------------------------------- shared copy
def exams_for(l):
    b, s = l["board"], l["slug"]
    if b == "gc":
        trade = "NASCLA Commercial General Building exam" if s == "nascla-commercial-general-building" else f"PSI {l['name']} trade exam"
        return [(trade, "Trade knowledge, codes, estimating and safety", "Open book, 70% to pass"),
                ("NC Business and Law exam", "Business, contracts, lien law and NCLBGC rules", "Open book, 70% to pass")]
    if b == "el":
        if s == "nascla-electrical-contractor":
            return [("NASCLA Electrical Contractor exam", "National exam on the NEC and contracting", "Accepted in place of the Board exam"),
                    ("NC Laws, Rules and Business Practices test", "25 questions on North Carolina rules", "18 correct to pass")]
        if s == "sp-sfd":
            return [("Board SP-SFD exam", "NEC rules for single-family detached homes", "Given by the electrical board"),
                    ("NASCLA Residential Electrical Contractor exam", "National residential electrical exam", "Accepted in place of the SP-SFD exam")]
        return [(f"Board {l['name']} exam", "NEC lookups, calculations and North Carolina electrical rules", "Written exam given by the electrical board")]
    if b == "pl":
        if s == "fire-sprinkler-installation":
            return [("Business and law part of the Board exam", "Contracting, business and North Carolina rules", "Taken at a Board testing center"),
                    ("NICET Level III certificate", "Automatic sprinkler system layout", "Required before licensing")]
        return [(f"Board {l['name']} exam", "Trade knowledge, North Carolina codes, business and law", "Allowed references in the room, 7 NC testing centers")]
    if b == "local":
        code = "International Plumbing Code" if "plumb" in s else "National Electrical Code"
        return [(f"{l['name']} exam", f"{code} lookups and calculations", "Check with your jurisdiction or employer")]
    if s == "business-and-law":
        return [("NC Business and Law exam", "Business, contracts, lien law and NCLBGC rules", "Open book, 70% to pass")]
    if s == "electrical-business-law":
        return [("Business and law questions for electrical contractors", "Contracts, business, safety and North Carolina rules", "Part of electrical contractor exam prep")]
    if b == "icc":
        return [("ICC special inspector exam", "Code and standards for the inspection module", "Computer-based ICC exam")]
    if b == "ref":
        return [("Reference books", "Code volumes and rules used across several exams", "Check your exam's reference list")]
    return [("No exam", "Paperwork and business setup", "Not applicable")]


def board_sources(l):
    return {"gc": ["gs87_1", "gs87_10", "ncac12a", "nclbgc"], "el": ["gs87_43", "art4", "ncac18b", "ncbeec", "nascla_el"],
            "pl": ["gs87_21", "art2", "plb_app", "plb"], "local": ["gs87_43", "ncbeec", "plb"], "bl": ["gs87_10", "nclbgc", "ncbeec"],
            "ref": ["gs87_1", "nclbgc"], "icc": ["icc", "nclbgc"], "svc": ["gs87_1", "nclbgc", "ncbeec", "plb"]}[l["board"]]


OPEN_BOOK = {
    "gc": "NCLBGC exams are open book, so tabbed books save time.",
    "el": "Electrical exams turn on fast NEC lookups, so a tabbed code book saves time.",
    "pl": "The Plumbing Board lets you bring the allowed references into the testing center, so tabbed books save time.",
}

TYPE_NOTE = {
    "The 1 Package": "exam prep, the board application service and business setup in one order",
    "Ultimate exam-room package": "the exam-room books with tabs, the online course and the application service",
    "Ultimate rental package": "the full rental book set with highlighting, tabs and course access",
    "Ultimate package": "the complete book set with highlighting, tabs and the online course",
    "Exam-room rental package": "rented exam-room books together with the online course",
    "Books and courses rental": "rented reference books together with the online course",
    "Books, tabs and course package": "the code books, tabs and the online course",
    "Highlighted and tabbed books": "the reference books, already highlighted and tabbed for fast lookups",
    "Exam-room books, highlighted and tabbed": "the books allowed into the exam room, highlighted and tabbed",
    "Exam-room books": "the books allowed into the exam room, new and untabbed",
    "Complete book package": "every reference book on the exam list, new and untabbed",
    "Live virtual training": "live instructor-led classes online plus self-study",
    "Online course": "self-paced online lessons and practice questions",
    "Online practice questions": "online practice questions in the exam format",
    "Pre-printed tabs": "printed tabs you stick into your own books",
    "Book with tabs": "the reference book with a set of tabs",
    "Complete pass package": "the business and law books with tabs, highlighting and practice",
    "Business and Law book": "the NASCLA business and law reference",
    "Study guide": "a study guide with 12 practice exams and 2 final exams",
    "Study guide and flash cards": "the study guide plus flash cards",
    "Study guide and online course": "the study guide plus an online course",
    "Study guide and NEC with tabs": "the study guide with the NEC code book and tabs",
    "Study guide, calculations and NEC": "the study guide, the calculations guide and the NEC",
    "Super combo": "study guides, flash cards, the NEC and tabs",
    "Ultimate combo": "every study guide, flash cards, the NEC, tabs and highlighting",
    "Study package with NEC course": "the ultimate combo plus an instructor-led NEC course",
    "Exam prep package": "the code book, tabs and a study guide",
    "Ultimate prep package": "the code book, tabs, study guide and extra practice",
    "Flash cards": "flash cards for quick review",
    "Service": "a done-for-you licensing or business filing service",
    "Ultimate service package": "the license application and business formation together",
    "Book": "a single reference book",
}


def delivery(p):
    if p["online"]:
        return "Online access is sent by email after checkout. Nothing ships."
    if "rental" in p["type"].lower():
        return "Rental books ship free by USPS Media Mail inside the United States; course access comes by email."
    return "Ships free by USPS Media Mail to US addresses."


DELIVERY_DAYS = {"@type": "OpeningHoursSpecification", "dayOfWeek": ["https://schema.org/Monday", "https://schema.org/Tuesday", "https://schema.org/Wednesday", "https://schema.org/Thursday", "https://schema.org/Friday"]}


def delivery_time(hmin, hmax, tmin, tmax):
    """ShippingDeliveryTime in business days. Matches the page copy: Media Mail 2 to 8 business days,
    rental / Ultimate / 1 Package orders up to 15, online access by email the same or next business day."""
    return {"@type": "ShippingDeliveryTime", "businessDays": DELIVERY_DAYS,
            "handlingTime": {"@type": "QuantitativeValue", "minValue": hmin, "maxValue": hmax, "unitCode": "DAY"},
            "transitTime": {"@type": "QuantitativeValue", "minValue": tmin, "maxValue": tmax, "unitCode": "DAY"}}


def offer_delivery_time(p):
    if p["online"]:
        return delivery_time(0, 1, 0, 0)
    if re.search(r"\b(rental|ultimate|1 package)\b", p["title"] + " " + p["type"], re.I):
        return delivery_time(0, 7, 2, 8)
    return delivery_time(0, 2, 2, 8)


# ---------------------------------------------------------------- product page
def product_card(p, lic_name=None):
    img = f'<img src="{E(p["img"])}&width=480" alt="{E(p["alt"])}" width="240" height="240" loading="lazy">' if p["img"] else '<img src="/assets/img/cat-services.webp" alt="Exam prep package illustration" width="240" height="240" loading="lazy">'
    tag = '<span class="tag tag-old">Older edition</span>' if p["old"] else f'<span class="tag">{E(p["type"])}</span>'
    price = money(p["price"]) + ("+" if p["pmax"] > p["price"] else "")
    return f'''<li class="card" data-type="{E(p["type"])}"><a class="card-img" href="{p["url"]}">{img}</a><div class="card-b">{tag}
<p class="card-t"><a href="{p["url"]}">{E(p["short"])}</a></p><p class="price">{price}</p>
<div class="card-cta"><a class="btn btn-sm btn-green" href="{CART.format(p["vid"])}" rel="nofollow">Buy now</a><a class="more" href="{p["url"]}">Details</a></div></div></li>'''


def ptitle(p, lic, taken):
    sfx = " | NC Exam Prep"
    tt = " ".join(w if w in ("and", "with") else w[:1].upper() + w[1:] for w in p["type"].split())
    nm = re.sub(r"\s*\([^)]*\)", "", lic["name"])
    cands = [p["short"], f'NC {nm} Exam: {tt}', f'{nm} Exam: {tt}', f'NC {nm} {tt}', f'NC {nm}: {tt}']
    yr = f' {p["year"]}' if p["year"] else ""
    for c in cands:
        for t in (c + sfx, c, c + yr):
            t = re.sub(r"\s+", " ", t).strip()
            if 30 <= len(t) <= 60 and t not in taken:
                taken.add(t); return t
    base = f'NC {nm} {p["type"]}'[:44]
    t = f'{base} {money(p["price"])}'
    if len(t) < 30:
        t = t + " | NC Exam Prep"
    t = t[:60]; k = 2
    while t in taken:
        t = t[:56] + f" #{k}"; k += 1
    taken.add(t); return t


def pdesc(p, lic):
    d = f'{p["short"]} for the North Carolina {lic["name"]} exam: {TYPE_NOTE.get(p["type"], "exam prep")}. {money(p["price"])}.'
    if len(d) > 158:
        d = f'{p["type"]} for the North Carolina {lic["name"]} exam: {TYPE_NOTE.get(p["type"], "exam prep")}. {money(p["price"])}.'
    if len(d) > 158:
        d = d[:155].rsplit(" ", 1)[0] + "."
    if len(d) < 75:
        d += " Free shipping on books."
    return d


def product_page(p, lic, siblings, taken):
    path = p["url"]
    title = ptitle(p, lic, taken)
    desc = pdesc(p, lic)
    s = p["sents"]
    c1, i = take(s, 0, 150)
    c2, i = take(s, i, 120)
    if not c1:
        c1 = [f"The {p['short']} is {TYPE_NOTE.get(p['type'], 'exam prep')} for North Carolina {lic['name']} candidates."]
    req = f'{"" if p["short"].startswith("The ") else "The "}{E(p["short"])} costs {money(p["price"])} and gives North Carolina {E(lic["name"])} candidates {E(TYPE_NOTE.get(p["type"], "exam prep"))}.'
    if wc(req) > 40:
        req = f'The {E(p["type"].lower())} costs {money(p["price"])} and gives North Carolina {E(lic["name"])} candidates {E(TYPE_NOTE.get(p["type"], "exam prep"))}.'
    lead = fit(req, [E(delivery(p)), f"Buy it below or call {PHONE} with questions.", "Orders are fulfilled by 1 Exam Prep.",
                     OPEN_BOOK.get(lic["board"], "Most code exams let you use the reference books, so tabs save time."),
                     "All sales are final, so ask before you order."])
    exams = exams_for(lic)
    sib = sorted([x for x in siblings if x["id"] != p["id"]], key=lambda x: (x["old"], x["rank"], x["price"]))[:8]
    sib_rows = "".join(f'<tr><td><a href="{x["url"]}">{E(x["short"])}</a></td><td>{E(x["type"])}</td><td>{money(x["price"])}</td></tr>' for x in sib)
    cmp_tbl = f'<table><thead><tr><th>Package</th><th>Type</th><th>Price</th></tr></thead><tbody><tr class="hl"><td>{E(p["short"])} (this page)</td><td>{E(p["type"])}</td><td>{money(p["price"])}</td></tr>{sib_rows}</tbody></table>'
    exam_list = "".join(f"<li><strong>{E(a)}</strong>: {E(b)} ({E(c)})</li>" for a, b, c in exams)
    old_note = f" This listing is an older edition ({p['year'] or 'previous'}); check which code edition your exam uses before you buy." if p["old"] else ""
    sections = [
        ("whats-included", f"What is in {'' if p['short'].startswith('The ') else 'the '}{p['short']}?", "<p>" + E(" ".join(c1)) + "</p>" + f'<ul class="facts"><li>Package type: {E(p["type"])}</li><li>Price: {money(p["price"])}{" to " + money(p["pmax"]) if p["pmax"] > p["price"] else ""}</li><li>Delivery: {E(delivery(p))}</li><li>License: <a href="/{lic["slug"]}/">North Carolina {E(lic["name"])}</a></li></ul>'),
        ("fit", f"How does it fit the North Carolina {lic['name']} exam?", f"<p>{E(lic['scope'])} {E(lic['note'])}{E(old_note)}</p><p>Candidates for this license prepare for {len(exams)} exam step{'s' if len(exams) > 1 else ''}:</p><ul>{exam_list}</ul>"),
    ]
    if c2:
        sections.append(("study", "What will you study with it?", "<p>" + E(" ".join(c2)) + "</p>"))
    sections.append(("compare", f"How does it compare with other {lic['name']} packages?",
                     f"<p>North Carolina {E(lic['name'])} prep comes in {len(siblings)} option{'s' if len(siblings) > 1 else ''} on this site, from {money(min(x['price'] for x in siblings))} to {money(max(x['price'] for x in siblings))}. The table lists the closest alternatives so you can trade price against how much is done for you.</p>{cmp_tbl}"))
    ob = {"gc": "Yes. NCLBGC trade and Business and Law exams allow the approved reference books, so tabbed and highlighted books save real time.",
          "el": "The electrical board exams are built around the NEC, and fast lookups in a tabbed code book decide most questions. Check the Board's exam notice for the books allowed.",
          "pl": "The Plumbing Board asks examinees to bring all allowed reference materials to the testing center, where they are checked against the Book Reference List."}.get(lic["board"], "Most code exams let candidates use the reference books. Check the reference list for your exam before you buy.")
    faq = [
        (f"How much does {'' if p['short'].startswith('The ') else 'the '}{p['short']} cost?", f"The price is {money(p['price'])} in US dollars{', and some options cost up to ' + money(p['pmax']) if p['pmax'] > p['price'] else ''}. Checkout runs through the 1 Exam Prep store, which takes major cards."),
        ("How is the order delivered?", delivery(p) + " Shipping is US only, and tracking comes by email once the order leaves the warehouse."),
        ("Can I return it?", f'All sales are final under the 1 Exam Prep <a href="{REFUND}" rel="noopener">refund policy</a>, so call {PHONE} before ordering if you are unsure which package fits your exam.'),
        (f"Which exams does the North Carolina {lic['name']} license need?", " ".join(f"{a}: {b}." for a, b, c in exams)),
        ("Can I bring books into the exam?", ob),
        ("Who do I contact with questions?", f'Call the 1 Exam Prep team at <a href="tel:{TEL}">{PHONE}</a> or email <a href="mailto:{EMAIL}">{EMAIL}</a>. You can also use the <a href="/contact/">contact form</a>.'),
    ]
    take_items = [f"Price: {money(p['price'])} ({E(p['type'])}).", E(delivery(p)), f"For the North Carolina {E(lic['name'])} license ({E(BOARDS[lic['board']])}).",
                  f"{len(siblings)} {E(lic['name'])} package{'s' if len(siblings) > 1 else ''} on this site, from {money(min(x['price'] for x in siblings))}."]
    crumbs = [("/", "Home"), ("/licenses/", "Licenses"), (f"/{lic['slug']}/", lic["name"]), (path, p["short"])]
    img_url = (p["img"] or SITE + "/assets/img/og.jpg")
    shipping = {"@type": "OfferShippingDetails", "shippingRate": {"@type": "MonetaryAmount", "value": 0, "currency": "USD"},
                "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "US"},
                "deliveryTime": offer_delivery_time(p)}
    shipping["shippingLabel"] = "Online access by email, nothing shipped" if p["online"] else "Free USPS (Media Mail)"
    offer = {"@type": "Offer", "url": SITE + path, "priceCurrency": "USD", "price": f"{p['price']:.2f}", "availability": "https://schema.org/InStock",
             "itemCondition": "https://schema.org/NewCondition", "seller": {"@type": "Organization", "name": "1 Exam Prep"},
             "priceValidUntil": "2027-12-31", "shippingDetails": shipping,
             "hasMerchantReturnPolicy": {"@type": "MerchantReturnPolicy", "applicableCountry": "US", "returnPolicyCategory": "https://schema.org/MerchantReturnNotPermitted", "merchantReturnLink": REFUND}}
    if p["pmax"] > p["price"]:
        offer = dict(offer, **{"@type": "AggregateOffer", "lowPrice": f"{p['price']:.2f}", "highPrice": f"{p['pmax']:.2f}", "offerCount": 2}); offer.pop("price")
    prod_ld = {"@type": "Product", "@id": SITE + path + "#product", "name": p["title"], "description": " ".join(c1)[:500] or desc,
               "image": [img_url], "sku": p["vid"], "url": SITE + path, "brand": {"@type": "Brand", "name": "1 Exam Prep"},
               "category": f"North Carolina {lic['name']} exam prep", "offers": offer}
    imgtag = f'<img src="{E(p["img"])}&width=720" alt="{E(p["alt"])}" width="360" height="360">' if p["img"] else '<img src="/assets/img/cat-services.webp" alt="Exam prep package illustration" width="360" height="360">'
    buybox = f'''<div class="buy"><div class="buy-img">{imgtag}</div><div class="buy-b"><span class="tag">{E(p["type"])}</span><p class="buy-price">{money(p["price"])}</p>
<p>{E(delivery(p))}</p><a class="btn btn-green btn-lg" href="{CART.format(p["vid"])}" rel="nofollow">Buy now</a><p class="small">Secure checkout at 1examprep.com. All sales are final.</p></div></div>'''
    side = f'<div class="side-box"><p class="side-h">{E(lic["name"])}</p><p class="side-price">{money(p["price"])}</p><a class="btn btn-green" href="{CART.format(p["vid"])}" rel="nofollow">Buy now</a><a class="help-link" href="/{lic["slug"]}/">All {E(lic["name"])} packages</a></div>'
    return dict(path=path, title=title, desc=desc, h1=p["title"], lead=lead, takeaways=take_items, sections=sections, faq=faq,
                sources=board_sources(lic), crumbs=crumbs, eyebrow=f"North Carolina {lic['name']}", pre=buybox, side=side, product=True,
                ogimg=p["img"] or None, ogalt=p["alt"],
                ld=[prod_ld, webpage_ld(path, title, desc, "ItemPage"), crumbs_ld(crumbs), faq_ld(faq)])


# ---------------------------------------------------------------- license page
def limits_section(l):
    b = l["board"]
    if b == "gc":
        rows = "".join(f"<tr><td>{a}</td><td>{x}</td><td>{y}</td><td>{z}</td><td>{f}</td></tr>" for a, x, y, z, f in GC_LIMITS)
        return ("job-limits", "How big a job can you bid with an NCLBGC license?",
                f"<p>Every NCLBGC license carries a limitation that caps the value of any single project. A license is needed once a project costs $40,000 or more under G.S. 87-1. The limitation depends on the working capital you show, or a surety bond in its place, and the application fee set by G.S. 87-10 rises with the tier.</p>"
                f"<table><thead><tr><th>Limitation</th><th>Single project limit</th><th>Working capital</th><th>Bond alternative</th><th>Application fee</th></tr></thead><tbody>{rows}</tbody></table>")
    if b == "el":
        return ("job-limits", "What do the electrical license classes allow?",
                "<p>G.S. 87-43.3 sets three electrical contracting classes and lets the Board create special restricted classes for one phase of work. The Board sets the working project limits, and the statute caps them.</p>"
                "<table><thead><tr><th>Class</th><th>Single project limit</th><th>Experience (G.S. 87-43.3)</th></tr></thead><tbody>"
                "<tr><td>Limited</td><td>Up to the Board limit, capped at $100,000, 1,000 volts or less</td><td>No more than 3,000 hours, at least 2,000 installing</td></tr>"
                "<tr><td>Intermediate</td><td>Up to the Board limit, capped at $200,000</td><td>No more than 5,750 hours, at least 5,000 installing</td></tr>"
                "<tr><td>Unlimited</td><td>Any value</td><td>Set by Board rule</td></tr>"
                "<tr><td>Special restricted (SP)</td><td>One phase of electrical work</td><td>No more than 3,000 hours</td></tr></tbody></table>")
    if b == "pl":
        return ("experience", "How much experience does the Plumbing Board ask for?",
                "<p>The Plumbing, Heating and Fire Sprinkler board lists experience by license on its applicant page. Exams are offered daily at 7 testing centers, must be taken within 90 days of notice, and a failed exam means a 90-day wait to retest.</p>"
                "<table><thead><tr><th>License</th><th>Experience</th></tr></thead><tbody>"
                "<tr><td>Plumbing or heating contractor</td><td>2 years (4,000 hours), up to 2,000 hours of training</td></tr>"
                "<tr><td>Technician, Class I</td><td>18 months (3,000 hours)</td></tr><tr><td>Technician, Class II</td><td>15 months (2,500 hours)</td></tr>"
                "<tr><td>Fuel Piping Contractor</td><td>1 year (2,000 hours), up to 1,000 hours of training</td></tr>"
                "<tr><td>Fuel Piping Technician</td><td>9 months (1,500 hours)</td></tr><tr><td>Restricted Limited Plumbing</td><td>9 months (1,500 hours), up to 750 hours of training</td></tr>"
                "<tr><td>Fire Sprinkler Installation Contractor</td><td>NICET Level III, automatic sprinkler system layout</td></tr></tbody></table>")
    if b == "local":
        return ("local", "Who tests journeyman and master candidates?",
                f"<p>North Carolina's state boards license contractors. Electrical contractor licenses come from the State Board of Examiners of Electrical Contractors, and plumbing contractors and technicians from the Plumbing, Heating and Fire Sprinkler board. Journeyman and master credentials for individual workers depend on the employer or the local program, so ask which code edition your exam uses before you buy. The packages here include current and older editions, clearly labeled.</p>")
    return None


def license_page(l, items):
    path = f"/{l['slug']}/"
    items = sorted(items, key=lambda x: (x["old"], x["rank"], x["price"]))
    lo, hi = min(x["price"] for x in items), max(x["price"] for x in items)
    n = len(items)
    nm = re.sub(r"\s*\([^)]*\)", "", l["name"])
    title = f"North Carolina {nm} Exam Prep"
    if len(title) > 60:
        title = f"NC {nm} Exam Prep"
    if len(title) < 30:
        title += " | Books and Courses"
    if len(title) > 60:
        title = f"NC {nm} Exam Prep"[:60]
    desc = f"North Carolina {l['name']} exam prep: {n} package{'s' if n > 1 else ''} from {money(lo)} to {money(hi)}. Books, tabs and courses, with exam facts from the state board."
    if len(desc) > 160:
        desc = f"NC {nm} exam prep: {n} package{'s' if n > 1 else ''} from {money(lo)}. Books, tabs and courses with exam facts from the state board."
    if len(desc) > 160:
        desc = desc[:157].rsplit(" ", 1)[0] + "."
    exams = exams_for(l)
    req = f"{E(l['scope'])} We carry {n} North Carolina {E(l['name'])} package{'s' if n > 1 else ''}, priced from {money(lo)} to {money(hi)}."
    if wc(req) > 50:
        req = f"We carry {n} North Carolina {E(l['name'])} exam prep package{'s' if n > 1 else ''}, priced from {money(lo)} to {money(hi)}, for the {E(BOARDS[l['board']])}."
    lead = fit(req, ["The packages cover the exams you need, from reference books to courses.",
                     "Every book ships free by USPS Media Mail.", "Online courses arrive by email right after checkout.", f"Call {PHONE} for help choosing."])
    types = defaultdict(list)
    for x in items:
        types[x["type"]].append(x)
    chips = '<div class="chips" role="group" aria-label="Filter packages"><button type="button" class="chip on" data-filter="all">All</button>' + "".join(
        f'<button type="button" class="chip" data-filter="{E(t)}">{E(t)}</button>' for t in sorted(types, key=lambda t: types[t][0]["rank"])) + "</div>" if len(types) > 2 else ""
    grid = f'<section class="pkgs" id="packages"><h2 id="packages-h">North Carolina {E(l["name"])} packages</h2><p>{n} package{"s" if n > 1 else ""} for this license, sorted with the most complete options first. Prices are in US dollars and books ship free.</p>{chips}<ul class="cards">{"".join(product_card(x) for x in items)}</ul></section>'
    exam_rows = "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td><td>{E(c)}</td></tr>" for a, b, c in exams)
    who = {"gc": "PSI gives the NCLBGC exams at its test centers.", "el": "The State Board of Examiners of Electrical Contractors gives its own written exams.",
           "pl": "The Plumbing, Heating and Fire Sprinkler board runs its exams at 7 testing centers across the state.",
           "local": "Journeyman and master exams follow the rules of the employer or local program."}.get(l["board"], "The table lists the exam or reference this page covers.")
    sections = [
        ("what-it-covers", f"What does the North Carolina {nm} license cover?", f"<p>{E(l['scope'])} {E(l['note'])}</p>"),
        ("exams", f"Which exams do {nm} candidates take?",
         f"<p>{who} The table lists what this license needs, based on the current statutes, board rules and board pages.</p><table><thead><tr><th>Exam</th><th>What it covers</th><th>Format</th></tr></thead><tbody>{exam_rows}</tbody></table>"),
    ]
    ls = limits_section(l)
    if ls:
        sections.append(ls)
    tl = sorted(types, key=lambda t: types[t][0]["rank"])
    type_list = "".join(f"<li><strong>{E(t)}</strong> ({len(types[t])}, from {money(min(x['price'] for x in types[t]))}): {E(TYPE_NOTE.get(t, 'exam prep'))}.</li>" for t in tl)
    sections.append(("choose", f"Which {nm} package should you choose?",
                     f"<p>Pick by how much time you have and how much of the setup you want done for you. Candidates with 6 weeks or less usually choose highlighted and tabbed books or a course, because lookup speed matters on reference-book exams.</p><ul>{type_list}</ul>"))
    best = items[0]
    cheap = min(items, key=lambda x: x["price"])
    ob = {"gc": "Yes. The NCLBGC trade and Business and Law exams allow the approved reference books, so tabbed and highlighted books are worth having.",
          "el": "The electrical exams are built around the National Electrical Code, and fast lookups decide most questions. Check the Board's exam notice for the books allowed in the room.",
          "pl": "The Plumbing Board asks examinees to bring their allowed references to the testing center, where they are checked against the Book Reference List."}.get(l["board"], "Most code exams let you use the reference books. Check the reference list for your exam.")
    sched = {"gc": "Apply to the NCLBGC first. Once the Board approves the application, you schedule the PSI exams.",
             "el": "Yes. Apply to the electrical board with proof of experience, then sit the Board's written exam.",
             "pl": "Yes. Apply to the Plumbing Board, then take the exam within 90 days of the notification date at one of its 7 testing centers."}.get(l["board"], "Ask the program or employer that gives the exam. Most require an application first.")
    faq = [
        (f"How much does North Carolina {nm} exam prep cost?", f"Packages on this site run from {money(lo)} to {money(hi)}. The lowest-priced option is {'' if cheap['short'].startswith('The ') else 'the '}{E(cheap['short'])} at {money(cheap['price'])}."),
        (f"Which exams do I need for the {nm} license?", " ".join(f"{a}: {b}." for a, b, c in exams)),
        ("Can I bring books into the exam?", ob),
        ("Do I need approval before scheduling the exam?", sched),
        ("Do the books ship free?", "Yes. Physical books and tabs ship free by USPS Media Mail inside the United States, and online courses arrive by email right after checkout."),
        ("Which package is the most complete?", f"The most complete option for this license is {'' if best['short'].startswith('The ') else 'the '}{E(best['short'])} at {money(best['price'])}. Call {PHONE} if you want help comparing it with the cheaper choices."),
        ("How do I get help choosing?", f'Call <a href="tel:{TEL}">{PHONE}</a>, email <a href="mailto:{EMAIL}">{EMAIL}</a> or use the <a href="/contact/">contact page</a>. Tell us the license and your exam date.'),
    ]
    take_items = [f"{n} package{'s' if n > 1 else ''} from {money(lo)} to {money(hi)}.", f"Issued by: {E(BOARDS[l['board']])}.",
                  " ".join(f"{E(a)}: {E(b)}." for a, b, c in exams[:2])]
    if l["board"] == "gc":
        take_items.append("A general contractor license is needed for projects of $40,000 or more.")
    elif l["board"] == "pl":
        take_items.append("Exams run daily at 7 testing centers; take yours within 90 days of notice.")
    elif l["board"] == "el":
        take_items.append("Limited and Intermediate project caps are set by statute at $100,000 and $200,000.")
    crumbs = [("/", "Home"), ("/licenses/", "Licenses"), (path, l["name"])]
    item_list = {"@type": "ItemList", "name": f"North Carolina {l['name']} exam prep packages", "numberOfItems": n,
                 "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": SITE + x["url"], "name": x["title"]} for i, x in enumerate(items)]}
    coll = webpage_ld(path, title, desc, "CollectionPage"); coll["mainEntity"] = {"@id": SITE + path + "#list"}; item_list["@id"] = SITE + path + "#list"
    side = f'''<div class="side-box"><p class="side-h">Exam facts</p><ul class="side-facts"><li><span>Issued by</span>{E(BOARDS[l["board"]])}</li>{"".join(f"<li><span>Exam</span>{E(a)}</li>" for a, b, c in exams)}<li><span>Packages</span>{n}, from {money(lo)}</li></ul><a class="btn btn-green" href="#packages">See packages</a></div>'''
    return dict(path=path, title=title, desc=desc, h1=f"North Carolina {l['name']} Exam Prep", lead=lead, takeaways=take_items, pre=grid,
                sections=sections, faq=faq, sources=board_sources(l), crumbs=crumbs, eyebrow=dict((g[0], g[1]) for g in GROUPS)[l["group"]],
                hero_img=f'<img class="ph-icon" src="/assets/img/cat-{l["group"]}.webp" alt="{E(l["name"])} license illustration" width="96" height="96">',
                side=side, ld=[coll, item_list, crumbs_ld(crumbs), faq_ld(faq)])


# ---------------------------------------------------------------- static pages
def license_tiles(counts, prices, heads=True):
    out = []
    for gk, gname, gdesc, icon in GROUPS:
        ls = [l for l in LICENSES if l["group"] == gk and counts[l["slug"]]]
        lis = "".join(f'<li data-name="{E(l["name"].lower())}"><a href="/{l["slug"]}/"><span>{E(l["name"])}</span><small>{counts[l["slug"]]} package{"s" if counts[l["slug"]] != 1 else ""} · from {money(prices[l["slug"]])}</small></a></li>' for l in ls)
        h = f'<h3 id="h-{gk}">{E(gname)}</h3>' if heads else f'<p class="g-title">{E(gname)}</p>'
        out.append(f'<div class="group" id="g-{gk}"><div class="g-head"><img src="/assets/img/cat-{icon}.webp" alt="{E(gname)} illustration" width="64" height="64" loading="lazy"><div>{h}<p>{E(gdesc)}</p></div></div><ul class="lic-list">{lis}</ul></div>')
    return "".join(out)


LIMIT_ROWS = "".join(f"<tr><td>{a}</td><td>{x}</td><td>{y}</td><td>{z}</td></tr>" for a, x, y, z, f in GC_LIMITS)
BOARD_TABLE = ("<table><thead><tr><th>Board</th><th>Who needs it</th><th>Exams</th></tr></thead><tbody>"
               "<tr><td>Licensing Board for General Contractors</td><td>Projects of $40,000 or more: building, residential, highway, utilities, specialty</td><td>PSI trade exam plus Business and Law, 70% to pass</td></tr>"
               "<tr><td>Board of Examiners of Electrical Contractors</td><td>Electrical contracting at any value, in Limited, Intermediate, Unlimited or SP classes</td><td>Board written exam, or NASCLA plus the NC rules test</td></tr>"
               "<tr><td>Plumbing, Heating and Fire Sprinkler board</td><td>Plumbing, HVAC, fuel piping and fire sprinkler contractors and technicians</td><td>Board exam at 7 testing centers</td></tr></tbody></table>")


def home_page(counts, prices, nprod):
    path = "/"
    nlic = sum(1 for l in LICENSES if counts[l["slug"]])
    title = "Pass Your North Carolina Contractor Exam | NC Exam Prep"
    desc = f"North Carolina contractor exam prep for {nlic} general, electrical, plumbing and HVAC licenses: {nprod} books, tabs and courses with free shipping."
    lead = (f"Passing a North Carolina contractor exam takes the right reference books and a plan. We stock {nprod} study packages for {nlic} licenses across all three state boards, "
            f"from the $40,000 general contractor threshold to Heating Group 3 and Unlimited Electrical. Call {PHONE} for help choosing.")
    hero = f'''<section class="hero"><picture><source type="image/webp" srcset="/assets/img/hero-800.webp 900w, /assets/img/hero.webp 1600w" sizes="100vw"><img class="hero-bg" src="/assets/img/hero.jpg" alt="{HERO_ALT}" width="1600" height="639"></picture>
<div class="wrap hero-in"><p class="eyebrow">NCLBGC · Electrical · Plumbing and Heating</p><h1>Pass your North Carolina contractor exam the first time.</h1>
<p class="hero-sub">Tabbed code books, online courses and practice exams for the tests North Carolina uses. Pick your license and get the exact books the exam allows.</p>
<div class="hero-cta"><a class="btn btn-gold btn-lg" href="#find">Find my license</a><a class="btn btn-ghost btn-lg" href="tel:{TEL}">Call {PHONE}</a></div></div></section>
<section class="statband" aria-label="Key numbers"><ul class="wrap"><li><b>$40,000</b><span>Project value that needs a state general contractor license</span></li><li><b>70%</b><span>Score to pass the NCLBGC trade and Business and Law exams</span></li><li><b>3 tiers</b><span>Limited to $750K, Intermediate to $1.5M, Unlimited with no cap</span></li><li><b>{nprod}</b><span>North Carolina packages, from {money(min(prices[l["slug"]] for l in LICENSES if counts[l["slug"]]))}</span></li></ul></section>'''
    finder = f'''<section class="finder" id="find"><div class="wrap"><h2 id="find-your-license">Which North Carolina license are you testing for?</h2><p class="sub">Type a trade or pick a board. Every license page lists the exams, the limits and every package we carry.</p>
<label class="search"><span class="sr">Search licenses</span><input id="lic-search" type="search" placeholder="Roofing, Heating Group 3, Unlimited Electrical" autocomplete="off"></label>
<div class="groups">{license_tiles(counts, prices)}</div></div></section>'''
    sections = [
        ("which-board", "Which North Carolina board licenses you?",
         "<p>North Carolina splits contractor licensing between three independent boards. The Licensing Board for General Contractors (NCLBGC) covers building, residential, highway, utility and specialty contractors on projects of $40,000 or more. "
         "The State Board of Examiners of Electrical Contractors covers electrical contracting. The State Board of Examiners of Plumbing, Heating and Fire Sprinkler Contractors covers plumbing, HVAC, fuel piping and fire sprinklers.</p>" + BOARD_TABLE),
        ("how-it-works", "How do you pass with 1 Exam Prep?",
         "<ol class='steps'><li><b>Pick your license.</b> Each license page lists the exams and every package we carry.</li><li><b>Choose how you study.</b> Tabbed books, online courses, live virtual classes or a complete rental.</li><li><b>Practice with the books you take in.</b> Reference-book exams reward fast lookups, not memory.</li><li><b>Apply, schedule and pass.</b> Each board approves your application before you test.</li></ol>"
         "<p>Most candidates study for 4 to 8 weeks. Highlighted and tabbed books cut lookup time on exams where every minute counts.</p>"),
        ("job-limits", "How big a job can a North Carolina general contractor bid?",
         f"<p>NCLBGC licenses carry a limitation that caps each single project. The limitation comes from your working capital or a surety bond, under G.S. 87-10 and 21 NCAC 12A .0204.</p><table><thead><tr><th>Limitation</th><th>Single project limit</th><th>Working capital</th><th>Bond alternative</th></tr></thead><tbody>{LIMIT_ROWS}</tbody></table>"),
        ("why-us", "Why do North Carolina contractors study with us?",
         f"<ul><li><b>Exam-room book sets</b>, new or rented, with tabs placed where the answers are.</li><li><b>Free USPS Media Mail shipping</b> on books and tabs inside the US.</li><li><b>Courses and practice tests for {nlic} licenses</b>, from Building Contractor to SP-PH and Fuel Piping.</li><li><b>Licensing help</b>: the board application service and LLC setup, or all of it in The 1 Package.</li><li><b>People who answer the phone</b> at {PHONE} and {EMAIL}.</li></ul>"),
    ]
    faq = [
        ("Do I need a contractor license in North Carolina?", "Yes, for general contracting on any project that costs $40,000 or more under G.S. 87-1. Electrical, plumbing, heating and fire sprinkler contractors need a license from their own board."),
        ("What score passes the NCLBGC exams?", "70 percent on the trade exam and on the Business and Law exam. Both are open book with the approved references."),
        ("What are the NCLBGC license limitations?", "Limited covers single projects up to $750,000, Intermediate up to $1,500,000, and Unlimited has no project limit."),
        ("Does North Carolina accept the NASCLA exam?", "Yes. The NCLBGC accepts the NASCLA Commercial General Building exam for the Building classification, and the electrical board accepts the NASCLA Electrical Contractor exam with a North Carolina rules test."),
        ("What is the difference between Heating Group 2 and Group 3?", "Heating Group 2 covers air conditioning systems greater than 15 tons. Heating Group 3 covers forced-air heating and cooling of 15 tons or less."),
        ("What does a Class II plumbing license cover?", "Class II covers plumbing and heating systems in single-family detached homes. Class I covers all structures."),
        ("Do you ship outside North Carolina?", "Books ship free by USPS Media Mail anywhere in the United States. Online courses are delivered by email, so you can study from anywhere."),
        ("How do I contact you?", f'Call <a href="tel:{TEL}">{PHONE}</a> or email <a href="mailto:{EMAIL}">{EMAIL}</a>. The <a href="/contact/">contact page</a> has a form as well.'),
    ]
    take = [f"{nprod} study packages for {nlic} North Carolina licenses.", "General contractor license needed for projects of $40,000 or more.",
            "NCLBGC trade and Business and Law exams: 70% to pass, open book.", "Limitations: $750,000, $1,500,000 or unlimited per project.", f"Help by phone at {PHONE}."]
    contact_band = f'''<section class="band" id="contact-band"><div class="wrap band-in"><div><p class="band-h">Not sure which package fits your exam?</p><p>Talk to a person who knows the North Carolina exams.</p></div><div class="band-cta"><a class="btn btn-gold btn-lg" href="tel:{TEL}">{PHONE}</a><a class="btn btn-ghost btn-lg" href="mailto:{EMAIL}">{EMAIL}</a></div></div></section>'''
    website = {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": BRAND, "publisher": {"@id": SITE + "/#org"}, "inLanguage": "en-US"}
    return dict(path=path, title=title, desc=desc, h1="", lead=lead, takeaways=take, sections=sections, faq=faq, sources=["gs87_1", "gs87_10", "ncac12a", "gs87_43", "gs87_21", "plb_app", "nascla_el"],
                crumbs=[("/", "Home")], hero_html=hero + finder, home=True, sidebar=False, post=contact_band,
                ld=[ld_org(), website, webpage_ld(path, title, desc), crumbs_ld([("/", "Home")]), faq_ld(faq)])


def licenses_index(counts, prices, nprod):
    path = "/licenses/"
    nlic = sum(1 for l in LICENSES if counts[l["slug"]])
    title = "North Carolina Contractor Licenses: Exam Prep by Trade"
    desc = f"All {nlic} North Carolina contractor licenses we cover, grouped by board, with package counts and starting prices. NCLBGC, electrical, plumbing and HVAC."
    lead = (f"North Carolina contractor licenses fall into eight groups on this site: {nlic} licenses in all, with {nprod} study packages between them. "
            "Pick a license to see its exams, limits and every book, tab and course we carry for it, or call us for a recommendation.")
    sections = [("all-licenses", "Which licenses does the site cover?", f'<p>The list below groups every license by board and trade. Counts and starting prices update each time the catalog is synced from the 1 Exam Prep store.</p><label class="search"><span class="sr">Search licenses</span><input id="lic-search" type="search" placeholder="Search {nlic} licenses" autocomplete="off"></label><div class="groups">{license_tiles(counts, prices)}</div>'),
                ("how-to-choose", "How do you know which license you need?",
                 "<p>Start with the trade and the size of the job. General contracting on a project of $40,000 or more needs an NCLBGC license. Electrical contracting needs a license from the electrical board at any value. "
                 "Plumbing, heating, fuel piping and fire sprinkler work needs the Plumbing, Heating and Fire Sprinkler board. The <a href='/how-to-get-licensed/'>licensing guide</a> walks through each path step by step.</p>")]
    faq = [
        ("How many North Carolina contractor licenses are there?", f"The three boards issue dozens of classifications. This site covers {nlic} of them, every one we stock prep material for."),
        ("Which board licenses HVAC contractors?", "The State Board of Examiners of Plumbing, Heating and Fire Sprinkler Contractors, through Heating Groups 1, 2 and 3."),
        ("Can I hold more than one classification?", "Yes. An NCLBGC license can carry several classifications. You pass the trade exam for each one."),
        ("Is there a statewide journeyman electrician license?", "No. The electrical board licenses electrical contractors. Journeyman credentials depend on the employer or local program."),
        ("Do all NCLBGC licenses need the Business and Law exam?", "Yes. Every NCLBGC applicant takes the Business and Law exam along with the trade exam."),
        ("Where do I take the exams?", "PSI gives the NCLBGC exams. The electrical board gives its own written exams, and the Plumbing Board tests at 7 centers across the state."),
    ]
    take = [f"{nlic} licenses, {nprod} packages.", "NCLBGC: projects of $40,000 or more.", "Electrical board: Limited, Intermediate, Unlimited and SP classes.", "Plumbing Board: plumbing, Heating Groups 1 to 3, fuel piping, fire sprinkler."]
    crumbs = [("/", "Home"), (path, "Licenses")]
    shown = [l for l in LICENSES if counts[l["slug"]]]
    il = {"@type": "ItemList", "name": "North Carolina contractor licenses", "numberOfItems": len(shown),
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/{l['slug']}/", "name": l["name"]} for i, l in enumerate(shown)]}
    return dict(path=path, title=title, desc=desc, h1="North Carolina Contractor Licenses", lead=lead, takeaways=take, sections=sections, faq=faq,
                sources=["gs87_1", "gs87_43", "gs87_21", "plb_app"], crumbs=crumbs, eyebrow="All licenses", sidebar=False,
                ld=[webpage_ld(path, title, desc, "CollectionPage"), il, crumbs_ld(crumbs), faq_ld(faq)])


def guide_page():
    path = "/how-to-get-licensed/"
    title = "How to Get a North Carolina Contractor License (2026)"
    desc = "Step-by-step guide to a North Carolina contractor license: which board, the $40,000 rule, exams, license limits, experience and fees. Updated November 2026."
    lead = ("To get a North Carolina contractor license, pick the board that covers your trade, apply with proof of experience or finances, then pass that board's exams. "
            "General contractors need an NCLBGC license for projects of $40,000 or more and pass a trade exam and Business and Law at 70 percent.")
    steps = [
        ("Pick the board", "General contracting goes to the NCLBGC, electrical work to the electrical board, and plumbing, HVAC, fuel piping and fire sprinkler work to the Plumbing Board."),
        ("Choose the classification", "Match your work to a classification such as Building, Residential, Unlimited Electrical or Heating Group 3."),
        ("Apply to the board", "Send the application with proof of experience, and for the NCLBGC, working capital or a bond for your limitation."),
        ("Pass the exams", "Take the trade exam and, for the NCLBGC, the Business and Law exam. Bring the allowed reference books."),
        ("Get licensed and renew", "Receive the license, set up the business and keep up with yearly renewal and continuing education."),
    ]
    steps_html = "<ol class='steps'>" + "".join(f"<li><b>{E(a)}.</b> {E(b)}</li>" for a, b in steps) + "</ol>"
    sections = [
        ("steps", "What are the steps to a North Carolina contractor license?", steps_html + "<p>Most candidates finish the exams within 4 to 8 weeks of starting to study. Board review time depends on how complete the application is.</p>"),
        ("which-board", "Which board covers your work?",
         "<p>North Carolina uses three independent boards, each set up by a different article of Chapter 87 of the General Statutes. Article 1 covers general contractors, Article 2 covers plumbing, heating and fire sprinkler contractors, and Article 4 covers electrical contractors.</p>" + BOARD_TABLE +
         "<p>A general contractor license does not let you do electrical, plumbing or HVAC work. Those trades need their own board's license even on a small job.</p>"),
        ("gc-limits", "How do NCLBGC limitations work?",
         f"<p>Every NCLBGC license carries a limitation that caps the value of a single project, excluding land. You qualify with working capital, or with a surety bond as the alternative, and the application fee rises with the tier.</p><table><thead><tr><th>Limitation</th><th>Single project limit</th><th>Working capital</th><th>Bond alternative</th></tr></thead><tbody>{LIMIT_ROWS}</tbody></table>"
         "<p>Application fees are $75 for Limited, $100 for Intermediate and $125 for Unlimited under G.S. 87-10.</p>"),
        ("electrical", "How does the electrical license work?",
         "<p>The State Board of Examiners of Electrical Contractors issues Limited, Intermediate and Unlimited licenses plus special restricted classes such as SP-SFD, SP-FA/LV and SP-PH. "
         "G.S. 87-43.3 caps the Limited project value at $100,000 on installations of 1,000 volts or less and the Intermediate value at $200,000, with the Board setting the working limits within those caps. "
         "Limited and SP applicants need up to 3,000 hours of experience, and Intermediate applicants up to 5,750 hours. "
         "The Board accepts the NASCLA Electrical Contractor exam as an alternative, as long as you also get 18 of 25 right on the North Carolina Laws, Rules and Business Practices test.</p>"),
        ("plumbing", "How does the Plumbing, Heating and Fire Sprinkler license work?",
         "<p>G.S. 87-21 sets two classes: Class I covers all structures, and Class II covers single-family detached homes. Heating is split into groups. Group 1 is hydronic heating, Group 2 is air conditioning greater than 15 tons, and Group 3 is forced-air heating and cooling. "
         "Contractor applicants need 2 years (4,000 hours) of experience. The Board tests daily at 7 centers: Asheville, Charlotte, Winston-Salem, Raleigh, Fayetteville, Greenville and Wilmington. "
         "You take the exam within 90 days of notice and wait 90 days to retest after a failed attempt.</p>"),
        ("study", "How should you study for a reference-book exam?",
         "<ul><li>Get the exact edition of every book on your exam's reference list.</li><li>Tab and highlight the sections that answer most questions, or buy them pre-tabbed.</li><li>Practice timed questions so lookups become automatic.</li><li>Take full practice exams in the last 2 weeks.</li></ul><p>Browse the <a href='/licenses/'>license list</a> to find the books for your classification, or read the <a href='/faq/'>FAQ</a>.</p>"),
    ]
    faq = [
        ("How long does it take to get a North Carolina contractor license?", "Most candidates study 4 to 8 weeks. Board review adds time before and after the exam, depending on the board and the application."),
        ("How much does an NCLBGC license cost?", "The application fee is $75 for Limited, $100 for Intermediate and $125 for Unlimited, plus PSI exam fees and the cost of showing working capital or a bond."),
        ("Do I need a license for work under $40,000?", "Not a general contractor license under G.S. 87-1. Electrical, plumbing, heating and fire sprinkler work still needs a license from those boards."),
        ("Do I need experience?", "The electrical and plumbing boards set experience hours by license, such as 4,000 hours for a plumbing or heating contractor. The NCLBGC checks your qualifications and finances."),
        ("Can a company hold the license?", "Yes. Licenses are issued to the business, with a qualifier who passed the exams."),
        ("What is the NASCLA exam?", "A national exam that North Carolina accepts for the NCLBGC Building classification and, with a rules test, for electrical contractors."),
        ("Which board licenses HVAC contractors?", "The Plumbing, Heating and Fire Sprinkler board, through Heating Groups 1, 2 and 3."),
    ]
    take = ["General contractor license required for projects of $40,000 or more.", "NCLBGC limits: $750,000, $1,500,000 or unlimited.", "NCLBGC exams: 70% to pass, open book.",
            "Electrical caps: $100,000 Limited, $200,000 Intermediate by statute.", "Plumbing Board: 7 testing centers; 90 days to test after notice."]
    crumbs = [("/", "Home"), (path, "How to get licensed")]
    howto = {"@type": "HowTo", "name": "How to get a North Carolina contractor license", "totalTime": "P8W",
             "step": [{"@type": "HowToStep", "position": i + 1, "name": a, "text": b} for i, (a, b) in enumerate(steps)]}
    return dict(path=path, title=title, desc=desc, h1="How to Get a North Carolina Contractor License", lead=lead, takeaways=take, sections=sections, faq=faq,
                sources=["gs87_1", "gs87_10", "ncac12a", "gs87_43", "ncac18b", "nascla_el", "gs87_21", "plb_app"], crumbs=crumbs, eyebrow="Licensing guide",
                side='<div class="side-box"><p class="side-h">On this page</p><ul class="toc">' + "".join(f'<li><a href="#{sid}">{E(h)}</a></li>' for sid, h, _ in sections) + "</ul></div>",
                ld=[webpage_ld(path, title, desc), howto, crumbs_ld(crumbs), faq_ld(faq)])


def faq_page():
    path = "/faq/"
    title = "North Carolina Contractor Exam FAQ | NC Exam Prep"
    desc = "Answers on North Carolina contractor exams: the $40,000 rule, passing scores, license limits, which board licenses you, shipping and how to order exam prep."
    lead = ("North Carolina contractor exams are reference-book tests run by three boards. NCLBGC applicants need 70 percent on a trade exam and the Business and Law exam, "
            "while electrical and plumbing candidates sit their own board's exam. The answers below cover exams, licenses and ordering from us.")
    sections = [
        ("about-the-exams", "What should you know about the exams?", "<ul><li>PSI gives the NCLBGC trade and Business and Law exams.</li><li>The electrical board gives its own written exams, and accepts NASCLA with a rules test.</li><li>The Plumbing Board tests daily at 7 centers across North Carolina.</li><li>Approved references are allowed in the room, so book editions matter.</li></ul>"),
        ("about-orders", "How do orders work?", f"<ul><li>Checkout runs on the 1 Exam Prep store.</li><li>Books and tabs ship free by USPS Media Mail inside the US.</li><li>Online courses and services are delivered by email.</li><li>All sales are final, so call {PHONE} if you are unsure.</li></ul>"),
        ("which-license", "Which license do you need?",
         "<p>The trade and the value of the work decide it. General contracting on a project of $40,000 or more needs an NCLBGC license in the right classification, such as Building, Residential, Highway or Roofing. "
         "Electrical contracting needs a Limited, Intermediate, Unlimited or special restricted license from the electrical board. "
         "Plumbing needs Class I for all buildings or Class II for single-family detached homes, and HVAC needs Heating Group 1, 2 or 3 from the Plumbing Board. "
         "Fuel gas piping and fire sprinkler contractors also license through the Plumbing Board. "
         "The <a href='/licenses/'>license list</a> groups every license we cover by board.</p>"),
        ("study-time", "How long should you study?",
         "<p>Most candidates need 4 to 8 weeks. Plan for more if you work full time or take a trade exam and Business and Law in the same month. "
         "A good split is 2 weeks learning the layout of each reference book, 2 to 4 weeks of practice questions, and a final 1 to 2 weeks of timed full-length exams. "
         "Because these exams allow reference books, the goal is fast lookups rather than memorizing. "
         "Read the <a href='/how-to-get-licensed/'>licensing guide</a> for the full process.</p>"),
        ("exam-day", "What should you bring on exam day?",
         "<p>Bring a government photo ID and the approval or admission notice from your board. For the NCLBGC exams at PSI and for the Plumbing Board exams, bring every allowed reference book in the edition on the reference list. "
         "Tabs must be permanently attached, and loose notes or papers tucked inside the books are not allowed. Arrive early so the books can be checked before you start. "
         "Check your board's candidate information for the exact list, because rules on calculators and highlighting can differ by exam.</p>"),
        ("still-stuck", "Can't find your answer?", f"<p>Call <a href='tel:{TEL}'>{PHONE}</a> or email <a href='mailto:{EMAIL}'>{EMAIL}</a>. You can also browse the <a href='/licenses/'>license pages</a> or the <a href='/how-to-get-licensed/'>licensing guide</a>.</p>"),
    ]
    faq = [
        ("When do I need a general contractor license?", "When a project costs $40,000 or more, under G.S. 87-1."),
        ("What score passes the NCLBGC exams?", "70 percent on both the trade exam and the Business and Law exam."),
        ("What are the NCLBGC limitations?", "Limited up to $750,000 per project, Intermediate up to $1,500,000 and Unlimited with no limit."),
        ("What working capital does each limitation need?", "$17,000 for Limited, $75,000 for Intermediate and $150,000 for Unlimited, or a $175,000, $500,000 or $1,000,000 bond."),
        ("What are the electrical license limits?", "The statute caps Limited at $100,000 and 1,000 volts and Intermediate at $200,000. Unlimited has no cap."),
        ("Where does the Plumbing Board test?", "Asheville, Charlotte, Winston-Salem, Raleigh, Fayetteville, Greenville and Wilmington, daily."),
        ("How much is shipping?", "Free for books and tabs by USPS Media Mail to US addresses."),
        ("Can I return books?", f'No. All sales are final under the <a href="{REFUND}" rel="noopener">1 Exam Prep refund policy</a>.'),
        ("Do you help with the board application?", "Yes. The License Application Service and The 1 Package include application help and business formation."),
        ("How do I reach a person?", f'Call <a href="tel:{TEL}">{PHONE}</a> or email <a href="mailto:{EMAIL}">{EMAIL}</a>.'),
    ]
    take = ["General contractor license at $40,000 or more.", "NCLBGC exams: 70% to pass.", "Plumbing Board tests daily at 7 centers.", "Free USPS Media Mail on books."]
    crumbs = [("/", "Home"), (path, "FAQ")]
    return dict(path=path, title=title, desc=desc, h1="North Carolina Contractor Exam FAQ", lead=lead, takeaways=take, sections=sections, faq=faq,
                sources=["gs87_1", "gs87_10", "ncac12a", "gs87_43", "plb_app"], crumbs=crumbs, eyebrow="FAQ",
                ld=[webpage_ld(path, title, desc), crumbs_ld(crumbs), faq_ld(faq)])


def contact_page():
    path = "/contact/"
    title = "Contact Pass Your NC Exam | Call (877) 775-9400"
    desc = "Call (877) 775-9400 or email sales@1examprep.com for help choosing North Carolina contractor exam books, courses and licensing services."
    lead = (f"The fastest way to reach us is by phone at {PHONE}. You can also email {EMAIL} or send the form below. Tell us your North Carolina license, "
            "your exam date and how you like to study, and we will point you to the right package, usually the same business day.")
    form = f'''<div class="form-wrap" id="contact-form" data-form="{FORM_ID}" data-source="passyournorthcarolinacontractorexam.com"><p>The contact form loads here. If it does not appear, call <a href="tel:{TEL}">{PHONE}</a> or email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div>'''
    cards = f'''<div class="contact-cards"><a class="cc" href="tel:{TEL}"><span>Call</span><b>{PHONE}</b></a><a class="cc" href="mailto:{EMAIL}"><span>Email</span><b>{EMAIL}</b></a><a class="cc" href="/licenses/"><span>Browse</span><b>All licenses</b></a></div>'''
    sections = [
        ("reach-us", "How can you reach us?", cards + "<p>Phone and email reach the same 1 Exam Prep team that ships the books. Calls get the quickest answer, and email works well when you want a written list of what to buy.</p>"),
        ("form", "Send a message", form),
        ("what-to-include", "What should you include in your message?", "<ul><li>The license or classification you are going for, for example Building Contractor or Heating Group 3.</li><li>Your exam date, or how many weeks you have to study.</li><li>Whether you already own any of the reference books.</li><li>If you want help with the board application or forming an LLC.</li></ul><p>With those 4 details we can usually recommend one package and tell you what it costs.</p>"),
        ("orders", "Need help with an order?", "<p>Include your order number and the email used at checkout. Books ship free by USPS Media Mail, which usually takes 2 to 8 business days. Online courses arrive by email after checkout, so check your spam folder before calling.</p>"),
        ("what-we-help-with", "What can the team help you with?",
         "<p>Most calls fall into one of five areas. Bring any of them to the phone or put them in an email.</p><ul>"
         "<li><b>Choosing books.</b> We match your classification to the exam's reference list, including the editions allowed in the testing room.</li>"
         "<li><b>Tabs and highlighting.</b> We explain what the pre-printed tabs cover and when a highlighted and tabbed set is worth the extra cost.</li>"
         "<li><b>Courses and live classes.</b> We compare the online course, the live virtual training and the rental packages for your schedule.</li>"
         "<li><b>The board application.</b> The License Application Service and the LLC setup take the paperwork off your hands.</li>"
         "<li><b>Company orders.</b> We quote books for several qualifiers or several classifications at once.</li></ul>"),
        ("company-accounts", "Can a company order for several people?",
         "<p>Yes. Contractors often order for 2 or more qualifiers at once, or for one person testing in several classifications, such as Building plus Business and Law, or Heating Group 3 plus SP-PH. "
         "Send the names of the licenses and how many sets you need, and the team will reply with one quote that lists every book, course and service with its price. "
         "Books for a company order ship free by USPS Media Mail to one US address, and course logins go by email to each person who will study.</p>"),
        ("before-you-call", "What happens after you get in touch?",
         "<p>A member of the 1 Exam Prep team reads every message and replies by phone or email, whichever you prefer. "
         "For product questions we usually send a short list: the package we recommend, its price and what is in the box. "
         "When you are ready, the Buy now button on any product page opens checkout with that item already in the cart. "
         "Questions about eligibility or experience are decided by the licensing boards, so we point you to the right board page when that is the real question. "
         "The three boards' official pages are in the sources list below.</p>"),
    ]
    faq = [
        ("What is your phone number?", f"Call {PHONE}. The same number handles product questions and order help."),
        ("What is your email address?", f"Email {EMAIL} for quotes, product lists and order questions."),
        ("How fast do you reply?", "Most emails and form messages get a reply the same business day."),
        ("Can you tell me which books my exam needs?", "Yes. Give us the license and we will match it to the exam's reference list."),
        ("Do you offer group or company orders?", "Yes. Contact us with the number of candidates and licenses, and we will put together a quote."),
        ("Are you part of a licensing board or PSI?", "No. We are an independent exam prep provider. Licensing decisions are made by the North Carolina boards."),
    ]
    take = [f"Phone: {PHONE}.", f"Email: {EMAIL}.", "Most messages answered the same business day.", "Include your license and exam date."]
    crumbs = [("/", "Home"), (path, "Contact")]
    cp = webpage_ld(path, title, desc, "ContactPage"); cp["mainEntity"] = {"@id": SITE + "/#org"}
    return dict(path=path, title=title, desc=desc, h1="Contact Us", lead=lead, takeaways=take, sections=sections, faq=faq,
                sources=["nclbgc", "ncbeec", "plb"], crumbs=crumbs, eyebrow="Contact",
                ld=[cp, ld_org(), crumbs_ld(crumbs), faq_ld(faq)])


# ---------------------------------------------------------------- blog
def nice_date(d):
    import datetime
    return datetime.date.fromisoformat(d).strftime("%B %-d, %Y")


def post_page(post):
    path = f"/blog/{post['slug']}/"
    crumbs = [("/", "Home"), ("/blog/", "Blog"), (path, post["title"])]
    byline = (f'<div class="post-meta">By <span class="author">{AUTHOR}</span> · Published <time datetime="{post["date"]}">{nice_date(post["date"])}</time>'
              f' · Updated <time datetime="{post["updated"]}">{nice_date(post["updated"])}</time></div>')
    words = sum(wc(b) for _, _, b in post["sections"])
    art = {"@type": "BlogPosting", "@id": SITE + path + "#post", "headline": post["title"], "url": SITE + path, "mainEntityOfPage": SITE + path,
           "description": post["meta_desc"], "image": SITE + "/assets/img/og.jpg", "datePublished": post["date"], "dateModified": post["updated"],
           "author": {"@type": "Person", "name": AUTHOR}, "publisher": publisher(), "inLanguage": "en-US", "keywords": ", ".join(post["tags"]),
           "articleSection": "North Carolina contractor licensing", "wordCount": words, "isPartOf": {"@id": SITE + "/blog/#blog"}}
    others = [x for x in POSTS if x is not post]
    related = "".join(f'<li><a href="/blog/{x["slug"]}/">{E(x["title"])}</a></li>' for x in others)
    side = ('<div class="side-box"><p class="side-h">In this post</p><ul class="toc">' + "".join(f'<li><a href="#{sid}">{E(h)}</a></li>' for sid, h, _ in post["sections"]) + "</ul></div>"
            + (f'<div class="side-box"><p class="side-h">More from the blog</p><ul class="toc">{related}</ul></div>' if related else ""))
    return dict(path=path, title=post["meta_title"], desc=post["meta_desc"], h1=post["title"], lead=E(post["lead"]), takeaways=post["takeaways"],
                sections=post["sections"], faq=post["faq"], sources=post["sources"], crumbs=crumbs, eyebrow="Blog · " + post["tags"][0],
                byline=byline, side=side, article=True, ld=[art, crumbs_ld(crumbs), faq_ld(post["faq"])])


def post_card(x):
    return (f'<li class="post-card"><p class="post-tag">{E(x["tags"][0])}</p><h3 id="post-{x["slug"]}"><a href="/blog/{x["slug"]}/">{E(x["title"])}</a></h3>'
            f'<p>{E(x["excerpt"])}</p><p class="post-by">By {AUTHOR} · <time datetime="{x["date"]}">{nice_date(x["date"])}</time></p>'
            f'<a class="more" href="/blog/{x["slug"]}/">Read the answers</a></li>')


def blog_index():
    path = "/blog/"
    title = "North Carolina Contractor Exam Blog | Pass Your NC Exam"
    desc = "Plain-English guides to North Carolina contractor licensing: NCLBGC, electrical and plumbing board rules, exams, study plans and costs. Checked against statute."
    lead = ("The Pass Your NC Exam blog answers the questions North Carolina contractors ask before they test: which board licenses them, what the exams cover, "
            "how long to study and what it costs. Every post is checked against the General Statutes and board pages and dated, so you know the facts are current.")
    cards = "".join(post_card(x) for x in POSTS)
    latest = POSTS[0]
    n = len(POSTS)
    sections = [
        ("latest-posts", "What are the latest posts?", f'<p>{n} post{"s" if n != 1 else ""} so far, newest first. Each one opens with a short answer, then goes question by question with tables, a FAQ and a list of official sources.</p><ul class="post-list">{cards}</ul>'),
        ("start-here", "Where should a new candidate start?",
         "<p>Start with the board, because everything else follows from it. General contracting on a project of $40,000 or more means the NCLBGC. Electrical work means the electrical board, and plumbing, HVAC, fuel piping and fire sprinkler work means the Plumbing Board. "
         f"Then read <a href='/blog/{latest['slug']}/'>{E(latest['title'])}</a> for the questions most people ask, and the <a href='/how-to-get-licensed/'>licensing guide</a> for the step-by-step process. "
         "When you know your classification, its <a href='/licenses/'>license page</a> lists the exams, the limits and every book and course we carry for it.</p>"
         "<ol><li>Pick the board by your trade.</li><li>Pick the classification, such as Building, Unlimited Electrical or Heating Group 3.</li>"
         "<li>Check the reference list for your exam and its editions.</li><li>Get the books 4 to 8 weeks before your exam date.</li><li>Tab, practice and take 2 timed exams before test day.</li></ol>"),
        ("topics", "What does the blog cover?",
         "<ul><li><b>Licensing rules:</b> the $40,000 general contractor threshold, the $750,000 and $1,500,000 limitations, and the electrical caps of $100,000 and $200,000.</li>"
         "<li><b>The exams:</b> the NCLBGC trade and Business and Law exams at 70 percent, the electrical board exams and the Plumbing Board's 7 testing centers.</li>"
         "<li><b>Studying:</b> how to tab and highlight books for a reference-book test, and how long to plan for.</li>"
         "<li><b>Costs:</b> the $75 to $125 NCLBGC application fee, exam fees, bonds and study materials.</li>"
         "<li><b>After the exam:</b> applications, working capital, business setup and renewals.</li></ul>"),
        ("how-we-check", "How are the facts checked?",
         "<p>Every number in a post comes from an official source: the North Carolina General Statutes in Chapter 87, the NC Administrative Code, or the boards' own pages. "
         "Each post links its sources at the bottom and shows the date it was last updated. When a rule changes, such as the move of the general contractor threshold from $30,000 to $40,000, the affected posts are updated and re-dated. "
         f"Spot something out of date? Email {EMAIL} and we will fix it.</p>"),
        ("who-writes", "Who writes the posts?",
         f"<p>Posts are written by {AUTHOR} for 1 Exam Prep, which supplies exam prep books, tabs and courses to contractors across the country. "
         f"The team behind the blog also answers the phone at {PHONE}, so the questions in each post are the ones contractors actually ask us. "
         "Posts stay practical: what the rule is, what it means for your next job, and what to study. Licensing decisions belong to the boards, and the posts say so when a question needs an official answer.</p>"),
        ("study-plan", "How long should you study for a North Carolina exam?",
         "<p>Most candidates need 4 to 8 weeks. A simple plan that works for all three boards:</p>"
         "<table><thead><tr><th>Week</th><th>Focus</th></tr></thead><tbody><tr><td>1 to 2</td><td>Learn the layout of each reference book; place tabs.</td></tr>"
         "<tr><td>3 to 5</td><td>Practice questions by topic; highlight the answers you look up.</td></tr><tr><td>6</td><td>Business and Law practice for NCLBGC candidates.</td></tr>"
         "<tr><td>7 to 8</td><td>2 or more full timed practice exams, then review misses.</td></tr></tbody></table>"
         "<p>Candidates with less time often choose highlighted and tabbed book sets or a live virtual class to shorten weeks 1 and 2.</p>"),
        ("key-numbers", "What numbers should every North Carolina candidate know?",
         "<ul><li><b>$40,000:</b> the project cost that triggers an NCLBGC license under G.S. 87-1.</li>"
         "<li><b>70 percent:</b> the passing score on the NCLBGC trade and Business and Law exams.</li>"
         "<li><b>$17,000, $75,000 and $150,000:</b> working capital for the Limited, Intermediate and Unlimited limitations.</li>"
         "<li><b>15 tons:</b> the line between Heating Group 2 and Heating Group 3.</li>"
         "<li><b>90 days:</b> the window to take a Plumbing Board exam after notice, and the wait after a failed attempt.</li></ul>"
         "<p>Before you bid near a limit or book an exam, check the date on the post and the linked statute or board page.</p>"),
        ("popular-licenses", "Which licenses do readers ask about most?",
         "<p>Five licenses account for most of the questions we get from North Carolina contractors. Each link goes to the license page with its exams, limits and study packages.</p><ul>"
         + "".join(f"<li><a href='/{l}/'>{E(BY_SLUG[l]['name'])}</a>: {E(BY_SLUG[l]['scope'])}</li>" for l in ("building-contractor", "residential-contractor", "unlimited-electrical", "heating-group-3-class-1", "plumbing-class-i"))
         + "</ul>"),
    ]
    faq = [
        ("How often is the blog updated?", "Posts are reviewed when a board or statute changes a rule, fee or exam, and each post shows its last updated date."),
        ("Who is the author?", f"Posts are written by {AUTHOR} for 1 Exam Prep and checked against the statutes and board pages."),
        ("Can I suggest a topic?", f"Yes. Email {EMAIL} with your question and it may become the next post."),
        ("Is the blog official licensing advice?", "No. The blog explains the rules in plain English. The boards make licensing decisions."),
        ("Where are the exam books?", "Every license page lists the books, tabs and courses for that exam, with free USPS Media Mail shipping on books."),
        ("How do I get help choosing a package?", f"Call {PHONE} or use the contact page, and tell us your license and exam date."),
    ]
    take = [f"{n} post{'s' if n != 1 else ''}, written by {AUTHOR} and checked against statute and board pages.", "Start with the board: NCLBGC, electrical or Plumbing Board.",
            "Most candidates study 4 to 8 weeks.", "Every post lists its official sources and update date."]
    crumbs = [("/", "Home"), (path, "Blog")]
    blog_ld = {"@type": "Blog", "@id": SITE + "/blog/#blog", "url": SITE + path, "name": "Pass Your NC Exam blog", "description": desc, "publisher": publisher(), "inLanguage": "en-US",
               "blogPost": [{"@type": "BlogPosting", "headline": x["title"], "url": f"{SITE}/blog/{x['slug']}/", "datePublished": x["date"], "dateModified": x["updated"],
                             "author": {"@type": "Person", "name": AUTHOR}} for x in POSTS]}
    il = {"@type": "ItemList", "name": "Blog posts", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}/blog/{x['slug']}/", "name": x["title"]} for i, x in enumerate(POSTS)]}
    pop = ("building-contractor", "residential-contractor", "unlimited-electrical", "heating-group-3-class-1", "plumbing-class-i")
    side = '<div class="side-box"><p class="side-h">Popular licenses</p><ul class="toc">' + "".join(f'<li><a href="/{l}/">{E(BY_SLUG[l]["name"])}</a></li>' for l in pop) + "</ul></div>"
    return dict(path=path, title=title, desc=desc, h1="North Carolina Contractor Exam Blog", lead=lead, takeaways=take, sections=sections, faq=faq,
                sources=["gs87_1", "gs87_10", "gs87_43", "gs87_21", "plb_app"], crumbs=crumbs, eyebrow="Blog", side=side,
                ld=[blog_ld, webpage_ld(path, title, desc, "CollectionPage"), il, crumbs_ld(crumbs), faq_ld(faq)])


# ---------------------------------------------------------------- build
def main():
    if os.path.exists(MANIFEST):
        for f in json.load(open(MANIFEST)):
            fp = os.path.join(OUT, f)
            if os.path.isfile(fp):
                os.remove(fp)
    os.makedirs(OUT, exist_ok=True)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"), dirs_exist_ok=True)
    prods = load_products()
    by = defaultdict(list)
    for p in prods:
        by[p["lic"]].append(p)
    counts = {l["slug"]: len(by[l["slug"]]) for l in LICENSES}
    prices = {l["slug"]: (min(x["price"] for x in by[l["slug"]]) if by[l["slug"]] else 0) for l in LICENSES}
    pages = [home_page(counts, prices, len(prods)), licenses_index(counts, prices, len(prods)), guide_page(), faq_page(), contact_page(), blog_index()] + [post_page(x) for x in POSTS]
    live = [l for l in LICENSES if by[l["slug"]]]
    for l in live:
        pages.append(license_page(l, by[l["slug"]]))
    taken = set(p["title"] for p in pages)
    for l in live:
        for p in by[l["slug"]]:
            pages.append(product_page(p, l, by[l["slug"]], taken))
    for pg in pages:
        write(pg["path"], render(pg))
    nf = dict(path="/404.html", title="Page Not Found | Pass Your NC Exam", desc="That page moved or never existed. Browse North Carolina contractor licenses or call (877) 775-9400 for help.",
              ld=[], h1="Page not found")
    write("/404.html", head(nf).replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">') + header() +
          f'<main id="main" class="wrap single nf"><h1>Page not found</h1><p class="lead">That page moved or never existed. Try the <a href="/licenses/">license list</a>, the <a href="/faq/">FAQ</a> or call <a href="tel:{TEL}">{PHONE}</a>.</p></main>' + footer())
    urls = "".join(f"<url><loc>{SITE}{pg['path']}</loc><lastmod>{CHECKED}</lastmod></url>" for pg in pages)
    open(os.path.join(OUT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(os.path.join(OUT, "robots.txt"), "w").write(
        "User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in ("GPTBot", "ClaudeBot", "Google-Extended", "PerplexityBot", "Bingbot")) + f"Sitemap: {SITE}/sitemap.xml\n")
    lic_lines = "\n".join(f"- [{l['name']}]({SITE}/{l['slug']}/): {counts[l['slug']]} packages from {money(prices[l['slug']])}. {l['scope']}" for l in live)
    blog_lines = "\n".join(f"- [{x['title']}]({SITE}/blog/{x['slug']}/): {x['excerpt']}" for x in POSTS)
    llms = f"""# {BRAND}

> Exam prep books, pre-printed tabs, online courses, live classes and licensing services for North Carolina contractor exams (Licensing Board for General Contractors, State Board of Examiners of Electrical Contractors, and State Board of Examiners of Plumbing, Heating and Fire Sprinkler Contractors). {len(prods)} products for {len(live)} licenses, fulfilled by 1 Exam Prep. Contact: {PHONE}, {EMAIL}.

## Key facts (checked {CHECKED_TEXT})
- General contractor license (NCLBGC) required for projects of $40,000 or more (G.S. 87-1).
- NCLBGC limitations: Limited up to $750,000, Intermediate up to $1,500,000, Unlimited no limit; working capital $17,000 / $75,000 / $150,000 or bond $175,000 / $500,000 / $1,000,000.
- NCLBGC trade and Business and Law exams: 70% to pass, open book; NASCLA accepted for Building.
- Electrical: Limited capped at $100,000 and 1,000 volts, Intermediate at $200,000, Unlimited any value (G.S. 87-43.3).
- Plumbing Board: Class I all structures, Class II single-family detached; Heating Group 2 over 15 tons; exams daily at 7 testing centers.
- Books ship free by USPS Media Mail (US only). All sales final.

## Main pages
- [Home]({SITE}/)
- [All licenses]({SITE}/licenses/)
- [How to get a North Carolina contractor license]({SITE}/how-to-get-licensed/)
- [FAQ]({SITE}/faq/)
- [Contact]({SITE}/contact/)
- [Blog]({SITE}/blog/)
{blog_lines}

## Licenses
{lic_lines}
"""
    open(os.path.join(OUT, "llms.txt"), "w").write(llms)
    open(os.path.join(OUT, "agents.md"), "w").write(llms.replace(f"# {BRAND}", f"# {BRAND}: agent guide") + f"\n## Buying\nEach product page has a Buy now link to {CART.format('<variant-id>')} on the 1 Exam Prep store. Product pages carry Product JSON-LD with price, availability, shipping and return policy.\n")
    open(os.path.join(OUT, "CNAME"), "w").write("passyournorthcarolinacontractorexam.com\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    made = []
    for d, dirs, fs in os.walk(OUT):
        dirs[:] = [x for x in dirs if x not in (".git", "source")]
        for f in fs:
            r = os.path.relpath(os.path.join(d, f), OUT)
            if r not in (".build-manifest.json", "README.md"):
                made.append(r)
    json.dump(sorted(made), open(MANIFEST, "w"), indent=0)
    print(f"built {len(pages)} pages ({len(prods)} products, {len(live)} licenses) into {OUT}")


if __name__ == "__main__":
    main()
