# Monte Carlo Portfolio Risk Simulation

This project implements a Monte Carlo simulation for portfolio risk analysis using VaR and ES metrics.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to customize:
- Data source, tickers, and date range
- Portfolio weights
- Model parameters (time horizon, return type)
- Simulation settings (number of paths, random seed)
- Risk metrics (confidence levels, ES computation)
- Output options (directory, plots, loss samples)

## Usage

```bash
python start.py
```

Results will be saved to the directory specified in `config.yaml` (default: `outputs/results.pdf`).

## Structure

- `config.yaml`: Configuration file for all parameters
- `start.py`: Main entry point
- `src/config_loader.py`: Load and validate configuration
- `src/data_loader.py`: Load and clean price data
- `src/parameter_estimation.py`: Estimate μ, σ, and correlations
- `src/simulation.py`: Generate Monte Carlo price paths
- `src/risk_metrics.py`: Compute VaR and ES
- `src/visualisation.py`: Produce plots and tables
