import os
import pandas as pd
import numpy as np

INPUT_CSV = os.path.join("data", "analyzed", "analyzed_market_data.csv")

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
    holding_period = 15  # Aantal minuten dat we een positie vasthouden (intraday horizon)
    cooldown_ticks = 15  # Voorkom overtraden binnen hetzelfde anomaly cluster
    
    # Init PnL trackers (in basispunten / percentages)
    pnl_mean_reversion = 0.0
    pnl_momentum = 0.0
    pnl_volatility_straddle = 0.0
    
    trade_count = 0
    cooldown_counter = 0

    print(f"📈 Analyzing time-series matrix ({len(df)} bars)...")

    # 2. Walk through time chronologically
    for i in range(len(df) - holding_period):
        if cooldown_counter > 0:
            cooldown_counter -= 1
            continue

        # Check of het rolling window model een anomalie signaleert
        if df.loc[i, 'is_anomaly_rolling'] == 1:
            trade_count += 1
            cooldown_counter = cooldown_ticks  # Activeer cooldown voor dit cluster
            
            # Identificeer de 'catalyst asset' (de asset met de grootste absolute return op dit moment)
            returns_at_trigger = {asset: df.loc[i, f"{asset}_return"] for asset in assets}
            catalyst_asset = max(returns_at_trigger, key=lambda k: abs(returns_at_trigger[k]))
            trigger_return = returns_at_trigger[catalyst_asset]
            
            # Meet de cumulatieve return van de asset over de komende 15 minuten
            price_at_trigger = df.loc[i, f"{catalyst_asset}_close"]
            price_at_exit = df.loc[i + holding_period, f"{catalyst_asset}_close"]
            future_return = (price_at_exit - price_at_trigger) / price_at_trigger
            
            # --- STRATEGIE 1: MEAN REVERSION (Gokken op herstel) ---
            # Als de trigger positief was, gaan we SHORT (winst bij daling). Anders LONG.
            if trigger_return > 0:
                strat1_pnl = -future_return
            else:
                strat1_pnl = future_return
            pnl_mean_reversion += strat1_pnl

            # --- STRATEGIE 2: MOMENTUM BREAKOUT (Meeliften met de storm) ---
            # Als de trigger positief was, gaan we LONG (winst bij stijging). Anders SHORT.
            if trigger_return > 0:
                strat2_pnl = future_return
            else:
                strat2_pnl = -future_return
            pnl_momentum += strat2_pnl

            # --- STRATEGIE 3: VOLATILITY STRADDLE (Optie-proxy) ---
            # Winst is de absolute beweging (ongeacht de richting) minus de geschatte optiepremie (0.04% cost)
            option_premium_cost = 0.0004 
            strat3_pnl = abs(future_return) - option_premium_cost
            pnl_volatility_straddle += strat3_pnl

    # 3. Genereer Institutioneel Performance Rapport
    print("\n" + "="*60)
    print("📊 MANTRA STRATEGY RESEARCH REPORT (PERFORMANCE SUMMARY)")
    print("="*60)
    print(f"🔹 Total Anomaly Signals Captured (Post-Cooldown): {trade_count}")
    print(f"🔹 Simulated Position Holding Period:             {holding_period} Minutes")
    print("-"*60)
    
    # We vermenigvuldigen met 100 voor procentuele weergave
    print(f"🔄 Strategy 1: Mean-Reversion Spread PnL:        {pnl_mean_reversion * 100:+.4f}%")
    print(f"🚀 Strategy 2: Momentum Breakout PnL:           {pnl_momentum * 100:+.4f}%")
    print(f"🎭 Strategy 3: Options Volatility Straddle PnL:  {pnl_volatility_straddle * 100:+.4f}%")
    print("="*60)
    
    # Strategisch Advies op basis van data
    results = {
        "Mean-Reversion": pnl_mean_reversion,
        "Momentum": pnl_momentum,
        "Volatility-Straddle": pnl_volatility_straddle
    }
    best_strat = max(results, key=results[k] for k in results)
    
    print(f"🔬 CRO RESEARCH VERDICT: The optimal regime deployment for this market window")
    print(f"   is the [{best_strat}] engine (Total Return: {results[best_strat]*100:+.3f}%).\n")

if __name__ == "__main__":
    run_multi_strategy_backtest()
