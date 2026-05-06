import requests
import pandas as pd


BASE_URL = "https://www.deribit.com/api/v2/public"


def fetch_eth_options():

    r = requests.get(
        f"{BASE_URL}/get_book_summary_by_currency",
        params={
            "currency": "ETH",
            "kind": "option"
        },
        timeout=15
    )

    if r.status_code != 200:
        raise RuntimeError(f"deribit request failed: {r.status_code}")

    rows = []

    for item in r.json()["result"]:

        instrument = item["instrument_name"]

        if "-C" not in instrument and "-P" not in instrument:
            continue

        rows.append({
            "instrument": instrument,
            "bid_iv": item.get("bid_iv"),
            "ask_iv": item.get("ask_iv"),
            "mark_iv": item.get("mark_iv"),
            "open_interest": item.get("open_interest", 0),
            "volume": item.get("volume", 0),
            "underlying_price": item.get("underlying_price")
        })

    return pd.DataFrame(rows)


def fetch_option_book():

    rows = []

    df = fetch_eth_options()

    for _, item in df.iterrows():

        parts = item["instrument"].split("-")

        if len(parts) != 4:
            continue

        _, expiry, strike, option_type = parts

        if pd.isna(item["mark_iv"]) or pd.isna(item["underlying_price"]):
            continue

        rows.append({
            "instrument": item["instrument"],
            "expiry": expiry,
            "strike": float(strike),
            "option_type": option_type,
            "mark_iv": float(item["mark_iv"]) / 100,
            "spot": float(item["underlying_price"]),
            "open_interest": float(item["open_interest"] or 0),
            "volume": float(item["volume"] or 0)
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":

    df = fetch_option_book()

    print("\nlive ETH option book\n")

    print(df.head())

    print(f"\ncontracts: {len(df)}")