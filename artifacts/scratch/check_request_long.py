import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
        except Exception as e:
            print(f"Failed to launch chromium: {e}")
            return
            
        page = await browser.new_page()
        
        page.on("request", lambda req: print(f"REQ: {req.method} {req.url}"))
        page.on("response", lambda res: print(f"RES: {res.status} {res.url}"))
        page.on("console", lambda msg: print(f"CONSOLE: [{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        print("Navigating to http://127.0.0.1:3000/candidate_search.html")
        await page.goto("http://127.0.0.1:3000/candidate_search.html")
        
        # Wait 20 seconds
        await asyncio.sleep(20)
        
        # Get grid elements html
        grid_html = await page.eval_on_selector("#candidates-grid", "el => el.innerHTML")
        print("GRID HTML SUBSTRING AFTER 20s:")
        print(grid_html[:2000])
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
