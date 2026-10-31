import asyncio, base64, pathlib
from playwright.async_api import async_playwright
items=[('logo-white.png','#231F20'),('logo-dark.png','#FAF7F2'),('mark.png','#231F20'),('wordmark.png','#231F20'),('mark-square.png','#FAF7F2')]
cells=[]
for f,bgc in items:
    d=base64.b64encode(pathlib.Path('assets/brand',f).read_bytes()).decode()
    cells.append(f'<div style="background:{bgc};padding:18px;display:grid;place-items:center;width:340px;height:200px"><img src="data:image/png;base64,{d}" style="max-height:150px;max-width:300px"><span style="font:11px sans-serif;color:#999">{f}</span></div>')
pathlib.Path('/tmp/bs.html').write_text('<body style="margin:0;background:#888;display:flex;flex-wrap:wrap;gap:10px;padding:12px">'+''.join(cells)+'</body>')
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':720,'height':450})
        await pg.goto('file:///tmp/bs.html'); await pg.wait_for_timeout(400)
        await pg.screenshot(path='shots/brand-assets.png', full_page=True); await b.close()
asyncio.run(main())
