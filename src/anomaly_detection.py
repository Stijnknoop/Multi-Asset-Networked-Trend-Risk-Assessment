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
    """Applies Isolation Forest and renders an advanced statistical diagnostics dashboard."""
    print("🧠 Initializing Advanced ML Diagnostics & Analytics Layer...")

    if not os.path.exists(INPUT_CSV):
        print(f"❌ ML Engine Aborted: Master data core not found at {INPUT_CSV}")
        return

    # 1. Ensure analyzed storage directory exists
    if not os.path.exists(ANALYZED_DIR):
        os.makedirs(ANALYZED_DIR)
        print(f"📂 Analyzed Storage Architecture initialized at: {ANALYZED_DIR}")

    # 2. Load data and compute statistical returns
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

    # 3. Fit Isolation Forest Model
    model = IsolationForest(contamination=0.01, random_state=42, n_estimators=100)
    market_features = df[feature_cols].values
    
    print("🏋️ Extracting non-linear dependencies and training Isolation Forest...")
    model.fit(market_features)
    
    df['anomaly_score'] = model.decision_function(market_features)
    predictions = model.predict(market_features)
    df['is_anomaly'] = np.where(predictions == -1, 1, 0)
    
    print(f"✅ Analytics completed. Systemic shocks isolated: {df['is_anomaly'].sum()}")

    # Save to the new Analyzed/Gold layer folder
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Rich features and anomaly vectors saved to Analyzed Layer: {OUTPUT_CSV}")

    # 4. Generate Enterprise-Grade Diagnostic Dashboard (Multi-Type Plots)
    print("📊 Constructing multi-type anomaly verification dashboard...")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    anomalies_df = df[df['is_anomaly'] == 1]
    normal_df = df[df['is_anomaly'] == 0]

    # --- PLOT 1 (Top Left): Cross-Asset Return Scatter Cloud (The Outlier Proof) ---
    axes[0, 0].scatter(normal_df['US500_return'] * 100, normal_df['OIL_CRUDE_return'] * 100, color='#1f78b4', alpha=0.4, label='Normal Market Minutes', s=15)
    axes[0, 0].scatter(anomalies_df['US500_return'] * 100, anomalies_df['OIL_CRUDE_return'] * 100, color='red', edgecolor='black', s=45, label='Systemic Anomaly (Outlier)', zorder=5)
    axes[0, 0].set_title("Cross-Asset Risk Space: US500 vs OIL Returns", fontsize=11, fontweight='bold', loc='left')
    axes[0, 0].set_xlabel("US500 Return (%)", fontsize=9)
    axes[0, 0].set_ylabel("OIL_CRUDE Return (%)", fontsize=9)
    axes[0, 0].grid(True, linestyle=':', alpha=0.6)
    axes[0, 0].axhline(0, color='black', linewidth=0.5, alpha=0.5)
    axes[0, 0].axvline(0, color='black', linewidth=0.5, alpha=0.5)
    axes[0, 0].legend(loc="upper right")

    # --- PLOT 2 (Top Right): Anomaly Score Distribution (The Statistical Proof) ---
    threshold_score = np.percentile(df['anomaly_score'], 1) # 1% contamination threshold
    axes[0, 1].hist(normal_df['anomaly_score'], bins=30, color='#2ca02c', alpha=0.6, label='Normal Distribution')
    axes[0, 1].hist(anomalies_df['anomaly_score'], bins=5, color='red', alpha=0.8, label='Anomaly Domain')
    axes[0, 1].axvline(threshold_score, color='darkred', linestyle='--', linewidth=2, label=f'Contamination Cutoff ({threshold_score:.3f})')
    axes[0, 1].set_title("Statistical Proof: Isolation Score Distribution Histogram", fontsize=11, fontweight='bold', loc='left')
    axes[0, 1].set_xlabel("Isolation Forest Decision Score (Lower = More Anomalous)", fontsize=9)
    axes[0, 1].set_ylabel("Frequency (Minute Counts)", fontsize=9)
    axes[0, 1].grid(True, linestyle=':', alpha=0.6)
    axes[0, 1].legend(loc="upper right")

    # --- PLOT 3 (Bottom Left): Timeline Validation - US500 Close ---
    axes[1, 0].plot(df['time'], df['US500_close'], color='#1f78b4', alpha=0.7, label='US500 Index Baseline')
    axes[1, 0].scatter(anomalies_df['time'], anomalies_df['US500_close'], color='red', s=25, label='Anomaly Node', zorder=5)
    axes[1, 0].set_title("Timeline Context: US500 Spot Index Reference", fontsize=11, fontweight='bold', loc='left')
    axes[1, 0].set_ylabel("Index Price", fontsize=9)
    axes[1, 0].grid(True, linestyle=':', alpha=0.5)
    axes[1, 0].legend(loc="upper left")

    # --- PLOT 4 (Bottom Right): Timeline Validation - GOLD Close ---
    axes[1, 1].plot(df['time'], df['GOLD_close'], color='#fdbf6f', alpha=0.8, label='GOLD Baseline')
    axes[1, 1].scatter(anomalies_df['time'], anomalies_df['GOLD_close'], color='red', s=25, label='Anomaly Node', zorder=5)
    axes[1, 1].set_title("Timeline Context: GOLD Spot Index Reference", fontsize=11, fontweight='bold', loc='left')
    axes[1, 1].set_ylabel("Gold Price", fontsize=9)
    axes[1, 1].grid(True, linestyle=':', alpha=0.5)
    axes[1, 1].legend(loc="upper left")

    # Clean up X-axis dates for the bottom timeline plots
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    
    plt.savefig(OUTPUT_PLOT, dpi=300)
    print(f"✅ Advanced Multi-Type Diagnostic Dashboard saved to Analyzed Layer: {OUTPUT_PLOT}\n")

if __name__ == "__main__":
    detect_market_anomalies()
