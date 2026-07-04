import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

INPUT_CSV = os.path.join("data", "analyzed", "analyzed_market_data.csv")
OUTPUT_DIR = os.path.join("data", "backtest_results")
OUTPUT_MD = os.path.join(OUTPUT_DIR, "backtest_performance.md")
# NIEUW ARTIFACT: De grafiek die de trades visueel onderbouwt
OUTPUT_PLOT = os.path.join(OUTPUT_DIR, "backtest_chart.png")

def run_multi_strategy_backtest():
    print("🧪 Booting MANTRA Visual Strategy Research Engine...")
    
    if not os.path.exists(INPUT_CSV):
        print(f"❌ Backtest Aborted: Analyzed gold-layer matrix not found at {INPUT_CSV}")
        return

    # 1. Load data
    df = pd.read_csv(INPUT_CSV)
    df['time'] = pd.to_datetime(df['time'])
    df = df.sort_values('time').reset_index(drop=True)

    assets = ["OIL_CRUDE", "GOLD", "US500"]
    holding_period = 15  
    cooldown_ticks = 15  
    
    pnl_mean_reversion = 0.0
    pnl_momentum = 0.0
    trade_count = 0
    cooldown_counter = 0
    
    # NIEUW: Tracker om de PnL-ontwikkeling per trade vast te leggen voor de grafiek
    trade_history = []

    print(f"📈 Analyzing time-series anomalies ({len(df)} bars)...")

    # 2. Backtest loop
    for i in range(len(df) - holding_period):
        if cooldown_counter > 0:
            cooldown_counter -= 1
            continue

        if df.loc[i, 'is_anomaly_rolling'] == 1:
            trade_count += 1
            cooldown_counter = cooldown_ticks  
            
            # Identify catalyst asset
            returns_at_trigger = {asset: df.loc[i, f"{asset}_return"] for asset in assets}
            catalyst_asset = max(returns_at_trigger, key=lambda k: abs(returns_at_trigger[k]))
            trigger_return = returns_at_trigger[catalyst_asset]
            
            # Calculate future performance
            price_at_trigger = df.loc[i, f"{catalyst_asset}_close"]
            price_at_exit = df.loc[i + holding_period, f"{catalyst_asset}_close"]
            future_return = (price_at_exit - price_at_trigger) / price_at_trigger
            
            # Strategy 1: Mean Reversion
            if trigger_return > 0:
                strat1_pnl = -future_return
            else:
                strat1_pnl = future_return
            pnl_mean_reversion += strat1_pnl

            # Strategy 2: Momentum Breakout
            if trigger_return > 0:
                strat2_pnl = future_return
            else:
                strat2_pnl = -future_return
            pnl_momentum += strat2_pnl

            # Sla de statistieken van deze specifieke trade op
            trade_history.append({
                "time": df.loc[i, 'time'],
                "asset": catalyst_asset,
                "mr_trade_return": strat1_pnl * 100,   # in procenten
                "mom_trade_return": strat2_pnl * 100, # in procenten
                "mr_cum_pnl": pnl_mean_reversion * 100,
                "mom_cum_pnl": pnl_momentum * 100
            })

    # 3. Determine best strategy
    results = {
        "Mean-Reversion Spread": pnl_mean_reversion,
        "Momentum Breakout": pnl_momentum
    }
    best_strat = max(results, key=results.get)
    best_pnl = results[best_strat] * 100

    # =========================================================================
    # 📊 NIEUW: GENEREEER DE STRATEGIE PERFORMANCE GRAFIEK
    # =========================================================================
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if trade_history:
        print("📊 Constructing quantitative equity curves and trade logs...")
        trade_df = pd.DataFrame(trade_history)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Panel 1: De Equity Curve (Het verloop over de tijd)
        ax1.plot(trade_df['time'], trade_df['mr_cum_pnl'], label='🔄 Strategy 1: Mean-Reversion Spread', color='#2ca02c', marker='o', linewidth=2)
        ax1.plot(trade_df['time'], trade_df['mom_cum_pnl'], label='🚀 Strategy 2: Momentum Breakout', color='#d62728', marker='x', linestyle='--', linewidth=1.5)
        ax1.set_title("MANTRA Strategy Performance: Cumulative Equity Curve Evolution", fontsize=12, fontweight='bold', loc='left')
        ax1.set_ylabel("Cumulative Net Return (%)", fontsize=10)
        ax1.grid(True, linestyle=':', alpha=0.6)
        ax1.legend(loc="upper left")
        
        # Panel 2: Losse trade returns van de winnende Mean-Reversion strategie
        colors = ['#2ca02c' if x > 0 else '#d62728' for x in trade_df['mr_trade_return']]
        time_labels = trade_df['time'].dt.strftime('%m-%d %H:%M')
        
        ax2.bar(time_labels, trade_df['mr_trade_return'], color=colors, alpha=0.75, edgecolor='black', width=0.4)
        ax2.axhline(0, color='black', linewidth=0.8, linestyle='-')
        ax2.set_title("Individual Trade Yield Breakdown (Winning Framework: Mean-Reversion)", fontsize=12, fontweight='bold', loc='left')
        ax2.set_ylabel("Single Position PnL (%)", fontsize=10)
        ax2.set_xlabel("Chronological Execution Timeline (UTC Target Ticks)", fontsize=10)
        plt.setp(ax2.get_xticklabels(), rotation=30, ha='right')
        ax2.grid(True, linestyle=':', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(OUTPUT_PLOT, dpi=300)
        plt.close()
        print(f"✅ Performance chart successfully saved to: {OUTPUT_PLOT}")
    else:
        print("⚠️ No trades recorded. Skipping plot generation.")

    # 4. Compile Corporate Markdown Report (Inclusief automatische afbeelding-link!)
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
    
### 🏁 Research Verdict
> **MARKET CHARACTERISTIC:** Following an isolation shock, the asset pricing registry historically favors the **{best_strat}** framework (Gross Return: {best_pnl:+.3f}%). *Note: This baseline pilot model excludes transactional spreads and execution slippage.*

---

### 📉 Visual Backtest Audit Ledger
Below is the verified performance data logging the equity path and structural distribution of the individual position yields.

![MANTRA Strategy Performance Chart](backtest_chart.png)
"""
    
    with open(OUTPUT_MD, "w") as f:
        f.write(report_content)
        
    print(f"✅ Quantitative performance metrics successfully compiled to: {OUTPUT_MD}")

if __name__ == "__main__":
    run_multi_strategy_backtest()
