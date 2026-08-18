




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
# #
# # KEEP FALSE WHILE TESTING.
# #
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
# # GENERAL CONFIG
# # =========================================================

# LOTS = 1

# TIMEFRAME = "5minute"


# # =========================================================
# # MARKET TIMINGS
# # =========================================================

# MARKET_OPEN = dt_time(9, 15)

# ENTRY_START = dt_time(9, 20)

# ENTRY_END = dt_time(14, 45)

# FORCE_EXIT_TIME = dt_time(15, 15)

# MARKET_CLOSE = dt_time(15, 30)


# # =========================================================
# # BOT LOOP
# # =========================================================

# CHECK_INTERVAL_SECONDS = 300

# WAIT_BEFORE_MARKET_SECONDS = 30


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
# # FILE
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
# # LOGIN / ENVIRONMENT
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
# #
# # GitHub Actions:
# #     KITE_ACCESS_TOKEN environment variable
# #
# # Local PC:
# #     access_token.txt
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

#             ACCESS_TOKEN = (
#                 f.read()
#                 .strip()
#             )

#     else:

#         raise SystemExit(
#             "KITE_ACCESS_TOKEN is not set "
#             "and access_token.txt was not found."
#         )


# if not ACCESS_TOKEN:

#     raise SystemExit(
#         "KITE_ACCESS_TOKEN is empty "
#         "and access_token.txt is empty."
#     )


# # =========================================================
# # KITE CONNECTION
# # =========================================================

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


# # =========================================================
# # MARKET STATUS
# # =========================================================

# def market_is_open():

#     t = now_ist().time()

#     return (
#         MARKET_OPEN
#         <= t
#         <= MARKET_CLOSE
#     )


# # =========================================================
# # ENTRY WINDOW
# # =========================================================

# def entry_window_open():

#     t = now_ist().time()

#     return (
#         ENTRY_START
#         <= t
#         <= ENTRY_END
#     )


# # =========================================================
# # MARKET CLOSED
# # =========================================================

# def market_has_closed():

#     return (
#         now_ist().time()
#         >= MARKET_CLOSE
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

#             from_date=
#                 start.to_pydatetime(),

#             to_date=
#                 now.to_pydatetime(),

#             interval=TIMEFRAME,
#         )

#     except Exception as exc:

#         print(
#             "DATA ERROR:",
#             type(exc).__name__,
#             str(exc)
#         )

#         return []


# # =========================================================
# # REMOVE CURRENT INCOMPLETE CANDLE
# # =========================================================

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

#         .reset_index(
#             drop=True
#         )
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
# # FIND OPTION
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
#             +
#             ":"
#             +
#             symbol
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
#             "SETUP: NONE"
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
#         *
#         LOTS
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
#     # PREMIUM SETUP MUST BE LATEST CLOSED CANDLE
#     # -----------------------------------------------------

#     latest_premium = (
#         premium_df.iloc[-1]
#     )


#     if (

#         pd.Timestamp(
#             premium_pullback[
#                 "date"
#             ]
#         )

#         !=

#         pd.Timestamp(
#             latest_premium[
#                 "date"
#             ]
#         )

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


#     # -----------------------------------------------------
#     # SIGNAL
#     # -----------------------------------------------------

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

#         # Fail safe:
#         # if Zerodha cannot confirm positions,
#         # do not open a new trade.

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


#     # =====================================================
#     # PAPER MODE
#     # =====================================================

#     if not LIVE_MODE:

#         print(
#             "PAPER MODE:"
#             " NO REAL ORDER PLACED."
#         )

#         return True


#     # =====================================================
#     # LIVE ORDER
#     # =====================================================

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
# # MAIN STRATEGY RUN
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


#     # =====================================================
#     # CONNECTION
#     # =====================================================

#     if not test_connection():

#         return


#     # =====================================================
#     # MARKET OPEN CHECK
#     # =====================================================

#     if not market_is_open():

#         print(
#             "Market is closed."
#         )

#         return


#     # =====================================================
#     # ENTRY WINDOW
#     #
#     # After 14:45:
#     #     Bot continues running
#     #     but no new entry is allowed.
#     # =====================================================

#     if not entry_window_open():

#         print(
#             "Outside entry window."
#         )

#         print(
#             "No new trade will be entered."
#         )

#         return


#     # =====================================================
#     # EXISTING POSITION
#     # =====================================================

#     if has_open_position():

#         print(
#             "Existing position detected."
#         )


#         print(
#             "No new trade."
#         )


#         return


#     # =====================================================
#     # LOAD NFO
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


#     # =====================================================
#     # LOAD BFO
#     # =====================================================

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


#     # =====================================================
#     # NO SIGNAL
#     # =====================================================

#     if not signals:

#         print()
#         print(
#             "NO TRADE ON NIFTY OR SENSEX."
#         )

#         return


#     # =====================================================
#     # SELECT SIGNAL
#     #
#     # If both NIFTY and SENSEX generate a signal
#     # during the same check, choose the first signal.
#     #
#     # This prevents two positions from opening
#     # at the same time.
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
# # WAIT UNTIL MARKET OPEN
# # =========================================================

# def wait_for_market_open():

#     print()
#     print(
#         "=========================================="
#     )

#     print(
#         "       NIFTY + SENSEX TRADING BOT"
#     )

#     print(
#         "=========================================="
#     )

#     print(
#         "MARKET OPEN :",
#         MARKET_OPEN
#     )

#     print(
#         "ENTRY START :",
#         ENTRY_START
#     )

#     print(
#         "ENTRY END   :",
#         ENTRY_END
#     )

#     print(
#         "MARKET CLOSE:",
#         MARKET_CLOSE
#     )

#     print(
#         "CHECK EVERY :",
#         CHECK_INTERVAL_SECONDS,
#         "seconds"
#     )

#     print(
#         "=========================================="
#     )


#     while True:

#         now = now_ist()


#         # -------------------------------------------------
#         # MARKET ALREADY CLOSED
#         # -------------------------------------------------

#         if now.time() >= MARKET_CLOSE:

#             print()
#             print(
#                 "=========================================="
#             )

#             print(
#                 "       MARKET CLOSED - BOT STOPPED"
#             )

#             print(
#                 "=========================================="
#             )

#             print(
#                 "BOT TIME:",
#                 now
#             )

#             return False


#         # -------------------------------------------------
#         # MARKET OPEN
#         # -------------------------------------------------

#         if now.time() >= MARKET_OPEN:

#             print()
#             print(
#                 "Market is open."
#             )

#             print(
#                 "Starting strategy checks..."
#             )

#             return True


#         # -------------------------------------------------
#         # WAIT
#         # -------------------------------------------------

#         print(
#             "Waiting for market open...",
#             now
#         )


#         time.sleep(
#             WAIT_BEFORE_MARKET_SECONDS
#         )


# # =========================================================
# # CONTINUOUS BOT LOOP
# # =========================================================

# def run_bot():

#     # =====================================================
#     # WAIT FOR 09:15
#     # =====================================================

#     if not wait_for_market_open():

#         return


#     # =====================================================
#     # CONTINUOUS LOOP
#     # =====================================================

#     while True:

#         now = now_ist()


#         # =================================================
#         # EXACT MARKET CLOSE CHECK
#         #
#         # At / after 15:30 IST:
#         #     stop immediately
#         # =================================================

#         if now.time() >= MARKET_CLOSE:

#             print()
#             print(
#                 "=========================================="
#             )

#             print(
#                 "       MARKET CLOSED - BOT STOPPED"
#             )

#             print(
#                 "=========================================="
#             )

#             print(
#                 "BOT TIME:",
#                 now
#             )

#             print(
#                 "MARKET CLOSE:",
#                 MARKET_CLOSE
#             )

#             print(
#                 "Trading bot stopped for today."
#             )

#             break


#         # =================================================
#         # BOT STATUS
#         # =================================================

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


#         # =================================================
#         # RUN STRATEGY
#         # =================================================

#         try:

#             main()

#         except Exception as exc:

#             print()
#             print(
#                 "=========================================="
#             )

#             print(
#                 "          UNEXPECTED BOT ERROR"
#             )

#             print(
#                 "=========================================="
#             )

#             print(
#                 "ERROR TYPE:",
#                 type(exc).__name__
#             )

#             print(
#                 "ERROR:",
#                 str(exc)
#             )


#         # =================================================
#         # CHECK MARKET CLOSE AGAIN
#         # =================================================

#         now = now_ist()


#         if now.time() >= MARKET_CLOSE:

#             print()
#             print(
#                 "=========================================="
#             )

#             print(
#                 "       MARKET CLOSED - BOT STOPPED"
#             )

#             print(
#                 "=========================================="
#             )

#             print(
#                 "BOT TIME:",
#                 now
#             )

#             print(
#                 "Trading bot stopped for today."
#             )

#             break


#         # =================================================
#         # NEXT CHECK
#         # =================================================

#         print()
#         print(
#             "Next strategy check in 5 minutes..."
#         )


#         print(
#             "Next check approximately:",
#             now + pd.Timedelta(
#                 seconds=CHECK_INTERVAL_SECONDS
#             )
#         )


#         print()


#         time.sleep(
#             CHECK_INTERVAL_SECONDS
#         )


# # =========================================================
# # START
# # =========================================================

# if __name__ == "__main__":

#     try:

#         run_bot()


#     except KeyboardInterrupt:

#         print()
#         print(
#             "=========================================="
#         )

#         print(
#             "       BOT STOPPED MANUALLY"
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
#             "       FATAL BOT ERROR"
#         )

#         print(
#             "=========================================="
#         )

#         print(
#             "ERROR TYPE:",
#             type(exc).__name__
#         )

#         print(
#             "ERROR:",
#             str(exc)
#         )

import os
import time
import json
import html
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

LIVE_MODE = False


# =========================================================
# MARKET CONFIG
# =========================================================

MARKETS = {
    "NIFTY": {
        "index_token": 256265,
        "spot_symbol": "NSE:NIFTY 50",
        "option_exchange": "NFO",
        "underlying_name": "NIFTY",
        "strike_interval": 50,
        "default_lot": 65,
    },
    "SENSEX": {
        "index_token": 265,
        "spot_symbol": "BSE:SENSEX",
        "option_exchange": "BFO",
        "underlying_name": "SENSEX",
        "strike_interval": 100,
        "default_lot": 20,
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
# FILES
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

DASHBOARD_FILE = os.path.join(
    SCRIPT_DIR,
    "trading_dashboard.html"
)

DASHBOARD_DATA_FILE = os.path.join(
    SCRIPT_DIR,
    "dashboard_trades.json"
)


# =========================================================
# LOGIN
# =========================================================

load_dotenv()

API_KEY = os.getenv("KITE_API_KEY")

if not API_KEY:
    raise SystemExit("KITE_API_KEY missing.")

ACCESS_TOKEN = os.getenv(
    "KITE_ACCESS_TOKEN"
)

if not ACCESS_TOKEN:
    if os.path.exists(ACCESS_TOKEN_FILE):
        with open(
            ACCESS_TOKEN_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            ACCESS_TOKEN = f.read().strip()
    else:
        raise SystemExit(
            "KITE_ACCESS_TOKEN is not set "
            "and access_token.txt was not found."
        )

if not ACCESS_TOKEN:
    raise SystemExit(
        "KITE_ACCESS_TOKEN is empty."
    )


# =========================================================
# KITE
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
# DASHBOARD
# =========================================================

def _dashboard_rows():
    if not os.path.exists(
        DASHBOARD_DATA_FILE
    ):
        return []

    try:
        with open(
            DASHBOARD_DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        return data if isinstance(data, list) else []

    except Exception:
        return []


def _save_dashboard_rows(rows):
    temp_file = (
        DASHBOARD_DATA_FILE + ".tmp"
    )

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            rows,
            f,
            indent=2
        )

    os.replace(
        temp_file,
        DASHBOARD_DATA_FILE
    )


def create_dashboard():
    rows = _dashboard_rows()

    mode = (
        "LIVE"
        if LIVE_MODE
        else "PAPER"
    )

    cards = f"""
    <div class="card">
        <span>MODE</span>
        <strong>{mode}</strong>
    </div>
    <div class="card">
        <span>TRADES</span>
        <strong>{len(rows)}</strong>
    </div>
    """

    table_rows = ""

    for trade in reversed(rows):
        table_rows += f"""
        <tr>
            <td>{html.escape(str(trade.get("time", "")))}</td>
            <td>{html.escape(str(trade.get("mode", "")))}</td>
            <td>{html.escape(str(trade.get("market", "")))}</td>
            <td>{html.escape(str(trade.get("direction", "")))}</td>
            <td>{html.escape(str(trade.get("symbol", "")))}</td>
            <td>{html.escape(str(trade.get("quantity", "")))}</td>
            <td>{html.escape(str(trade.get("entry", "")))}</td>
            <td>{html.escape(str(trade.get("stop_loss", "")))}</td>
            <td>{html.escape(str(trade.get("target", "")))}</td>
            <td>{html.escape(str(trade.get("risk_points", "")))}</td>
            <td>{html.escape(str(trade.get("status", "")))}</td>
        </tr>
        """

    if not table_rows:
        table_rows = """
        <tr>
            <td colspan="11" class="empty">
                No trades yet
            </td>
        </tr>
        """

    page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="5">
<title>NIFTY SENSEX Trading Dashboard</title>

<style>
* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 25px;
    font-family: Arial, sans-serif;
    background: #0f172a;
    color: #e2e8f0;
}}

h1 {{
    margin-bottom: 5px;
}}

.subtitle {{
    color: #94a3b8;
    margin-bottom: 25px;
}}

.cards {{
    display: flex;
    gap: 15px;
    margin-bottom: 25px;
}}

.card {{
    min-width: 180px;
    padding: 18px;
    border-radius: 12px;
    background: #1e293b;
    border: 1px solid #334155;
}}

.card span {{
    display: block;
    color: #94a3b8;
    font-size: 12px;
    margin-bottom: 8px;
}}

.card strong {{
    font-size: 24px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    background: #1e293b;
    border-radius: 12px;
    overflow: hidden;
}}

th {{
    background: #334155;
    color: #f8fafc;
    padding: 12px;
    text-align: left;
    font-size: 13px;
}}

td {{
    padding: 11px;
    border-bottom: 1px solid #334155;
    font-size: 13px;
}}

tr:hover {{
    background: #263449;
}}

.empty {{
    text-align: center;
    color: #94a3b8;
    padding: 30px;
}}

.paper {{
    color: #facc15;
}}

.live {{
    color: #4ade80;
}}
</style>
</head>

<body>

<h1>NIFTY + SENSEX Trading Dashboard</h1>

<div class="subtitle">
    Automatically updated whenever a PAPER or LIVE trade is placed.
    Page refreshes every 5 seconds.
</div>

<div class="cards">
    {cards}
</div>

<table>
<thead>
<tr>
    <th>Time</th>
    <th>Mode</th>
    <th>Market</th>
    <th>Direction</th>
    <th>Symbol</th>
    <th>Qty</th>
    <th>Entry</th>
    <th>SL</th>
    <th>Target</th>
    <th>Risk</th>
    <th>Status</th>
</tr>
</thead>

<tbody>
{table_rows}
</tbody>

</table>

</body>
</html>
"""

    temp_file = DASHBOARD_FILE + ".tmp"

    with open(
        temp_file,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(page)

    os.replace(
        temp_file,
        DASHBOARD_FILE
    )


def record_trade(
    signal,
    status,
    order_id=""
):
    trade = {
        "time": str(now_ist()),
        "mode": (
            "LIVE"
            if LIVE_MODE
            else "PAPER"
        ),
        "market": signal.get(
            "market",
            ""
        ),
        "direction": signal.get(
            "direction",
            ""
        ),
        "symbol": signal.get(
            "option_symbol",
            ""
        ),
        "quantity": signal.get(
            "quantity",
            0
        ),
        "entry": round(
            float(signal.get(
                "entry",
                0
            )),
            2
        ),
        "stop_loss": round(
            float(signal.get(
                "stop_loss",
                0
            )),
            2
        ),
        "target": round(
            float(signal.get(
                "target",
                0
            )),
            2
        ),
        "risk_points": round(
            float(signal.get(
                "risk_points",
                0
            )),
            2
        ),
        "status": status,
        "order_id": order_id,
    }

    rows = _dashboard_rows()

    rows.append(trade)

    _save_dashboard_rows(rows)

    create_dashboard()

    print()
    print("==========================================")
    print("       DASHBOARD TRADE RECORDED")
    print("==========================================")
    print("MODE:", trade["mode"])
    print("MARKET:", trade["market"])
    print("DIRECTION:", trade["direction"])
    print("SYMBOL:", trade["symbol"])
    print("ENTRY:", trade["entry"])
    print("SL:", trade["stop_loss"])
    print("TARGET:", trade["target"])
    print("STATUS:", trade["status"])

    if order_id:
        print("ORDER ID:", order_id)

    print("DASHBOARD:", DASHBOARD_FILE)
    print("==========================================")


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


def entry_window_open():
    t = now_ist().time()

    return (
        ENTRY_START
        <= t
        <= ENTRY_END
    )


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
            profile.get("user_name")
        )

        print(
            "USER ID:",
            profile.get("user_id")
        )

        print(
            "MODE:",
            "LIVE" if LIVE_MODE else "PAPER"
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

def fetch_today_candles(token):
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
            from_date=start.to_pydatetime(),
            to_date=now.to_pydatetime(),
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
# REMOVE CURRENT CANDLE
# =========================================================

def remove_current_candle(df):
    if df.empty:
        return df

    current_start = now_ist().floor("5min")

    return (
        df[
            df["date"] < current_start
        ]
        .copy()
        .reset_index(drop=True)
    )


# =========================================================
# SPOT
# =========================================================

def get_spot(symbol):
    try:
        data = kite.quote([symbol])

        return float(
            data[symbol]["last_price"]
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

def get_instruments(exchange):
    try:
        return kite.instruments(exchange)

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
            spot /
            config["strike_interval"]
        )
        * config["strike_interval"]
    )

    today = date.today()
    candidates = []

    for instrument in instruments:
        try:
            if instrument.get("name") != \
                    config["underlying_name"]:
                continue

            if instrument.get("instrument_type") != \
                    direction:
                continue

            if float(
                instrument.get("strike", 0)
            ) != float(atm):
                continue

            expiry = instrument.get("expiry")

            if not expiry or expiry < today:
                continue

            candidates.append(instrument)

        except Exception:
            continue

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: x["expiry"]
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
            exchange +
            ":" +
            symbol
        )

        data = kite.ltp([key])

        return float(
            data[key]["last_price"]
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
    print("==========================================")
    print("CHECKING:", market_name)
    print("==========================================")

    raw = fetch_today_candles(
        config["index_token"]
    )

    if not raw:
        print("No", market_name, "data.")
        return None

    df = calculate_indicators(raw)
    df = remove_current_candle(df)

    if len(df) < 2:
        print(
            "Not enough completed",
            market_name,
            "candles."
        )
        return None

    latest = df.iloc[-1]

    print("Latest:", latest["date"])
    print(
        "Close:",
        round(float(latest["close"]), 2)
    )

    print(
        "EMA20:",
        round(float(latest["ema20"]), 2)
    )

    print(
        "VWAP:",
        round(float(latest["vwap"]), 2)
    )

    if market_name == "NIFTY":
        setups = find_nifty_setups(df)
    else:
        setups = find_sensex_setups(df)

    if not setups:
        print(
            market_name,
            "SETUP: NONE"
        )
        return None

    setup = setups[-1]

    direction = setup["direction"]
    breakout = setup["breakout"]
    pullback = setup["pullback"]

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

    spot = get_spot(
        config["spot_symbol"]
    )

    if spot is None:
        return None

    option = find_option(
        option_instruments,
        config,
        direction,
        spot
    )

    if option is None:
        print("Option not found.")
        return None

    option_symbol = option["tradingsymbol"]
    option_token = option["instrument_token"]

    option_lot = int(
        option.get(
            "lot_size",
            config["default_lot"]
        )
    )

    quantity = option_lot * LOTS

    print(
        "Option:",
        option_symbol
    )

    print(
        "Exchange:",
        config["option_exchange"]
    )

    print(
        "Lot size:",
        option_lot
    )

    print(
        "Quantity:",
        quantity
    )

    premium_raw = fetch_today_candles(
        option_token
    )

    if not premium_raw:
        print("No premium candles.")
        return None

    premium_df = calculate_indicators(
        premium_raw
    )

    premium_df = remove_current_candle(
        premium_df
    )

    if len(premium_df) < 2:
        return None

    if market_name == "NIFTY":
        premium_setups = find_premium_setups(
            premium_df,
            pd.Timestamp(breakout["date"]),
            pd.Timestamp(pullback["date"])
        )
    else:
        premium_setups = find_sensex_premium_setups(
            premium_df,
            pd.Timestamp(breakout["date"]),
            pd.Timestamp(pullback["date"])
        )

    if not premium_setups:
        print("Premium setup: NONE")
        return None

    premium_setup = premium_setups[-1]

    premium_breakout = premium_setup["breakout"]
    premium_pullback = premium_setup["pullback"]

    latest_premium = premium_df.iloc[-1]

    if (
        pd.Timestamp(
            premium_pullback["date"]
        )
        !=
        pd.Timestamp(
            latest_premium["date"]
        )
    ):
        print("Premium setup is old.")
        return None

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
        print("Invalid risk.")
        return None

    return {
        "market": market_name,
        "direction": direction,
        "option_symbol": option_symbol,
        "option_token": option_token,
        "option_exchange": config["option_exchange"],
        "quantity": quantity,
        "entry": risk["entry"],
        "stop_loss": risk["stop_loss"],
        "target": risk["target"],
        "risk_points": risk["risk_points"],
        "nifty_or_sensex_breakout": str(
            breakout["date"]
        ),
        "nifty_or_sensex_pullback": str(
            pullback["date"]
        ),
        "premium_breakout": str(
            premium_breakout["date"]
        ),
        "premium_pullback": str(
            premium_pullback["date"]
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

        return True


# =========================================================
# BUY
# =========================================================

def place_buy(signal):
    print()
    print("==========================================")
    print("             TRADE SIGNAL")
    print("==========================================")

    print(
        "Market:",
        signal["market"]
    )

    print(
        "Action: BUY",
        signal["direction"]
    )

    print(
        "Symbol:",
        signal["option_symbol"]
    )

    print(
        "Exchange:",
        signal["option_exchange"]
    )

    print(
        "Quantity:",
        signal["quantity"]
    )

    print(
        "Entry:",
        round(signal["entry"], 2)
    )

    print(
        "SL:",
        round(signal["stop_loss"], 2)
    )

    print(
        "Target:",
        round(signal["target"], 2)
    )

    # =====================================================
    # PAPER MODE
    # =====================================================

    if not LIVE_MODE:
        print(
            "PAPER MODE: NO REAL ORDER PLACED."
        )

        record_trade(
            signal,
            "PAPER_TRADE"
        )

        return True

    # =====================================================
    # LIVE ORDER
    # =====================================================

    try:
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=signal[
                "option_exchange"
            ],
            tradingsymbol=signal[
                "option_symbol"
            ],
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=signal["quantity"],
            product=kite.PRODUCT_MIS,
            order_type=kite.ORDER_TYPE_MARKET,
            validity=kite.VALIDITY_DAY,
            market_protection=-1,
            tag="NIF_SEN_ALGO",
        )

        print(
            "ORDER ID:",
            order_id
        )

        # Dashboard is updated ONLY
        # after Zerodha accepts the order.
        record_trade(
            signal,
            "LIVE_ORDER_PLACED",
            order_id
        )

        return True

    except Exception as exc:
        print(
            "BUY ORDER ERROR:",
            type(exc).__name__,
            str(exc)
        )

        # Failed LIVE order is not
        # recorded as a successful trade.
        return False


# =========================================================
# MAIN STRATEGY RUN
# =========================================================

def main():
    print()
    print("==========================================")
    print("     NIFTY + SENSEX LIVE TRADER")
    print("          EMA20 + VWAP ONLY")
    print("==========================================")

    print("TIME:", now_ist())

    print(
        "MODE:",
        "LIVE" if LIVE_MODE else "PAPER"
    )

    if not test_connection():
        return

    if not market_is_open():
        print("Market is closed.")
        return

    if not entry_window_open():
        print("Outside entry window.")
        print("No new trade will be entered.")
        return

    if has_open_position():
        print("Existing position detected.")
        print("No new trade.")
        return

    print()
    print("Loading NFO instruments...")

    nfo_instruments = get_instruments("NFO")

    print(
        "NFO instruments:",
        len(nfo_instruments)
    )

    print()
    print("Loading BFO instruments...")

    bfo_instruments = get_instruments("BFO")

    print(
        "BFO instruments:",
        len(bfo_instruments)
    )

    nifty_signal = check_market(
        "NIFTY",
        MARKETS["NIFTY"],
        nfo_instruments
    )

    sensex_signal = check_market(
        "SENSEX",
        MARKETS["SENSEX"],
        bfo_instruments
    )

    signals = []

    if nifty_signal is not None:
        signals.append(nifty_signal)

    if sensex_signal is not None:
        signals.append(sensex_signal)

    if not signals:
        print()
        print(
            "NO TRADE ON NIFTY OR SENSEX."
        )
        return

    selected = signals[0]

    for signal in signals:
        print()
        print(
            "VALID SIGNAL:",
            signal["market"],
            signal["direction"],
            signal["option_symbol"]
        )

    print()
    print(
        "SELECTED:",
        selected["market"],
        selected["option_symbol"]
    )

    place_buy(selected)


# =========================================================
# WAIT FOR MARKET
# =========================================================

def wait_for_market_open():
    print()
    print("==========================================")
    print("       NIFTY + SENSEX TRADING BOT")
    print("==========================================")

    print("MARKET OPEN :", MARKET_OPEN)
    print("ENTRY START :", ENTRY_START)
    print("ENTRY END   :", ENTRY_END)
    print("MARKET CLOSE:", MARKET_CLOSE)

    print(
        "CHECK EVERY :",
        CHECK_INTERVAL_SECONDS,
        "seconds"
    )

    print("==========================================")

    while True:
        now = now_ist()

        if now.time() >= MARKET_CLOSE:
            print()
            print("MARKET CLOSED - BOT STOPPED")
            print("BOT TIME:", now)
            return False

        if now.time() >= MARKET_OPEN:
            print()
            print("Market is open.")
            print("Starting strategy checks...")
            return True

        print(
            "Waiting for market open...",
            now
        )

        time.sleep(
            WAIT_BEFORE_MARKET_SECONDS
        )


# =========================================================
# CONTINUOUS BOT
# =========================================================

def run_bot():
    # Create dashboard immediately.
    create_dashboard()

    if not wait_for_market_open():
        return

    while True:
        now = now_ist()

        if now.time() >= MARKET_CLOSE:
            print()
            print("MARKET CLOSED - BOT STOPPED")
            print("BOT TIME:", now)
            print("MARKET CLOSE:", MARKET_CLOSE)
            print(
                "Trading bot stopped for today."
            )
            break

        print()
        print("------------------------------------------")
        print("BOT TIME:", now)
        print("------------------------------------------")

        try:
            main()

        except Exception as exc:
            print()
            print("==========================================")
            print("          UNEXPECTED BOT ERROR")
            print("==========================================")
            print(
                "ERROR TYPE:",
                type(exc).__name__
            )
            print("ERROR:", str(exc))

        now = now_ist()

        if now.time() >= MARKET_CLOSE:
            print()
            print("MARKET CLOSED - BOT STOPPED")
            print("BOT TIME:", now)
            print(
                "Trading bot stopped for today."
            )
            break

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
        print("==========================================")
        print("       BOT STOPPED MANUALLY")
        print("==========================================")

    except Exception as exc:
        print()
        print("==========================================")
        print("       FATAL BOT ERROR")
        print("==========================================")

        print(
            "ERROR TYPE:",
            type(exc).__name__
        )

        print(
            "ERROR:",
            str(exc)
        )