import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        console_messages = []
        network_requests = []
        network_responses = []
        
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        page.on("request", lambda req: network_requests.append(req.url))
        
        async def handle_response(response):
            if "api/copilot/chat" in response.url or "api/candidates" in response.url:
                try:
                    text = await response.text()
                    network_responses.append(f"{response.url} -> {response.status}: {text[:200]}")
                except:
                    pass
        
        page.on("response", handle_response)
        
        print("Navigating to Recruiter Copilot...")
        await page.goto("file:///d:/TalentMindAI/frontend_screens/recruiter_copilot.html")
        await page.wait_for_timeout(2000)
        
        print("Typing message...")
        await page.fill("#copilot-input", "draft an email")
        await page.click("#copilot-send-btn")
        await page.wait_for_timeout(2000)
        
        print("\n--- Console Messages ---")
        for msg in console_messages:
            print(msg)
            
        print("\n--- Network Requests ---")
        for req in network_requests:
            if "127.0.0.1" in req or "localhost" in req:
                print(req)
                
        print("\n--- Network Responses ---")
        for res in network_responses:
            print(res)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
