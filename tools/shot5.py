import asyncio
from playwright.async_api import async_playwright
TARGETS=[(1440,900,'.lstrip-foot','50-foot-logos'),(1440,900,'#team','51-team'),(390,844,'.lstrip-foot','52-m-foot-logos'),(390,844,'#team','53-m-team'),(768,1024,'#team','54-t-team')]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for w,h,sel,name in TARGETS:
            pg=await b.new_page(viewport={'width':w,'height':h})
            await pg.goto('file:///home/user/index.html'); await pg.wait_for_timeout(700)
            for _ in range(4):
                await pg.evaluate(f"document.querySelector('{sel}').scrollIntoView({{block:'center'}})")
                await pg.wait_for_timeout(450)
            await pg.screenshot(path=f'shots/{name}.png'); await pg.close()
        await b.close()
asyncio.run(main())
