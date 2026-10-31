import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for w in (390,768,1440):
            pg=await b.new_page(viewport={'width':w,'height':900})
            errs=[]
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file:///home/user/index.html'); await pg.wait_for_timeout(700)
            r=await pg.evaluate("({sw:document.documentElement.scrollWidth, iw:window.innerWidth, h:document.body.scrollHeight})")
            print(w, r, 'errors:', errs)
            await pg.close()
        await b.close()
asyncio.run(main())
