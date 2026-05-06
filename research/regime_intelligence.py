import pandas as pd
from pathlib import Path


OUT = Path("outputs")


def load(name):
    return pd.read_csv(OUT / name)


def bucket_execution(discount_bps):

    if discount_bps >= 5000:
        return "execution_breakdown"

    if discount_bps >= 1000:
        return "fragile_size"

    if discount_bps >= 250:
        return "thin_marginal_depth"

    return "normal_execution"


def bucket_skew(rr_25d, convexity_premium):

    if rr_25d <= -5 or convexity_premium >= 12:
        return "downside_convexity_bid"

    if rr_25d <= -2 or convexity_premium >= 8:
        return "mild_tail_hedging"

    if rr_25d >= 5:
        return "upside_call_bid"

    return "neutral_surface"


def bucket_inventory(imbalance_ratio):

    if imbalance_ratio >= 0.65:
        return "eth_inventory_stressed"

    if imbalance_ratio >= 0.50:
        return "eth_inventory_thinning"

    if imbalance_ratio <= 0.30:
        return "steth_heavy_pool"

    return "balanced_inventory"


def main():

    signal = load("latest_signal.csv").iloc[0]
    slippage = load("slippage_curve.csv")
    put_surface = load("front_expiry_put_surface.csv")
    history = load("validated_history.csv")

    ten_k = slippage[slippage["trade_size_steth"] == 10000].iloc[0]
    fifty_k = slippage[slippage["trade_size_steth"] == 50000].iloc[0]

    deep_puts = put_surface.nsmallest(5, "log_moneyness")
    atm_puts = put_surface.iloc[
        put_surface["log_moneyness"].abs().argsort()[:5]
    ]

    convexity_premium = deep_puts["iv_pct"].mean() - atm_puts["iv_pct"].mean()

    regime = {
        "inventory_regime": bucket_inventory(signal["imbalance_ratio"]),
        "execution_regime_10k": bucket_execution(ten_k["discount_bps"]),
        "execution_regime_50k": bucket_execution(fifty_k["discount_bps"]),
        "skew_regime": bucket_skew(signal["risk_reversal_25d"], convexity_premium),
        "spot_stress_days_365d": int(history["stress_event"].sum()),
        "early_warning_days_365d": int(history["early_warning_window"].sum()),
        "max_spot_deviation_bps_365d": float(history["deviation_bps"].max()),
        "current_spot_deviation_bps": float(history["deviation_bps"].iloc[-1]),
        "current_pool_eth_share": float(signal["imbalance_ratio"]),
        "risk_reversal_25d": float(signal["risk_reversal_25d"]),
        "downside_convexity_premium": float(convexity_premium),
        "discount_bps_10k": float(ten_k["discount_bps"]),
        "discount_bps_50k": float(fifty_k["discount_bps"])
    }

    interpretation = []

    if regime["inventory_regime"] == "steth_heavy_pool":
        interpretation.append(
            "Curve inventory is currently stETH-heavy rather than ETH-stressed, so realized exit pressure is not elevated."
        )

    if regime["execution_regime_10k"] != "normal_execution":
        interpretation.append(
            "Despite non-stressed inventory, modeled execution quality deteriorates with trade size, showing that TVL overstates usable liquidity."
        )

    if regime["skew_regime"] in ["downside_convexity_bid", "mild_tail_hedging"]:
        interpretation.append(
            "The options surface is pricing downside convexity more aggressively than spot pool state alone would suggest."
        )

    if regime["current_spot_deviation_bps"] < 30 and regime["downside_convexity_premium"] > 8:
        interpretation.append(
            "Current cross-market state is a divergence regime: spot spread is calm while downside convexity remains bid."
        )

    if not interpretation:
        interpretation.append(
            "Current state is broadly normal across inventory, execution, spot spread, and options surface."
        )

    regime["interpretation"] = " ".join(interpretation)

    pd.DataFrame([regime]).to_csv("outputs/regime_intelligence.csv", index=False)

    print("\nregime intelligence\n")
    for k, v in regime.items():
        print(f"{k}: {v}")

    print("\nsaved: outputs/regime_intelligence.csv")


if __name__ == "__main__":
    main()