#!/usr/bin/env python3
"""
Test the updated configuration parameters.
"""

from src.config import SimulationConfig, MATERIAL_PROPERTIES

print("Updated Simulation Configuration:")
print("=" * 50)

# Test default config
config = SimulationConfig()
print(f"Default simulation time: {config.t_max}s")
print(f"Default steps: {config.n_steps}")
print(f"Output interval: {config.output_interval}")
print(f"Data points collected: {config.n_steps // config.output_interval}")

print("\nTheoretical equilibration times:")
print("=" * 50)

L = 0.025  # Domain size (m)
for material, alpha in sorted(MATERIAL_PROPERTIES.items(), key=lambda x: x[1], reverse=True):
    t_ss = L**2 / (4 * alpha)
    config_mat = SimulationConfig.get_material_config(material)
    status = "✓ Equilibrated" if t_ss <= config_mat.t_max else "⚠ Still rising"
    print(f"{material.replace('_', ' ').title():15s}: {t_ss:5.1f}s  {status}")

print(f"\nSimulation time: {config.t_max}s")
print("Materials that will reach steady state: Silver, Gold, Copper, Aluminum")
print("Materials still equilibrating: Iron, Steel Carbon, Steel Stainless")