# HVAC Energy Insight Agent

## Overview

This project implements an AI-driven Energy Insight Agent for HVAC systems, developed for the TN Industry Impact Challenge 2026 (EnergyETA x CoE AI4NetZero, IIT Madras).

The system autonomously analyzes multi-parameter HVAC operational data and generates structured technical decision reports focused on:

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
- Occupancy Load Profile

Derived metric:

- COP (Coefficient of Performance)

---

## Implemented Capabilities

### Predictive Analytics

- 168-hour load forecasting (Random Forest)
- Weather-adjusted demand prediction (Open-Meteo API)
- Peak demand anticipation

### Diagnostic Intelligence

- Multi-parameter anomaly detection (Isolation Forest)
- Efficiency degradation trend analysis
- Root cause classification (equipment vs behavioral)
- Maintenance priority scoring

### Impact Quantification

- Projected energy variation (kWh)
- Estimated electricity cost impact
- Estimated CO₂ emission impact

---

## Architecture

The system follows a modular structure:

- data_loader.py → Data ingestion and preprocessing
- diagnostics.py → Health analysis and anomaly detection
- forecasting.py → ML forecasting and weather integration
- reporting.py → Automated HTML report generation
- app.py → System orchestrator

This design enables clarity, maintainability, and scalability toward multi-agent architecture.

---

## Technical Stack

- Python
- Pandas
- NumPy
- Scikit-learn
- Open-Meteo Weather API
- HTML-based report generation

---

## Execution

Install dependencies:

pip install -r requirements.txt

Run the system:

python app.py

Generated report location:

reports/decision_report.html

---

## Competition Alignment

This solution satisfies:

- Processing of ≥3 core parameters
- Implementation of ≥2 analytical techniques
- Explainable technical decision logic
- Automated HTML technical reporting
- Weather API integration
- Modular production-grade structure

---

## Planned Enhancements

- Setpoint optimization logic
- Chiller load balancing recommendations
- Scenario-based simulation layer
- Multi-agent orchestration
- Real-time data streaming
- Containerized deployment