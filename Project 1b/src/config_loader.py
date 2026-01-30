import yaml
import numpy as np

def load_config(config_path='config.yaml'):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate weights sum to 1
    weights = np.array(config['portfolio']['weights'])
    if not np.isclose(weights.sum(), 1.0):
        raise ValueError(f"Portfolio weights must sum to 1, got {weights.sum()}")
    
    return config
