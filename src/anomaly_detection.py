import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

PROCESSED_DIR = os.path.join("data", "processed")
ANALYZED_DIR = os.path.join("data", "analyzed")

INPUT_CSV = os.path.join(PROCESSED_DIR, "master_market_data.csv")
OUTPUT_CSV = os.path.join(ANALYZED_DIR, "analyzed_market_data.csv") 
OUTPUT_PLOT = os.path.join(ANALYZED_DIR, "anomaly_diagnostic_dashboard.png")

def detect_market_anomalies():
    """Applies both Batch and Rolling window Isolation Forests for comparative risk analysis."""
    print("🧠 Initializing Dual-Method Machine Learning Inference Engine...")

    if not os.path.exists(INPUT_CSV):
        print(f"❌ ML Engine Aborted: Master data core not found at {INPUT_CSV}")
        return

    if not os.path.exists(ANALYZED_DIR):
        os.makedirs(ANALYZED_DIR)

    # 1. Load data and compute statistical returns
    df = pd.read_csv(INPUT_CSV)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)

    assets = ["OIL_CRUDE", "GOLD", "US500"]
    feature_cols = []

    df = df.dropna().copy()
    for asset in assets:
        return_col = f"{asset}_return"
        df[return_col] = df[f"{asset}_close"].pct_change()
        feature_cols.append(return_col)

    df = df.dropna(subset=feature_cols).reset_index(drop=True)

    if len(df) < 250:
        print("⚠️ Insufficient data depth to execute a 240-minute rolling window simulation.")
        return

    market_features = df[feature_cols].values

    # --- METHOD 1: BATCH ISOLATION FOREST (In-Sample / Looks at total day) ---
    print("🏋️ Executing Method 1: Batch Institutional Isolation Forest...")
    batch_model = IsolationForest(contamination=0.01, random_state=42, n_estimators=100)
    batch_model.fit(market_features)
    df['anomaly_score_batch'] = batch_model.decision_function(market_features)
    df['is_anomaly_batch'] = np.where(batch_model.predict(market_features) == -1, 1, 0)

    # --- METHOD 2: ROLLING WINDOW ISOLATION FOREST (Out-of-Sample / Pure Past History) ---
    print("🔄 Executing Method 2: 240-Minute Sliding Rolling Window Simulation...")
    window_size = 240
    rolling_anomalies = np.zeros(len(df))
    rolling_scores = np.zeros(len(df))

    # Loop through the time-series simulating real-time minutely ingestion
    for i in range(window_size, len(df)):
        # Train ONLY on the past window_size rows (strictly prevents lookahead data leakage)
        train_slice = market_features[i - window_size : i]
        current_sample = market_features[i].reshape(1, -1)
        
        # Fast configuration optimized for minutely iterative loops
        rolling_model = IsolationForest(contamination=0.01, random_state=42, n_estimators=50, n_jobs=-1)
        rolling_model.fit(train_slice)
        
        rolling_scores[i] = rolling_model.decision_function(current_sample)[0]
        rolling_anomalies[i] = 1 if rolling_model.predict(current_sample)[0] == -1 else 0

    df['anomaly_score_rolling'] = rolling_scores
    df['is_anomaly_rolling'] = rolling_anomalies

    print(f"✅ Statistical Summary:")
    print(f"👉 Total Data Points: {len(df)} minutes")
    print(f"🔴 Batch Anomalies Flagged: {df['is_anomaly_batch'].sum()}")
    print(f"💜 Rolling Anomalies Flagged: {df['is_anomaly_rolling'].sum()} (Active post-burn-in window)")

    # Save the expanded multi-model dataset
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Dual-model vectors saved to Analyzed Layer: {OUTPUT_CSV}")

    # 4. Generate Advanced Comparative 3x2 Diagnostic Dashboard
    print("📊 Constructing comparative anomaly verification dashboard...")
    fig, axes = plt.subplots(3, 2, figsize=(16, 16))
    
    # Isolate data subsets for plotting
    batch_anomalies = df[df['is_anomaly_batch'] == 1]
    rolling_anomalies = df[df['is_anomaly_rolling'] == 1]
    normal_df = df[(df['is_anomaly_batch'] == 0) & (df['is_anomaly_rolling'] == 0)]

    # --- ROW 1, LEFT: Batch Risk Space (US500 vs OIL) ---
    axes[0, 0].scatter(normal_df['US500_return'] * 100, normal_df['OIL_CRUDE_return'] * 100, color='gray', alpha=0.3, s=15, label='Normal Minutes')
    axes[0, 0].scatter(batch_anomalies['US500_return'] * 100, batch_anomalies['OIL_CRUDE_return'] * 100, color='red', edgecolor='black', s=45, label='Batch Anomaly (🔴)', zorder=5)
    axes[0, 0].set_title("Method 1: Batch Risk Space (US500 vs OIL)", fontsize=11, fontweight='bold', loc='left')
    axes[0, 0].set_xlabel("US500 Return (%)"); axes[0, 0].set_ylabel("OIL_CRUDE Return (%)")
    axes[0, 0].grid(True, linestyle=':', alpha=0.6); axes[0, 0].legend(loc="upper right")

    # --- ROW 1, RIGHT: Rolling Risk Space (US500 vs OIL) ---
    axes[0, 1].scatter(normal_df['US500_return'] * 100, normal_df['OIL_CRUDE_return'] * 100, color='gray', alpha=0.3, s=15, label='Normal Minutes')
    axes[0, 1].scatter(rolling_anomalies['US500_return'] * 100, rolling_anomalies['OIL_CRUDE_return'] * 100, color='purple', edgecolor='black', marker='^', s=55, label='Rolling Anomaly (💜)', zorder=5)
    axes[0, 1].set_title("Method 2: 240-Min Rolling Risk Space (US500 vs OIL)", fontsize=11, fontweight='bold', loc='left')
    axes[0, 1].set_xlabel("US500 Return (%)"); axes[0, 1].set_ylabel("OIL_CRUDE Return (%)")
    axes[0, 1].grid(True, linestyle=':', alpha=0.6); axes[0, 1].legend(loc="upper right")

    # --- ROW 2, LEFT: Timeline Validation - OIL_CRUDE ---
    axes[1, 0].plot(df['time'], df['OIL_CRUDE_close'], color='#d95f02', alpha=0.6, label='OIL Baseline')
    axes[1, 0].scatter(batch_anomalies['time'], batch_anomalies['OIL_CRUDE_close'], color='red', s=30, label='Batch (🔴)', zorder=5)
    axes[1, 0].scatter(rolling_anomalies['time'], rolling_anomalies['OIL_CRUDE_close'], color='purple', marker='^', s=45, label='Rolling (💜)', zorder=6)
    axes[1, 0].set_title("Timeline Context: OIL_CRUDE Spot Comparison", fontsize=11, fontweight='bold', loc='left')
    axes[1, 0].set_ylabel("Crude Price ($)"); axes[1, 0].grid(True, linestyle=':'); axes[1, 0].legend(loc="upper left")

    # --- ROW 2, RIGHT: Timeline Validation - GOLD ---
    axes[1, 1].plot(df['time'], df['GOLD_close'], color='#fdbf6f', alpha=0.7, label='GOLD Baseline')
    axes[1, 1].scatter(batch_anomalies['time'], batch_anomalies['GOLD_close'], color='red', s=30, label='Batch (🔴)', zorder=5)
    axes[1, 1].scatter(rolling_anomalies['time'], rolling_anomalies['GOLD_close'], color='purple', marker='^', s=45, label='Rolling (💜)', zorder=6)
    axes[1, 1].set_title("Timeline Context: GOLD Spot Comparison", fontsize=11, fontweight='bold', loc='left')
    axes[1, 1].set_ylabel("Gold Price ($)"); axes[1, 1].grid(True, linestyle=':'); axes[1, 1].legend(loc="upper left")

    # --- ROW 3, LEFT: Timeline Validation - US500 ---
    axes[2, 0].plot(df['time'], df['US500_close'], color='#1f78b4', alpha=0.6, label='US500 Baseline')
    axes[2, 0].scatter(batch_anomalies['time'], batch_anomalies['US500_close'], color='red', s=30, label='Batch (🔴)', zorder=5)
    axes[2, 0].scatter(rolling_anomalies['time'], rolling_anomalies['US500_close'], color='purple', marker='^', s=45, label='Rolling (💜)', zorder=6)
    axes[2, 0].set_title("Timeline Context: US500 Spot Comparison", fontsize=11, fontweight='bold', loc='left')
    axes[2, 0].set_ylabel("Index Price"); axes[2, 0].grid(True, linestyle=':'); axes[2, 0].legend(loc="upper left")

    # --- ROW 3, RIGHT: Analytical Score Comparison (Distribution lines) ---
    axes[2, 1].plot(df['time'], df['anomaly_score_batch'], color='red', alpha=0.5, label='Batch Score (In-Sample)')
    axes[2, 1].plot(df['time'], df['anomaly_score_rolling'], color='purple', alpha=0.5, label='Rolling Score (Out-of-Sample)')
    axes[2, 1].set_title("Signal Telemetry: Isolation Scores Over Time", fontsize=11, fontweight='bold', loc='left')
    axes[2, 1].set_xlabel("Timeline"); axes[2, 1].set_ylabel("Decision Score (Lower = More Volatile)")
    axes[2, 1].grid(True, linestyle=':'); axes[2, 1].legend(loc="lower left")

    # Realign X-axis date layouts for all lower charts
    for row in range(1, 3):
        for col in range(2):
            plt.sca(axes[row, col])
            plt.xticks(rotation=30)
        
    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT, dpi=300)
    print(f"✅ Comparative Diagnostic Dashboard saved to Analyzed Layer: {OUTPUT_PLOT}\n")

if __name__ == "__main__":
    detect_market_anomalies()
