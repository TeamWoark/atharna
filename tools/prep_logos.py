import asyncio, pathlib, base64
from PIL import Image
from playwright.async_api import async_playwright
OUT = pathlib.Path('assets/partners')

def white_to_alpha(im, thr=243):
    im = im.convert('RGBA'); px = im.load(); w,h = im.size
    for y in range(h):
        for x in range(w):
            r,g,b,a = px[x,y]
            if r>thr and g>thr and b>thr: px[x,y] = (255,255,255,0)
    return im

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':900,'height':900}, device_scale_factor=2)
        for name, f, w in [('sbmf-logo','sbmf.svg',760), ('riyada-logo','riyada.svg',760)]:
            data = base64.b64encode((OUT/f).read_bytes()).decode()
            pathlib.Path('/tmp/l.html').write_text(
              f'<body style="margin:0;background:transparent"><img id="im" src="data:image/svg+xml;base64,{data}" style="width:{w}px;display:block"></body>')
            await pg.goto('file:///tmp/l.html'); await pg.wait_for_timeout(350)
            await pg.locator('#im').screenshot(path=f'/tmp/{name}.png', omit_background=True)
        await b.close()

    for name in ['sbmf-logo','riyada-logo']:
        im = Image.open(f'/tmp/{name}.png').convert('RGBA').crop(Image.open(f'/tmp/{name}.png').convert('RGBA').getbbox())
        im.save(OUT/f'{name}.png'); print(name, im.size)

    for name, src in [('cgschool-logo','cg-square.webp'), ('futureskills-logo','fs.png')]:
        im = white_to_alpha(Image.open(OUT/src))
        im = im.crop(im.getbbox())
        im.save(OUT/f'{name}.png'); print(name, im.size)

asyncio.run(main())
