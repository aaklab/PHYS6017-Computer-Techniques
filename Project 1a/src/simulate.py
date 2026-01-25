"""
Main Monte Carlo simulation engine.
"""

import time
from typing import Dict, List, Optional
import numpy as np

try:
    from .config import SimulationConfig
    from .model import HeatSink
    from .rng import ReproducibleRNG
    from .observables import ObservableCollector
except ImportError:
    # Fallback for direct execution
    from config import SimulationConfig
    from model import HeatSink
    from rng import ReproducibleRNG
    from observables import ObservableCollector


class MonteCarloSimulator:
    """Main Monte Carlo heat diffusion simulator."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.heat_sink = HeatSink(config)
        self.rng_manager = ReproducibleRNG(config.random_seed or 42)
        self.observable_collector = ObservableCollector(config)
        
        # Simulation state
        self.current_step = 0
        self.current_time = 0.0
        self.is_running = False
        self.start_time = None
        self.end_time = None
    
    def initialize(self):
        """Initialize simulation to starting state."""
        self.heat_sink.reset()
        self.rng_manager.reset_all()
        self.observable_collector.reset()
        
        # CRITICAL FIX: Place initial packets in hotspot
        self._seed_initial_packets()
        
        self.current_step = 0
        self.current_time = 0.0
        self.is_running = False
        
        print(f"Simulation initialized:")
        print(f"  {self.config}")
    
    def _seed_initial_packets(self):
        """Place initial heat packets in the hotspot region."""
        injection_rng = self.rng_manager.get_injection_rng()
        
        # Add initial packets to establish baseline temperature
        initial_packets = max(1, int(self.config.N_packets * 0.1))  # 10% of total packets
        
        for _ in range(initial_packets):
            x, y = self.heat_sink.grid.get_random_hotspot_position(injection_rng)
            self.heat_sink.packet_manager.add_packet(x, y)
        
        print(f"Seeded {initial_packets} initial packets in hotspot")
    
    def step(self) -> Dict:
        """Perform single simulation time step."""
        if not self.is_running:
            raise RuntimeError("Simulation not started. Call run() first.")
        
        # Get appropriate RNGs
        injection_rng = self.rng_manager.get_injection_rng()
        packet_rng = self.rng_manager.get_packet_rng()
        
        # Step 4a: Inject heat packets
        injected = self.heat_sink.inject_heat_packets(injection_rng)
        
        # Step 4b: Random-walk update
        removed = self.heat_sink.move_packets(packet_rng)
        
        # Step 4c: Apply boundary conditions (handled in move_packets)
        
        # Step 4d: Record observables
        observables = self.heat_sink.get_observables()
        
        # Collect data if needed
        if self.current_step % self.config.output_interval == 0:
            self.observable_collector.collect(
                step=self.current_step,
                time=self.current_time,
                observables=observables,
                temperature_field=self.heat_sink.get_temperature_field() if self.config.save_snapshots else None
            )
        
        # Update simulation state
        self.current_step += 1
        self.current_time = self.current_step * self.config.dt
        
        # Return step summary
        return {
            'step': self.current_step,
            'time': self.current_time,
            'injected': injected,
            'removed': removed,
            'active_packets': observables['active_packets'],
            'hotspot_temp': observables['hotspot_temperature']
        }
    
    def run(self, progress_callback: Optional[callable] = None) -> Dict:
        """Run complete simulation."""
        self.initialize()
        
        print(f"Starting simulation: {self.config.n_steps} steps...")
        self.start_time = time.time()
        self.is_running = True
        
        try:
            # Main simulation loop
            for step in range(self.config.n_steps):
                step_result = self.step()
                
                # Progress reporting
                if progress_callback:
                    progress_callback(step_result)
                elif step % (self.config.n_steps // 10) == 0:
                    self._default_progress_report(step_result)
            
            self.is_running = False
            self.end_time = time.time()
            
            # Final summary
            results = self._compile_results()
            self._print_final_summary(results)
            
            return results
            
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user.")
            self.is_running = False
            return self._compile_results()
        
        except Exception as e:
            print(f"\nSimulation failed with error: {e}")
            self.is_running = False
            raise
    
    def run_until_condition(self, condition_func: callable, max_steps: Optional[int] = None) -> Dict:
        """Run simulation until specified condition is met."""
        self.initialize()
        
        max_steps = max_steps or self.config.n_steps
        print(f"Running simulation until condition met (max {max_steps} steps)...")
        
        self.start_time = time.time()
        self.is_running = True
        
        try:
            for step in range(max_steps):
                step_result = self.step()
                
                # Check termination condition
                if condition_func(step_result, self.observable_collector.get_data()):
                    print(f"Condition met at step {step}")
                    break
                
                # Progress reporting
                if step % (max_steps // 20) == 0:
                    self._default_progress_report(step_result)
            
            self.is_running = False
            self.end_time = time.time()
            
            return self._compile_results()
            
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user.")
            self.is_running = False
            return self._compile_results()
    
    def _default_progress_report(self, step_result: Dict):
        """Default progress reporting."""
        progress = (step_result['step'] / self.config.n_steps) * 100
        print(f"Step {step_result['step']:6d}/{self.config.n_steps} ({progress:5.1f}%) | "
              f"Active: {step_result['active_packets']:5d} | "
              f"Hotspot T: {step_result['hotspot_temp']:6.2f} | "
              f"Time: {step_result['time']:6.3f}s")
    
    def _compile_results(self) -> Dict:
        """Compile final simulation results."""
        data = self.observable_collector.get_data()
        
        # Calculate performance metrics
        metrics = self._calculate_performance_metrics(data)
        
        # Simulation metadata
        runtime = (self.end_time - self.start_time) if (self.start_time and self.end_time) else None
        
        return {
            'config': self.config.to_dict(),
            'data': data,
            'metrics': metrics,
            'metadata': {
                'completed_steps': self.current_step,
                'final_time': self.current_time,
                'runtime_seconds': runtime,
                'rng_state': self.rng_manager.get_state_summary(),
                'heat_sink_stats': self.heat_sink.get_statistics_summary()
            }
        }
    
    def _calculate_performance_metrics(self, data: Dict) -> Dict:
        """Calculate heat sink performance metrics."""
        if not data['hotspot_temperature']:
            return {}
        
        hotspot_temps = np.array(data['hotspot_temperature'])
        times = np.array(data['time'])
        
        # Maximum temperature reached
        max_temp = np.max(hotspot_temps)
        max_temp_time = times[np.argmax(hotspot_temps)]
        
        # Cooling time (time to decrease by 1/e from maximum)
        cooling_threshold = max_temp / np.e
        cooling_time = None
        
        # Find when temperature drops below threshold after reaching maximum
        max_idx = np.argmax(hotspot_temps)
        if max_idx < len(hotspot_temps) - 1:
            post_max_temps = hotspot_temps[max_idx:]
            post_max_times = times[max_idx:]
            
            below_threshold = post_max_temps <= cooling_threshold
            if np.any(below_threshold):
                cooling_idx = np.where(below_threshold)[0][0]
                cooling_time = post_max_times[cooling_idx] - post_max_times[0]
        
        # Spatial uniformity (from final temperature field)
        final_temp_field = data['temperature_snapshots'][-1] if data['temperature_snapshots'] else None
        spatial_uniformity = np.std(final_temp_field) if final_temp_field is not None else None
        
        # Steady-state analysis (last 20% of simulation)
        steady_start_idx = int(0.8 * len(hotspot_temps))
        steady_temps = hotspot_temps[steady_start_idx:]
        steady_state_temp = np.mean(steady_temps) if len(steady_temps) > 0 else None
        steady_state_std = np.std(steady_temps) if len(steady_temps) > 0 else None
        
        return {
            'max_temperature': max_temp,
            'max_temperature_time': max_temp_time,
            'cooling_time': cooling_time,
            'spatial_uniformity': spatial_uniformity,
            'steady_state_temperature': steady_state_temp,
            'steady_state_fluctuation': steady_state_std,
            'final_active_packets': data['active_packets'][-1] if data['active_packets'] else 0
        }
    
    def _print_final_summary(self, results: Dict):
        """Print final simulation summary."""
        metadata = results['metadata']
        metrics = results['metrics']
        
        print("\n" + "="*60)
        print("SIMULATION COMPLETED")
        print("="*60)
        print(f"Steps completed: {metadata['completed_steps']}")
        print(f"Simulation time: {metadata['final_time']:.3f}s")
        print(f"Runtime: {metadata['runtime_seconds']:.2f}s")
        
        if metrics:
            print(f"\nPerformance Metrics:")
            print(f"  Max temperature: {metrics['max_temperature']:.2f}")
            print(f"  Cooling time: {metrics['cooling_time']:.3f}s" if metrics['cooling_time'] else "  Cooling time: Not reached")
            print(f"  Spatial uniformity: {metrics['spatial_uniformity']:.2f}" if metrics['spatial_uniformity'] else "  Spatial uniformity: N/A")
            print(f"  Final active packets: {metrics['final_active_packets']}")
    
    def get_current_state(self) -> Dict:
        """Get current simulation state."""
        return {
            'step': self.current_step,
            'time': self.current_time,
            'is_running': self.is_running,
            'observables': self.heat_sink.get_observables() if self.is_running else None
        }