import os
import pandas as pd
import numpy as np

INPUT_CSV = os.path.join("data", "analyzed", "analyzed_market_data.csv")
# NEW LOCATION: Dedicated directory for backtest output
OUTPUT_DIR = os.path.join("data", "backtest_results")
OUTPUT_MD = os.path.join(OUTPUT_DIR, "backtest_performance.md")

def run_multi_strategy_backtest():
    print("🧪 Booting MANTRA Quantitative Strategy Research Engine...")
    
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
    pnl_volatility_straddle = 0.0
    
    trade_count = 0
    cooldown_counter = 0

    print(f"📈 Analyzing time-series matrix ({len(df)} bars)...")

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
                pnl_mean_reversion += (-future_return)
            else:
                pnl_mean_reversion += future_return

            # Strategy 2: Momentum Breakout
            if trigger_return > 0:
                pnl_momentum += future_return
            else:
                pnl_momentum += (-future_return)

            # Strategy 3: Volatility Straddle Proxy (0.04% options premium cost)
            option_premium_cost = 0.0004 
            pnl_volatility_straddle += (abs(future_return) - option_premium_cost)

    # 3. Determine best strategy
    results = {
        "Mean-Reversion Spread": pnl_mean_reversion,
        "Momentum Breakout": pnl_momentum,
        "Volatility Straddle": pnl_volatility_straddle
    }
    best_strat = max(results, key=results.get)
    best_pnl = results[best_strat] * 100

    # 4. Compile Corporate Markdown Report
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    report_content = f"""# 📊 MANTRA Quantitative Strategy Simulation
    
This automated research node evaluates the mathematical exploitability of detected rolling anomaly clusters using three concurrent institutional execution frameworks.
    
### 🔬 Simulation Parameters
* **Captured Anomaly Signals (Post-Cooldown):** {trade_count}
* **Position Holding Horizon:** {holding_period} Minutes
* **Cluster Cooldown Window:** {cooldown_ticks} Minutes
    
### 📈 Performance Leaderboard
| Execution Architecture | Total Simulated PnL (%) | Status |
| :--- | :--- | :--- |
| **🔄 Strategy 1: Mean-Reversion Spread** | {pnl_mean_reversion * 100:+.4f}% | {"🟢 Profitable" if pnl_mean_reversion > 0 else "🔴 Unprofitable"} |
| **🚀 Strategy 2: Momentum Breakout** | {pnl_momentum * 100:+.4f}% | {"🟢 Profitable" if pnl_momentum > 0 else "🔴 Unprofitable"} |
| **🎭 Strategy 3: Options Volatility Straddle** | {pnl_volatility_straddle * 100:+.4f}% | {"🟢 Profitable" if pnl_volatility_straddle > 0 else "🔴 Unprofitable"} |
    
### 🏁 Research Verdict
> **OPTIMAL REGIME DEPLOYMENT:** The data streams isolate the **{best_strat}** engine as the alpha generator for this specific market matrix, yielding a total risk-adjusted return of **{best_pnl:+.3f}%**.
"""
    
    with open(OUTPUT_MD, "w") as f:
        f.write(report_content)
        
    print(f"✅ Quantitative performance metrics successfully compiled to: {OUTPUT_MD}")

if __name__ == "__main__":
    run_multi_strategy_backtest()
