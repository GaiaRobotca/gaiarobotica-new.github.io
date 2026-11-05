"""Rebuild faithful vector contours and PNG exports from the preserved GAIA source.

Optional authoring dependencies: opencv-python-headless, playwright, pillow;
install Chromium with `python -m playwright install chromium`.
The static site itself has no runtime dependency on these packages.
"""
from pathlib import Path
import cv2
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / 'assets/images/marca'
SOCIAL = ROOT / 'assets/images/social'


def main():
    original = cv2.imread(str(BRAND / 'logo-gaia.png'), cv2.IMREAD_GRAYSCALE)
    _, mask = cv2.threshold(original, 128, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    paths = []
    for contour in contours:
        if cv2.contourArea(contour) < 24:
            continue
        points = cv2.approxPolyDP(contour, 1.25, True).reshape(-1, 2)
        paths.append('M' + 'L'.join(f'{x},{y}' for x, y in points) + 'Z')
    # Compound evenodd paths retain the white holes without raster embedding.
    for variant, ink in [('dark', '#FFF5E9'), ('light', '#001A7F')]:
        body = f'<path fill="{ink}" fill-rule="evenodd" d="{"".join(paths)}"/>'
        symbol = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="96 40 816 808">{body}</svg>'
        (BRAND / f'gaia-symbol-{variant}.svg').write_text(symbol, encoding='utf-8')
        # Preserve the outlined lettering master; replace only its symbol group.
        logo = BRAND / f'gaia-logo-{variant}.svg'
        old = logo.read_text(encoding='utf-8')
        lettering = old[old.index('<g transform="translate(145'):old.rindex('</svg>')]
        logo.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 128"><g transform="scale(.1584) translate(-96 -40)">{body}</g>{lettering}</svg>', encoding='utf-8')
    symbol = (BRAND / 'gaia-symbol-dark.svg').read_text(encoding='utf-8')
    symbol_body = symbol[symbol.index('>') + 1:symbol.rindex('</svg>')]
    for filename, width, height, size in [('gaia-preview', 2400, 2400, 1600), ('gaia-preview-horizontal', 2400, 1260, 1000)]:
        x, y = (width-size)/2, (height-size)/2
        art = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#001A7F"/><svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="96 40 816 808">{symbol_body}</svg></svg>'
        (SOCIAL / f'{filename}.svg').write_text(art, encoding='utf-8')
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(device_scale_factor=1)
        exports = [(BRAND/'gaia-favicon.svg', BRAND/f'gaia-favicon-{size}.png',size,size) for size in [16,32,192,512]]
        exports += [(BRAND/'gaia-favicon.svg',BRAND/'gaia-touch-180.png',180,180)]
        exports += [(SOCIAL/f'{name}.svg',SOCIAL/f'{name}.png',w,h) for name,w,h in [('gaia-preview',2400,2400),('gaia-preview-horizontal',2400,1260)]]
        for source,target,width,height in exports:
            page.set_viewport_size({'width':width,'height':height})
            page.set_content('<style>html,body{margin:0;width:100%;height:100%;}svg{display:block;width:100%;height:100%;}</style>'+source.read_text(encoding='utf-8'))
            page.screenshot(path=str(target),omit_background=True)
        browser.close()
    Image.open(BRAND/'gaia-favicon-512.png').save(BRAND/'gaia-favicon.ico',sizes=[(16,16),(32,32),(48,48)])
    print('Brand SVG/PNG/ICO assets rebuilt from logo-gaia.png and favicon optical master.')


if __name__ == '__main__':
    main()
