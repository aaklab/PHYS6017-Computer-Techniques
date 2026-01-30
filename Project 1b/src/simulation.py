import numpy as np

def generate_correlated_returns(mu, sigma, R, config):
    """Generate Monte Carlo price paths using Cholesky decomposition."""
    dt = config['model']['dt'] / 252  # Convert trading days to years
    H = config['model']['horizon_days']
    N_paths = config['simulation']['n_paths']
    random_seed = config['simulation']['random_seed']
    
    np.random.seed(random_seed)
    
    N = len(mu)
    L = np.linalg.cholesky(R)
    
    paths = np.zeros((N_paths, H, N))
    
    for path in range(N_paths):
        Z = np.random.randn(H, N)
        epsilon = Z @ L.T
        returns = mu * dt + sigma * np.sqrt(dt) * epsilon
        paths[path] = returns
    
    return paths
