# MANTRA: Multi-Asset Networked Trend Risk Assessment

MANTRA is an enterprise-grade, end-to-end Quantitative Data Engineering and Agentic AI platform designed to ingest high-frequency market parameters, isolate systemic multi-asset risk structures, and orchestrate automated backtesting and AI Risk Committees to deliver actionable institutional briefings.

The architecture strictly adheres to a decoupled, event-driven **Medallion Architecture (Raw ➔ Processed ➔ Analyzed & Backtested)** powered by Chained GitHub Actions pipelines, unsupervised Machine Learning (`scikit-learn`), and multi-agent systems (`CrewAI` + `Gemini 2.0 Flash`).

---

## 🏛️ System Architecture & Data Layers

The pipeline isolates infrastructure responsibilities into distinct operational layers to ensure absolute fault tolerance, clear separation of concerns, and the total prevention of lookahead data leakage.

```
    [Market API] 
         │
         ▼ (Every hour, Mon-Fri)
    ┌────────────────────────────────────────────────────────┐
    │ 1. INGESTION LAYER (data/raw/)                         │ ──► Drops asynchronous tick feeds
    └────────────────────────────────────────────────────────┘
         │
         ▼ (Triggered on Ingestion Success)
    ┌────────────────────────────────────────────────────────┐
    │ 2. PROCESSING LAYER (data/processed/)                  │ ──► Time-series synchronization (merge_asof)
    └────────────────────────────────────────────────────────┘
         │
         ▼ (Triggered on Processing Success)
    ┌────────────────────────────────────────────────────────┐
    │ 3. ANALYTICS & ML LAYER (data/analyzed/)               │ ──► Isolation Forest (Batch vs. 240m Rolling)
    └────────────────────────────────────────────────────────┘
         ├──► (Triggered on Analytics Success)
         │    ┌────────────────────────────────────────────────────────┐
         │    │ 4. AGENTIC AI LAYER (data/agentic_analysis_...)       │ ──► CrewAI Committee Generates Briefings
         │    └────────────────────────────────────────────────────────┘
         │
         └──► (Triggered on Analytics Success)
              ┌────────────────────────────────────────────────────────┐
              │ 5. BACKTEST ENGINE (data/backtest_results/)            │ ──► Equity Curve & Asset Exposure Analytics
              └────────────────────────────────────────────────────────┘
```

### Data Directory Schema
* **`data/raw/`**: Landing zone for individual asset tick histories (`GOLD.csv`, `OIL_CRUDE.csv`, `US500.csv`).
* **`data/processed/`**: The unified ledger (`master_market_data.csv`) aligned millisecond-by-millisecond using backward-looking time matching.
* **`data/analyzed/`**: Gold-standard telemetry zone containing engineered overlapping return features, comparative model tracking logs (`analyzed_market_data.csv`), structural JSON agent streams (`rolling_anomalies.json`), and diagnostic visualization matrices.
* **`data/backtest_results/`**: Production environment for strategy performance ledgers, containing directional return analyses (`backtest_performance.md`) and the visual equity curve evolution dashboard (`backtest_chart.png`).
* **`data/agentic_analysis_of_rolling_anomalies/`**: Secured environment for generative executive risk briefings (`risk_committee_report.md`).

---

## 🔗 The Chained Production Pipelines (CI/CD)

The infrastructure is orchestrated across four distinct automated GitHub Actions workflows under `.github/workflows/` to enforce strict operational decoupling:

| Pipeline Name | Trigger | Core Execution | Key Artifacts |
| :--- | :--- | :--- | :--- |
| **1. Market Data Ingestion** | Cron (`0 * * * 1-5`) | Authenticates with broker API; fetches 1-min OHLC arrays; executes `pd.merge_asof`. | `data/raw/*.csv`<br>`data/processed/master_market_data.csv` |
| **2. Market Analytics & ML** | `workflow_run` (On Ingestion Success) | Computes overlapping macro returns; trains Batch vs. Out-of-Sample 240-Min Sliding Isolation Forests. | `data/analyzed/anomaly_diagnostic_dashboard.png`<br>`data/analyzed/rolling_anomaly_report.png`<br>`data/analyzed/rolling_anomalies.json` |
| **3. AI Risk Agents Committee** | `workflow_run` (On Analytics Success) | Boots up CrewAI workspace; feeds chronological macro JSON logs into specialized Gemini-powered agents. | `data/agentic_analysis_of_rolling_anomalies/risk_committee_report.md` |
| **4. Quantitative Strategy Backtest** | `workflow_run` (On Analytics Success) / Manual | Simulates directional returns following anomaly triggers; calculates asset class concentration. | `data/backtest_results/backtest_performance.md`<br>`data/backtest_results/backtest_chart.png` |

---

## 🧠 Advanced Machine Learning: Overlapping Return Windows

To transition from legacy statistical batching to an engine capable of capturing systemic market shocks, MANTRA runs an out-of-sample **Unsupervised Isolation Forest** configuration optimized to mitigate lookahead bias and filter high-frequency noise:

### Method: Out-of-Sample Overlapping Rolling Window Simulation
The system maintains a native 1-minute execution frequency to ensure no micro-signals are dropped, but computes mathematical return vectors across an aggregated **15-minute macro period** (`periods=15`). 

This architecture provides distinct institutional advantages:
1. **Macro-Regime Filtering:** Eliminates fractional noise, flash order fluctuations, and algorithmic order-book jitter isolated inside tight 1-minute frames.
2. **Momentum & Cohesion Analysis:** Successfully captures structural asset-correlation disruptions and broader macro-shocks that build up incrementally over a quarter-hour window.
3. **Strict Boundary Bounding:** The training context is bounded to a rolling historical block of **240 observations (4 hours)** to eliminate data leakage.

---

## 📊 Quantitative Strategy Simulation & Asset Exposure

Following an out-of-sample anomaly trigger (`is_anomaly_rolling == 1`), the backtest engine runs a high-fidelity simulation to evaluate whether the market chaos manifests as an exploitable directional regime. 

To ensure complete empirical transparency, this baseline pilot framework evaluates gross returns using standard closing mid-prices across two concurrent execution philosophies:
* **Strategy 1: Institutional Mean-Reversion Spread** – Positioned under the mathematical assumption that cross-asset correlation disruptions behave like an overextended elastic band and will rapidly revert to the rolling baseline.
* **Strategy 2: Institutional Momentum Breakout** – Positioned under the assumption that the anomaly signifies a fundamental structural break, catching a massive multi-minute price sprint.

### 📦 Asset Class Exposure & Risk Concentration
The simulation engine logs and aggregates the specific underlying asset that acted as the primary catalyst for the cross-asset disruption. This transparency isolates idiosyncratic volatility waves (e.g., highly concentrated shocks in `OIL_CRUDE` due to geopolitics or OPEC releases) versus system-wide equities liquidation events (`US500`).

### 📉 Visual Backtest Audit Ledger
The engine automatically generates a dual-panel verification dashboard (`backtest_chart.png`) displayed directly within the production run environment:
* **Panel 1 (Cumulative Equity Curve):** Plots the chronological path of capital evolution, isolating exact entry nodes to track regime efficiency.
* **Panel 2 (Individual Yield Distribution):** A structural bar-chart breakdown documenting single position wins and losses to evaluate portfolio variance.

---

## 🤖 Agentic AI Risk Committee Framework

When a rolling anomaly cluster settles, the pipeline packages the chronological telemetry data into a streaming JSON ledger. CrewAI then orchestrates an automated committee briefing leveraging `gemini-2.0-flash` to translate quantitative parameters into executive mandates:

1. **Senior Quantitative Risk Analyst**: Processes the data streams out-of-sample to compute cross-asset return velocities and isolate the volatility catalyst node.
2. **Chief Risk Officer (CRO)**: Evaluates the quantitative risk matrix and dictates real-time operational execution mandates for the portfolio.

### Actionable Risk Verdict Matrix
The CRO agent is programmed to issue time-stamped operational mandates based strictly on the risk threshold profiles fed to it:
* `🔴 VERDICT: EMERGENCY DE-RISK` - Highly coordinated cross-asset liquidations; mandates immediate leverage reductions.
* `🟡 VERDICT: TACTICAL HEDGE` - Structural correlation adjustments; mandates options purchasing to cap portfolio variance.
* `🟢 VERDICT: OPPORTUNISTIC ENTRY` - Temporary asset price dislocations backed by stable system anchors.
* `⚪ VERDICT: MAINTAIN POSITION / HOLD` - High volume activity safely contained inside acceptable baseline volatilities.

---

## 🛠️ Repository Blueprint & Local Execution

### Project File Tree
```
    .
    ├── .github/
    │   └── workflows/
    │       ├── 1_market_data_ingestion.yml
    │       ├── 2_market_analytics.yml
    │       ├── 3_market_agents.yml
    │       └── 4_strategy_backtest.yml
    ├── data/
    │   ├── raw/
    │   ├── processed/
    │   ├── analyzed/
    │   ├── backtest_results/
    │   └── agentic_analysis_of_rolling_anomalies/
    ├── src/
    │   ├── data_ingestion.py
    │   ├── data_processing.py
    │   ├── anomaly_detection.py
    │   ├── backtest_engine.py
    │   └── agent_orchestrator.py
    ├── requirements.txt
    └── README.md
```

### Installation & Deployment
To mirror the production architecture on your local environment, configure your workspace credentials and run the modules sequentially:

```bash
# Clone the infrastructure
git clone [https://github.com/YOUR_USERNAME/Multi-Asset-Networked-Trend-Risk-Assessment.git](https://github.com/YOUR_USERNAME/Multi-Asset-Networked-Trend-Risk-Assessment.git)
cd Multi-Asset-Networked-Trend-Risk-Assessment

# Install enterprise dependencies (including Google GenAI extensions)
pip install -r requirements.txt

# Set local tracking credentials (mirroring GitHub Secrets)
export IDENTIFIER="your_broker_login"
export PASSWORD="your_broker_password"
export X_CAP_API_KEY="your_broker_api_key"
export GEMINI_API_KEY="your_google_ai_studio_key"

# Execute full production pipeline chain manually
python src/data_ingestion.py --epic US500
python src/data_processing.py
python src/anomaly_detection.py
python src/backtest_engine.py
python src/agent_orchestrator.py
```
