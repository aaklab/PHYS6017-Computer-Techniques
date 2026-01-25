#!/usr/bin/env python3
"""
Estimate runtime for regenerating all results with 10-second simulations.
"""

import sys
sys.path.append('src')

def estimate_total_runtime():
    """Estimate total runtime for all required simulations."""
    
    print("Runtime Estimation for 10-Second Simulations")
    print("=" * 50)
    
    # Performance from earlier tests
    steps_per_second = 150  # Conservative estimate from our tests
    
    # Simulation parameters
    dt = 0.002  # seconds per step
    t_max = 10.0  # simulation time
    steps_per_simulation = int(t_max / dt)  # 5000 steps
    runtime_per_simulation = steps_per_simulation / steps_per_second
    
    print(f"Per simulation:")
    print(f"  Steps needed: {steps_per_simulation}")
    print(f"  Estimated time: {runtime_per_simulation:.1f}s ({runtime_per_simulation/60:.1f} min)")
    print()
    
    # Count simulations needed for required results
    simulations = []
    
    # Figure 1: Copper heating curve (Q=20)
    simulations.append(("Figure 1", "Copper Q=20", 1))
    
    # Figure 2: Copper heat map (Q=20) - same as Figure 1, no extra simulation
    
    # Figure 3: Material comparison (Silver, Copper, Steel Carbon at Q=20)
    simulations.append(("Figure 3", "Silver Q=20", 1))
    # Copper already done for Figure 1
    simulations.append(("Figure 3", "Steel Carbon Q=20", 1))
    
    # Figure 4: Copper injection-rate dependence (Q=[5,10,15,20,25])
    # Q=20 already done for Figure 1
    simulations.append(("Figure 4", "Copper Q=5,10,15,25", 4))
    
    # Table A1: All materials, all Q values
    materials = ['silver', 'gold', 'copper', 'aluminum', 'iron', 'steel_carbon']
    Q_values = [5, 10, 15, 20, 25]
    
    # Count unique simulations (avoid double-counting)
    unique_sims = set()
    for material in materials:
        for Q in Q_values:
            unique_sims.add((material, Q))
    
    # Remove already counted simulations
    already_counted = {
        ('copper', 20),  # Figure 1
        ('silver', 20),  # Figure 3
        ('steel_carbon', 20),  # Figure 3
        ('copper', 5), ('copper', 10), ('copper', 15), ('copper', 25)  # Figure 4
    }
    
    remaining_sims = unique_sims - already_counted
    simulations.append(("Table A1", "Remaining combinations", len(remaining_sims)))
    
    # Calculate totals
    print("Simulation Breakdown:")
    print("-" * 30)
    
    total_simulations = 0
    for purpose, description, count in simulations:
        total_simulations += count
        sim_time = count * runtime_per_simulation
        print(f"{purpose:10s}: {count:2d} sims × {runtime_per_simulation:.1f}s = {sim_time:5.1f}s ({sim_time/60:.1f} min)")
    
    total_runtime = total_simulations * runtime_per_simulation
    
    print("-" * 30)
    print(f"TOTAL: {total_simulations} simulations")
    print(f"Estimated runtime: {total_runtime:.1f}s ({total_runtime/60:.1f} minutes)")
    
    # Add overhead for plotting and PDF generation
    overhead = 60  # seconds for plotting and PDF generation
    total_with_overhead = total_runtime + overhead
    
    print(f"With overhead: {total_with_overhead:.1f}s ({total_with_overhead/60:.1f} minutes)")
    
    print(f"\nBreakdown:")
    print(f"  Simulation time: {total_runtime/60:.1f} minutes")
    print(f"  Plotting/PDF: {overhead/60:.1f} minutes")
    print(f"  TOTAL: {total_with_overhead/60:.1f} minutes")
    
    return total_with_overhead

if __name__ == "__main__":
    total_time = estimate_total_runtime()
    
    print(f"\n" + "="*50)
    if total_time < 300:  # 5 minutes
        print("✅ REASONABLE - Less than 5 minutes")
    elif total_time < 600:  # 10 minutes
        print("⚠️  MODERATE - 5-10 minutes")
    else:
        print("❌ LONG - More than 10 minutes")
    
    print(f"Estimated total time: {total_time/60:.1f} minutes")