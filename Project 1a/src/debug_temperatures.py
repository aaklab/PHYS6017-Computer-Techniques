#!/usr/bin/env python3
"""
Debug temperature inconsistencies between Figure 3 and tables.
"""

import sys
sys.path.append('src')

from config import SimulationConfig
from simulate import MonteCarloSimulator

def debug_figure_3_vs_tables():
    """Check what temperatures are used in Figure 3 vs tables."""
    
    print("Debugging Figure 3 vs Table Inconsistencies")
    print("=" * 50)
    
    # Materials used in Figure 3
    materials = ['silver', 'copper', 'steel_carbon']
    Q = 20
    
    print("Running simulations for Figure 3 materials at Q=20:")
    print("-" * 50)
    
    results = {}
    
    for material in materials:
        print(f"\n{material.replace('_', ' ').title()}:")
        
        # Run simulation
        config = SimulationConfig.get_material_config(material, Q=Q)
        simulator = MonteCarloSimulator(config)
        result = simulator.run()
        
        # Get temperatures
        data = result['data']
        if data['hotspot_temperature']:
            raw_temp = data['hotspot_temperature'][-1]
            corrected_temp = config.apply_temperature_correction(raw_temp)
            
            print(f"  Raw simulation: {raw_temp:.1f} packets")
            print(f"  Corrected temp: {corrected_temp:.1f}°C")
            
            results[material] = {
                'raw': raw_temp,
                'corrected': corrected_temp
            }
    
    print(f"\n" + "="*50)
    print("COMPARISON:")
    print("="*50)
    
    print("Figure 3 should show these values:")
    for material, temps in results.items():
        print(f"  {material.replace('_', ' ').title():15s}: {temps['corrected']:5.1f}°C")
    
    print(f"\nTable A1 should show these same values for Q=20 column")
    print(f"Table A3 (Monte Carlo) should use these as base temperatures")
    
    return results

if __name__ == "__main__":
    results = debug_figure_3_vs_tables()
    
    print(f"\nIf Figure 3 shows different values, there's a data inconsistency!")
    print(f"All tables and figures should use the SAME simulation results.")