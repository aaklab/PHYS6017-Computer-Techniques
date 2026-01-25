"""
Grid and geometry management for the heat diffusion simulation.
"""

import numpy as np
from typing import Tuple, List

try:
    from .config import SimulationConfig
except ImportError:
    # Fallback for direct execution
    from config import SimulationConfig


class Grid:
    """Manages the 2D grid for the heat diffusion simulation."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.Nx = config.Nx
        self.Ny = config.Ny
        self.dx = config.dx
        
        # Initialize temperature field
        self.temperature_field = np.zeros((self.Nx, self.Ny), dtype=float)
        
        # Pre-compute hot-spot mask for efficiency
        self.hotspot_mask = self._create_hotspot_mask()
        
        # Pre-compute neighbor directions for random walk
        self.neighbor_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    def _create_hotspot_mask(self) -> np.ndarray:
        """Create boolean mask for hot-spot region."""
        mask = np.zeros((self.Nx, self.Ny), dtype=bool)
        center_x, center_y = self.config.hotspot_center
        radius = self.config.hotspot_radius
        
        for i in range(self.Nx):
            for j in range(self.Ny):
                dx = i - center_x
                dy = j - center_y
                if dx*dx + dy*dy <= radius*radius:
                    mask[i, j] = True
        
        return mask
    
    def is_in_hotspot(self, x: int, y: int) -> bool:
        """Check if coordinates are within the hot-spot region."""
        if 0 <= x < self.Nx and 0 <= y < self.Ny:
            return self.hotspot_mask[x, y]
        return False
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if coordinates are within grid boundaries."""
        return 0 <= x < self.Nx and 0 <= y < self.Ny
    
    def get_random_hotspot_position(self, rng) -> Tuple[int, int]:
        """Generate random position within hot-spot region using proper disk sampling."""
        center_x, center_y = self.config.hotspot_center
        radius = self.config.hotspot_radius
        
        # FIXED: Proper uniform sampling over disk area
        # Use r = R * sqrt(u) where u ~ U(0,1) for uniform area sampling
        u = rng.random()  # uniform [0,1)
        r = radius * np.sqrt(u)  # proper radial distribution
        angle = rng.uniform(0, 2 * np.pi)
        
        x = int(center_x + r * np.cos(angle))
        y = int(center_y + r * np.sin(angle))
        
        # Ensure position is within grid bounds
        x = max(0, min(x, self.Nx - 1))
        y = max(0, min(y, self.Ny - 1))
        
        return x, y
    
    def get_neighbor_positions(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighbor positions for a given coordinate."""
        neighbors = []
        for dx, dy in self.neighbor_directions:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_position(new_x, new_y):
                neighbors.append((new_x, new_y))
        return neighbors
    
    def update_temperature_field(self, packet_positions: List[Tuple[int, int]]):
        """Update temperature field from packet positions."""
        # Reset field
        self.temperature_field.fill(0)
        
        # Count packets in each cell
        for x, y in packet_positions:
            if self.is_valid_position(x, y):
                self.temperature_field[x, y] += 1
    
    def get_hotspot_temperature(self) -> float:
        """Calculate average temperature in hot-spot region with thermal conductivity correction."""
        hotspot_temps = self.temperature_field[self.hotspot_mask]
        raw_temperature = np.mean(hotspot_temps) if len(hotspot_temps) > 0 else 0.0
        
        # Apply thermal conductivity correction
        corrected_temperature = self.config.apply_temperature_correction(raw_temperature)
        return corrected_temperature
    
    def get_temperature_statistics(self) -> dict:
        """Calculate temperature field statistics."""
        return {
            'mean': np.mean(self.temperature_field),
            'std': np.std(self.temperature_field),
            'max': np.max(self.temperature_field),
            'min': np.min(self.temperature_field),
            'hotspot_mean': self.get_hotspot_temperature()
        }
    
    def get_spatial_coordinates(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get physical coordinate arrays for plotting."""
        x = np.linspace(0, self.config.Lx, self.Nx)
        y = np.linspace(0, self.config.Ly, self.Ny)
        return np.meshgrid(x, y, indexing='ij')
    
    def reset(self):
        """Reset the grid to initial state."""
        self.temperature_field.fill(0)