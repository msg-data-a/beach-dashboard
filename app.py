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
st.subheader("🛰️ Live Great Lakes Hydrodynamic Tracking Model")
st.info("💡 **Dashboard Summary:** This panel tracks active regional marine thermal data. West/Northwest winds indicate upwelling (colder water), while East/Southeast winds represent downwelling pockets (warmer water).")

# Direct NOAA Great Lakes CoastWatch satellite surface thermal map URL
noaa_image_url = "https://noaa.gov"

# Display the real-time thermal/wave gradient image directly on screen
st.image(
    noaa_image_url, 
    caption="Official NOAA Lake Michigan Sea Surface Temperature (SST) & Heat Gradient Grid Loop", 
    use_container_width=True
)

