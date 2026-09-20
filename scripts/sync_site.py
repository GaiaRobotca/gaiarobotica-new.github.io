"""Render the shared header, footer, member list, metadata and legacy redirects.

Uses Python 3 standard library only. Run after editing data/team.json, data/site.json
or this template. Published pages are complete HTML and need no build service.
"""
from pathlib import Path
from html import escape
import json
import os
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]


def relative(target, current):
    return os.path.relpath(ROOT / target, (ROOT / current).parent).replace('\\', '/')


def replace_region(text, name, content):
    pattern = r'<!--\s*' + re.escape(name) + r':start\s*-->.*?<!--\s*' + re.escape(name) + r':end\s*-->'
    updated, count = re.subn(pattern, lambda _: f'<!-- {name}:start -->\n{content}\n<!-- {name}:end -->', text, flags=re.S)
    if count != 1:
        raise ValueError(f'Expected exactly one {name} region, got {count}')
    return updated


def render_member(member, current, former=False):
    name = escape(member['name'])
    avatar_class = 'ex-avatar' if former else 'ms-avatar'
    size = 80 if former else 88
    if member.get('photo'):
        src = escape(relative(member['photo'], current), quote=True)
        photo = f'<img class="{avatar_class}" src="{src}" alt="{name}" width="{size}" height="{size}" loading="lazy" decoding="async">'
    else:
        initials = ''.join(word[0] for word in member['name'].split()[:2])
        photo = f'<span class="{avatar_class} avatar-placeholder" aria-hidden="true">{escape(initials)}</span>'
    if former:
        period = f'<div class="ex-years">{escape(member["period"])}</div>' if member.get('period') else ''
        return f'<div class="exmembros-card">{photo}<div class="ex-name">{name}</div><div class="ex-role">Ex-integrante</div>{period}</div>'
    return f'<div class="member-card">{photo}<div class="ms-name">{name}</div><div class="ms-role">{escape(member["role"])}</div></div>'


def member_sort_key(member):
    normalized = unicodedata.normalize('NFD', member['name'].casefold())
    return ''.join(character for character in normalized if not unicodedata.combining(character))


def main():
    site = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
    team = json.loads((ROOT / 'data/team.json').read_text(encoding='utf-8'))
    members = sorted(team['members'], key=member_sort_key)
    base = site['base_url'].rstrip('/') + '/'
    contributor_links = ', '.join(f'<a href="{escape(person["url"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(person["name"])}</a>' for person in site.get('contributors', []))
    credit = f'<span class="site-credit">Colaboração e desenvolvimento do site: {contributor_links}.</span>' if contributor_links else ''
    for page in site['pages']:
        path = page['path']
        r = lambda target: relative(target, path)
        brand = f'''<a class="site-brand" href="{r('index.html')}" aria-label="Projeto GAIA — início"><img src="{r('assets/images/marca/gaia-g.svg')}" alt="" width="44" height="44"><span>GAIA<small>PROJETO · UFTM</small></span></a>'''
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
        footer = f'''<footer class="site-footer"><div class="site-footer-inner"><div>{brand}<p class="footer-description">Projeto GAIA · Robótica e Eletroquad.<br>Universidade Federal do Triângulo Mineiro · Uberaba, MG</p></div><div class="site-footer-links" aria-label="Links do rodapé"><a href="{r('paginas/aprenda.html')}">Aprenda</a><a href="{r('paginas/patrocine.html')}">Apoie o projeto</a><a href="{r('paginas/contato.html')}">Contato</a><a href="https://www.instagram.com/gaia.robotica/" target="_blank" rel="noopener noreferrer">Instagram ↗</a><a href="https://github.com/GaiaRobotca/gaiarobotica-new.github.io" target="_blank" rel="noopener noreferrer">GitHub ↗</a><a href="{r('paginas/portal.html')}">Todos os links</a></div></div><p class="site-footer-note">GAIA · Desde 2023 · Conhecimento que vira projeto.</p></footer>'''
        footer = footer.replace('Conhecimento que vira projeto.</p>', f'Conhecimento que vira projeto.{credit}</p>')
        title, desc = escape(page['title'], quote=True), escape(page['description'], quote=True)
        url = escape(base + path, quote=True)
        img_rel = page.get('image', 'assets/images/social/projeto-gaia-hd.png')
        img_alt = escape(page.get('image_alt', 'Símbolo G verde e nome GAIA branco sobre fundo azul-escuro.'), quote=True)
        img_url = escape(base + img_rel, quote=True)
        twitter_img_rel = page.get('twitter_image', page.get('image', 'assets/images/social/projeto-gaia-horizontal-hd.png'))
        twitter_img_url = escape(base + twitter_img_rel, quote=True)
        meta = f'''<meta name="description" content="{desc}">
<meta name="theme-color" content="#050f26">
<link rel="canonical" href="{url}">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Projeto GAIA — UFTM">
<meta property="og:type" content="{'article' if path.startswith(('artigos/', 'noticias/', 'conquistas/')) else 'website'}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img_url}">
<meta property="og:image:alt" content="{img_alt}">
<meta property="og:image:width" content="2400">
<meta property="og:image:height" content="2400">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{twitter_img_url}">
<meta name="twitter:image:alt" content="{img_alt}">'''
        text = (ROOT / path).read_text(encoding='utf-8')
        text = replace_region(text, 'shared-header', header)
        text = replace_region(text, 'shared-footer', footer)
        text = replace_region(text, 'page-meta', meta)
        if path == 'index.html':
            cards = [render_member(member, path) for member in members if member['status'] == 'active']
            text = replace_region(text, 'team-members', '<div class="members-grid">\n' + '\n'.join(cards) + '\n</div>')
        elif path == 'paginas/ex-membros.html':
            cards = [render_member(member, path, former=True) for member in members if member['status'] == 'former']
            text = replace_region(text, 'former-members', '<div class="exmembros-grid">\n' + '\n'.join(cards) + '\n</div>')
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
