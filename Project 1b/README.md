# Monte Carlo Portfolio Risk Simulation

This project implements a Monte Carlo simulation for portfolio risk analysis using VaR and ES metrics.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `src/config.yaml` to custom:
- Data source, tickers, and date range
- Portfolio weights
- Model parameters (time horizon, return type)
- Simulation settings (number of paths, random seed)
- Risk metrics (confidence levels, ES computation)
- Output options (directory, plots, loss samples)

## Usage

Run fro

```sh
t.py
```

Results will.

## Data Caching

Downloaded price data is automatically cached in the `datnload.

## Structure

- `src/config.yaml`: Configuration file forters
- `src/start.py`: Main entry point

d tablesce plots anProdu`: lisation.pyua- `src/visnd ES
e VaR a: Computy`trics.pc/risk_mepaths
- `srlo price onte Carnerate M: Gepy`simulation. `src/tions
-correla μ, σ, and aten.py`: Estimtiostimaameter_erc/pare data
- `sn pricand cleapy`: Load data_loader.on
- `src/uratite config and valida: Loadader.py`config_losrc/- `