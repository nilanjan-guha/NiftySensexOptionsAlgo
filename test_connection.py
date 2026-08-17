# import os
# from datetime import datetime, timedelta

# from dotenv import load_dotenv
# from kiteconnect import KiteConnect

# load_dotenv()

# api_key = os.getenv("KITE_API_KEY")

# with open("access_token.txt", "r") as file:
#     access_token = file.read().strip()

# kite = KiteConnect(api_key=api_key)
# kite.set_access_token(access_token)

# # NIFTY 50 instrument token
# NIFTY_TOKEN = 256265

# to_date = datetime.now()
# from_date = to_date - timedelta(days=5)

# print("Fetching 5-minute NIFTY candles...")

# candles = kite.historical_data(
#     instrument_token=NIFTY_TOKEN,
#     from_date=from_date,
#     to_date=to_date,
#     interval="5minute"
# )

# print("\nTotal candles:", len(candles))

# if candles:
#     print("\nLatest 5 candles:")

#     for candle in candles[-5:]:
#         print(
#             candle["date"],
#             "| Open:", candle["open"],
#             "| High:", candle["high"],
#             "| Low:", candle["low"],
#             "| Close:", candle["close"],
#             "| Volume:", candle["volume"]
#         )
# else:
#     print("No candle data received.")





















import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from kiteconnect import KiteConnect


# =========================================================
# LOAD ZERODHA CREDENTIALS
# =========================================================

load_dotenv()

api_key = os.getenv("KITE_API_KEY")

if not api_key:
    print("ERROR: KITE_API_KEY not found in .env")
    raise SystemExit(1)

try:
    with open("access_token.txt", "r", encoding="utf-8") as file:
        access_token = file.read().strip()
except FileNotFoundError:
    print("ERROR: access_token.txt not found")
    raise SystemExit(1)

if not access_token:
    print("ERROR: access_token.txt is empty")
    raise SystemExit(1)


# =========================================================
# ZERODHA CONNECTION
# =========================================================

print("\n==========================================")
print("        ZERODHA CONNECTION TEST")
print("==========================================")

kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)


# =========================================================
# TEST LOGIN
# =========================================================

try:
    profile = kite.profile()

    print("\nZERODHA CONNECTION: SUCCESS")
    print("User :", profile.get("user_name"))
    print("User ID :", profile.get("user_id"))

except Exception as exc:
    print("\nZERODHA CONNECTION: FAILED")
    print(type(exc).__name__)
    print(str(exc))
    raise SystemExit(1)


# =========================================================
# INDEX TOKENS
# =========================================================

NIFTY_TOKEN = 256265


# =========================================================
# FIND SENSEX TOKEN
# =========================================================

def find_sensex_token():
    print("\nFinding SENSEX instrument...")

    try:
        instruments = kite.instruments("BSE")
    except Exception as exc:
        print("Could not download BSE instruments.")
        print(type(exc).__name__)
        print(str(exc))
        return None

    for instrument in instruments:

        name = str(
            instrument.get("name", "")
        ).upper()

        tradingsymbol = str(
            instrument.get("tradingsymbol", "")
        ).upper()

        instrument_type = str(
            instrument.get("instrument_type", "")
        ).upper()

        # SENSEX index normally appears as an INDEX instrument.
        if (
            (
                name == "SENSEX"
                or tradingsymbol == "SENSEX"
            )
            and instrument_type == "INDEX"
        ):
            return instrument.get("instrument_token")

    # Fallback: search by symbol/name.
    for instrument in instruments:

        name = str(
            instrument.get("name", "")
        ).upper()

        tradingsymbol = str(
            instrument.get("tradingsymbol", "")
        ).upper()

        if (
            "SENSEX" in name
            or "SENSEX" in tradingsymbol
        ):
            return instrument.get("instrument_token")

    return None


SENSEX_TOKEN = find_sensex_token()

if SENSEX_TOKEN is None:
    print("\nERROR: Could not find SENSEX instrument token.")
    raise SystemExit(1)

print("SENSEX token:", SENSEX_TOKEN)


# =========================================================
# FETCH CANDLES
# =========================================================

def fetch_candles(
    token,
    index_name,
):

    to_date = datetime.now()

    from_date = (
        to_date
        - timedelta(days=5)
    )

    print("\n------------------------------------------")
    print(f"Fetching 5-minute {index_name} candles...")
    print("------------------------------------------")

    try:

        candles = kite.historical_data(
            instrument_token=token,
            from_date=from_date,
            to_date=to_date,
            interval="5minute",
        )

    except Exception as exc:

        print(
            f"{index_name} DATA ERROR"
        )

        print(
            type(exc).__name__
        )

        print(
            str(exc)
        )

        return []

    print(
        f"Total {index_name} candles:",
        len(candles),
    )

    return candles


# =========================================================
# PRINT LATEST CANDLES
# =========================================================

def print_latest_candles(
    candles,
    index_name,
):

    if not candles:

        print(
            f"\nNo {index_name} candle data received."
        )

        return

    print(
        f"\nLatest 5 {index_name} candles:"
    )

    print(
        "------------------------------------------"
    )

    for candle in candles[-5:]:

        print(
            candle["date"],
            "| Open:",
            candle["open"],
            "| High:",
            candle["high"],
            "| Low:",
            candle["low"],
            "| Close:",
            candle["close"],
            "| Volume:",
            candle["volume"],
        )


# =========================================================
# NIFTY
# =========================================================

nifty_candles = fetch_candles(
    NIFTY_TOKEN,
    "NIFTY",
)

print_latest_candles(
    nifty_candles,
    "NIFTY",
)


# =========================================================
# SENSEX
# =========================================================

sensex_candles = fetch_candles(
    SENSEX_TOKEN,
    "SENSEX",
)

print_latest_candles(
    sensex_candles,
    "SENSEX",
)


# =========================================================
# FINAL RESULT
# =========================================================

print("\n==========================================")
print("          CONNECTION TEST COMPLETE")
print("==========================================")

if nifty_candles:
    print("NIFTY  : OK")
else:
    print("NIFTY  : FAILED")

if sensex_candles:
    print("SENSEX : OK")
else:
    print("SENSEX : FAILED")

print("==========================================")
