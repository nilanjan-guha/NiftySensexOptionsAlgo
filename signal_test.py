# import os
# from datetime import date

# import pandas as pd
# from dotenv import load_dotenv
# from kiteconnect import KiteConnect

# from strategy import (
#     calculate_indicators,
#     bullish_breakout,
#     bearish_breakout,
#     bullish_pullback,
#     bearish_pullback,
#     premium_bullish_breakout,
#     premium_bullish_pullback,
#     bullish_confirmation,
#     get_setup_strength,
#     recommended_rr,
#     calculate_dynamic_risk,
#     MAX_PULLBACK_CANDLES,
#     MAX_SETUP_GAP_MINUTES,
#     PULLBACK_BUFFER,
# )


# # =========================================================
# # CONFIG
# # =========================================================

# NIFTY_INDEX_TOKEN = 256265
# STRIKE_INTERVAL = 50

# LOT_SIZE = 65
# LOTS = 1
# QUANTITY = LOT_SIZE * LOTS


# # =========================================================
# # ZERODHA
# # =========================================================

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# load_dotenv()

# API_KEY = os.getenv("KITE_API_KEY")

# if not API_KEY:
#     print("ERROR: KITE_API_KEY not found in .env")
#     raise SystemExit(1)

# try:
#     with open(
#         os.path.join(SCRIPT_DIR, "access_token.txt"),
#         "r",
#         encoding="utf-8",
#     ) as f:
#         ACCESS_TOKEN = f.read().strip()
# except Exception:
#     print("ERROR: access_token.txt not found")
#     raise SystemExit(1)

# kite = KiteConnect(api_key=API_KEY)
# kite.set_access_token(ACCESS_TOKEN)


# # =========================================================
# # TODAY
# # =========================================================

# def get_today_market_range():
#     now = pd.Timestamp.now(tz="Asia/Kolkata")

#     market_open = pd.Timestamp(
#         year=now.year,
#         month=now.month,
#         day=now.day,
#         hour=9,
#         minute=15,
#         tz="Asia/Kolkata",
#     )

#     return market_open, now


# def fetch_today_candles(token):
#     market_open, now = get_today_market_range()

#     if now < market_open:
#         print("Market has not opened yet.")
#         return []

#     try:
#         return kite.historical_data(
#             instrument_token=token,
#             from_date=market_open.to_pydatetime(),
#             to_date=now.to_pydatetime(),
#             interval="5minute",
#         )
#     except Exception as exc:
#         print("\nZERODHA DATA ERROR")
#         print(type(exc).__name__)
#         print(str(exc))
#         return []


# def remove_current_candle(df):
#     if df.empty:
#         return df

#     now = pd.Timestamp.now(tz="Asia/Kolkata")
#     current_start = now.floor("5min")

#     return df[
#         df["date"] < current_start
#     ].copy().reset_index(drop=True)


# # =========================================================
# # NIFTY SETUP
# # =========================================================

# def find_nifty_setup(df):
#     if len(df) < 3:
#         return None

#     start = max(0, len(df) - 35)

#     # Newest first. This is for live signal generation.
#     for i in range(len(df) - 2, start - 1, -1):
#         breakout = df.iloc[i]

#         if bullish_breakout(breakout):
#             direction = "CE"
#             pullback_fn = bullish_pullback

#         elif bearish_breakout(breakout):
#             direction = "PE"
#             pullback_fn = bearish_pullback

#         else:
#             continue

#         for offset in range(1, MAX_PULLBACK_CANDLES + 1):
#             j = i + offset

#             if j >= len(df):
#                 break

#             pullback = df.iloc[j]

#             if not pullback_fn(
#                 pullback,
#                 PULLBACK_BUFFER,
#             ):
#                 continue

#             # The pullback candle must be closed.
#             return {
#                 "direction": direction,
#                 "breakout": breakout,
#                 "pullback": pullback,
#             }

#     return None


# # =========================================================
# # OPTION
# # =========================================================

# def find_option(direction, spot):
#     atm = round(spot / STRIKE_INTERVAL) * STRIKE_INTERVAL

#     try:
#         instruments = kite.instruments("NFO")
#     except Exception as exc:
#         print("Could not download NFO instruments.")
#         print(str(exc))
#         return None

#     today = date.today()
#     selected = None
#     selected_expiry = None

#     for instrument in instruments:
#         try:
#             if instrument.get("name") != "NIFTY":
#                 continue

#             if instrument.get("instrument_type") != direction:
#                 continue

#             if float(instrument.get("strike", 0)) != float(atm):
#                 continue

#             expiry = instrument.get("expiry")

#             if not expiry or expiry < today:
#                 continue

#             if (
#                 selected_expiry is None
#                 or expiry < selected_expiry
#             ):
#                 selected = instrument
#                 selected_expiry = expiry

#         except Exception:
#             continue

#     return selected


# # =========================================================
# # PREMIUM SETUP
# # =========================================================

# def find_premium_setup(
#     premium_df,
#     nifty_breakout_time,
#     nifty_pullback_time,
# ):
#     if premium_df.empty:
#         return None

#     candidates = premium_df[
#         premium_df["date"] >= nifty_breakout_time
#     ].reset_index(drop=True)

#     for i in range(len(candidates) - 2, -1, -1):
#         premium_breakout = candidates.iloc[i]

#         if not premium_bullish_breakout(
#             premium_breakout
#         ):
#             continue

#         gap = (
#             pd.Timestamp(premium_breakout["date"])
#             - nifty_breakout_time
#         ).total_seconds() / 60

#         if gap < 0 or gap > MAX_SETUP_GAP_MINUTES:
#             continue

#         for offset in range(
#             1,
#             MAX_PULLBACK_CANDLES + 1
#         ):
#             j = i + offset

#             if j >= len(candidates) - 1:
#                 break

#             premium_pullback = candidates.iloc[j]

#             if not premium_bullish_pullback(
#                 premium_pullback,
#                 PULLBACK_BUFFER,
#             ):
#                 continue

#             pullback_time = pd.Timestamp(
#                 premium_pullback["date"]
#             )

#             gap2 = (
#                 pullback_time
#                 - nifty_pullback_time
#             ).total_seconds() / 60

#             if gap2 < 0 or gap2 > MAX_SETUP_GAP_MINUTES:
#                 continue

#             confirmation = candidates.iloc[j + 1]

#             if not bullish_confirmation(
#                 premium_pullback,
#                 confirmation,
#             ):
#                 continue

#             return {
#                 "breakout": premium_breakout,
#                 "pullback": premium_pullback,
#                 "confirmation": confirmation,
#             }

#     return None


# # =========================================================
# # MAIN
# # =========================================================

# print("\n==========================================")
# print("       NIFTY OPTIONS IMPROVED SIGNAL")
# print("==========================================")

# nifty_raw = fetch_today_candles(NIFTY_INDEX_TOKEN)

# if not nifty_raw:
#     print("No NIFTY candles returned.")
#     raise SystemExit(1)

# nifty_df = calculate_indicators(nifty_raw)
# nifty_df = remove_current_candle(nifty_df)

# if nifty_df.empty:
#     print("No completed NIFTY candles.")
#     raise SystemExit(1)

# latest = nifty_df.iloc[-1]

# print("\nLATEST NIFTY")
# print("Time :", latest["date"])
# print("Open :", latest["open"])
# print("High :", latest["high"])
# print("Low  :", latest["low"])
# print("Close:", latest["close"])
# print("EMA20:", round(float(latest["ema20"]), 2))
# print("EMA50:", round(float(latest["ema50"]), 2))
# print("VWAP :", round(float(latest["vwap"]), 2))
# print("RSI  :", round(float(latest["rsi14"]), 2))
# print("ADX  :", round(float(latest["adx14"]), 2))
# print("ATR  :", round(float(latest["atr14"]), 2))


# nifty_setup = find_nifty_setup(nifty_df)

# if nifty_setup is None:
#     print("\nNIFTY SIGNAL: NO TRADE")
#     raise SystemExit(0)

# direction = nifty_setup["direction"]
# nifty_breakout = nifty_setup["breakout"]
# nifty_pullback = nifty_setup["pullback"]

# print("\n==========================================")
# print("       NIFTY SETUP CONFIRMED")
# print("==========================================")
# print("Direction:", direction)
# print("Breakout :", nifty_breakout["date"])
# print("Pullback :", nifty_pullback["date"])


# # ---------------------------------------------------------
# # SPOT
# # ---------------------------------------------------------

# try:
#     quote = kite.quote(["NSE:NIFTY 50"])
#     spot = float(
#         quote["NSE:NIFTY 50"]["last_price"]
#     )
# except Exception as exc:
#     print("Could not fetch NIFTY spot.")
#     print(str(exc))
#     raise SystemExit(1)


# option = find_option(direction, spot)

# if option is None:
#     print("Option not found.")
#     raise SystemExit(1)

# option_symbol = option["tradingsymbol"]
# option_token = option["instrument_token"]

# print("\nSELECTED OPTION")
# print("Symbol :", option_symbol)
# print("Expiry :", option["expiry"])
# print("Token  :", option_token)
# print("Qty    :", QUANTITY)


# # ---------------------------------------------------------
# # PREMIUM
# # ---------------------------------------------------------

# premium_raw = fetch_today_candles(option_token)

# if not premium_raw:
#     print("No premium candles returned.")
#     raise SystemExit(1)

# premium_df = calculate_indicators(premium_raw)
# premium_df = remove_current_candle(premium_df)

# if premium_df.empty:
#     print("No completed premium candles.")
#     raise SystemExit(1)

# latest_premium = premium_df.iloc[-1]

# print("\nLATEST PREMIUM")
# print("Time :", latest_premium["date"])
# print("Open :", latest_premium["open"])
# print("High :", latest_premium["high"])
# print("Low  :", latest_premium["low"])
# print("Close:", latest_premium["close"])
# print("EMA20:", round(float(latest_premium["ema20"]), 2))
# print("VWAP :", round(float(latest_premium["vwap"]), 2))
# print("RSI  :", round(float(latest_premium["rsi14"]), 2))
# print("ADX  :", round(float(latest_premium["adx14"]), 2))


# premium_setup = find_premium_setup(
#     premium_df,
#     pd.Timestamp(nifty_breakout["date"]),
#     pd.Timestamp(nifty_pullback["date"]),
# )

# if premium_setup is None:
#     print("\nPREMIUM SETUP: NOT CONFIRMED")
#     print("Need: premium breakout -> pullback -> NEXT green confirmation candle.")
#     print("NO TRADE")
#     raise SystemExit(0)

# premium_breakout = premium_setup["breakout"]
# premium_pullback = premium_setup["pullback"]
# premium_confirmation = premium_setup["confirmation"]


# # The confirmation candle must be the latest closed candle.
# if pd.Timestamp(
#     premium_confirmation["date"]
# ) != pd.Timestamp(
#     latest_premium["date"]
# ):
#     print("\nSETUP OCCURRED EARLIER.")
#     print("Wait for a fresh setup.")
#     raise SystemExit(0)


# strength = get_setup_strength(
#     nifty_breakout,
#     nifty_pullback,
#     premium_breakout,
#     premium_pullback,
#     premium_confirmation,
# )

# rr = recommended_rr(strength)

# if rr is None:
#     print("\nSETUP STRENGTH:", strength)
#     print("Setup is not strong enough.")
#     print("NO TRADE")
#     raise SystemExit(0)


# entry = float(
#     premium_confirmation["close"]
# )

# risk = calculate_dynamic_risk(
#     entry,
#     premium_pullback,
#     premium_confirmation,
#     direction,
#     strength,
# )

# if risk is None:
#     print("\nRisk is too wide / invalid.")
#     print("NO TRADE")
#     raise SystemExit(0)


# print("\n==========================================")
# print("             TRADE SIGNAL")
# print("==========================================")

# print("ACTION       : BUY", direction)
# print("Symbol       :", option_symbol)
# print("Quantity     :", QUANTITY)
# print("Entry        :", round(risk["entry"], 2))
# print("Stop Loss    :", round(risk["stop_loss"], 2))
# print("Risk         :", round(risk["risk_points"], 2), "points")
# print("Risk Reward  : 1:", int(risk["rr"]))
# print("Target       :", round(risk["target"], 2))
# print("Setup        :", risk["setup_strength"])

# print("\nWHY:")
# print("NIFTY breakout :", nifty_breakout["date"])
# print("NIFTY pullback :", nifty_pullback["date"])
# print("Premium breakout:", premium_breakout["date"])
# print("Premium pullback:", premium_pullback["date"])
# print("Premium confirmation:", premium_confirmation["date"])

# print("\nR:R RULE")
# print("NORMAL      -> 1:2")
# print("STRONG      -> 1:3")
# print("VERY_STRONG -> 1:4")

# print("\nNO LIVE ORDER PLACED.")

















import os
from datetime import date

import pandas as pd
from dotenv import load_dotenv
from kiteconnect import KiteConnect

from strategy import (
    calculate_indicators,
    bullish_breakout,
    bearish_breakout,
    bullish_pullback,
    bearish_pullback,
    premium_bullish_breakout,
    premium_bullish_pullback,
    find_nifty_setups,
    find_sensex_setups,
    find_premium_setups,
    find_sensex_premium_setups,
    calculate_dynamic_risk,
    PULLBACK_BUFFER,
    MAX_PULLBACK_CANDLES,
    MAX_SETUP_GAP_MINUTES,
)


# =========================================================
# CONFIG
# =========================================================

NIFTY_INDEX_TOKEN = 256265
SENSEX_INDEX_TOKEN = 136444164

NIFTY_STRIKE_INTERVAL = 50
SENSEX_STRIKE_INTERVAL = 100

NIFTY_DEFAULT_LOT = 65
SENSEX_DEFAULT_LOT = 20

LOTS = 1


# =========================================================
# ZERODHA
# =========================================================

SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

load_dotenv()

API_KEY = os.getenv(
    "KITE_API_KEY"
)

if not API_KEY:
    print(
        "ERROR: KITE_API_KEY not found in .env"
    )
    raise SystemExit(1)

try:

    with open(
        os.path.join(
            SCRIPT_DIR,
            "access_token.txt"
        ),
        "r",
        encoding="utf-8"
    ) as f:

        ACCESS_TOKEN = f.read().strip()

except Exception:

    print(
        "ERROR: access_token.txt not found"
    )

    raise SystemExit(1)


kite = KiteConnect(
    api_key=API_KEY
)

kite.set_access_token(
    ACCESS_TOKEN
)


# =========================================================
# FETCH TODAY
# =========================================================

def fetch_today_candles(
    token
):

    now = pd.Timestamp.now(
        tz="Asia/Kolkata"
    )

    market_open = pd.Timestamp(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=9,
        minute=15,
        tz="Asia/Kolkata"
    )

    try:

        candles = kite.historical_data(
            instrument_token=token,
            from_date=market_open.to_pydatetime(),
            to_date=now.to_pydatetime(),
            interval="5minute"
        )

        return candles

    except Exception as exc:

        print(
            "ZERODHA DATA ERROR:",
            type(exc).__name__,
            str(exc)
        )

        return []


# =========================================================
# REMOVE CURRENT CANDLE
# =========================================================

def remove_current_candle(
    df
):

    if df.empty:
        return df

    now = pd.Timestamp.now(
        tz="Asia/Kolkata"
    )

    current_start = now.floor(
        "5min"
    )

    return (
        df[
            df["date"]
            <
            current_start
        ]
        .copy()
        .reset_index(drop=True)
    )


# =========================================================
# GET SPOT
# =========================================================

def get_spot(
    symbol
):

    try:

        quote = kite.quote(
            [symbol]
        )

        return float(
            quote[symbol][
                "last_price"
            ]
        )

    except Exception as exc:

        print(
            "SPOT ERROR:",
            type(exc).__name__,
            str(exc)
        )

        return None


# =========================================================
# DOWNLOAD NFO/BFO
# =========================================================

def get_instruments(
    exchange
):

    try:
        return kite.instruments(
            exchange
        )
    except Exception as exc:

        print(
            "Instrument download error:",
            exchange,
            str(exc)
        )

        return []


# =========================================================
# FIND OPTION
# =========================================================

def find_option(
    instruments,
    underlying_name,
    direction,
    spot,
    strike_interval
):

    atm = (
        round(
            spot
            /
            strike_interval
        )
        *
        strike_interval
    )

    today = date.today()

    candidates = []

    for instrument in instruments:

        try:

            if instrument.get(
                "name"
            ) != underlying_name:
                continue

            if instrument.get(
                "instrument_type"
            ) != direction:
                continue

            if float(
                instrument.get(
                    "strike",
                    0
                )
            ) != float(atm):
                continue

            expiry = instrument.get(
                "expiry"
            )

            if not expiry:
                continue

            if expiry < today:
                continue

            candidates.append(
                instrument
            )

        except Exception:
            continue

    if not candidates:
        return None

    candidates.sort(
        key=lambda x:
        x["expiry"]
    )

    return candidates[0]


# =========================================================
# TEST ONE UNDERLYING
# =========================================================

def test_underlying(
    label,
    token,
    spot_symbol,
    instrument_exchange,
    underlying_name,
    strike_interval,
    default_lot
):

    print()
    print(
        "=========================================="
    )

    print(
        label,
        "5-MIN SIGNAL"
    )

    print(
        "=========================================="
    )

    raw = fetch_today_candles(
        token
    )

    if not raw:

        print(
            "No",
            label,
            "candles."
        )

        return

    df = calculate_indicators(
        raw
    )

    df = remove_current_candle(
        df
    )

    if len(df) < 2:

        print(
            "Not enough completed candles."
        )

        return

    latest = df.iloc[-1]

    print(
        "Latest:",
        latest["date"]
    )

    print(
        "Close:",
        round(
            float(
                latest["close"]
            ),
            2
        )
    )

    print(
        "EMA20:",
        round(
            float(
                latest["ema20"]
            ),
            2
        )
    )

    print(
        "VWAP:",
        round(
            float(
                latest["vwap"]
            ),
            2
        )
    )

    # -----------------------------------------------------
    # SETUP
    # -----------------------------------------------------

    if label == "NIFTY":

        setups = find_nifty_setups(
            df
        )

    else:

        setups = find_sensex_setups(
            df
        )

    if not setups:

        print(
            label,
            "setup: NONE"
        )

        return

    setup = setups[-1]

    direction = setup[
        "direction"
    ]

    breakout = setup[
        "breakout"
    ]

    pullback = setup[
        "pullback"
    ]

    print()
    print(
        label,
        "SETUP:",
        direction
    )

    print(
        "Breakout:",
        breakout["date"]
    )

    print(
        "Pullback:",
        pullback["date"]
    )

    # -----------------------------------------------------
    # SPOT
    # -----------------------------------------------------

    spot = get_spot(
        spot_symbol
    )

    if spot is None:
        return

    print(
        "Spot:",
        spot
    )

    # -----------------------------------------------------
    # OPTION INSTRUMENTS
    # -----------------------------------------------------

    instruments = get_instruments(
        instrument_exchange
    )

    if not instruments:
        return

    option = find_option(
        instruments,
        underlying_name,
        direction,
        spot,
        strike_interval
    )

    if option is None:

        print(
            "Option not found."
        )

        return

    option_symbol = (
        option["tradingsymbol"]
    )

    option_token = (
        option["instrument_token"]
    )

    quantity = (
        int(
            option.get(
                "lot_size",
                default_lot
            )
        )
        *
        LOTS
    )

    print()
    print(
        "OPTION:",
        option_symbol
    )

    print(
        "Exchange:",
        instrument_exchange
    )

    print(
        "Expiry:",
        option["expiry"]
    )

    print(
        "Lot size:",
        option.get(
            "lot_size",
            default_lot
        )
    )

    print(
        "Quantity:",
        quantity
    )

    # -----------------------------------------------------
    # PREMIUM
    # -----------------------------------------------------

    premium_raw = fetch_today_candles(
        option_token
    )

    if not premium_raw:

        print(
            "No premium candles."
        )

        return

    premium_df = calculate_indicators(
        premium_raw
    )

    premium_df = remove_current_candle(
        premium_df
    )

    if len(premium_df) < 2:

        return

    if label == "NIFTY":

        premium_setups = (
            find_premium_setups(
                premium_df,
                pd.Timestamp(
                    breakout["date"]
                ),
                pd.Timestamp(
                    pullback["date"]
                )
            )
        )

    else:

        premium_setups = (
            find_sensex_premium_setups(
                premium_df,
                pd.Timestamp(
                    breakout["date"]
                ),
                pd.Timestamp(
                    pullback["date"]
                )
            )
        )

    if not premium_setups:

        print(
            "Premium setup: NONE"
        )

        return

    premium_setup = (
        premium_setups[-1]
    )

    premium_breakout = (
        premium_setup["breakout"]
    )

    premium_pullback = (
        premium_setup["pullback"]
    )

    latest_premium = (
        premium_df.iloc[-1]
    )

    if pd.Timestamp(
        premium_pullback["date"]
    ) != pd.Timestamp(
        latest_premium["date"]
    ):

        print(
            "Premium setup occurred earlier."
        )

        return

    entry = float(
        premium_pullback["close"]
    )

    risk = calculate_dynamic_risk(
        entry,
        premium_pullback,
        premium_pullback,
        direction
    )

    if risk is None:

        print(
            "Invalid risk."
        )

        return

    print()
    print(
        "------------------------------------------"
    )

    print(
        "FINAL SIGNAL"
    )

    print(
        "------------------------------------------"
    )

    print(
        "BUY",
        direction
    )

    print(
        "Symbol:",
        option_symbol
    )

    print(
        "Quantity:",
        quantity
    )

    print(
        "Entry:",
        round(
            risk["entry"],
            2
        )
    )

    print(
        "SL:",
        round(
            risk["stop_loss"],
            2
        )
    )

    print(
        "Target:",
        round(
            risk["target"],
            2
        )
    )

    print(
        "R:R: 1:2"
    )


# =========================================================
# MAIN
# =========================================================

print()
print(
    "=========================================="
)

print(
    "      NIFTY + SENSEX SIGNAL TEST"
)

print(
    "          EMA20 + VWAP ONLY"
)

print(
    "=========================================="
)

test_underlying(
    label="NIFTY",
    token=NIFTY_INDEX_TOKEN,
    spot_symbol="NSE:NIFTY 50",
    instrument_exchange="NFO",
    underlying_name="NIFTY",
    strike_interval=NIFTY_STRIKE_INTERVAL,
    default_lot=NIFTY_DEFAULT_LOT,
)

test_underlying(
    label="SENSEX",
    token=SENSEX_INDEX_TOKEN,
    spot_symbol="BSE:SENSEX",
    instrument_exchange="BFO",
    underlying_name="SENSEX",
    strike_interval=SENSEX_STRIKE_INTERVAL,
    default_lot=SENSEX_DEFAULT_LOT,
)

print()
print(
    "Signal test complete."
)