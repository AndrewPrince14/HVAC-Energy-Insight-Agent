import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os, time, base64, numpy as np
from datetime import datetime
from groq import Groq

from modules.data_loader import load_data
from modules.scenario_engine import apply_scenario, SCENARIO_DESCRIPTIONS
from modules.diagnostics import run_diagnostics
from modules.forecasting import run_forecasting
from modules.chiller_sequencing import run_chiller_sequencing
from modules.renewable import apply_renewable_offset
from modules.optimization import run_optimization
from modules.weather_api import get_weather
from dotenv import load_dotenv
load_dotenv()

# ── PAGE CONFIG ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Energy Insight AI Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── DARK INDUSTRIAL CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow', sans-serif;
    background-color: #0a0e1a;
    color: #c8d6e5;
}
.stApp { background-color: #0a0e1a; }

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a1628 100%);
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * { color: #8ab4d4 !important; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1117;
    border-bottom: 1px solid #1e3a5f;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #4a6fa5 !important;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    letter-spacing: 1px;
    border: 1px solid transparent;
    border-radius: 4px 4px 0 0;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: #0a1628 !important;
    color: #00d4ff !important;
    border-color: #1e3a5f !important;
    border-bottom-color: #0a1628 !important;
}

/* METRICS */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0d1b2a 0%, #0a1628 100%);
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 16px;
}
[data-testid="stMetricLabel"] { color: #4a6fa5 !important; font-size: 11px; letter-spacing: 1px; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #00d4ff !important; font-family: 'Share Tech Mono', monospace; font-size: 22px; }

/* HEADERS */
.main-title {
    font-size: 42px;
    font-weight: 800;
    letter-spacing: 2px;
    background: linear-gradient(90deg, #00d4ff, #0080ff, #7b2fff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.section-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    letter-spacing: 3px;
    color: #00d4ff;
    text-transform: uppercase;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 8px;
    margin: 24px 0 16px 0;
}
.subtitle { font-size: 13px; color: #4a6fa5; letter-spacing: 1px; }

/* SAVINGS BANNER */
.savings-banner {
    background: linear-gradient(135deg, #0d2137 0%, #0a1f35 50%, #071525 100%);
    border: 1px solid #00d4ff33;
    border-radius: 12px;
    padding: 20px 28px;
    margin: 16px 0;
    display: flex;
    gap: 40px;
    align-items: center;
}
.savings-item { text-align: center; }
.savings-value { font-family: 'Share Tech Mono', monospace; font-size: 28px; color: #00ff88; font-weight: bold; }
.savings-label { font-size: 11px; color: #4a6fa5; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px; }

/* SCENARIO BADGE */
.scenario-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    letter-spacing: 1px;
    margin-left: 8px;
}

/* CHAT */
.chat-wrapper {
    height: 500px;
    overflow-y: auto;
    padding: 20px;
    background: #060c18;
    border-radius: 12px;
    border: 1px solid #1e3a5f;
    display: flex;
    flex-direction: column;
    gap: 14px;
    margin-bottom: 16px;
}
.bubble-user {
    align-self: flex-end;
    background: linear-gradient(135deg, #0080ff, #0055cc);
    color: white;
    padding: 10px 16px;
    border-radius: 18px 18px 4px 18px;
    max-width: 72%;
    font-size: 14px;
    line-height: 1.6;
}
.bubble-ai {
    align-self: flex-start;
    background: linear-gradient(135deg, #0d1b2a, #0a1628);
    color: #c8d6e5;
    padding: 10px 16px;
    border-radius: 18px 18px 18px 4px;
    max-width: 72%;
    font-size: 14px;
    line-height: 1.6;
    border: 1px solid #1e3a5f;
}
.bubble-label { font-size: 11px; color: #4a6fa5; margin-bottom: 3px; font-family: 'Share Tech Mono', monospace; }
.bubble-label-right { text-align: right; }

/* RISK BADGE */
.risk-high { color: #ff4757; font-weight: bold; }
.risk-moderate { color: #ffa502; font-weight: bold; }
.risk-low { color: #2ed573; font-weight: bold; }

/* IMPACT TABLE */
.impact-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1e3a5f; }
.impact-label { color: #4a6fa5; font-size: 13px; }
.impact-value { color: #00d4ff; font-family: 'Share Tech Mono', monospace; font-size: 13px; }

/* SELECTBOX / BUTTONS */
.stSelectbox > div, .stButton > button {
    background: #0d1b2a !important;
    border-color: #1e3a5f !important;
    color: #8ab4d4 !important;
}
.stButton > button:hover { border-color: #00d4ff !important; color: #00d4ff !important; }

/* PROGRESS */
.stProgress > div > div { background: linear-gradient(90deg, #0080ff, #00d4ff); }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚡ SYSTEM CONTROL")
st.sidebar.markdown("---")

ALL_SCENARIOS = ["normal", "heatwave", "equipment_fault", "solar_boost", "night_mode", "monsoon", "maintenance_mode"]
scenario = st.sidebar.selectbox("SIMULATION SCENARIO", ALL_SCENARIOS,
    format_func=lambda x: x.replace("_", " ").upper())
st.sidebar.caption(SCENARIO_DESCRIPTIONS.get(scenario, ""))
st.sidebar.markdown("---")
horizon = int(st.sidebar.selectbox("FORECAST HORIZON", ["24", "48", "72", "168"], index=3))
st.sidebar.markdown("---")

# Report viewer
st.sidebar.markdown("### 📄 REPORTS")
reports = {
    "Normal": "reports/normal_report.html",
    "Heatwave": "reports/heatwave_report.html",
    "Equipment Fault": "reports/equipment_fault_report.html",
    "Solar Boost": "reports/solar_boost_report.html",
    "Comparison": "reports/scenario_comparison.html",
}
report_choice = st.sidebar.selectbox("SELECT REPORT", list(reports.keys()))
if st.sidebar.button("📂 VIEW REPORT"):
    rpath = reports[report_choice]
    if os.path.exists(rpath):
        with open(rpath, "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=1000, scrolling=True)
    else:
        st.sidebar.error("Report not found.")

# ── DATA PIPELINE ─────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_data()

df_raw = get_data()
if 'COP' in df_raw.columns:
    df_raw = df_raw.drop(columns=['COP'])

df = apply_scenario(df_raw, scenario)

try:
    weather = get_weather()
except Exception:
    weather = {"temperature": 28.0, "humidity": 65, "windspeed": 12}

diag = run_diagnostics(df)
anomalies      = diag["anomalies"]
root_cause     = diag["root_cause"]
maint_priority = diag["maintenance_priority"]
degradation    = diag["degradation_status"]
priority_score = diag["priority_score"]
anomaly_ratio  = diag["anomaly_ratio"]
anomaly_desc   = diag["anomaly_description"]

@st.cache_data
def get_forecast(scenario, horizon):
    df_s = apply_scenario(get_data(), scenario)
    return run_forecasting(df_s, horizon)

fc_result = get_forecast(scenario, horizon)
future_pred    = fc_result["future_prediction"]
upper_band     = fc_result["upper_band"]
lower_band     = fc_result["lower_band"]
pred_peak      = fc_result["predicted_peak"]
hist_peak      = fc_result["historical_peak"]
peak_risk      = fc_result["peak_risk"]
mae            = fc_result["mae"]
accuracy_pct   = fc_result["accuracy_pct"]
shap_importance = fc_result.get("shap_importance", {})

if weather['temperature'] > 32.0:
    future_pred = [v * 1.05 for v in future_pred]
    pred_peak = max(future_pred)

future_pred, solar_generated = apply_renewable_offset(future_pred, horizon)
pred_avg = float(np.mean(future_pred))

seq = run_chiller_sequencing(pred_peak, pred_avg, scenario)
chillers_req   = seq["chillers_required"]
opt_cop        = seq["optimized_cop"]
load_per_ch    = seq["load_per_chiller"]
loading_ratio  = seq["loading_ratio"]
load_status    = seq["load_status"]
seq_summary    = f"{chillers_req} chillers | COP {opt_cop} | {loading_ratio}% load each"

opt_recs = run_optimization(pred_avg, df["kWh"].mean(), pred_peak, hist_peak,
                             peak_risk, maint_priority, df, horizon)

# ── IMPACT CALCULATIONS ───────────────────────────────────────────────
baseline_kwh   = df_raw["kWh"].mean() * horizon
current_kwh    = pred_avg * horizon
kwh_saved      = max(baseline_kwh - current_kwh + solar_generated, 0)
cost_saved     = round(kwh_saved * 8.0, 2)
co2_saved      = round(kwh_saved * 0.82, 2)
solar_pct      = round((solar_generated / max(current_kwh, 1)) * 100, 1)

# ── HEADER ────────────────────────────────────────────────────────────
st.markdown("<div class='main-title'>ENERGY INSIGHT AI AGENT</div>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>Central IT Park, Chennai &nbsp;|&nbsp; {scenario.replace('_',' ').upper()} &nbsp;|&nbsp; {horizon}h Forecast &nbsp;|&nbsp; {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

# ── SAVINGS BANNER ────────────────────────────────────────────────────
st.markdown("<div class='section-title'>⚡ ESTIMATED IMPACT — CURRENT SCENARIO</div>", unsafe_allow_html=True)
b1, b2, b3, b4, b5 = st.columns(5)
b1.metric("💰 Cost Savings", f"₹{cost_saved:,.0f}", delta="vs baseline")
b2.metric("⚡ Grid Energy Saved", f"{kwh_saved:,.0f} kWh")
b3.metric("🌿 CO₂ Avoided", f"{co2_saved:,.0f} kg")
b4.metric("☀️ Solar Coverage", f"{solar_pct}%")
b5.metric("🎯 Forecast Accuracy", f"{accuracy_pct}%")
st.divider()

# ── GROQ CLIENT ───────────────────────────────────────────────────────
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ── TABS ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 DASHBOARD", "📡 LIVE STREAM", "⚙️ OPTIMIZATION",
    "🔍 DIAGNOSTICS", "💬 AI ASSISTANT", "📈 IMPACT SUMMARY"
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    st.markdown("<div class='section-title'>🌍 LIVE OUTDOOR CONDITIONS (Open-Meteo API — Chennai)</div>", unsafe_allow_html=True)
    w1, w2, w3, w4 = st.columns(4)
    w1.metric("Outdoor Temp", f"{weather['temperature']} °C")
    w2.metric("Humidity", f"{weather['humidity']} %")
    w3.metric("Wind Speed", f"{weather['windspeed']} km/h")
    w4.metric("Thermal Stress", "HIGH ⚠️" if weather['temperature'] > 32 else "Normal ✅")

    st.markdown("<div class='section-title'>🏭 SCENARIO-ADJUSTED FACILITY CONDITIONS</div>", unsafe_allow_html=True)
    wbt_val = round(df['WBT'].mean(), 1) if 'WBT' in df.columns else "N/A"
    facility_temp = round(df['Ambient_Temp'].mean(), 1)
    facility_humidity = round(df['Humidity'].mean(), 1)
    baseline_temp = round(df_raw['Ambient_Temp'].mean(), 1)
    baseline_humidity = round(df_raw['Humidity'].mean(), 1)
    temp_delta = round(facility_temp - baseline_temp, 1)
    hum_delta = round(facility_humidity - baseline_humidity, 1)
    f1, f2, f3, f4, f5 = st.columns(5)
    f1.metric("Facility Temp", f"{facility_temp} °C", delta=f"{temp_delta:+.1f}°C vs baseline")
    f2.metric("Facility Humidity", f"{facility_humidity} %", delta=f"{hum_delta:+.1f}% vs baseline")
    f3.metric("Wet Bulb Temp", f"{wbt_val} °C")
    f4.metric("Avg Occupancy", f"{int(df['Occupancy'].mean())} pax")
    f5.metric("Scenario", scenario.replace("_"," ").upper())

    st.markdown("<div class='section-title'>FACILITY PERFORMANCE</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Avg Load", f"{df['kWh'].mean():.1f} kWh")
    c2.metric("Predicted Peak", f"{pred_peak:.1f} kWh")
    avg_eff_val = df['iKW-TR'].mean()
    eff_status = "🔴 CRITICAL" if avg_eff_val > 0.75 else "🟡 WARNING" if avg_eff_val > 0.65 else "🟢 HEALTHY"
    c3.metric("iKW-TR Efficiency", f"{avg_eff_val:.3f}", delta=eff_status)
    c4.metric("Peak Risk", peak_risk)
    c5.metric("Forecast MAE", f"{mae:.1f} kWh")

    st.markdown(f"<div class='section-title'>{horizon}-HOUR PREDICTIVE FORECAST</div>", unsafe_allow_html=True)
    hours = list(range(len(future_pred)))
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(
        x=hours + hours[::-1],
        y=upper_band + lower_band[::-1],
        fill='toself',
        fillcolor='rgba(0,128,255,0.10)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Confidence Band'
    ))
    fig_forecast.add_trace(go.Scatter(
        x=hours, y=future_pred,
        line=dict(color='#00d4ff', width=2),
        name='Predicted Load'
    ))
    fig_forecast.update_layout(
        template='plotly_dark', paper_bgcolor='#0a0e1a', plot_bgcolor='#0d1b2a',
        margin=dict(l=0, r=0, t=30, b=0), height=300,
        legend=dict(orientation="h", y=1.1),
        xaxis_title=f"Hour (next {horizon}h)", yaxis_title="kWh"
    )
    st.plotly_chart(fig_forecast, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        fig_hist = px.line(df, x="Timestamp", y="kWh", title="Historical Energy Profile",
                           color_discrete_sequence=['#00ff88'])
        fig_hist.update_layout(template='plotly_dark', paper_bgcolor='#0a0e1a', plot_bgcolor='#0d1b2a', height=250, margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig_hist, use_container_width=True)
    with col_b:
        fig_temp = px.line(df, x="Timestamp", y="Ambient_Temp", title="Ambient Temperature (°C)",
                           color_discrete_sequence=['#ff4757'])
        fig_temp.update_layout(template='plotly_dark', paper_bgcolor='#0a0e1a', plot_bgcolor='#0d1b2a', height=250, margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig_temp, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    st.markdown("<div class='section-title'>REAL-TIME BMS TELEMETRY STREAM</div>", unsafe_allow_html=True)
    if st.button("▶ INITIALIZE LIVE STREAM", type="primary"):
        placeholder = st.empty()
        stream_data = []
        live_df = df.tail(24)
        for _, row in live_df.iterrows():
            z = abs((row["kWh"] - df["kWh"].mean()) / df["kWh"].std())
            packet = {
                "Time": datetime.now().strftime("%H:%M:%S"),
                "kW": round(row["kWh"], 2),
                "iKW-TR": round(row["iKW-TR"], 3),
                "Temp_C": round(row["Ambient_Temp"], 1),
                "Occupancy": int(row["Occupancy"]),
                "Anomaly": "⚠️ FLAGGED" if z > 2.5 else "✅ Normal"
            }
            stream_data.append(packet)
            with placeholder.container():
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("Live kW Draw", f"{packet['kW']}")
                m2.metric("iKW-TR", f"{packet['iKW-TR']}")
                m3.metric("Ambient Temp", f"{packet['Temp_C']} °C")
                m4.metric("Occupancy", f"{packet['Occupancy']}")
                m5.metric("Status", packet["Anomaly"])
                st.line_chart(pd.DataFrame(stream_data).set_index("Time")[["kW", "iKW-TR"]])
            time.sleep(0.5)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    st.markdown("<div class='section-title'>OPTIMIZATION ENGINE</div>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Efficiency Benchmarking")
        avg_eff = df['iKW-TR'].mean()
        st.metric("Live iKW-TR", f"{avg_eff:.3f}", delta="Target < 0.65")
        stress = min(avg_eff / 1.0, 1.0)
        st.progress(stress, text=f"Compressor Stress: {stress:.0%}")

        # ── SHAP FEATURE IMPORTANCE ───────────────────────────────────
        st.markdown("#### 🧠 SHAP — Forecast Drivers")
        st.caption("Why is the model predicting this energy demand?")
        icon_map = {
            "Ambient_Temp": "🌡️",
            "Humidity": "💧",
            "Occupancy": "👥",
            "WBT": "🌀",
            "iKW-TR": "⚡",
            "iKW_TR": "⚡"
        }
        if shap_importance:
            for feature, pct in shap_importance.items():
                icon = icon_map.get(feature, "📊")
                label = feature.replace("_", " ")
                st.markdown(f"{icon} **{label}** — {pct}%")
                st.progress(min(pct / 100, 1.0))
        else:
            st.info("SHAP data unavailable.")

        st.markdown("#### Chiller Sequencing")
        cs1, cs2, cs3 = st.columns(3)
        cs1.metric("Chillers Active", chillers_req)
        cs2.metric("Optimized COP", opt_cop)
        cs3.metric("Load/Chiller", f"{load_per_ch} kWh")
        st.info(load_status)

        st.markdown("#### Chiller Loading")
        for i in range(chillers_req):
            load_frac = min(loading_ratio / 100, 1.0)
            color = "🔴" if loading_ratio > 85 else "🟡" if loading_ratio > 60 else "🟢"
            st.progress(load_frac, text=f"{color} Chiller {i+1}: {loading_ratio}% loaded")

    with col_right:
        st.markdown(f"#### AI Recommendations ({horizon}h Horizon)")
        for rec in opt_recs:
            if "🔴" in rec or "⚠️" in rec:
                st.error(rec)
            elif "✅" in rec:
                st.success(rec)
            else:
                st.warning(rec)

    st.markdown("<div class='section-title'>SCENARIO PEAK COMPARISON</div>", unsafe_allow_html=True)
    comp_data = []
    for s in ALL_SCENARIOS:
        df_s = apply_scenario(df_raw, s)
        f_s = run_forecasting(df_s, horizon)
        comp_data.append({"Scenario": s.replace("_"," ").title(), "Peak kWh": f_s["predicted_peak"], "Accuracy": f_s["accuracy_pct"]})
    fig_comp = px.bar(pd.DataFrame(comp_data), x="Scenario", y="Peak kWh", color="Scenario",
                      text="Peak kWh", color_discrete_sequence=px.colors.qualitative.Bold)
    fig_comp.update_layout(template='plotly_dark', paper_bgcolor='#0a0e1a', plot_bgcolor='#0d1b2a',
                           height=320, margin=dict(l=0,r=0,t=30,b=0), showlegend=False)
    fig_comp.update_traces(texttemplate='%{text:.0f}', textposition='outside')
    st.plotly_chart(fig_comp, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    st.markdown("<div class='section-title'>DIAGNOSTIC INTELLIGENCE</div>", unsafe_allow_html=True)
    col_score, col_rca = st.columns([1, 2])

    with col_score:
        risk_val = 85 if maint_priority == "High" else 55 if maint_priority == "Moderate" else 20
        risk_class = "risk-high" if maint_priority == "High" else "risk-moderate" if maint_priority == "Moderate" else "risk-low"
        st.metric("Risk Score", f"{risk_val} / 100")
        st.progress(risk_val / 100)
        st.markdown(f"<div class='{risk_class}'>● {maint_priority} Priority</div>", unsafe_allow_html=True)
        st.metric("Priority Score", f"{priority_score} / 12")
        st.metric("Anomaly Rate", f"{anomaly_ratio}%")
        st.metric("Peak Risk", peak_risk)
        st.metric("Degradation", degradation)
        st.metric("Worst Anomaly", anomaly_desc)

    with col_rca:
        st.markdown("#### Root Cause Analysis")
        a_count = len(anomalies)
        behavioral = int(df['Humidity'].mean() / 10)
        sys_drift = int(df['iKW-TR'].std() * 20)
        fig_rca = px.pie(
            names=["Equipment Faults", "Behavioral Bias", "System Drift"],
            values=[max(a_count, 1), max(behavioral, 1), max(sys_drift, 1)],
            hole=0.45,
            color_discrete_sequence=["#ff4757", "#ffa502", "#00d4ff"]
        )
        fig_rca.update_layout(template='plotly_dark', paper_bgcolor='#0a0e1a', height=280, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig_rca, use_container_width=True)
        st.write(f"**Root Cause:** {root_cause}")
        st.write(f"**Degradation Status:** {degradation}")
        st.write(f"**Anomalies:** {a_count} detected ({anomaly_ratio}% of dataset)")

    st.markdown("<div class='section-title'>iKW-TR EFFICIENCY TREND WITH ANOMALY DETECTION</div>", unsafe_allow_html=True)
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=df["Timestamp"], y=df["iKW-TR"],
        line=dict(color='#00d4ff', width=1.5),
        name='iKW-TR'
    ))
    if len(anomalies) > 0:
        fig_trend.add_trace(go.Scatter(
            x=anomalies["Timestamp"], y=anomalies["iKW-TR"],
            mode='markers',
            marker=dict(color='#ff4757', size=7, symbol='x'),
            name=f'Anomalies ({len(anomalies)})'
        ))
    fig_trend.add_hline(y=0.65, line_dash="dash", line_color="#2ed573", annotation_text="Target 0.65")
    fig_trend.add_hline(y=0.75, line_dash="dash", line_color="#ff4757", annotation_text="Critical 0.75")
    fig_trend.update_layout(
        template='plotly_dark', paper_bgcolor='#0a0e1a', plot_bgcolor='#0d1b2a',
        height=300, margin=dict(l=0,r=0,t=30,b=0),
        xaxis_title="Time", yaxis_title="iKW-TR"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    if len(anomalies) > 0:
        st.markdown("<div class='section-title'>TOP ANOMALY EVENTS</div>", unsafe_allow_html=True)
        top_anoms = anomalies.nlargest(8, "max_z")[["Timestamp", "kWh", "iKW-TR", "Ambient_Temp", "max_z", "anomaly_col"]].copy()
        top_anoms.columns = ["Timestamp", "kWh", "iKW-TR", "Amb Temp", "Z-Score", "Parameter"]
        top_anoms["Z-Score"] = top_anoms["Z-Score"].round(2)
        st.dataframe(top_anoms, use_container_width=True, hide_index=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab5:
    st.markdown("<div class='section-title'>CONVERSATIONAL AI DECISION ASSISTANT</div>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    hvac_context = f"""You are an expert HVAC systems engineer and energy analyst embedded in an industrial AI monitoring platform.
You have real-time access to live system data for Central IT Park, Chennai.

CURRENT STATE:
- Scenario: {scenario.upper()} — {SCENARIO_DESCRIPTIONS.get(scenario, '')}
- Forecast Horizon: {horizon} hours
- Avg Load: {df['kWh'].mean():.2f} kWh | Predicted Peak: {pred_peak:.2f} kWh | Historical Peak: {hist_peak:.2f} kWh
- iKW-TR: {df['iKW-TR'].mean():.3f} (target < 0.65, critical > 0.75)
- Peak Risk: {peak_risk} | Maintenance Priority: {maint_priority} (Score: {priority_score}/12)
- Outdoor Temp: {weather['temperature']}°C | Humidity: {weather['humidity']}% | WBT: {wbt_val}°C
- Anomalies: {len(anomalies)} detected ({anomaly_ratio}%) | Worst: {anomaly_desc}
- Degradation: {degradation} | Root Cause: {root_cause}
- Chillers: {chillers_req} active | COP: {opt_cop} | Load/chiller: {load_per_ch} kWh ({loading_ratio}%)
- Solar Offset: {solar_generated:.0f} kWh | Est. Cost Savings: ₹{cost_saved:,.0f} | CO₂ Avoided: {co2_saved:.0f} kg
- SHAP Top Driver: {list(shap_importance.keys())[0] if shap_importance else 'N/A'} ({list(shap_importance.values())[0] if shap_importance else 'N/A'}% influence)

RULES: Technical precision. HVAC industry terminology. Reference live data. 6 sentences max unless asked for more. Flag iKW-TR > 0.75 automatically."""

    chat_html = "<div class='chat-wrapper'>"
    if not st.session_state.chat_history:
        chat_html += "<div style='color:#1e3a5f; text-align:center; margin-top:210px; font-family:Share Tech Mono,monospace; font-size:12px; letter-spacing:2px;'>⚡ SYSTEM READY — ASK ANYTHING</div>"
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            chat_html += f"<div class='bubble-label bubble-label-right'>YOU</div><div class='bubble-user'>{msg['content']}</div>"
        else:
            chat_html += f"<div class='bubble-label'>🤖 HVAC AGENT</div><div class='bubble-ai'>{msg['content']}</div>"
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    col_i, col_s, col_c = st.columns([7, 1, 1])
    with col_i:
        user_q = st.text_input("", key="chat_input", label_visibility="collapsed",
                               placeholder="e.g. Why is iKW-TR elevated? What should I do before Monday peak?")
    with col_s:
        send = st.button("SEND", type="primary", use_container_width=True)
    with col_c:
        if st.button("CLEAR", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    if send and user_q.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_q})
        msgs = [{"role": "system", "content": hvac_context}]
        for t in st.session_state.chat_history[-6:]:
            msgs.append({"role": t["role"], "content": t["content"]})
        try:
            with st.spinner("⚡ Analyzing..."):
                resp = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile", messages=msgs,
                    temperature=0.4, max_tokens=512)
            reply = resp.choices[0].message.content
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()
        except Exception as e:
            st.error(f"Groq Error: {e}")

    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "assistant":
        b64 = base64.b64encode(st.session_state.chat_history[-1]["content"].encode()).decode()
        st.markdown(f'<a href="data:text/plain;base64,{b64}" download="hvac_response.txt" style="color:#4a6fa5; font-size:11px; font-family:Share Tech Mono,monospace;">↓ DOWNLOAD LAST RESPONSE</a>', unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab6:
    st.markdown("<div class='section-title'>IMPACT SUMMARY — ENERGY & SUSTAINABILITY</div>", unsafe_allow_html=True)

    i1, i2, i3, i4 = st.columns(4)
    i1.metric("Total kWh Saved", f"{kwh_saved:,.0f}")
    i2.metric("Cost Savings (₹)", f"₹{cost_saved:,.0f}")
    i3.metric("CO₂ Avoided (kg)", f"{co2_saved:,.0f}")
    i4.metric("Solar Coverage", f"{solar_pct}%")

    st.markdown("<div class='section-title'>ALL SCENARIOS COMPARISON</div>", unsafe_allow_html=True)
    full_comp = []
    for s in ALL_SCENARIOS:
        df_s = apply_scenario(df_raw, s)
        f_s = run_forecasting(df_s, horizon)
        fp, _ = apply_renewable_offset(f_s["future_prediction"], horizon)
        pa = float(np.mean(fp))
        base = df_raw["kWh"].mean() * horizon
        curr = pa * horizon
        sol = _
        saved_kwh = max(base - curr + sol, 0)
        full_comp.append({
            "Scenario": s.replace("_"," ").title(),
            "Peak kWh": round(f_s["predicted_peak"], 1),
            "Avg kWh": round(pa, 1),
            "kWh Saved": round(saved_kwh, 0),
            "₹ Saved": round(saved_kwh * 8, 0),
            "CO₂ Saved (kg)": round(saved_kwh * 0.82, 0),
            "Forecast Accuracy": f"{f_s['accuracy_pct']}%",
        })
    df_comp = pd.DataFrame(full_comp)
    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    col_x, col_y = st.columns(2)
    with col_x:
        fig_cost = px.bar(df_comp, x="Scenario", y="₹ Saved", title="Estimated Cost Savings by Scenario",
                          color="₹ Saved", color_continuous_scale="Blues")
        fig_cost.update_layout(template='plotly_dark', paper_bgcolor='#0a0e1a', plot_bgcolor='#0d1b2a',
                               height=300, margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig_cost, use_container_width=True)
    with col_y:
        fig_co2 = px.bar(df_comp, x="Scenario", y="CO₂ Saved (kg)", title="CO₂ Avoided by Scenario",
                         color="CO₂ Saved (kg)", color_continuous_scale="Greens")
        fig_co2.update_layout(template='plotly_dark', paper_bgcolor='#0a0e1a', plot_bgcolor='#0d1b2a',
                               height=300, margin=dict(l=0,r=0,t=30,b=0))
        st.plotly_chart(fig_co2, use_container_width=True)

    st.markdown("<div class='section-title'>SYSTEM PARAMETERS</div>", unsafe_allow_html=True)
    params = {
        "Tariff Rate": "₹8.00 / kWh (TN Commercial)",
        "CO₂ Emission Factor": "0.82 kg CO₂ / kWh (India Grid)",
        "Solar Panel Capacity": "120 kWh/hr (08:00–17:00)",
        "Chiller Capacity": "800 kWh per unit",
        "iKW-TR Target": "< 0.65 (Critical > 0.75)",
        "Forecast Model": "RandomForest 200 estimators + SHAP Explainability",
        "Anomaly Method": "Z-Score (threshold: 2.5σ)",
        "Facility": "Central IT Park, Chennai",
    }
    for k, v in params.items():
        st.markdown(f"<div class='impact-row'><span class='impact-label'>{k}</span><span class='impact-value'>{v}</span></div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<div style='text-align:center; color:#1e3a5f; font-family:Share Tech Mono,monospace; font-size:11px; letter-spacing:2px;'>ENERGY INSIGHT AI AGENT | CENTRAL IT PARK CHENNAI | {datetime.now().year}</div>", unsafe_allow_html=True)