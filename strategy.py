
# # strategy.py


# import numpy as np
# import pandas as pd


# # =========================================================
# # CONFIGURATION
# # =========================================================

# PULLBACK_BUFFER = 2.0

# SL_BUFFER = 0.50

# MAX_PULLBACK_CANDLES = 4

# MAX_SETUP_GAP_MINUTES = 20

# R_MULTIPLES = (2.0, 3.0, 4.0)


# # =========================================================
# # INDICATORS
# # =========================================================

# def calculate_indicators(candles):
#     """
#     Convert Zerodha candle data into a DataFrame and calculate:

#         EMA20
#         VWAP
#         range
#         body
#         body_ratio

#     This function is intentionally kept simple and robust.
#     """

#     if candles is None:
#         return pd.DataFrame()

#     if isinstance(candles, pd.DataFrame):
#         df = candles.copy()
#     else:
#         try:
#             df = pd.DataFrame(candles).copy()
#         except Exception:
#             return pd.DataFrame()

#     if df.empty:
#         return pd.DataFrame()

#     if "date" not in df.columns:
#         return pd.DataFrame()

#     # -----------------------------------------------------
#     # DATE
#     # -----------------------------------------------------

#     df["date"] = pd.to_datetime(
#         df["date"],
#         errors="coerce"
#     )

#     df = (
#         df
#         .dropna(subset=["date"])
#         .sort_values("date")
#         .reset_index(drop=True)
#     )

#     # -----------------------------------------------------
#     # REQUIRED OHLC
#     # -----------------------------------------------------

#     required = [
#         "open",
#         "high",
#         "low",
#         "close",
#     ]

#     for column in required:

#         if column not in df.columns:
#             return pd.DataFrame()

#         df[column] = pd.to_numeric(
#             df[column],
#             errors="coerce"
#         )

#     # -----------------------------------------------------
#     # VOLUME
#     # -----------------------------------------------------

#     if "volume" not in df.columns:
#         df["volume"] = 0

#     df["volume"] = pd.to_numeric(
#         df["volume"],
#         errors="coerce"
#     ).fillna(0)

#     df = (
#         df
#         .dropna(subset=required)
#         .reset_index(drop=True)
#     )

#     if df.empty:
#         return df

#     # =====================================================
#     # EMA20
#     # =====================================================

#     df["ema20"] = (
#         df["close"]
#         .ewm(
#             span=20,
#             adjust=False,
#             min_periods=1
#         )
#         .mean()
#     )

#     # =====================================================
#     # VWAP
#     # =====================================================

#     df["typical_price"] = (
#         df["high"]
#         + df["low"]
#         + df["close"]
#     ) / 3.0

#     df["date_only"] = df["date"].dt.date

#     df["pv"] = (
#         df["typical_price"]
#         * df["volume"]
#     )

#     df["cumulative_pv"] = (
#         df
#         .groupby("date_only")["pv"]
#         .cumsum()
#     )

#     df["cumulative_volume"] = (
#         df
#         .groupby("date_only")["volume"]
#         .cumsum()
#     )

#     df["vwap"] = (
#         df["cumulative_pv"]
#         /
#         df["cumulative_volume"].replace(
#             0,
#             np.nan
#         )
#     )

#     # -----------------------------------------------------
#     # If volume is zero/unavailable,
#     # use typical price as fallback.
#     # -----------------------------------------------------

#     df["vwap"] = (
#         df["vwap"]
#         .replace(
#             [np.inf, -np.inf],
#             np.nan
#         )
#         .fillna(
#             df["typical_price"]
#         )
#     )

#     # =====================================================
#     # CANDLE STRUCTURE
#     # =====================================================

#     df["range"] = (
#         df["high"]
#         -
#         df["low"]
#     ).clip(lower=0)

#     df["body"] = (
#         df["close"]
#         -
#         df["open"]
#     ).abs()

#     df["body_ratio"] = (
#         df["body"]
#         /
#         df["range"].replace(
#             0,
#             np.nan
#         )
#     ).fillna(0)

#     return df


# # =========================================================
# # CANDLE HELPERS
# # =========================================================

# def candle_is_green(candle):

#     return (
#         float(candle["close"])
#         >
#         float(candle["open"])
#     )


# def candle_is_red(candle):

#     return (
#         float(candle["close"])
#         <
#         float(candle["open"])
#     )


# def above_ema_vwap(candle):

#     close = float(candle["close"])

#     ema = float(candle["ema20"])

#     vwap = float(candle["vwap"])

#     return (
#         close > ema
#         and
#         close > vwap
#     )


# def below_ema_vwap(candle):

#     close = float(candle["close"])

#     ema = float(candle["ema20"])

#     vwap = float(candle["vwap"])

#     return (
#         close < ema
#         and
#         close < vwap
#     )


# # =========================================================
# # INDEX BREAKOUT
# # =========================================================

# def bullish_breakout(candle):

#     return (
#         candle_is_green(candle)
#         and
#         above_ema_vwap(candle)
#     )


# def bearish_breakout(candle):

#     return (
#         candle_is_red(candle)
#         and
#         below_ema_vwap(candle)
#     )


# def bullish_nifty_breakout(candle):

#     return bullish_breakout(candle)


# def bearish_nifty_breakout(candle):

#     return bearish_breakout(candle)


# def bullish_sensex_breakout(candle):

#     return bullish_breakout(candle)


# def bearish_sensex_breakout(candle):

#     return bearish_breakout(candle)


# # =========================================================
# # BULLISH PULLBACK
# # =========================================================

# def bullish_pullback(
#     candle,
#     pullback_buffer=PULLBACK_BUFFER
# ):

#     ema = float(candle["ema20"])

#     vwap = float(candle["vwap"])

#     low = float(candle["low"])

#     close = float(candle["close"])

#     zone_low = min(
#         ema,
#         vwap
#     )

#     zone_high = max(
#         ema,
#         vwap
#     )

#     touched_zone = (
#         low
#         <=
#         zone_high + pullback_buffer
#     )

#     if not touched_zone:
#         return False

#     return (
#         close >= zone_low
#     )


# # =========================================================
# # BEARISH PULLBACK
# # =========================================================

# def bearish_pullback(
#     candle,
#     pullback_buffer=PULLBACK_BUFFER
# ):

#     ema = float(candle["ema20"])

#     vwap = float(candle["vwap"])

#     high = float(candle["high"])

#     close = float(candle["close"])

#     zone_low = min(
#         ema,
#         vwap
#     )

#     zone_high = max(
#         ema,
#         vwap
#     )

#     touched_zone = (
#         high
#         >=
#         zone_low - pullback_buffer
#     )

#     if not touched_zone:
#         return False

#     return (
#         close <= zone_high
#     )


# # =========================================================
# # PREMIUM BREAKOUT
# # =========================================================

# def premium_bullish_breakout(candle):

#     return (
#         candle_is_green(candle)
#         and
#         above_ema_vwap(candle)
#     )


# # =========================================================
# # PREMIUM PULLBACK
# # =========================================================

# def premium_bullish_pullback(
#     candle,
#     pullback_buffer=PULLBACK_BUFFER
# ):

#     ema = float(candle["ema20"])

#     vwap = float(candle["vwap"])

#     low = float(candle["low"])

#     close = float(candle["close"])

#     zone_low = min(
#         ema,
#         vwap
#     )

#     zone_high = max(
#         ema,
#         vwap
#     )

#     touched_zone = (
#         low
#         <=
#         zone_high + pullback_buffer
#     )

#     if not touched_zone:
#         return False

#     return (
#         close >= zone_low
#     )


# # =========================================================
# # PREMIUM CONFIRMATION
# # =========================================================

# def bullish_confirmation(
#     previous_candle,
#     candle
# ):

#     return (
#         candle_is_green(candle)
#         and
#         above_ema_vwap(candle)
#     )


# # =========================================================
# # INDEX SETUPS
# # =========================================================

# def _find_index_setups(
#     df,
#     breakout_bullish,
#     breakout_bearish
# ):

#     setups = []

#     if df is None or df.empty:
#         return setups

#     if len(df) < 3:
#         return setups

#     i = 0

#     while i < len(df) - 1:

#         breakout = df.iloc[i]

#         # -------------------------------------------------
#         # BULLISH
#         # -------------------------------------------------

#         if breakout_bullish(breakout):

#             direction = "CE"

#             pullback_fn = bullish_pullback

#         # -------------------------------------------------
#         # BEARISH
#         # -------------------------------------------------

#         elif breakout_bearish(breakout):

#             direction = "PE"

#             pullback_fn = bearish_pullback

#         else:

#             i += 1
#             continue

#         found = None

#         found_index = None

#         # -------------------------------------------------
#         # FIND PULLBACK
#         # -------------------------------------------------

#         for offset in range(
#             1,
#             MAX_PULLBACK_CANDLES + 1
#         ):

#             j = i + offset

#             if j >= len(df):
#                 break

#             pullback = df.iloc[j]

#             if pullback_fn(
#                 pullback,
#                 PULLBACK_BUFFER
#             ):

#                 found = {
#                     "direction": direction,
#                     "breakout": breakout,
#                     "pullback": pullback,
#                 }

#                 found_index = j

#                 break

#         # -------------------------------------------------
#         # VALID SETUP
#         # -------------------------------------------------

#         if found is not None:

#             setups.append(found)

#             i = found_index + 1

#         else:

#             i += 1

#     return setups


# # =========================================================
# # NIFTY
# # =========================================================

# def find_nifty_setups(day_df):

#     return _find_index_setups(
#         day_df,
#         bullish_nifty_breakout,
#         bearish_nifty_breakout
#     )


# def find_nifty_setup(df):

#     setups = find_nifty_setups(df)

#     if not setups:
#         return None

#     return setups[-1]


# # =========================================================
# # SENSEX
# # =========================================================

# def find_sensex_setups(day_df):

#     return _find_index_setups(
#         day_df,
#         bullish_sensex_breakout,
#         bearish_sensex_breakout
#     )


# def find_sensex_setup(df):

#     setups = find_sensex_setups(df)

#     if not setups:
#         return None

#     return setups[-1]


# # =========================================================
# # GENERIC INDEX
# # =========================================================

# def find_index_setup(
#     df,
#     index_name="NIFTY"
# ):

#     if str(index_name).upper() == "SENSEX":

#         return find_sensex_setup(df)

#     return find_nifty_setup(df)


# # =========================================================
# # PREMIUM SETUPS
# # =========================================================

# def _find_premium_setups(
#     premium_df,
#     index_breakout_time,
#     index_pullback_time
# ):

#     setups = []

#     if premium_df is None:
#         return setups

#     if premium_df.empty:
#         return setups

#     index_breakout_time = pd.Timestamp(
#         index_breakout_time
#     )

#     index_pullback_time = pd.Timestamp(
#         index_pullback_time
#     )

#     candidates = premium_df[
#         premium_df["date"]
#         >=
#         index_breakout_time
#     ].copy()

#     candidates = (
#         candidates
#         .sort_values("date")
#         .reset_index(drop=True)
#     )

#     if candidates.empty:
#         return setups

#     i = 0

#     while i < len(candidates) - 1:

#         premium_breakout = candidates.iloc[i]

#         if not premium_bullish_breakout(
#             premium_breakout
#         ):

#             i += 1
#             continue

#         breakout_time = pd.Timestamp(
#             premium_breakout["date"]
#         )

#         gap = (
#             breakout_time
#             -
#             index_breakout_time
#         ).total_seconds() / 60.0

#         if (
#             gap < 0
#             or
#             gap > MAX_SETUP_GAP_MINUTES
#         ):

#             i += 1
#             continue

#         found = None

#         found_index = None

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
#                 PULLBACK_BUFFER
#             ):

#                 continue

#             pullback_time = pd.Timestamp(
#                 premium_pullback["date"]
#             )

#             if (
#                 pullback_time
#                 <
#                 index_pullback_time
#             ):

#                 continue

#             gap2 = (
#                 pullback_time
#                 -
#                 index_pullback_time
#             ).total_seconds() / 60.0

#             if (
#                 gap2 < 0
#                 or
#                 gap2 > MAX_SETUP_GAP_MINUTES
#             ):

#                 continue

#             confirmation = candidates.iloc[
#                 j + 1
#             ]

#             if not bullish_confirmation(
#                 premium_pullback,
#                 confirmation
#             ):

#                 continue

#             found = {
#                 "breakout": premium_breakout,
#                 "pullback": premium_pullback,
#                 "confirmation": confirmation,
#             }

#             found_index = j + 1

#             break

#         if found is not None:

#             setups.append(found)

#             i = found_index + 1

#         else:

#             i += 1

#     return setups


# # =========================================================
# # NIFTY PREMIUM
# # =========================================================

# def find_premium_setups(
#     premium_df,
#     nifty_breakout_time,
#     nifty_pullback_time
# ):

#     return _find_premium_setups(
#         premium_df,
#         nifty_breakout_time,
#         nifty_pullback_time
#     )


# def find_premium_setup(
#     premium_df,
#     index_breakout_time,
#     index_pullback_time
# ):

#     setups = find_premium_setups(
#         premium_df,
#         index_breakout_time,
#         index_pullback_time
#     )

#     if not setups:
#         return None

#     return setups[-1]


# # =========================================================
# # SENSEX PREMIUM
# # =========================================================

# def find_sensex_premium_setups(
#     premium_df,
#     sensex_breakout_time,
#     sensex_pullback_time
# ):

#     return _find_premium_setups(
#         premium_df,
#         sensex_breakout_time,
#         sensex_pullback_time
#     )


# def find_sensex_premium_setup(
#     premium_df,
#     sensex_breakout_time,
#     sensex_pullback_time
# ):

#     setups = find_sensex_premium_setups(
#         premium_df,
#         sensex_breakout_time,
#         sensex_pullback_time
#     )

#     if not setups:
#         return None

#     return setups[-1]


# # =========================================================
# # SETUP STRENGTH
# # =========================================================

# def get_setup_strength(
#     index_breakout,
#     index_pullback,
#     premium_breakout=None,
#     premium_pullback=None,
#     premium_confirmation=None
# ):

#     score = 0

#     # Index breakout
#     if (
#         above_ema_vwap(index_breakout)
#         or
#         below_ema_vwap(index_breakout)
#     ):
#         score += 2

#     # Breakout candle body
#     if float(index_breakout["body"]) > 0:
#         score += 1

#     # Premium breakout
#     if premium_breakout is not None:

#         if above_ema_vwap(
#             premium_breakout
#         ):
#             score += 2

#     # Premium pullback
#     if premium_pullback is not None:

#         ema = float(
#             premium_pullback["ema20"]
#         )

#         vwap = float(
#             premium_pullback["vwap"]
#         )

#         low = float(
#             premium_pullback["low"]
#         )

#         if (
#             low
#             <=
#             max(ema, vwap)
#             +
#             PULLBACK_BUFFER
#         ):
#             score += 1

#     # Confirmation
#     if premium_confirmation is not None:

#         if above_ema_vwap(
#             premium_confirmation
#         ):
#             score += 2

#     if score >= 7:
#         return "VERY_STRONG"

#     if score >= 5:
#         return "STRONG"

#     if score >= 3:
#         return "NORMAL"

#     return "WEAK"


# # =========================================================
# # R:R
# # =========================================================

# def recommended_rr(setup_strength):

#     return {
#         "WEAK": None,
#         "NORMAL": 2.0,
#         "STRONG": 3.0,
#         "VERY_STRONG": 4.0,
#     }.get(
#         setup_strength
#     )


# # =========================================================
# # DYNAMIC RISK
# # =========================================================

# def calculate_dynamic_risk(
#     entry_price,
#     pullback_candle,
#     confirmation_candle=None,
#     direction="CE",
#     setup_strength="NORMAL"
# ):

#     entry = float(entry_price)

#     pullback_low = float(
#         pullback_candle["low"]
#     )

#     stop_loss = (
#         pullback_low
#         -
#         SL_BUFFER
#     )

#     risk = (
#         entry
#         -
#         stop_loss
#     )

#     if risk <= 0:
#         return None

#     max_risk = max(
#         15.0,
#         entry * 0.30
#     )

#     if risk > max_risk:
#         return None

#     rr = recommended_rr(
#         setup_strength
#     )

#     if rr is None:
#         return None

#     target = (
#         entry
#         +
#         risk * rr
#     )

#     return {
#         "entry": entry,
#         "stop_loss": stop_loss,
#         "risk_points": risk,
#         "rr": rr,
#         "target": target,
#         "setup_strength": setup_strength,
#         "direction": direction,
#     }


# # =========================================================
# # ALL TARGETS
# # =========================================================

# def calculate_all_targets(
#     entry_price,
#     pullback_candle,
#     confirmation_candle=None
# ):

#     entry = float(entry_price)

#     stop_loss = (
#         float(
#             pullback_candle["low"]
#         )
#         -
#         SL_BUFFER
#     )

#     risk = (
#         entry
#         -
#         stop_loss
#     )

#     if risk <= 0:
#         return None

#     return {
#         "entry": entry,
#         "stop_loss": stop_loss,
#         "risk_points": risk,
#         "target_1_2": entry + risk * 2.0,
#         "target_1_3": entry + risk * 3.0,
#         "target_1_4": entry + risk * 4.0,
#     }


# # =========================================================
# # COMPATIBILITY ALIASES
# # =========================================================

# bullish_nifty = bullish_nifty_breakout

# bearish_nifty = bearish_nifty_breakout

# bullish_sensex = bullish_sensex_breakout

# bearish_sensex = bearish_sensex_breakout

import numpy as np
import pandas as pd

PULLBACK_BUFFER = 2.0
SL_BUFFER = 0.50
MAX_PULLBACK_CANDLES = 4
MAX_SETUP_GAP_MINUTES = 20
R_MULTIPLES = (2.0, 3.0, 4.0)


# =========================================================
# INDICATORS
# =========================================================

def calculate_indicators(candles):
    if candles is None:
        return pd.DataFrame()

    try:
        df = candles.copy() if isinstance(candles, pd.DataFrame) \
            else pd.DataFrame(candles).copy()
    except Exception:
        return pd.DataFrame()

    if df.empty or "date" not in df.columns:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date")
    df = df.reset_index(drop=True)

    required = ["open", "high", "low", "close"]

    for column in required:
        if column not in df.columns:
            return pd.DataFrame()

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    if "volume" not in df.columns:
        df["volume"] = 0

    df["volume"] = pd.to_numeric(
        df["volume"],
        errors="coerce"
    ).fillna(0)

    df = df.dropna(subset=required).reset_index(drop=True)

    if df.empty:
        return df

    # EMA20
    df["ema20"] = df["close"].ewm(
        span=20,
        adjust=False,
        min_periods=1
    ).mean()

    # VWAP
    df["typical_price"] = (
        df["high"] + df["low"] + df["close"]
    ) / 3.0

    df["date_only"] = df["date"].dt.date
    df["pv"] = df["typical_price"] * df["volume"]

    df["cumulative_pv"] = (
        df.groupby("date_only")["pv"].cumsum()
    )

    df["cumulative_volume"] = (
        df.groupby("date_only")["volume"].cumsum()
    )

    df["vwap"] = (
        df["cumulative_pv"] /
        df["cumulative_volume"].replace(0, np.nan)
    )

    df["vwap"] = (
        df["vwap"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(df["typical_price"])
    )

    # Candle structure
    df["range"] = (
        df["high"] - df["low"]
    ).clip(lower=0)

    df["body"] = (
        df["close"] - df["open"]
    ).abs()

    df["body_ratio"] = (
        df["body"] /
        df["range"].replace(0, np.nan)
    ).fillna(0)

    return df


# =========================================================
# CANDLE HELPERS
# =========================================================

def candle_is_green(candle):
    return float(candle["close"]) > float(candle["open"])


def candle_is_red(candle):
    return float(candle["close"]) < float(candle["open"])


def above_ema_vwap(candle):
    close = float(candle["close"])
    ema = float(candle["ema20"])
    vwap = float(candle["vwap"])

    return close > ema and close > vwap


def below_ema_vwap(candle):
    close = float(candle["close"])
    ema = float(candle["ema20"])
    vwap = float(candle["vwap"])

    return close < ema and close < vwap


# =========================================================
# INDEX BREAKOUT
# =========================================================

def bullish_breakout(candle):
    return (
        candle_is_green(candle)
        and above_ema_vwap(candle)
    )


def bearish_breakout(candle):
    return (
        candle_is_red(candle)
        and below_ema_vwap(candle)
    )


def bullish_nifty_breakout(candle):
    return bullish_breakout(candle)


def bearish_nifty_breakout(candle):
    return bearish_breakout(candle)


def bullish_sensex_breakout(candle):
    return bullish_breakout(candle)


def bearish_sensex_breakout(candle):
    return bearish_breakout(candle)


# =========================================================
# BULLISH PULLBACK
# =========================================================

def bullish_pullback(
    candle,
    pullback_buffer=PULLBACK_BUFFER
):
    ema = float(candle["ema20"])
    vwap = float(candle["vwap"])
    low = float(candle["low"])
    close = float(candle["close"])

    zone_low = min(ema, vwap)
    zone_high = max(ema, vwap)

    touched_zone = (
        low <= zone_high + pullback_buffer
    )

    if not touched_zone:
        return False

    return close >= zone_low


# =========================================================
# BEARISH PULLBACK
# =========================================================

def bearish_pullback(
    candle,
    pullback_buffer=PULLBACK_BUFFER
):
    ema = float(candle["ema20"])
    vwap = float(candle["vwap"])
    high = float(candle["high"])
    close = float(candle["close"])

    zone_low = min(ema, vwap)
    zone_high = max(ema, vwap)

    touched_zone = (
        high >= zone_low - pullback_buffer
    )

    if not touched_zone:
        return False

    return close <= zone_high


# =========================================================
# PREMIUM
# =========================================================

def premium_bullish_breakout(candle):
    return (
        candle_is_green(candle)
        and above_ema_vwap(candle)
    )


def premium_bullish_pullback(
    candle,
    pullback_buffer=PULLBACK_BUFFER
):
    ema = float(candle["ema20"])
    vwap = float(candle["vwap"])
    low = float(candle["low"])
    close = float(candle["close"])

    zone_low = min(ema, vwap)
    zone_high = max(ema, vwap)

    touched_zone = (
        low <= zone_high + pullback_buffer
    )

    if not touched_zone:
        return False

    return close >= zone_low


def bullish_confirmation(
    previous_candle,
    candle
):
    return (
        candle_is_green(candle)
        and above_ema_vwap(candle)
    )


# =========================================================
# INDEX SETUPS
# =========================================================

def _find_index_setups(
    df,
    breakout_bullish,
    breakout_bearish
):
    setups = []

    if df is None or df.empty or len(df) < 3:
        return setups

    i = 0

    while i < len(df) - 1:
        breakout = df.iloc[i]

        if breakout_bullish(breakout):
            direction = "CE"
            pullback_fn = bullish_pullback

        elif breakout_bearish(breakout):
            direction = "PE"
            pullback_fn = bearish_pullback

        else:
            i += 1
            continue

        found = None
        found_index = None

        for offset in range(
            1,
            MAX_PULLBACK_CANDLES + 1
        ):
            j = i + offset

            if j >= len(df):
                break

            pullback = df.iloc[j]

            if pullback_fn(
                pullback,
                PULLBACK_BUFFER
            ):
                found = {
                    "direction": direction,
                    "breakout": breakout,
                    "pullback": pullback,
                }

                found_index = j
                break

        if found is not None:
            setups.append(found)
            i = found_index + 1
        else:
            i += 1

    return setups


# =========================================================
# NIFTY
# =========================================================

def find_nifty_setups(day_df):
    return _find_index_setups(
        day_df,
        bullish_nifty_breakout,
        bearish_nifty_breakout
    )


def find_nifty_setup(df):
    setups = find_nifty_setups(df)

    return setups[-1] if setups else None


# =========================================================
# SENSEX
# =========================================================

def find_sensex_setups(day_df):
    return _find_index_setups(
        day_df,
        bullish_sensex_breakout,
        bearish_sensex_breakout
    )


def find_sensex_setup(df):
    setups = find_sensex_setups(df)

    return setups[-1] if setups else None


# =========================================================
# GENERIC INDEX
# =========================================================

def find_index_setup(
    df,
    index_name="NIFTY"
):
    if str(index_name).upper() == "SENSEX":
        return find_sensex_setup(df)

    return find_nifty_setup(df)


# =========================================================
# PREMIUM SETUPS
# =========================================================

def _find_premium_setups(
    premium_df,
    index_breakout_time,
    index_pullback_time
):
    setups = []

    if premium_df is None or premium_df.empty:
        return setups

    index_breakout_time = pd.Timestamp(
        index_breakout_time
    )

    index_pullback_time = pd.Timestamp(
        index_pullback_time
    )

    candidates = premium_df[
        premium_df["date"] >= index_breakout_time
    ].copy()

    candidates = (
        candidates
        .sort_values("date")
        .reset_index(drop=True)
    )

    if candidates.empty:
        return setups

    i = 0

    while i < len(candidates) - 1:
        premium_breakout = candidates.iloc[i]

        if not premium_bullish_breakout(
            premium_breakout
        ):
            i += 1
            continue

        breakout_time = pd.Timestamp(
            premium_breakout["date"]
        )

        gap = (
            breakout_time -
            index_breakout_time
        ).total_seconds() / 60.0

        if gap < 0 or gap > MAX_SETUP_GAP_MINUTES:
            i += 1
            continue

        found = None
        found_index = None

        for offset in range(
            1,
            MAX_PULLBACK_CANDLES + 1
        ):
            j = i + offset

            if j >= len(candidates) - 1:
                break

            premium_pullback = candidates.iloc[j]

            if not premium_bullish_pullback(
                premium_pullback,
                PULLBACK_BUFFER
            ):
                continue

            pullback_time = pd.Timestamp(
                premium_pullback["date"]
            )

            if pullback_time < index_pullback_time:
                continue

            gap2 = (
                pullback_time -
                index_pullback_time
            ).total_seconds() / 60.0

            if gap2 < 0 or gap2 > MAX_SETUP_GAP_MINUTES:
                continue

            confirmation = candidates.iloc[j + 1]

            if not bullish_confirmation(
                premium_pullback,
                confirmation
            ):
                continue

            found = {
                "breakout": premium_breakout,
                "pullback": premium_pullback,
                "confirmation": confirmation,
            }

            found_index = j + 1
            break

        if found is not None:
            setups.append(found)
            i = found_index + 1
        else:
            i += 1

    return setups


def find_premium_setups(
    premium_df,
    nifty_breakout_time,
    nifty_pullback_time
):
    return _find_premium_setups(
        premium_df,
        nifty_breakout_time,
        nifty_pullback_time
    )


def find_premium_setup(
    premium_df,
    index_breakout_time,
    index_pullback_time
):
    setups = find_premium_setups(
        premium_df,
        index_breakout_time,
        index_pullback_time
    )

    return setups[-1] if setups else None


# =========================================================
# SENSEX PREMIUM
# =========================================================

def find_sensex_premium_setups(
    premium_df,
    sensex_breakout_time,
    sensex_pullback_time
):
    return _find_premium_setups(
        premium_df,
        sensex_breakout_time,
        sensex_pullback_time
    )


def find_sensex_premium_setup(
    premium_df,
    sensex_breakout_time,
    sensex_pullback_time
):
    setups = find_sensex_premium_setups(
        premium_df,
        sensex_breakout_time,
        sensex_pullback_time
    )

    return setups[-1] if setups else None


# =========================================================
# SETUP STRENGTH
# =========================================================

def get_setup_strength(
    index_breakout,
    index_pullback,
    premium_breakout=None,
    premium_pullback=None,
    premium_confirmation=None
):
    score = 0

    if (
        above_ema_vwap(index_breakout)
        or below_ema_vwap(index_breakout)
    ):
        score += 2

    if float(index_breakout["body"]) > 0:
        score += 1

    if premium_breakout is not None:
        if above_ema_vwap(premium_breakout):
            score += 2

    if premium_pullback is not None:
        ema = float(premium_pullback["ema20"])
        vwap = float(premium_pullback["vwap"])
        low = float(premium_pullback["low"])

        if low <= max(ema, vwap) + PULLBACK_BUFFER:
            score += 1

    if premium_confirmation is not None:
        if above_ema_vwap(premium_confirmation):
            score += 2

    if score >= 7:
        return "VERY_STRONG"

    if score >= 5:
        return "STRONG"

    if score >= 3:
        return "NORMAL"

    return "WEAK"


# =========================================================
# R:R
# =========================================================

def recommended_rr(setup_strength):
    return {
        "WEAK": None,
        "NORMAL": 2.0,
        "STRONG": 3.0,
        "VERY_STRONG": 4.0,
    }.get(setup_strength)


# =========================================================
# DYNAMIC RISK
# =========================================================

def calculate_dynamic_risk(
    entry_price,
    pullback_candle,
    confirmation_candle=None,
    direction="CE",
    setup_strength="NORMAL"
):
    entry = float(entry_price)

    pullback_low = float(
        pullback_candle["low"]
    )

    stop_loss = pullback_low - SL_BUFFER
    risk = entry - stop_loss

    if risk <= 0:
        return None

    max_risk = max(
        15.0,
        entry * 0.30
    )

    if risk > max_risk:
        return None

    rr = recommended_rr(setup_strength)

    if rr is None:
        return None

    target = entry + risk * rr

    return {
        "entry": entry,
        "stop_loss": stop_loss,
        "risk_points": risk,
        "rr": rr,
        "target": target,
        "setup_strength": setup_strength,
        "direction": direction,
    }


# =========================================================
# ALL TARGETS
# =========================================================

def calculate_all_targets(
    entry_price,
    pullback_candle,
    confirmation_candle=None
):
    entry = float(entry_price)

    stop_loss = (
        float(pullback_candle["low"])
        - SL_BUFFER
    )

    risk = entry - stop_loss

    if risk <= 0:
        return None

    return {
        "entry": entry,
        "stop_loss": stop_loss,
        "risk_points": risk,
        "target_1_2": entry + risk * 2.0,
        "target_1_3": entry + risk * 3.0,
        "target_1_4": entry + risk * 4.0,
    }


# =========================================================
# COMPATIBILITY
# =========================================================

bullish_nifty = bullish_nifty_breakout
bearish_nifty = bearish_nifty_breakout
bullish_sensex = bullish_sensex_breakout
bearish_sensex = bearish_sensex_breakout