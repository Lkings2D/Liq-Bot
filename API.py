import time
from datetime import datetime
import uuid
import requests

API_BASE_URL = "https://sandbox.myfundedperpetuals.com/v1"
API_KEY = "YOUR_API_KEY_HERE"
TARGET_ACCOUNT_NUMBER = "FP-123456"  # Replace with your actual target account number

def get_target_account_id():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.get(f"{API_BASE_URL}/accounts", headers=headers)
    if response.status_code == 200:
        accounts = response.json().get("data", [])
        for acc in accounts:
            if acc.get("account_number") == TARGET_ACCOUNT_NUMBER or acc.get("name") == TARGET_ACCOUNT_NUMBER:
                return acc.get("id")
        for acc in accounts:
            if TARGET_ACCOUNT_NUMBER in str(acc):
                return acc.get("id")
    return None

def close_all_positions():
    account_id = get_target_account_id()
    if not account_id:
        print(f"[{datetime.now()}] ERROR: Could not resolve internal ID for {TARGET_ACCOUNT_NUMBER}")
        return

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        list_url = f"{API_BASE_URL}/positions?account_id={account_id}"
        response = requests.get(list_url, headers=headers)
        
        if response.status_code != 200:
            print(f"[{datetime.now()}] ERROR: Failed to fetch positions: {response.text}")
            return
            
        positions = response.json().get("data", [])
        if not positions:
            print(f"[{datetime.now()}] No open positions found to close on {TARGET_ACCOUNT_NUMBER}.")
            return

        for pos in positions:
            pos_id = pos.get("id")
            symbol = pos.get("symbol", "UNKNOWN")
            
            # Scenario handler: Dynamically fetch live price for any asset
            current_price = pos.get("mark_price") or pos.get("entry_price")
            if not current_price or float(current_price) <= 0:
                print(f"[{datetime.now()}] ERROR: Invalid price detected for {symbol}")
                continue
                
            close_url = f"{API_BASE_URL}/positions/{pos_id}/close?account_id={account_id}"
            
            close_headers = headers.copy()
            close_headers["Idempotency-Key"] = str(uuid.uuid4())
            
            payload = {
                "type": "market",
                "expected_price": float(current_price)
            }
            
            close_response = requests.post(close_url, headers=close_headers, json=payload)
            if close_response.status_code in [200, 201]:
                print(f"[{datetime.now()}] SUCCESS: Closed {symbol} position ID {pos_id} at price {current_price}")
            else:
                print(f"[{datetime.now()}] ERROR closing position {pos_id}: {close_response.text}")
                
    except Exception as e:
        print(f"[{datetime.now()}] EXCEPTION: {e}")

def run_schedule():
    print("Starting pre-midnight auto-liquidation worker...")
    while True:
        now = datetime.now()
        
        # Production trigger: 11:55 PM (23:55)
        if now.hour == 23 and now.minute == 55:
            print("11:55 PM reached! Triggering emergency position closure...")
            close_all_positions()
            time.sleep(70) # Prevents duplicate triggers within the same minute window
            
        time.sleep(10)

if __name__ == "__main__":
    run_schedule()