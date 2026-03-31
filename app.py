import streamlit as st
import os
import asyncio
from PIL import Image
from playwright.async_api import async_playwright
from engine import run_visual_check
from utils import get_url_id

# 1. Page Configuration
st.set_page_config(page_title="Visual Guard", layout="wide")
st.title("🛡️ Visual Guard: Site Monitor")

# 2. Sidebar Configuration
st.sidebar.header("Controls")
url_to_check = st.sidebar.text_input("URL to monitor", "https://www.wikipedia.org")
run_button = st.sidebar.button("Run Manual Check")

# 3. Logic & State
url_id = get_url_id(url_to_check)
base_path = f"baseline_{url_id}.png"
curr_path = f"current_{url_id}.png"
diff_path = f"diff_{url_id}.png"

# Handle Execution
if run_button:
    with st.spinner(f"Analyzing {url_to_check}..."):
        async def trigger_engine():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                # Ensure context matches your engine's expectations
                context = await browser.new_context(viewport={'width': 1280, 'height': 800})
                await run_visual_check(context, url_to_check)
                await browser.close()
        
        try:
            asyncio.run(trigger_engine())
            st.sidebar.success("Check Complete!")
            st.rerun() 
        except Exception as e:
            st.sidebar.error(f"Execution Error: {e}")

# 4. Main UI Display
if os.path.exists(base_path):
    cols = st.columns(3)
    
    with cols[0]:
        st.subheader("Baseline")
        st.image(base_path, use_container_width=True)
    
    with cols[1]:
        st.subheader("Current")
        if os.path.exists(curr_path):
            st.image(curr_path, use_container_width=True)
        else:
            st.info("No current snapshot found. Run a check.")

    with cols[2]:
        st.subheader("Differences")
        if os.path.exists(diff_path):
            st.warning("Visual Mismatch Detected!")
            st.image(diff_path, use_container_width=True)
        else:
            st.success("No visual changes detected.")
else:
    st.info("No baseline established for this URL. Run a manual check to create one.")