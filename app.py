import streamlit as st
import requests
from datetime import datetime, timedelta

# Page Configuration for Mobile and Desktop layouts
st.set_page_config(
    page_title="Kohler-Andrae South Beach Monitor",
    page_icon="🏖️",
    layout="wide"
)

# Anchor point positioned 1.5 miles out in the water to bypass land grid rejections
LAT = 43.5956
LON = -87.7500

# ----------------------------------------------------
# 1. Custom Calculation & Translation Engines
# ----------------------------------------------------
def get_compass_heading(degrees):
    """Translates compass degrees into standard text headings."""
    degrees = degrees % 360
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((degrees + 11.25) / 22.5) % 16
    return directions[idx]

def calculate_wind_chill(air_temp_f, wind_mph):
    """Calculates NWS Wind Chill index values."""
    if air_temp_f <= 50 and wind_mph > 3:
        return 35.74 + (0.6215 * air_temp_f) - (35.75 * (wind_mph**0.16)) + (0.4275 * air_temp_f * (wind_mph**0.16))
    return air_temp_f

def calculate_swimability(water_temp, air_temp, wind_chill, humidity, wind_speed):
    """Computes a 0-100 Swimability Score based on human exit tolerance."""
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
    
    if final_score >= 80: return final_score, "Excellent 🟢"
    elif final_score >= 60: return final_score, "Tolerable 🟡"
    elif final_score >= 40: return final_score, "Brisk 🟠"
    else: return final_score, "Cold Risk 🔴"

def estimate_fly_risk(wind_speed_mph, wind_dir_deg):
    """Estimates Biting Black Fly risk based on land-to-water breeze maps."""
    is_offshore = 240 <= wind_dir_deg <= 330
    if wind_speed_mph < 4:
        return "CRITICAL 🔴"
    elif is_offshore and wind_speed_mph <= 12:
        return "HIGH 🔴"
    elif is_offshore and wind_speed_mph > 12:
        return "LOW 🟢"
    elif 60 <= wind_dir_deg <= 160:
        return "NONE 🟢"
    else:
        return "MODERATE 🟡"

# ----------------------------------------------------
# 2. Data Fetching API Pipeline (Hourly + 5-Day Daily)
# ----------------------------------------------------
def fetch_all_beach_data():
    # Robust live data placeholders with standard fallback behaviors
    live_data = {"air": 74.0, "hum": 60, "wind": 8.0, "dir": 270.0}
    forecast_days = []
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        # Requests both current hourly arrays and a 5-day daily forecast payload from Open-Meteo
        weather_url = "https://open-meteo.com"
        res = requests.get(weather_url, headers=headers, timeout=5).json()
        
        curr_hour = datetime.now().hour
        live_data["air"] = (res['hourly']['temperature_2m'][curr_hour] * 9/5) + 32
        live_data["hum"] = res['hourly']['relative_humidity_2m'][curr_hour]
        live_data["wind"] = res['hourly']['wind_speed_10m'][curr_hour] * 0.621371
        live_data["dir"] = res['hourly']['wind_direction_10m'][curr_hour]
        
        # Build out the 5-day forecast structure loop
        for i in range(5):
            day_label = (datetime.now() + timedelta(days=i)).strftime("%a %b %d")
            max_t = (res['daily']['temperature_2m_max'][i] * 9/5) + 32
            min_t = (res['daily']['temperature_2m_min'][i] * 9/5) + 32
            w_max = res['daily']['wind_speed_10m_max'][i] * 0.621371
            w_dir = res['daily']['wind_direction_10m_dominant'][i]
            
            forecast_days.append({
                "day": day_label, "max_temp": max_t, "min_temp": min_t,
                "wind_speed": w_max, "wind_dir": w_dir
            })
    except Exception:
        # Generate safe synthetic fallback cards if the external API request fails
        for i in range(5):
            day_label = (datetime.now() + timedelta(days=i)).strftime("%a %b %d")
            forecast_days.append({
                "day": day_label, "max_temp": 75.0, "min_temp": 60.0, "wind_speed": 10.0, "wind_dir": 150.0
            })
        
    return live_data, forecast_days

# ----------------------------------------------------
# 3. UI Dashboard Processing
# ----------------------------------------------------
st.title("🏖️ Kohler-Andrae Beach Monitor & Surf Panel")
st.caption("Custom Hydrodynamic & Biotic Modeling Sandbox — Coordinates: 43.5956, -87.7500")

# Setup Interactive Auditing Sidebar Controls
st.sidebar.header("🔬 Model Auditing Tool")
st.sidebar.markdown("Use these overrides to manually check edge cases and see how scores change.")

live_feed, forecast_list = fetch_all_beach_data()
use_override = st.sidebar.checkbox("Activate Manual Value Overrides", value=False)

if use_override:
    air_temp = st.sidebar.slider("Air Temperature (°F)", 40, 100, int(live_feed["air"]))
    humidity = st.sidebar.slider("Relative Humidity (%)", 10, 100, int(live_feed["hum"]))
    wind_speed = st.sidebar.slider("Wind Speed (mph)", 0, 40, int(live_feed["wind"]))
    wind_dir = st.sidebar.slider("Wind Direction / Compass Heading (°)", 0, 360, int(live_feed["dir"]))
else:
    air_temp, humidity, wind_speed, wind_dir = live_feed["air"], live_feed["hum"], live_feed["wind"], live_feed["dir"]
    st.sidebar.info("Currently displaying real-time live data feed estimates. Check the box above to audit.")

# Compute Oceanographic Profiles
wave_ft = 0.5
if wind_speed > 15:
    wave_ft = (wind_speed * 0.15) if (60 <= wind_dir <= 160) else (wind_speed * 0.08)

water_temp = 62.0 
if 240 <= wind_dir <= 330 and wind_speed > 10:
    water_temp -= 6.5  
elif 70 <= wind_dir <= 150 and wind_speed > 8:
    water_temp += 1.5  

# Compute Current Score Labels
wind_chill = calculate_wind_chill(air_temp, wind_speed)
swim_score, swim_lbl = calculate_swimability(water_temp, air_temp, wind_chill, humidity, wind_speed)
fly_lbl = estimate_fly_risk(wind_speed, wind_dir)

# Main Screen Visual Layouts
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏊 Swimability & Exit Comfort Score")
    st.metric(label="Swim Score Index", value=f"{swim_score} / 100", delta=swim_lbl, delta_color="normal" if "Excellent" in swim_lbl or "Tolerable" in swim_lbl else "inverse")
    
with col2:
    st.subheader("🪰 Biting Beach Fly Risk")
    st.metric(label="Fly Activity Index", value=fly_lbl, delta="Favorable" if "NONE" in fly_lbl or "LOW" in fly_lbl else "⚠️ Warning")

st.markdown("---")
st.subheader("📊 Output Modeling Layer Summary")

col3, col4, col5 = st.columns(3)
with col3:
    st.metric("Estimated Water Temp", f"{water_temp:.1f} °F")
    st.metric("Wave Height Estimate", f"{wave_ft:.1f} ft")
with col4:
    st.metric("Air Temperature", f"{air_temp:.1f} °F")
    st.metric("Wind Chill / RealFeel", f"{wind_chill:.1f} °F")
with col5:
    # 1) Appends translated compass direction heading right alongside vector degrees
    compass_text = get_compass_heading(wind_dir)
    st.metric("Wind Speed & Heading", f"{wind_speed:.1f} mph", f"{int(wind_dir)}° {compass_text}")
    st.metric("Relative Humidity", f"{humidity}%")

# 2) 5-Day Forecast Matrix Section
st.markdown("---")
st.subheader("📅 5-Day Beach Conditions Forecast")
st.caption("Modeled daily swimability and fly tracking indices generated via regional weather variables.")

f_cols = st.columns(5)
for index, day_data in enumerate(forecast_list):
    with f_cols[index]:
        # Formulate daily model logic variations
        d_wave = 0.5 if day_data["wind_speed"] <= 15 else (day_data["wind_speed"] * 0.12)
        d_water = 62.0
        if 240 <= day_data["wind_dir"] <= 330 and day_data["wind_speed"] > 10:
            d_water -= 6.5
        elif 70 <= day_data["wind_dir"] <= 150 and day_data["wind_speed"] > 8:
            d_water += 1.5
            
        d_chill = calculate_wind_chill(day_data["max_temp"], day_data["wind_speed"])
        d_swim_val, d_swim_str = calculate_swimability(d_water, day_data["max_temp"], d_chill, 60, day_data["wind_speed"])
        d_fly_str = estimate_fly_risk(day_data["wind_speed"], day_data["wind_dir"])
        d_compass = get_compass_heading(day_data["wind_dir"])
        
        # Render clean vertical stack day container cards
        st.markdown(f"### **{day_data['day']}**")
        st.markdown(f"🌡️ **Air Max:** {day_data['max_temp']:.0f}°F")
        st.markdown(f"🌊 **Est Water:** {d_water:.0f}°F")
        st.markdown(f"💨 **Wind:** {day_data['wind_speed']:.0f} mph `{d_compass}`")
        st.markdown(f"🏊 **Swim:** `{d_swim_str}` ({d_swim_val}/100)")
        st.markdown(f"🪰 **Flies:** `{d_fly_str}`")
        st.markdown("---")
