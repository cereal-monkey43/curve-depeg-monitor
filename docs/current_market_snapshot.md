# Current Market Snapshot

This snapshot was generated from live Curve and Deribit data through `scripts/run_pipeline.sh`.

## Live liquidity state

The current Curve stETH/ETH pool is stETH-heavy rather than ETH-stressed. ETH represents roughly 28.7% of the pool, which means realized exit pressure into ETH is not currently elevated.

## Execution quality

Although spot conditions are calm, the execution curve is nonlinear. A modeled 10k stETH exit produces roughly 618 bps of executable discount, while a 50k stETH exit produces roughly 7603 bps of discount.

This is the main liquidity-quality point: TVL is not the same as usable liquidity. The pool can look large while marginal execution deteriorates sharply with size.

## Options surface

The live Deribit ETH front-expiry surface shows roughly 11 vol points of downside convexity premium, measured as deep OTM put IV minus near-ATM put IV.

This suggests the options market is still pricing tail risk more aggressively than the calm spot spread alone would imply.

## Interpretation

Current state is a cross-market divergence regime:

- spot spread is calm
- Curve inventory is not ETH-stressed
- executable slippage is nonlinear for size
- downside convexity remains bid

The takeaway is not that a depeg is imminent. The takeaway is that visible liquidity and executable liquidity are different state variables.