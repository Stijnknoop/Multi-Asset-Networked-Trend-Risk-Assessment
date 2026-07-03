import http.client
import json
import pandas as pd
import os
import argparse
import sys
from datetime import datetime

# --- Argument Parser ---
parser = argparse.ArgumentParser(description='Fetch market data.')
parser.add_argument('--epic', type=str, required=True, help='The EPIC symbol (e.g., OIL_CRUDE, GOLD, or UK100)')
args = parser.parse_args()

EPIC_SYMBOL = args.epic
DATA_DIR = "data"  # Centrale datamap voor het project

# Globale tokens
SECURITY_TOKEN = None
CST = None

def load_credentials():
    return {
        "identifier": os.environ["IDENTIFIER"],
        "password": os.environ["PASSWORD"],
        "api_key": os.environ["X_CAP_API_KEY"]
    }

def tokens():
    global SECURITY_TOKEN, CST
    creds = load_credentials()
    
    conn = http.client.HTTPSConnection("api-capital.backend-capital.com")
    payload = json.dumps({"identifier": creds['identifier'], "password": creds['password']})
    headers = {"Content-Type": "application/json", "X-CAP-API-KEY": creds['api_key']}

    conn.request("POST", "/api/v1/session", payload, headers)
    res = conn.getresponse()
    CST = res.getheader("CST")
    SECURITY_TOKEN = res.getheader("X-SECURITY-TOKEN")
    return SECURITY_TOKEN, CST

def data_nu():
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
        print(f"❌ Fout bij ophalen data voor {EPIC_SYMBOL}: {res.status} {res.reason}")
        sys.exit(1)

    ohlc = json.loads(res.read().decode("utf-8"))
    prices = ohlc.get('prices', [])

    df = pd.json_normalize(prices)
    if df.empty:
        print(f"⚠️ Geen data ontvangen voor {EPIC_SYMBOL}")
        return pd.DataFrame()

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
    
    # Zorg dat de tijdkolom als string of datetime consistent is voor de merge
    df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%d %H:%M:%S')
    return df

if __name__ == "__main__":
    print(f"🚀 Starten van data-ingestion voor: {EPIC_SYMBOL}")
    
    # Zorg dat de centrale data-map bestaat
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"📂 Centrale datamap aangemaakt: {DATA_DIR}")

    # Haal tokens en nieuwe data op
    tokens()
    df_new = data_nu()

    if not df_new.empty:
        filename = os.path.join(DATA_DIR, f"{EPIC_SYMBOL}.csv")
        
        # Incrementele opslag-logica: controleren of bestand al bestaat
        if os.path.exists(filename):
            print(f"🔄 Bestaande data gevonden voor {EPIC_SYMBOL}. Samenvoegen en ontdubbelen...")
            df_existing = pd.read_csv(filename)
            
            # Combineer oude en nieuwe data
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            print(f"📝 Geen bestaand bestand gevonden. Nieuwe tabel initialiseren voor {EPIC_SYMBOL}...")
            df_combined = df_new

        # --- HET MAGISCHE DATA ENGINEERING STUK ---
        # Ontdubbel op basis van de unieke tijdstempels en sorteer chronologisch
        df_combined = df_combined.drop_duplicates(subset=['time'], keep='last')
        df_combined = df_combined.sort_values(by='time').reset_index(drop=True)

        # Overschrijf de mastertabel met de geüpdatete en schone dataset
        df_combined.to_csv(filename, index=False)
        print(f"✅ Master-tabel succesvol bijgewerkt ({len(df_combined)} rijen totaal): {filename}")
