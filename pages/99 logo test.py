"""
Minimal Logo Test Dashboard
"""

import streamlit as st
import os

st.set_page_config(page_title="Logo Test Simple", page_icon="🖼️", layout="wide")

st.title("🖼️ Simple Logo Test")

# Test 1: Check if file exists
LOGO_PATH = "/mount/src/mind-platform/assets/miva_logo_dark.png"

st.header("Test 1: File Existence")
if os.path.exists(LOGO_PATH):
    st.success(f"✅ File exists at: {LOGO_PATH}")
    st.write(f"File size: {os.path.getsize(LOGO_PATH):,} bytes")
else:
    st.error(f"❌ File not found at: {LOGO_PATH}")

st.markdown("---")

# Test 2: Try to display in main area
st.header("Test 2: Display in Main Area")
try:
    st.image(LOGO_PATH, width=300, caption="Logo in main area")
    st.success("✅ Logo displayed in main area successfully!")
except Exception as e:
    st.error(f"❌ Error displaying in main area: {e}")

st.markdown("---")

# Test 3: Try to display in sidebar
st.header("Test 3: Display in Sidebar")
try:
    st.sidebar.image(LOGO_PATH, width=180)
    st.success("✅ Check the sidebar - logo should be visible there!")
except Exception as e:
    st.error(f"❌ Error displaying in sidebar: {e}")

st.markdown("---")

# Test 4: Alternative paths
st.header("Test 4: Try Alternative Paths")

alternative_paths = [
    "assets/miva_logo_dark.png",
    "./assets/miva_logo_dark.png",
    "/mount/src/mind-platform/assets/miva_logo_dark.png",
]

for path in alternative_paths:
    if os.path.exists(path):
        st.success(f"✅ Found at: {path}")
        try:
            st.image(path, width=200, caption=f"Using: {path}")
        except Exception as e:
            st.error(f"Error displaying: {e}")
    else:
        st.warning(f"❌ Not found: {path}")

st.markdown("---")

# Show actual sidebar code
st.header("Sidebar Code Test")
st.code("""
# This is the code in your sidebar:
try:
    LOGO_PATH = "/mount/src/mind-platform/assets/miva_logo_dark.png"
    if os.path.exists(LOGO_PATH):
        st.sidebar.image(LOGO_PATH, width=180)
except Exception as e:
    st.sidebar.error(f"Logo error: {e}")
""")

st.info("👈 **Look at the sidebar** - do you see the MIVA logo there?")
