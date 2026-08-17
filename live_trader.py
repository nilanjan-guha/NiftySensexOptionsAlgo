

# import os
# import time
# from datetime import date, time as dt_time

# import pandas as pd
# from dotenv import load_dotenv
# from kiteconnect import KiteConnect

# from strategy import (
#     calculate_indicators,
#     find_nifty_setups,
#     find_sensex_setups,
#     find_premium_setups,
#     find_sensex_premium_setups,
#     calculate_dynamic_risk,
#     MAX_SETUP_GAP_MINUTES,
# )


# # =========================================================
# # MODE
# # =========================================================

# # False = PAPER
# # True  = REAL ORDERS
# LIVE_MODE = False


# # =========================================================
# # MARKET CONFIG
# # =========================================================

# MARKETS = {

#     "NIFTY": {

#         "index_token": 256265,

#         "spot_symbol":
#             "NSE:NIFTY 50",

#         "option_exchange":
#             "NFO",

#         "underlying_name":
#             "NIFTY",

#         "strike_interval":
#             50,

#         "default_lot":
#             65,
#     },

#     "SENSEX": {

#         "index_token": 265,

#         "spot_symbol":
#             "BSE:SENSEX",

#         "option_exchange":
#             "BFO",

#         "underlying_name":
#             "SENSEX",

#         "strike_interval":
#             100,

#         "default_lot":
#             20,
#     },
# }


# # =========================================================
# # TRADING CONFIG
# # =========================================================

# LOTS = 1

# TIMEFRAME = "5minute"

# MARKET_OPEN = dt_time(9, 15)

# ENTRY_START = dt_time(9, 20)

# # New entries allowed only until 2:45 PM
# ENTRY_END = dt_time(14, 45)

# # Intended force exit time
# FORCE_EXIT_TIME = dt_time(15, 15)

# # Bot stops at market close
# MARKET_CLOSE = dt_time(15, 30)


# # =========================================================
# # DAILY LIMITS
# # =========================================================

# MAX_TRADES_PER_DAY = 3

# TRADE_COOLDOWN_SECONDS = 10


# # =========================================================
# # RISK
# # =========================================================

# DEFAULT_RR = 2.0

# SL_BUFFER = 0.50


# # =========================================================
# # FILES
# # =========================================================

# SCRIPT_DIR = os.path.dirname(
#     os.path.abspath(__file__)
# )

# ACCESS_TOKEN_FILE = os.path.join(
#     SCRIPT_DIR,
#     "access_token.txt"
# )

# TRADE_LOG_FILE = os.path.join(
#     SCRIPT_DIR,
#     "live_trades.csv"
# )


# # =========================================================
# # LOGIN
# # =========================================================

# load_dotenv()

# API_KEY = os.getenv(
#     "KITE_API_KEY"
# )

# if not API_KEY:

#     raise SystemExit(
#         "KITE_API_KEY missing."
#     )


# # =========================================================
# # ACCESS TOKEN
# # =========================================================
# #
# # GitHub Actions:
# #     Uses KITE_ACCESS_TOKEN environment variable
# #
# # Local PC:
# #     Uses access_token.txt
# #
# # =========================================================

# ACCESS_TOKEN = os.getenv(
#     "KITE_ACCESS_TOKEN"
# )

# if not ACCESS_TOKEN:

#     if os.path.exists(
#         ACCESS_TOKEN_FILE
#     ):

#         with open(
#             ACCESS_TOKEN_FILE,
#             "r",
#             encoding="utf-8"
#         ) as f:

#             ACCESS_TOKEN = f.read().strip()

#     else:

#         raise SystemExit(
#             "KITE_ACCESS_TOKEN is not set and "
#             "access_token.txt was not found."
#         )


# if not ACCESS_TOKEN:

#     raise SystemExit(
#         "KITE_ACCESS_TOKEN is empty and "
#         "access_token.txt is empty."
#     )


# kite = KiteConnect(
#     api_key=API_KEY
# )

# kite.set_access_token(
#     ACCESS_TOKEN
# )


# # =========================================================
# # TIME
# # =========================================================

# def now_ist():

#     return pd.Timestamp.now(
#         tz="Asia/Kolkata"
#     )


# def market_is_open():

#     current_time = now_ist().time()

#     return (
#         MARKET_OPEN
#         <= current_time
#         <= MARKET_CLOSE
#     )


# def entry_window_open():

#     current_time = now_ist().time()

#     return (
#         ENTRY_START
#         <= current_time
#         <= ENTRY_END
#     )


# # =========================================================
# # CONNECTION
# # =========================================================

# def test_connection():

#     try:

#         profile = kite.profile()

#         print(
#             "ZERODHA:",
#             profile.get(
#                 "user_name"
#             )
#         )

#         print(
#             "USER ID:",
#             profile.get(
#                 "user_id"
#             )
#         )

#         print(
#             "MODE:",
#             "LIVE"
#             if LIVE_MODE
#             else "PAPER"
#         )

#         return True

#     except Exception as exc:

#         print(
#             "ZERODHA CONNECTION ERROR:",
#             type(exc).__name__,
#             str(exc)
#         )

#         return False


# # =========================================================
# # CANDLES
# # =========================================================

# def fetch_today_candles(
#     token
# ):

#     now = now_ist()

#     start = pd.Timestamp(
#         year=now.year,
#         month=now.month,
#         day=now.day,
#         hour=9,
#         minute=15,
#         tz="Asia/Kolkata"
#     )

#     try:

#         return kite.historical_data(
#             instrument_token=token,
#             from_date=start.to_pydatetime(),
#             to_date=now.to_pydatetime(),
#             interval=TIMEFRAME,
#         )

#     except Exception as exc:

#         print(
#             "DATA ERROR:",
#             type(exc).__name__,
#             str(exc)
#         )

#         return []


# def remove_current_candle(
#     df
# ):

#     if df.empty:

#         return df

#     current_start = (
#         now_ist().floor("5min")
#     )

#     return (
#         df[
#             df["date"]
#             <
#             current_start
#         ]
#         .copy()
#         .reset_index(drop=True)
#     )


# # =========================================================
# # SPOT
# # =========================================================

# def get_spot(
#     symbol
# ):

#     try:

#         data = kite.quote(
#             [symbol]
#         )

#         return float(
#             data[
#                 symbol
#             ][
#                 "last_price"
#             ]
#         )

#     except Exception as exc:

#         print(
#             "SPOT ERROR:",
#             symbol,
#             str(exc)
#         )

#         return None


# # =========================================================
# # INSTRUMENTS
# # =========================================================

# def get_instruments(
#     exchange
# ):

#     try:

#         return kite.instruments(
#             exchange
#         )

#     except Exception as exc:

#         print(
#             "INSTRUMENT ERROR:",
#             exchange,
#             str(exc)
#         )

#         return []


# # =========================================================
# # OPTION
# # =========================================================

# def find_option(
#     instruments,
#     config,
#     direction,
#     spot
# ):

#     atm = (
#         round(
#             spot
#             /
#             config[
#                 "strike_interval"
#             ]
#         )
#         *
#         config[
#             "strike_interval"
#         ]
#     )

#     today = date.today()

#     candidates = []

#     for instrument in instruments:

#         try:

#             if instrument.get(
#                 "name"
#             ) != config[
#                 "underlying_name"
#             ]:

#                 continue

#             if instrument.get(
#                 "instrument_type"
#             ) != direction:

#                 continue

#             if float(
#                 instrument.get(
#                     "strike",
#                     0
#                 )
#             ) != float(atm):

#                 continue

#             expiry = instrument.get(
#                 "expiry"
#             )

#             if (
#                 not expiry
#                 or
#                 expiry < today
#             ):

#                 continue

#             candidates.append(
#                 instrument
#             )

#         except Exception:

#             continue

#     if not candidates:

#         return None

#     candidates.sort(
#         key=lambda x:
#         x["expiry"]
#     )

#     return candidates[0]


# # =========================================================
# # OPTION LTP
# # =========================================================

# def option_ltp(
#     exchange,
#     symbol
# ):

#     try:

#         key = (
#             exchange
#             + ":"
#             + symbol
#         )

#         data = kite.ltp(
#             [key]
#         )

#         return float(
#             data[
#                 key
#             ][
#                 "last_price"
#             ]
#         )

#     except Exception as exc:

#         print(
#             "LTP ERROR:",
#             str(exc)
#         )

#         return None


# # =========================================================
# # SIGNAL FOR ONE MARKET
# # =========================================================

# def check_market(
#     market_name,
#     config,
#     option_instruments
# ):

#     print()
#     print(
#         "=========================================="
#     )

#     print(
#         "CHECKING:",
#         market_name
#     )

#     print(
#         "=========================================="
#     )

#     # -----------------------------------------------------
#     # UNDERLYING
#     # -----------------------------------------------------

#     raw = fetch_today_candles(
#         config[
#             "index_token"
#         ]
#     )

#     if not raw:

#         print(
#             "No",
#             market_name,
#             "data."
#         )

#         return None

#     df = calculate_indicators(
#         raw
#     )

#     df = remove_current_candle(
#         df
#     )

#     if len(df) < 2:

#         print(
#             "Not enough completed",
#             market_name,
#             "candles."
#         )

#         return None

#     latest = df.iloc[-1]

#     print(
#         "Latest:",
#         latest["date"]
#     )

#     print(
#         "Close:",
#         round(
#             float(
#                 latest["close"]
#             ),
#             2
#         )
#     )

#     print(
#         "EMA20:",
#         round(
#             float(
#                 latest["ema20"]
#             ),
#             2
#         )
#     )

#     print(
#         "VWAP:",
#         round(
#             float(
#                 latest["vwap"]
#             ),
#             2
#         )
#     )

#     # -----------------------------------------------------
#     # UNDERLYING SETUP
#     # -----------------------------------------------------

#     if market_name == "NIFTY":

#         setups = (
#             find_nifty_setups(
#                 df
#             )
#         )

#     else:

#         setups = (
#             find_sensex_setups(
#                 df
#             )
#         )

#     if not setups:

#         print(
#             market_name,
#             "setup: NONE"
#         )

#         return None

#     setup = setups[-1]

#     direction = (
#         setup["direction"]
#     )

#     breakout = (
#         setup["breakout"]
#     )

#     pullback = (
#         setup["pullback"]
#     )

#     print(
#         market_name,
#         "SETUP:",
#         direction
#     )

#     print(
#         "Breakout:",
#         breakout["date"]
#     )

#     print(
#         "Pullback:",
#         pullback["date"]
#     )

#     # -----------------------------------------------------
#     # SPOT
#     # -----------------------------------------------------

#     spot = get_spot(
#         config[
#             "spot_symbol"
#         ]
#     )

#     if spot is None:

#         return None

#     # -----------------------------------------------------
#     # OPTION
#     # -----------------------------------------------------

#     option = find_option(
#         option_instruments,
#         config,
#         direction,
#         spot
#     )

#     if option is None:

#         print(
#             "Option not found."
#         )

#         return None

#     option_symbol = (
#         option[
#             "tradingsymbol"
#         ]
#     )

#     option_token = (
#         option[
#             "instrument_token"
#         ]
#     )

#     option_lot = int(
#         option.get(
#             "lot_size",
#             config[
#                 "default_lot"
#             ]
#         )
#     )

#     quantity = (
#         option_lot
#         * LOTS
#     )

#     print(
#         "Option:",
#         option_symbol
#     )

#     print(
#         "Exchange:",
#         config[
#             "option_exchange"
#         ]
#     )

#     print(
#         "Lot size:",
#         option_lot
#     )

#     print(
#         "Quantity:",
#         quantity
#     )

#     # -----------------------------------------------------
#     # PREMIUM
#     # -----------------------------------------------------

#     premium_raw = (
#         fetch_today_candles(
#             option_token
#         )
#     )

#     if not premium_raw:

#         print(
#             "No premium candles."
#         )

#         return None

#     premium_df = (
#         calculate_indicators(
#             premium_raw
#         )
#     )

#     premium_df = (
#         remove_current_candle(
#             premium_df
#         )
#     )

#     if len(premium_df) < 2:

#         return None

#     if market_name == "NIFTY":

#         premium_setups = (
#             find_premium_setups(
#                 premium_df,
#                 pd.Timestamp(
#                     breakout["date"]
#                 ),
#                 pd.Timestamp(
#                     pullback["date"]
#                 )
#             )
#         )

#     else:

#         premium_setups = (
#             find_sensex_premium_setups(
#                 premium_df,
#                 pd.Timestamp(
#                     breakout["date"]
#                 ),
#                 pd.Timestamp(
#                     pullback["date"]
#                 )
#             )
#         )

#     if not premium_setups:

#         print(
#             "Premium setup: NONE"
#         )

#         return None

#     premium_setup = (
#         premium_setups[-1]
#     )

#     premium_breakout = (
#         premium_setup[
#             "breakout"
#         ]
#     )

#     premium_pullback = (
#         premium_setup[
#             "pullback"
#         ]
#     )

#     # -----------------------------------------------------
#     # MUST BE LATEST CLOSED CANDLE
#     # -----------------------------------------------------

#     latest_premium = (
#         premium_df.iloc[-1]
#     )

#     if pd.Timestamp(
#         premium_pullback[
#             "date"
#         ]
#     ) != pd.Timestamp(
#         latest_premium[
#             "date"
#         ]
#     ):

#         print(
#             "Premium setup is old."
#         )

#         return None

#     # -----------------------------------------------------
#     # ENTRY + RISK
#     # -----------------------------------------------------

#     entry = float(
#         premium_pullback[
#             "close"
#         ]
#     )

#     risk = (
#         calculate_dynamic_risk(
#             entry,
#             premium_pullback,
#             premium_pullback,
#             direction
#         )
#     )

#     if risk is None:

#         print(
#             "Invalid risk."
#         )

#         return None

#     return {

#         "market":
#             market_name,

#         "direction":
#             direction,

#         "option_symbol":
#             option_symbol,

#         "option_token":
#             option_token,

#         "option_exchange":
#             config[
#                 "option_exchange"
#             ],

#         "quantity":
#             quantity,

#         "entry":
#             risk[
#                 "entry"
#             ],

#         "stop_loss":
#             risk[
#                 "stop_loss"
#             ],

#         "target":
#             risk[
#                 "target"
#             ],

#         "risk_points":
#             risk[
#                 "risk_points"
#             ],

#         "nifty_or_sensex_breakout":
#             str(
#                 breakout[
#                     "date"
#                 ]
#             ),

#         "nifty_or_sensex_pullback":
#             str(
#                 pullback[
#                     "date"
#                 ]
#             ),

#         "premium_breakout":
#             str(
#                 premium_breakout[
#                     "date"
#                 ]
#             ),

#         "premium_pullback":
#             str(
#                 premium_pullback[
#                     "date"
#                 ]
#             ),
#     }


# # =========================================================
# # POSITIONS
# # =========================================================

# def has_open_position():

#     try:

#         positions = kite.positions()

#         for position in positions.get(
#             "net",
#             []
#         ):

#             if int(
#                 position.get(
#                     "quantity",
#                     0
#                 )
#             ) != 0:

#                 return True

#         return False

#     except Exception as exc:

#         print(
#             "POSITION ERROR:",
#             str(exc)
#         )

#         # Safety:
#         # If we cannot determine the position,
#         # assume a position exists.
#         return True


# # =========================================================
# # BUY
# # =========================================================

# def place_buy(
#     signal
# ):

#     print()
#     print(
#         "=========================================="
#     )

#     print(
#         "             TRADE SIGNAL"
#     )

#     print(
#         "=========================================="
#     )

#     print(
#         "Market:",
#         signal[
#             "market"
#         ]
#     )

#     print(
#         "Action: BUY",
#         signal[
#             "direction"
#         ]
#     )

#     print(
#         "Symbol:",
#         signal[
#             "option_symbol"
#         ]
#     )

#     print(
#         "Exchange:",
#         signal[
#             "option_exchange"
#         ]
#     )

#     print(
#         "Quantity:",
#         signal[
#             "quantity"
#         ]
#     )

#     print(
#         "Entry:",
#         round(
#             signal[
#                 "entry"
#             ],
#             2
#         )
#     )

#     print(
#         "SL:",
#         round(
#             signal[
#                 "stop_loss"
#             ],
#             2
#         )
#     )

#     print(
#         "Target:",
#         round(
#             signal[
#                 "target"
#             ],
#             2
#         )
#     )

#     if not LIVE_MODE:

#         print(
#             "PAPER MODE:"
#             " NO REAL ORDER PLACED."
#         )

#         return True

#     try:

#         order_id = kite.place_order(

#             variety=
#                 kite.VARIETY_REGULAR,

#             exchange=
#                 signal[
#                     "option_exchange"
#                 ],

#             tradingsymbol=
#                 signal[
#                     "option_symbol"
#                 ],

#             transaction_type=
#                 kite.TRANSACTION_TYPE_BUY,

#             quantity=
#                 signal[
#                     "quantity"
#                 ],

#             product=
#                 kite.PRODUCT_MIS,

#             order_type=
#                 kite.ORDER_TYPE_MARKET,

#             validity=
#                 kite.VALIDITY_DAY,

#             market_protection=-1,

#             tag="NIF_SEN_ALGO",
#         )

#         print(
#             "ORDER ID:",
#             order_id
#         )

#         return True

#     except Exception as exc:

#         print(
#             "BUY ORDER ERROR:",
#             type(exc).__name__,
#             str(exc)
#         )

#         return False


# # =========================================================
# # MAIN
# # =========================================================

# def main():

#     print()
#     print(
#         "=========================================="
#     )

#     print(
#         "     NIFTY + SENSEX LIVE TRADER"
#     )

#     print(
#         "          EMA20 + VWAP ONLY"
#     )

#     print(
#         "=========================================="
#     )

#     print(
#         "TIME:",
#         now_ist()
#     )

#     print(
#         "MODE:",
#         "LIVE"
#         if LIVE_MODE
#         else "PAPER"
#     )

#     # -----------------------------------------------------
#     # CONNECTION
#     # -----------------------------------------------------

#     if not test_connection():

#         return

#     # -----------------------------------------------------
#     # MARKET STATUS
#     # -----------------------------------------------------

#     current_time = now_ist().time()

#     if current_time < MARKET_OPEN:

#         print(
#             "Market has not opened yet."
#         )

#         return

#     if current_time >= MARKET_CLOSE:

#         print(
#             "Market is closed."
#         )

#         return

#     # -----------------------------------------------------
#     # ENTRY WINDOW
#     # -----------------------------------------------------

#     if not entry_window_open():

#         print(
#             "Outside entry window."
#         )

#         print(
#             "New entries are allowed only until:",
#             ENTRY_END
#         )

#         return

#     # -----------------------------------------------------
#     # EXISTING POSITION
#     # -----------------------------------------------------

#     if has_open_position():

#         print(
#             "Existing position detected."
#         )

#         print(
#             "No new trade."
#         )

#         return

#     # =====================================================
#     # LOAD BOTH OPTION EXCHANGES
#     # =====================================================

#     print()
#     print(
#         "Loading NFO instruments..."
#     )

#     nfo_instruments = (
#         get_instruments(
#             "NFO"
#         )
#     )

#     print(
#         "NFO instruments:",
#         len(
#             nfo_instruments
#         )
#     )

#     print()
#     print(
#         "Loading BFO instruments..."
#     )

#     bfo_instruments = (
#         get_instruments(
#             "BFO"
#         )
#     )

#     print(
#         "BFO instruments:",
#         len(
#             bfo_instruments
#         )
#     )

#     # =====================================================
#     # CHECK NIFTY
#     # =====================================================

#     nifty_signal = check_market(
#         "NIFTY",
#         MARKETS[
#             "NIFTY"
#         ],
#         nfo_instruments
#     )

#     # =====================================================
#     # CHECK SENSEX
#     # =====================================================

#     sensex_signal = check_market(
#         "SENSEX",
#         MARKETS[
#             "SENSEX"
#         ],
#         bfo_instruments
#     )

#     # =====================================================
#     # COLLECT SIGNALS
#     # =====================================================

#     signals = []

#     if nifty_signal is not None:

#         signals.append(
#             nifty_signal
#         )

#     if sensex_signal is not None:

#         signals.append(
#             sensex_signal
#         )

#     if not signals:

#         print()
#         print(
#             "NO TRADE ON NIFTY OR SENSEX."
#         )

#         return

#     # =====================================================
#     # EXECUTION POLICY
#     #
#     # If both produce a signal during the
#     # same check, choose the first signal.
#     #
#     # =====================================================

#     selected = signals[0]

#     for signal in signals:

#         print()
#         print(
#             "VALID SIGNAL:",
#             signal[
#                 "market"
#             ],
#             signal[
#                 "direction"
#             ],
#             signal[
#                 "option_symbol"
#             ]
#         )

#     print()
#     print(
#         "SELECTED:",
#         selected[
#             "market"
#         ],
#         selected[
#             "option_symbol"
#         ]
#     )

#     # =====================================================
#     # PLACE BUY
#     # =====================================================

#     place_buy(
#         selected
#     )


# # =========================================================
# # CONTINUOUS TRADING LOOP
# # =========================================================

# def run_trading_loop():

#     print()
#     print(
#         "=========================================="
#     )

#     print(
#         "       TRADING BOT STARTED"
#     )

#     print(
#         "=========================================="
#     )

#     print(
#         "Market open:",
#         MARKET_OPEN
#     )

#     print(
#         "Entry start:",
#         ENTRY_START
#     )

#     print(
#         "Entry end:",
#         ENTRY_END
#     )

#     print(
#         "Force exit time:",
#         FORCE_EXIT_TIME
#     )

#     print(
#         "Market close:",
#         MARKET_CLOSE
#     )

#     print(
#         "Check interval:",
#         "5 minutes"
#     )

#     print(
#         "=========================================="
#     )

#     while True:

#         now = now_ist()

#         current_time = now.time()

#         print()
#         print(
#             "------------------------------------------"
#         )

#         print(
#             "BOT TIME:",
#             now
#         )

#         print(
#             "------------------------------------------"
#         )

#         # -------------------------------------------------
#         # BEFORE MARKET OPEN
#         # -------------------------------------------------

#         if current_time < MARKET_OPEN:

#             print(
#                 "Waiting for market open..."
#             )

#             time.sleep(60)

#             continue

#         # -------------------------------------------------
#         # MARKET CLOSED
#         # -------------------------------------------------

#         if current_time >= MARKET_CLOSE:

#             print()
#             print(
#                 "=========================================="
#             )

#             print(
#                 "MARKET CLOSED"
#             )

#             print(
#                 "Trading bot stopped."
#             )

#             print(
#                 "=========================================="
#             )

#             break

#         # -------------------------------------------------
#         # RUN STRATEGY
#         # -------------------------------------------------

#         try:

#             main()

#         except Exception as exc:

#             print()
#             print(
#                 "STRATEGY LOOP ERROR:",
#                 type(exc).__name__,
#                 str(exc)
#             )

#         # -------------------------------------------------
#         # WAIT
#         # -------------------------------------------------

#         print()
#         print(
#             "Next strategy check in 5 minutes..."
#         )

#         time.sleep(300)


# # =========================================================
# # START
# # =========================================================

# if __name__ == "__main__":

#     try:

#         run_trading_loop()

#     except KeyboardInterrupt:

#         print()
#         print(
#             "=========================================="
#         )

#         print(
#             "Bot stopped manually."
#         )

#         print(
#             "=========================================="
#         )

#     except Exception as exc:

#         print()
#         print(
#             "=========================================="
#         )

#         print(
#             "UNEXPECTED ERROR:",
#             type(exc).__name__,
#             str(exc)
#         )

#         print(
#             "=========================================="
#         )






import os
import time
from datetime import date, time as dt_time

import pandas as pd
from dotenv import load_dotenv
from kiteconnect import KiteConnect

from strategy import (
    calculate_indicators,
    find_nifty_setups,
    find_sensex_setups,
    find_premium_setups,
    find_sensex_premium_setups,
    calculate_dynamic_risk,
    MAX_SETUP_GAP_MINUTES,
)


# =========================================================
# MODE
# =========================================================

# False = PAPER
# True  = REAL ORDERS
#
# KEEP FALSE WHILE TESTING.
#
LIVE_MODE = False


# =========================================================
# MARKET CONFIG
# =========================================================

MARKETS = {

    "NIFTY": {

        "index_token": 256265,

        "spot_symbol":
            "NSE:NIFTY 50",

        "option_exchange":
            "NFO",

        "underlying_name":
            "NIFTY",

        "strike_interval":
            50,

        "default_lot":
            65,
    },

    "SENSEX": {

        "index_token": 265,

        "spot_symbol":
            "BSE:SENSEX",

        "option_exchange":
            "BFO",

        "underlying_name":
            "SENSEX",

        "strike_interval":
            100,

        "default_lot":
            20,
    },
}


# =========================================================
# GENERAL CONFIG
# =========================================================

LOTS = 1

TIMEFRAME = "5minute"


# =========================================================
# MARKET TIMINGS
# =========================================================

MARKET_OPEN = dt_time(9, 15)

ENTRY_START = dt_time(9, 20)

ENTRY_END = dt_time(14, 45)

FORCE_EXIT_TIME = dt_time(15, 15)

MARKET_CLOSE = dt_time(15, 30)


# =========================================================
# BOT LOOP
# =========================================================

CHECK_INTERVAL_SECONDS = 300

WAIT_BEFORE_MARKET_SECONDS = 30


# =========================================================
# DAILY LIMITS
# =========================================================

MAX_TRADES_PER_DAY = 3

TRADE_COOLDOWN_SECONDS = 10


# =========================================================
# RISK
# =========================================================

DEFAULT_RR = 2.0

SL_BUFFER = 0.50


# =========================================================
# FILE
# =========================================================

SCRIPT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


ACCESS_TOKEN_FILE = os.path.join(
    SCRIPT_DIR,
    "access_token.txt"
)


TRADE_LOG_FILE = os.path.join(
    SCRIPT_DIR,
    "live_trades.csv"
)


# =========================================================
# LOGIN / ENVIRONMENT
# =========================================================

load_dotenv()


API_KEY = os.getenv(
    "KITE_API_KEY"
)


if not API_KEY:

    raise SystemExit(
        "KITE_API_KEY missing."
    )


# =========================================================
# ACCESS TOKEN
#
# GitHub Actions:
#     KITE_ACCESS_TOKEN environment variable
#
# Local PC:
#     access_token.txt
#
# =========================================================

ACCESS_TOKEN = os.getenv(
    "KITE_ACCESS_TOKEN"
)


if not ACCESS_TOKEN:

    if os.path.exists(
        ACCESS_TOKEN_FILE
    ):

        with open(
            ACCESS_TOKEN_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            ACCESS_TOKEN = (
                f.read()
                .strip()
            )

    else:

        raise SystemExit(
            "KITE_ACCESS_TOKEN is not set "
            "and access_token.txt was not found."
        )


if not ACCESS_TOKEN:

    raise SystemExit(
        "KITE_ACCESS_TOKEN is empty "
        "and access_token.txt is empty."
    )


# =========================================================
# KITE CONNECTION
# =========================================================

kite = KiteConnect(
    api_key=API_KEY
)


kite.set_access_token(
    ACCESS_TOKEN
)


# =========================================================
# TIME
# =========================================================

def now_ist():

    return pd.Timestamp.now(
        tz="Asia/Kolkata"
    )


# =========================================================
# MARKET STATUS
# =========================================================

def market_is_open():

    t = now_ist().time()

    return (
        MARKET_OPEN
        <= t
        <= MARKET_CLOSE
    )


# =========================================================
# ENTRY WINDOW
# =========================================================

def entry_window_open():

    t = now_ist().time()

    return (
        ENTRY_START
        <= t
        <= ENTRY_END
    )


# =========================================================
# MARKET CLOSED
# =========================================================

def market_has_closed():

    return (
        now_ist().time()
        >= MARKET_CLOSE
    )


# =========================================================
# CONNECTION
# =========================================================

def test_connection():

    try:

        profile = kite.profile()

        print(
            "ZERODHA:",
            profile.get(
                "user_name"
            )
        )

        print(
            "USER ID:",
            profile.get(
                "user_id"
            )
        )

        print(
            "MODE:",
            "LIVE"
            if LIVE_MODE
            else "PAPER"
        )

        return True

    except Exception as exc:

        print(
            "ZERODHA CONNECTION ERROR:",
            type(exc).__name__,
            str(exc)
        )

        return False


# =========================================================
# CANDLES
# =========================================================

def fetch_today_candles(
    token
):

    now = now_ist()

    start = pd.Timestamp(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=9,
        minute=15,
        tz="Asia/Kolkata"
    )

    try:

        return kite.historical_data(

            instrument_token=token,

            from_date=
                start.to_pydatetime(),

            to_date=
                now.to_pydatetime(),

            interval=TIMEFRAME,
        )

    except Exception as exc:

        print(
            "DATA ERROR:",
            type(exc).__name__,
            str(exc)
        )

        return []


# =========================================================
# REMOVE CURRENT INCOMPLETE CANDLE
# =========================================================

def remove_current_candle(
    df
):

    if df.empty:

        return df


    current_start = (
        now_ist().floor("5min")
    )


    return (

        df[
            df["date"]
            <
            current_start
        ]

        .copy()

        .reset_index(
            drop=True
        )
    )


# =========================================================
# SPOT
# =========================================================

def get_spot(
    symbol
):

    try:

        data = kite.quote(
            [symbol]
        )

        return float(
            data[
                symbol
            ][
                "last_price"
            ]
        )

    except Exception as exc:

        print(
            "SPOT ERROR:",
            symbol,
            str(exc)
        )

        return None


# =========================================================
# INSTRUMENTS
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
            "INSTRUMENT ERROR:",
            exchange,
            str(exc)
        )

        return []


# =========================================================
# FIND OPTION
# =========================================================

def find_option(
    instruments,
    config,
    direction,
    spot
):

    atm = (

        round(
            spot
            /
            config[
                "strike_interval"
            ]
        )

        *

        config[
            "strike_interval"
        ]
    )


    today = date.today()


    candidates = []


    for instrument in instruments:

        try:

            if instrument.get(
                "name"
            ) != config[
                "underlying_name"
            ]:

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


            if (
                not expiry
                or
                expiry < today
            ):

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
# OPTION LTP
# =========================================================

def option_ltp(
    exchange,
    symbol
):

    try:

        key = (
            exchange
            +
            ":"
            +
            symbol
        )


        data = kite.ltp(
            [key]
        )


        return float(
            data[
                key
            ][
                "last_price"
            ]
        )


    except Exception as exc:

        print(
            "LTP ERROR:",
            str(exc)
        )

        return None


# =========================================================
# SIGNAL FOR ONE MARKET
# =========================================================

def check_market(
    market_name,
    config,
    option_instruments
):

    print()
    print(
        "=========================================="
    )

    print(
        "CHECKING:",
        market_name
    )

    print(
        "=========================================="
    )


    # -----------------------------------------------------
    # UNDERLYING
    # -----------------------------------------------------

    raw = fetch_today_candles(
        config[
            "index_token"
        ]
    )


    if not raw:

        print(
            "No",
            market_name,
            "data."
        )

        return None


    df = calculate_indicators(
        raw
    )


    df = remove_current_candle(
        df
    )


    if len(df) < 2:

        print(
            "Not enough completed",
            market_name,
            "candles."
        )

        return None


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
    # UNDERLYING SETUP
    # -----------------------------------------------------

    if market_name == "NIFTY":

        setups = (
            find_nifty_setups(
                df
            )
        )

    else:

        setups = (
            find_sensex_setups(
                df
            )
        )


    if not setups:

        print(
            market_name,
            "SETUP: NONE"
        )

        return None


    setup = setups[-1]


    direction = (
        setup["direction"]
    )


    breakout = (
        setup["breakout"]
    )


    pullback = (
        setup["pullback"]
    )


    print(
        market_name,
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
        config[
            "spot_symbol"
        ]
    )


    if spot is None:

        return None


    # -----------------------------------------------------
    # OPTION
    # -----------------------------------------------------

    option = find_option(
        option_instruments,
        config,
        direction,
        spot
    )


    if option is None:

        print(
            "Option not found."
        )

        return None


    option_symbol = (
        option[
            "tradingsymbol"
        ]
    )


    option_token = (
        option[
            "instrument_token"
        ]
    )


    option_lot = int(
        option.get(
            "lot_size",
            config[
                "default_lot"
            ]
        )
    )


    quantity = (
        option_lot
        *
        LOTS
    )


    print(
        "Option:",
        option_symbol
    )


    print(
        "Exchange:",
        config[
            "option_exchange"
        ]
    )


    print(
        "Lot size:",
        option_lot
    )


    print(
        "Quantity:",
        quantity
    )


    # -----------------------------------------------------
    # PREMIUM
    # -----------------------------------------------------

    premium_raw = (
        fetch_today_candles(
            option_token
        )
    )


    if not premium_raw:

        print(
            "No premium candles."
        )

        return None


    premium_df = (
        calculate_indicators(
            premium_raw
        )
    )


    premium_df = (
        remove_current_candle(
            premium_df
        )
    )


    if len(premium_df) < 2:

        return None


    if market_name == "NIFTY":

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

        return None


    premium_setup = (
        premium_setups[-1]
    )


    premium_breakout = (
        premium_setup[
            "breakout"
        ]
    )


    premium_pullback = (
        premium_setup[
            "pullback"
        ]
    )


    # -----------------------------------------------------
    # PREMIUM SETUP MUST BE LATEST CLOSED CANDLE
    # -----------------------------------------------------

    latest_premium = (
        premium_df.iloc[-1]
    )


    if (

        pd.Timestamp(
            premium_pullback[
                "date"
            ]
        )

        !=

        pd.Timestamp(
            latest_premium[
                "date"
            ]
        )

    ):

        print(
            "Premium setup is old."
        )

        return None


    # -----------------------------------------------------
    # ENTRY + RISK
    # -----------------------------------------------------

    entry = float(
        premium_pullback[
            "close"
        ]
    )


    risk = (
        calculate_dynamic_risk(

            entry,

            premium_pullback,

            premium_pullback,

            direction
        )
    )


    if risk is None:

        print(
            "Invalid risk."
        )

        return None


    # -----------------------------------------------------
    # SIGNAL
    # -----------------------------------------------------

    return {

        "market":
            market_name,

        "direction":
            direction,

        "option_symbol":
            option_symbol,

        "option_token":
            option_token,

        "option_exchange":
            config[
                "option_exchange"
            ],

        "quantity":
            quantity,

        "entry":
            risk[
                "entry"
            ],

        "stop_loss":
            risk[
                "stop_loss"
            ],

        "target":
            risk[
                "target"
            ],

        "risk_points":
            risk[
                "risk_points"
            ],

        "nifty_or_sensex_breakout":
            str(
                breakout[
                    "date"
                ]
            ),

        "nifty_or_sensex_pullback":
            str(
                pullback[
                    "date"
                ]
            ),

        "premium_breakout":
            str(
                premium_breakout[
                    "date"
                ]
            ),

        "premium_pullback":
            str(
                premium_pullback[
                    "date"
                ]
            ),
    }


# =========================================================
# POSITIONS
# =========================================================

def has_open_position():

    try:

        positions = kite.positions()


        for position in positions.get(
            "net",
            []
        ):

            if int(
                position.get(
                    "quantity",
                    0
                )
            ) != 0:

                return True


        return False


    except Exception as exc:

        print(
            "POSITION ERROR:",
            str(exc)
        )

        # Fail safe:
        # if Zerodha cannot confirm positions,
        # do not open a new trade.

        return True


# =========================================================
# BUY
# =========================================================

def place_buy(
    signal
):

    print()
    print(
        "=========================================="
    )


    print(
        "             TRADE SIGNAL"
    )


    print(
        "=========================================="
    )


    print(
        "Market:",
        signal[
            "market"
        ]
    )


    print(
        "Action: BUY",
        signal[
            "direction"
        ]
    )


    print(
        "Symbol:",
        signal[
            "option_symbol"
        ]
    )


    print(
        "Exchange:",
        signal[
            "option_exchange"
        ]
    )


    print(
        "Quantity:",
        signal[
            "quantity"
        ]
    )


    print(
        "Entry:",
        round(
            signal[
                "entry"
            ],
            2
        )
    )


    print(
        "SL:",
        round(
            signal[
                "stop_loss"
            ],
            2
        )
    )


    print(
        "Target:",
        round(
            signal[
                "target"
            ],
            2
        )
    )


    # =====================================================
    # PAPER MODE
    # =====================================================

    if not LIVE_MODE:

        print(
            "PAPER MODE:"
            " NO REAL ORDER PLACED."
        )

        return True


    # =====================================================
    # LIVE ORDER
    # =====================================================

    try:

        order_id = kite.place_order(

            variety=
                kite.VARIETY_REGULAR,

            exchange=
                signal[
                    "option_exchange"
                ],

            tradingsymbol=
                signal[
                    "option_symbol"
                ],

            transaction_type=
                kite.TRANSACTION_TYPE_BUY,

            quantity=
                signal[
                    "quantity"
                ],

            product=
                kite.PRODUCT_MIS,

            order_type=
                kite.ORDER_TYPE_MARKET,

            validity=
                kite.VALIDITY_DAY,

            market_protection=-1,

            tag="NIF_SEN_ALGO",
        )


        print(
            "ORDER ID:",
            order_id
        )


        return True


    except Exception as exc:

        print(
            "BUY ORDER ERROR:",
            type(exc).__name__,
            str(exc)
        )


        return False


# =========================================================
# MAIN STRATEGY RUN
# =========================================================

def main():

    print()
    print(
        "=========================================="
    )


    print(
        "     NIFTY + SENSEX LIVE TRADER"
    )


    print(
        "          EMA20 + VWAP ONLY"
    )


    print(
        "=========================================="
    )


    print(
        "TIME:",
        now_ist()
    )


    print(
        "MODE:",
        "LIVE"
        if LIVE_MODE
        else "PAPER"
    )


    # =====================================================
    # CONNECTION
    # =====================================================

    if not test_connection():

        return


    # =====================================================
    # MARKET OPEN CHECK
    # =====================================================

    if not market_is_open():

        print(
            "Market is closed."
        )

        return


    # =====================================================
    # ENTRY WINDOW
    #
    # After 14:45:
    #     Bot continues running
    #     but no new entry is allowed.
    # =====================================================

    if not entry_window_open():

        print(
            "Outside entry window."
        )

        print(
            "No new trade will be entered."
        )

        return


    # =====================================================
    # EXISTING POSITION
    # =====================================================

    if has_open_position():

        print(
            "Existing position detected."
        )


        print(
            "No new trade."
        )


        return


    # =====================================================
    # LOAD NFO
    # =====================================================

    print()
    print(
        "Loading NFO instruments..."
    )


    nfo_instruments = (
        get_instruments(
            "NFO"
        )
    )


    print(
        "NFO instruments:",
        len(
            nfo_instruments
        )
    )


    # =====================================================
    # LOAD BFO
    # =====================================================

    print()
    print(
        "Loading BFO instruments..."
    )


    bfo_instruments = (
        get_instruments(
            "BFO"
        )
    )


    print(
        "BFO instruments:",
        len(
            bfo_instruments
        )
    )


    # =====================================================
    # CHECK NIFTY
    # =====================================================

    nifty_signal = check_market(

        "NIFTY",

        MARKETS[
            "NIFTY"
        ],

        nfo_instruments
    )


    # =====================================================
    # CHECK SENSEX
    # =====================================================

    sensex_signal = check_market(

        "SENSEX",

        MARKETS[
            "SENSEX"
        ],

        bfo_instruments
    )


    # =====================================================
    # COLLECT SIGNALS
    # =====================================================

    signals = []


    if nifty_signal is not None:

        signals.append(
            nifty_signal
        )


    if sensex_signal is not None:

        signals.append(
            sensex_signal
        )


    # =====================================================
    # NO SIGNAL
    # =====================================================

    if not signals:

        print()
        print(
            "NO TRADE ON NIFTY OR SENSEX."
        )

        return


    # =====================================================
    # SELECT SIGNAL
    #
    # If both NIFTY and SENSEX generate a signal
    # during the same check, choose the first signal.
    #
    # This prevents two positions from opening
    # at the same time.
    # =====================================================

    selected = signals[0]


    for signal in signals:

        print()
        print(
            "VALID SIGNAL:",
            signal[
                "market"
            ],
            signal[
                "direction"
            ],
            signal[
                "option_symbol"
            ]
        )


    print()
    print(
        "SELECTED:",
        selected[
            "market"
        ],
        selected[
            "option_symbol"
        ]
    )


    # =====================================================
    # PLACE BUY
    # =====================================================

    place_buy(
        selected
    )


# =========================================================
# WAIT UNTIL MARKET OPEN
# =========================================================

def wait_for_market_open():

    print()
    print(
        "=========================================="
    )

    print(
        "       NIFTY + SENSEX TRADING BOT"
    )

    print(
        "=========================================="
    )

    print(
        "MARKET OPEN :",
        MARKET_OPEN
    )

    print(
        "ENTRY START :",
        ENTRY_START
    )

    print(
        "ENTRY END   :",
        ENTRY_END
    )

    print(
        "MARKET CLOSE:",
        MARKET_CLOSE
    )

    print(
        "CHECK EVERY :",
        CHECK_INTERVAL_SECONDS,
        "seconds"
    )

    print(
        "=========================================="
    )


    while True:

        now = now_ist()


        # -------------------------------------------------
        # MARKET ALREADY CLOSED
        # -------------------------------------------------

        if now.time() >= MARKET_CLOSE:

            print()
            print(
                "=========================================="
            )

            print(
                "       MARKET CLOSED - BOT STOPPED"
            )

            print(
                "=========================================="
            )

            print(
                "BOT TIME:",
                now
            )

            return False


        # -------------------------------------------------
        # MARKET OPEN
        # -------------------------------------------------

        if now.time() >= MARKET_OPEN:

            print()
            print(
                "Market is open."
            )

            print(
                "Starting strategy checks..."
            )

            return True


        # -------------------------------------------------
        # WAIT
        # -------------------------------------------------

        print(
            "Waiting for market open...",
            now
        )


        time.sleep(
            WAIT_BEFORE_MARKET_SECONDS
        )


# =========================================================
# CONTINUOUS BOT LOOP
# =========================================================

def run_bot():

    # =====================================================
    # WAIT FOR 09:15
    # =====================================================

    if not wait_for_market_open():

        return


    # =====================================================
    # CONTINUOUS LOOP
    # =====================================================

    while True:

        now = now_ist()


        # =================================================
        # EXACT MARKET CLOSE CHECK
        #
        # At / after 15:30 IST:
        #     stop immediately
        # =================================================

        if now.time() >= MARKET_CLOSE:

            print()
            print(
                "=========================================="
            )

            print(
                "       MARKET CLOSED - BOT STOPPED"
            )

            print(
                "=========================================="
            )

            print(
                "BOT TIME:",
                now
            )

            print(
                "MARKET CLOSE:",
                MARKET_CLOSE
            )

            print(
                "Trading bot stopped for today."
            )

            break


        # =================================================
        # BOT STATUS
        # =================================================

        print()
        print(
            "------------------------------------------"
        )

        print(
            "BOT TIME:",
            now
        )

        print(
            "------------------------------------------"
        )


        # =================================================
        # RUN STRATEGY
        # =================================================

        try:

            main()

        except Exception as exc:

            print()
            print(
                "=========================================="
            )

            print(
                "          UNEXPECTED BOT ERROR"
            )

            print(
                "=========================================="
            )

            print(
                "ERROR TYPE:",
                type(exc).__name__
            )

            print(
                "ERROR:",
                str(exc)
            )


        # =================================================
        # CHECK MARKET CLOSE AGAIN
        # =================================================

        now = now_ist()


        if now.time() >= MARKET_CLOSE:

            print()
            print(
                "=========================================="
            )

            print(
                "       MARKET CLOSED - BOT STOPPED"
            )

            print(
                "=========================================="
            )

            print(
                "BOT TIME:",
                now
            )

            print(
                "Trading bot stopped for today."
            )

            break


        # =================================================
        # NEXT CHECK
        # =================================================

        print()
        print(
            "Next strategy check in 5 minutes..."
        )


        print(
            "Next check approximately:",
            now + pd.Timedelta(
                seconds=CHECK_INTERVAL_SECONDS
            )
        )


        print()


        time.sleep(
            CHECK_INTERVAL_SECONDS
        )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    try:

        run_bot()


    except KeyboardInterrupt:

        print()
        print(
            "=========================================="
        )

        print(
            "       BOT STOPPED MANUALLY"
        )

        print(
            "=========================================="
        )


    except Exception as exc:

        print()
        print(
            "=========================================="
        )

        print(
            "       FATAL BOT ERROR"
        )

        print(
            "=========================================="
        )

        print(
            "ERROR TYPE:",
            type(exc).__name__
        )

        print(
            "ERROR:",
            str(exc)
        )

