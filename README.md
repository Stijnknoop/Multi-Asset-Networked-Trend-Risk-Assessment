# MANTRA: Multi-Asset Networked Trend Risk Assessment

MANTRA is an enterprise-grade, end-to-end Quantitative Data Engineering and Agentic AI pipeline designed to ingest high-frequency market parameters, isolate systemic multi-asset risk structures, and orchestrate an automated AI Risk Committee to deliver actionable institutional briefings.

The architecture strictly adheres to a decoupled, event-driven **Medallion Architecture (Raw ➔ Processed ➔ Analyzed)** powered by Chained GitHub Actions, unsupervised Machine Learning (`scikit-learn`), and multi-agent systems (`CrewAI` + `Gemini 2.0 Flash`).

---

## 🏛️ System Architecture & Data Layers

The pipeline isolates infrastructure responsibilities into distinct operational layers to ensure absolute fault tolerance, high scannability, and prevent lookahead data leakage.

    [Market API] 
         │
         ▼ (Every hour, Mon-Fri)
    ┌────────────────────────────────────────────────────────┐
    │ 1. INGESTION LAYER (data/raw/)                         │ ──► Drops asynchronous tick feeds
    └────────────────────────────────────────────────────────┘
         │
         ▼ (Triggered on Ingestion Success)
    ┌────────────────────────────────────────────────────────┐
    │ 2. PROCESSING LAYER (data/processed/)                 │ ──► Time-series synchronization (merge_asof)
    └────────────────────────────────────────────────────────┘
         │
         ▼ (Triggered on Processing Success)
    ┌────────────────────────────────────────────────────────┐
    │ 3. ANALYTICS & ML LAYER (data/analyzed/)               │ ──► Isolation Forest (Batch vs. 240m Rolling)
    └────────────────────────────────────────────────────────┘
         │
         ▼ (Triggered on Analytics Success)
    ┌────────────────────────────────────────────────────────┐
    │ 4. AGENTIC AI LAYER (data/analyzed/report)             │ ──► CrewAI Committee Issues Financial Verdicts
    └────────────────────────────────────────────────────────┘

### Data Directory Schema
* **`data/raw/`**: Landing zone for individual asset tick histories (`GOLD.csv`, `OIL_CRUDE.csv`, `US500.csv`).
* **`data/processed/`**: The unified ledger (`master_market_data.csv`) aligned millisecond-by-millisecond using backward-looking time matching.
* **`data/analyzed/`**: Gold-standard telemetry zone containing engineered return features, comparative model tracking logs (`analyzed_market_data.csv`), structural JSON agent streams (`rolling_anomalies.json`), diagnostic visualization matrices, and the final executive markdown report.

---

## 🔗 The Chained Production Pipelines (CI/CD)

The infrastructure is orchestrated across three distinct automated GitHub Actions workflows under `.github/workflows/` to implement strict **Separation of Concerns**:

| Pipeline Name | Trigger | Core Execution | Key Artifacts |
| :--- | :--- | :--- | :--- |
| **1. Market Data Ingestion** | Cron (`0 * * * 1-5`) | Authenticates with broker API; fetches 1-min OHLC arrays; executes `pd.merge_asof`. | `data/raw/*.csv`<br>`data/processed/master_market_data.csv` |
| **2. Market Analytics & ML** | `workflow_run` (On Ingestion Success) | Computes minutely returns; trains Batch vs. Out-of-Sample 240-Min Rolling Isolation Forests. | `data/analyzed/anomaly_diagnostic_dashboard.png`<br>`data/analyzed/rolling_anomaly_report.png`<br>`data/analyzed/rolling_anomalies.json` |
| **3. AI Risk Agents Committee** | `workflow_run` (On Analytics Success) | Boots up CrewAI workspace; feeds chronological JSON logs into specialized Gemini-powered agents. | `data/analyzed/risk_committee_report.md` |

---

## 🧠 Advanced Machine Learning: Mitigating Lookahead Bias

To transition from statistical batching to an engine capable of live deployment on a trading desk, MANTRA runs two concurrent **Unsupervised Isolation Forest** configurations:

### Method 1: In-Sample Batch Processing
Evaluates the continuous data matrix retroactively across the entire timeline. While excellent for post-trade historical analysis, it suffers from **Lookahead Bias** (the model's parameters are influenced by future price thresholds that a live system would not yet know).

### Method 2: Out-of-Sample Rolling Window Simulation
Implements a strict **240-minute (4-Hour) Sliding Window**. The model iterates chronologically, fitting a distinct Isolation Forest exclusively on the *past 240 minutes* of asset behaviors to predict the current minutely state. This effectively isolates local, high-velocity shocks that standard batch models overlook due to larger daily macroeconomic variations.

---

## 🤖 Agentic AI Risk Committee Framework

When a rolling anomaly triggers (`is_anomaly_rolling == 1`), the pipeline isolates the raw telemetry variables and packages them into a chronological, streaming JSON ledger. CrewAI then orchestrates an automated committee briefing leveraging `gemini-2.0-flash`:

1.  **Senior Quantitative Risk Analyst**: Processes the data stream out-of-sample to compute cross-asset return velocities, identify correlation breakdowns, and determine the volatility catalyst node.
2.  **Chief Risk Officer (CRO)**: Evaluates the quantitative risk matrix and dictates real-time operational execution mandates for the institutional fund. 

### Actionable Risk Verdict Matrix
The CRO agent is programmed to issue time-stamped operational mandates based strictly on the risk threshold profiles fed to it:
* `🔴 VERDICT: EMERGENCY DE-RISK` - Triggered during highly coordinated cross-asset market liquidations; mandates immediate leverage reductions and margin buffer enforcement.
* `🟡 VERDICT: TACTICAL HEDGE` - Triggered upon structural correlation adjustments; mandates options purchasing to cap portfolio variance.
* `🟢 VERDICT: OPPORTUNISTIC ENTRY` - Triggered upon temporary asset price dislocations backed by stable system anchors.
* `⚪ VERDICT: MAINTAIN POSITION / HOLD` - High volume activity safely contained inside acceptable baseline volatilities.

---

## 🛠️ Repository Blueprint & Local Execution

### Project File Tree
    .
    ├── .github/
    │   └── workflows/
    │       ├── 1_market_data_ingestion.yml
    │       ├── 2_market_analytics.yml
    │       └── 3_market_agents.yml
    ├── data/
    │   ├── raw/
    │   ├── processed/
    │   └── analyzed/
    ├── src/
    │   ├── data_ingestion.py
    │   ├── data_processing.py
    │   ├── anomaly_detection.py
    │   └── agent_orchestrator.py
    ├── requirements.txt
    └── README.md

### Installation & Deployment
To mirror the production architecture on your local environment, configure your workspace credentials and run the modules sequentially:

    # Clone the infrastructure
    git clone [https://github.com/YOUR_USERNAME/Multi-Asset-Networked-Trend-Risk-Assessment.git](https://github.com/YOUR_USERNAME/Multi-Asset-Networked-Trend-Risk-Assessment.git)
    cd Multi-Asset-Networked-Trend-Risk-Assessment

    # Install enterprise dependencies (including Google GenAI extensions)
    pip install -r requirements.txt

    # Set local tracking credentials (mirroring GitHub Secrets)
    export IDENTIFIER="your_capital_login"
    export PASSWORD="your_capital_password"
    export X_CAP_API_KEY="your_capital_api_key"
    export GEMINI_API_KEY="your_google_ai_studio_key"

    # Execute full pipeline chain manually
    python src/data_ingestion.py --epic US500
    python src/data_processing.py
    python src/anomaly_detection.py
    python src/agent_orchestrator.py
