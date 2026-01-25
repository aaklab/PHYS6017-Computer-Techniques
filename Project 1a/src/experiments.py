"""
Experiment definitions and execution framework.
"""

from typing import Dict, List, Any, Optional, Callable
import numpy as np
import time
import matplotlib.pyplot as plt

try:
    from .config import SimulationConfig
    from .simulate import MonteCarloSimulator
except ImportError:
    # Fallback for direct execution
    from config import SimulationConfig
    from simulate import MonteCarloSimulator


class ExperimentRunner:
    """Framework for running and managing multiple simulation experiments."""
    
    def __init__(self):
        self.experiments = {}
        self.results = {}
    
    def add_experiment(self, name: str, config: SimulationConfig, 
                      description: str = ""):
        """Add an experiment configuration."""
        self.experiments[name] = {
            'config': config,
            'description': description,
            'completed': False
        }
    
    def run_experiment(self, name: str, progress_callback: Optional[Callable] = None) -> Dict:
        """Run a single experiment."""
        if name not in self.experiments:
            raise ValueError(f"Experiment '{name}' not found")
        
        config = self.experiments[name]['config']
        print(f"\nRunning experiment: {name}")
        print(f"Description: {self.experiments[name]['description']}")
        
        # Create and run simulator
        simulator = MonteCarloSimulator(config)
        results = simulator.run(progress_callback)
        
        # Store results
        self.results[name] = results
        self.experiments[name]['completed'] = True
        
        return results
    
    def run_all_experiments(self, progress_callback: Optional[Callable] = None):
        """Run all configured experiments."""
        for name in self.experiments:
            if not self.experiments[name]['completed']:
                self.run_experiment(name, progress_callback)
    
    def compare_materials(self, materials: Dict[str, float], 
                         base_config: SimulationConfig) -> Dict:
        """Compare different materials (thermal diffusivities)."""
        print("Running material comparison study...")
        
        results = {}
        
        for material_name, alpha in materials.items():
            # Create config for this material - copy only the constructor parameters
            config_dict = {
                'Lx': base_config.Lx,
                'Ly': base_config.Ly,
                'dx': base_config.dx,
                'dt': base_config.dt,
                't_max': base_config.t_max,
                'alpha': alpha,  # Use the new alpha value
                'N_packets': base_config.N_packets,
                'random_seed': base_config.random_seed,
                'hotspot_center': base_config.hotspot_center,
                'hotspot_radius': base_config.hotspot_radius,
                'Q': base_config.Q,
                'boundary_type': base_config.boundary_type,
                'output_interval': base_config.output_interval,
                'save_snapshots': base_config.save_snapshots
            }
            
            config = SimulationConfig(**config_dict)
            
            print(f"\nTesting {material_name} (α = {alpha:.2e} m²/s)")
            
            simulator = MonteCarloSimulator(config)
            result = simulator.run()
            
            results[material_name] = {
                'config': config,
                'results': result,
                'alpha': alpha
            }
        
        # Generate comparison plots
        self._plot_material_comparison(results)
        
        return results
    
    def parameter_sweep(self, parameter_name: str, values: List[Any],
                       base_config: SimulationConfig) -> Dict:
        """Sweep a parameter across different values."""
        print(f"Running parameter sweep for {parameter_name}...")
        
        results = {}
        
        for value in values:
            print(f"\nTesting {parameter_name} = {value}")
            
            # Create config with modified parameter - copy constructor parameters
            config_dict = {
                'Lx': base_config.Lx,
                'Ly': base_config.Ly,
                'dx': base_config.dx,
                'dt': base_config.dt,
                't_max': base_config.t_max,
                'alpha': base_config.alpha,
                'N_packets': base_config.N_packets,
                'random_seed': base_config.random_seed,
                'hotspot_center': base_config.hotspot_center,
                'hotspot_radius': base_config.hotspot_radius,
                'Q': base_config.Q,
                'boundary_type': base_config.boundary_type,
                'output_interval': base_config.output_interval,
                'save_snapshots': base_config.save_snapshots
            }
            
            # Update the specific parameter
            config_dict[parameter_name] = value
            config = SimulationConfig(**config_dict)
            
            simulator = MonteCarloSimulator(config)
            result = simulator.run()
            
            results[value] = {
                'config': config,
                'results': result,
                'parameter_value': value
            }
        
        # Generate sweep plots
        self._plot_parameter_sweep(parameter_name, results)
        
        return results
    
    def convergence_study(self, packet_counts: List[int], 
                         base_config: SimulationConfig,
                         n_realizations: int = 3) -> Dict:
        """Study Monte Carlo convergence with different packet numbers."""
        print("Running Monte Carlo convergence study...")
        
        results = {}
        
        for N in packet_counts:
            print(f"\nTesting N_packets = {N}")
            
            realization_results = []
            
            for realization in range(n_realizations):
                print(f"  Realization {realization + 1}/{n_realizations}")
                
                # Create config with different packet count and seed
                config_dict = {
                    'Lx': base_config.Lx,
                    'Ly': base_config.Ly,
                    'dx': base_config.dx,
                    'dt': base_config.dt,
                    't_max': base_config.t_max,
                    'alpha': base_config.alpha,
                    'N_packets': N,  # Use the new packet count
                    'random_seed': 42 + realization,  # Different seed per realization
                    'hotspot_center': base_config.hotspot_center,
                    'hotspot_radius': base_config.hotspot_radius,
                    'Q': base_config.Q,
                    'boundary_type': base_config.boundary_type,
                    'output_interval': base_config.output_interval,
                    'save_snapshots': base_config.save_snapshots
                }
                
                config = SimulationConfig(**config_dict)
                
                simulator = MonteCarloSimulator(config)
                result = simulator.run()
                
                realization_results.append(result)
            
            results[N] = {
                'realizations': realization_results,
                'packet_count': N
            }
        
        # Analyze convergence
        convergence_analysis = self._analyze_convergence(results)
        
        # Generate convergence plots
        self._plot_convergence_study(results, convergence_analysis)
        
        return {
            'results': results,
            'analysis': convergence_analysis
        }
    
    def _analyze_convergence(self, results: Dict) -> Dict:
        """Analyze Monte Carlo convergence statistics."""
        analysis = {}
        
        for N, data in results.items():
            realizations = data['realizations']
            
            # Extract max temperatures from each realization
            max_temps = []
            for result in realizations:
                if result['metrics']:
                    max_temps.append(result['metrics']['max_temperature'])
            
            if max_temps:
                analysis[N] = {
                    'mean_max_temp': np.mean(max_temps),
                    'std_max_temp': np.std(max_temps),
                    'relative_error': np.std(max_temps) / np.mean(max_temps),
                    'theoretical_error': 1.0 / np.sqrt(N)  # Expected 1/√N scaling
                }
        
        return analysis
    
    def _plot_material_comparison(self, results: Dict):
        """Generate plots comparing different materials."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Temperature evolution comparison
        ax = axes[0, 0]
        for material, data in results.items():
            times = data['results']['data']['time']
            temps = data['results']['data']['hotspot_temperature']
            alpha = data['alpha']
            ax.plot(times, temps, label=f'{material} (α={alpha:.1e})')
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Hotspot Temperature')
        ax.set_title('Temperature Evolution Comparison')
        ax.legend()
        ax.grid(True)
        
        # Performance metrics comparison
        materials = list(results.keys())
        max_temps = [results[m]['results']['metrics']['max_temperature'] 
                    for m in materials if results[m]['results']['metrics']]
        
        ax = axes[0, 1]
        ax.bar(materials, max_temps)
        ax.set_ylabel('Max Temperature')
        ax.set_title('Maximum Temperature Comparison')
        ax.tick_params(axis='x', rotation=45)
        
        # Final temperature distributions
        for i, (material, data) in enumerate(list(results.items())[:2]):
            ax = axes[1, i]
            snapshots = data['results']['data']['temperature_snapshots']
            if snapshots:
                final_temp = snapshots[-1]
                im = ax.imshow(final_temp.T, origin='lower', cmap='hot')
                ax.set_title(f'{material} - Final Temperature')
                plt.colorbar(im, ax=ax)
        
        plt.tight_layout()
        plt.show()
    
    def _plot_parameter_sweep(self, parameter_name: str, results: Dict):
        """Generate plots for parameter sweep results."""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        values = list(results.keys())
        max_temps = []
        cooling_times = []
        final_packets = []
        
        for value in values:
            metrics = results[value]['results']['metrics']
            if metrics:
                max_temps.append(metrics['max_temperature'])
                cooling_times.append(metrics['cooling_time'] or 0)
                final_packets.append(metrics['final_active_packets'])
        
        # Max temperature vs parameter
        axes[0].plot(values, max_temps, 'o-')
        axes[0].set_xlabel(parameter_name)
        axes[0].set_ylabel('Max Temperature')
        axes[0].set_title(f'Max Temperature vs {parameter_name}')
        axes[0].grid(True)
        
        # Cooling time vs parameter
        axes[1].plot(values, cooling_times, 'o-')
        axes[1].set_xlabel(parameter_name)
        axes[1].set_ylabel('Cooling Time (s)')
        axes[1].set_title(f'Cooling Time vs {parameter_name}')
        axes[1].grid(True)
        
        # Final packets vs parameter
        axes[2].plot(values, final_packets, 'o-')
        axes[2].set_xlabel(parameter_name)
        axes[2].set_ylabel('Final Active Packets')
        axes[2].set_title(f'Final Packets vs {parameter_name}')
        axes[2].grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def _plot_convergence_study(self, results: Dict, analysis: Dict):
        """Generate plots for convergence study."""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        packet_counts = list(analysis.keys())
        mean_temps = [analysis[N]['mean_max_temp'] for N in packet_counts]
        std_temps = [analysis[N]['std_max_temp'] for N in packet_counts]
        relative_errors = [analysis[N]['relative_error'] for N in packet_counts]
        theoretical_errors = [analysis[N]['theoretical_error'] for N in packet_counts]
        
        # Convergence with error bars
        axes[0].errorbar(packet_counts, mean_temps, yerr=std_temps, 
                        fmt='o-', capsize=5)
        axes[0].set_xlabel('Number of Packets')
        axes[0].set_ylabel('Max Temperature')
        axes[0].set_title('Monte Carlo Convergence')
        axes[0].grid(True)
        
        # Error scaling
        axes[1].loglog(packet_counts, relative_errors, 'o-', label='Observed')
        axes[1].loglog(packet_counts, theoretical_errors, '--', label='1/√N theoretical')
        axes[1].set_xlabel('Number of Packets')
        axes[1].set_ylabel('Relative Error')
        axes[1].set_title('Error Scaling')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def get_experiment_summary(self) -> Dict:
        """Get summary of all experiments."""
        summary = {
            'total_experiments': len(self.experiments),
            'completed_experiments': sum(1 for exp in self.experiments.values() 
                                       if exp['completed']),
            'experiments': {}
        }
        
        for name, exp in self.experiments.items():
            summary['experiments'][name] = {
                'description': exp['description'],
                'completed': exp['completed'],
                'config_summary': str(exp['config']) if exp['config'] else None
            }
        
        return summary