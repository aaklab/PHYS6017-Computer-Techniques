#!/usr/bin/env python3
"""
Test the shared data generation.
"""

import sys
sys.path.append('src')

from generate_required_results import generate_all_simulation_data

print("Testing shared data generation...")
data = generate_all_simulation_data()
print(f"Copper Q=20 corrected temp: {data['copper'][20]['corrected_temp']:.1f}°C")
print(f"Silver Q=20 corrected temp: {data['silver'][20]['corrected_temp']:.1f}°C")
print(f"Steel Q=20 corrected temp: {data['steel_carbon'][20]['corrected_temp']:.1f}°C")
print("✅ Shared data generation works!")