import requests
import csv
from datetime import datetime, timezone
import subprocess
import os
import traceback

# ---- LOGGING ----
log_file = r"C:\Users\admin\Downloads\token-price-logger\log.txt"

def log(message):
    with open(log_file, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")


log("=== Script started ===")

# ---- CONFIG ----
CSV_PATH = r"C:\Users\admin\Downloads\token-price-logger\data\prices.csv"
REPO_PATH = r"C:\Users\admin\Downloads\token-price-logger"
PYTHON_PATH = r"C:\Users\admin\AppData\Local\Programs\Python\Python313\python.exe"

# ---- FETCH PRICE ----
def fetch_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        r = requests.get(url, timeout=10)
        data = r.json()
        price = float(data["price"])
        log(f"Fetched price: {price}")
        return price
    except Exception as e:
        log(f"Fetch price ERROR: {e}")
        log(traceback.format_exc())
        return None


# ---- APPEND TO CSV ----
def save_price(price):
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        new_row = [now, price]

        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(new_row)

        log("Price written to CSV")
    except Exception as e:
        log(f"CSV write ERROR: {e}")
        log(traceback.format_exc())


# ---- RUN GIT COMMAND ----
def git(cmd):
    try:
        result = subprocess.run(cmd, cwd=REPO_PATH, capture_output=True, text=True, shell=True)
        if result.stdout:
            log("GIT OUT: " + result.stdout.strip())
        if result.stderr:
            log("GIT ERR: " + result.stderr.strip())
    except Exception as e:
        log(f"GIT ERROR: {e}")
        log(traceback.format_exc())


# ---- MAIN LOGIC ----
try:
    price = fetch_price()
    if price is not None:
        save_price(price)

        git("git add .")
        git(f'git commit -m "Auto update price {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"')
        git("git push origin main")
    else:
        log("Price fetch failed. No git actions executed.")

except Exception as e:
    log("MAIN ERROR:")
    log(str(e))
    log(traceback.format_exc())

log("=== Script finished ===")
