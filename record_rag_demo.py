import time
import os
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = "/config/.gemini/antigravity/brain/1327f152-ddab-4f55-bc32-a0386397aae0"
PROJECT_DIR = "/config/Desktop/Session3/travel-destination-explorer"
APP_URL = "https://travel-destination-explorer-frontend-879292600164.us-east1.run.app"

def record_demo():
    print(f"Starting Playwright video recording targeting {APP_URL}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            record_video_dir=ARTIFACT_DIR,
            record_video_size={"width": 1280, "height": 800},
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        page.goto(APP_URL, wait_until="networkidle")
        print("Page loaded.")
        time.sleep(3)

        # Action 1: Show beach destinations as cards
        print("Executing Action 1: Show beach destinations as cards...")
        page.click("text='Show me beach destinations'")
        time.sleep(12)

        # Action 2: Check weather in Bali
        print("Executing Action 2: Check weather in Bali...")
        page.click("text='What is the weather in Bali'")
        time.sleep(10)

        # Action 3: Generate an image of Santorini
        print("Executing Action 3: Generate an image of Santorini...")
        page.click("text='Generate an image of Santorini'")
        time.sleep(15)

        # Action 4: RAG Engine Scenario — Consult travel guide for herbal notes
        print("Executing Action 4: RAG Engine — Consult travel guide for herbal notes...")
        page.fill("#input", "Consult the travel guide for herbal notes")
        page.click("button[type='submit']")
        time.sleep(15)
        print("Action 4 complete.")

        video = page.video
        context.close()
        browser.close()

        if video:
            video_path = video.path()
            target_webm = os.path.join(PROJECT_DIR, "travel_agent_demo.webm")
            os.rename(video_path, target_webm)
            print(f"Saved demo video to {target_webm}")

if __name__ == "__main__":
    record_demo()
