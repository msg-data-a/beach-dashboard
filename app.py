import streamlit as st

# Page Configuration for Mobile and Desktop layouts
st.set_page_config(
    page_title="Kohler-Andrae South Beach Monitor",
    page_icon="🏖️",
    layout="wide"
)

LAT = 43.5956
LON = -87.7500  # Shifted slightly offshore into open water for marine models

# Title Header Configuration
st.title("🏖️ Kohler-Andrae Beach Monitor & Surf Panel")
st.caption(f"Custom client-side responsive tracking dashboard for coordinates: {LAT}, {LON}")
st.markdown("---")

# Row 1: The Reference Guidelines
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏊 Swimability & Exit Comfort Guide")
    st.markdown("""
    * **🟢 Favorable**: Warm air temperatures, low wind speeds, and onshore headings. Minimal body heat loss upon water exit.
    * **🟡 Brisk**: Surf conditions are safe, but active breezes will cause a swift chill the second you step out onto the sand.
    * **🔴 Polar**: Heavy risk of cold shock. Strong West/Northwest winds cause **Upwelling**, drawing freezing deep water to the shoreline.
    """)

with col2:
    st.subheader("🪰 Biting Black Fly Risk Index")
    st.markdown("""
    * **🟢 LOW RISK**: Robust onshore winds (East/Southeast) blowing flies away from the sand, or wind speeds exceeding **12 mph**.
    * **🟡 MODERATE**: Calm or stagnant air conditions. Keep bug spray handy.
    * **🔴 HIGH RISK**: Light or gentle offshore breeze (**West/Northwest winds at 4-11 mph**). This floats swarms out of the trees down onto the beach.
    """)

st.markdown("---")
st.subheader("📊 Live Hydrodynamic, Surf & Local Weather Station Data")
st.info("💡 **Dashboard Fix Applied:** This panel now utilizes direct data integration. If the widget below appears blank, make sure to temporarily pause any aggressive browser tracking shields or script blockers.")

# Injecting an unblockable, cross-origin safe frontend chart widget. 
# This runs locally via your own browser session, bypassing Streamlit cloud server blocks completely.
embed_html = f"""
<div style="width: 100%; height: 600px; overflow: hidden; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <iframe 
        src="https://windy.com{LAT}&lon={LON}"
        width="100%" 
        height="100%" 
        frameborder="0"
        style="border: none;">
    </iframe>
</div>
"""

# Render the frontend container
st.components.v1.html(embed_html, height=620)

st.markdown("---")
st.subheader("🛰️ Secondary Regional Thermal Map Loop")

# Updated, active NOAA CoastWatch satellite surface thermal map URL
noaa_image_url = "https://noaa.gov"

# Display the real-time thermal/wave gradient image directly on screen
st.image(
    noaa_image_url, 
    caption="Official NOAA CoastWatch Daily Great Lakes Surface Environmental Analysis (GLSEA)", 
    use_container_width=True
)
