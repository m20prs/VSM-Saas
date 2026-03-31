import asyncio
import os
import hashlib
from playwright.async_api import async_playwright
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch
from database import log_result
from notifications import send_discord_alert

async def run_visual_check(context, url):
    # Create a unique ID for the URL to prevent filename conflicts
    url_id = hashlib.md5(url.encode()).hexdigest()[:8]
    baseline_path = f"baseline_{url_id}.png"
    current_path = f"current_{url_id}.png"
    diff_path = f"diff_{url_id}.png"

    page = await context.new_page()
    
    try:
        print(f"🔍 Monitoring: {url}")
        # Navigate to the URL and wait for the initial load
        await page.goto(url, wait_until="load", timeout=60000)
        
        # Artificial delay to allow dynamic content/fonts to stabilize
        await asyncio.sleep(2) 
        
        # Capture the current state of the page
        await page.screenshot(path=current_path, full_page=True)
        
        # Step 1: Establish baseline if one does not exist
        if not os.path.exists(baseline_path):
            os.rename(current_path, baseline_path)
            log_result(url, "✅ Baseline Created", 0, baseline_path, "", "")
            print(f"✅ Baseline established for {url_id}.")
            return

        # Step 2: Comparison Logic
        with Image.open(baseline_path).convert("RGBA") as img1, \
             Image.open(current_path).convert("RGBA") as img2:
            
            # Normalize images to the same canvas size to prevent pixelmatch errors
            max_width = max(img1.width, img2.width)
            max_height = max(img1.height, img2.height)

            img1_f = Image.new("RGBA", (max_width, max_height))
            img2_f = Image.new("RGBA", (max_width, max_height))
            img1_f.paste(img1, (0, 0))
            img2_f.paste(img2, (0, 0))

            diff = Image.new("RGBA", (max_width, max_height))
            
            # Perform pixel-by-pixel comparison
            mismatch = pixelmatch(img1_f, img2_f, diff, threshold=0.1)

            # Determine status based on the mismatch threshold (500 pixels)
            status = "✅ Stable" if mismatch <= 500 else "❌ Change Detected"
            
            if mismatch > 500:
                diff.save(diff_path)
                print(f"❌ Change Detected! Pixels: {mismatch}")
                
                # Notification Trigger (Discord)
                DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE" 
                if DISCORD_WEBHOOK_URL != "YOUR_DISCORD_WEBHOOK_URL_HERE":
                    send_discord_alert(DISCORD_WEBHOOK_URL, url, mismatch, diff_path)
            else:
                print(f"✅ Stable.")

            # Record results in the SQLite database
            log_result(url, status, mismatch, baseline_path, current_path, diff_path)

    except Exception as e:
        print(f"⚠️ Error during visual check: {e}")
        log_result(url, f"⚠️ Error: {str(e)}", 0, "", "", "")
    finally:
        # Ensure the page is closed to free up browser resources
        await page.close()

async def main():
    # Standard test URL used for local execution
    url = "https://www.wikipedia.org"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Create a browser context with a fixed viewport for consistency
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        
        await run_visual_check(context, url)
        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped by user. Cleaning up...")