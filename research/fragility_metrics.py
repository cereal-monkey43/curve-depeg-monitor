import pandas as pd
from pathlib import Path


HISTORY_PATH = Path("outputs/validated_history.csv")


def load_history():

    df = pd.read_csv(HISTORY_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def add_forward_risk(df):

    df = df.copy()

    df["future_max_7d"] = (
        df["deviation_bps"]
        .rolling(window=7, min_periods=1)
        .max()
        .shift(-7)
    )

    df["future_fragile_7d"] = df["future_max_7d"] >= 30
    df["spread_widening_3d"] = df["deviation_bps"].diff(3)

    return df


def conditional_fragility(df):

    calm = df[df["deviation_bps"] < 15]
    widening = df[
        (df["deviation_bps"] < 30) &
        (df["spread_widening_3d"] > 8)
    ]

    stressed = df[df["deviation_bps"] >= 30]

    return {
        "observations": int(len(df)),
        "calm_days": int(len(calm)),
        "widening_but_not_stressed_days": int(len(widening)),
        "stress_days": int(len(stressed)),
        "p_fragile_7d_given_calm": float(calm["future_fragile_7d"].mean()),
        "p_fragile_7d_given_widening": float(widening["future_fragile_7d"].mean()) if len(widening) else 0.0,
        "avg_future_max_after_calm": float(calm["future_max_7d"].mean()),
        "avg_future_max_after_widening": float(widening["future_max_7d"].mean()) if len(widening) else 0.0
    }


if __name__ == "__main__":

    df = load_history()
    df = add_forward_risk(df)

    stats = conditional_fragility(df)

    print("\nconditional fragility metrics\n")

    for k, v in stats.items():
        print(f"{k}: {v}")

    pd.DataFrame([stats]).to_csv(
        "outputs/conditional_fragility.csv",
        index=False
    )

    print("\nsaved: outputs/conditional_fragility.csv")