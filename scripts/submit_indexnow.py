#!/usr/bin/env python3
"""Submit this deployed project's sitemap URLs to IndexNow (not Google)."""
import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://shaokunw.github.io/linecheck-site/'
ENDPOINT = 'https://api.indexnow.org/indexnow'

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--submit', action='store_true', help='Verify deployed key and sitemap, then notify IndexNow; otherwise print a dry run.')
    args = parser.parse_args()
    key = (ROOT/'indexnow-key.txt').read_text().strip()
    if not (8 <= len(key) <= 128 and all(c in '0123456789abcdef' for c in key)):
        raise ValueError('Invalid IndexNow key')
    ns = {'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    local_sitemap = (ROOT/'sitemap.xml').read_bytes()
    urls = [el.text for el in ET.fromstring(local_sitemap).findall('s:url/s:loc', ns)]
    if not urls or len(urls) > 10000 or any(not url.startswith(BASE) for url in urls):
        raise ValueError('Submit only canonical URLs in this project path')
    payload = {'host':urlsplit(BASE).netloc, 'key':key, 'keyLocation':BASE+'indexnow-key.txt', 'urlList':urls}
    if not args.submit:
        print(f'Dry run: {len(urls)} URLs to {ENDPOINT}; no request sent.')
        for url in urls: print(url)
        return
    with urlopen(payload['keyLocation'], timeout=30) as response:
        if response.read().decode().strip() != key:
            raise ValueError('Published verification key does not match; finish deployment first')
    with urlopen(BASE+'sitemap.xml', timeout=30) as response:
        if response.read() != local_sitemap:
            raise ValueError('Published sitemap does not match; finish deployment first')
    request = Request(ENDPOINT, data=json.dumps(payload).encode(), headers={'Content-Type':'application/json; charset=utf-8'}, method='POST')
    with urlopen(request, timeout=30) as response:
        if response.status == 200:
            print(f'HTTP 200: IndexNow received {len(urls)} URLs. This is not proof of indexing or a Google submission.')
        elif response.status == 202:
            print(f'HTTP 202: IndexNow received {len(urls)} URLs; key validation is pending. This is not proof of indexing or a Google submission.')
        else:
            raise ValueError(f'Unexpected IndexNow status: {response.status}')

if __name__ == '__main__':
    try:
        main()
    except (HTTPError, URLError, ValueError) as error:
        raise SystemExit(f'IndexNow submission failed: {error}')
