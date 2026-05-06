#!/bin/bash

set -e

echo "1/6 live liquidity stress signal"
python3 models/depeg_signal.py

echo "2/6 executable slippage curve"
python3 models/amm.py

echo "3/6 options surface convexity"
python3 models/sabr.py

echo "4/6 historical stETH/ETH spread"
python3 data/coingecko.py

echo "5/6 historical regime study"
python3 backtest/regime_study.py

echo "6/6 regime intelligence + plots"
python3 research/regime_intelligence.py
python3 plots/generate_plots.py

echo "done"