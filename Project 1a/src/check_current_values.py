#!/usr/bin/env python3
"""
Check current convection effectiveness and temperature values.
"""

import sys
sys.path.append('src')

from config import SimulationConfig, CONVECTION_PROB
from simulate import MonteCarloSimulator

def check_convection_effectiveness():
    """Check convection effectiveness for different materials."""
    
    print(f"Current CONVECTION_PROB = {CONVECTION_PROB}")
    print("=" * 50)
    
    materials = ['silver', 'copper', 'steel_carbon']
    Q = 20  # Standard test value
    
    for material in materials:
        print(f"\n{material.replace('_', ' ').title()}:")
        print("-" * 30)
        
        # Create config and run simulation
        config = SimulationConfig.get_material_config(material, Q=Q)
        simulator = MonteCarloSimulator(config)
        result = simulator.run()
        
        # Get final values
        data = result['data']
        if data['total_injected'] and data['total_removed'] and data['total_convected']:
            total_injected = data['total_injected'][-1]
            total_removed = data['total_removed'][-1]
            total_convected = data['total_convected'][-1]
            
            # Calculate percentages
            total_lost = total_removed + total_convected
            convection_pct = (total_convected / total_lost * 100) if total_lost > 0 else 0
            boundary_pct = (total_removed / total_lost * 100) if total_lost > 0 else 0
            
            # Get temperature
            hotspot_temp = data['hotspot_temperature'][-1] if data['hotspot_temperature'] else 0
            corrected_temp = config.apply_temperature_correction(hotspot_temp)
            absolute_temp = corrected_temp + 21  # Add ambient temperature
            
            print(f"  Simulation temperature: {hotspot_temp:.1f} packets")
            print(f"  Corrected temperature: {corrected_temp:.1f}°C")
            print(f"  Absolute temperature: {absolute_temp:.1f}°C")
            print(f"  Total injected: {total_injected}")
            print(f"  Total lost: {total_removed + total_convected}")
            print(f"  Via convection: {total_convected} ({convection_pct:.1f}%)")
            print(f"  Via boundaries: {total_removed} ({boundary_pct:.1f}%)")
        else:
            print("  No data available")

if __name__ == "__main__":
    check_convection_effectiveness()