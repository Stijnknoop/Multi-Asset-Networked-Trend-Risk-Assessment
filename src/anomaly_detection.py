import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest

PROCESSED_DIR = os.path.join("data", "processed")
INPUT_CSV = os.path.join(PROCESSED_DIR, "master_market_data.csv")
OUTPUT_CSV = os.path.join(PROCESSED_DIR, "master_market_data.csv") # Overwrite with ML features
OUTPUT_PLOT = os.path.join(PROCESSED_DIR, "anomaly_detection_report.png")

def detect_market_anomalies():
    """Applies an unsupervised Isolation Forest model to flag systemic cross-asset shocks."""
    print("🧠 Initializing Machine Learning Anomaly Detection Layer...")

    if not os.path.exists(INPUT_CSV):
        print(f"❌ ML Engine Aborted: Master data core not found at {INPUT_CSV}")
        return

    # 1. Load data and calculate financial returns (percentage change per minute)
    df = pd.read_csv(INPUT_CSV)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)

    assets = ["OIL_CRUDE", "GOLD", "US500"]
    feature_cols = []

    # Drop early rows with NaNs caused by the rolling/shifting operations to keep clean feature vectors
    df = df.dropna().copy()

    for asset in assets:
        return_col = f"{asset}_return"
        # Calculate log returns or simple returns to normalize the pricing scale differences
        df[return_col] = df[f"{asset}_close"].pct_change()
        feature_cols.append(return_col)

    # Drop the very first row because its return calculation will always be NaN
    df = df.dropna(subset=feature_cols).reset_index(drop=True)

    if len(df) < 10:
        print("⚠️ Insufficient historical data depth to execute Isolation Forest inference.")
        return

    # 2. Fit Isolation Forest
    # contamination=0.01 maps to flagging the top 1% most volatile/extreme joint outliers
    model = IsolationForest(contamination=0.01, random_state=42, n_estimators=100)
    
    # Train and predict across the multi-asset return matrix
    market_features = df[feature_cols]
    df['anomaly_score'] = model.decision_function(market_features)
    predictions = model.predict(market_features)
    
    # Map scikit-learn's output (-1: anomaly, 1: normal) to explicit flags (1: anomaly, 0: normal)
    df['is_anomaly'] = np.where(predictions == -1, 1, 0)
    
    anomalies_count = df['is_anomaly'].sum()
    print(f"✅ Unsupervised inference completed. Systemic anomalies identified: {anomalies_count}")

    # Save the enriched dataset back to the processed layer
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Integrated features and anomaly vectors saved to core: {OUTPUT_CSV}")

    # 3. Generate Anomaly Detection Visualization Report
    print("📊 Plotting anomaly matrices and diagnostic graphics...")
    fig, axes = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
    graph_colors = ['#d95f02', '#fdbf6f', '#1f78b4']
    
    anomalies_df = df[df['is_anomaly'] == 1]

    for idx, asset in enumerate(assets):
        # Plot continuous baseline price trend line
        axes[idx].plot(df['time'], df[f'{asset}_close'], color=graph_colors[idx], alpha=0.7, label=f'{asset} Baseline', linewidth=1.2)
        
        # Overlay structural anomaly intersections as bright red scattered nodes
        axes[idx].scatter(anomalies_df['time'], anomalies_df[f'{asset}_close'], color='red', s=25, label='Systemic Anomaly Flag', zorder=5)
        
        axes[idx].set_title(f"MANTRA Diagnostic Node: {asset} Anomalies Over Time", fontsize=11, fontweight='bold', loc='left')
        axes[idx].set_ylabel("Index Valuation", fontsize=9)
        axes[idx].grid(True, linestyle=':', alpha=0.5)
        axes[idx].legend(loc="upper left")

    plt.xlabel("Execution Timeline (UTC)", fontsize=10)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    
    plt.savefig(OUTPUT_PLOT, dpi=300)
    print(f"✅ Automated ML graphic report rendered and saved: {OUTPUT_PLOT}\n")

if __name__ == "__main__":
    detect_market_anomalies()
