"""
Bluestock Fintech - Mutual Fund Analytics Platform
Script: scripts/live_nav_fetch.py
Objective: Live NAV ingestion from AMFI-compliant API (mfapi.in) for selected schemes.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import requests
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("LiveNAVFetch")

BASE_URL = "https://api.mfapi.in/mf"
RAW_API_DIR = os.path.join("data", "raw", "api_responses")

# Five confirmed benchmark schemes from project specification
TARGET_SCHEMES = {
    125497: "HDFC Top 100",
    119551: "SBI Bluechip",
    120503: "ICICI Bluechip",
    118632: "Nippon Large Cap",
    119092: "Axis Bluechip"
}

def ensure_dirs():
    os.makedirs(RAW_API_DIR, exist_ok=True)

def fetch_scheme_nav(amfi_code: int, retries: int = 1, timeout: int = 3, use_cache: bool = True) -> Optional[Dict[str, Any]]:
    """
    Fetch historical NAV series from api.mfapi.in with retries, validation, and caching.
    """
    ensure_dirs()
    cache_path = os.path.join(RAW_API_DIR, f"{amfi_code}.json")
    
    if use_cache and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("status") == "SUCCESS" and "data" in data:
                    logger.info(f"Loaded cached NAV for AMFI code {amfi_code} ({data.get('meta', {}).get('scheme_name')})")
                    return data
        except Exception as e:
            logger.warning(f"Error reading cache for {amfi_code}: {e}. Retrying live fetch.")

    url = f"{BASE_URL}/{amfi_code}"
    headers = {"User-Agent": "Bluestock-Fintech-Analytics/1.0"}
    
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Fetching NAV for AMFI code {amfi_code} from {url} (Attempt {attempt}/{retries})...")
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "SUCCESS" and "data" in data and len(data["data"]) > 0:
                    meta = data.get("meta", {})
                    logger.info(f"Successfully fetched {len(data['data'])} NAV records for {meta.get('scheme_name', amfi_code)}")
                    # Save raw response
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    return data
                else:
                    logger.warning(f"API returned status '{data.get('status')}' for scheme {amfi_code}")
            else:
                logger.warning(f"HTTP {response.status_code} for scheme {amfi_code}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Network error on attempt {attempt} for {amfi_code}: {e}")
            if attempt < retries:
                time.sleep(2 * attempt)
                
    logger.error(f"Failed to fetch live NAV for scheme {amfi_code} after {retries} attempts.")
    return None

def parse_nav_to_dataframe(api_data: Dict[str, Any], amfi_code: int) -> pd.DataFrame:
    """
    Parse mfapi.in response into standard DataFrame format [amfi_code, date, nav]
    """
    raw_nav_list = api_data.get("data", [])
    records = []
    for item in raw_nav_list:
        try:
            # mfapi format is DD-MM-YYYY
            d_str = item.get("date")
            n_str = item.get("nav")
            if d_str and n_str:
                dt = datetime.strptime(d_str, "%d-%m-%Y")
                nav_val = float(n_str)
                if nav_val > 0:
                    records.append({
                        "amfi_code": amfi_code,
                        "date": dt.strftime("%Y-%m-%d"),
                        "nav": nav_val
                    })
        except Exception:
            continue
            
    df = pd.DataFrame(records)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df

def fetch_all_target_schemes(use_cache: bool = True) -> Dict[int, pd.DataFrame]:
    """
    Fetch NAV for all five designated target schemes.
    """
    results = {}
    for code, name in TARGET_SCHEMES.items():
        data = fetch_scheme_nav(code, use_cache=use_cache)
        if data:
            df = parse_nav_to_dataframe(data, code)
            results[code] = df
            logger.info(f"Parsed {len(df)} NAV rows for {name} ({code})")
        else:
            logger.warning(f"Could not retrieve live NAV for {name} ({code}). Will rely on calibrated synthetic series.")
    return results

if __name__ == "__main__":
    ensure_dirs()
    print("Testing Live NAV Fetch for 5 specified schemes...")
    res = fetch_all_target_schemes(use_cache=True)
    for code, df in res.items():
        print(f"Scheme {code} ({TARGET_SCHEMES.get(code)}): {len(df)} records. Latest: {df.iloc[-1].to_dict() if not df.empty else 'N/A'}")
