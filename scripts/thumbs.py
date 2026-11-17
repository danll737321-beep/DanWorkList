"""Take a small screenshot of each GitHub Pages site in items.json -> thumbs/<repo>.jpg.

Only missing thumbnails are made; pass --all to redo every one.
Needs: pip install playwright pillow && python -m playwright install chromium
Runs in the GitHub Action "Thumbnails" (the Claude workspace cannot reach github.io).
"""
import io, json, pathlib, sys
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'thumbs'
OUT.mkdir(exist_ok=True)
items = [i for i in json.loads((ROOT / 'items.json').read_text(encoding='utf-8'))['items'] if i['k'] == 'github']
todo = [i for i in items if '--all' in sys.argv or not (OUT / f"{i['id']}.jpg").exists()]
made = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1280, 'height': 800})
    for i in todo:
        try:
            pg.goto(f"https://danll737321-beep.github.io/{i['id']}/", wait_until='networkidle', timeout=30000)
            pg.wait_for_timeout(1200)
            im = Image.open(io.BytesIO(pg.screenshot())).convert('RGB').resize((320, 200), Image.LANCZOS)
            im.save(OUT / f"{i['id']}.jpg", quality=78, optimize=True)
            made += 1
        except Exception as e:
            print('skip', i['id'], e)
    b.close()
print(f'Made {made} of {len(todo)} thumbnails.')
