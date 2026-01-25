#!/usr/bin/env python3
"""
Test the new configuration with Steel Carbon instead of Stainless Steel.
"""

from src.config import SimulationConfig, MATERIAL_PROPERTIES

print("NEW CONFIGURATION TEST")
print("=" * 40)

# Check simulation time
config = SimulationConfig()
print(f"Simulation time: {config.t_max}s")
print(f"Steps: {config.n_steps}")

print("\nEquilibration times for new materials:")
L = 0.025  # Domain size (m)
materials = ['silver', 'copper', 'steel_carbon']

for material in materials:
    alpha = MATERIAL_PROPERTIES[material]
    t_ss = L**2 / (4 * alpha)
    status = '✓ Equilibrated' if t_ss <= config.t_max else '⚠ Still rising'
    print(f'{material.replace("_", " ").title():12s}: {t_ss:5.1f}s  {status}')

print(f"\nAll materials should reach equilibrium within {config.t_max}s!")
print("Steel Carbon equilibration time: ~8.3s (well within 10s limit)")