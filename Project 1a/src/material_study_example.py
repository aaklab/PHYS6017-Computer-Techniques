#!/usr/bin/env python3
"""
Example script demonstrating material-based heat diffusion studies.
Shows how to use the new material-specific configurations.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from src.config import SimulationConfig, print_material_properties, print_standard_q_values
from src.simulate import MonteCarloSimulator

# Set matplotlib to non-interactive backend
plt.ioff()


def demonstrate_material_configs():
    """Demonstrate the new material-based configuration system."""
    
    print("="*60)
    print("MATERIAL-BASED HEAT DIFFUSION STUDY DEMONSTRATION")
    print("="*60)
    
    # Show available materials
    print_material_properties()
    print_standard_q_values()
    
    # Ensure reporting directory exists
    import os
    os.makedirs("reporting", exist_ok=True)
    
    # Create PDF for all plots
    with PdfPages('reporting/material_study_results.pdf') as pdf:
        
        print("1. SINGLE MATERIAL AT DIFFERENT HEAT INJECTION RATES")
        print("-" * 50)
        
        # Study copper at different Q values
        Q_values = [10, 20, 30]
        copper_results = {}
        
        for Q in Q_values:
            print(f"Running copper simulation with Q = {Q} packets/step...")
            
            # Create material-specific config
            config = SimulationConfig.get_material_config('copper', Q=Q)
            print(f"  {config}")
            
            # Run simulation
            simulator = MonteCarloSimulator(config)
            result = simulator.run()
            
            copper_results[Q] = {
                'config': config,
                'result': result
            }
        
        # Plot results - save to PDF
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Temperature evolution
        for Q in Q_values:
            times = copper_results[Q]['result']['data']['time']
            temps = copper_results[Q]['result']['data']['hotspot_temperature']
            ax1.plot(times, temps, linewidth=2, label=f'Q = {Q}')
        
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Hotspot Temperature')
        ax1.set_title('Copper: Temperature vs Heat Injection Rate')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Steady-state temperatures
        steady_temps = []
        for Q in Q_values:
            # Take average of last 20% of simulation as steady-state
            temps = copper_results[Q]['result']['data']['hotspot_temperature']
            steady_temp = np.mean(temps[-len(temps)//5:])
            steady_temps.append(steady_temp)
        
        ax2.plot(Q_values, steady_temps, 'ro-', linewidth=2, markersize=8)
        ax2.set_xlabel('Heat Injection Rate Q (packets/step)')
        ax2.set_ylabel('Steady-State Temperature')
        ax2.set_title('Copper: Steady-State Temperature vs Q')
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle('Page 1: Copper Heat Injection Rate Study', fontsize=14, fontweight='bold')
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
        print("\n2. MATERIAL COMPARISON AT FIXED HEAT INJECTION RATE")
        print("-" * 50)
        
        # Compare materials at fixed Q
        Q_fixed = 20
        materials = ['copper', 'aluminum', 'steel']
        material_results = {}
        
        for material in materials:
            print(f"Running {material} simulation with Q = {Q_fixed}...")
            
            config = SimulationConfig.get_material_config(material, Q=Q_fixed)
            print(f"  α = {config.alpha:.1e} m²/s")
            
            simulator = MonteCarloSimulator(config)
            result = simulator.run()
            
            material_results[material] = {
                'config': config,
                'result': result
            }
        
        # Plot material comparison - save to PDF
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Temperature evolution comparison
        colors = ['red', 'blue', 'green']
        for i, material in enumerate(materials):
            times = material_results[material]['result']['data']['time']
            temps = material_results[material]['result']['data']['hotspot_temperature']
            alpha = material_results[material]['config'].alpha
            ax1.plot(times, temps, color=colors[i], linewidth=2, 
                    label=f'{material.title()} (α={alpha:.1e})')
        
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Hotspot Temperature')
        ax1.set_title(f'Material Comparison at Q = {Q_fixed}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Steady-state comparison
        steady_temps = []
        alphas = []
        
        for material in materials:
            temps = material_results[material]['result']['data']['hotspot_temperature']
            steady_temp = np.mean(temps[-len(temps)//5:])
            steady_temps.append(steady_temp)
            alphas.append(material_results[material]['config'].alpha)
        
        bars = ax2.bar(materials, steady_temps, color=colors, alpha=0.7)
        ax2.set_ylabel('Steady-State Temperature')
        ax2.set_title(f'Steady-State Temperature Comparison (Q={Q_fixed})')
        
        # Add alpha values on bars
        for bar, alpha, temp in zip(bars, alphas, steady_temps):
            ax2.text(bar.get_x() + bar.get_width()/2, temp + 1,
                    f'α={alpha:.1e}', ha='center', va='bottom', fontsize=9)
        
        plt.suptitle('Page 2: Material Comparison Study', fontsize=14, fontweight='bold')
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
        print("\n3. COMPREHENSIVE STEADY-STATE STUDY")
        print("-" * 50)
        
        # Generate all combinations for study
        study_configs = SimulationConfig.steady_state_study_configs(
            materials=['copper', 'aluminum', 'steel'],
            Q_values=[15, 25]
        )
        
        print("Generated configurations for comprehensive study:")
        for material in study_configs:
            for Q in study_configs[material]:
                config = study_configs[material][Q]
                print(f"  {material.title()} at Q={Q}: α={config.alpha:.1e} m²/s")
    
    print(f"\nAll plots saved to: reporting/material_study_results.pdf")


def run_steady_state_analysis():
    """Run a focused steady-state analysis."""
    
    print("\n" + "="*60)
    print("FOCUSED STEADY-STATE ANALYSIS")
    print("="*60)
    
    # Test three materials at three Q values
    materials = ['copper', 'aluminum', 'steel']
    Q_values = [15, 20, 25]
    
    results = {}
    
    print("Running simulations...")
    for material in materials:
        results[material] = {}
        for Q in Q_values:
            print(f"  {material.title()} at Q={Q}...")
            
            config = SimulationConfig.get_material_config(material, Q=Q)
            simulator = MonteCarloSimulator(config)
            result = simulator.run()
            
            # Calculate steady-state temperature (last 20% of simulation)
            temps = result['data']['hotspot_temperature']
            steady_temp = np.mean(temps[-len(temps)//5:])
            
            results[material][Q] = {
                'steady_temp': steady_temp,
                'max_temp': result['metrics']['max_temperature'],
                'alpha': config.alpha
            }
    
    # Create summary plot and save to PDF
    with PdfPages('reporting/steady_state_analysis.pdf') as pdf:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        colors = ['red', 'blue', 'green']
        for i, material in enumerate(materials):
            steady_temps = [results[material][Q]['steady_temp'] for Q in Q_values]
            ax.plot(Q_values, steady_temps, 'o-', color=colors[i], 
                    linewidth=2, markersize=8, label=f'{material.title()}')
        
        ax.set_xlabel('Heat Injection Rate Q (packets/step)')
        ax.set_ylabel('Steady-State Temperature')
        ax.set_title('Steady-State Temperature vs Heat Injection Rate')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add thermal diffusivity info
        info_text = "Thermal Diffusivities:\n"
        for material in materials:
            alpha = results[material][Q_values[0]]['alpha']
            info_text += f"{material.title()}: {alpha:.1e} m²/s\n"
        
        ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    
    print(f"Steady-state analysis plot saved to: reporting/steady_state_analysis.pdf")
    
    # Print summary table
    print("\nSteady-State Temperature Summary:")
    print("=" * 60)
    print(f"{'Material':<12} {'α (m²/s)':<12} {'Q=15':<8} {'Q=20':<8} {'Q=25':<8}")
    print("-" * 60)
    
    for material in materials:
        alpha = results[material][Q_values[0]]['alpha']
        temps = [f"{results[material][Q]['steady_temp']:.1f}" for Q in Q_values]
        print(f"{material.title():<12} {alpha:<12.1e} {temps[0]:<8} {temps[1]:<8} {temps[2]:<8}")


if __name__ == "__main__":
    # Run demonstrations
    demonstrate_material_configs()
    run_steady_state_analysis()
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETED")
    print("="*60)
    print("\nPDF files generated:")
    print("1. reporting/material_study_results.pdf - Material comparison and Q studies")
    print("2. reporting/steady_state_analysis.pdf - Comprehensive steady-state analysis")
    print("\nKey takeaways:")
    print("1. Use SimulationConfig.get_material_config(material, Q) for single configs")
    print("2. Use SimulationConfig.steady_state_study_configs() for comprehensive studies")
    print("3. Use SimulationConfig.material_comparison_config(Q) for material comparison")
    print("4. All other parameters are fixed for consistent comparison")
    print("5. Higher thermal diffusivity → better heat spreading → lower temperatures")
    print("6. All plots are saved to PDF files, not displayed on screen")