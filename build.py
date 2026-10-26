#!/usr/bin/env python3
"""Build real HTML pages with the Python standard library; no network or packages."""
import argparse
import hashlib
import html
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree.ElementTree import Element, SubElement, tostring

ROOT = Path(__file__).resolve().parent
VOID = set('area base br col embed hr img input link meta param source track wbr'.split())
BIND = re.compile(r'{{\s*([\w.]+)\s*}}')


class Node:
    def __init__(self, tag='', attrs=(), text=''):
        self.tag, self.attrs, self.text, self.children = tag, dict(attrs), text, []


class Template(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = Node('root')
        self.stack = [self.root]
        self.feed(source)
        if len(self.stack) != 1:
            raise ValueError('Unclosed template element')

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.stack[-1].tag != tag:
            raise ValueError(f'Mismatched template element: {tag}')
        self.stack.pop()

    def handle_data(self, data):
        self.stack[-1].children.append(Node(text=data))


def resolve(key, data):
    if key in ('true', 'false'):
        return key == 'true'
    value = data
    for part in key.split('.'):
        value = value[part]
    return value


def interpolate(value, data):
    parts, start = [], 0
    for match in BIND.finditer(value):
        parts.append(html.escape(value[start:match.start()], quote=False))
        item = resolve(match[1], data)
        parts.append(item['$html'] if isinstance(item, dict) and '$html' in item
                     else html.escape(str(item), quote=False))
        start = match.end()
    return ''.join(parts) + html.escape(value[start:], quote=False)


class Renderer:
    def __init__(self, prefix):
        self.prefix, self.rules = prefix, {}

    def local_url(self, value):
        if value == '#main':
            return value
        if value.startswith('#'):
            return self.prefix + '/' + (value if value != '#top' else '')
        if value.startswith('/') and not value.startswith('//'):
            return self.prefix + value
        return value

    def css_class(self, style, pseudo=''):
        key = style, pseudo
        if key not in self.rules:
            self.rules[key] = 'v-' + hashlib.sha256((style + pseudo).encode()).hexdigest()[:12]
        return self.rules[key]

    def render(self, node, data):
        if not node.tag:
            return interpolate(node.text, data)
        children = lambda ctx: ''.join(self.render(n, ctx) for n in node.children)
        if node.tag == 'root':
            return children(data)
        if node.tag == 'sc-if':
            key = BIND.fullmatch(node.attrs['value'])[1]
            return children(data) if resolve(key, data) else ''
        if node.tag == 'sc-for':
            key = BIND.fullmatch(node.attrs['list'])[1]
            return ''.join(children(dict(data, **{node.attrs['as']: item})) for item in resolve(key, data))
        attrs, classes = [], []
        for key, raw in node.attrs.items():
            if key == 'ref' or key.startswith(('on', 'hint-', 'data-dc')):
                continue
            value = html.unescape(interpolate(raw, data)) if raw is not None else None
            if key == 'class':
                classes.append(value)
            elif key in ('style', 'style-hover', 'style-focus'):
                pseudo = {'style': '', 'style-hover': ':hover', 'style-focus': ':focus'}[key]
                classes.append(self.css_class(value, pseudo))
            else:
                if key in ('href', 'src') and value:
                    value = self.local_url(value)
                attrs.append(' ' + key + ('' if value is None else '="' + html.escape(value, quote=True) + '"'))
        if classes:
            attrs.append(' class="' + html.escape(' '.join(classes), quote=True) + '"')
        opening = '<' + node.tag + ''.join(attrs) + '>'
        return opening if node.tag in VOID else opening + children(data) + '</' + node.tag + '>'

    def stylesheet(self):
        return '\n'.join('.' + name + pseudo + '{' + style + '}'
                         for (style, pseudo), name in self.rules.items())


def site_config(site_url, production, base_path=''):
    if production and not site_url:
        raise ValueError('Production requires --site-url with the actual public HTTPS URL')
    origin = ''
    prefix = base_path.rstrip('/')
    if site_url:
        url = urlsplit(site_url)
        if (url.scheme != 'https' or not url.hostname or url.username or url.password
                or url.query or url.fragment or url.port or re.search(r'\s', site_url)):
            raise ValueError('Use a public HTTPS URL without credentials, port, query, or fragment')
        prefix = url.path.rstrip('/')
        origin = f'https://{url.netloc}' + prefix
        if base_path and base_path.rstrip('/') != prefix:
            raise ValueError('--base-path must match the path in --site-url')
    if prefix and (not re.fullmatch(r'/[A-Za-z0-9_./-]+', prefix)
                   or any(s in ('', '.', '..') for s in prefix[1:].split('/'))):
        raise ValueError('Invalid base path')
    return origin, prefix


def head(title, description, route, origin, prefix, production, not_found):
    esc = html.escape
    canonical = origin + route if origin and not not_found else ''
    image = (origin or prefix) + '/assets/social-card.png'
    robots = 'index, follow' if production and not not_found else 'noindex, nofollow'
    csp = "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'none'; base-uri 'none'; form-action 'none'; object-src 'none'"
    lines = ['<!doctype html>', '<html lang="en">', '<head>', '<meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             f'<meta http-equiv="Content-Security-Policy" content="{esc(csp, quote=True)}">',
             '<meta name="referrer" content="strict-origin-when-cross-origin">',
             '<meta name="theme-color" content="#080C12">',
             f'<title>{esc(title)}</title>', f'<meta name="description" content="{esc(description, quote=True)}">',
             f'<meta name="robots" content="{robots}">',
             '<meta property="og:type" content="website">', '<meta property="og:site_name" content="vrt">',
             f'<meta property="og:title" content="{esc(title, quote=True)}">',
             f'<meta property="og:description" content="{esc(description, quote=True)}">',
             f'<meta property="og:image" content="{esc(image, quote=True)}">',
             '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
             '<meta property="og:image:alt" content="vrt — code, traces, and no guesswork">',
             '<meta name="twitter:card" content="summary_large_image">',
             f'<meta name="twitter:image" content="{esc(image, quote=True)}">',
             f'<link rel="icon" href="{prefix}/assets/favicon.svg" type="image/svg+xml">',
             f'<link rel="alternate icon" href="{prefix}/assets/favicon.ico">',
             f'<link rel="stylesheet" href="{prefix}/assets/site.css">',
             f'<link rel="preload" href="{prefix}/assets/fonts/ibm-plex-sans-latin.woff2" as="font" type="font/woff2" crossorigin>',
             f'<script src="{prefix}/assets/site.js" defer></script>']
    if canonical:
        lines += [f'<link rel="canonical" href="{esc(canonical, quote=True)}">',
                  f'<meta property="og:url" content="{esc(canonical, quote=True)}">']
    return '\n'.join(lines) + '\n</head>\n<body>\n'


def build(output, site_url=None, production=False, base_path=''):
    origin, prefix = site_config(site_url, production, base_path)
    if output.resolve() == ROOT or output.resolve() in (ROOT / 'src', ROOT / 'assets'):
        raise ValueError('Output must be a separate generated directory')
    data = json.loads((ROOT / 'src/content.json').read_text())
    body = (ROOT / 'src/body.html').read_text().replace('{{ siteHeader }}', (ROOT / 'src/header.html').read_text())
    template = Template(body).root
    renderer = Renderer(prefix)
    cases = data['cases']
    pages = [('/', 'index.html', 'home', None), ('/404.html', '404.html', '404', None)]
    pages += [(f'/work/{c["slug"]}/', f'work/{c["slug"]}/index.html', 'case', i) for i, c in enumerate(cases)]
    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / 'assets', output / 'assets', dirs_exist_ok=True)
    for route, file, view, index in pages:
        ctx = dict(data, isHome=view == 'home', isCase=view == 'case', is404=view == '404', caseCount=f'{len(cases):02d}')
        title = 'vrt — Under the hood. No guesswork.'
        description = 'I’m vrt — an ethical hacker with 18+ years of finding bugs in websites, web services, mobile apps, and the stuff under the hood.'
        if index is not None:
            ctx.update(cs=cases[index], prev=cases[(index-1) % len(cases)], next=cases[(index+1) % len(cases)])
            title, description = cases[index]['title'] + ' — vrt', cases[index]['summary']
        elif view == '404':
            title, description = 'Wrong turn — vrt', 'That link took a wrong turn. Head back to home base or dig into a case.'
        result = head(title, description, route, origin, prefix, production, view == '404') + renderer.render(template, ctx) + '\n</body>\n</html>\n'
        if '{{' in result or '<sc-' in result or '<x-dc' in result:
            raise ValueError(f'Unresolved template in {file}')
        destination = output / file
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(result)
    css = (ROOT / 'src/base.css').read_text() + '\n' + renderer.stylesheet() + '\n' + (ROOT / 'src/enhancements.css').read_text()
    (output / 'assets/site.css').write_text(css)
    (output / '.nojekyll').write_text('')
    robots = 'User-agent: *\n' + ('Allow: /\n' if production else 'Disallow: /\n')
    if origin:
        robots += 'Sitemap: ' + origin + '/sitemap.xml\n'
    (output / 'robots.txt').write_text(robots)
    sitemap = Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    if origin:
        for route, _, view, _ in pages:
            if view != '404':
                SubElement(SubElement(sitemap, 'url'), 'loc').text = origin + route
    (output / 'sitemap.xml').write_bytes(tostring(sitemap, encoding='utf-8', xml_declaration=True))
    # GitHub Pages does not apply this optional portability file. CSP/referrer policy are also in HTML.
    (output / '_headers').write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: DENY\n  Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'none'; base-uri 'none'; form-action 'none'; object-src 'none'; frame-ancestors 'none'\n")
    manifest = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'build-manifest.json'}
    (output / 'build-manifest.json').write_text(json.dumps({'mode': 'production' if production else 'preview', 'site_url': origin or None, 'base_path': prefix, 'sha256': manifest}, indent=2) + '\n')
    return len(pages)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    parser.add_argument('--site-url', help='Actual HTTPS site URL, including a GitHub project subpath if needed')
    parser.add_argument('--base-path', default='', help='Optional subpath for local previews, e.g. /portfolio')
    parser.add_argument('--production', action='store_true', help='Enable indexing; requires --site-url')
    args = parser.parse_args()
    try:
        count = build(args.output, args.site_url, args.production, args.base_path)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(f'Built {count} static HTML pages in {args.output} ({"production" if args.production else "preview"})')


if __name__ == '__main__':
    main()
