"""Browser regression checks. Requires Playwright + Chromium and a local HTTP server.

Usage: python scripts/check_browser.py [http://127.0.0.1:8765/]
Screenshots and the report go to the system temporary directory, outside the site.
No contact message is sent: clipboard behavior is stubbed for the form checks.
"""
from pathlib import Path
import json
import os
import sys
import tempfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765/'
OUTPUT = Path(tempfile.gettempdir()) / 'gaia-browser-review'
OUTPUT.mkdir(exist_ok=True)


def main():
    site = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
    failures, checks = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 960})
        current = {'path': ''}
        page.on('pageerror', lambda error: failures.append(f'{current["path"]}: JS: {error}'))
        page.on('response', lambda response: failures.append(f'{current["path"]}: HTTP {response.status} {response.url}') if response.url.startswith(BASE) and response.status >= 400 else None)
        for width in ([] if os.environ.get('GAIA_INTERACTIONS_ONLY') else [1440, 768, 390, 320]):
            page.set_viewport_size({'width': width, 'height': 900})
            for record in site['pages']:
                path = record['path']
                current['path'] = f'{path}@{width}'
                page.goto(BASE + path, wait_until='networkidle')
                # Load lazy images too, without scrolling through every lengthy tutorial.
                broken = page.evaluate('''async () => {
                  const images = [...document.images];
                  images.forEach(img => img.loading = 'eager');
                  await Promise.all(images.map(img => img.decode().catch(() => {})));
                  return images.filter(img => !img.naturalWidth).map(img => img.getAttribute('src'));
                }''')
                if broken:
                    failures.append(f'{current["path"]}: broken images: {broken}')
                overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
                if overflow:
                    failures.append(f'{current["path"]}: horizontal overflow')
                if page.locator('h1').count() != 1 or page.locator('main').count() != 1:
                    failures.append(f'{current["path"]}: heading/main landmark')
                if path in ['index.html', 'paginas/ex-membros.html']:
                    distorted = page.locator('.leader-avatar, .docente-avatar, .ms-avatar, .founder-avatar, .ex-avatar').evaluate_all('''avatars => avatars.flatMap(avatar => {
                      const box = avatar.getBoundingClientRect();
                      const style = getComputedStyle(avatar);
                      return Math.abs(box.width - box.height) > 1 || style.borderRadius !== '50%'
                        ? [{name: avatar.alt || avatar.textContent.trim(), width: box.width, height: box.height}]
                        : [];
                    })''')
                    if distorted:
                        failures.append(f'{current["path"]}: noncircular avatars: {distorted}')
                if width == 390:
                    toggle = page.locator('.site-menu-toggle')
                    toggle.click()
                    if toggle.get_attribute('aria-expanded') != 'true' or not page.locator('.site-links').is_visible():
                        failures.append(f'{current["path"]}: menu did not open')
                    page.keyboard.press('Escape')
                    if toggle.get_attribute('aria-expanded') != 'false':
                        failures.append(f'{current["path"]}: Escape did not close menu')
                if width in [390, 1440] and path in ['index.html', 'paginas/aprenda.html', 'paginas/contato.html', 'paginas/portal.html', 'artigos/seguidor-linha.html', 'noticias/fundacao.html']:
                    page.screenshot(path=str(OUTPUT / (path.replace('/', '-') + f'-{width}.png')), full_page=False)
                checks.append(current['path'])
            print(f'Checked 22 pages at {width}px', flush=True)

        print(f'Layout/image/script failures: {len(failures)}', failures, flush=True)
        page.set_viewport_size({'width': 1440, 'height': 960})
        page.goto(BASE + 'paginas/aprenda.html', wait_until='networkidle')
        search = page.locator('#article-search')
        search.fill('naoexistegaia')
        assert page.locator('.learn-card:visible').count() == 0, 'Search empty state failed'
        search.fill('arduino')
        assert page.locator('.learn-card:visible').count() >= 1, 'Arduino search failed'
        search.fill('visao')
        assert page.locator('.learn-card:visible').count() >= 1, 'Accent-insensitive search failed'
        search.fill('')
        assert page.locator('.learn-card:visible').count() == 7, 'Search reset failed'
        for category, count in [('arduino', 2), ('ia', 2), ('robotica', 2), ('drones', 1), ('eletronica', 2)]:
            page.locator(f'[data-filter="{category}"]').click()
            assert page.locator('.learn-card:visible').count() == count, category + ' category filter'
        page.locator('[data-filter="todos"]').click()
        checks.append('Aprenda search / accents / empty state / reset')

        for path in ['paginas/contato.html', 'paginas/patrocine.html']:
            page.goto(BASE + path, wait_until='networkidle')
            page.evaluate("Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {writeText: async text => { window.__copied = text; }}})")
            form = page.locator('[data-email-form]')
            form.locator('[name="Nome"]').fill('Teste de qualidade')
            form.locator('[name="Email"]').fill('teste@example.com')
            if form.locator('[name="Assunto"]').count():
                form.locator('[name="Assunto"]').fill('Teste local do formulário')
            form.locator('[name="Mensagem"]').fill('Mensagem de teste local. Nada foi enviado.')
            select = form.locator('select')
            if select.count():
                options = select.locator('option').evaluate_all('(options) => options.map(o => o.value).filter(Boolean)')
                select.select_option(options[0])
            form.locator('[data-copy-message]').click()
            assert 'Teste de qualidade' in page.evaluate('window.__copied || ""'), path + ' copy draft failed'
            page.evaluate("() => { navigator.clipboard.writeText = async () => { throw new Error('Clipboard denied for test'); }; }")
            form.locator('[data-copy-message]').click()
            assert form.locator('[data-email-preview]').is_visible(), path + ' clipboard fallback failed'
            checks.append(path + ' local draft / copy')

        for path in ['conquistas/sae.html', 'conquistas/escolas.html']:
            page.goto(BASE + path, wait_until='networkidle')
            page.locator('.carousel-btn.next').click()
            assert '-100%' in page.locator('.carousel-track').get_attribute('style'), path + ' gallery next'
            page.locator('.carousel-btn.prev').click()
            assert '0%' in page.locator('.carousel-track').get_attribute('style'), path + ' gallery previous'
            checks.append(path + ' gallery controls')

        page.goto(BASE + 'artigo-seguidor-linha.html?origem=teste#programacao', wait_until='networkidle')
        assert '/artigos/seguidor-linha.html?origem=teste#programacao' in page.url, 'Legacy redirect lost query/anchor'
        checks.append('Legacy redirect preserves query and fragment')
        browser.close()

    report = {'checks': checks, 'failures': failures}
    (OUTPUT / 'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'{len(checks)} checks, {len(failures)} failures. Report: {OUTPUT}')
    for failure in failures:
        print('ERROR:', failure)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
