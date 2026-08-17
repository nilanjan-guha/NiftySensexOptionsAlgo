# bot.py


import csv
import json
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
    get_setup_strength,
    recommended_rr,
    MAX_SETUP_GAP_MINUTES,
)


# =========================================================
# MODE
# =========================================================
#
# FALSE = PAPER TRADING
#
# TRUE = REAL ZERODHA ORDERS
#
# IMPORTANT:
#
# Keep FALSE while testing.
#
# When you are completely satisfied with paper trading,
# change only this:
#
# LIVE_MODE = True
#
# The same trade tracking logic is used in both modes.
# =========================================================

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
# MARKET TIMING
# =========================================================

MARKET_OPEN = dt_time(
    9,
    15
)

ENTRY_START = dt_time(
    9,
    20
)

ENTRY_END = dt_time(
    14,
    45
)

FORCE_EXIT_TIME = dt_time(
    15,
    15
)

MARKET_CLOSE = dt_time(
    15,
    30
)


# =========================================================
# BOT TIMING
# =========================================================

STRATEGY_CHECK_SECONDS = 300

TRADE_MONITOR_SECONDS = 5

WAIT_BEFORE_MARKET_SECONDS = 30


# =========================================================
# DAILY LIMIT
# =========================================================

MAX_TRADES_PER_DAY = 3


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

ACTIVE_TRADE_FILE = os.path.join(
    SCRIPT_DIR,
    "active_trade.json"
)

TRADE_LOG_FILE = os.path.join(
    SCRIPT_DIR,
    "trades.csv"
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv(
    os.path.join(
        SCRIPT_DIR,
        ".env"
    )
)


API_KEY = os.getenv(
    "KITE_API_KEY"
)


if not API_KEY:

    raise SystemExit(
        "KITE_API_KEY missing from .env"
    )


# =========================================================
# ACCESS TOKEN
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
        ) as file:

            ACCESS_TOKEN = (
                file.read()
                .strip()
            )


if not ACCESS_TOKEN:

    raise SystemExit(
        "KITE_ACCESS_TOKEN missing "
        "and access_token.txt not found."
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
# MARKET STATUS
# =========================================================

def market_is_open():

    current = now_ist().time()

    return (
        MARKET_OPEN
        <=
        current
        <=
        MARKET_CLOSE
    )


def entry_window_open():

    current = now_ist().time()

    return (
        ENTRY_START
        <=
        current
        <=
        ENTRY_END
    )


def force_exit_time_reached():

    return (
        now_ist().time()
        >=
        FORCE_EXIT_TIME
    )


def market_close_reached():

    return (
        now_ist().time()
        >=
        MARKET_CLOSE
    )


# =========================================================
# FILE HELPERS
# =========================================================

def save_json(
    path,
    data
):

    temporary = (
        path
        +
        ".tmp"
    )

    with open(
        temporary,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            default=str
        )

    os.replace(
        temporary,
        path
    )


def load_json(path):

    if not os.path.exists(path):

        return None

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception as exc:

        print(
            "Could not read:",
            path
        )

        print(
            type(exc).__name__,
            str(exc)
        )

        return None


def delete_file(path):

    try:

        if os.path.exists(path):

            os.remove(path)

    except Exception as exc:

        print(
            "FILE DELETE ERROR:",
            type(exc).__name__,
            str(exc)
        )


# =========================================================
# ACTIVE TRADE
# =========================================================

def get_active_trade():

    return load_json(
        ACTIVE_TRADE_FILE
    )


def save_active_trade(
    trade
):

    save_json(
        ACTIVE_TRADE_FILE,
        trade
    )


def clear_active_trade():

    delete_file(
        ACTIVE_TRADE_FILE
    )


# =========================================================
# TRADE LOG
# =========================================================

TRADE_COLUMNS = [
    "date",
    "market",
    "direction",
    "symbol",
    "exchange",
    "quantity",
    "entry",
    "stop_loss",
    "target",
    "exit",
    "pnl",
    "result",
    "entry_mode",
    "entry_order_id",
    "exit_order_id",
    "entry_time",
    "exit_time",
]


def log_trade(
    trade,
    exit_price,
    result,
    exit_order_id=""
):

    file_exists = os.path.exists(
        TRADE_LOG_FILE
    )

    entry = float(
        trade["entry_price"]
    )

    exit_price = float(
        exit_price
    )

    quantity = int(
        trade["quantity"]
    )

    pnl = (
        exit_price
        -
        entry
    ) * quantity

    row = {

        "date":
            str(
                now_ist().date()
            ),

        "market":
            trade["market"],

        "direction":
            trade["direction"],

        "symbol":
            trade["symbol"],

        "exchange":
            trade["exchange"],

        "quantity":
            quantity,

        "entry":
            entry,

        "stop_loss":
            trade["stop_loss"],

        "target":
            trade["target"],

        "exit":
            exit_price,

        "pnl":
            round(
                pnl,
                2
            ),

        "result":
            result,

        "entry_mode":
            trade["entry_mode"],

        "entry_order_id":
            trade.get(
                "entry_order_id",
                ""
            ),

        "exit_order_id":
            exit_order_id,

        "entry_time":
            trade.get(
                "entry_time",
                ""
            ),

        "exit_time":
            str(
                now_ist()
            ),
    }

    with open(
        TRADE_LOG_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=TRADE_COLUMNS
        )

        if not file_exists:

            writer.writeheader()

        writer.writerow(
            row
        )

    print()
    print(
        "TRADE LOGGED"
    )

    print(
        "Result:",
        result
    )

    print(
        "Entry:",
        entry
    )

    print(
        "Exit:",
        exit_price
    )

    print(
        "P&L:",
        round(
            pnl,
            2
        )
    )


# =========================================================
# TODAY TRADE COUNT
# =========================================================

def get_today_trade_count():

    if not os.path.exists(
        TRADE_LOG_FILE
    ):

        return 0

    today = str(
        now_ist().date()
    )

    count = 0

    try:

        with open(
            TRADE_LOG_FILE,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(
                file
            )

            for row in reader:

                if row.get(
                    "date"
                ) == today:

                    count += 1

    except Exception as exc:

        print(
            "TRADE COUNT ERROR:",
            type(exc).__name__,
            str(exc)
        )

    return count


# =========================================================
# CONNECTION
# =========================================================

def test_connection():

    try:

        profile = kite.profile()

        print()
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

        print()
        print(
            "ZERODHA CONNECTION ERROR"
        )

        print(
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
            type(exc).__name__,
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
            type(exc).__name__,
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

    if spot is None:

        return None

    interval = float(
        config[
            "strike_interval"
        ]
    )

    atm = (
        round(
            float(spot)
            /
            interval
        )
        *
        interval
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
# LTP
# =========================================================

def get_option_ltp(
    exchange,
    symbol
):

    key = (
        exchange
        +
        ":"
        +
        symbol
    )

    try:

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
            key,
            type(exc).__name__,
            str(exc)
        )

        return None


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

            quantity = int(
                position.get(
                    "quantity",
                    0
                )
            )

            if quantity != 0:

                return True

        return False

    except Exception as exc:

        print(
            "POSITION ERROR:",
            type(exc).__name__,
            str(exc)
        )

        # Fail safe.
        return True


# =========================================================
# FIND EXECUTED PRICE
# =========================================================

def get_order_average_price(
    order_id,
    timeout_seconds=15
):

    start = time.time()

    while (
        time.time()
        -
        start
        <
        timeout_seconds
    ):

        try:

            orders = kite.orders()

            for order in orders:

                if str(
                    order.get(
                        "order_id"
                    )
                ) != str(
                    order_id
                ):

                    continue

                status = str(
                    order.get(
                        "status",
                        ""
                    )
                ).upper()

                if status == "COMPLETE":

                    average_price = order.get(
                        "average_price"
                    )

                    if average_price:

                        return float(
                            average_price
                        )

                if status in (
                    "REJECTED",
                    "CANCELLED",
                    "AMO REJECTED",
                ):

                    return None

        except Exception as exc:

            print(
                "ORDER STATUS ERROR:",
                type(exc).__name__,
                str(exc)
            )

        time.sleep(
            1
        )

    return None


# =========================================================
# BUY ORDER
# =========================================================

def execute_buy(
    signal
):

    print()
    print(
        "=========================================="
    )

    print(
        "BUY SIGNAL"
    )

    print(
        "=========================================="
    )

    print(
        "Market:",
        signal["market"]
    )

    print(
        "Direction:",
        signal["direction"]
    )

    print(
        "Symbol:",
        signal["option_symbol"]
    )

    print(
        "Quantity:",
        signal["quantity"]
    )

    print(
        "Expected Entry:",
        round(
            signal["entry"],
            2
        )
    )

    print(
        "SL:",
        round(
            signal["stop_loss"],
            2
        )
    )

    print(
        "Target:",
        round(
            signal["target"],
            2
        )
    )

    # =====================================================
    # PAPER
    # =====================================================

    if not LIVE_MODE:

        entry_price = float(
            signal["entry"]
        )

        trade = {

            "market":
                signal["market"],

            "direction":
                signal["direction"],

            "symbol":
                signal["option_symbol"],

            "exchange":
                signal["option_exchange"],

            "token":
                signal["option_token"],

            "quantity":
                signal["quantity"],

            "entry_price":
                entry_price,

            "stop_loss":
                signal["stop_loss"],

            "target":
                signal["target"],

            "entry_mode":
                "PAPER",

            "entry_order_id":
                "",

            "entry_time":
                str(
                    now_ist()
                ),

            "status":
                "OPEN",
        }

        save_active_trade(
            trade
        )

        print()
        print(
            "PAPER BUY EXECUTED"
        )

        print(
            "Entry:",
            round(
                entry_price,
                2
            )
        )

        print(
            "SL:",
            round(
                signal["stop_loss"],
                2
            )
        )

        print(
            "Target:",
            round(
                signal["target"],
                2
            )
        )

        return trade


    # =====================================================
    # LIVE
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
            "BUY ORDER:",
            order_id
        )

        actual_entry = (
            get_order_average_price(
                order_id
            )
        )

        if actual_entry is None:

            print(
                "BUY order was not confirmed."
            )

            return None

        # -------------------------------------------------
        # IMPORTANT:
        #
        # Recalculate SL/target from ACTUAL fill price.
        # -------------------------------------------------

        entry_difference = (
            actual_entry
            -
            signal["entry"]
        )

        actual_sl = (
            signal["stop_loss"]
            +
            entry_difference
        )

        actual_target = (
            actual_entry
            +
            (
                actual_entry
                -
                actual_sl
            )
            *
            signal["rr"]
        )

        trade = {

            "market":
                signal["market"],

            "direction":
                signal["direction"],

            "symbol":
                signal["option_symbol"],

            "exchange":
                signal["option_exchange"],

            "token":
                signal["option_token"],

            "quantity":
                signal["quantity"],

            "entry_price":
                actual_entry,

            "stop_loss":
                actual_sl,

            "target":
                actual_target,

            "entry_mode":
                "LIVE",

            "entry_order_id":
                str(
                    order_id
                ),

            "entry_time":
                str(
                    now_ist()
                ),

            "status":
                "OPEN",
        }

        save_active_trade(
            trade
        )

        print()
        print(
            "LIVE BUY EXECUTED"
        )

        print(
            "Actual Entry:",
            round(
                actual_entry,
                2
            )
        )

        print(
            "SL:",
            round(
                actual_sl,
                2
            )
        )

        print(
            "Target:",
            round(
                actual_target,
                2
            )
        )

        return trade

    except Exception as exc:

        print()
        print(
            "LIVE BUY ERROR:",
            type(exc).__name__,
            str(exc)
        )

        return None


# =========================================================
# SELL / EXIT
# =========================================================

def execute_exit(
    trade,
    exit_reason,
    observed_price
):

    print()
    print(
        "=========================================="
    )

    print(
        "EXIT:",
        exit_reason
    )

    print(
        "=========================================="
    )

    print(
        "Symbol:",
        trade["symbol"]
    )

    print(
        "Observed LTP:",
        round(
            observed_price,
            2
        )
    )

    print(
        "Entry:",
        round(
            float(
                trade["entry_price"]
            ),
            2
        )
    )

    print(
        "SL:",
        round(
            float(
                trade["stop_loss"]
            ),
            2
        )
    )

    print(
        "Target:",
        round(
            float(
                trade["target"]
            ),
            2
        )
    )

    # =====================================================
    # PAPER EXIT
    # =====================================================

    if not LIVE_MODE:

        exit_price = float(
            observed_price
        )

        log_trade(
            trade,
            exit_price,
            exit_reason,
            ""
        )

        clear_active_trade()

        print(
            "PAPER EXIT COMPLETE."
        )

        return True


    # =====================================================
    # LIVE EXIT
    # =====================================================

    try:

        order_id = kite.place_order(

            variety=
                kite.VARIETY_REGULAR,

            exchange=
                trade[
                    "exchange"
                ],

            tradingsymbol=
                trade[
                    "symbol"
                ],

            transaction_type=
                kite.TRANSACTION_TYPE_SELL,

            quantity=
                trade[
                    "quantity"
                ],

            product=
                kite.PRODUCT_MIS,

            order_type=
                kite.ORDER_TYPE_MARKET,

            validity=
                kite.VALIDITY_DAY,

            market_protection=-1,

            tag="NIF_SEN_EXIT",
        )

        print(
            "SELL ORDER:",
            order_id
        )

        actual_exit = (
            get_order_average_price(
                order_id
            )
        )

        if actual_exit is None:

            print()
            print(
                "WARNING:"
            )

            print(
                "SELL order was not confirmed."
            )

            print(
                "Active trade WILL remain saved."
            )

            print(
                "The bot will continue monitoring."
            )

            return False

        log_trade(
            trade,
            actual_exit,
            exit_reason,
            str(
                order_id
            )
        )

        clear_active_trade()

        print()
        print(
            "LIVE EXIT COMPLETE."
        )

        print(
            "Actual Exit:",
            round(
                actual_exit,
                2
            )
        )

        return True

    except Exception as exc:

        print()
        print(
            "LIVE SELL ERROR:",
            type(exc).__name__,
            str(exc)
        )

        print(
            "ACTIVE TRADE IS KEPT SAFE."
        )

        return False


# =========================================================
# ACTIVE TRADE MONITOR
# =========================================================

def monitor_active_trade():

    trade = get_active_trade()

    if trade is None:

        return False

    print()
    print(
        "=========================================="
    )

    print(
        "ACTIVE TRADE FOUND"
    )

    print(
        "=========================================="
    )

    print(
        "Market:",
        trade["market"]
    )

    print(
        "Symbol:",
        trade["symbol"]
    )

    print(
        "Entry:",
        trade["entry_price"]
    )

    print(
        "SL:",
        trade["stop_loss"]
    )

    print(
        "Target:",
        trade["target"]
    )

    print(
        "Mode:",
        trade["entry_mode"]
    )

    print()
    print(
        "Starting continuous trade monitoring..."
    )


    while True:

        # -------------------------------------------------
        # FORCE EXIT
        # -------------------------------------------------

        if force_exit_time_reached():

            ltp = get_option_ltp(
                trade["exchange"],
                trade["symbol"]
            )

            if ltp is None:

                print(
                    "Could not get LTP for force exit."
                )

                time.sleep(
                    TRADE_MONITOR_SECONDS
                )

                continue

            execute_exit(
                trade,
                "FORCE_EXIT",
                ltp
            )

            return True


        # -------------------------------------------------
        # MARKET CLOSE SAFETY
        # -------------------------------------------------

        if market_close_reached():

            ltp = get_option_ltp(
                trade["exchange"],
                trade["symbol"]
            )

            if ltp is not None:

                execute_exit(
                    trade,
                    "MARKET_CLOSE",
                    ltp
                )

            return True


        # -------------------------------------------------
        # LTP
        # -------------------------------------------------

        ltp = get_option_ltp(
            trade["exchange"],
            trade["symbol"]
        )

        if ltp is None:

            print(
                "Waiting for LTP..."
            )

            time.sleep(
                TRADE_MONITOR_SECONDS
            )

            continue


        entry = float(
            trade["entry_price"]
        )

        stop_loss = float(
            trade["stop_loss"]
        )

        target = float(
            trade["target"]
        )


        # -------------------------------------------------
        # P&L
        # -------------------------------------------------

        pnl = (
            ltp
            -
            entry
        ) * int(
            trade["quantity"]
        )


        print(
            f"[{now_ist().strftime('%H:%M:%S')}] "
            f"{trade['symbol']} "
            f"LTP={ltp:.2f} "
            f"Entry={entry:.2f} "
            f"SL={stop_loss:.2f} "
            f"Target={target:.2f} "
            f"P&L={pnl:.2f}"
        )


        # -------------------------------------------------
        # STOP LOSS
        #
        # IMPORTANT:
        #
        # We BUY the CE/PE premium.
        #
        # Therefore:
        #
        # LTP <= SL
        #
        # means loss.
        # -------------------------------------------------

        if ltp <= stop_loss:

            print()
            print(
                "STOP LOSS HIT."
            )

            execute_exit(
                trade,
                "STOP_LOSS",
                ltp
            )

            return True


        # -------------------------------------------------
        # TARGET
        #
        # We BUY the premium.
        #
        # Therefore:
        #
        # LTP >= TARGET
        #
        # means target hit.
        # -------------------------------------------------

        if ltp >= target:

            print()
            print(
                "TARGET HIT."
            )

            execute_exit(
                trade,
                "TARGET",
                ltp
            )

            return True


        time.sleep(
            TRADE_MONITOR_SECONDS
        )


# =========================================================
# FIND SIGNAL
# =========================================================

def check_market(
    market_name,
    config,
    instruments
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
    # INDEX CANDLES
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


    if len(df) < 3:

        print(
            "Not enough completed candles."
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
    # INDEX SETUP
    # -----------------------------------------------------

    if market_name == "NIFTY":

        setups = find_nifty_setups(
            df
        )

    else:

        setups = find_sensex_setups(
            df
        )


    if not setups:

        print(
            market_name,
            "SETUP: NONE"
        )

        return None


    # -----------------------------------------------------
    # ONLY CONSIDER SETUPS THAT HAVE ALREADY COMPLETED
    # -----------------------------------------------------

    completed_setups = []

    latest_time = pd.Timestamp(
        latest["date"]
    )


    for setup in setups:

        pullback_time = pd.Timestamp(
            setup[
                "pullback"
            ]["date"]
        )

        if pullback_time <= latest_time:

            completed_setups.append(
                setup
            )


    if not completed_setups:

        print(
            "No completed setup."
        )

        return None


    setup = completed_setups[-1]


    direction = setup[
        "direction"
    ]

    breakout = setup[
        "breakout"
    ]

    pullback = setup[
        "pullback"
    ]


    print(
        "Direction:",
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


    print(
        "Spot:",
        spot
    )


    # -----------------------------------------------------
    # OPTION
    # -----------------------------------------------------

    option = find_option(
        instruments,
        config,
        direction,
        spot
    )

    if option is None:

        print(
            "Option not found."
        )

        return None


    option_symbol = option[
        "tradingsymbol"
    ]

    option_token = option[
        "instrument_token"
    ]


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
        "Lot:",
        option_lot
    )

    print(
        "Quantity:",
        quantity
    )


    # -----------------------------------------------------
    # PREMIUM CANDLES
    # -----------------------------------------------------

    premium_raw = (
        fetch_today_candles(
            option_token
        )
    )

    if not premium_raw:

        print(
            "No premium data."
        )

        return None


    premium_df = calculate_indicators(
        premium_raw
    )

    premium_df = remove_current_candle(
        premium_df
    )


    if len(premium_df) < 3:

        print(
            "Not enough premium candles."
        )

        return None


    # -----------------------------------------------------
    # PREMIUM SETUP
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # ONLY COMPLETED PREMIUM SETUPS
    # -----------------------------------------------------

    completed_premium = []


    latest_premium = pd.Timestamp(
        premium_df.iloc[-1]["date"]
    )


    for premium_setup in premium_setups:

        confirmation_time = pd.Timestamp(
            premium_setup[
                "confirmation"
            ]["date"]
        )

        if confirmation_time <= latest_premium:

            completed_premium.append(
                premium_setup
            )


    if not completed_premium:

        print(
            "Premium setup not completed."
        )

        return None


    premium_setup = (
        completed_premium[-1]
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

    premium_confirmation = (
        premium_setup[
            "confirmation"
        ]
    )


    # -----------------------------------------------------
    # CONFIRMATION MUST BE LATEST CLOSED CANDLE
    # -----------------------------------------------------

    confirmation_time = pd.Timestamp(
        premium_confirmation[
            "date"
        ]
    )


    if confirmation_time != latest_premium:

        print(
            "Premium setup is old."
        )

        return None


    # -----------------------------------------------------
    # STRENGTH
    # -----------------------------------------------------

    strength = get_setup_strength(

        breakout,

        pullback,

        premium_breakout,

        premium_pullback,

        premium_confirmation
    )


    rr = recommended_rr(
        strength
    )


    if rr is None:

        print(
            "Setup strength too weak."
        )

        return None


    # -----------------------------------------------------
    # ENTRY
    #
    # Signal entry = confirmation close.
    #
    # For LIVE mode the actual fill price is obtained
    # AFTER Zerodha executes the BUY.
    # -----------------------------------------------------

    expected_entry = float(
        premium_confirmation[
            "close"
        ]
    )


    # -----------------------------------------------------
    # RISK
    # -----------------------------------------------------

    risk = calculate_dynamic_risk(

        expected_entry,

        premium_pullback,

        premium_confirmation,

        direction,

        strength
    )


    if risk is None:

        print(
            "Risk rejected."
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

        "rr":
            risk[
                "rr"
            ],

        "setup_strength":
            strength,

        "breakout":
            str(
                breakout[
                    "date"
                ]
            ),

        "pullback":
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

        "premium_confirmation":
            str(
                premium_confirmation[
                    "date"
                ]
            ),
    }


# =========================================================
# MAIN STRATEGY SCAN
# =========================================================

def find_best_signal():

    # -----------------------------------------------------
    # DAILY LIMIT
    # -----------------------------------------------------

    count = get_today_trade_count()

    if count >= MAX_TRADES_PER_DAY:

        print()
        print(
            "MAX DAILY TRADES REACHED:",
            count
        )

        return None


    # -----------------------------------------------------
    # LOAD INSTRUMENTS
    # -----------------------------------------------------

    print()
    print(
        "Loading NFO instruments..."
    )

    nfo = get_instruments(
        "NFO"
    )

    print(
        "NFO:",
        len(nfo)
    )


    print()
    print(
        "Loading BFO instruments..."
    )

    bfo = get_instruments(
        "BFO"
    )

    print(
        "BFO:",
        len(bfo)
    )


    # -----------------------------------------------------
    # NIFTY
    # -----------------------------------------------------

    nifty_signal = check_market(

        "NIFTY",

        MARKETS[
            "NIFTY"
        ],

        nfo
    )


    # -----------------------------------------------------
    # SENSEX
    # -----------------------------------------------------

    sensex_signal = check_market(

        "SENSEX",

        MARKETS[
            "SENSEX"
        ],

        bfo
    )


    signals = []


    if nifty_signal is not None:

        signals.append(
            nifty_signal
        )


    if sensex_signal is not None:

        signals.append(
            sensex_signal
        )


    if not signals:

        return None


    # -----------------------------------------------------
    # CURRENT IMPLEMENTATION:
    # first valid signal wins.
    # -----------------------------------------------------

    selected = signals[0]


    print()
    print(
        "=========================================="
    )

    print(
        "SELECTED SIGNAL"
    )

    print(
        "=========================================="
    )

    print(
        selected["market"],
        selected["direction"],
        selected["option_symbol"]
    )

    print(
        "Entry:",
        round(
            selected["entry"],
            2
        )
    )

    print(
        "SL:",
        round(
            selected["stop_loss"],
            2
        )
    )

    print(
        "Target:",
        round(
            selected["target"],
            2
        )
    )

    print(
        "R:R:",
        "1:",
        selected["rr"]
    )

    print(
        "Strength:",
        selected["setup_strength"]
    )


    return selected


# =========================================================
# WAIT FOR MARKET
# =========================================================

def wait_for_market_open():

    print()
    print(
        "=========================================="
    )

    print(
        "NIFTY + SENSEX OPTIONS BOT"
    )

    print(
        "=========================================="
    )

    print(
        "Mode:",
        "LIVE"
        if LIVE_MODE
        else "PAPER"
    )

    print(
        "Market open:",
        MARKET_OPEN
    )

    print(
        "Entry start:",
        ENTRY_START
    )

    print(
        "Entry end:",
        ENTRY_END
    )

    print(
        "Force exit:",
        FORCE_EXIT_TIME
    )

    print(
        "Market close:",
        MARKET_CLOSE
    )

    print(
        "Trade monitor:",
        TRADE_MONITOR_SECONDS,
        "seconds"
    )

    print(
        "Strategy scan:",
        STRATEGY_CHECK_SECONDS,
        "seconds"
    )


    while True:

        now = now_ist()

        if now.time() >= MARKET_CLOSE:

            print(
                "Market already closed."
            )

            return False


        if now.time() >= MARKET_OPEN:

            print(
                "Market is open."
            )

            return True


        print(
            "Waiting for market open...",
            now
        )


        time.sleep(
            WAIT_BEFORE_MARKET_SECONDS
        )


# =========================================================
# BOT
# =========================================================

def run_bot():

    if not test_connection():

        return


    # -----------------------------------------------------
    # WAIT FOR MARKET
    # -----------------------------------------------------

    if not wait_for_market_open():

        return


    # -----------------------------------------------------
    # CONTINUOUS DAY LOOP
    # -----------------------------------------------------

    while True:

        now = now_ist()


        # =================================================
        # MARKET CLOSE
        # =================================================

        if now.time() >= MARKET_CLOSE:

            print()
            print(
                "=========================================="
            )

            print(
                "MARKET CLOSED"
            )

            print(
                "BOT STOPPED"
            )

            print(
                "=========================================="
            )

            return


        # =================================================
        # ACTIVE TRADE
        #
        # THIS HAS PRIORITY OVER NEW SIGNALS.
        #
        # If a trade exists, the bot monitors it.
        # It does NOT search for another trade.
        # =================================================

        active_trade = get_active_trade()


        if active_trade is not None:

            monitor_active_trade()

            # ------------------------------------------------
            # After trade closes, continue normal bot loop.
            # ------------------------------------------------

            continue


        # =================================================
        # FORCE EXIT WINDOW
        #
        # After 15:15 we do not open new trades.
        # =================================================

        if force_exit_time_reached():

            print()
            print(
                "Force-exit time reached."
            )

            print(
                "No new trades allowed."
            )

            time.sleep(
                30
            )

            continue


        # =================================================
        # ENTRY WINDOW
        # =================================================

        if not entry_window_open():

            print()
            print(
                "Outside entry window."
            )

            print(
                "No new trade."
            )

            time.sleep(
                STRATEGY_CHECK_SECONDS
            )

            continue


        # =================================================
        # EXISTING ZERODHA POSITION
        #
        # This is an additional safety check.
        # =================================================

        if has_open_position():

            print()
            print(
                "ZERODHA POSITION DETECTED."
            )

            print(
                "Bot will NOT open another trade."
            )

            time.sleep(
                STRATEGY_CHECK_SECONDS
            )

            continue


        # =================================================
        # STRATEGY
        # =================================================

        print()
        print(
            "=========================================="
        )

        print(
            "NEW STRATEGY SCAN"
        )

        print(
            "TIME:",
            now_ist()
        )

        print(
            "=========================================="
        )


        try:

            signal = find_best_signal()

        except Exception as exc:

            print()
            print(
                "STRATEGY ERROR:"
            )

            print(
                type(exc).__name__,
                str(exc)
            )

            signal = None


        # =================================================
        # NO SIGNAL
        # =================================================

        if signal is None:

            print()
            print(
                "NO VALID TRADE."
            )

            print(
                "Next scan in 5 minutes."
            )

            time.sleep(
                STRATEGY_CHECK_SECONDS
            )

            continue


        # =================================================
        # BUY
        # =================================================

        trade = execute_buy(
            signal
        )


        if trade is None:

            print(
                "Trade was not opened."
            )

            time.sleep(
                STRATEGY_CHECK_SECONDS
            )

            continue


        # =================================================
        # IMMEDIATELY START TRACKING
        #
        # This is the key part.
        #
        # The bot does NOT wait 5 minutes after entering.
        #
        # It starts checking every 5 seconds.
        # =================================================

        monitor_active_trade()


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
            "BOT STOPPED MANUALLY"
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
            "FATAL BOT ERROR"
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

