import re, json, os, shutil, html as H
from seo_data import SITE, ORG_DESC, SERVICES, BYKEY

SRC = open('body.html').read()
CSS = SRC[SRC.index('<style>') + 7: SRC.index('</style>')]
SCRIPT = SRC[SRC.index('<script>') + 8: SRC.rindex('</script>')]
HEADER = SRC[SRC.index('<header class="site-header">'): SRC.index('</header>') + 9]
FOOTER = SRC[SRC.index('<footer class="site-footer">'): SRC.index('</footer>') + 9]

def page_block(name):
    start = SRC.index(f'<div class="page" data-page="{name}">')
    start = SRC.index('>', start) + 1
    nxt = [SRC.find(f'<div class="page" data-page="{n}">') for n in ('home', 'services', 'about', 'contact')]
    ends = [i for i in nxt if i > start] + [SRC.index('</main>')]
    end = min(ends)
    block = re.sub(r'\s*<!--[^>]*-->\s*$', '', SRC[start:end].rstrip()).rstrip()
    assert block.endswith('</div>')
    return block[:-6]

SLUG = {s['key']: s['slug'] + '.html' for s in SERVICES}

def rewrite(h):
    h = re.sub(r'href="#services" data-link data-target="svc-(\w+)"', lambda m: f'href="{SLUG[m.group(1)]}"', h)
    h = re.sub(r'href="#contact" data-link data-reason="(\w+)"', r'href="contact.html?reason=\1"', h)
    h = h.replace('href="#home" data-link', 'href="index.html"').replace('href="#services" data-link', 'href="services.html"')
    h = h.replace('href="#about" data-link', 'href="about.html"').replace('href="#contact" data-link', 'href="contact.html"')
    assert 'data-link' not in h, re.findall(r'.{60}data-link.{60}', h)[:3]
    return h

EXTRA_CSS = """
.crumbs{display:flex;flex-wrap:wrap;gap:6px;list-style:none;margin:0 0 22px;padding:0;font-size:.92rem;color:var(--on-navy-soft)}
.crumbs li+li::before{content:"/";margin-right:6px;color:rgba(169,184,206,.5)}
.crumbs a{color:var(--on-navy-soft);text-decoration:none}
.crumbs a:hover{color:#fff;text-decoration:underline}
.crumbs [aria-current]{color:#fff}
.head-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:30px}
.page-head .lede{max-width:66ch}
.svc-row h2 a{color:inherit;text-decoration:none}
.svc-row h2 a:hover{color:var(--cobalt)}
.more{display:inline-flex;align-items:center;gap:6px;margin-top:16px;font-weight:600;text-decoration:none}
.more:hover{text-decoration:underline}
.detail-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:clamp(28px,5vw,72px)}
.detail-grid h2{font-size:clamp(1.5rem,1.2rem + 1vw,2rem);margin-bottom:14px}
.detail-grid p{color:var(--steel)}
@media (max-width: 820px){.detail-grid{grid-template-columns:1fr}}
.incl.one{grid-template-columns:1fr}
.related{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0 clamp(20px,4vw,48px)}
.related li{border-top:1px solid var(--mist)}
.related a{display:block;padding:20px 0;text-decoration:none;color:inherit}
.related h3{transition:color .2s;margin-bottom:6px}
.related p{color:var(--steel)}
.related a:hover h3{color:var(--cobalt)}
@media (max-width: 820px){.related{grid-template-columns:1fr}}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.nf{min-height:50vh;display:grid;align-content:center;gap:18px}
"""

JS_COMMON = """
(function () {
  const navLinks = document.getElementById('nav-links');
  const toggle = document.querySelector('.menu-toggle');
  toggle.addEventListener('click', () => {
    const open = navLinks.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  });
  const y = document.getElementById('year'); if (y) y.textContent = new Date().getFullYear();
})();
"""
cfg = SCRIPT[:SCRIPT.index('(function () {')]
hero = SCRIPT[SCRIPT.index('  /* ---------- Hero'): SCRIPT.index('  /* ---------- Contact form')]
form = SCRIPT[SCRIPT.index('  /* ---------- Contact form'): SCRIPT.index("  show(location.hash")]
hero = hero.replace("  window.addEventListener('resize', () => { size(); draw(); });", "  window.addEventListener('resize', () => { size(); draw(); });\n  startHero();")
JS_HERO = "(function () {\n  if (!document.getElementById('trace')) return;\n" + hero + "})();\n"
form = form.replace("  const form = document.getElementById('contact-form');",
  "  const form = document.getElementById('contact-form');\n  if (!form) return;\n  try { const r = new URLSearchParams(location.search).get('reason'); const sel = document.getElementById('f-reason'); if (r && sel && [...sel.options].some(o => o.value === r)) sel.value = r; } catch (_) {}")
JS_FORM = "(function () {\n" + form + "})();\n"
SITE_JS = cfg + JS_COMMON + JS_HERO + JS_FORM

HEADER_R = rewrite(HEADER)
FOOTER_R = rewrite(FOOTER)
FOOTER_R = FOOTER_R.replace('<h3>Services</h3>', '<h3>Services</h3>', 1)
# fuller footer service list for internal linking
svc_links = ''.join(f'<li><a href="{SLUG[k]}">{n}</a></li>' for k, n in [
    ('managed', '24/7/365 managed IT'), ('ai', 'AI-powered monitoring'), ('cyber', 'Cybersecurity'), ('cloud', 'Cloud solutions'),
    ('backup', 'Backup and recovery'), ('datacenter', 'Datacenter services')])
FOOTER_R = re.sub(r'(<h3>Services</h3>\s*<ul>).*?(</ul>)', lambda m: m.group(1) + svc_links + '<li><a href="services.html">All services</a></li>' + m.group(2), FOOTER_R, flags=re.S)

ORG = {"@type": "Organization", "@id": SITE + "/#organization", "name": "KU Tech, LLC", "alternateName": "Ku Tech",
       "url": SITE + "/", "logo": SITE + "/images/kutech-logo.png", "image": SITE + "/images/og-image.jpg",
       "description": ORG_DESC, "slogan": "Managed IT, Cybersecurity, Cloud Solutions, and More",
       "knowsAbout": ["Managed IT services", "Cybersecurity", "Cloud computing", "Microsoft 365", "Backup and disaster recovery",
                      "Datacenter infrastructure", "IT project management", "AI-powered IT monitoring"],
       "contactPoint": {"@type": "ContactPoint", "contactType": "customer support", "url": SITE + "/contact.html",
                        "availableLanguage": "English",
                        "hoursAvailable": {"@type": "OpeningHoursSpecification",
                                           "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                           "opens": "00:00", "closes": "23:59"}}}

def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + "/" + u} for i, (n, u) in enumerate(items)]}

def faq_ld(pairs):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}

def crumbs_html(items):
    lis = []
    for i, (n, u) in enumerate(items):
        lis.append(f'<li aria-current="page">{H.escape(n)}</li>' if i == len(items) - 1 else f'<li><a href="{u or "index.html"}">{H.escape(n)}</a></li>')
    return '<nav aria-label="Breadcrumb"><ol class="crumbs">' + ''.join(lis) + '</ol></nav>'

def doc(fname, title, desc, body, ld, inline, current=None, og_type="website", preload=None):
    canon = SITE + '/' + ('' if fname == 'index.html' else fname)
    graph = {"@context": "https://schema.org", "@graph": [ORG] + ld}
    head = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f'<title>{H.escape(title)}</title>',
        f'<meta name="description" content="{H.escape(desc)}">',
        f'<link rel="canonical" href="{canon}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        '<meta name="theme-color" content="#0B1B33">',
        f'<meta property="og:type" content="{og_type}">', '<meta property="og:site_name" content="Ku Tech">',
        f'<meta property="og:title" content="{H.escape(title)}">', f'<meta property="og:description" content="{H.escape(desc)}">',
        f'<meta property="og:url" content="{canon}">', f'<meta property="og:image" content="{SITE}/images/og-image.jpg">',
        '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
        '<meta property="og:image:alt" content="Ku Tech logo over a network of blue cables">', '<meta property="og:locale" content="en_US">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<link rel="icon" type="image/svg+xml" href="images/kutech-mark.svg">', '<link rel="icon" type="image/png" href="images/favicon.png">',
        '<link rel="apple-touch-icon" href="images/apple-touch-icon.png">',
        '<link rel="preconnect" href="https://fonts.googleapis.com">', '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Hanken+Grotesk:wght@400..700&display=swap">',
    ]
    if preload:
        head.append(f'<link rel="preload" as="image" href="{preload[0]}" imagesrcset="{preload[1]}" imagesizes="100vw" fetchpriority="high">')
    head.append(f'<style>{CSS}{EXTRA_CSS}</style>' if inline else '<link rel="stylesheet" href="styles.css">')
    head.append('<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False) + '</script>')
    hdr = HEADER_R
    if current:
        hdr = hdr.replace(f'<li><a href="{current}">', f'<li><a href="{current}" aria-current="page">', 1)
    script = f'<script>{SITE_JS}</script>' if inline else '<script src="site.js" defer></script>'
    body_html = f'<a class="skip" href="#main">Skip to content</a>\n{hdr}\n<main id="main" tabindex="-1">\n{body}\n</main>\n{FOOTER_R}\n{script}'
    if inline:  # artifact skeleton adds doctype/html/head/body
        return '\n'.join(head[2:]) + '\n' + body_html + '\n'
    return '<!doctype html>\n<html lang="en">\n<head>\n' + '\n'.join(head) + '\n</head>\n<body>\n' + body_html + '\n</body>\n</html>\n'

CHK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 5 5L20 7"/></svg>'
PM = '<span class="pm" aria-hidden="true"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg></span>'
ALT = {"help-desk": "A support specialist wearing a headset, smiling at her computer", "monitoring": "A monitoring screen showing live performance charts",
       "security": "Close-up of a laptop keyboard glowing blue", "cloud": "Illustration of a cloud icon surrounded by floating data charts",
       "server-rack": "Rows of neatly cabled servers glowing in a dark rack", "technician": "An engineer connecting cables in a server rack",
       "team": "A team meeting around a long table in a bright office", "business-owners": "Two small business owners standing proudly in their cafe",
       "hero-network": "Blue network cables connected to a switch"}

def service_page(s, inline):
    items = [("Home", "index.html"), ("Services", "services.html"), (s["name"], s["slug"] + ".html")]
    incl = ''.join(f'<li>{CHK}{H.escape(x)}</li>' for x in s["included"])
    faqs = ''.join(f'<details><summary>{H.escape(q)}{PM}</summary><p>{H.escape(a)}</p></details>' for q, a in s["faqs"])
    rel = ''.join(f'<li><a href="{BYKEY[k]["slug"]}.html"><h3>{H.escape(BYKEY[k]["name"])}</h3><p>{H.escape(BYKEY[k]["short"])}</p></a></li>' for k in s["related"])
    p = s["photo"]
    body = f'''<header class="page-head">
  <div class="wrap">
    {crumbs_html(items)}
    <h1>{H.escape(s["name"])}</h1>
    <p class="lede">{H.escape(s["intro"])}</p>
    <div class="head-actions"><a class="btn btn-primary" href="contact.html?reason=assessment">Book a free IT assessment</a><a class="btn btn-ghost" href="services.html">All services</a></div>
  </div>
</header>
<section>
  <div class="wrap split">
    <div class="stack-lg"><h2>What's included</h2><ul class="incl one">{incl}</ul></div>
    <div class="photo"><img src="images/{p}.webp" srcset="images/{p}-sm.webp 800w, images/{p}.webp 1600w" sizes="(max-width: 880px) 100vw, 50vw" alt="{ALT[p]}" width="1600" height="1067" loading="lazy"></div>
  </div>
</section>
<section class="band-white">
  <div class="wrap detail-grid">
    <div><h2>Who it's for</h2><p>{H.escape(s["who"])}</p></div>
    <div><h2>How Ku Tech delivers it</h2><p>{H.escape(s["how"])}</p></div>
  </div>
</section>
<section>
  <div class="wrap">
    <div class="section-head"><h2>Questions about {H.escape(s["name"][0].lower() + s["name"][1:]) if not s["name"].startswith(("IT","AI")) else H.escape(s["name"])}</h2></div>
    <div class="faq">{faqs}</div>
  </div>
</section>
<section class="band-white">
  <div class="wrap">
    <div class="section-head"><h2>Related services</h2></div>
    <ul class="related">{rel}</ul>
  </div>
</section>
<div class="wrap" style="margin-top:clamp(64px,9vw,120px)">
  <div class="cta">
    <div><h2>See how Ku Tech can help.</h2><p>Book a free, no-obligation IT assessment and get a clear plan for your business.</p></div>
    <a class="btn" href="contact.html?reason=assessment">Book your free assessment</a>
  </div>
</div>'''
    svc = {"@type": "Service", "@id": SITE + "/" + s["slug"] + ".html#service", "name": s["name"], "serviceType": s["name"],
           "description": s["intro"], "url": SITE + "/" + s["slug"] + ".html", "provider": {"@id": SITE + "/#organization"},
           "hasOfferCatalog": {"@type": "OfferCatalog", "name": s["name"], "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": x}} for x in s["included"]]}}
    ld = [svc, crumbs_ld([(n, "" if u == "index.html" else u) for n, u in items]), faq_ld(s["faqs"])]
    return doc(s["slug"] + ".html", s["meta_title"], s["meta_desc"], body, ld, inline, current="services.html", og_type="article")

def build(outdir, inline):
    os.makedirs(outdir, exist_ok=True)
    # HOME
    home = rewrite(page_block('home'))
    home = home.replace('alt="" fetchpriority="high">', 'alt="" fetchpriority="high" width="1600" height="1067">')
    ld_home = [{"@type": "WebSite", "@id": SITE + "/#website", "name": "Ku Tech", "url": SITE + "/", "publisher": {"@id": SITE + "/#organization"}}]
    open(f'{outdir}/index.html', 'w').write(doc('index.html', 'Managed IT Services & 24/7/365 IT Support | Ku Tech',
        'Managed IT services, cybersecurity and cloud solutions with 24/7/365 support and AI-powered monitoring. Ku Tech keeps you running so you can focus on business.',
        home, ld_home, inline, current='index.html', preload=('images/hero-network.webp', 'images/hero-network-sm.webp 800w, images/hero-network.webp 1600w')))
    # SERVICES overview
    sv = page_block('services')
    for s in SERVICES:
        k = s['key']
        sv = re.sub(rf'(<article class="svc-row" id="svc-{k}" tabindex="-1">\s*<div>)<h2>(.*?)</h2>(<p class="desc">.*?</p>)',
                    lambda m: f'{m.group(1)}<h2><a href="{s["slug"]}.html">{m.group(2)}</a></h2>{m.group(3)}<a class="more" href="{s["slug"]}.html">Learn more<span class="sr-only"> about {H.escape(s["name"])}</span> <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>', sv, count=1, flags=re.S)
    assert sv.count('class="more"') == len(SERVICES)
    sv = re.sub(r'<a href="#services" data-link data-target="svc-(\w+)">', r'<a href="#svc-\1">', sv)
    sv = rewrite(sv)
    sv = sv.replace('<div class="wrap">\n      <h1>', '<div class="wrap">\n      ' + crumbs_html([("Home", "index.html"), ("Services", "services.html")]) + '\n      <h1>', 1)
    faqs_sv = re.findall(r'<summary>(.*?)<span class="pm".*?</summary><p>(.*?)</p>', sv, re.S)
    ld_sv = [{"@type": "ItemList", "name": "Ku Tech IT services", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "url": SITE + "/" + s["slug"] + ".html", "name": s["name"]} for i, s in enumerate(SERVICES)]},
             crumbs_ld([("Home", ""), ("Services", "services.html")]), faq_ld([(H.unescape(q), H.unescape(a)) for q, a in faqs_sv])]
    open(f'{outdir}/services.html', 'w').write(doc('services.html', 'IT Services: Managed IT, Cybersecurity & Cloud | Ku Tech',
        'Ku Tech IT services: 24/7/365 managed IT, AI monitoring, cybersecurity, cloud, backup, datacenter, equipment, mobile workforce and project management.',
        sv, ld_sv, inline, current='services.html'))
    # ABOUT
    ab = rewrite(page_block('about'))
    ab = ab.replace('<div class="wrap">\n      <h1>', '<div class="wrap">\n      ' + crumbs_html([("Home", "index.html"), ("About us", "about.html")]) + '\n      <h1>', 1)
    open(f'{outdir}/about.html', 'w').write(doc('about.html', 'About Ku Tech | Customer-Focused Managed IT Services',
        'KU Tech, LLC is a customer-focused managed IT company combining experienced engineers and AI-powered tools for cost-efficient, future-ready IT.',
        ab, [{"@type": "AboutPage", "url": SITE + "/about.html", "about": {"@id": SITE + "/#organization"}}, crumbs_ld([("Home", ""), ("About us", "about.html")])], inline, current='about.html'))
    # CONTACT
    ct = rewrite(page_block('contact'))
    ct = ct.replace('<div class="wrap">\n      <h1>', '<div class="wrap">\n      ' + crumbs_html([("Home", "index.html"), ("Contact", "contact.html")]) + '\n      <h1>', 1)
    open(f'{outdir}/contact.html', 'w').write(doc('contact.html', 'Contact Ku Tech | Book a Free IT Assessment',
        'Contact Ku Tech to book a free IT assessment, request a quote or get help with managed IT, cybersecurity and cloud services. We reply to every message.',
        ct, [{"@type": "ContactPage", "url": SITE + "/contact.html", "about": {"@id": SITE + "/#organization"}}, crumbs_ld([("Home", ""), ("Contact", "contact.html")])], inline, current='contact.html'))
    # SERVICE PAGES
    for s in SERVICES:
        open(f'{outdir}/{s["slug"]}.html', 'w').write(service_page(s, inline))
    # 404
    nf = '<section><div class="wrap nf"><h1 style="font-size:clamp(2.4rem,1.5rem + 4vw,4rem)">We couldn\'t find that page.</h1><p class="lede">The link may be old or mistyped. Try one of these instead.</p><div class="head-actions"><a class="btn btn-primary" href="index.html">Go to the home page</a><a class="btn btn-line" href="services.html">See our services</a><a class="btn btn-line" href="contact.html">Contact us</a></div></div></section>'
    d404 = doc('404.html', 'Page not found | Ku Tech', 'The page you were looking for could not be found.', nf, [], inline)
    d404 = d404.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">').replace(f'<link rel="canonical" href="{SITE}/404.html">\n', '')
    open(f'{outdir}/404.html', 'w').write(d404)
    if not inline:
        open(f'{outdir}/styles.css', 'w').write(CSS.strip() + '\n' + EXTRA_CSS.strip() + '\n')
        open(f'{outdir}/site.js', 'w').write(SITE_JS)
        urls = [('', '1.0'), ('services.html', '0.9'), ('about.html', '0.7'), ('contact.html', '0.8')] + [(s['slug'] + '.html', '0.8') for s in SERVICES]
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
            f'  <url><loc>{SITE}/{u}</loc><lastmod>2026-09-25</lastmod><priority>{p}</priority></url>\n' for u, p in urls) + '</urlset>\n'
        open(f'{outdir}/sitemap.xml', 'w').write(sm)
        open(f'{outdir}/robots.txt', 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n')
    # images
    os.makedirs(f'{outdir}/images', exist_ok=True)
    for f in os.listdir('images'):
        if f.endswith(('.webp', '.svg')) or f in ('favicon.png', 'kutech-logo.png', 'og-image.jpg', 'apple-touch-icon.png'):
            shutil.copy(f'images/{f}', f'{outdir}/images/{f}')

build('dist', inline=False)
build('preview', inline=True)
print('built', sorted(os.listdir('dist')))
