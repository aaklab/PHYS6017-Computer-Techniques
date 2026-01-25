"""
Data collection and observable calculation for the simulation.
"""

from typing import Dict, List, Optional, Any
import numpy as np

try:
    from .config import SimulationConfig
except ImportError:
    # Fallback for direct execution
    from config import SimulationConfig


class ObservableCollector:
    """Collects and manages observable data during simulation."""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.reset()
    
    def reset(self):
        """Reset all collected data."""
        # Time series data
        self.steps: List[int] = []
        self.times: List[float] = []
        
        # Primary observables
        self.hotspot_temperature: List[float] = []
        self.active_packets: List[int] = []
        
        # Temperature field statistics
        self.temp_mean: List[float] = []
        self.temp_std: List[float] = []
        self.temp_max: List[float] = []
        self.temp_min: List[float] = []
        
        # Packet statistics
        self.total_injected: List[int] = []
        self.total_removed: List[int] = []
        self.total_convected: List[int] = []  # Track convection losses
        
        # Temperature field snapshots (if enabled)
        self.temperature_snapshots: List[np.ndarray] = []
        self.snapshot_times: List[float] = []
    
    def collect(self, step: int, time: float, observables: Dict, 
                temperature_field: Optional[np.ndarray] = None):
        """Collect observables at current time step."""
        
        # Basic time information
        self.steps.append(step)
        self.times.append(time)
        
        # Primary observables
        self.hotspot_temperature.append(observables['hotspot_temperature'])
        self.active_packets.append(observables['active_packets'])
        
        # Temperature statistics
        temp_stats = observables['temperature_stats']
        self.temp_mean.append(temp_stats['mean'])
        self.temp_std.append(temp_stats['std'])
        self.temp_max.append(temp_stats['max'])
        self.temp_min.append(temp_stats['min'])
        
        # Packet statistics
        self.total_injected.append(observables['total_injected'])
        self.total_removed.append(observables['total_removed'])
        self.total_convected.append(observables.get('total_convected', 0))  # Handle missing key gracefully
        
        # Temperature field snapshots
        if temperature_field is not None:
            self.temperature_snapshots.append(temperature_field.copy())
            self.snapshot_times.append(time)
    
    def get_data(self) -> Dict:
        """Get all collected data as dictionary."""
        return {
            'steps': self.steps,
            'time': self.times,
            'hotspot_temperature': self.hotspot_temperature,
            'active_packets': self.active_packets,
            'temperature_mean': self.temp_mean,
            'temperature_std': self.temp_std,
            'temperature_max': self.temp_max,
            'temperature_min': self.temp_min,
            'total_injected': self.total_injected,
            'total_removed': self.total_removed,
            'total_convected': self.total_convected,
            'temperature_snapshots': self.temperature_snapshots,
            'snapshot_times': self.snapshot_times
        }
    
    def get_arrays(self) -> Dict[str, np.ndarray]:
        """Get data as numpy arrays for analysis."""
        data = self.get_data()
        arrays = {}
        
        for key, values in data.items():
            if key not in ['temperature_snapshots']:  # Skip 3D arrays
                arrays[key] = np.array(values)
        
        # Handle temperature snapshots separately
        if self.temperature_snapshots:
            arrays['temperature_snapshots'] = np.array(self.temperature_snapshots)
        
        return arrays
    
    def calculate_derived_observables(self) -> Dict:
        """Calculate derived observables from collected data."""
        if not self.times:
            return {}
        
        arrays = self.get_arrays()
        
        # Time derivatives
        dt_avg = np.mean(np.diff(arrays['time'])) if len(arrays['time']) > 1 else self.config.dt
        
        # Temperature evolution metrics
        hotspot_temp = arrays['hotspot_temperature']
        
        # Peak temperature and time
        max_temp_idx = np.argmax(hotspot_temp)
        peak_temperature = hotspot_temp[max_temp_idx]
        peak_time = arrays['time'][max_temp_idx]
        
        # Temperature gradients
        temp_gradient = np.gradient(hotspot_temp, dt_avg) if len(hotspot_temp) > 1 else np.array([0])
        max_heating_rate = np.max(temp_gradient)
        max_cooling_rate = np.min(temp_gradient)
        
        # Packet flow analysis
        net_packets = arrays['total_injected'] - arrays['total_removed']
        packet_accumulation_rate = np.gradient(net_packets, dt_avg) if len(net_packets) > 1 else np.array([0])
        
        # Steady-state analysis (last 20% of simulation)
        steady_start = int(0.8 * len(hotspot_temp))
        if steady_start < len(hotspot_temp):
            steady_temp = hotspot_temp[steady_start:]
            steady_state_mean = np.mean(steady_temp)
            steady_state_std = np.std(steady_temp)
            
            # Check for steady state (coefficient of variation < 5%)
            is_steady_state = (steady_state_std / steady_state_mean) < 0.05 if steady_state_mean > 0 else False
        else:
            steady_state_mean = hotspot_temp[-1] if len(hotspot_temp) > 0 else 0
            steady_state_std = 0
            is_steady_state = False
        
        # Cooling time constants
        cooling_times = self._calculate_cooling_times(arrays['time'], hotspot_temp)
        
        return {
            'peak_temperature': peak_temperature,
            'peak_time': peak_time,
            'max_heating_rate': max_heating_rate,
            'max_cooling_rate': abs(max_cooling_rate),
            'steady_state_temperature': steady_state_mean,
            'steady_state_fluctuation': steady_state_std,
            'is_steady_state': is_steady_state,
            'cooling_times': cooling_times,
            'final_net_packets': net_packets[-1] if len(net_packets) > 0 else 0,
            'avg_packet_accumulation_rate': np.mean(packet_accumulation_rate)
        }
    
    def _calculate_cooling_times(self, times: np.ndarray, temperatures: np.ndarray) -> Dict:
        """Calculate various cooling time constants."""
        if len(temperatures) < 2:
            return {}
        
        max_idx = np.argmax(temperatures)
        max_temp = temperatures[max_idx]
        max_time = times[max_idx]
        
        # Only analyze cooling after peak
        if max_idx >= len(temperatures) - 1:
            return {'peak_reached_at_end': True}
        
        post_peak_temps = temperatures[max_idx:]
        post_peak_times = times[max_idx:]
        
        cooling_times = {}
        
        # Different cooling thresholds
        thresholds = {
            'e_fold': max_temp / np.e,  # 1/e cooling time
            'half_life': max_temp / 2,   # Half-life
            'quarter': max_temp / 4,     # Quarter temperature
            'ten_percent': max_temp * 0.1  # 10% of peak
        }
        
        for name, threshold in thresholds.items():
            below_threshold = post_peak_temps <= threshold
            if np.any(below_threshold):
                cooling_idx = np.where(below_threshold)[0][0]
                cooling_time = post_peak_times[cooling_idx] - max_time
                cooling_times[f'{name}_time'] = cooling_time
        
        return cooling_times
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics of all observables."""
        if not self.times:
            return {}
        
        arrays = self.get_arrays()
        summary = {}
        
        # Statistics for each observable
        for key, values in arrays.items():
            if key in ['temperature_snapshots', 'steps']:
                continue
            
            if len(values) > 0:
                summary[key] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'final': values[-1]
                }
        
        # Add derived observables
        derived = self.calculate_derived_observables()
        summary['derived'] = derived
        
        return summary
    
    def export_data(self, filename: str, format: str = 'npz'):
        """Export collected data to file."""
        data = self.get_data()
        
        if format == 'npz':
            # Save as compressed numpy archive
            arrays = self.get_arrays()
            np.savez_compressed(filename, **arrays)
        
        elif format == 'csv':
            # Save time series data as CSV
            import pandas as pd
            
            # Create DataFrame with time series data
            df_data = {
                'step': self.steps,
                'time': self.times,
                'hotspot_temperature': self.hotspot_temperature,
                'active_packets': self.active_packets,
                'temperature_mean': self.temp_mean,
                'temperature_std': self.temp_std,
                'temperature_max': self.temp_max,
                'temperature_min': self.temp_min,
                'total_injected': self.total_injected,
                'total_removed': self.total_removed,
                'total_convected': self.total_convected
            }
            
            df = pd.DataFrame(df_data)
            df.to_csv(filename, index=False)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def load_data(self, filename: str, format: str = 'npz'):
        """Load data from file."""
        if format == 'npz':
            loaded = np.load(filename)
            
            # Restore lists from arrays
            self.steps = loaded['steps'].tolist()
            self.times = loaded['time'].tolist()
            self.hotspot_temperature = loaded['hotspot_temperature'].tolist()
            self.active_packets = loaded['active_packets'].tolist()
            self.temp_mean = loaded['temperature_mean'].tolist()
            self.temp_std = loaded['temperature_std'].tolist()
            self.temp_max = loaded['temperature_max'].tolist()
            self.temp_min = loaded['temperature_min'].tolist()
            self.total_injected = loaded['total_injected'].tolist()
            self.total_removed = loaded['total_removed'].tolist()
            self.total_convected = loaded.get('total_convected', []).tolist()  # Handle missing key
            
            # Handle snapshots if present
            if 'temperature_snapshots' in loaded:
                self.temperature_snapshots = [snap for snap in loaded['temperature_snapshots']]
                self.snapshot_times = loaded['snapshot_times'].tolist()
        
        else:
            raise ValueError(f"Unsupported load format: {format}")