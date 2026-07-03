import os
import pandas as pd
import matplotlib.pyplot as plt

RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")

OUTPUT_CSV = os.path.join(PROCESSED_DIR, "master_market_data.csv")
OUTPUT_PLOT = os.path.join(PROCESSED_DIR, "market_trends.png")

def process_and_align_assets():
    """Transforms standalone raw data feeds into an integrated processed data ledger."""
    target_assets = ["OIL_CRUDE", "GOLD", "US500"]
    dataframe_registry = {}

    print("🔄 Initializing multi-asset temporal alignment layers...")

    # 1. Ensure processed storage directory exists
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)
        print(f"📂 Processed Storage Architecture initialized at: {PROCESSED_DIR}")

    # 2. Parse and register separate source files from the raw layer
    for asset in target_assets:
        file_path = os.path.join(RAW_DIR, f"{asset}.csv")
        if not os.path.exists(file_path):
            print(f"❌ Pipeline Interrupted: Missing raw source file for registered asset: {asset}")
            return
        
        df = pd.read_csv(file_path)
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        
        df = df[['time', 'close_bid']].rename(columns={'close_bid': f'{asset}_close'})
        dataframe_registry[asset] = df

    # 3. Execute High-Performance Asynchronous Time-Series Matching (pd.merge_asof)
    master_dataframe = dataframe_registry[target_assets[0]]
    for asset in target_assets[1:]:
        master_dataframe = pd.merge_asof(
            master_dataframe, 
            dataframe_registry[asset], 
            on='time', 
            direction='backward'
        )

    # Export normalized master database matrix to processed layer
    master_dataframe.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Integrated Master Core saved successfully to Processed Layer: {OUTPUT_CSV} ({len(master_dataframe)} rows matched)")

    # 4. Render Enterprise-Grade Visualization Analytics
    print("📊 Generating dynamic multi-panel market trending charts...")
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    graph_colors = ['#d95f02', '#fdbf6f', '#1f78b4'] 
    
    for idx, asset in enumerate(target_assets):
        axes[idx].plot(
            master_dataframe['time'], 
            master_dataframe[f'{asset}_close'], 
            color=graph_colors[idx], 
            label=f'{asset} Close (Bid)', 
            linewidth=1.2
        )
        axes[idx].set_title(f"MANTRA Stream Analysis Engine: {asset} Spot Index", fontsize=11, fontweight='bold', loc='left')
        axes[idx].set_ylabel("Index Valuation", fontsize=9)
        axes[idx].grid(True, linestyle=':', alpha=0.6)
        axes[idx].legend(loc="upper left")
        
    plt.xlabel("Execution Timeline (UTC)", fontsize=10)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    
    # Save visualization to processed layer
    plt.savefig(OUTPUT_PLOT, dpi=300)
    print(f"✅ Analytical graphic matrix rendered and saved to Processed Layer: {OUTPUT_PLOT}")

if __name__ == "__main__":
    process_and_align_assets()
