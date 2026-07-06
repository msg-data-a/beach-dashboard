import streamlit as st

# Page Configuration for Mobile and Desktop layouts
st.set_page_config(
    page_title="Kohler-Andrae South Beach Monitor",
    page_icon="🏖️",
    layout="wide"
)

LAT = 43.595644
LON = -87.768558

# Title Header Configuration
st.title("🏖️ Kohler-Andrae Beach Monitor & Surf Panel")
st.caption(f"Custom live monitoring dashboard targeting beach coordinates: {LAT}, {LON}")
st.markdown("---")

# Row 1: Explaining your Custom Calculation Reference Guidelines
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏊 Swimability & Exit Guide")
    st.markdown("""
    * **🟢 Favorable (75-100)**: Warm air, high humidity, light onshore winds. Minimal body heat loss upon exit.
    * **🟡 Brisk (50-74)**: Good swimming conditions, but an active breeze will cause an immediate chill the second you step out of the surf.
    * **🔴 Chilling / Polar (<50)**: High risk of cold shock. Strong West/Northwest offshore winds cause **Upwelling**, dropping water temps rapidly.
    """)

with col2:
    st.subheader("🪰 Biting Black Fly Risk Index")
    st.markdown("""
    * **🟢 LOW RISK**: Heavy onshore winds (East/Southeast) blowing flies away from the sand, or wind speeds exceeding **12 mph**.
    * **🟡 MODERATE**: Calm conditions. Keep bug spray handy.
    * **🔴 HIGH RISK**: Light or gentle offshore breeze (**West/Northwest winds at 4-11 mph**). This actively floats swarms out of the woods down onto the open beach.
    """)

st.markdown("---")
st.subheader("📊 Live Hydrodynamic, Wave & Weather Station Map")
st.info("💡 **Interactive Panel Instructions:** Use the widget below to view live sea surface temperatures, precise hourly wind vectors, wave heights, and upwelling shifts directly over our target coordinates.")

# Embed the responsive meteorological panel. It renders client-side on your screen, completely avoiding API server blocks.
embed_html = f"""
<div style="width: 100%; height: 700px; overflow: hidden; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <iframe 
        src="https://windy.com{LAT}&lon={LON}"
        width="100%" 
        height="100%" 
        frameborder="0"
        style="border: none;">
    </iframe>
</div>
"""

# Inject into the Streamlit Web Application
st.components.v1.html(embed_html, height=720)
