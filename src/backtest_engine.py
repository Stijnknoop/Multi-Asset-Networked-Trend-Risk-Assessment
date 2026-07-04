import os
import pandas as pd
import numpy as np

INPUT_CSV = os.path.join("data", "analyzed", "analyzed_market_data.csv")
OUTPUT_DIR = os.path.join("data", "backtest_results")
OUTPUT_MD = os.path.join(OUTPUT_DIR, "backtest_performance.md")

def run_multi_strategy_backtest():
    print("🧪 Booting MANTRA Simplified Strategy Research Engine...")
    
    if not os.path.exists(INPUT_CSV):
        print(f"❌ Backtest Aborted: Analyzed gold-layer matrix not found at {INPUT_CSV}")
        return

    # 1. Load standard processed close data
    df = pd.read_csv(INPUT_CSV)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)

    assets = ["OIL_CRUDE", "GOLD", "US500"]
    holding_period = 15  # Hoeveel minuten kijken we vooruit na een anomalie
    cooldown_ticks = 15  # Voorkom overtraden binnen hetzelfde cluster
    
    pnl_mean_reversion = 0.0
    pnl_momentum = 0.0
    trade_count = 0
    cooldown_counter = 0

    print(f"📈 Analyzing time-series anomalies ({len(df)} bars)...")

    # 2. Straightforward Backtest Loop
    for i in range(len(df) - holding_period):
        if cooldown_counter > 0:
            cooldown_counter -= 1
            continue

        if df.loc[i, 'is_anomaly_rolling'] == 1:
            trade_count += 1
            cooldown_counter = cooldown_ticks  
            
            # Identificeer welke asset de schok veroorzaakte (grootste afwijking)
            returns_at_trigger = {asset: df.loc[i, f"{asset}_return"] for asset in assets}
            catalyst_asset = max(returns_at_trigger, key=lambda k: abs(returns_at_trigger[k]))
            trigger_return = returns_at_trigger[catalyst_asset]
            
            # Bereken het verloop van de close-prijs over de volgende 15 minuten
            price_at_trigger = df.loc[i, f"{catalyst_asset}_close"]
            price_at_exit = df.loc[i + holding_period, f"{catalyst_asset}_close"]
            future_return = (price_at_exit - price_at_trigger) / price_at_trigger
            
            # Strategy 1: Mean Reversion (Inzetten op herstel)
            if trigger_return > 0:
                pnl_mean_reversion += (-future_return)
            else:
                pnl_mean_reversion += future_return

            # Strategy 2: Momentum Breakout (Meeliften met de richting)
            if trigger_return > 0:
                pnl_momentum += future_return
            else:
                pnl_momentum += (-future_return)

    # 3. Bepaal de winnaar op basis van pure richting
    results = {
        "Mean-Reversion Spread": pnl_mean_reversion,
        "Momentum Breakout": pnl_momentum
    }
    best_strat = max(results, key=results.get)
    best_pnl = results[best_strat] * 100

    # 4. Schrijf een clean en eerlijk rapport
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    report_content = f"""# 📊 MANTRA Quantitative Pilot Simulation
    
This automated research node evaluates the directionality of asset prices immediately following a detected rolling anomaly cluster. 
    
### 🔬 Pilot Parameters
* **Captured Anomaly Signals (Post-Cooldown):** {trade_count}
* **Position Holding Horizon:** {holding_period} Minutes
* **Data Scale Basis:** Standard Closing Mid-Prices (Proof of Concept)
    
### 📈 Directional Leaderboard
| Directional Strategy | Total Simulated PnL (%) | Baseline Status |
| :--- | :--- | :--- |
| **🔄 Strategy 1: Mean-Reversion Spread** | {pnl_mean_reversion * 100:+.4f}% | {"🟢 Positive Horizon" if pnl_mean_reversion > 0 else "🔴 Negative Horizon"} |
| **🚀 Strategy 2: Momentum Breakout** | {pnl_momentum * 100:+.4f}% | {"🟢 Positive Horizon" if pnl_momentum > 0 else "🔴 Negative Horizon"} |
    
### 🏁 Pilot Verdict
> **MARKET CHARACTERISTIC:** Following an isolation shock, the asset pricing registry historically favors the **{best_strat}** framework (Gross Return: {best_pnl:+.3f}%). *Note: This baseline pilot model excludes transactional spreads and execution slippage.*
"""
    
    with open(OUTPUT_MD, "w") as f:
        f.write(report_content)
        
    print(f"✅ Baseline performance metrics successfully compiled to: {OUTPUT_MD}")

if __name__ == "__main__":
    run_multi_strategy_backtest()
