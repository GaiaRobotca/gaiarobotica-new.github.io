"""Check static files before publication, using Python 3 standard library only.

Checks exact filename case, local HTML/CSS references, anchors, duplicate IDs,
image descriptions and primary landmarks. External URLs and runtime JavaScript
are intentionally checked separately with a browser.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from collections import Counter
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.refs, self.errors = path, [], [], []
        self.h1 = self.main = 0
        self.redirect = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        self.h1 += tag == 'h1'
        self.main += tag == 'main'
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
            self.redirect = True
        if tag == 'img' and 'alt' not in attrs:
            self.errors.append('Image without alt: ' + attrs.get('src', ''))
        for name in ['src', 'href', 'poster']:
            if name in attrs:
                self.refs.append(attrs[name])
        if 'srcset' in attrs:
            self.refs.extend(v.strip().split()[0] for v in attrs['srcset'].split(','))
        if 'style' in attrs:
            self.refs.extend(css_urls(attrs['style']))


def css_urls(text):
    return re.findall(r'url\(\s*[\"\x27]?([^\"\x27)]+)', text)


def exact_exists(path):
    try:
        parts = path.relative_to(ROOT).parts
    except ValueError:
        return False
    current = ROOT
    for part in parts:
        if not current.is_dir() or part not in {entry.name for entry in current.iterdir()}:
            return False
        current = current / part
    return current.exists()


def main():
    documents = {}
    errors = []
    files = [p for p in ROOT.rglob('*.html') if '.git' not in p.parts]
    for path in files:
        doc = Document(path)
        try:
            doc.feed(path.read_text(encoding='utf-8'))
        except UnicodeError:
            errors.append(f'{path.relative_to(ROOT)}: not valid UTF-8')
            continue
        documents[path.resolve()] = doc
        errors.extend(f'{path.relative_to(ROOT)}: {e}' for e in doc.errors)
        if not doc.redirect and (doc.h1 != 1 or doc.main != 1):
            errors.append(f'{path.relative_to(ROOT)}: expected one h1/main, found {doc.h1}/{doc.main}')
        for value, count in Counter(doc.ids).items():
            if count > 1:
                errors.append(f'{path.relative_to(ROOT)}: duplicate id {value}')
    references = [(p, value) for p, doc in documents.items() for value in doc.refs]
    for path in (ROOT / 'assets').rglob('*.css'):
        references.extend((path, value) for value in css_urls(path.read_text(encoding='utf-8')))
    for origin, value in references:
        if value in ['', '#']:
            errors.append(f'{origin.relative_to(ROOT)}: empty link {value!r}')
            continue
        url = urlsplit(value)
        if url.scheme or url.netloc:
            continue
        target = (origin.parent / unquote(url.path)).resolve() if url.path else origin
        if target.is_dir():
            target = target / 'index.html'
        if not exact_exists(target):
            errors.append(f'{origin.relative_to(ROOT)}: missing file or incorrect case: {value}')
        elif url.fragment and target.suffix == '.html':
            doc = documents.get(target)
            if doc and unquote(url.fragment) not in doc.ids and not doc.redirect:
                errors.append(f'{origin.relative_to(ROOT)}: missing anchor: {value}')
    for error in sorted(set(errors)):
        print('ERROR:', error)
    print(f'{len(documents)} HTML files; {len(references)} references; {len(set(errors))} errors.')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
