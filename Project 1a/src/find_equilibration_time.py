#!/usr/bin/env python3
"""
Find the actual equilibration time needed for steel carbon.
"""

import sys
sys.path.append('src')

import numpy as np
import matplotlib.pyplot as plt
from config import SimulationConfig
from simulate import MonteCarloSimulator

def find_steel_equilibration_time():
    """Run a long simulation to find true equilibration time for steel."""
    
    print("Finding Steel Carbon Equilibration Time")
    print("=" * 45)
    
    # Run a 15-second simulation to be sure
    config = SimulationConfig.get_material_config('steel_carbon', Q=20, t_max=15.0)
    
    print(f"Running {config.t_max}s simulation ({config.n_steps} steps)...")
    print(f"This will take approximately {config.n_steps/150:.0f} seconds...")
    print()
    
    # Run simulation
    simulator = MonteCarloSimulator(config)
    result = simulator.run()
    
    # Analyze temperature evolution
    data = result['data']
    times = np.array(data['time'])
    temps = np.array(data['hotspot_temperature'])
    
    # Apply temperature correction
    corrected_temps = [config.apply_temperature_correction(t) for t in temps]
    corrected_temps = np.array(corrected_temps)
    
    print("\nEquilibration Analysis:")
    print("-" * 25)
    
    # Find equilibration time using different criteria
    equilibration_times = {}
    
    # Criterion 1: Temperature rise rate < 0.5°C/s
    window_size = 50  # data points for moving average
    if len(corrected_temps) > window_size:
        temp_rates = []
        time_windows = []
        
        for i in range(window_size, len(corrected_temps)):
            window_temps = corrected_temps[i-window_size:i]
            window_times = times[i-window_size:i]
            
            if len(window_temps) > 1:
                rate = (window_temps[-1] - window_temps[0]) / (window_times[-1] - window_times[0])
                temp_rates.append(rate)
                time_windows.append(times[i])
        
        # Find when rate drops below 0.5°C/s
        temp_rates = np.array(temp_rates)
        time_windows = np.array(time_windows)
        
        stable_mask = np.abs(temp_rates) < 0.5
        if np.any(stable_mask):
            equilibration_times['rate_criterion'] = time_windows[stable_mask][0]
    
    # Criterion 2: Temperature within 2% of final value
    final_temp = corrected_temps[-1]
    tolerance = 0.02 * final_temp
    
    within_tolerance = np.abs(corrected_temps - final_temp) <= tolerance
    if np.any(within_tolerance):
        equilibration_times['tolerance_criterion'] = times[within_tolerance][0]
    
    # Criterion 3: Coefficient of variation < 1% in sliding window
    cv_threshold = 0.01
    window_size_cv = 100  # larger window for CV
    
    if len(corrected_temps) > window_size_cv:
        for i in range(window_size_cv, len(corrected_temps)):
            window_temps = corrected_temps[i-window_size_cv:i]
            
            if len(window_temps) > 1:
                cv = np.std(window_temps) / np.mean(window_temps)
                if cv < cv_threshold:
                    equilibration_times['cv_criterion'] = times[i]
                    break
    
    # Report results
    print(f"Final temperature: {final_temp:.1f}°C")
    print(f"Maximum temperature: {np.max(corrected_temps):.1f}°C")
    print()
    
    print("Equilibration Time Estimates:")
    for criterion, eq_time in equilibration_times.items():
        print(f"  {criterion.replace('_', ' ').title()}: {eq_time:.1f}s")
    
    # Temperature at different time points
    print(f"\nTemperature Evolution:")
    time_points = [1, 2, 5, 10, 15]
    for t in time_points:
        if t <= config.t_max:
            # Find closest time point
            idx = np.argmin(np.abs(times - t))
            temp_at_t = corrected_temps[idx]
            print(f"  At {t:2d}s: {temp_at_t:.1f}°C")
    
    # Check final stability
    last_20_percent = int(0.8 * len(corrected_temps))
    if last_20_percent < len(corrected_temps):
        late_temps = corrected_temps[last_20_percent:]
        late_times = times[last_20_percent:]
        
        late_mean = np.mean(late_temps)
        late_std = np.std(late_temps)
        late_cv = (late_std / late_mean) * 100
        
        if len(late_temps) > 1:
            late_rate = (late_temps[-1] - late_temps[0]) / (late_times[-1] - late_times[0])
            
            print(f"\nFinal Stability (last 20%):")
            print(f"  Mean temperature: {late_mean:.1f}°C")
            print(f"  Standard deviation: {late_std:.2f}°C")
            print(f"  Coefficient of variation: {late_cv:.2f}%")
            print(f"  Temperature rise rate: {late_rate:.3f}°C/s")
            
            if abs(late_rate) < 0.1:
                print("  ✅ STEADY-STATE ACHIEVED")
            elif abs(late_rate) < 0.5:
                print("  ⚠️  Nearly steady-state")
            else:
                print("  ❌ Still equilibrating")
    
    # Create detailed plot
    plt.figure(figsize=(12, 8))
    
    # Main temperature plot
    plt.subplot(2, 1, 1)
    plt.plot(times, corrected_temps, 'b-', linewidth=2, label='Steel Carbon Temperature')
    plt.axhline(y=final_temp, color='r', linestyle='--', alpha=0.7, label=f'Final: {final_temp:.1f}°C')
    
    # Mark equilibration times
    colors = ['green', 'orange', 'purple']
    for i, (criterion, eq_time) in enumerate(equilibration_times.items()):
        plt.axvline(x=eq_time, color=colors[i % len(colors)], linestyle=':', alpha=0.8, 
                   label=f'{criterion.replace("_", " ").title()}: {eq_time:.1f}s')
    
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (°C)')
    plt.title('Steel Carbon Temperature Evolution - Equilibration Analysis')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Temperature rate plot
    plt.subplot(2, 1, 2)
    if 'temp_rates' in locals():
        plt.plot(time_windows, temp_rates, 'g-', linewidth=1, label='Temperature Rate')
        plt.axhline(y=0.5, color='r', linestyle='--', alpha=0.7, label='±0.5°C/s threshold')
        plt.axhline(y=-0.5, color='r', linestyle='--', alpha=0.7)
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        
        plt.xlabel('Time (s)')
        plt.ylabel('Temperature Rate (°C/s)')
        plt.title('Temperature Change Rate')
        plt.grid(True, alpha=0.3)
        plt.legend()
    
    plt.tight_layout()
    
    # Save to appropriate folders
    import os
    reporting_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reporting")
    figures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "figures")
    os.makedirs(reporting_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    output_path = os.path.join(figures_dir, 'steel_equilibration_analysis.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nDetailed plot saved as: {output_path}")
    
    return {
        'final_temp': final_temp,
        'equilibration_times': equilibration_times,
        'times': times,
        'temperatures': corrected_temps
    }

if __name__ == "__main__":
    result = find_steel_equilibration_time()