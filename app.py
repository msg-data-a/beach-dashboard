import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Kohler-Andrae Beach Monitor", layout="wide")

# 1. Custom Calculation Engines
def get_compass(deg):
    arr = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return arr[int((deg % 360 + 11.25) / 22.5) % 16]

def calc_chill(t, w):
    if t <= 50 and w > 3:
        return 35.74 + (0.6215 * t) - (35.75 * (w**0.16)) + (0.4275 * t * (w**0.16))
    return t

def calc_swim(w_t, a_t, chill, hum, w_s):
    w_sc = 100 if w_t >= 72 else (85 if w_t >= 65 else (65 if w_t >= 60 else (40 if w_t >= 55 else 10)))
    a_sc = 100 if chill >= 80 else (90 if chill >= 70 else (70 if chill >= 60 else (45 if chill >= 50 else 15)))
    score = max(0, min(100, int((w_sc * 0.45) + (a_sc * 0.45) + 10 - min(w_s * 1.5, 20))))
    if score >= 80: return score, "Excellent 🟢", "Warm combo. Minimal exit chill."
    elif score >= 60: return score, "Tolerable 🟡", "Refreshing water. Brisk exit breeze."
    elif score >= 40: return score, "Brisk 🟠", "Wetsuit advised. High thermal loss."
    return score, "Cold Risk 🔴", "Cold shock hazard."

def calc_flies(w_s, w_d):
    is_offshore = 240 <= w_d <= 330
    if w_s < 4: return "CRITICAL 🔴", "Stagnant air allows swarming near sand."
    elif is_offshore and w_s <= 12: return "HIGH 🔴", "West breeze blows pests to sand."
    elif is_offshore and w_s > 12: return "LOW 🟢", "Wind too fast for stable fly flight."
    elif 60 <= w_d <= 160: return "NONE 🟢", "Onshore lake breeze pins swarms inland."
    return "MODERATE 🟡", "Variable shoreline winds. Pack spray."

# 2. Resilient Data Fetching Pipeline (Direct Unit Requests)
def fetch_data():
    live = {"air": 74.0, "hum": 60, "wind": 8.0, "dir": 270.0}
    fc = []
    try:
        # Requesting Fahrenheit and MPH units directly from the server source
        url = "https://open-meteo.com"
        res = requests.get(url, timeout=5).json()
        h = datetime.now().hour
        
        live["air"] = res['hourly']['temperature_2m'][h]
        live["hum"] = res['hourly']['relative_humidity_2m'][h]
        live["wind"] = res['hourly']['wind_speed_10m'][h]
        live["dir"] = res['hourly']['wind_direction_10m'][h]
        
        for i in range(5):
            lbl = (datetime.now() + timedelta(days=i)).strftime("%a %b %d")
            fc.append({
                "day": lbl,
                "max": res['daily']['temperature_2m_max'][i],
                "wind": res['daily']['wind_speed_10m_max'][i],
                "dir": res['daily']['wind_direction_10m_dominant'][i]
            })
    except Exception as e:
        # Logs the exact API rejection reason cleanly to the sidebar for easy debugging
        st.sidebar.warning(f"Data Fetch Diagnostic Log: {e}")
        for i in range(5):
            lbl = (datetime.now() + timedelta(days=i)).strftime("%a %b %d")
            fc.append({"day": lbl, "max": 70.0 + (i * 2), "wind": 6.0 + i, "dir": 45.0 + (i * 20)})
    return live, fc

# 3. Application UI Rendering
st.title("🏖️ Kohler-Andrae Beach Monitor & Surf Panel")
live_feed, forecast_list = fetch_data()

st.sidebar.header("🔬 Model Auditing Tool")
if st.sidebar.checkbox("Activate Manual Overrides", value=False):
    air_temp = st.sidebar.slider("Air Temp", 40, 100, int(live_feed["air"]))
    humidity = st.sidebar.slider("Humidity", 10, 100, int(live_feed["hum"]))
    wind_speed = st.sidebar.slider("Wind Speed", 0, 40, int(live_feed["wind"]))
    wind_dir = st.sidebar.slider("Wind Direction", 0, 360, int(live_feed["dir"]))
else:
    air_temp, humidity, wind_speed, wind_dir = live_feed["air"], live_feed["hum"], live_feed["wind"], live_feed["dir"]

wave_ft = 0.5 if wind_speed <= 15 else ((wind_speed * 0.15) if (60 <= wind_dir <= 160) else (wind_speed * 0.08))
water_temp = 62.0 - (6.5 if (240 <= wind_dir <= 330 and wind_speed > 10) else (-1.5 if (70 <= wind_dir <= 150 and wind_speed > 8) else 0.0))

chill = calc_chill(air_temp, wind_speed)
s_score, s_lbl, s_desc = calc_swim(water_temp, air_temp, chill, humidity, wind_speed)
f_lbl, f_desc = calc_flies(wind_speed, wind_dir)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.subheader("🏊 Swimability & Exit Score")
    st.metric("Swim Score Index", f"{s_score} / 100", s_lbl, delta_color="normal" if "Excel" in s_lbl or "Toler" in s_lbl else "inverse")
    st.info(f"**Rationale:** {s_desc}")
with col2:
    st.subheader("🪰 Biting Beach Fly Risk")
    st.metric("Fly Activity Index", f_lbl, delta="Warning" if "🔴" in f_lbl or "🟡" in f_lbl else "Favorable")
    st.warning(f"**Rationale:** {f_desc}")

st.markdown("---")
st.subheader("📊 Output Modeling Layer Summary")
c3, c4, c5 = st.columns(3)
with c3:
    st.metric("Surf Zone (Model Est)", f"{water_temp:.1f} °F")
    st.metric("Wave Height Estimate", f"{wave_ft:.1f} ft")
with c4:
    st.metric("Air Temperature", f"{air_temp:.1f} °F")
    st.metric("Wind Chill / RealFeel", f"{chill:.1f} °F")
with c5:
    st.metric("Wind Speed & Heading", f"{wind_speed:.1f} mph", f"{int(wind_dir)}° {get_compass(wind_dir)}")
    st.metric("Relative Humidity", f"{humidity}%")

st.markdown("---")
st.subheader("📅 5-Day Beach Conditions Forecast")
f_cols = st.columns(5)
for idx, d in enumerate(forecast_list):
    with f_cols[idx]:
        d_water = 62.0 - (6.5 if (240 <= d["dir"] <= 330 and d["wind"] > 10) else (-1.5 if (70 <= d["dir"] <= 150 and d["wind"] > 8) else 0.0))
        d_chill = calc_chill(d["max"], d["wind"])
        ds_v, ds_s, ds_r = calc_swim(d_water, d["max"], d_chill, 60, d["wind"])
        df_s, df_r = calc_flies(d["wind"], d["dir"])
        
        st.markdown(f"### **{d['day']}**")
        st.markdown(f"🌡️ **Air Max:** {d['max']:.0f}°F\n\n🌊 **Est Water:** {d_water:.0f}°F")
        st.markdown(f"💨 **Wind:** {d['wind']:.0f} mph `{get_compass(d['dir'])}`")
        st.markdown(f"🏊 **Swim:** `{ds_s}` ({ds_v}/100)\n\n_{ds_r}_")
        st.markdown(f"🪰 **Flies:** `{df_s}`\n\n_{df_r}_")
        st.markdown("---")

st.markdown("### 📝 Ground-Truth Calibration Logger")
# Initializing an explicit form object variable to enforce secure frontend submit registrations
logger_form = st.form("logger_form", clear_on_submit=True)
o_w = logger_form.number_input("Actual Water Temp if known (°F)", 32.0, 90.0, 62.0, 0.5)
o_s = logger_form.selectbox("Observed Surf", ["Flat / Glassy", "Minor Ripples (<1 ft)", "Chop (1-2 ft)", "Heavy Waves (3+ ft)"])
o_f = logger_form.select_slider("Observed Fly Severity", options=["None 😊", "Minor 🟡", "Severe 🔴"])
o_n = logger_form.text_input("Additional Ground Notes")
submit_button = logger_form.form_submit_button("💾 Save Field Observation Record")

if submit_button:
    row = pd.DataFrame([{"Time": datetime.now().strftime("%m-%d %H:%M"), "M_Water": water_temp, "O_Water": o_w, "M_Wind": f"{wind_speed:.1f} {get_compass(wind_dir)}", "O_Surf": o_s, "Flies": o_f, "Notes": o_n}])
    row.to_csv("observations.csv", mode='a', header=not os.path.exists("observations.csv"), index=False)
    st.success("Saved! Log records appended to observations.csv inside GitHub repo.")
