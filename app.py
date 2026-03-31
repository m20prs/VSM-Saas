import streamlit as st
import os
import asyncio
import sqlite3
import pandas as pd
from PIL import Image
from playwright.async_api import async_playwright
from engine import run_visual_check
from utils import get_url_id

st.set_page_config(page_title="Visual Guard", layout="wide")
st.title("🛡️ Visual Guard: Site Monitor")

# 1. Sidebar for controls
url_to_check = st.sidebar.text_input("URL to monitor", "https://www.wikipedia.org")
run_button = st.sidebar.button("Run Manual Check")

url_id = get_url_id(url_to_check)
base_path = f"baseline_{url_id}.png"
curr_path = f"current_{url_id}.png"
diff_path = f"diff_{url_id}.png"

# 2. Trigger Logic
if run_button:
    with st.spinner(f"Analyzing {url_to_check}..."):
        async def trigger_engine():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(viewport={'width': 1280, 'height': 800})
                await run_visual_check(context, url_to_check)
                await browser.close()
        
        try:
            asyncio.run(trigger_engine())
            st.sidebar.success("Check Complete!")
            st.rerun() 
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

# 3. Main Results Display
if os.path.exists(base_path):
    cols = st.columns(3)
    with cols[0]:
        st.subheader("Baseline")
        st.image(base_path, use_container_width=True)
    with cols[1]:
        st.subheader("Current")
        if os.path.exists(curr_path):
            st.image(curr_path, use_container_width=True)
    with cols[2]:
        st.subheader("Differences")
        if os.path.exists(diff_path):
            st.image(diff_path, use_container_width=True)
        else:
            st.success("No visual changes detected.")

# 4. Persistence UI (History Table)
st.divider()
st.subheader("📜 Scan History")

if os.path.exists("monitor_results.db"):
    conn = sqlite3.connect("monitor_results.db")
    df = pd.read_sql_query("SELECT timestamp, url, status, mismatch_pixels FROM scan_history ORDER BY timestamp DESC LIMIT 10", conn)
    conn.close()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("History is currently empty.")
else:
    st.warning("Database not initialized. Run a check to start logging.")