"""Render the shared header, footer, member list, metadata and legacy redirects.

Uses Python 3 standard library only. Run after editing data/team.json, data/site.json
or this template. Published pages are complete HTML and need no build service.
"""
from pathlib import Path
from html import escape
import json
import os
import re

ROOT = Path(__file__).resolve().parents[1]


def relative(target, current):
    return os.path.relpath(ROOT / target, (ROOT / current).parent).replace('\\', '/')


def replace_region(text, name, content):
    pattern = r'<!--\s*' + re.escape(name) + r':start\s*-->.*?<!--\s*' + re.escape(name) + r':end\s*-->'
    updated, count = re.subn(pattern, lambda _: f'<!-- {name}:start -->\n{content}\n<!-- {name}:end -->', text, flags=re.S)
    if count != 1:
        raise ValueError(f'Expected exactly one {name} region, got {count}')
    return updated


def main():
    site = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
    team = json.loads((ROOT / 'data/team.json').read_text(encoding='utf-8'))
    base = site['base_url'].rstrip('/') + '/'
    for page in site['pages']:
        path = page['path']
        r = lambda target: relative(target, path)
        brand = f'''<a class="site-brand" href="{r('index.html')}" aria-label="GAIA Robótica — início"><img src="{r('assets/images/marca/favicon-verde.png')}" alt="" width="36" height="36"><span>GAIA<small>ROBÓTICA · UFTM</small></span></a>'''
        links = []
        for label, target in [('Sobre', 'index.html#sobre'), ('Projetos', 'index.html#robos'), ('Conquistas', 'index.html#conquistas'), ('Equipe', 'index.html#equipe'), ('Aprenda', 'paginas/aprenda.html'), ('Apoie', 'paginas/patrocine.html'), ('Contato', 'paginas/contato.html')]:
            active = ' aria-current="page"' if path == target or (label == 'Aprenda' and path.startswith('artigos/')) or (label == 'Conquistas' and path.startswith('conquistas/')) else ''
            css = ' class="site-contact"' if label == 'Contato' else ''
            target_path, _, anchor = target.partition('#')
            href = r(target_path) + ('#' + anchor if anchor else '')
            links.append(f'<li><a href="{href}"{css}{active}>{label}</a></li>')
        header = f'''<a class="skip-link" href="#main-content">Pular para o conteúdo</a>
<header class="site-header"><nav class="site-nav" aria-label="Navegação principal">
{brand}
<button class="site-menu-toggle" type="button" aria-label="Abrir menu" aria-expanded="false" aria-controls="site-menu">☰</button>
<ul class="site-links" id="site-menu">{''.join(links)}</ul>
</nav></header>
<noscript><link rel="stylesheet" href="{r('assets/css/no-script.css')}"></noscript>'''
        footer = f'''<footer class="site-footer"><div class="site-footer-inner"><div>{brand}<p class="footer-description">Robótica, drones e extensão universitária.<br>Universidade Federal do Triângulo Mineiro · Uberaba, MG</p></div><div class="site-footer-links" aria-label="Links do rodapé"><a href="{r('paginas/aprenda.html')}">Aprenda</a><a href="{r('paginas/patrocine.html')}">Apoie o projeto</a><a href="{r('paginas/contato.html')}">Contato</a><a href="https://www.instagram.com/gaia.robotica/" target="_blank" rel="noopener noreferrer">Instagram ↗</a><a href="https://github.com/GaiaRobotca/gaiarobotica-new.github.io" target="_blank" rel="noopener noreferrer">GitHub ↗</a><a href="{r('paginas/portal.html')}">Todos os links</a></div></div><p class="site-footer-note">GAIA · Desde 2023 · Conhecimento que vira projeto.</p></footer>'''
        title, desc = escape(page['title'], quote=True), escape(page['description'], quote=True)
        url = escape(base + path, quote=True)
        meta = f'''<meta name="description" content="{desc}">
<meta name="theme-color" content="#050f26">
<link rel="canonical" href="{url}">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="GAIA Robótica — UFTM">
<meta property="og:type" content="{'article' if path.startswith(('artigos/', 'noticias/', 'conquistas/')) else 'website'}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{base}assets/images/social/gaia-equipe.jpg">
<meta property="og:image:alt" content="Equipe GAIA Robótica na SAE Brasil EletroQuad">
<meta name="twitter:card" content="summary_large_image">'''
        text = (ROOT / path).read_text(encoding='utf-8')
        text = replace_region(text, 'shared-header', header)
        text = replace_region(text, 'shared-footer', footer)
        text = replace_region(text, 'page-meta', meta)
        if path == 'index.html':
            cards = []
            for member in team['members']:
                if member['status'] != 'active':
                    continue
                name = escape(member['name'])
                if member.get('photo'):
                    photo = f'<img class="ms-avatar" src="{escape(member["photo"], quote=True)}" alt="{name}" width="100" height="100" loading="lazy" decoding="async">'
                else:
                    initials = ''.join(word[0] for word in member['name'].split()[:2])
                    photo = f'<span class="ms-avatar avatar-placeholder" aria-hidden="true">{escape(initials)}</span>'
                cards.append(f'<div class="member-card">{photo}<div class="ms-name">{name}</div><div class="ms-role">{escape(member["role"])}</div></div>')
            text = replace_region(text, 'team-members', '<div class="members-grid">\n' + '\n'.join(cards) + '\n</div>')
        (ROOT / path).write_text(text, encoding='utf-8')
        if page['legacy'] != path:
            target = path
            redirect = f'''<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><meta http-equiv="refresh" content="1; url={target}"><link rel="canonical" href="{url}"><meta name="robots" content="noindex"><script src="assets/js/redirect.js" defer></script></head><body><p>Esta página mudou de endereço. <a id="redirect-target" href="{target}">Continuar para {title}</a>.</p></body></html>
'''
            (ROOT / page['legacy']).write_text(redirect, encoding='utf-8')
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '\n'.join('  <url><loc>' + escape(base + page['path']) + '</loc></url>' for page in site['pages'])
    (ROOT / 'sitemap.xml').write_text(sitemap + '\n</urlset>\n', encoding='utf-8')
    (ROOT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n', encoding='utf-8')
    print(f'Synchronized {len(site["pages"])} pages, metadata and legacy redirects.')


if __name__ == '__main__':
    main()
