#!/usr/bin/env python3
"""
Get current simulation results for Table 8 update.
"""

import sys
sys.path.append('src')

from config import SimulationConfig
from simulate import MonteCarloSimulator

def get_current_steady_state_temps():
    """Get current steady-state temperatures for copper and steel."""
    
    results = {}
    materials = ['copper', 'steel_carbon']
    Q = 20
    
    for material in materials:
        print(f"Getting {material} steady-state temperature...")
        config = SimulationConfig.get_material_config(material, Q=Q)
        simulator = MonteCarloSimulator(config)
        result = simulator.run()
        
        # Get corrected temperature
        data = result['data']
        if data['hotspot_temperature']:
            hotspot_temp = data['hotspot_temperature'][-1]
            corrected_temp = config.apply_temperature_correction(hotspot_temp)
            results[material] = corrected_temp
            print(f"  {material}: {corrected_temp:.1f}°C")
    
    return results

if __name__ == "__main__":
    temps = get_current_steady_state_temps()
    print(f"\nFor Table 8 update:")
    print(f"  Copper: {temps.get('copper', 0):.1f}°C (replace 45.0)")
    print(f"  Steel: {temps.get('steel_carbon', 0):.1f}°C (replace 85.0)")