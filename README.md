# HVAC Energy Insight Agent

## Overview
An AI-driven Energy Insight Agent that autonomously analyzes multi-parameter HVAC operational data and generates structured technical decision reports focused on:
- Energy efficiency
- Peak demand management
- Fault detection
- Maintenance prioritization
- Impact quantification

---

## Core Parameters
The system processes:
- kWh (Energy Consumption)
- iKW-TR (Cooling Efficiency)
- Ambient Temperature
- Relative Humidity
- Wet Bulb Temperature (WBT)
- Occupancy Load Profile

---

## Implemented Capabilities

### Scenario Simulation
- 7 physics-based operational scenarios (Normal, Heatwave, Equipment Fault, Solar Boost, Night Mode, Monsoon, Maintenance Mode)
- Two-layer Digital Twin (Live weather API + scenario engine)

### Predictive Analytics
- 24/72/168-hour load forecasting (Random Forest, 200 estimators)
- Confidence bands (15th–85th percentile)
- Weather-adjusted demand prediction (Open-Meteo API)

### Diagnostic Intelligence
- Z-Score anomaly detection (σ = 2.5)
- Efficiency degradation trend analysis (Stable / Marginal / Degrading)
- Root cause classification
- Maintenance priority scoring (0–12)

### Optimization
- Horizon-aware recommendations (immediate / scheduled / strategic)
- Scenario-aware chiller sequencing (1–3 units)
- Solar offset calculation

### Impact Quantification
- Projected energy variation (kWh)
- Estimated cost impact (₹8.00/kWh TN tariff)
- CO₂ emission impact (0.82 kg/kWh India grid)

---

## Architecture
- `data_loader.py` → Data ingestion, WBT calculation, column preprocessing
- `scenario_engine.py` → Physics-based scenario modifications
- `diagnostics.py` → Z-Score anomaly detection and priority scoring
- `forecasting.py` → RandomForest forecasting with confidence bands
- `chiller_sequencing.py` → Dynamic chiller allocation
- `optimization.py` → Horizon-aware recommendation engine
- `renewable.py` → Solar offset calculations
- `weather_api.py` → Live Open-Meteo API integration
- `reporting.py` → Automated HTML report generation
- `streamlit_app.py` → 6-tab industrial dashboard

---

## Technical Stack
- Python 3.11
- Pandas, NumPy
- Scikit-learn (RandomForest)
- Plotly, Streamlit
- Groq API (Llama-3.3-70B)
- Open-Meteo Weather API

---

## Setup

Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key_here
```

Install dependencies:
```
pip install -r requirements.txt
```

Run the system:
```
streamlit run streamlit_app.py
```

---

## Planned Enhancements
- Real-time BMS sensor integration
- Multi-facility federated learning
- Edge deployment for on-premise inference
- Docker containerization