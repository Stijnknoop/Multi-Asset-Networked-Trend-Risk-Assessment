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
    """Applies Isolation Forest and renders an advanced 6-panel statistical diagnostics dashboard."""
    print("🧠 Initializing Advanced ML Diagnostics & Analytics Layer...")

    if not os.path.exists(INPUT_CSV):
        print(f"❌ ML Engine Aborted: Master data core not found at {INPUT_CSV}")
        return

    if not os.path.exists(ANALYZED_DIR):
        os.makedirs(ANALYZED_DIR)
        print(f"📂 Analyzed Storage Architecture initialized at: {ANALYZED_DIR}")

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

    if len(df) < 15:
        print("⚠️ Insufficient historical data depth to execute advanced diagnostics.")
        return

    # 2. Fit Isolation Forest Model
    model = IsolationForest(contamination=0.01, random_state=42, n_estimators=100)
    market_features = df[feature_cols].values
    
    print("🏋️ Extracting non-linear dependencies and training Isolation Forest...")
    model.fit(market_features)
    
    df['anomaly_score'] = model.decision_function(market_features)
    predictions = model.predict(market_features)
    df['is_anomaly'] = np.where(predictions == -1, 1, 0)
    
    print(f"✅ Analytics completed. Systemic shocks isolated: {df['is_anomaly'].sum()}")

    df.to_csv(OUTPUT_CSV, index=False)

    # 3. Generate Advanced 3x2 Diagnostic Dashboard
    print("📊 Constructing 6-panel anomaly verification dashboard...")
    fig, axes = plt.subplots(3, 2, figsize=(16, 16))
    
    anomalies_df = df[df['is_anomaly'] == 1]
    normal_df = df[df['is_anomaly'] == 0]

    # --- ROW 1, LEFT: Cross-Asset Risk Space (US500 vs OIL) ---
    axes[0, 0].scatter(normal_df['US500_return'] * 100, normal_df['OIL_CRUDE_return'] * 100, color='#1f78b4', alpha=0.4, label='Normal Minutes', s=15)
    axes[0, 0].scatter(anomalies_df['US500_return'] * 100, anomalies_df['OIL_CRUDE_return'] * 100, color='red', edgecolor='black', s=45, label='Systemic Anomaly', zorder=5)
    axes[0, 0].set_title("Risk Space Matrix: US500 vs OIL_CRUDE Returns", fontsize=11, fontweight='bold', loc='left')
    axes[0, 0].set_xlabel("US500 Return (%)", fontsize=9)
    axes[0, 0].set_ylabel("OIL_CRUDE Return (%)", fontsize=9)
    axes[0, 0].grid(True, linestyle=':', alpha=0.6)
    axes[0, 0].axhline(0, color='black', linewidth=0.5, alpha=0.5)
    axes[0, 0].axvline(0, color='black', linewidth=0.5, alpha=0.5)
    axes[0, 0].legend(loc="upper right")

    # --- ROW 1, RIGHT: Cross-Asset Risk Space (US500 vs GOLD) ---
    axes[0, 1].scatter(normal_df['US500_return'] * 100, normal_df['GOLD_return'] * 100, color='#2ca02c', alpha=0.4, label='Normal Minutes', s=15)
    axes[0, 1].scatter(anomalies_df['US500_return'] * 100, anomalies_df['GOLD_return'] * 100, color='red', edgecolor='black', s=45, label='Systemic Anomaly', zorder=5)
    axes[0, 1].set_title("Risk Space Matrix: US500 vs GOLD Returns", fontsize=11, fontweight='bold', loc='left')
    axes[0, 1].set_xlabel("US500 Return (%)", fontsize=9)
    axes[0, 1].set_ylabel("GOLD Return (%)", fontsize=9)
    axes[0, 1].grid(True, linestyle=':', alpha=0.6)
    axes[0, 1].axhline(0, color='black', linewidth=0.5, alpha=0.5)
    axes[0, 1].axvline(0, color='black', linewidth=0.5, alpha=0.5)
    axes[0, 1].legend(loc="upper right")

    # --- ROW 2, LEFT: Anomaly Score Distribution Histogram ---
    threshold_score = np.percentile(df['anomaly_score'], 1)
    axes[1, 0].hist(normal_df['anomaly_score'], bins=30, color='gray', alpha=0.5, label='Normal Domain')
    axes[1, 0].hist(anomalies_df['anomaly_score'], bins=5, color='red', alpha=0.8, label='Anomaly Domain')
    axes[1, 0].axvline(threshold_score, color='darkred', linestyle='--', linewidth=2, label='Cutoff Threshold')
    axes[1, 0].set_title("Statistical Distribution: Isolation Scores", fontsize=11, fontweight='bold', loc='left')
    axes[1, 0].set_xlabel("Decision Score (Lower = More Anomalous)", fontsize=9)
    axes[1, 0].set_ylabel("Frequency (Minute Counts)", fontsize=9)
    axes[1, 0].grid(True, linestyle=':', alpha=0.6)
    axes[1, 0].legend(loc="upper right")

    # --- ROW 2, RIGHT: Timeline Validation - OIL_CRUDE Close (FOUND OIL!) ---
    axes[1, 1].plot(df['time'], df['OIL_CRUDE_close'], color='#d95f02', alpha=0.7, label='OIL_CRUDE Index Baseline')
    axes[1, 1].scatter(anomalies_df['time'], anomalies_df['OIL_CRUDE_close'], color='red', s=25, label='Anomaly Node', zorder=5)
    axes[1, 1].set_title("Timeline Context: OIL_CRUDE Spot Reference", fontsize=11, fontweight='bold', loc='left')
    axes[1, 1].set_ylabel("Crude Price ($)", fontsize=9)
    axes[1, 1].grid(True, linestyle=':', alpha=0.5)
    axes[1, 1].legend(loc="upper left")

    # --- ROW 3, LEFT: Timeline Validation - GOLD Close ---
    axes[2, 0].plot(df['time'], df['GOLD_close'], color='#fdbf6f', alpha=0.8, label='GOLD Baseline')
    axes[2, 0].scatter(anomalies_df['time'], anomalies_df['GOLD_close'], color='red', s=25, label='Anomaly Node', zorder=5)
    axes[2, 0].set_title("Timeline Context: GOLD Spot Reference", fontsize=11, fontweight='bold', loc='left')
    axes[2, 0].set_ylabel("Gold Price ($)", fontsize=9)
    axes[2, 0].grid(True, linestyle=':', alpha=0.5)
    axes[2, 0].legend(loc="upper left")

    # --- ROW 3, RIGHT: Timeline Validation - US500 Close ---
    axes[2, 1].plot(df['time'], df['US500_close'], color='#1f78b4', alpha=0.7, label='US500 Index Baseline')
    axes[2, 1].scatter(anomalies_df['time'], anomalies_df['US500_close'], color='red', s=25, label='Anomaly Node', zorder=5)
    axes[2, 1].set_title("Timeline Context: US500 Spot Reference", fontsize=11, fontweight='bold', loc='left')
    axes[2, 1].set_ylabel("Index Price", fontsize=9)
    axes[2, 1].grid(True, linestyle=':', alpha=0.5)
    axes[2, 1].legend(loc="upper left")

    # Realign X-axis date layouts for all lower timeline plots
    for ax in [axes[1, 1], axes[2, 0], axes[2, 1]]:
        plt.sca(ax)
        plt.xticks(rotation=30)
        
    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT, dpi=300)
    print(f"✅ Advanced 6-Panel Diagnostic Dashboard saved to Analyzed Layer: {OUTPUT_PLOT}\n")

if __name__ == "__main__":
    detect_market_anomalies()
