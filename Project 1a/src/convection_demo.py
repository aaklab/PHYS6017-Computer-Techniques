#!/usr/bin/env python3
"""
Demonstration of convection cooling in Monte Carlo heat diffusion simulation.

This script shows how to use the convection cooling feature to simulate
heat loss to air through forced or natural convection.
"""

import sys
import os
sys.path.append('src')

from config import SimulationConfig
from simulate import MonteCarloSimulator

def demonstrate_convection_cooling():
    """Demonstrate convection cooling with different settings."""
    
    print("Monte Carlo Heat Diffusion - Convection Cooling Demo")
    print("=" * 55)
    
    # Example 1: No convection (baseline)
    print("\n1. Baseline simulation (no convection cooling)")
    print("-" * 50)
    
    config_baseline = SimulationConfig.get_material_config('copper', Q=20)
    config_baseline.convection_prob = 0.0  # No convection
    
    simulator = MonteCarloSimulator(config_baseline)
    result_baseline = simulator.run()
    
    baseline_temp = result_baseline['data']['hotspot_temperature'][-1]
    print(f"Final temperature (no convection): {baseline_temp:.1f}")
    
    # Example 2: Weak convection (natural convection)
    print("\n2. Natural convection cooling")
    print("-" * 50)
    
    config_natural = SimulationConfig.get_material_config('copper', Q=20)
    config_natural.convection_prob = 0.001  # Weak convection
    
    simulator = MonteCarloSimulator(config_natural)
    result_natural = simulator.run()
    
    natural_temp = result_natural['data']['hotspot_temperature'][-1]
    natural_convected = result_natural['data']['total_convected'][-1]
    print(f"Final temperature (natural convection): {natural_temp:.1f}")
    print(f"Packets lost to convection: {natural_convected}")
    
    # Example 3: Strong convection (forced air cooling)
    print("\n3. Forced air cooling")
    print("-" * 50)
    
    config_forced = SimulationConfig.get_material_config('copper', Q=20)
    config_forced.convection_prob = 0.01  # Strong convection
    
    simulator = MonteCarloSimulator(config_forced)
    result_forced = simulator.run()
    
    forced_temp = result_forced['data']['hotspot_temperature'][-1]
    forced_convected = result_forced['data']['total_convected'][-1]
    print(f"Final temperature (forced air): {forced_temp:.1f}")
    print(f"Packets lost to convection: {forced_convected}")
    
    # Summary
    print(f"\n" + "=" * 55)
    print("CONVECTION COOLING EFFECTIVENESS")
    print("=" * 55)
    
    print(f"{'Cooling Type':<20} {'Final Temp':<12} {'Reduction':<12} {'Convected':<10}")
    print("-" * 55)
    
    print(f"{'No convection':<20} {baseline_temp:<12.1f} {'--':<12} {'0':<10}")
    
    natural_reduction = baseline_temp - natural_temp
    print(f"{'Natural convection':<20} {natural_temp:<12.1f} {natural_reduction:<12.1f} {natural_convected:<10}")
    
    forced_reduction = baseline_temp - forced_temp
    print(f"{'Forced air':<20} {forced_temp:<12.1f} {forced_reduction:<12.1f} {forced_convected:<10}")
    
    print(f"\nConvection cooling provides significant temperature reduction!")
    print(f"Natural convection: {100*natural_reduction/baseline_temp:.1f}% temperature reduction")
    print(f"Forced air cooling: {100*forced_reduction/baseline_temp:.1f}% temperature reduction")

def show_convection_parameters():
    """Show how to configure convection parameters."""
    
    print(f"\n" + "=" * 55)
    print("CONVECTION PARAMETER GUIDE")
    print("=" * 55)
    
    print("Convection probability represents the chance per time step that")
    print("a heat packet 'evaporates' into the air, simulating heat loss")
    print("through convection cooling.\n")
    
    print("Recommended values:")
    print("  0.000 - No convection (vacuum or perfect insulation)")
    print("  0.001 - Natural convection (still air)")
    print("  0.005 - Moderate forced convection (small fan)")
    print("  0.010 - Strong forced convection (large fan)")
    print("  0.020 - Very strong cooling (liquid cooling)")
    
    print(f"\nTo use convection cooling in your simulation:")
    print("1. Create a configuration:")
    print("   config = SimulationConfig.get_material_config('copper', Q=20)")
    print("2. Set convection probability:")
    print("   config.convection_prob = 0.005  # Moderate cooling")
    print("3. Run simulation:")
    print("   simulator = MonteCarloSimulator(config)")
    print("   result = simulator.run()")

if __name__ == "__main__":
    demonstrate_convection_cooling()
    show_convection_parameters()