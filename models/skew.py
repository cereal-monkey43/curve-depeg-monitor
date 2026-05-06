import requests
import pandas as pd
import numpy as np

from datetime import datetime, timezone
from scipy.stats import norm


DERIBIT_URL = "https://www.deribit.com/api/v2/public/get_book_summary_by_currency"


def fetch_eth_surface():
    r = requests.get(
        DERIBIT_URL,
        params={"currency": "ETH", "kind": "option"},
        timeout=10
    )

    if r.status_code != 200:
        raise RuntimeError(f"deribit failed: {r.status_code}")

    rows = []

    for x in r.json()["result"]:
        inst = x["instrument_name"]

        if "-C" not in inst and "-P" not in inst:
            continue

        iv = x.get("mark_iv")
        spot = x.get("underlying_price")

        if iv is None or spot is None:
            continue

        rows.append({
            "instrument": inst,
            "mark_iv": float(iv) / 100,
            "spot": float(spot),
            "open_interest": float(x.get("open_interest") or 0),
            "volume": float(x.get("volume") or 0)
        })

    return pd.DataFrame(rows)


def parse_expiry(expiry):
    return datetime.strptime(expiry, "%d%b%y").replace(tzinfo=timezone.utc)


def year_fraction(expiry):
    now = datetime.now(timezone.utc)
    expiry_dt = parse_expiry(expiry)

    tau = (expiry_dt - now).total_seconds() / (365 * 24 * 3600)

    return max(tau, 1 / 365)


def parse_surface(df):
    split = df["instrument"].str.split("-", expand=True)

    df = df.copy()
    df["expiry"] = split[1]
    df["strike"] = split[2].astype(float)
    df["option_type"] = split[3]
    df["tau"] = df["expiry"].apply(year_fraction)

    return df


def bs_delta(row):
    spot = row["spot"]
    strike = row["strike"]
    vol = row["mark_iv"]
    tau = row["tau"]

    d1 = (np.log(spot / strike) + 0.5 * vol ** 2 * tau) / (vol * np.sqrt(tau))

    if row["option_type"] == "C":
        return norm.cdf(d1)

    return norm.cdf(d1) - 1


def closest_delta_leg(df, option_type, target_abs_delta):
    leg = df[df["option_type"] == option_type].copy()

    if leg.empty:
        raise RuntimeError(f"missing {option_type} leg")

    leg["abs_delta_error"] = np.abs(np.abs(leg["delta"]) - target_abs_delta)

    # open interest tie-break keeps us away from dead strikes
    leg = leg.sort_values(["abs_delta_error", "open_interest"], ascending=[True, False])

    return leg.iloc[0]


def front_expiry_skew():
    df = parse_surface(fetch_eth_surface())

    df["delta"] = df.apply(bs_delta, axis=1)

    expiries = sorted(df["expiry"].unique(), key=parse_expiry)
    front_expiry = expiries[0]

    front = df[df["expiry"] == front_expiry].copy()

    put_25d = closest_delta_leg(front, "P", 0.25)
    call_25d = closest_delta_leg(front, "C", 0.25)

    put_iv = put_25d["mark_iv"] * 100
    call_iv = call_25d["mark_iv"] * 100

    # negative = downside convexity bid. This is the actual stress variable.
    rr_25d = call_iv - put_iv

    return {
        "front_expiry": front_expiry,
        "spot": float(front["spot"].median()),
        "put_strike": float(put_25d["strike"]),
        "call_strike": float(call_25d["strike"]),
        "put_delta": float(put_25d["delta"]),
        "call_delta": float(call_25d["delta"]),
        "put_iv": float(put_iv),
        "call_iv": float(call_iv),
        "risk_reversal_25d": float(rr_25d)
    }


if __name__ == "__main__":
    skew = front_expiry_skew()

    print("\nfront expiry delta-based 25d skew\n")

    for k, v in skew.items():
        print(f"{k}: {v}")