#!/usr/bin/env python3
"""
Analysis of equilibration times for different materials.
"""

import numpy as np
from src.config import MATERIAL_PROPERTIES

print("EQUILIBRATION TIME ANALYSIS")
print("=" * 60)
print("Problem: Stainless steel reaches 'steady state' too quickly")
print("Solution: Extend simulation time or acknowledge non-equilibrium")
print()

# Calculate theoretical equilibration times
L = 0.025  # Domain size (m)
print("Theoretical time to steady state: t_ss ≈ L²/(4α)")
print(f"Domain size L = {L*1000:.0f} mm")
print()

print("Material           α (mm²/s)    t_ss (s)   Status at 2.0s   Status at 15.0s")
print("-" * 75)

for material, alpha in sorted(MATERIAL_PROPERTIES.items(), key=lambda x: x[1], reverse=True):
    alpha_mm2s = alpha * 1e6  # Convert to mm²/s
    t_ss = L**2 / (4 * alpha)
    
    # Status at different simulation times
    status_2s = "Equilibrated" if t_ss <= 2.0 else "Rising"
    status_15s = "Equilibrated" if t_ss <= 15.0 else "Rising"
    
    print(f"{material.replace('_', ' ').title():15s} {alpha_mm2s:8.1f}    {t_ss:6.1f}    {status_2s:12s}   {status_15s}")

print()
print("RECOMMENDATIONS:")
print("1. Use 15s simulation time (compromise between accuracy and runtime)")
print("2. Acknowledge in results that stainless steel is still equilibrating")
print("3. Show equilibration trends rather than claiming steady state")
print("4. Include theoretical equilibration times in tables")