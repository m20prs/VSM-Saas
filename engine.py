import asyncio
import os
import hashlib
from playwright.async_api import async_playwright
from PIL import Image
from pixelmatch.contrib.PIL import pixelmatch

async def run_visual_check(context, url):
    url_id = hashlib.md5(url.encode()).hexdigest()[:8]
    baseline_path = f"baseline_{url_id}.png"
    current_path = f"current_{url_id}.png"
    diff_path = f"diff_{url_id}.png"

    page = await context.new_page()
    
    try:
        print(f"🔍 Monitoring: {url}")
        await page.goto(url, wait_until="load", timeout=60000)
        
        # Force a wait for dynamic elements or fonts
        await asyncio.sleep(2) 
        
        # Take the screenshot
        await page.screenshot(path=current_path, full_page=True)
        
        if not os.path.exists(baseline_path):
            os.rename(current_path, baseline_path)
            print(f"✅ Baseline established for {url_id}.")
            return

        # Comparison Logic
        with Image.open(baseline_path).convert("RGBA") as img1, \
             Image.open(current_path).convert("RGBA") as img2:
            
            max_width = max(img1.width, img2.width)
            max_height = max(img1.height, img2.height)

            img1_f = Image.new("RGBA", (max_width, max_height))
            img2_f = Image.new("RGBA", (max_width, max_height))
            img1_f.paste(img1, (0, 0))
            img2_f.paste(img2, (0, 0))

            diff = Image.new("RGBA", (max_width, max_height))
            mismatch = pixelmatch(img1_f, img2_f, diff, threshold=0.1)

            if mismatch > 500:
                diff.save(diff_path)
                print(f"❌ Change Detected! Pixels: {mismatch}")
            else:
                print(f"✅ Stable.")

    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        await page.close()

async def main():
    url = "https://www.wikipedia.org"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a single context to manage state/cookies if needed
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        

        await run_visual_check(context, url)
        # while True:
        #     await run_visual_check(context, url)
        #     print("💤 Sleeping for 5 minutes...")
        #     await asyncio.sleep(300)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped by user. Cleaning up...")