import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

PROCESSED_DIR = os.path.join("data", "processed")
ANALYZED_DIR = os.path.join("data", "analyzed")

INPUT_CSV = os.path.join(PROCESSED_DIR, "master_market_data.csv")
OUTPUT_CSV = os.path.join(ANALYZED_DIR, "analyzed_market_data.csv") 
OUTPUT_COMPARE_PLOT = os.path.join(ANALYZED_DIR, "anomaly_diagnostic_dashboard.png")
OUTPUT_ROLLING_PLOT = os.path.join(ANALYZED_DIR, "rolling_anomaly_report.png")
OUTPUT_JSON = os.path.join(ANALYZED_DIR, "rolling_anomalies.json")

# --- CONFIGURATIE VOOR HET AGGREGATIENIVEAU ---
AGGREGATION_MINUTES = 5  # Verander dit naar 10 voor een nog grotere macro-blik
WINDOW_SIZE = 240        # Het rolling window blijft exact 240 minuten groot

def detect_market_anomalies():
    """Applies rolling returns over a macro block while maintaining 1-minute execution steps."""
    print(f"🧠 Initializing Overlapping {AGGREGATION_MINUTES}-Min Return Inference Engine (1-Min Resolution)...")

    if not os.path.exists(INPUT_CSV):
        print(f"❌ ML Engine Aborted: Master data core not found at {INPUT_CSV}")
        return

    if not os.path.exists(ANALYZED_DIR):
        os.makedirs(ANALYZED_DIR)

    # 1. Load data at native 1-minute steps
    df = pd.read_csv(INPUT_CSV)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)

    assets = ["OIL_CRUDE", "GOLD", "US500"]
    feature_cols = []

    # --- THE QUANT UPGRADE: Compute rolling returns over a multi-minute period ---
    print(f"📊 Calculating {AGGREGATION_MINUTES}-minute overlapping return vectors at 1-minute steps...")
    for asset in assets:
        return_col = f"{asset}_return"
        # periods=5 zorgt ervoor dat we de huidige minuut vergelijken met 5 minuten geleden
        df[return_col] = df[f"{asset}_close"].pct_change(periods=AGGREGATION_MINUTES)
        feature_cols.append(return_col)

    # Clean up the initial rows that don't have enough history for the return window yet
    df = df.dropna(subset=feature_cols).reset_index(drop=True)

    if len(df) < (WINDOW_SIZE + 10):
        print(f"⚠️ Insufficient data history to fill the {WINDOW_SIZE}-minute rolling window.")
        return

    market_features = df[feature_cols].values

    # --- METHOD 1: BATCH ISOLATION FOREST ---
    print("🏋️ Executing Method 1: Batch Isolation Forest (Overlapping Features)...")
    batch_model = IsolationForest(contamination=0.01, random_state=42, n_estimators=100)
    batch_model.fit(market_features)
    df['anomaly_score_batch'] = batch_model.decision_function(market_features)
    df['is_anomaly_batch'] = np.where(batch_model.predict(market_features) == -1, 1, 0)

    # --- METHOD 2: ROLLING WINDOW SIMULATION (1-Min steps, 240-Min lookback) ---
    print(f"🔄 Executing Method 2: {WINDOW_SIZE}-Minute Sliding Window Simulation...")
    rolling_anomalies = np.zeros(len(df))
    rolling_scores = np.zeros(len(df))

    for i in range(WINDOW_SIZE, len(df)):
        train_slice = market_features[i - WINDOW_SIZE : i]
        current_sample = market_features[i].reshape(1, -1)
        
        rolling_model = IsolationForest(contamination=0.01, random_state=42, n_estimators=50, n_jobs=-1)
        rolling_model.fit(train_slice)
        
        rolling_scores[i] = rolling_model.decision_function(current_sample)[0]
        rolling_anomalies[i] = 1 if rolling_model.predict(current_sample)[0] == -1 else 0

    df['anomaly_score_rolling'] = rolling_scores
    df['is_anomaly_rolling'] = rolling_anomalies

    print("✅ Matrices populated. Saving analysis to CSV...")
    df.to_csv(OUTPUT_CSV, index=False)

    # =========================================================================
    # 🧾 JSON EXTRACTION FOR AI RISK COMMITTEE
    # =========================================================================
    print("📝 Extracting active rolling anomalies into JSON ledger...")
    active_rolling_df = df.iloc[WINDOW_SIZE:].reset_index(drop=True)
    active_anomalies = active_rolling_df[active_rolling_df['is_anomaly_rolling'] == 1]
    
    json_payload = []
    for _, row in active_anomalies.iterrows():
        anomaly_entry = {
            "timestamp_utc": row['time'].strftime('%Y-%m-%d %H:%M:%S'),
            "telemetry_metrics": {
                "isolation_decision_score": float(row['anomaly_score_rolling']),
                "systemic_anomaly_flag": int(row['is_anomaly_rolling']),
                "return_window_aggregation": f"{AGGREGATION_MINUTES}_minutes"
            },
            "market_state": {
                "US500": {
                    "close_index": float(row['US500_close']),
                    "rolling_return_pct": float(row['US500_return'] * 100)
                },
                "OIL_CRUDE": {
                    "close_price_usd": float(row['OIL_CRUDE_close']),
                    "rolling_return_pct": float(row['OIL_CRUDE_return'] * 100)
                },
                "GOLD": {
                    "close_price_usd": float(row['GOLD_close']),
                    "rolling_return_pct": float(row['GOLD_return'] * 100)
                }
            }
        }
        json_payload.append(anomaly_entry)
        
    with open(OUTPUT_JSON, 'w') as json_file:
        json.dump(json_payload, json_file, indent=2)
    print(f"✅ AI Risk Ledger successfully exported ({len(json_payload)} entries): {OUTPUT_JSON}")

    # =========================================================================
    # 📊 DASHBOARD GENERATION
    # =========================================================================
    print("📊 Constructing comparative 6-panel verification dashboard...")
    fig, axes = plt.subplots(3, 2, figsize=(16, 16))
    batch_anomalies = df[df['is_anomaly_batch'] == 1]
    rolling_anomalies_df = df[df['is_anomaly_rolling'] == 1]
    normal_df = df[(df['is_anomaly_batch'] == 0) & (df['is_anomaly_rolling'] == 0)]

    axes[0, 0].scatter(normal_df['US500_return'] * 100, normal_df['OIL_CRUDE_return'] * 100, color='gray', alpha=0.3, s=15, label='Normal Ticks')
    axes[0, 0].scatter(batch_anomalies['US500_return'] * 100, batch_anomalies['OIL_CRUDE_return'] * 100, color='red', edgecolor='black', s=45, label='Batch Anomaly', zorder=5)
    axes[0, 0].set_title(f"Method 1: Batch Risk Space ({AGGREGATION_MINUTES}m Returns)", fontsize=11, fontweight='bold', loc='left')
    axes[0, 0].set_xlabel(f"US500 {AGGREGATION_MINUTES}m Return (%)"); axes[0, 0].set_ylabel(f"OIL_CRUDE {AGGREGATION_MINUTES}m Return (%)")
    axes[0, 0].grid(True, linestyle=':', alpha=0.6); axes[0, 0].legend(loc="upper right")

    axes[0, 1].scatter(normal_df['US500_return'] * 100, normal_df['OIL_CRUDE_return'] * 100, color='gray', alpha=0.3, s=15, label='Normal Ticks')
    axes[0, 1].scatter(rolling_anomalies_df['US500_return'] * 100, rolling_anomalies_df['OIL_CRUDE_return'] * 100, color='purple', edgecolor='black', marker='^', s=55, label='Rolling Anomaly', zorder=5)
    axes[0, 1].set_title(f"Method 2: 240m Rolling Risk Space ({AGGREGATION_MINUTES}m Returns)", fontsize=11, fontweight='bold', loc='left')
    axes[0, 1].set_xlabel(f"US500 {AGGREGATION_MINUTES}m Return (%)"); axes[0, 1].set_ylabel(f"OIL_CRUDE {AGGREGATION_MINUTES}m Return (%)")
    axes[0, 1].grid(True, linestyle=':', alpha=0.6); axes[0, 1].legend(loc="upper right")

    # De prijsgrafieken behouden hun volledige 1-minuut resolutie
    axes[1, 0].plot(df['time'], df['OIL_CRUDE_close'], color='#d95f02', alpha=0.6, label='OIL Baseline')
    axes[1, 0].scatter(batch_anomalies['time'], batch_anomalies['OIL_CRUDE_close'], color='red', s=30, label='Batch (Red)', zorder=5)
    axes[1, 0].scatter(rolling_anomalies_df['time'], rolling_anomalies_df['OIL_CRUDE_close'], color='purple', marker='^', s=45, label='Rolling (Purple)', zorder=6)
    axes[1, 0].set_title("Timeline Context: OIL_CRUDE Spot Comparison", fontsize=11, fontweight='bold', loc='left')
    axes[1, 0].set_ylabel("Crude Price ($)"); axes[1, 0].grid(True, linestyle=':'); axes[1, 0].legend(loc="upper left")

    axes[1, 1].plot(df['time'], df['GOLD_close'], color='#fdbf6f', alpha=0.7, label='GOLD Baseline')
    axes[1, 1].scatter(batch_anomalies['time'], batch_anomalies['GOLD_close'], color='red', s=30, label='Batch (Red)', zorder=5)
    axes[1, 1].scatter(rolling_anomalies_df['time'], rolling_anomalies_df['GOLD_close'], color='purple', marker='^', s=45, label='Rolling (Purple)', zorder=6)
    axes[1, 1].set_title("Timeline Context: GOLD Spot Comparison", fontsize=11, fontweight='bold', loc='left')
    axes[1, 1].set_ylabel("Gold Price ($)"); axes[1, 1].grid(True, linestyle=':'); axes[1, 1].legend(loc="upper left")

    axes[2, 0].plot(df['time'], df['US500_close'], color='#1f78b4', alpha=0.6, label='US500 Baseline')
    axes[2, 0].scatter(batch_anomalies['time'], batch_anomalies['US500_close'], color='red', s=30, label='Batch (Red)', zorder=5)
    axes[2, 0].scatter(rolling_anomalies_df['time'], rolling_anomalies_df['US500_close'], color='purple', marker='^', s=45, label='Rolling (Purple)', zorder=6)
    axes[2, 0].set_title("Timeline Context: US500 Spot Comparison", fontsize=11, fontweight='bold', loc='left')
    axes[2, 0].set_ylabel("Index Price"); axes[2, 0].grid(True, linestyle=':'); axes[2, 0].legend(loc="upper left")

    axes[2, 1].plot(df['time'], df['anomaly_score_batch'], color='red', alpha=0.5, label='Batch Score')
    axes[2, 1].plot(df['time'], df['anomaly_score_rolling'], color='purple', alpha=0.5, label='Rolling Score')
    axes[2, 1].set_title("Telemetry: Isolation Scores Over Time", fontsize=11, fontweight='bold', loc='left')
    axes[2, 1].set_xlabel("Timeline"); axes[2, 1].set_ylabel("Decision Score")
    axes[2, 1].grid(True, linestyle=':'); axes[2, 1].legend(loc="lower left")

    for row in range(1, 3):
        for col in range(2):
            plt.sca(axes[row, col])
            plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(OUTPUT_COMPARE_PLOT, dpi=300)
    plt.close()

    print("📊 Generating standalone Out-of-Sample Rolling Window Report...")
    fig_roll, axes_roll = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
    asset_colors = ['#d95f02', '#fdbf6f', '#1f78b4']
    asset_labels = ['OIL_CRUDE ($)', 'GOLD ($)', 'US500 Index']
    
    for idx, asset in enumerate(assets):
        axes_roll[idx].plot(active_rolling_df['time'], active_rolling_df[f'{asset}_close'], color=asset_colors[idx], alpha=0.8, label=f'{asset} Baseline', linewidth=1.2)
        axes_roll[idx].scatter(active_anomalies['time'], active_anomalies[f'{asset}_close'], color='purple', marker='^', s=40, label='Rolling Anomaly (Purple)', zorder=5)
        axes_roll[idx].set_title(f"MANTRA Production Node: 1-Min Step / {AGGREGATION_MINUTES}m Return Feed - {asset}", fontsize=11, fontweight='bold', loc='left')
        axes_roll[idx].set_ylabel(asset_labels[idx], fontsize=9)
        axes_roll[idx].grid(True, linestyle=':', alpha=0.5)
        axes_roll[idx].legend(loc="upper left")
        
    plt.xlabel("Streaming Timeline (UTC)", fontsize=10)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(OUTPUT_ROLLING_PLOT, dpi=300)
    plt.close()
    print("✅ System run completely processed with overlapping returns.\n")

if __name__ == "__main__":
    detect_market_anomalies()
