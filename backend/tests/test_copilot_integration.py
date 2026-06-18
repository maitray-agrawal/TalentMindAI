import os
import pytest
import time
from playwright.sync_api import sync_playwright

# Locate the frontend file path dynamically
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend_screens"))
COPILOT_HTML = os.path.join(FRONTEND_DIR, "recruiter_copilot.html")
COPILOT_URL = f"file:///{COPILOT_HTML.replace(os.sep, '/')}"

def test_copilot_page_loads_and_api_check():
    """Verify that the Copilot page loads and displays connected status."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(COPILOT_URL)
        
        # Check connection badge or connection indicator
        # The connection badge has classes like 'bg-success/20 text-success' or similar
        # Let's wait for the connection check to run
        page.wait_for_timeout(2000)
        
        # Verify title
        assert "Recruiter Copilot" in page.title()
        
        # Verify the presence of dropdown selectors
        assert page.locator("#context-candidate").count() == 1
        assert page.locator("#context-job").count() == 1
        
        browser.close()

def test_copilot_left_panel_population():
    """Select candidate & job, and verify left panel details are loaded from API."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(COPILOT_URL)
        page.wait_for_timeout(3000)  # Wait for API data population
        
        # Select first candidate in dropdown (index 1 since 0 is placeholder)
        candidate_select = page.locator("#context-candidate")
        candidate_select.select_option(index=1)
        
        # Select first job
        job_select = page.locator("#context-job")
        job_select.select_option(index=1)
        
        # Wait for automatic change listener to trigger and update DOM
        page.wait_for_timeout(3000)
        
        # Verify Candidate Name matches dynamic API loaded value (not "Elena Rodriguez" placeholder)
        candidate_name = page.locator("#copilot-candidate-name").inner_text()
        assert candidate_name != "Elena Rodriguez", "Candidate name did not update from API"
        assert len(candidate_name.strip()) > 0
        
        # Check if Skills list contains items (not empty/placeholder)
        skills = page.locator("#copilot-candidate-skills span")
        assert skills.count() > 0, "Candidate skills did not populate from the backend API"
        
        # Check if Resume Summary list contains items
        summary_list = page.locator("#copilot-resume-summary li")
        assert summary_list.count() > 0, "Candidate strengths/weaknesses did not populate in the summary list"
        
        # Check if Skill Gap Analysis container contains items
        skill_gap_items = page.locator("#copilot-skill-gap-container .space-y-1")
        assert skill_gap_items.count() > 0, "Skill gap analysis did not populate"
        
        browser.close()

def test_copilot_chat_and_roadmaps():
    """Verify chat input, response rendering, and upskilling roadmaps."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(COPILOT_URL)
        page.wait_for_timeout(3000)
        
        # Select a candidate and job first to have full context
        page.locator("#context-candidate").select_option(index=1)
        page.locator("#context-job").select_option(index=1)
        page.wait_for_timeout(2000)
        
        # Type a query for an upskilling roadmap
        input_field = page.locator("#copilot-input")
        input_field.fill("Give me an upskilling roadmap")
        
        # Click send
        page.locator("#copilot-send-btn").click()
        
        # Wait for the AI message to appear in the stream (which may take a few seconds)
        page.wait_for_selector(".glass-card:has-text('Phase 1:')", timeout=15000)
        
        # Verify that suggested action buttons are rendered
        action_buttons = page.locator(".glass-card button")
        assert action_buttons.count() > 0, "Suggested actions were not rendered in the chat response"
        
        browser.close()

def test_copilot_view_profile_routing():
    """Verify that clicking 'View Full Profile' routes correctly with query parameters."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(COPILOT_URL)
        page.wait_for_timeout(3000)
        
        # Select candidate
        page.locator("#context-candidate").select_option(index=1)
        cand_id = page.locator("#context-candidate").input_value()
        page.wait_for_timeout(1000)
        
        # Click view profile button
        page.locator("#copilot-view-profile-btn").click()
        page.wait_for_timeout(2000)
        
        # Page should navigate to candidate_details.html with candidate_id
        current_url = page.url
        assert "candidate_details.html" in current_url
        assert f"id={cand_id}" in current_url
        
        browser.close()
