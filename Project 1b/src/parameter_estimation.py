import numpy as np

def estimate_parameters(returns):
    """Estimate mean, volatility, and correlation matrix."""
    mu = returns.mean().values
    sigma = returns.std().values
    R = returns.corr().values
    return mu, sigma, R
