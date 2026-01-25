"""
Configuration module for Monte Carlo heat diffusion simulation.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Dict
import numpy as np


# Material thermal diffusivity constants (mm²/s) from Wikipedia
# Source: Brown, Marco (1958). Introduction to Heat Transfer (3rd ed.). McGraw-Hill.
# https://en.wikipedia.org/wiki/Thermal_diffusivity
MATERIAL_PROPERTIES: Dict[str, float] = {
    'silver': 165.63e-6,    # Silver, pure (99.9%) - converted from 165.63 mm²/s
    'gold': 127e-6,         # Gold - converted from 127 mm²/s  
    'copper': 111e-6,       # Copper at 25°C - converted from 111 mm²/s
    'aluminum': 97e-6,      # Aluminum - converted from 97 mm²/s
    'iron': 23e-6,          # Iron - converted from 23 mm²/s
    'steel_carbon': 18.8e-6, # Steel, AISI 1010 (0.1% carbon) - converted from 18.8 mm²/s
    'steel_stainless': 4.2e-6, # Steel, stainless 304A at 27°C - converted from 4.2 mm²/s
}

# Material thermal conductivity constants (W/m·K) for temperature scaling
# Source: CRC Handbook of Chemistry and Physics, 104th Edition (2023-2024)
#         Section 12: Properties of Solids, Table "Thermal Conductivity of Metals and Alloys"
#         All values at room temperature (20-25°C)
THERMAL_CONDUCTIVITY: Dict[str, float] = {
    'silver': 429,          # Silver, pure
    'gold': 317,            # Gold, pure (updated to match table)
    'copper': 401,          # Copper, pure
    'aluminum': 237,        # Aluminum, pure
    'iron': 80,             # Iron, pure (updated to match table)
    'steel_carbon': 50,     # Steel, carbon (updated to match table)
    'steel_stainless': 16,  # Steel, stainless (updated to match table)
}

# --- SIMULATION PARAMETERS ---
# Probability that a packet evaporates into the air per time step.
# Calibrated for realistic heat sink temperatures based on industrial data.
# Sources: Culham & Muzychka (2001), Teertstra et al. (2000), Kraus & Bar-Cohen (1995)
# Target: Copper heat sink should reach 45-60°C under typical load (21°C ambient)
# Calibration: Adjusted to achieve ~30°C simulation temperature for copper
CONVECTION_PROB = 0.004  # Realistic heat sink cooling (copper: ~50°C, silver: ~49°C)

# Standard heat injection rates for steady-state studies (packets/step)
STANDARD_Q_VALUES = [5, 10, 15, 20, 25, 30, 35, 40]


@dataclass
class SimulationConfig:
    """Configuration parameters for the Monte Carlo heat diffusion simulation."""
    
    # Fixed geometry parameters (standardized for all studies)
    Lx: float = 0.025  # Plate width (m) - FIXED
    Ly: float = 0.025  # Plate height (m) - FIXED
    dx: float = 0.002  # Grid spacing (m) - FIXED
    
    # Fixed time parameters (standardized for all studies)
    dt: float = 0.002  # Time step (s) - FIXED for stability
    t_max: float = 5.0  # Total simulation time (s) - REDUCED for faster runs (was 10.0)
    
    # Material properties - USE get_material_config() to set
    alpha: float = 1.1e-4  # Thermal diffusivity (m²/s) - SET BY MATERIAL
    
    # Fixed Monte Carlo parameters (standardized for all studies)
    N_packets: int = 800  # Number of heat packets - REDUCED for speed (was 1500)
    random_seed: Optional[int] = 42  # Random seed for reproducibility - FIXED
    
    # Fixed hot-spot parameters (standardized for all studies)
    hotspot_center: Optional[Tuple[int, int]] = None  # (x, y) in grid coordinates - FIXED
    hotspot_radius: int = 3  # Hot-spot radius in grid cells - FIXED
    Q: int = 15  # Heat injection rate (packets per time step) - ADJUSTABLE FOR STUDIES
    
    # Fixed boundary conditions (standardized for all studies)
    boundary_type: str = "absorbing"  # "absorbing" or "reflecting" - FIXED
    
    # Convection cooling parameters
    convection_prob: float = CONVECTION_PROB  # Probability of packet evaporation per time step
    
    # Fixed output parameters (standardized for all studies)
    output_interval: int = 100  # Steps between data collection - INCREASED for speed (was 50)
    save_snapshots: bool = True  # Save temperature field snapshots - FIXED
    
    def __post_init__(self):
        """Validate and compute derived parameters."""
        # Calculate grid dimensions
        self.Nx = int(self.Lx / self.dx)
        self.Ny = int(self.Ly / self.dx)
        
        # Set default hot-spot location to center
        if self.hotspot_center is None:
            self.hotspot_center = (self.Nx // 2, self.Ny // 2)
        
        # Calculate move probability from diffusivity
        # From equation (4): α ≈ (Δr)²/(4Δt)
        self.move_probability = 4 * self.alpha * self.dt / (self.dx ** 2)
        
        # Calculate total simulation steps
        self.n_steps = int(self.t_max / self.dt)
        
        # Validate parameters
        self._validate_parameters()
    
    def _validate_parameters(self):
        """Validate configuration parameters."""
        if self.move_probability > 1.0:
            raise ValueError(
                f"Move probability {self.move_probability:.3f} > 1.0. "
                f"Reduce dt or increase dx for stability."
            )
        
        if self.hotspot_center[0] >= self.Nx or self.hotspot_center[1] >= self.Ny:
            raise ValueError("Hot-spot center is outside grid boundaries.")
        
        if self.hotspot_radius <= 0:
            raise ValueError("Hot-spot radius must be positive.")
    
    @classmethod
    def get_material_config(cls, material: str, Q: int = 15, **kwargs) -> 'SimulationConfig':
        """
        Create configuration for specific material with adjustable heat injection rate.
        
        Args:
            material: Material name (see MATERIAL_PROPERTIES keys)
            Q: Heat injection rate (packets per time step) - for steady-state studies
            **kwargs: Additional parameters to override defaults
            
        Returns:
            SimulationConfig with material-specific thermal diffusivity
            
        Example:
            # Study copper at different heat injection rates
            config_cu_low = SimulationConfig.get_material_config('copper', Q=10)
            config_cu_high = SimulationConfig.get_material_config('copper', Q=30)
            
            # Compare materials at same heat injection rate
            config_cu = SimulationConfig.get_material_config('copper', Q=20)
            config_al = SimulationConfig.get_material_config('aluminum', Q=20)
        """
        if material not in MATERIAL_PROPERTIES:
            available = ', '.join(MATERIAL_PROPERTIES.keys())
            raise ValueError(f"Unknown material '{material}'. Available: {available}")
        
        defaults = {
            'alpha': MATERIAL_PROPERTIES[material],
            'Q': Q
        }
        defaults.update(kwargs)
        return cls(**defaults)
    
    @classmethod
    def steady_state_study_configs(cls, materials: list = None, Q_values: list = None) -> Dict[str, Dict[int, 'SimulationConfig']]:
        """
        Generate configurations for steady-state temperature studies.
        
        Args:
            materials: List of materials to study (default: ['silver', 'copper', 'steel_stainless'])
            Q_values: List of Q values to test (default: [5, 10, 15, 20, 25])
            
        Returns:
            Dictionary: {material: {Q: config}} for all combinations
            
        Example:
            configs = SimulationConfig.steady_state_study_configs()
            # Run copper at Q=20
            result = simulator.run(configs['copper'][20])
        """
        if materials is None:
            materials = ['silver', 'copper', 'steel_carbon']  # Best, benchmark, reasonable worst from Wikipedia data
        if Q_values is None:
            Q_values = [5, 10, 15, 20, 25]
            
        configs = {}
        for material in materials:
            configs[material] = {}
            for Q in Q_values:
                configs[material][Q] = cls.get_material_config(material, Q=Q)
        
        return configs
    
    @classmethod
    def material_comparison_config(cls, Q: int = 15) -> Dict[str, 'SimulationConfig']:
        """
        Generate configurations for comparing all materials at fixed Q.
        
        Args:
            Q: Heat injection rate for all materials
            
        Returns:
            Dictionary: {material: config} for all materials
            
        Example:
            configs = SimulationConfig.material_comparison_config(Q=20)
            for material, config in configs.items():
                result = simulator.run(config)
        """
        configs = {}
        for material in MATERIAL_PROPERTIES.keys():
            configs[material] = cls.get_material_config(material, Q=Q)
        return configs
    
    def get_temperature_correction_factor(self) -> float:
        """
        Calculate temperature correction factor based on thermal conductivity.
        
        Real physics: T ∝ 1/κ (conductivity)
        Model physics: T ∝ 1/α (diffusivity)
        
        Correction: T_corrected = T_simulated × (α/κ_normalized)
        
        Returns:
            Correction factor to multiply simulated temperatures
        """
        # Find material name from alpha value
        material_name = None
        for name, alpha_val in MATERIAL_PROPERTIES.items():
            if abs(self.alpha - alpha_val) < 1e-8:
                material_name = name
                break
        
        if material_name is None:
            return 1.0  # No correction for unknown materials
        
        # Get thermal properties
        alpha = MATERIAL_PROPERTIES[material_name]
        kappa = THERMAL_CONDUCTIVITY[material_name]
        
        # Use steel as reference material (normalize to steel values)
        alpha_ref = MATERIAL_PROPERTIES['steel_carbon']
        kappa_ref = THERMAL_CONDUCTIVITY['steel_carbon']
        
        # Calculate correction factor: (α/κ) / (α_ref/κ_ref)
        correction_factor = (alpha / kappa) / (alpha_ref / kappa_ref)
        
        return correction_factor
    
    def apply_temperature_correction(self, temperature: float) -> float:
        """
        Apply thermal conductivity correction to simulated temperature.
        
        Args:
            temperature: Raw simulated temperature (packet count)
            
        Returns:
            Corrected temperature accounting for thermal conductivity
        """
        correction_factor = self.get_temperature_correction_factor()
        return temperature * correction_factor
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'geometry': {
                'Lx': self.Lx, 'Ly': self.Ly, 'dx': self.dx,
                'Nx': self.Nx, 'Ny': self.Ny
            },
            'time': {
                'dt': self.dt, 't_max': self.t_max, 'n_steps': self.n_steps
            },
            'material': {
                'alpha': self.alpha, 'move_probability': self.move_probability
            },
            'monte_carlo': {
                'N_packets': self.N_packets, 'random_seed': self.random_seed
            },
            'hotspot': {
                'center': self.hotspot_center, 'radius': self.hotspot_radius,
                'injection_rate': self.Q
            },
            'boundary': {
                'type': self.boundary_type
            },
            'convection': {
                'probability': self.convection_prob
            },
            'output': {
                'interval': self.output_interval, 'save_snapshots': self.save_snapshots
            }
        }
    
    def __str__(self) -> str:
        """String representation of configuration."""
        # Find material name from alpha value
        material_name = "custom"
        for name, alpha_val in MATERIAL_PROPERTIES.items():
            if abs(self.alpha - alpha_val) < 1e-6:
                material_name = name.title()
                break
        
        return (
            f"SimulationConfig(\n"
            f"  Grid: {self.Nx}×{self.Ny} ({self.Lx*1000:.0f}×{self.Ly*1000:.0f} mm)\n"
            f"  Time: {self.n_steps} steps of {self.dt*1000:.1f}ms\n"
            f"  Material: {material_name} (α={self.alpha:.2e} m²/s, p={self.move_probability:.3f})\n"
            f"  Packets: {self.N_packets}, Injection: {self.Q}/step\n"
            f"  Hot-spot: center={self.hotspot_center}, radius={self.hotspot_radius}\n"
            f"  Convection: probability={self.convection_prob:.3f}\n"
            f")"
        )


def print_material_properties():
    """Print available materials and their thermal diffusivities."""
    print("Available Materials and Thermal Diffusivities (Wikipedia/Brown 1958):")
    print("=" * 65)
    for material, alpha in sorted(MATERIAL_PROPERTIES.items(), key=lambda x: x[1], reverse=True):
        alpha_mm2_s = alpha * 1e6  # Convert back to mm²/s for display
        print(f"{material.replace('_', ' ').title():20s}: {alpha:.2e} m²/s ({alpha_mm2_s:.1f} mm²/s)")
    print()


def print_standard_q_values():
    """Print standard Q values for steady-state studies."""
    print("Standard Heat Injection Rates (Q values):")
    print("=" * 40)
    print(f"Range: {min(STANDARD_Q_VALUES)} - {max(STANDARD_Q_VALUES)} packets/step")
    print(f"Values: {STANDARD_Q_VALUES}")
    print()


# Convenience functions for quick access
def get_material_alpha(material: str) -> float:
    """Get thermal diffusivity for a material."""
    if material not in MATERIAL_PROPERTIES:
        available = ', '.join(MATERIAL_PROPERTIES.keys())
        raise ValueError(f"Unknown material '{material}'. Available: {available}")
    return MATERIAL_PROPERTIES[material]


def get_material_conductivity(material: str) -> float:
    """Get thermal conductivity for a material."""
    if material not in THERMAL_CONDUCTIVITY:
        available = ', '.join(THERMAL_CONDUCTIVITY.keys())
        raise ValueError(f"Unknown material '{material}'. Available: {available}")
    return THERMAL_CONDUCTIVITY[material]


def list_materials() -> list:
    """Get list of available materials."""
    return list(MATERIAL_PROPERTIES.keys())