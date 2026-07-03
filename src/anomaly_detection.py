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

AGGREGATION_MINUTES = 5  
WINDOW_SIZE = 240        

def detect_market_anomalies():
    """Applies rolling returns and clusters consecutive anomalies into multi-minute macro events."""
    print(f"🧠 Initializing Overlapping {AGGREGATION_MINUTES}-Min Return Inference Engine...")

    if not os.path.exists(INPUT_CSV):
        print(f"❌ ML Engine Aborted: Master data core not found at {INPUT_CSV}")
        return

    if not os.path.exists(ANALYZED_DIR):
        os.makedirs(ANALYZED_DIR)

    df = pd.read_csv(INPUT_CSV)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)

    assets = ["OIL_CRUDE", "GOLD", "US500"]
    feature_cols = []

    for asset in assets:
        return_col = f"{asset}_return"
        df[return_col] = df[f"{asset}_close"].pct_change(periods=AGGREGATION_MINUTES)
        feature_cols.append(return_col)

    df = df.dropna(subset=feature_cols).reset_index(drop=True)

    if len(df) < (WINDOW_SIZE + 10):
        print(f"⚠️ Insufficient data history to fill the {WINDOW_SIZE}-minute rolling window.")
        return

    market_features = df[feature_cols].values

    # --- METHOD 1: BATCH ISOLATION FOREST ---
    batch_model = IsolationForest(contamination=0.01, random_state=42, n_estimators=100)
    batch_model.fit(market_features)
    df['anomaly_score_batch'] = batch_model.decision_function(market_features)
    df['is_anomaly_batch'] = np.where(batch_model.predict(market_features) == -1, 1, 0)

    # --- METHOD 2: ROLLING WINDOW SIMULATION ---
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

    df.to_csv(OUTPUT_CSV, index=False)

    # =========================================================================
    # ⚡ TEMPORAL CLUSTERING ALGORITHM
    # =========================================================================
    print("📝 Grouping persistent anomaly clusters into single Macro Shock Events...")
    active_rolling_df = df.iloc[WINDOW_SIZE:].reset_index(drop=True)
    anomalies_indices = active_rolling_df[active_rolling_df['is_anomaly_rolling'] == 1].index.tolist()
    
    json_payload = []
    
    if anomalies_indices:
        clusters = []
        current_cluster = [anomalies_indices[0]]
        MAX_GAP_MINUTES = 10 
        
        for idx in anomalies_indices[1:]:
            time_diff = (active_rolling_df.loc[idx, 'time'] - active_rolling_df.loc[current_cluster[-1], 'time']).total_seconds() / 60
            if time_diff <= MAX_GAP_MINUTES:
                current_cluster.append(idx)
            else:
                clusters.append(current_cluster)
                current_cluster = [idx]
        clusters.append(current_cluster)
        
        for event_id, cluster in enumerate(clusters, start=1):
            cluster_df = active_rolling_df.loc[cluster]
            peak_row = cluster_df.loc[cluster_df['anomaly_score_rolling'].idxmin()]
            
            event_entry = {
                "event_id": event_id,
                "wave_start_utc": cluster_df['time'].min().strftime('%Y-%m-%d %H:%M:%S'),
                "wave_end_utc": cluster_df['time'].max().strftime('%Y-%m-%d %H:%M:%S'),
                "total_duration_minutes": int((cluster_df['time'].max() - cluster_df['time'].min()).total_seconds() / 60) + 1,
                "ticks_in_cluster": len(cluster),
                "peak_telemetry": {
                    "peak_timestamp_utc": peak_row['time'].strftime('%Y-%m-%d %H:%M:%S'),
                    "worst_isolation_score": float(peak_row['anomaly_score_rolling'])
                },
                "macro_peak_market_returns": {
                    "US500_max_return_pct": float(cluster_df['US500_return'].max() * 100 if cluster_df['US500_return'].max() > abs(cluster_df['US500_return'].min()) else cluster_df['US500_return'].min() * 100),
                    "OIL_CRUDE_max_return_pct": float(cluster_df['OIL_CRUDE_return'].max() * 100 if cluster_df['OIL_CRUDE_return'].max() > abs(cluster_df['OIL_CRUDE_return'].min()) else cluster_df['OIL_CRUDE_return'].min() * 100),
                    "GOLD_max_return_pct": float(cluster_df['GOLD_return'].max() * 100 if cluster_df['GOLD_return'].max() > abs(cluster_df['GOLD_return'].min()) else cluster_df['GOLD_return'].min() * 100)
                }
            }
            json_payload.append(event_entry)

    with open(OUTPUT_JSON, 'w') as json_file:
        json.dump(json_payload, json_file, indent=2)
    print(f"✅ Aggregated Event Risk Ledger exported ({len(json_payload)} macro events): {OUTPUT_JSON}")

    # =========================================================================
    # 📊 DASHBOARD GENERATION (FIXED: Definitions added)
    # =========================================================================
    print("📊 Constructing comparative 6-panel verification dashboard...")
    fig, axes = plt.subplots(3, 2, figsize=(16, 16))
    
    # FIX: Hier zijn de ontbrekende variabelen netjes gedefinieerd!
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
        axes_roll[idx].scatter(rolling_anomalies_df['time'], rolling_anomalies_df[f'{asset}_close'], color='purple', marker='^', s=40, label='Rolling Anomaly (Purple)', zorder=5)
        axes_roll[idx].set_title(f"MANTRA Production Node: 1-Min Step / {AGGREGATION_MINUTES}m Return Feed - {asset}", fontsize=11, fontweight='bold', loc='left')
        axes_roll[idx].set_ylabel(asset_labels[idx], fontsize=9)
        axes_roll[idx].grid(True, linestyle=':', alpha=0.5)
        axes_roll[idx].legend(loc="upper left")
        
    plt.xlabel("Streaming Timeline (UTC)", fontsize=10)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(OUTPUT_ROLLING_PLOT, dpi=300)
    plt.close()
    print("✅ System run completely processed with clustered event states.\n")

if __name__ == "__main__":
    detect_market_anomalies()
