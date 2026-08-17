import logging
import time
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo

from live_trader import main


IST = ZoneInfo("Asia/Kolkata")

MARKET_START = dt_time(9, 15)
MARKET_END = dt_time(15, 30)

INTERVAL_SECONDS = 5 * 60


def now_ist():
    return datetime.now(IST)


def market_hours():
    now = now_ist()

    if now.weekday() >= 5:
        return False

    current_time = now.time()

    return MARKET_START <= current_time <= MARKET_END


def seconds_until_next_5_minute():
    now = now_ist()

    seconds_into_minute = now.second
    minutes = now.minute

    next_minute = ((minutes // 5) + 1) * 5

    if next_minute >= 60:
        next_hour = now.replace(
            minute=0,
            second=0,
            microsecond=0
        )

        next_hour = next_hour.replace(
            hour=(now.hour + 1) % 24
        )

        delay = (
            next_hour - now
        ).total_seconds()

    else:
        next_run = now.replace(
            minute=next_minute,
            second=0,
            microsecond=0
        )

        delay = (
            next_run - now
        ).total_seconds()

    return max(1, int(delay))


def run():

    logging.info("==========================================")
    logging.info("GITHUB TRADING RUNNER STARTED")
    logging.info("==========================================")

    logging.info(
        "Current IST time: %s",
        now_ist().strftime("%Y-%m-%d %H:%M:%S")
    )

    if not market_hours():

        logging.info(
            "Outside market hours. Runner will exit."
        )

        return

    while True:

        now = now_ist()

        if not market_hours():

            logging.info(
                "Market hours finished at %s IST.",
                now.strftime("%H:%M:%S")
            )

            break

        logging.info("==========================================")
        logging.info(
            "TRADING CYCLE: %s IST",
            now.strftime("%Y-%m-%d %H:%M:%S")
        )
        logging.info("==========================================")

        try:

            main()

            logging.info(
                "Trading cycle completed."
            )

        except Exception:

            logging.exception(
                "Trading cycle failed."
            )

        now = now_ist()

        if now.time() >= MARKET_END:

            logging.info(
                "Reached market closing time."
            )

            break

        delay = seconds_until_next_5_minute()

        logging.info(
            "Next trading cycle in approximately %s seconds.",
            delay
        )

        time.sleep(delay)

    logging.info("==========================================")
    logging.info("GITHUB TRADING RUNNER STOPPED")
    logging.info("==========================================")


if __name__ == "__main__":

    try:

        run()

    except KeyboardInterrupt:

        logging.info(
            "Trading runner stopped manually."
        )