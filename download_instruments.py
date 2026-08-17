import os
import csv

from dotenv import load_dotenv
from kiteconnect import KiteConnect


# =========================================================
# CONFIG
# =========================================================

SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

OUTPUT_FILE = os.path.join(
    SCRIPT_DIR,
    "instruments.csv"
)


# =========================================================
# LOAD ZERODHA CREDENTIALS
# =========================================================

load_dotenv()

API_KEY = os.getenv("KITE_API_KEY")

if not API_KEY:
    print("ERROR: KITE_API_KEY not found in .env")
    raise SystemExit(1)

ACCESS_TOKEN_FILE = os.path.join(
    SCRIPT_DIR,
    "access_token.txt"
)

try:
    with open(
        ACCESS_TOKEN_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        ACCESS_TOKEN = file.read().strip()

except FileNotFoundError:
    print("ERROR: access_token.txt not found")
    raise SystemExit(1)

if not ACCESS_TOKEN:
    print("ERROR: access_token.txt is empty")
    raise SystemExit(1)


# =========================================================
# CONNECT TO ZERODHA
# =========================================================

print()
print("==========================================")
print("     ZERODHA INSTRUMENT DOWNLOADER")
print("==========================================")

kite = KiteConnect(
    api_key=API_KEY
)

kite.set_access_token(
    ACCESS_TOKEN
)

try:
    profile = kite.profile()

    print()
    print("ZERODHA CONNECTION: SUCCESS")
    print("User :", profile.get("user_name"))
    print("User ID :", profile.get("user_id"))

except Exception as exc:
    print()
    print("ZERODHA CONNECTION: FAILED")
    print(type(exc).__name__)
    print(str(exc))
    raise SystemExit(1)


# =========================================================
# DOWNLOAD NFO
# =========================================================

print()
print("------------------------------------------")
print("Downloading NFO instruments...")
print("------------------------------------------")

try:
    nfo_instruments = kite.instruments("NFO")

except Exception as exc:
    print("NFO DOWNLOAD FAILED")
    print(type(exc).__name__)
    print(str(exc))
    raise SystemExit(1)

print(
    "NFO instruments:",
    len(nfo_instruments)
)


# =========================================================
# DOWNLOAD BFO
# =========================================================

print()
print("------------------------------------------")
print("Downloading BFO instruments...")
print("------------------------------------------")

try:
    bfo_instruments = kite.instruments("BFO")

except Exception as exc:
    print("BFO DOWNLOAD FAILED")
    print(type(exc).__name__)
    print(str(exc))
    raise SystemExit(1)

print(
    "BFO instruments:",
    len(bfo_instruments)
)


# =========================================================
# COMBINE
# =========================================================

all_instruments = (
    nfo_instruments
    +
    bfo_instruments
)

print()
print("------------------------------------------")
print("Combining instruments...")
print("------------------------------------------")

print(
    "Total instruments:",
    len(all_instruments)
)


# =========================================================
# CSV COLUMNS
# =========================================================

fieldnames = [
    "instrument_token",
    "exchange_token",
    "tradingsymbol",
    "name",
    "last_price",
    "expiry",
    "strike",
    "tick_size",
    "lot_size",
    "instrument_type",
    "segment",
    "exchange",
]


# =========================================================
# WRITE CSV
# =========================================================

print()
print("------------------------------------------")
print("Creating instruments.csv...")
print("------------------------------------------")

try:

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for instrument in all_instruments:

            writer.writerow(
                {
                    field: instrument.get(
                        field,
                        ""
                    )
                    for field in fieldnames
                }
            )

except Exception as exc:

    print("CSV CREATION FAILED")
    print(type(exc).__name__)
    print(str(exc))
    raise SystemExit(1)


# =========================================================
# VERIFY
# =========================================================

nifty_futures = [
    x
    for x in nfo_instruments
    if x.get("name") == "NIFTY"
    and x.get("instrument_type") == "FUT"
]

sensex_futures = [
    x
    for x in bfo_instruments
    if x.get("name") == "SENSEX"
    and x.get("instrument_type") == "FUT"
]


# =========================================================
# RESULT
# =========================================================

print()
print("==========================================")
print("       INSTRUMENT DOWNLOAD COMPLETE")
print("==========================================")

print()
print("File created:")
print(OUTPUT_FILE)

print()
print("NIFTY futures found:")
print(len(nifty_futures))

print("SENSEX futures found:")
print(len(sensex_futures))

print()

if nifty_futures:
    print("Nearest NIFTY future:")
    print(
        nifty_futures[0]["tradingsymbol"]
    )

if sensex_futures:
    print("Nearest SENSEX future:")
    print(
        sensex_futures[0]["tradingsymbol"]
    )

print()
print("==========================================")