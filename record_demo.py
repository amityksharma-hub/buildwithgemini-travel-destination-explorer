import time
import os
from playwright.sync_api import sync_playwright

ARTIFACT_DIR = "/config/.gemini/antigravity/brain/1327f152-ddab-4f55-bc32-a0386397aae0"
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
        time.sleep(2)

        # Action 1: Show all destinations as cards (Click 'Show me beach destinations')
        print("Executing Action 1: Show beach destinations as cards...")
        page.click("text='Show me beach destinations'")
        # Wait for agent response message bubble to appear and finish loading
        page.wait_for_selector(".msg.agent .a2card", timeout=45000)
        print("Action 1 complete: Cards rendered.")
        time.sleep(5)

        # Action 2: Check weather in Bali (Click 'What is the weather in Bali')
        print("Executing Action 2: Check weather in Bali...")
        page.click("text='What is the weather in Bali'")
        # Wait for second agent response bubble
        page.wait_for_selector(".msg.agent:nth-of-type(4)", timeout=45000)
        print("Action 2 complete: Weather response rendered.")
        time.sleep(5)

        # Action 3: Generate an image of Santorini and show it in a card
        print("Executing Action 3: Generate an image of Santorini...")
        page.click("text='Generate an image of Santorini'")
        # Wait for image generation tool response containing an <img> or rich card
        page.wait_for_selector(".msg.agent:nth-of-type(6)", timeout=60000)
        time.sleep(8)
        print("Action 3 complete: Image card rendered.")

        video = page.video
        context.close()
        browser.close()

        if video:
            video_path = video.path()
            target_path = os.path.join(ARTIFACT_DIR, "travel_agent_demo.webm")
            os.rename(video_path, target_path)
            print(f"Saved demo video to {target_path}")

if __name__ == "__main__":
    record_demo()
