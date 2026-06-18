import os
import sys
import time
from playwright.sync_api import sync_playwright

def print_narration(step_num, title, text):
    border = "=" * 80
    print(f"\n{border}")
    print(f" STEP {step_num}: {title.upper()}")
    print(f"{border}")
    print(text)
    print(f"{border}\n")

def run():
    print("Initializing Playwright automation for TalentMind AI...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )
        
        # Create a context with viewport matching a full screen
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        
        # Get path to dashboard
        dashboard_path = os.path.abspath("frontend_screens/dashboard.html")
        dashboard_url = f"file:///{dashboard_path.replace(os.sep, '/')}"
        
        print(f"Opening dashboard at {dashboard_url}...")
        page.goto(dashboard_url)
        page.wait_for_timeout(2000)  # wait for API sync
        
        # Step 1: Dashboard and Scale
        print_narration(1, "The Command Center - Dashboard & Scale", 
            "NARRATION:\n"
            "Welcome to TalentMind AI, a premium candidate discovery and ranking platform.\n"
            "Here we are on the Recruiter Dashboard. Notice the green 'API Online' status badge,\n"
            "and our candidate dataset scale: 100,001 candidate profiles fully indexed in our database.\n"
            "Below, we see our active job roles and recruitment activities.")
        input(">>> Press ENTER when you are ready to navigate to Candidate Explorer...")
        
        # Step 2: Navigate to Candidate Search
        print("Navigating to Candidate Search...")
        page.click('a[href="candidate_search.html"]')
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        
        print_narration(2, "Search & Discovery at 100k Scale", 
            "NARRATION:\n"
            "Let's explore Candidate Explorer. We're querying over 100k records in milliseconds.\n"
            "I'll filter for candidates with experience of 5+ years, and toggle Remote Global work preference.\n"
            "Watch as the results adapt instantly.")
        
        # Interact with the search page
        # Set experience slider to 5
        slider = page.locator('input[type="range"]')
        if slider.count() > 0:
            slider.evaluate("el => { el.value = 5; el.dispatchEvent(new Event('input')); }")
            page.wait_for_timeout(1000)
            
        # Select React Native skill if present, or search for "Python"
        search_input = page.locator('header input, main input').first
        if search_input.count() > 0:
            search_input.click()
            # type Python character by character for realistic typing
            search_input.type("Python", delay=100)
            page.wait_for_timeout(2000)
            
        input(">>> Press ENTER when you are ready to navigate to the Matching & Ranking View...")
        
        # Step 3: Match & Rank Engine
        print("Navigating to Ranking...")
        page.click('a[href="candidate_ranking.html"]')
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)
        
        print_narration(3, "Hybrid Match & Rank Engine", 
            "NARRATION:\n"
            "Now let's see our multi-variate Rank Engine. I will select the 'Senior Frontend Engineer' open role\n"
            "from our selector. The engine instantly computes complex heuristic matches, scoring candidates\n"
            "on skills (30%), experience (20%), and behavioral signals (10%).")
        
        # Select job role
        # We know ID 3 is Senior Frontend Engineer
        job_selector = page.locator('#job-selector')
        if job_selector.count() > 0:
            job_selector.select_option("3")
            page.wait_for_timeout(3000) # Wait for table to load
            
        input(">>> Press ENTER to trigger Groq AI Recruiter Reranking...")
        
        # Step 4: Groq AI Recruiter Reranking
        print("Triggering Groq Reranking...")
        rerank_btn = page.locator('#btn-groq-rerank')
        if rerank_btn.count() > 0:
            rerank_btn.click()
            # The loading simulation will take place, and then load rankings
            page.wait_for_timeout(4000)
            
        print_narration(4, "Groq AI Recruiter Reranking & XAI", 
            "NARRATION:\n"
            "With one click, we run the Groq AI Reranker. This utilizes Gemini/Groq LLMs to analyze qualitative alignment,\n"
            "re-weighting our candidates. Notice the pulsing 'Groq AI' badges next to their names.\n"
            "Let's drill down into the top candidate's profile to inspect their detailed fit.")
        
        # Click on the first candidate's name to view profile details
        first_candidate_name = page.locator('main tbody tr h4').first
        if first_candidate_name.count() > 0:
            first_candidate_name.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            
        input(">>> Press ENTER to view Candidate Comparison...")
        
        # Step 5: Candidate Comparison & Skill Gap
        print("Navigating to Comparison...")
        page.click('a[href="candidate_comparison.html"]')
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        print_narration(5, "Candidate Comparison & Skill Gap Analysis", 
            "NARRATION:\n"
            "Here we compare top contenders side-by-side. The dashboard maps their skills spectrum,\n"
            "experience years, and behavioral risks like retention probability or counter-offer risk.\n"
            "Let's look at the Skill Gap and upskilling roadmaps generated to help bridge technical gaps.")
        
        # Go to Skill Gap
        page.click('a[href="skill_gap_analysis.html"]')
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        # Select the candidate and job role in Skill Gap
        cand_select = page.locator('#candidate-selector')
        if cand_select.count() > 0:
            # Select first option that isn't empty
            cand_select.select_option(index=1)
            page.wait_for_timeout(1000)
            
        job_sel_gap = page.locator('#job-selector')
        if job_sel_gap.count() > 0:
            job_sel_gap.select_option("3")
            page.wait_for_timeout(2000)
            
        input(">>> Press ENTER to activate the Recruiter Copilot...")
        
        # Step 6: Recruiter Copilot
        print("Navigating to Recruiter Copilot...")
        page.click('a[href="recruiter_copilot.html"]')
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1500)
        
        print_narration(6, "Recruiter Copilot (Outreach)", 
            "NARRATION:\n"
            "Finally, let's open Recruiter Copilot, a conversational assistant. I'll ask it to draft a personalized\n"
            "outreach email for our top candidate Elena Rodriguez, highlighting her micro-frontends experience.")
        
        chat_input = page.locator('input[placeholder*="Type a message"], textarea').first
        if chat_input.count() > 0:
            chat_input.click()
            chat_input.type("Draft a personalized outreach email for Elena Rodriguez for the Senior Frontend Engineer role. Mention her blog post on micro-frontends.", delay=80)
            page.wait_for_timeout(1000)
            # Press send button or press enter
            page.keyboard.press("Enter")
            page.wait_for_timeout(4000) # Wait for assistant response
            
        input(">>> Press ENTER to view FastAPI Backend Swagger Docs...")
        
        # Step 7: Swagger Docs
        print("Navigating to Swagger Docs...")
        page.goto("http://127.0.0.1:8000/docs")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        
        print_narration(7, "Production Swagger APIs & Challenge Compliance", 
            "NARRATION:\n"
            "Our FastAPI backend is fully self-documenting, exposing optimized endpoints for ranking, searching, and reranking.\n"
            "Under the submission namespace, we execute the CSV generation pipeline, producing a fully validated,\n"
            "schema-compliant 100-candidate ranking file matching the Hack2Skill requirements.\n"
            "Thank you for watching the TalentMind AI demonstration!")
            
        input(">>> Press ENTER to finish and close the browser...")
        print("Demo automation complete. Exiting...")
        browser.close()

if __name__ == "__main__":
    run()
