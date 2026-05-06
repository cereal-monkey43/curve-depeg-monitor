# Cross-Market stETH Liquidity Fragility Engine

## Abstract

This project studies how liquidity stress forms in the stETH/ETH market across three layers:

1. Curve AMM inventory
2. executable slippage under size
3. ETH options skew and downside convexity

The core idea is that stETH/ETH fragility is not always visible in spot price first. Spot spread and TVL can look stable while executable liquidity deteriorates and derivatives markets price downside convexity.

The project is not a depeg prediction bot. It is a research system for measuring when liquidity quality starts becoming fragile before realized spot dislocation becomes obvious.

## Core question

Do derivatives markets and executable AMM depth reveal liquidity fragility before spot stETH/ETH dislocation becomes severe?

More specifically:

> Is visible liquidity overstating actual executable liquidity during cross-market stress regimes?

## Motivation

Most crypto liquidity monitoring focuses on spot price, peg deviation, or TVL.

Those are useful, but incomplete.

TVL measures how much liquidity exists in a pool. It does not measure how usable that liquidity is for a directional exit. A pool can have large notional liquidity while the marginal execution path becomes extremely nonlinear once inventory becomes one-sided.

This project treats liquidity quality as a state variable.

The important object is not only:


How much liquidity is in the pool?
How quickly does execution quality deteriorate under size?
Are options markets pricing downside convexity before spot stress becomes visible?