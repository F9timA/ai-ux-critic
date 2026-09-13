import streamlit as st
from PIL import Image
from analyze import analyze_screenshot
import tempfile
import os

st.set_page_config(page_title="AI UX Critic", page_icon="🔍", layout="centered")

# --- Custom styling ---
st.markdown("""
<style>
.issue-card {
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 14px;
    background-color: #1e1e1e;
    border-left: 5px solid;
}
.severity-high { border-left-color: #e5484d; }
.severity-medium { border-left-color: #f5a524; }
.severity-low { border-left-color: #4cc9f0; }
.severity-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.badge-high { background-color: #e5484d; color: white; }
.badge-medium { background-color: #f5a524; color: black; }
.badge-low { background-color: #4cc9f0; color: black; }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.title("🔍 AI UX Critic")
st.write("Upload a UI screenshot and get an instant usability critique, grounded in real UX heuristics and accessibility guidelines.")

# --- Upload ---
uploaded_file = st.file_uploader("Upload a screenshot", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded screenshot", use_container_width=True)

    if st.button("Run Critique", type="primary"):
        with st.spinner("Analyzing against UX heuristics and accessibility guidelines..."):
            # Save temporarily so analyze_screenshot can open it by path
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                image.save(tmp.name)
                tmp_path = tmp.name

            try:
                result = analyze_screenshot(tmp_path)
            finally:
                os.remove(tmp_path)

        st.subheader("Critique Results")

        issues = result.get("issues", [])
        if not issues:
            st.info("No major issues found.")
        else:
            for issue in issues:
                severity = issue.get("severity", "low").lower()
                st.markdown(f"""
                <div class="issue-card severity-{severity}">
                    <span class="severity-badge badge-{severity}">{severity}</span>
                    <p><strong>{issue.get('heuristic_violated', '')}</strong></p>
                    <p>{issue.get('explanation', '')}</p>
                    <p>📍 {issue.get('location_in_image', '')}</p>
                    <p>💡 {issue.get('suggested_fix', '')}</p>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("👆 Upload a screenshot to get started.")