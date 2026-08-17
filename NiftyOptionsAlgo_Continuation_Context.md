# NiftyOptionsAlgo — Continuation Context

## Purpose
Handoff document for continuing the NiftyOptionsAlgo project in a new AI chat. Read this first. Do not restart completed setup unless a test proves it is broken.

## User workflow preference
The user is doing this setup for the first time. Give exact beginner-friendly commands, one step at a time when asked for “next”. Explain expected output briefly. Do not repeat completed installation. Practical/direct answers are preferred.

## Project
Folder:
`C:\Nagarro\MyCreations\NiftyOptionsAlgo`

Python trading project for NIFTY/SENSEX. It contains backtesting, strategy logic, signal testing, Zerodha/Kite connectivity, live trading, and Azure Functions automation. Current trading mode is PAPER.

## Important files
- `live_trader.py` — live trading implementation; verified entry point is `main()`.
- `strategy.py` — strategy logic.
- `backtest.py` — backtesting.
- `signal_test.py` — signal testing.
- `login.py` — login/token logic.
- `test_connection.py` — connection testing.
- `function_app.py` — Azure Functions timer entry point.
- `requirements.txt` — Python dependencies.
- `host.json` — Azure Functions host config.
- `local.settings.json` — local Azure settings.
- `nfo_instruments.csv` — NFO instruments.
- `.env` and `access_token.txt` may contain secrets; never expose or commit them.

## Python environments
There are `venv` and `azurevenv`. Azure work uses `azurevenv`.

Create command used:
`py -3.12 -m venv azurevenv`

Activate:
`.\azurevenv\Scripts\Activate.ps1`

Current Azure Python:
`Python 3.12.10`

Python 3.13 previously caused Azure Functions Core Tools `Destination is too short` error during Python version verification, so keep using Python 3.12 unless a new verified reason exists.

## Dependencies
`requirements.txt` currently contains:
```text
azure-functions
pandas
numpy
python-dotenv
kiteconnect
openpyxl
```

Verified successfully with:
`python -c "import azure.functions, pandas, numpy, dotenv, kiteconnect, openpyxl; print('ALL PACKAGES OK')"`

Output was `ALL PACKAGES OK`.

## Azure Functions Core Tools
Node:
`v24.14.1`

npm:
`11.11.0`

Installed:
`npm install -g azure-functions-core-tools@4 --unsafe-perm true`

Core Tools:
`4.13.0`

If `func` is not recognized in a new PowerShell session, add:
`$env:Path += ";C:\Users\nilanjanguha\AppData\Roaming\npm"`

Then:
`func --version`
should return `4.13.0`.

## Azurite
Installed:
`3.36.0`

Start local storage emulator:
`azurite`

Services:
- Blob: `http://127.0.0.1:10000`
- Queue: `http://127.0.0.1:10001`
- Table: `http://127.0.0.1:10002`

Keep Azurite running in Terminal 1 during local Azure Functions testing.

## host.json
Current:
```json
{
  "version": "2.0"
}
```

## local.settings.json
Current:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

This works when Azurite is running.

## Previous local storage error — already fixed
Before Azurite was running, `func start --python` failed with `Could not create BlobContainerClient for ScheduleMonitor`, `Unable to create client for AzureWebJobsStorage`, and connection refused at `127.0.0.1:10000`.

After starting Azurite, the Azure Function host successfully acquired its host lock. Do not reinstall/fix storage unless a new error appears.

## Local Azure Function startup
Use:
```powershell
cd C:\Nagarro\MyCreations\NiftyOptionsAlgo
.\azurevenv\Scripts\Activate.ps1
$env:Path += ";C:\Users\nilanjanguha\AppData\Roaming\npm"
func --version
func start --python
```

Expected discovery:
```text
Functions:

        trading_timer: timerTrigger
```

and:
`Host lock lease acquired...`

That means the local Function host is working.

## Correct live-trader entry point
This works:
```powershell
python -c "from live_trader import main; main()"
```

It produced the application banner:
```text
NIFTY + SENSEX LIVE TRADER
EMA20 + VWAP ONLY
MODE: PAPER
Market is closed.
```

A previous attempt to import `run_live_strategy` failed:
`ImportError: cannot import name 'run_live_strategy' from 'live_trader'`

Therefore the current correct function is `live_trader.main()`. Do not change it to `run_live_strategy()` unless the file is later modified and verified.

Also, do not type `run_live_strategy()` directly into PowerShell; use `python -c ...` for Python execution.

## Current function_app.py
The latest intended file is:
```python
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import azure.functions as func


app = func.FunctionApp()


@app.timer_trigger(
    schedule="0 */5 9-15 * * 1-5",
    arg_name="timer",
    run_on_startup=False,
    use_monitor=True
)
def trading_timer(timer: func.TimerRequest):

    logging.info("========================================")
    logging.info("TRADING TIMER STARTED")
    logging.info("========================================")

    # Current Indian Standard Time
    now = datetime.now(ZoneInfo("Asia/Kolkata"))

    logging.info(
        f"Current IST time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # ---------------------------------------------------------
    # Trading window: 09:15 AM to 03:30 PM IST
    # ---------------------------------------------------------

    current_time = now.hour * 60 + now.minute
    start_time = 9 * 60 + 15       # 09:15
    end_time = 15 * 60 + 30       # 15:30

    if current_time < start_time or current_time > end_time:
        logging.info(
            "Market trading logic skipped. "
            "Trading window is 09:15 to 15:30 IST."
        )
        return

    # ---------------------------------------------------------
    # Run live trading strategy
    # ---------------------------------------------------------

    try:

        from live_trader import main

        logging.info(
            "Calling live_trader.main()"
        )

        main()

        logging.info(
            "Trading cycle completed successfully"
        )

    except Exception as e:

        logging.exception(
            f"Trading cycle failed: {e}"
        )
```

## Timer behavior
The Azure timer expression is:
`0 */5 9-15 * * 1-5`

The Python time check enforces the actual desired trading window:
Monday–Friday, 09:15 IST through 15:30 IST.

Expected:
- 09:00–09:10: skip
- 09:15: run
- every 5 minutes through 15:30: run
- after 15:30: skip
- Saturday/Sunday: no timer trigger

The broad cron range is intentional; the Python check handles the exact 09:15 and 15:30 boundaries.

## Terminal arrangement
Terminal 1: Azurite (`azurite`) — keep running.

Terminal 2: Azure Functions (`func start --python`) — keep running.

Terminal 3: direct Python tests, e.g.:
`python -c "from live_trader import main; main()"`

Terminal 1 will show repeated Azurite `PUT`/`GET` lease messages. These are normal storage operations.

Terminal 2 should show the function discovery and host lock when healthy. When the timer actually invokes the function during the allowed window, it should show:
`TRADING TIMER STARTED`
`Current IST time: ...`
`Calling live_trader.main()`
then either:
`Trading cycle completed successfully`
or an error/traceback.

## TimerRequest test that failed — not a function problem
This was attempted:
`python -c "from function_app import trading_timer; import azure.functions as func; trading_timer(func.TimerRequest(partition_id='test', past_due=False, schedule_status=None))"`

It failed because `TimerRequest()` does not accept those constructor arguments. This does not indicate the Azure Function is broken. The real host successfully discovers `trading_timer`.

## Confirmed working
- Python 3.12.10 / `azurevenv`
- Required Python packages
- Azure Functions Core Tools 4.13.0
- Azurite 3.36.0
- `host.json`
- `local.settings.json`
- Azure Functions host startup
- `trading_timer` discovery
- local Azure storage lease
- `function_app.py` import
- `live_trader.py` import
- `live_trader.main()` direct execution
- PAPER mode trading application startup

## Not completed yet
The major remaining work is cloud deployment:
1. Create/configure Azure resources.
2. Deploy this Python Function App to Azure.
3. Configure Azure storage for the cloud Function App.
4. Move secrets/tokens from local `.env`/`access_token.txt` into secure Azure application settings or an appropriate secret store.
5. Configure and verify the cloud timer.
6. Confirm the deployed function runs automatically Monday–Friday, 09:15–15:30 IST without the PC being on.
7. Configure logs/monitoring/alerts.
8. Continue in PAPER mode until the entire automation is proven safe.

## Security
Do not expose or commit `.env`, `access_token.txt`, or any real API credentials/tokens. The actual values are intentionally not included in this handoff.

Do not put real credentials into GitHub.

For Azure, eventually use Function App Application Settings/environment variables or a proper secret mechanism.

## Trading safety
Current mode is PAPER. Keep it that way while testing Azure automation.

Do not switch to live orders simply because the Azure timer starts. First validate timer timing, IST boundaries, API/data access, order-generation behavior, duplicate execution prevention, errors/retries, logging, restarts, market holidays, and token/session handling.

## Exact next objective
Continue from the current working local state and deploy the Function App to Azure cloud.

Do NOT restart Python/Azure Functions/Azurite installation.

Before deployment, verify only if needed:
```powershell
python --version
func --version
python -c "import function_app; print('FUNCTION APP IMPORT OK')"
python -c "from live_trader import main; main()"
```

Then proceed to Azure cloud deployment step-by-step.

## New AI instruction
Treat this document as the project handoff. Understand the completed setup and continue from the `Not completed yet` section. If a new command fails, diagnose that exact failure rather than restarting the whole setup.
