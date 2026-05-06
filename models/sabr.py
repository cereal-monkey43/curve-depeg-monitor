import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import numpy as np

from data.deribit import fetch_option_book


def normalized_strike_distance(strike, spot):

    return np.log(strike / spot)


def surface_snapshot():

    df = fetch_option_book()

    front_expiry = sorted(df["expiry"].unique())[0]

    front = df[df["expiry"] == front_expiry].copy()

    front["log_moneyness"] = front.apply(
        lambda r: normalized_strike_distance(
            r["strike"],
            r["spot"]
        ),
        axis=1
    )

    front["iv_pct"] = front["mark_iv"] * 100

    calls = front[front["option_type"] == "C"][
        [
            "strike",
            "log_moneyness",
            "iv_pct",
            "open_interest",
            "volume"
        ]
    ]

    puts = front[front["option_type"] == "P"][
        [
            "strike",
            "log_moneyness",
            "iv_pct",
            "open_interest",
            "volume"
        ]
    ]

    return {
        "expiry": front_expiry,
        "spot": float(front["spot"].median()),
        "calls": calls.sort_values("strike"),
        "puts": puts.sort_values("strike")
    }


def downside_convexity_score(puts):

    wing = puts.nsmallest(5, "log_moneyness")

    atm = puts.iloc[
        (puts["log_moneyness"].abs()).argsort()[:5]
    ]

    wing_iv = wing["iv_pct"].mean()
    atm_iv = atm["iv_pct"].mean()

    return wing_iv - atm_iv


if __name__ == "__main__":

    snap = surface_snapshot()

    puts = snap["puts"]

    convexity_bid = downside_convexity_score(puts)

    print("\nfront expiry volatility surface\n")

    print(f"expiry: {snap['expiry']}")
    print(f"spot: {snap['spot']:.2f}")

    print("\ndownside convexity premium\n")

    print(f"{convexity_bid:.2f} vol points")

    print("\nlowest strike puts\n")

    print(
        puts[
            [
                "strike",
                "log_moneyness",
                "iv_pct",
                "open_interest"
            ]
        ].head(10)
    )

    puts.to_csv(
        "outputs/front_expiry_put_surface.csv",
        index=False
    )

    print("\nsaved: outputs/front_expiry_put_surface.csv")