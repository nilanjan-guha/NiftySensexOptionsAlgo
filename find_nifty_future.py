import csv
from datetime import date

today = date.today()

indices = ["NIFTY", "SENSEX"]
futures = {}

with open("instruments.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:

        name = row["name"]

        if (
            name in indices
            and row["instrument_type"] == "FUT"
            and row["expiry"]
            and row["expiry"] >= today.isoformat()
        ):
            futures.setdefault(name, []).append(row)


for name in indices:

    futures.setdefault(name, [])

    futures[name].sort(
        key=lambda x: x["expiry"]
    )

    print(f"\nNearest {name} Futures:")

    for future in futures[name][:3]:

        print(
            "Symbol:", future["tradingsymbol"],
            "| Expiry:", future["expiry"],
            "| Token:", future["instrument_token"],
            "| Exchange:", future["exchange"]
        )