"""
Random number generation utilities for Monte Carlo simulation.
"""

import numpy as np
from typing import Optional, Tuple, List


class RandomNumberGenerator:
    """Manages random number generation for the simulation."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize random number generator with optional seed."""
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        self._call_count = 0
    
    def uniform(self, low: float = 0.0, high: float = 1.0) -> float:
        """Generate uniform random number."""
        self._call_count += 1
        return self.rng.uniform(low, high)
    
    def choice(self, options: List) -> any:
        """Choose random element from list."""
        self._call_count += 1
        return options[self.rng.randint(0, len(options))]
    
    def random(self) -> float:
        """Generate random number in [0, 1)."""
        self._call_count += 1
        return self.rng.random()
    
    def randint(self, low: int, high: int) -> int:
        """Generate random integer in [low, high)."""
        self._call_count += 1
        return self.rng.randint(low, high)
    
    def normal(self, mean: float = 0.0, std: float = 1.0) -> float:
        """Generate normal random number."""
        self._call_count += 1
        return self.rng.normal(mean, std)
    
    def exponential(self, scale: float = 1.0) -> float:
        """Generate exponential random number."""
        self._call_count += 1
        return self.rng.exponential(scale)
    
    def get_state(self) -> dict:
        """Get current state of random number generator."""
        return {
            'seed': self.seed,
            'call_count': self._call_count,
            'state': self.rng.get_state()
        }
    
    def set_state(self, state: dict):
        """Set state of random number generator."""
        self.seed = state['seed']
        self._call_count = state['call_count']
        self.rng.set_state(state['state'])
    
    def reset(self, seed: Optional[int] = None):
        """Reset random number generator."""
        if seed is not None:
            self.seed = seed
        self.rng = np.random.RandomState(self.seed)
        self._call_count = 0


class ReproducibleRNG:
    """Random number generator that ensures reproducible results."""
    
    def __init__(self, base_seed: int = 42):
        """Initialize with base seed for reproducibility."""
        self.base_seed = base_seed
        self.simulation_rng = RandomNumberGenerator(base_seed)
        self.packet_rng = RandomNumberGenerator(base_seed + 1)
        self.injection_rng = RandomNumberGenerator(base_seed + 2)
    
    def get_simulation_rng(self) -> RandomNumberGenerator:
        """Get RNG for general simulation use."""
        return self.simulation_rng
    
    def get_packet_rng(self) -> RandomNumberGenerator:
        """Get RNG for packet movement."""
        return self.packet_rng
    
    def get_injection_rng(self) -> RandomNumberGenerator:
        """Get RNG for heat injection."""
        return self.injection_rng
    
    def reset_all(self):
        """Reset all random number generators."""
        self.simulation_rng.reset(self.base_seed)
        self.packet_rng.reset(self.base_seed + 1)
        self.injection_rng.reset(self.base_seed + 2)
    
    def get_state_summary(self) -> dict:
        """Get summary of all RNG states."""
        return {
            'base_seed': self.base_seed,
            'simulation_calls': self.simulation_rng._call_count,
            'packet_calls': self.packet_rng._call_count,
            'injection_calls': self.injection_rng._call_count
        }