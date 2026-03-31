import streamlit as st
import os
from PIL import Image

st.set_page_config(layout="wide")
st.title("🛡️ Visual Guard: Site Monitor")

# Sidebar for controls
url_to_check = st.sidebar.text_input("URL to monitor", "https://wikipedia.org")
if st.sidebar.button("Run Manual Check"):
    # Trigger your run_visual_check function here
    st.sidebar.success("Check triggered!")

# Main UI: Results Gallery
cols = st.columns(3)

# Logic to grab the latest images based on your hashing
url_id = "your_hash_here" # You'd pull this from a database or file list
base = f"baseline_{url_id}.png"
curr = f"current_{url_id}.png"
diff = f"diff_{url_id}.png"

if os.path.exists(base):
    with cols[0]:
        st.subheader("Baseline")
        st.image(base)
    with cols[1]:
        st.subheader("Current")
        st.image(curr)
    with cols[2]:
        st.subheader("Differences")
        if os.path.exists(diff):
            st.image(diff)
        else:
            st.success("No differences detected.")