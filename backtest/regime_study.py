import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd

from data.coingecko import build_steth_eth_spread


def label_stress_windows(df, stress_bps=30):

    df = df.copy()

    df["stress_event"] = df["deviation_bps"] >= stress_bps
    df["spread_change_3d"] = df["deviation_bps"].diff(3)

    df["early_warning_window"] = (
        (df["spread_change_3d"] > 8) &
        (df["deviation_bps"] < stress_bps)
    )

    return df


def summarize_history(df):

    stress = df[df["stress_event"]]
    warnings = df[df["early_warning_window"]]

    worst = df.loc[df["deviation_bps"].idxmax()]

    return {
        "observations": len(df),
        "stress_days_above_30bps": int(len(stress)),
        "early_warning_days": int(len(warnings)),
        "max_deviation_bps": float(worst["deviation_bps"]),
        "worst_day": str(worst["timestamp"].date()),
        "avg_stress_deviation_bps": float(stress["deviation_bps"].mean()) if len(stress) else 0.0
    }


if __name__ == "__main__":

    df = build_steth_eth_spread()
    df = label_stress_windows(df)

    summary = summarize_history(df)

    print("\nstETH/ETH historical regime study\n")

    for k, v in summary.items():
        print(f"{k}: {v}")

    df.to_csv("outputs/validated_history.csv", index=False)

    print("\nsaved: outputs/validated_history.csv")