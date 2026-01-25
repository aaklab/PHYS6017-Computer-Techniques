#!/usr/bin/env python3
"""
Test steel carbon equilibrium vs Table 6 values.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
from config import SimulationConfig
from simulate import MonteCarloSimulator

print('STEEL CARBON EQUILIBRIUM TEST')
print('='*35)

# Test steel carbon at Q=20 for full equilibration
config = SimulationConfig.get_material_config('steel_carbon', Q=20)
print(f'Running steel carbon for {config.t_max}s (full equilibration)')
print('This will take a while...')

simulator = MonteCarloSimulator(config)
result = simulator.run()

temps = np.array(result['data']['hotspot_temperature'])
times = np.array(result['data']['time'])

# Find temperature at different time points
t_2s_idx = np.argmin(np.abs(times - 2.0))
temp_at_2s = temps[t_2s_idx]
temp_final = np.mean(temps[-10:])  # Average of last 10 points

print(f'\nResults:')
print(f'Temperature at t=2.0s: {temp_at_2s:.1f}')
print(f'Temperature at t={times[-1]:.1f}s: {temp_final:.1f}')
print(f'\nTable 6 value: 237.1')
print(f'Difference at 2s: {temp_at_2s - 237.1:+.1f}')
print(f'Difference at equilibrium: {temp_final - 237.1:+.1f}')

print(f'\nCONCLUSION:')
if abs(temp_at_2s - 237.1) < 5:
    print('✓ Table 6 values appear to be at t=2s (intermediate values)')
else:
    print('✗ Table 6 values do not match t=2s')

if abs(temp_final - 237.1) < 5:
    print('✓ Table 6 values are true steady-state values')
else:
    print('✗ Table 6 values are NOT true steady-state values')
    print(f'  True steady-state is {temp_final:.1f}, not 237.1')