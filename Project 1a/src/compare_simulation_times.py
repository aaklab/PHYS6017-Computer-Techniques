#!/usr/bin/env python3
"""
Compare simulation times and estimate runtime for longer simulations.
"""

import sys
sys.path.append('src')

import time
from config import SimulationConfig
from simulate import MonteCarloSimulator

def estimate_simulation_times():
    """Estimate runtime for different simulation durations."""
    
    print("Simulation Time Analysis")
    print("=" * 40)
    
    # Current configuration
    current_config = SimulationConfig.get_material_config('steel_carbon', Q=20)
    print(f"Current setup:")
    print(f"  Simulation time: {current_config.t_max}s")
    print(f"  Time step: {current_config.dt}s")
    print(f"  Total steps: {current_config.n_steps}")
    print(f"  Grid size: {current_config.Nx}×{current_config.Ny}")
    print(f"  Packets: {current_config.N_packets}")
    print()
    
    # Test different simulation times
    test_times = [1.0, 2.0, 5.0]  # seconds
    runtimes = []
    
    for sim_time in test_times:
        print(f"Testing {sim_time}s simulation...")
        
        # Create config with different simulation time
        config = SimulationConfig.get_material_config('steel_carbon', Q=20, t_max=sim_time)
        
        # Time the simulation
        start_time = time.time()
        simulator = MonteCarloSimulator(config)
        result = simulator.run()
        end_time = time.time()
        
        runtime = end_time - start_time
        runtimes.append(runtime)
        
        steps_per_second = config.n_steps / runtime
        
        print(f"  Simulation time: {sim_time}s ({config.n_steps} steps)")
        print(f"  Runtime: {runtime:.2f}s")
        print(f"  Performance: {steps_per_second:.0f} steps/s")
        print(f"  Final temperature: {result['data']['hotspot_temperature'][-1]:.1f} packets")
        print()
    
    # Estimate scaling
    print("Runtime Scaling Analysis:")
    print("-" * 30)
    
    # Calculate average performance
    avg_steps_per_second = sum(
        (test_times[i] / current_config.dt) / runtimes[i] 
        for i in range(len(test_times))
    ) / len(test_times)
    
    print(f"Average performance: {avg_steps_per_second:.0f} steps/s")
    
    # Estimate for different simulation times
    target_times = [5.0, 10.0, 15.0, 20.0]
    
    for target_time in target_times:
        target_steps = int(target_time / current_config.dt)
        estimated_runtime = target_steps / avg_steps_per_second
        
        print(f"{target_time:4.1f}s simulation: {target_steps:5d} steps → ~{estimated_runtime:5.1f}s runtime ({estimated_runtime/60:.1f} min)")
    
    # Memory considerations
    print("\nMemory Considerations:")
    print("-" * 20)
    
    # Estimate data collection overhead
    output_interval = current_config.output_interval
    for target_time in target_times:
        target_steps = int(target_time / current_config.dt)
        data_points = target_steps // output_interval
        
        # Rough memory estimate (each data point ~100 bytes)
        memory_mb = data_points * 100 / (1024 * 1024)
        
        print(f"{target_time:4.1f}s: {data_points:4d} data points → ~{memory_mb:.1f} MB")
    
    return avg_steps_per_second

def quick_performance_test():
    """Quick test to measure current performance."""
    print("\nQuick Performance Test (Steel Carbon)")
    print("=" * 40)
    
    # Very short test
    config = SimulationConfig.get_material_config('steel_carbon', Q=20, t_max=0.5)
    
    start_time = time.time()
    simulator = MonteCarloSimulator(config)
    result = simulator.run()
    end_time = time.time()
    
    runtime = end_time - start_time
    steps_per_second = config.n_steps / runtime
    
    print(f"Test: {config.t_max}s simulation ({config.n_steps} steps)")
    print(f"Runtime: {runtime:.2f}s")
    print(f"Performance: {steps_per_second:.0f} steps/s")
    
    # Extrapolate to 10 seconds
    steps_10s = int(10.0 / config.dt)
    estimated_runtime_10s = steps_10s / steps_per_second
    
    print(f"\nExtrapolation to 10s:")
    print(f"  Steps needed: {steps_10s}")
    print(f"  Estimated runtime: {estimated_runtime_10s:.1f}s ({estimated_runtime_10s/60:.1f} minutes)")
    
    return steps_per_second

if __name__ == "__main__":
    # Quick test first
    performance = quick_performance_test()
    
    print("\n" + "="*50)
    
    # More detailed analysis
    avg_performance = estimate_simulation_times()
    
    print(f"\nSUMMARY:")
    print(f"Current performance: ~{performance:.0f} steps/s")
    print(f"10-second simulation would take: ~{5000/performance:.1f}s ({5000/performance/60:.1f} minutes)")