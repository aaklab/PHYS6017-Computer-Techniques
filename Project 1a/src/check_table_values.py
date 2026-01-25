#!/usr/bin/env python3
"""
Check current simulation values to verify table consistency.
"""

import sys
sys.path.append('src')

from config import SimulationConfig
from simulate import MonteCarloSimulator

def check_current_table_values():
    """Check current simulation values for table verification."""
    
    print("Checking Current Table Values")
    print("=" * 40)
    
    # Test the materials mentioned in the feedback
    materials = ['copper', 'steel_carbon', 'steel_stainless']
    Q = 20  # Standard test value
    
    results = {}
    
    for material in materials:
        if material in ['steel_stainless']:
            # Check if this material is still in our config
            from config import MATERIAL_PROPERTIES
            if material not in MATERIAL_PROPERTIES:
                print(f"⚠️  {material} not in current configuration (removed earlier)")
                continue
        
        print(f"\n{material.replace('_', ' ').title()}:")
        print("-" * 30)
        
        # Create config and run simulation
        config = SimulationConfig.get_material_config(material, Q=Q)
        simulator = MonteCarloSimulator(config)
        result = simulator.run()
        
        # Get final values
        data = result['data']
        if data['hotspot_temperature']:
            hotspot_temp = data['hotspot_temperature'][-1]
            corrected_temp = config.apply_temperature_correction(hotspot_temp)
            
            print(f"  Simulation temperature: {hotspot_temp:.1f} packets")
            print(f"  Corrected temperature: {corrected_temp:.1f}°C")
            
            results[material] = {
                'simulation_temp': hotspot_temp,
                'corrected_temp': corrected_temp
            }
    
    print(f"\n" + "="*50)
    print("SUMMARY FOR TABLE VERIFICATION:")
    print("="*50)
    
    for material, values in results.items():
        print(f"{material.replace('_', ' ').title():15s}: {values['corrected_temp']:5.1f}°C")
    
    # Check what the feedback is referring to
    print(f"\nFeedback mentions:")
    print(f"  Table 6 - Copper: 29.2°C")
    print(f"  Table 6 - Steel: 89.8°C") 
    print(f"  Table 8 - Copper: 45.0°C")
    print(f"  Table 8 - Steel: 85.0°C")
    
    if 'copper' in results:
        current_copper = results['copper']['corrected_temp']
        print(f"\nCurrent Copper: {current_copper:.1f}°C")
        if abs(current_copper - 29.2) < 2:
            print("  ✅ Matches Table 6 expectation (~29.2°C)")
        elif abs(current_copper - 45.0) < 2:
            print("  ⚠️  Matches Table 8 expectation (~45.0°C)")
        else:
            print(f"  ❌ Doesn't match either table expectation")
    
    if 'steel_carbon' in results:
        current_steel = results['steel_carbon']['corrected_temp']
        print(f"\nCurrent Steel Carbon: {current_steel:.1f}°C")
        if abs(current_steel - 89.8) < 2:
            print("  ✅ Matches Table 6 expectation (~89.8°C)")
        elif abs(current_steel - 85.0) < 2:
            print("  ⚠️  Matches Table 8 expectation (~85.0°C)")
        else:
            print(f"  ❌ Doesn't match either table expectation")

if __name__ == "__main__":
    check_current_table_values()