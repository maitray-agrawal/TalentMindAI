import asyncio
import time
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Listen to requests/responses
        req_times = {}
        
        def handle_request(req):
            req_times[req.url] = time.time()
            
        def handle_response(res):
            url = res.url
            if url in req_times:
                duration = time.time() - req_times[url]
                print(f"FETCH COMPLETED: {res.status} {url} in {duration:.3f} seconds")
                
        page.on("request", handle_request)
        page.on("response", handle_response)
        page.on("console", lambda msg: print(f"CONSOLE: [{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        print("\n--- STAGE 1: Page Load and Speed Verification ---")
        t0 = time.time()
        await page.goto("http://127.0.0.1:3000/candidate_search.html")
        
        # Wait up to 1 second and check if candidate cards are rendered
        try:
            await page.wait_for_selector("#candidates-grid .glass-card", timeout=1500)
            print("SUCCESS: Candidate cards rendered in <1.5s (non-blocking)!")
        except Exception as e:
            print(f"FAILED: Candidate cards did not render within 1.5 seconds: {e}")
            
        # Get count of initial cards
        initial_count = await page.eval_on_selector_all("#candidates-grid .glass-card", "els => els.length")
        print(f"Initial cards count: {initial_count}")
        
        print("\n--- STAGE 2: Wait for Stats to load ---")
        # Wait for stats endpoint to finish
        await page.wait_for_selector("#skills-filter-container button", timeout=15000)
        skills = await page.eval_on_selector_all("#skills-filter-container button", "els => els.map(el => el.textContent)")
        print(f"Skills loaded dynamically: {skills}")
        
        print("\n--- STAGE 3: Test Search Input ('Python') ---")
        # Find search input. It's in the header.
        search_input = await page.query_selector("header input")
        if not search_input:
            search_input = await page.query_selector("main input")
            
        if search_input:
            print("Typing 'Python' in search bar...")
            await search_input.fill("Python")
            await asyncio.sleep(2) # wait for debounce + fetch
            python_count = await page.eval_on_selector_all("#candidates-grid .glass-card", "els => els.length")
            print(f"Cards count after searching 'Python': {python_count}")
            # print first candidate name
            first_name = await page.eval_on_selector("#candidates-grid .glass-card h3", "el => el.textContent")
            print(f"First candidate name: {first_name}")
            # clear search
            await search_input.fill("")
            await asyncio.sleep(2)
        else:
            print("FAILED: Search input not found!")
            
        print("\n--- STAGE 4: Test Experience Filter ---")
        # Slider
        slider = await page.query_selector('input[type="range"]')
        if slider:
            print("Setting experience slider to 10 years...")
            # We can use dispatch_event to change the value
            await page.eval_on_selector('input[type="range"]', "el => { el.value = 10; el.dispatchEvent(new Event('input')); }")
            await asyncio.sleep(2)
            exp_count = await page.eval_on_selector_all("#candidates-grid .glass-card", "els => els.length")
            print(f"Cards count with 10+ years experience: {exp_count}")
            # Reset slider
            await page.eval_on_selector('input[type="range"]', "el => { el.value = 0; el.dispatchEvent(new Event('input')); }")
            await asyncio.sleep(2)
        else:
            print("FAILED: Experience range slider not found!")
            
        print("\n--- STAGE 5: Test Work Preference Checkbox Toggles ---")
        # Checkboxes are in Location Type. The first one is Remote. Let's toggle the checkboxes.
        checkboxes = await page.query_selector_all("aside input[type=\"checkbox\"]")
        if len(checkboxes) >= 2:
            print("Checking both Remote and Hybrid/On-site...")
            # Toggle the second one to checked
            is_checked = await checkboxes[1].is_checked()
            if not is_checked:
                await checkboxes[1].click()
                
            await asyncio.sleep(2)
            both_count = await page.eval_on_selector_all("#candidates-grid .glass-card", "els => els.length")
            print(f"Cards count with BOTH checked: {both_count}")
        else:
            print(f"FAILED: Found {len(checkboxes)} checkboxes in aside.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
