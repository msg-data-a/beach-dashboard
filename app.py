import streamlit as st
import requests
from datetime import datetime

# Page Configuration for Mobile and Desktop layouts
st.set_page_config(
    page_title="Kohler-Andrae South Beach Monitor",
    page_icon="🏖️",
    layout="wide"
)

# ----------------------------------------------------
# 1. Custom Calculation Engines
# ----------------------------------------------------
def calculate_wind_chill(air_temp_f, wind_mph):
    if air_temp_f <= 50 and wind_mph > 3:
        return 35.74 + (0.6215 * air_temp_f) - (35.75 * (wind_mph**0.16)) + (0.4275 * air_temp_f * (wind_mph**0.16))
    return air_temp_f

def calculate_swimability(water_temp, air_temp, wind_chill, humidity, wind_speed):
    if water_temp >= 72: water_score = 100
    elif water_temp >= 65: water_score = 85
    elif water_temp >= 60: water_score = 65
    elif water_temp >= 55: water_score = 40
    else: water_score = 10
    
    if wind_chill >= 80: air_score = 100
    elif wind_chill >= 70: air_score = 90
    elif wind_chill >= 60: air_score = 70
    elif wind_chill >= 50: air_score = 45
    else: air_score = 15
    
    wind_penalty = min(wind_speed * 1.5, 20)
    raw_score = (water_score * 0.45) + (air_score * 0.45) + 10 - wind_penalty
    final_score = max(0, min(100, int(raw_score)))
    
    if final_score >= 80: return final_score, "Excellent 🟢", "Perfect day. Warm water, calm air, and minimal exit chill."
    elif final_score >= 60: return final_score, "Tolerable 🟡", "Good swimming, but expect a brisk chill the moment you step out."
    elif final_score >= 40: return final_score, "Brisk / Polar 🟠", "Wetsuit recommended. Active upwelling or high winds make it cold."
    else: return final_score, "Hazardous / Cold 🔴", "High risk of cold shock or miserable exit conditions."

def estimate_fly_risk(wind_speed_mph, wind_dir_deg):
    is_offshore = 240 <= wind_dir_deg <= 330
    if wind_speed_mph < 4:
        return "CRITICAL 🔴", "No wind to keep them down. Flies can swarm from any direction."
    elif is_offshore and wind_speed_mph <= 12:
        return "HIGH 🔴", "Gentle offshore breeze is actively carrying biting flies out of the woods onto the beach."
    elif is_offshore and wind_speed_mph > 12:
        return "LOW 🟢", "Offshore wind is present, but it is too strong for flies to maintain flight."
    elif 60 <= wind_dir_deg <= 160:
        return "NONE 🟢", "Onshore lake breeze is blowing them away from the beach into the trees."
    else:
        return "MODERATE 🟡", "Keep bug spray handy. Winds allow minor movement."

# ----------------------------------------------------
# 2. Data Fetching API Pipeline
# ----------------------------------------------------
@st.cache_data(ttl=900)
def fetch_all_beach_data():
    # Flattened strings with fixed coordinates to prevent string interpretation errors
    marine_url = "https://open-meteo.com"
    weather_url = "https://open-meteo.com"
    
    m_res = requests.get(marine_url).json()
    w_res = requests.get(weather_url).json()
    
    curr_hour = datetime.now().hour
    
    air_temp_f = (w_res['hourly']['temperature_2m'][curr_hour] * 9/5) + 32
    humidity = w_res['hourly']['relative_humidity_2m'][curr_hour]
    wind_mph = w_res['hourly']['wind_speed_10m'][curr_hour] * 0.621371
    wind_dir = w_res['hourly']['wind_direction_10m'][curr_hour]
    
    wave_ft = m_res['hourly']['wave_height'][curr_hour] * 3.28084
    wave_period = m_res['hourly']['wave_period'][curr_hour]
    
    sst_f = 62.0 
    if 240 <= wind_dir <= 330 and wind_mph > 10:
        sst_f -= 6.0  
    elif 70 <= wind_dir <= 150 and wind_mph > 8:
        sst_f += 2.0  
        
    return air_temp_f, humidity, wind_mph, wind_dir, wave_ft, wave_period, sst_f

# ----------------------------------------------------
# 3. UI Dashboard Rendering
# ----------------------------------------------------
try:
    air_temp, humidity, wind_speed, wind_dir, wave_ft, wave_period, water_temp = fetch_all_beach_data()
    wind_chill = calculate_wind_chill(air_temp, wind_speed)
    swim_score, swim_lbl, swim_desc = calculate_swimability(water_temp, air_temp, wind_chill, humidity, wind_speed)
    fly_lbl, fly_desc = estimate_fly_risk(wind_speed, wind_dir)

    st.title("🏖️ Kohler-Andrae Beach Monitor & Surf Panel")
    st.caption("Live hydrodynamic monitoring dashboard targeting beach coordinates: 43.595644, -87.768558")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏊 Swimability & Exit Comfort Score")
        st.metric(label="Swim Score Index", value=f"{swim_score} / 100", delta=swim_lbl, delta_color="normal" if "Excellent" in swim_lbl or "Tolerable" in swim_lbl else "inverse")
        st.info(f"**Condition Context:** {swim_desc}")
        
    with col2:
        st.subheader("🪰 Biting Beach Fly Risk")
        st.metric(label="Fly Activity Index", value=fly_lbl, delta="Favorable" if "NONE" in fly_lbl or "LOW" in fly_lbl else "⚠️ Warning")
        st.warning(f"**Biotic Factor:** {fly_desc}")

    st.markdown("---")
    st.subheader("🌊 Current Surf & Water Conditions")
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("Estimated Nearshore Temp", f"{water_temp:.1f} °F")
    with col4:
        st.metric("Wave Height", f"{wave_ft:.1f} ft")
    with col5:
        st.metric("Wave Interval/Period", f"{wave_period} sec")

    st.markdown("---")
    st.subheader("🌤️ Beach Atmospheric Conditions")
    col6, col7, col8, col9 = st.columns(4)
    with col6:
        st.metric("Air Temperature", f"{air_temp:.1f} °F")
    with col7:
        st.metric("Wind Chill / RealFeel", f"{wind_chill:.1f} °F")
    with col8:
        st.metric("Wind Speed & Heading", f"{wind_speed:.1f} mph", f"{int(wind_dir)}° Vector")
    with col9:
        st.metric("Relative Humidity", f"{humidity}%")

except Exception as e:
    st.error(f"Could not load live dashboard data layers: {e}")

st.markdown("---")
st.subheader("Satellites & Secondary Regional Monitoring Maps")
noaa_image_url = "https://noaa.gov"
st.image(noaa_image_url, caption="Official NOAA Lake Michigan Sea Surface Temperature Thermal Grid Loop", use_container_width=True)
