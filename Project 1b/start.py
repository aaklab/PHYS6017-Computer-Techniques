import numpy as np
from src.config_loader import load_config
from src.data_loader import load_data, compute_returns
from src.parameter_estimation import estimate_parameters
from src.simulation import generate_correlated_returns
from src.risk_metrics import compute_portfolio_losses, compute_risk_metrics
from src.visualisation import save_results

# Load configuration
print("Loading configuration...")
config = load_config('config.yaml')

# Load and process data
print("Loading data...")
prices = load_data(config)
returns = compute_returns(prices, config['model']['return_type'])

# Estimate parameters
print("Estimating parameters...")
mu, sigma, R = estimate_parameters(returns)

# Run simulation
n_paths = config['simulation']['n_paths']
print(f"Running {n_paths:,} Monte Carlo simulations...")
paths = generate_correlated_returns(mu, sigma, R, config)

# Compute risk metrics
print("Computing risk metrics...")
weights = np.array(config['portfolio']['weights'])
S0 = prices.iloc[-1].values
losses = compute_portfolio_losses(paths, weights, S0)
risk_metrics = compute_risk_metrics(losses, config)

# Save results
print("Generating results PDF...")
output_file = save_results(losses, risk_metrics, config)

print(f"\nResults:")
for metric, value in risk_metrics.items():
    print(f"{metric}: {value:.2f}")
print(f"\nResults saved to {output_file}")
