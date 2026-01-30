import numpy as np

def compute_portfolio_losses(paths, weights, S0):
    """Compute portfolio losses from simulated paths."""
    N_paths, H, N = paths.shape
    losses = np.zeros(N_paths)
    
    for i in range(N_paths):
        cumulative_returns = np.sum(paths[i], axis=0)
        final_prices = S0 * np.exp(cumulative_returns)
        V0 = np.sum(weights * S0)
        VT = np.sum(weights * final_prices)
        losses[i] = V0 - VT
    
    return losses

def compute_var(losses, alpha=0.95):
    """Compute Value at Risk at confidence level alpha."""
    return np.percentile(losses, alpha * 100)

def compute_es(losses, alpha=0.95):
    """Compute Expected Shortfall at confidence level alpha."""
    var = compute_var(losses, alpha)
    return losses[losses >= var].mean()

def compute_risk_metrics(losses, config):
    """Compute all risk metrics based on config."""
    confidence_levels = config['risk']['confidence_levels']
    compute_es_flag = config['risk']['compute_expected_shortfall']
    
    results = {}
    for alpha in confidence_levels:
        var = compute_var(losses, alpha)
        results[f'VaR_{int(alpha*100)}'] = var
        
        if compute_es_flag:
            es = compute_es(losses, alpha)
            results[f'ES_{int(alpha*100)}'] = es
    
    return results
