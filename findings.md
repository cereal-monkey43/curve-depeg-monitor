# Findings

## Core result

This project studies stETH/ETH liquidity fragility as a cross-market state transition problem, not as a simple depeg prediction problem.

The main finding is that visible liquidity can remain calm while executable liquidity and options-implied convexity show much more fragile conditions.

In other words:

> TVL and spot spread are lagging measures of liquidity quality.

The useful state variables are:

1. Curve inventory balance
2. executable AMM slippage by trade size
3. ETH options skew and downside convexity
4. realized stETH/ETH spread behavior

## Current live state

Latest live run:

- Curve pool: steCRV
- ETH share of pool: ~28.7%
- 25d ETH risk reversal: ~8.3 vol points
- downside convexity premium: ~11.4 vol points
- 10k stETH modeled execution discount: ~618 bps
- 50k stETH modeled execution discount: ~7603 bps
- current regime: spot calm, execution fragile, convexity bid

The key observation is cross-market disagreement. Spot spread and inventory do not currently show extreme realized stress, but executable depth deteriorates sharply with size and the options surface still prices meaningful downside convexity.

## Historical spread regime

Using 365 days of CoinGecko stETH/ETH data:

- observations: 365
- stress days above 30 bps discount: 14
- early-warning widening days: 58
- maximum observed discount: ~63.4 bps
- average stress-period discount: ~40.4 bps

This shows that stETH stress is clustered rather than continuous. The market spends most days in calm regimes, but transition windows matter because spread widening can happen quickly.

## Conditional fragility

Using realized spread behavior:

- calm days: 291
- widening-but-not-stressed days: 58
- stress days: 14
- probability of entering fragile conditions within 7 days after calm state: ~4.1%
- probability after widening-but-not-stressed state: ~12.1%

This is the more useful result. The project is not trying to forecast every depeg. It is identifying when calm-looking regimes become more likely to transition into fragile states.

## Execution curvature

The AMM layer shows that liquidity quality deteriorates nonlinearly with trade size. This matters because large notional pool balances can hide weak marginal depth.

A pool can appear healthy by TVL while the execution path for one-sided exits becomes extremely poor. This is why TVL alone is a weak proxy for usable liquidity.

## Options surface interpretation

The options layer measures whether the derivatives market is pricing downside convexity.

A rich downside put wing while spot spread remains calm suggests that derivatives markets may be pricing tail liquidity risk before it is obvious in spot dislocation.

This does not prove prediction yet because historical Deribit skew snapshots are not included. The live architecture is built to collect that going forward.

## Market structure implication

The project’s core implication is:

> stETH liquidity fragility is a convexity problem, not just a spot price problem.

When inventory becomes asymmetric, execution quality can deteriorate superlinearly. When options markets begin paying for downside convexity, the system may already be entering a more fragile liquidity state even if spot spread and TVL still look normal.

## Limitations

This is not a production trading model.

Current limitations:

- historical stETH/ETH spread data is daily, not intraday
- Deribit options skew is live-only unless snapshots are collected over time
- the AMM execution model is a StableSwap-style approximation, not a byte-for-byte Curve contract replica
- the project does not reconstruct actual historical Curve swaps
- no claim is made about exact predictive accuracy, lead time, or false positive rate

The correct interpretation is that this repo builds a factual research framework for measuring liquidity fragility across market layers.

## Future work

Next extensions:

- collect live Deribit skew snapshots over time
- collect intraday Curve pool inventory snapshots
- estimate lead-lag relationships between skew, inventory, and spread
- build transition probabilities across full cross-market regimes
- reconstruct swap-level stETH exits from on-chain events
- compare Curve depth with Uniswap and CEX liquidity