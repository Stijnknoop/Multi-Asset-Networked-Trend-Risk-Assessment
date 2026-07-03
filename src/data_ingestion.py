import os
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = "data"
OUTPUT_CSV = os.path.join(DATA_DIR, "master_market_data.csv")
OUTPUT_PLOT = os.path.join(DATA_DIR, "market_trends.png")

def process_and_align():
    assets = ["OIL_CRUDE", "GOLD", "US500"]
    dfs = {}

    print("🔄 Starten met datakoppeling en uitlijning...")

    # 1. Bestanden inlezen en voorbereiden
    for asset in assets:
        path = os.path.join(DATA_DIR, f"{asset}.csv")
        if not os.path.exists(path):
            print(f"⚠️ Geen data gevonden voor {asset}. Verwerking afgebroken.")
            return
        
        df = pd.read_csv(path)
        df['time'] = pd.to_datetime(df['time'])
        df = df.sort_values('time')
        
        # Selecteer alleen de tijd en de sluitingsprijs, hernoem deze naar de asset-naam
        df = df[['time', 'close_bid']].rename(columns={'close_bid': f'{asset}_close'})
        dfs[asset] = df

    # 2. De magische 'pd.merge_asof' tijdsynchronisatie
    master_df = dfs[assets[0]]
    for asset in assets[1:]:
        master_df = pd.merge_asof(master_df, dfs[asset], on='time', direction='backward')

    # Sla de gecombineerde dataset op in 1 centrale CSV
    master_df.to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Centrale master-tabel succesvol opgeslagen: {OUTPUT_CSV} ({len(master_df)} rijen)")

    # 3. Grafiek genereren (3 gestapelde subplots vanwege de verschillende prijswaarden)
    print("📊 Trends visualiseren en grafiek genereren...")
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    colors = ['#d95f02', '#fdbf6f', '#1f78b4'] # Professioneel corporate/tech palette
    
    for i, asset in enumerate(assets):
        axes[i].plot(master_df['time'], master_df[f'{asset}_close'], color=colors[i], label=f'{asset} Close Price', linewidth=1.5)
        axes[i].set_title(f"{asset} Market Trend", fontsize=12, fontweight='bold', loc='left')
        axes[i].set_ylabel("Price / Value", fontsize=10)
        axes[i].grid(True, linestyle='--', alpha=0.5)
        axes[i].legend(loc="upper left")
        
    plt.xlabel("Timestamp (UTC)", fontsize=11)
    plt.gcf().autofmt_xdate() # Zorgt dat de datums op de X-as netjes schuin staan
    plt.tight_layout()
    
    # Opslaan als PNG afbeelding
    plt.savefig(OUTPUT_PLOT, dpi=300)
    print(f"✅ Trend-afbeelding succesvol opgeslagen: {OUTPUT_PLOT}")

if __name__ == "__main__":
    process_and_align()
