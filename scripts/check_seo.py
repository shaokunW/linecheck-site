#!/usr/bin/env python3
"""Validate crawlable pages, canonical URLs, translated links, and local assets."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import json
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://shaokunw.github.io/linecheck-site/'

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links, self.refs, self.ids, self.meta = [], [], set(), {}
        self.h1 = 0
        self.lang = None
        self.title = ''
        self.in_title = False
        self.in_json = False
        self.json_text = ''
        self.structured = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            assert a['id'] not in self.ids, f'Duplicate id: {a["id"]}'
            self.ids.add(a['id'])
        if tag == 'html': self.lang = a.get('lang')
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.in_title = True
        if tag == 'link': self.links.append(a)
        if tag == 'meta': self.meta[a.get('name', a.get('property'))] = a.get('content', '')
        if tag in ('a', 'link') and a.get('href'): self.refs.append(a['href'])
        if tag == 'img':
            assert all(k in a for k in ('alt','width','height')), 'Image needs alt and dimensions'
            self.refs.append(a['src'])
            if a.get('srcset'):
                self.refs.extend(item.strip().split()[0] for item in a['srcset'].split(','))
        if tag == 'script':
            assert a.get('type') == 'application/ld+json', 'Pages should not require executable JavaScript'
            self.in_json = True
            self.json_text = ''

    def handle_data(self, data):
        if self.in_title: self.title += data
        if self.in_json: self.json_text += data

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag == 'script' and self.in_json:
            self.structured.append(json.loads(self.json_text))
            self.in_json = False

    def canonical(self):
        values = [a['href'] for a in self.links if a.get('rel') == 'canonical']
        assert len(values) == 1, 'Exactly one canonical URL required'
        return values[0]

    def alternates(self):
        return {a['hreflang']: a['href'] for a in self.links if a.get('rel') == 'alternate' and 'hreflang' in a}

pages = {}
for file in ROOT.rglob('*.html'):
    rel = file.relative_to(ROOT).as_posix()
    url = BASE + (rel[:-10] if rel.endswith('index.html') else rel)
    pages[url] = Page(file.read_text())

titles, descriptions, crawlable = set(), set(), set()
for url, page in pages.items():
    assert page.lang and page.h1 == 1, f'{url}: needs language and one h1'
    if 'noindex' in page.meta.get('robots', ''):
        assert url == BASE + '404.html'
        continue
    crawlable.add(url)
    assert page.title and page.title not in titles, f'{url}: missing or duplicate title'
    titles.add(page.title)
    desc = page.meta.get('description', '')
    assert desc and desc not in descriptions, f'{url}: missing or duplicate description'
    descriptions.add(desc)
    assert page.canonical() == url, f'{url}: canonical mismatch'
    assert page.meta['og:url'] == url
    assert page.meta['og:title'] == page.title
    assert page.meta['og:description'] == desc
    assert page.meta['twitter:card'] in ('summary', 'summary_large_image')
    if page.meta['twitter:card'] == 'summary_large_image':
        assert int(page.meta['og:image:width']) >= 1200
        assert int(page.meta['og:image:height']) > 0
    assert page.structured and page.structured[0]['url'] == url
    for lang, alt in page.alternates().items():
        assert alt in pages, f'{url}: alternate is missing: {alt}'
        assert pages[alt].alternates() == page.alternates(), f'{url}: nonreciprocal hreflang'
        if lang != 'x-default': assert pages[alt].lang == lang
    for key in ('og:image', 'twitter:image'):
        assert (ROOT / page.meta[key].removeprefix(BASE)).is_file(), f'{url}: missing sharing image'

for url, page in pages.items():
    for ref in page.refs:
        target = urlsplit(urljoin(url, ref))
        if target.scheme not in ('http','https') or target.netloc != urlsplit(BASE).netloc:
            continue
        absolute = target._replace(query='', fragment='').geturl()
        assert absolute.startswith(BASE), f'{url}: link escapes project path: {ref}'
        path = ROOT / unquote(absolute.removeprefix(BASE))
        if path.is_dir(): path /= 'index.html'
        assert path.is_file(), f'{url}: missing local target {ref}'
        if target.fragment:
            assert absolute in pages and unquote(target.fragment) in pages[absolute].ids, f'{url}: missing fragment {ref}'

ns = {'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls = [el.text for el in ET.parse(ROOT/'sitemap.xml').findall('s:url/s:loc', ns)]
assert len(urls) == len(set(urls)), 'Duplicate sitemap URLs'
assert set(urls) == crawlable, 'Sitemap must match canonical, indexable pages'
assert 'noindex' in pages[BASE+'404.html'].meta['robots']
print(f'PASS: {len(crawlable)} indexable pages; sitemap, metadata, JSON-LD, hreflang, local links and fragments, image sizes, and noindex 404.')
