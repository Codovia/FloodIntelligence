# Decisions Log

This document tracks all rejected approaches, threshold choices, and key engineering decisions throughout the project lifecycle.

## Week 1
- **Day 1**: Chose FastAPI and Vite-React for the backend and frontend scaffolds, based on ease of use and modern performance.
- **Day 1**: Proceeding with sourcing real shelter data starting manually using official Karnataka State disaster management sites, as the rule restricts fake data.

## Previous Decisions (Inherited)
- **Rejected Google Flood Hub / Forecasting API**: Waitlist delays and lack of original model implementation (defeats the academic purpose).
- **Rejected H2O.ai + NVIDIA Flood Blueprint**: Built for US data (USGS/NOAA), closed-source LLM for risk analysis, templated design lacks verifiable rigor.
