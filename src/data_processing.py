import os
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = "data"
OUTPUT_CSV = os.path.join(DATA_DIR, "master_market_data.csv")
OUTPUT_PLOT = os.path.join(DATA_DIR, "market_trends.png")

def process_and_align_assets():
    """Transforms standalone asset data feeds into an integrated multi-asset data ledger."""
    target_assets = ["OIL_CRUDE", "GOLD", "US500"]
    dataframe_registry = {}

    print("🔄 Initializing multi-asset temporal alignment layers...")

    # 1. Parse, scrub, and register separate source files
    for asset in target_assets:
        file_path = os.path.join(DATA_DIR, f"{asset}.csv")
        if not os.path.exists(file_path):
            print(f"❌ Pipeline Interrupted: Missing source file for registered asset: {asset}")
            return
        
        df = pd.read_csv(file_path)
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        
        # Isolate close parameter and map distinct column headings to avoid namespace collisions
        df = df[['time', 'close_bid']].rename(columns={'close_bid': f'{asset}_close'})
        dataframe_registry[asset] = df

    # 2. Execute High-Performance Asynchronous Time-Series Matching (pd.merge_asof)
    # Uses 'backward' matching to link decoupled tick feeds safely without forward data leakage
    master_dataframe = dataframe_registry[target_assets[0]]
    for asset in target_assets[1:]:
        master_dataframe = pd.merge_asof(
            master_dataframe, 
            dataframe_registry[asset], 
            on='time', 
            direction='backward'
        )

    # Export normalized master database matrix
    master_dataframe.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Integrated Master Core saved successfully: {OUTPUT_CSV} ({len(master_dataframe)} rows matched)")

    # 3. Render Enterprise-Grade Visualization Analytics
    print("📊 Generating dynamic multi-panel market trending charts...")
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    # Institutional/Quant color palette configurations
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
    plt.gcf().autofmt_xdate()  # Intelligently realigns x-axis timestamps diagonally
    plt.tight_layout()
    
    # Save visualization to disk
    plt.savefig(OUTPUT_PLOT, dpi=300)
    print(f"✅ Analytical graphic matrix rendered and saved: {OUTPUT_PLOT}")

if __name__ == "__main__":
    process_and_align_assets()
