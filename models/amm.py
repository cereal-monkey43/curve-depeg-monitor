import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd

from data.curve_graph import fetch_steth_pool


A = 100
N_COINS = 2


def get_D(xp, amp=A):

    S = sum(xp)

    if S == 0:
        return 0

    D = S
    Ann = amp * N_COINS

    for _ in range(255):
        D_P = D

        for x in xp:
            D_P = D_P * D / (x * N_COINS)

        D_prev = D

        D = (
            (Ann * S + D_P * N_COINS) * D
            /
            ((Ann - 1) * D + (N_COINS + 1) * D_P)
        )

        if abs(D - D_prev) <= 1e-9:
            break

    return D


def get_y(i, j, x, xp, amp=A):

    D = get_D(xp, amp)
    Ann = amp * N_COINS

    c = D
    S_ = 0

    for idx in range(N_COINS):

        if idx == i:
            _x = x
        elif idx == j:
            continue
        else:
            _x = xp[idx]

        S_ += _x
        c = c * D / (_x * N_COINS)

    c = c * D / (Ann * N_COINS)
    b = S_ + D / Ann

    y = D

    for _ in range(255):
        y_prev = y
        y = (y * y + c) / (2 * y + b - D)

        if abs(y - y_prev) <= 1e-9:
            break

    return y


def steth_to_eth_out(eth_balance, steth_balance, trade_size_steth):

    # coin order: [stETH, ETH]
    xp = [steth_balance, eth_balance]

    x_new = xp[0] + trade_size_steth
    y_new = get_y(0, 1, x_new, xp)

    eth_out = xp[1] - y_new

    return eth_out


def executable_discount_bps(eth_balance, steth_balance, trade_size_steth):

    eth_out = steth_to_eth_out(
        eth_balance,
        steth_balance,
        trade_size_steth
    )

    executable_price = eth_out / trade_size_steth

    # quoted peg is 1 ETH per stETH; discount is executable degradation from peg
    discount_bps = (1 - executable_price) * 10000

    return {
        "trade_size_steth": trade_size_steth,
        "eth_out": eth_out,
        "executable_price": executable_price,
        "discount_bps": discount_bps
    }


def slippage_curve(eth_balance, steth_balance):

    sizes = [100, 500, 1000, 5000, 10000, 25000, 50000]

    return [
        executable_discount_bps(
            eth_balance,
            steth_balance,
            size
        )
        for size in sizes
    ]


if __name__ == "__main__":

    pool = fetch_steth_pool().iloc[0]

    rows = slippage_curve(
        float(pool["eth_balance"]),
        float(pool["steth_balance"])
    )

    df = pd.DataFrame(rows)

    print("\nCurve-style executable stETH -> ETH slippage curve\n")
    print(df)

    df.to_csv("outputs/slippage_curve.csv", index=False)

    print("\nsaved: outputs/slippage_curve.csv")