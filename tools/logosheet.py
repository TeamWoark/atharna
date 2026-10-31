import asyncio, base64, pathlib
from playwright.async_api import async_playwright
files = ['sbmf.svg','riyada.svg','cgschool.webp','sbmf.png']
cells=[]
for f in files:
    p=pathlib.Path('assets/partners')/f
    if not p.exists(): continue
    mime='image/svg+xml' if f.endswith('.svg') else ('image/webp' if f.endswith('.webp') else 'image/png')
    b=base64.b64encode(p.read_bytes()).decode()
    cells.append(f'<div style="background:#fff;padding:16px;border:1px solid #ccc;display:grid;place-items:center;width:320px;height:200px"><img src="data:{mime};base64,{b}" style="max-width:100%;max-height:170px"><div style="font:12px sans-serif;color:#555">{f}</div></div>')
html='<body style="background:#f2f2f2;display:flex;flex-wrap:wrap;gap:14px;padding:20px">'+''.join(cells)+'</body>'
pathlib.Path('/tmp/sheet.html').write_text(html)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':720,'height':500})
        await pg.goto('file:///tmp/sheet.html'); await pg.wait_for_timeout(500)
        await pg.screenshot(path='shots/logos.png', full_page=True); await b.close()
asyncio.run(main())
