import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Try to launch chromium
        try:
            browser = await p.chromium.launch(headless=True)
        except Exception as e:
            print(f"Failed to launch chromium: {e}")
            print("Installing chromium...")
            import subprocess
            subprocess.run(["playwright", "install", "chromium"])
            browser = await p.chromium.launch(headless=True)
            
        page = await browser.new_page()
        
        # Capture console messages
        page.on("console", lambda msg: print(f"CONSOLE: [{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        print("Navigating to http://127.0.0.1:3000/candidate_search.html")
        await page.goto("http://127.0.0.1:3000/candidate_search.html")
        
        # Wait for some time to let async fetches happen
        await asyncio.sleep(3)
        
        # Get content or grid elements count
        grid_html = await page.eval_on_selector("#candidates-grid", "el => el.innerHTML")
        print("GRID HTML SUBSTRING:")
        print(grid_html[:1000])
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
