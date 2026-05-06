# Cross-Market stETH Liquidity Fragility Engine

A research system for studying how liquidity weakens across the stETH market before visible depeg stress appears.

This project started from something that kept bothering me while watching stETH during periods of market stress.

Most dashboards focus almost entirely on the spot spread:
- Is stETH trading below ETH?
- By how much?
- Is the peg breaking?

But during large dislocations, the spread itself often feels like a lagging symptom rather than the actual problem.

The more important question seemed to be:

> What happens to executable liquidity before the market visibly breaks?

A pool can still show billions in TVL while actual execution quality deteriorates extremely quickly under size. Options markets can start aggressively pricing downside convexity while the spot spread still looks relatively calm. Liquidity can appear stable right up until it suddenly isn’t.

That disconnect is what this project tries to study.

---

## What the project does

The engine combines live and historical data from:
- Curve
- CoinGecko
- Deribit

to model liquidity conditions across multiple layers of the stETH market simultaneously.

Instead of treating the market as a single spot spread, the system looks at:
- pool inventory imbalance
- executable slippage paths
- historical spread widening regimes
- options skew and convexity structure
- conditional fragility transitions

The goal is not to “predict a depeg.”

The goal is to understand whether liquidity quality is already deteriorating before visible stress fully shows up in price.

---

## Core idea

One thing I found interesting while building this is that liquidity stress is often nonlinear.

A market can look stable for small trades while becoming extremely fragile for larger execution sizes.

That matters because real stress events are usually driven by forced flows:
- liquidations
- large exits
- deleveraging
- hedge adjustments
- inventory imbalances

In those situations, marginal execution quality matters more than displayed TVL.

This project tries to model that distinction directly.

---

# System Components

## 1. Live Liquidity Stress Engine

Pulls live Curve stETH pool data and models executable liquidation paths.

The system estimates:
- pool imbalance
- executable ETH received under different trade sizes
- marginal depth deterioration
- liquidation discounts
- execution regime quality

One thing that became clear very quickly is that execution quality deteriorates much faster than raw TVL numbers would suggest.

---

## 2. Historical Regime Study

Builds a rolling history of stETH/ETH spread behavior and classifies:
- widening regimes
- realized stress periods
- early-warning windows
- dislocation persistence

The idea here was to move away from isolated screenshots of stress and instead look at how fragility evolves over time.

---

## 3. Options Convexity Surface

Pulls live ETH option surface data from Deribit and studies downside skew structure.

The engine tracks:
- put skew steepness
- downside convexity premium
- risk reversals
- deep OTM put demand
- relative repricing across strikes

What interested me here was whether options markets begin pricing instability before spot stress becomes obvious.

In several cases, they appeared to.

---

## 4. Conditional Fragility Layer

This part tries to answer a more statistical question:

> Do widening regimes actually precede future stress more often than calm regimes?

The engine compares:
- calm liquidity states
- widening-but-not-yet-stressed states
- realized future dislocation probabilities

Across 365 daily observations:
- calm regimes showed roughly a 4.1% probability of entering a fragility event within 7 days
- widening regimes increased that probability to around 12.1%

That doesn’t “predict” depegs, but it does suggest that liquidity deterioration contains meaningful structure before major visible stress.

---

## 5. Regime Intelligence Engine

Combines:
- spot spread behavior
- executable liquidity quality
- pool imbalance
- options convexity structure

into a unified interpretation layer.

One of the more interesting outcomes was seeing situations where:
- spot spreads looked relatively calm
- but options convexity and executable depth both suggested rising instability underneath the surface

That divergence became one of the main conclusions of the project.

---

# Key Findings

Across the historical sample:
- severe spot dislocations above 30bps were relatively rare
- but liquidity deterioration appeared much more frequently underneath the surface

The engine identified 58 widening regimes where:
- spreads remained below formal stress thresholds
- but execution quality and liquidity structure weakened materially

At larger execution sizes, modeled liquidation paths became highly nonlinear:
- 50k stETH liquidation paths produced extremely severe execution deterioration under thin marginal depth assumptions

At the same time:
- downside convexity stayed persistently elevated in options markets
- even when visible spot stress looked relatively contained

One thing I kept coming back to while building this was that “spot calmness” and “liquidity stability” are not necessarily the same thing.

That distinction became the central motivation behind the entire system.

---

# Why I built this

I’ve always liked market structure problems where the important variables are partially hidden underneath the surface.

Crypto is especially interesting because so much of the market is observable in real time:
- pool inventories
- liquidity imbalances
- options surfaces
- execution paths
- funding dynamics

You can actually watch liquidity conditions evolve.

The difficult part is figuring out which changes are structural and which are just noise.

This project was basically my attempt to think more carefully about that problem.

---

# Repository Structure

```text
backtest/
    regime_study.py
    validate.py

data/
    coingecko.py
    curve_graph.py
    deribit.py

models/
    amm.py
    depeg_signal.py
    sabr.py
    skew.py

research/
    build_memo.py
    fragility_metrics.py
    regime_intelligence.py
    transition_matrix.py

plots/
    generate_plots.py

scripts/
    run_pipeline.sh