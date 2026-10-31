import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':1440,'height':900})
        errs=[]
        pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file:///home/user/index.html')
        await pg.wait_for_timeout(1200)
        await pg.screenshot(path='shots/01-hero.png')
        for sid,name in [('challenge','02-challenge'),('journey','03-journey'),('market','04-market'),
                         ('solutions','05-solutions'),('roadmap','06-roadmap'),('gallery','07-gallery'),
                         ('brand','08-brand'),('team','09-team'),('partners','12-partners')]:
            await pg.evaluate(f"document.getElementById('{sid}').scrollIntoView()")
            await pg.wait_for_timeout(900)
            await pg.screenshot(path=f'shots/{name}.png')
        await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await pg.wait_for_timeout(600)
        await pg.screenshot(path='shots/10-footer.png')
        m = await b.new_page(viewport={'width':390,'height':844})
        await m.goto('file:///home/user/index.html')
        await m.wait_for_timeout(1000)
        await m.screenshot(path='shots/11-mobile-hero.png')
        print("ERRORS:", errs[:10])
        await b.close()
asyncio.run(main())
