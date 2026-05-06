import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
from datetime import datetime, timezone

from data.curve_graph import fetch_steth_pool
from models.skew import front_expiry_skew
from models.amm import executable_discount_bps


def score_imbalance(imbalance_ratio):

    if imbalance_ratio >= 0.65:
        return 3
    if imbalance_ratio >= 0.50:
        return 2
    if imbalance_ratio >= 0.35:
        return 1

    return 0


def score_skew(risk_reversal_25d):

    if risk_reversal_25d <= -8:
        return 3
    if risk_reversal_25d <= -5:
        return 2
    if risk_reversal_25d <= -2:
        return 1

    return 0


def score_execution(discount_bps_10k):

    # this is model-implied executable degradation, not an observed trade
    if discount_bps_10k >= 1000:
        return 3
    if discount_bps_10k >= 500:
        return 2
    if discount_bps_10k >= 150:
        return 1

    return 0


def classify_state(total_score):

    if total_score >= 6:
        return "elevated"
    if total_score >= 3:
        return "watch"

    return "normal"


def live_depeg_signal():

    pool = fetch_steth_pool().iloc[0]
    skew = front_expiry_skew()

    eth_balance = float(pool["eth_balance"])
    steth_balance = float(pool["steth_balance"])

    slippage_10k = executable_discount_bps(
        eth_balance,
        steth_balance,
        10000
    )

    imbalance_ratio = float(pool["imbalance_ratio"])
    rr_25d = float(skew["risk_reversal_25d"])
    discount_bps_10k = float(slippage_10k["discount_bps"])

    imbalance_score = score_imbalance(imbalance_ratio)
    skew_score = score_skew(rr_25d)
    execution_score = score_execution(discount_bps_10k)

    total_score = imbalance_score + skew_score + execution_score

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "pool": pool["pool"],
        "eth_balance": eth_balance,
        "steth_balance": steth_balance,
        "imbalance_ratio": imbalance_ratio,
        "front_expiry": skew["front_expiry"],
        "spot": float(skew["spot"]),
        "put_strike": float(skew["put_strike"]),
        "call_strike": float(skew["call_strike"]),
        "put_delta": float(skew["put_delta"]),
        "call_delta": float(skew["call_delta"]),
        "put_iv": float(skew["put_iv"]),
        "call_iv": float(skew["call_iv"]),
        "risk_reversal_25d": rr_25d,
        "discount_bps_10k_steth": discount_bps_10k,
        "executable_price_10k_steth": float(slippage_10k["executable_price"]),
        "imbalance_score": imbalance_score,
        "skew_score": skew_score,
        "execution_score": execution_score,
        "total_score": total_score,
        "state": classify_state(total_score)
    }


if __name__ == "__main__":

    signal = live_depeg_signal()

    print("\nlive stETH/ETH liquidity stress signal\n")

    for k, v in signal.items():
        print(f"{k}: {v}")

    pd.DataFrame([signal]).to_csv(
        "outputs/latest_signal.csv",
        index=False
    )

    print("\nsaved: outputs/latest_signal.csv")