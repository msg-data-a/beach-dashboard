import streamlit as st
import requests
from datetime import datetime, timedelta

# Page Setup
st.set_page_config(
    page_title="Kohler-Andrae South Beach Monitor",
    page_icon="🏖️",
    layout="wide"
)

LAT = 43.5956
LON = -87.7500

# ----------------------------------------------------
# 1. Custom Calculation Engines
# ----------------------------------------------------
def get_compass_heading(degrees):
    degrees = degrees % 360
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return directions[int((degrees + 11.25) / 22.5) % 16]

def calculate_wind_chill(air_temp_f, wind_mph):
    if air_temp_f <= 50 and wind_mph > 3:
        return 35.74 + (0.6215 * air_temp_f) - (35.75 * (wind_mph**0.16)) + (0.4275 * air_temp_f * (wind_mph**0.16))
    return air_temp_f

def calculate_swimability(water_temp, air_temp, wind_chill, humidity, wind_speed):
    w_score = 100 if water_temp >= 72 else (85 if water_temp >= 65 else (65 if water_temp >= 60 else (40 if water_temp >= 55 else 10)))
    a_score = 100 if wind_chill >= 80 else (90 if wind_chill >= 70 else (70 if wind_chill >= 60 else (45 if wind_chill >= 50 else 15)))
    w_penalty = min(wind_speed * 1.5, 20)
    final_score = max(0, min(100, int((w_score * 0.45) + (a_score * 0.45) + 10 - w_penalty)))
    
    if final_score >= 80: return final_score, "Excellent 🟢", "Warm water/air. Easy exit."
    elif final_score >= 60: return final_score, "Tolerable 🟡", "Refreshing water. Brisk exit chill."
    elif final_score >= 40: return final_score, "Brisk 🟠", "Wetsuit advised. High thermal loss."
    else: return final_score, "Cold Risk 🔴", "Cold shock danger."

def estimate_fly_risk(wind_speed_mph, wind_dir_deg):
    is_offshore = 240 <= wind_dir_deg <= 330
    if wind_speed_mph < 4: return "CRITICAL 🔴", "Stagnant air lets swarms group."
    elif is_offshore and wind_speed_mph <= 12: return "HIGH 🔴", "West breeze blows pests to sand."
    elif is_offshore and wind_speed_mph > 12: return "LOW 🟢", "Wind too fast for stable flight."
    elif 60 <= wind_dir_deg <= 160: return "NONE 🟢", "Onshore breeze pins swarms inland."
    else: return "MODERATE 🟡", "Variable winds. Pack spray."

# ----------------------------------------------------
# 2. Data Fetching API Pipeline
# ----------------------------------------------------
def fetch_all_beach_data():
    live_data = {"air": 74.0, "hum": 60, "wind": 8.0, "dir": 270.0}
    forecast_days = []
    
    try:
        url = "https://open-meteo.com"
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5).json()
        h_idx = datetime.now().hour
        
        live_data["air"] = (res['hourly']['temperature_2m'][h_idx] * 9/5) + 32
        live_data["hum"] = res['hourly']['relative_humidity_2m'][h_idx]
        live_data["wind"] = res['hourly']['wind_speed_10m'][h_idx] * 0.621371
        live_data["dir"] = res['hourly']['wind_direction_10m'][h_idx]
        
        for i in range(5):
            lbl = (datetime.now() + timedelta(days=i)).strftime("%a %b %d")
            forecast_days.append({
                "day": lbl,
                "max_temp": (res['daily']['temperature_2m_max'][i] * 9/5) + 32,
                "min_temp": (res['daily']['temperature_2m_min'][i] * 9/5) + 32,
                "wind_speed": res['daily']['wind_speed_10m_max'][i] * 0.621371,
                "wind_dir": res['daily']['wind_direction_10m_dominant'][i]
            })
    except Exception:
        for i in range(5):
            lbl = (datetime.now() + timedelta(days=i)).strftime("%a %b %d")
            forecast_days.append({"day": lbl, "max_temp": 72.0+(i*2), "min_temp": 60.0, "wind_speed": 6.0+(i*1.5), "wind_dir": 120.0+(i*45)})
        
    return live_data, forecast_days

# ----------------------------------------------------
# 3. UI Dashboard Processing
# ----------------------------------------------------
st.title("🏖️ Kohler-Andrae Beach Monitor & Surf Panel")
st.caption("Coordinates: 43.5956, -87.7500")

live_feed, forecast_list = fetch_all_beach_data()
st.sidebar.header("🔬 Model Auditing Tool")
use_override = st.sidebar.checkbox("Activate Manual Overrides", value=False)

if use_override:
    air_temp = st.sidebar.slider("Air Temp (°F)", 40, 100, int(live_feed["air"]))
    humidity = st.sidebar.slider("Humidity (%)", 10, 100, int(live_feed["hum"]))
    wind_speed = st.sidebar.slider("Wind Speed (mph)", 0, 40, int(live_feed["wind"]))
    wind_dir = st.sidebar.slider("Wind Direction (°)", 0, 360, int(live_feed["dir"]))
else:
    air_temp, humidity, wind_speed, wind_dir = live_feed["air"], live_feed["hum"], live_feed["wind"], live_feed["dir"]

wave_ft = 0.5 if wind_speed <= 15 else ((wind_speed * 0.15) if (60 <= wind_dir <= 160) else (wind_speed * 0.08))
water_temp = 62.0 - (6.5 if (240 <= wind_dir <= 330 and wind_speed > 10) else (-1.5 if (70 <= wind_dir <= 150 and wind_speed > 8) else 0.0))

wind_chill = calculate_wind_chill(air_temp, wind_speed)
swim_score, swim_lbl, swim_desc = calculate_swimability(water_temp, air_temp, wind_chill, humidity, wind_speed)
fly_lbl, fly_desc = estimate_fly_risk(wind_speed, wind_dir)

st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.subheader("🏊 Swimability & Exit Score")
    st.metric("Swim Score Index", f"{swim_score} / 100", swim_lbl, delta_color="normal" if "Excel" in swim_lbl or "Toler" in swim_lbl else "inverse")
    st.info(f"**Rationale:** {swim_desc}")
with c2:
    st.subheader("🪰 Biting Beach Fly Risk")
    st.metric("Fly Activity Index", fly_lbl, delta="Warning" if "CRIT" in fly_lbl or "HIGH" in fly_lbl else "Favorable")
    st.warning(f"**Rationale:** {fly_desc}")

st.markdown("---")
st.subheader("📊 Output Modeling Layer Summary")
c3, c4, c5 = st.columns(3)
with c3:
    st.metric("Est. Water Temp", f"{water_temp:.1f} °F")
    st.metric("Wave Height Estimate", f"{wave_ft:.1f} ft")
with c4:
    st.metric("Air Temperature", f"{air_temp:.1f} °F")
    st.metric("Wind Chill / RealFeel", f"{wind_chill:.1f} °F")
with c5:
    st.metric("Wind Speed & Heading", f"{wind_speed:.1f} mph", f"{int(wind_dir)}° {get_compass_heading(wind_dir)}")
    st.metric("Relative Humidity", f"{humidity}%")

st.markdown("---")
st.subheader("📅 5-Day Beach Conditions Forecast")
f_cols = st.columns(5)
for index, day_data in enumerate(forecast_list):
    with f_cols[index]:
        d_wave = 0.5 if day_data["wind_speed"] <= 15 else (day_data["wind_speed"] * 0.12)
        d_water = 62.0 - (6.5 if (240 <= day_data["wind_dir"] <= 330 and day_data["wind_speed"] > 10) else (-1.5 if (70 <= day_data["wind_dir"] <= 150 and day_data["wind_speed"] > 8) else 0.0))
        d_chill = calculate_wind_chill(day_data["max_temp"], day_data["wind_speed"])
        ds_val, ds_str, ds_reason = calculate_swimability(d_water, day_data["max_temp"], d_chill, 60, day_data["wind_speed"])
        df_str, df_reason = estimate_fly_risk(day_data["wind_speed"], day_data["wind_dir"])
        
        st.markdown(f"### **{day_data['day']}**")
        st.markdown(f"🌡️ **Air Max:** {day_data['max_temp']:.0f}°F")
        st.markdown(f"🌊 **Est Water:** {d_water:.0f}°F")
        st.markdown(f"💨 **Wind:** {day_data['wind_speed']:.0f} mph `{get_compass_heading(day_data['wind_dir'])}`")
        st.markdown(f"🏊 **Swim:** `{ds_str}` ({ds_val}/100)")
        st.caption(f"_{ds_reason}_")
        st.markdown(f"🪰 **Flies:** `{df_str}`")
        st.caption(f"_{df_reason}_")
        st.markdown("---")
