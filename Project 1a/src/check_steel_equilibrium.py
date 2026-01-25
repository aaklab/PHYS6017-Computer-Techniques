#!/usr/bin/env python3
"""
Check if steel carbon reaches steady-state in 2 seconds.
"""

import sys
sys.path.append('src')

import numpy as np
import matplotlib.pyplot as plt
from config import SimulationConfig
from simulate import MonteCarloSimulator

def check_steel_equilibration():
    """Check steel carbon equilibration behavior."""
    
    print("Checking Steel Carbon Equilibration")
    print("=" * 40)
    
    # Test steel carbon at Q=20
    config = SimulationConfig.get_material_config('steel_carbon', Q=20)
    print(f"Material: Steel Carbon")
    print(f"Thermal diffusivity: {config.alpha:.2e} m²/s")
    print(f"Move probability: {config.move_probability:.3f}")
    print(f"Simulation time: {config.t_max}s ({config.n_steps} steps)")
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
    
    print("\nTemperature Evolution Analysis:")
    print("-" * 30)
    
    # Check different time windows for steady-state
    windows = [0.5, 1.0, 1.5, 2.0]  # seconds
    
    for window_time in windows:
        # Find data points in the last 'window_time' seconds
        start_time = config.t_max - window_time
        window_mask = times >= start_time
        
        if np.sum(window_mask) > 1:
            window_temps = corrected_temps[window_mask]
            window_times = times[window_mask]
            
            mean_temp = np.mean(window_temps)
            std_temp = np.std(window_temps)
            cv = (std_temp / mean_temp) * 100 if mean_temp > 0 else 0
            
            # Calculate temperature change rate
            temp_gradient = np.gradient(window_temps, window_times[-1] - window_times[0]) if len(window_temps) > 1 else [0]
            avg_rate = np.mean(np.abs(temp_gradient))
            
            print(f"Last {window_time}s: Mean={mean_temp:.1f}°C, Std={std_temp:.2f}°C, CV={cv:.1f}%, Rate={avg_rate:.1f}°C/s")
    
    # Overall analysis
    final_temp = corrected_temps[-1]
    max_temp = np.max(corrected_temps)
    max_temp_time = times[np.argmax(corrected_temps)]
    
    print(f"\nOverall Results:")
    print(f"Final temperature: {final_temp:.1f}°C")
    print(f"Maximum temperature: {max_temp:.1f}°C at t={max_temp_time:.2f}s")
    
    # Check if still rising significantly
    last_20_percent = int(0.8 * len(corrected_temps))
    if last_20_percent < len(corrected_temps):
        late_temps = corrected_temps[last_20_percent:]
        late_times = times[last_20_percent:]
        
        if len(late_temps) > 1:
            late_gradient = np.gradient(late_temps, late_times[-1] - late_times[0])
            avg_late_rate = np.mean(late_gradient)
            
            print(f"Temperature rise rate in last 20%: {avg_late_rate:.2f}°C/s")
            
            if avg_late_rate > 1.0:
                print("⚠️  Still rising significantly - may need longer simulation")
            elif avg_late_rate > 0.1:
                print("⚠️  Still rising slowly - approaching steady-state")
            else:
                print("✅ Temperature stabilized")
    
    # Create a quick plot
    plt.figure(figsize=(10, 6))
    plt.plot(times, corrected_temps, 'b-', linewidth=2, label='Steel Carbon')
    plt.axhline(y=final_temp, color='r', linestyle='--', alpha=0.7, label=f'Final: {final_temp:.1f}°C')
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (°C)')
    plt.title('Steel Carbon Temperature Evolution (Q=20)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    # Save to appropriate folders
    import os
    reporting_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reporting")
    figures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "figures")
    os.makedirs(reporting_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    output_path = os.path.join(figures_dir, 'steel_equilibration_check.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nPlot saved as: {output_path}")
    
    return {
        'final_temp': final_temp,
        'max_temp': max_temp,
        'max_temp_time': max_temp_time,
        'times': times,
        'temperatures': corrected_temps
    }

if __name__ == "__main__":
    result = check_steel_equilibration()