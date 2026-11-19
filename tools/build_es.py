"""Builds the Spanish version of the site (es/*.html) from the English pages and adds the language switch to both.
Run from the repo root:  python3 tools/build_es.py
Edit translations in tools/es_translations.py. English pages are the source of truth."""
import os, re, sys
from bs4 import BeautifulSoup, Comment, NavigableString
sys.path.insert(0, os.path.dirname(__file__))
import es_translations as T

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BASE = 'https://emeraldreservepr.com'
PAGES = ['index.html', 'the-project.html', 'smart-living.html', 'contact.html', 'pre-sale.html', '404.html']
INLINE = {'a', 'strong', 'em', 'b', 'i', 'span', 'br', 'sup', 'sub', 'small', 'abbr', 'u'}
PAGE_LINK = re.compile(r'^(index|the-project|smart-living|contact|pre-sale|404)\.html(#.*)?$')
GLOBE = '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg>'


def norm(h): return ' '.join(h.split())
def url_en(p): return BASE + '/' if p == 'index.html' else f'{BASE}/{p}'
def url_es(p): return f'{BASE}/es/' if p == 'index.html' else f'{BASE}/es/{p}'


def add_lang_features_en(html, page):
    """Additive changes to the English page: language bar, stylesheet, hreflang alternates."""
    if 'lang-bar' in html:
        return html
    bar = (f'<div class="lang-bar"><div class="container"><a href="es/{page}" hreflang="es" lang="es">{GLOBE}<span>Leer en español</span></a></div></div>\n\n  ')
    html = html.replace('<body>\n', '<body>\n\n  ' + bar, 1)
    html = html.replace('<link rel="stylesheet" href="css/styles.css">', '<link rel="stylesheet" href="css/styles.css">\n  <link rel="stylesheet" href="css/lang.css">', 1)
    alt = (f'  <link rel="alternate" hreflang="en" href="{url_en(page)}">\n  <link rel="alternate" hreflang="es" href="{url_es(page)}">\n'
           f'  <link rel="alternate" hreflang="x-default" href="{url_en(page)}">\n')
    html = re.sub(r'(  <link rel="canonical"[^\n]*\n)', lambda m: m.group(1) + alt, html, count=1)
    return html


def build_es(html, page):
    soup = BeautifulSoup(html, 'lxml')
    missing = []

    def units():
        out = []
        for el in soup.find_all(True):
            if el.name in ('script', 'style', 'svg', 'path', 'head', 'html', 'body', 'title', 'meta', 'link', 'noscript') or el.find_parent('svg') or el.find_parent('head'):
                continue
            if not el.get_text(strip=True): continue
            if [d for d in el.find_all(True) if d.name not in INLINE and d.name not in ('svg', 'path', 'br', 'img')]: continue
            if el.name in INLINE and el.parent is not None and el.parent.name not in ('html', 'body'):
                if not [d for d in el.parent.find_all(True) if d.name not in INLINE and d.name not in ('svg', 'path', 'br', 'img')]: continue
            out.append(el)
        return out

    for el in units():
        key = norm(el.decode_contents())
        if key in T.KEEP: continue
        if key in T.UNITS:
            frag = BeautifulSoup(T.UNITS[key], 'html.parser')
            el.clear()
            for c in list(frag.contents): el.append(c)
        else:
            missing.append(key)
    # text nodes beside form inputs
    for el in soup.find_all(True):
        if el.name in ('script', 'style', 'svg', 'head', 'title') or el.find_parent('svg') or el.find_parent('head'): continue
        if not [d for d in el.find_all(True) if d.name not in INLINE and d.name not in ('svg', 'path', 'br', 'img')]: continue
        for c in list(el.children):
            if isinstance(c, NavigableString) and not isinstance(c, Comment) and c.strip():
                k = ' '.join(c.split())
                if k in T.TEXT: c.replace_with(c.replace(c.strip(), T.TEXT[k]))
                elif k not in T.KEEP: missing.append(k)
    # attributes
    for el in soup.find_all(True):
        for a in ('alt', 'aria-label', 'placeholder', 'title'):
            if el.get(a):
                if el[a] in T.ATTRS: el[a] = T.ATTRS[el[a]]
                else: missing.append('@' + a + ':' + el[a])
        if el.name == 'input' and el.get('name') == 'interest' and el.get('value') in T.INPUT_VALUES:
            el['value'] = T.INPUT_VALUES[el['value']]
        if el.name == 'meta' and el.get('content') and (el.get('name') in ('description', 'twitter:title') or el.get('property') in ('og:title', 'og:description')):
            if el['content'] in T.META: el['content'] = T.META[el['content']]
            else: missing.append('@meta:' + el['content'])
    t = soup.find('title')
    if t and t.string:
        if t.string.strip() in T.TITLES: t.string = T.TITLES[t.string.strip()]
        else: missing.append('@title:' + t.string)
    # inline script of the map page
    for sc in soup.find_all('script'):
        if sc.string and 'const LOTS' in sc.string:
            code = sc.string
            for old, new in T.SCRIPT:
                if old not in code: missing.append('@script:' + old)
                code = code.replace(old, new)
            sc.string = code
    # language + SEO
    soup.html['lang'] = 'es'
    for l in soup.find_all('link', rel='canonical'): l['href'] = url_es(page)
    for m in soup.find_all('meta', property='og:url'): m['content'] = url_es(page)
    og = soup.find('meta', property='og:url')
    if og:
        loc = soup.new_tag('meta'); loc['property'] = 'og:locale'; loc['content'] = 'es_PR'; og.insert_after(loc)
    # language bar link -> English
    bar = soup.select_one('.lang-bar a')
    bar['href'] = f'../{page}'; bar['hreflang'] = 'en'; bar['lang'] = 'en'
    bar.find('span').string = 'Read in English'
    # paths: everything relative moves up one level, except links between pages
    for el in soup.find_all(True):
        for a in ('href', 'src', 'poster'):
            v = el.get(a)
            if not v: continue
            if v.startswith(('http:', 'https:', '#', 'mailto:', 'tel:', 'data:', '/', '../')): continue
            if el.name == 'a' and PAGE_LINK.match(v): continue
            if el is bar: continue
            el[a] = '../' + v
        st = el.get('style')
        if st and 'url(' in st: el['style'] = re.sub(r"url\((['\"]?)(?!http|data:|\.\./)", lambda m: f"url({m.group(1)}../", st)
    return soup.decode(), missing


def main():
    os.makedirs(os.path.join(ROOT, 'es'), exist_ok=True)
    problems = {}
    for page in PAGES:
        path = os.path.join(ROOT, page)
        html = add_lang_features_en(open(path, encoding='utf-8').read(), page)
        open(path, 'w', encoding='utf-8').write(html)
        out, missing = build_es(html, page)
        open(os.path.join(ROOT, 'es', page), 'w', encoding='utf-8').write(out)
        if missing: problems[page] = missing
    # sitemap
    sm = open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8').read()
    if '/es/' not in sm:
        add = ''.join(f'  <url><loc>{url_es(p)}</loc></url>\n' for p in PAGES if p not in ('pre-sale.html', '404.html'))
        sm = sm.replace('</urlset>', add + '</urlset>')
        open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(sm)
    for p, m in problems.items():
        print('MISSING in', p)
        for x in sorted(set(m)): print('   ', repr(x)[:140])
    print('done; pages with missing translations:', len(problems))


if __name__ == '__main__':
    main()
