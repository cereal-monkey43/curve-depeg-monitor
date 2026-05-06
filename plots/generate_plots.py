import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


HISTORY_PATH = "outputs/validated_history.csv"

PLOT_DIR = Path("plots")
PLOT_DIR.mkdir(exist_ok=True)


def plot_steth_spread(df):

    plt.figure(figsize=(12, 5))

    plt.plot(
        df["timestamp"],
        df["deviation_bps"],
        linewidth=1.7
    )

    plt.axhline(
        30,
        linestyle="--",
        linewidth=1
    )

    stress = df[df["stress_event"]]

    plt.scatter(
        stress["timestamp"],
        stress["deviation_bps"],
        s=30
    )

    plt.title("stETH/ETH Historical Dislocation")
    plt.xlabel("Date")
    plt.ylabel("Discount to ETH (bps)")

    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / "steth_eth_dislocation.png",
        dpi=220
    )


def plot_warning_windows(df):

    plt.figure(figsize=(12, 5))

    plt.plot(
        df["timestamp"],
        df["spread_change_3d"],
        linewidth=1.7
    )

    plt.axhline(
        8,
        linestyle="--",
        linewidth=1
    )

    warnings = df[df["early_warning_window"]]

    plt.scatter(
        warnings["timestamp"],
        warnings["spread_change_3d"],
        s=30
    )

    plt.title("3-Day Spread Widening Early Warning Windows")
    plt.xlabel("Date")
    plt.ylabel("3-Day Spread Change (bps)")

    plt.tight_layout()

    plt.savefig(
        PLOT_DIR / "early_warning_windows.png",
        dpi=220
    )


def save_summary(df):

    summary = {
        "observations": len(df),
        "stress_days": int(df["stress_event"].sum()),
        "warning_days": int(df["early_warning_window"].sum()),
        "max_dislocation_bps": float(df["deviation_bps"].max()),
        "latest_dislocation_bps": float(df["deviation_bps"].iloc[-1])
    }

    pd.DataFrame([summary]).to_csv(
        "outputs/plot_summary.csv",
        index=False
    )


if __name__ == "__main__":

    df = pd.read_csv(HISTORY_PATH)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    plot_steth_spread(df)
    plot_warning_windows(df)

    save_summary(df)

    print("\nsaved plots:")
    print("plots/steth_eth_dislocation.png")
    print("plots/early_warning_windows.png")

    print("\nsaved: outputs/plot_summary.csv")