import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1800,'height':1000},device_scale_factor=2)
    pg.goto('file://'+sys.argv[1]); pg.wait_for_timeout(300)
    h=pg.evaluate('document.body.scrollHeight')
    pg.set_viewport_size({'width':1800,'height':h})
    pg.screenshot(path=sys.argv[2],full_page=True)
    pg.pdf(path=sys.argv[3],width='1800px',height=f'{h+2}px',print_background=True)
    b.close(); print(h)
