"""Run Chromium + axe checks; see docs/visual-identity.md for setup and limits."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from playwright.sync_api import sync_playwright
import json
import argparse
import tempfile

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Brand accessibility, prefix hosting and shop regression checks')
parser.add_argument('--axe-script',type=Path,required=True,help='Path to axe-core/axe.min.js')
parser.add_argument('--output',type=Path,default=Path(tempfile.gettempdir())/'gaia-brand-review')
args=parser.parse_args()
OUTPUT=args.output
OUTPUT.mkdir(parents=True,exist_ok=True)
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_GET(self):
        if not self.path.startswith('/gaiarobotica-new.github.io/'):
            self.send_error(404);return
        self.path=self.path.removeprefix('/gaiarobotica-new.github.io')
        super().do_GET()
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/gaiarobotica-new.github.io/'
results={'axe':[],'layout':[],'requests':[],'shop':[]}
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(reduced_motion='reduce')
    page.on('response',lambda r:results['requests'].append({'url':r.url,'status':r.status}) if r.url.startswith(base) and r.status>=400 else None)
    paths=[x['path'] for x in json.loads((ROOT/'data/site.json').read_text(encoding='utf-8'))['pages']]+['loja/index.html']
    for path in paths:
        for theme in (['dark','light'] if path.startswith('loja') else ['dark']):
            page.set_viewport_size({'width':1440,'height':960})
            page.goto(base+path,wait_until='networkidle')
            if path.startswith('loja'):page.evaluate('(t)=>document.documentElement.dataset.theme=t',theme)
            page.add_script_tag(path=str(args.axe_script))
            audit=page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}});return r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}));}''')
            results['axe'].append({'path':path,'theme':theme,'violations':audit})
            for width in [320,390,768,1440]:
                page.set_viewport_size({'width':width,'height':960})
                results['layout'].append({'path':path,'theme':theme,'width':width,'overflow':page.evaluate('document.documentElement.scrollWidth>innerWidth+1')})
        print(path,flush=True)
    page.goto(base+'loja/index.html',wait_until='networkidle')
    page.set_viewport_size({'width':390,'height':960})
    initial=page.locator('html').get_attribute('data-theme')
    page.locator('#theme-toggle').click();page.reload()
    assert page.locator('html').get_attribute('data-theme')!=initial
    results['shop'].append('Theme toggle and persistence')
    page.locator('[data-filter="adesivo"]').click()
    assert page.locator('.product-card').count()==1
    page.locator('[data-add="adesivo"]').click()
    assert page.locator('#cart-dialog').is_visible()
    page.locator('[data-qty="adesivo"][data-delta="1"]').click()
    assert page.locator('#cart-count').inner_text()=='2'
    page.keyboard.press('Escape');page.reload()
    assert page.locator('#cart-count').inner_text()=='2'
    page.locator('#cart-toggle').click()
    page.locator('#order-form input[name="name"]').fill('Teste local GAIA')
    page.locator('#order-form input[name="email"]').fill('teste@example.invalid')
    # Prevent mail client invocation while exercising the complete local draft flow.
    page.evaluate("document.addEventListener('click',e=>{if(e.target.closest('a[href^=\"mailto:\"]'))e.preventDefault()},true)")
    page.locator('#checkout-btn').click()
    assert page.locator('#order-result').is_visible()
    assert 'Adesivos' in page.locator('#order-result textarea').input_value()
    results['shop'].append('Product filter, add, quantity, persistence and order preparation (no message sent)')
    browser.close()
server.shutdown()
(OUTPUT/'audit.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print('VIOLATIONS',[(r['path'],r['theme'],[(v['id'],len(v['nodes'])) for v in r['violations']]) for r in results['axe'] if r['violations']])
print('OVERFLOW',[r for r in results['layout'] if r['overflow']])
print('HTTP',results['requests'])

assert not results['requests'], 'Broken or incorrectly rooted local assets'
assert not any(r['overflow'] for r in results['layout']), 'Horizontal overflow'
assert not any(r['violations'] for r in results['axe']), 'Automated WCAG violations'
