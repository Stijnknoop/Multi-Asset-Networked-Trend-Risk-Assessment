import http.client
import json
import pandas as pd
import os
import argparse
import sys
from datetime import datetime

# --- Argument Parser Configuration ---
parser = argparse.ArgumentParser(description='Fetch high-frequency market data from Capital.com.')
parser.add_argument('--epic', type=str, required=True, help='The EPIC symbol (e.g., OIL_CRUDE, GOLD, or US500)')
args = parser.parse_args()

EPIC_SYMBOL = args.epic
DATA_DIR = "data"  # Centralized data repository folder

# Global Session Tokens
SECURITY_TOKEN = None
CST = None

def load_credentials():
    """Extracts API access credentials from environmental variables securely."""
    try:
        return {
            "identifier": os.environ["IDENTIFIER"],
            "password": os.environ["PASSWORD"],
            "api_key": os.environ["X_CAP_API_KEY"]
        }
    except KeyError as e:
        print(f"❌ Initialization Error: Missing environmental variable {e}")
        print("👉 Ensure IDENTIFIER, PASSWORD, and X_CAP_API_KEY are configured in GitHub Secrets.")
        sys.exit(1)

def fetch_session_tokens():
    """Authenticates with the API platform and retrieves dynamic session headers."""
    global SECURITY_TOKEN, CST
    creds = load_credentials()
    
    conn = http.client.HTTPSConnection("api-capital.backend-capital.com")
    payload = json.dumps({"identifier": creds['identifier'], "password": creds['password']})
    headers = {"Content-Type": "application/json", "X-CAP-API-KEY": creds['api_key']}

    print(f"🔐 Authenticating session for asset execution...")
    conn.request("POST", "/api/v1/session", payload, headers)
    res = conn.getresponse()
    
    # Fail-fast block to prevent downstream downstream header errors
    if res.status != 200:
        print(f"❌ Authentication Failed: {res.status} {res.reason}")
        print("👉 Please verify that your registered repository credentials/secrets are valid.")
        sys.exit(1)
        
    CST = res.getheader("CST")
    SECURITY_TOKEN = res.getheader("X-SECURITY-TOKEN")
    
    if not CST or not SECURITY_TOKEN:
        print("❌ Protocol Error: Session established but critical telemetry headers (CST/X-SECURITY-TOKEN) are missing.")
        sys.exit(1)
        
    return SECURITY_TOKEN, CST

def fetch_market_prices():
    """Queries the backend endpoint for the latest 1000 candles at a 1-minute interval."""
    global SECURITY_TOKEN, CST
    conn = http.client.HTTPSConnection("api-capital.backend-capital.com")
    payload = ''
    headers = {'X-SECURITY-TOKEN': SECURITY_TOKEN, 'CST': CST}
    
    resolution = "MINUTE"
    max_candles = 1000
    url = f"/api/v1/prices/{EPIC_SYMBOL}?resolution={resolution}&max={max_candles}"

    conn.request("GET", url, payload, headers)
    res = conn.getresponse()
    
    if res.status != 200:
        print(f"❌ API Query Failure for {EPIC_SYMBOL}: {res.status} {res.reason}")
        sys.exit(1)

    ohlc_data = json.loads(res.read().decode("utf-8"))
    prices = ohlc_data.get('prices', [])

    df = pd.json_normalize(prices)
    if df.empty:
        print(f"⚠️ Empty Frame Warning: No active pricing arrays returned for {EPIC_SYMBOL}")
        return pd.DataFrame()

    # Filter and map structural market features
    df = df[[  
        'snapshotTime',
        'openPrice.bid', 'highPrice.bid', 'lowPrice.bid', 'closePrice.bid',
        'openPrice.ask', 'highPrice.ask', 'lowPrice.ask', 'closePrice.ask',
        'lastTradedVolume'
    ]]
    df.columns = [
        'time',
        'open_bid', 'high_bid', 'low_bid', 'close_bid',
        'open_ask', 'high_ask', 'low_ask', 'close_ask',
        'volume'
    ]
    
    # Guarantee unified ISO time format strings for subsequent cross-asset merging
    df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    return df

if __name__ == "__main__":
    print(f"🚀 Initializing Data Ingestion Engine for Target Epic: {EPIC_SYMBOL}")
    
    # Establish local data storage structures
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"📂 Storage Architecture initialized at: {DATA_DIR}")

    # Process execution chain
    fetch_session_tokens()
    df_new = fetch_market_prices()

    if not df_new.empty:
        filename = os.path.join(DATA_DIR, f"{EPIC_SYMBOL}.csv")
        
        # Incremental state integration logic
        if os.path.exists(filename):
            print(f"🔄 Existing master file found for {EPIC_SYMBOL}. Executing delta append...")
            df_existing = pd.read_csv(filename)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            print(f"📝 Initializing fresh time-series ledger for {EPIC_SYMBOL}...")
            df_combined = df_new

        # Core Data Engineering: Resolve transactional overlaps and preserve chronological line
        df_combined = df_combined.drop_duplicates(subset=['time'], keep='last')
        df_combined = df_combined.sort_values(by='time').reset_index(drop=True)

        # Commit back to data storage system
        df_combined.to_csv(filename, index=False)
        print(f"✅ State Matrix updated successfully ({len(df_combined)} records total): {filename}\n")
