import requests
import pandas as pd


COINGECKO_URL = "https://api.coingecko.com/api/v3/coins"


def fetch_price_history(coin_id, days=365):

    r = requests.get(
        f"{COINGECKO_URL}/{coin_id}/market_chart",
        params={
            "vs_currency": "usd",
            "days": days,
            "interval": "daily"
        },
        timeout=15
    )

    if r.status_code != 200:
        raise RuntimeError(f"coingecko failed: {r.status_code}")

    rows = []

    for ts, px in r.json()["prices"]:
        rows.append({
            "timestamp": pd.to_datetime(ts, unit="ms"),
            "price": px
        })

    return pd.DataFrame(rows)


def build_steth_eth_spread():

    eth = fetch_price_history("ethereum")
    steth = fetch_price_history("staked-ether")

    merged = eth.merge(
        steth,
        on="timestamp",
        suffixes=("_eth", "_steth")
    )

    merged["steth_eth_ratio"] = merged["price_steth"] / merged["price_eth"]

    # positive bps = stETH trading below ETH
    merged["deviation_bps"] = (1 - merged["steth_eth_ratio"]) * 10000

    return merged


if __name__ == "__main__":

    df = build_steth_eth_spread()

    print("\nstETH/ETH historical spread\n")
    print(df.tail())

    print("\nworst dislocations\n")
    print(
        df.nlargest(
            10,
            "deviation_bps"
        )[
            [
                "timestamp",
                "steth_eth_ratio",
                "deviation_bps"
            ]
        ]
    )

    df.to_csv("outputs/steth_eth_history.csv", index=False)

    print("\nsaved: outputs/steth_eth_history.csv")