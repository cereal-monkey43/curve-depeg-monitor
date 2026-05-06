import requests
import pandas as pd


CURVE_URL = "https://api.curve.fi/api/getPools/ethereum/main"
TARGET_POOL = "steCRV"


def normalize_balance(raw_balance):
    return float(raw_balance) / 1e18


def fetch_steth_pool():

    r = requests.get(CURVE_URL, timeout=10)

    if r.status_code != 200:
        raise RuntimeError(f"curve api failed: {r.status_code}")

    data = r.json()["data"]["poolData"]

    for pool in data:

        if pool.get("symbol") != TARGET_POOL:
            continue

        token_map = {}

        for coin in pool["coins"]:
            token_map[coin["symbol"]] = normalize_balance(coin["poolBalance"])

        eth_balance = token_map.get("ETH", 0.0)
        steth_balance = token_map.get("stETH", 0.0)

        total = eth_balance + steth_balance

        imbalance_ratio = eth_balance / total

        return pd.DataFrame([{
            "pool": TARGET_POOL,
            "eth_balance": eth_balance,
            "steth_balance": steth_balance,
            "imbalance_ratio": imbalance_ratio,
            "tvl_usd": float(pool.get("usdTotal", 0))
        }])

    raise RuntimeError("stETH Curve pool not found")


if __name__ == "__main__":

    df = fetch_steth_pool()

    print("\nlive stETH pool imbalance\n")
    print(df)