"""
Signal generation module for vibration analysis.
Implements the mathematical model from the project specification.
"""

import numpy as np
from typing import Tuple, List, Optional

class VibrationSignalGenerator:
    """
    Generates vibration signals based on the model:
    x(t) = A0*sin(2π*f0*t) + Σ Ak*sin(2π*fk*t) + η(t)
    
    Where:
    - f0 is the rotation frequency
    - A0 is the fundamental amplitude
    - fk, Ak represent additional frequency components (wear)
    - η(t) is stochastic noise
    """
    
    def __init__(self, sampling_frequency: float = 1000.0):
        self.fs = sampling_frequency
        
    def generate_signal(self, 
                       duration: float,
                       rotation_freq: float,
                       fundamental_amplitude: float = 1.0,
                       wear_components: Optional[List[Tuple[float, float]]] = None,
                       noise_amplitude: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate vibration signal with specified parameters.
        
        Args:
            duration: Signal duration in seconds
            rotation_freq: Fundamental rotation frequency (f0) in Hz
            fundamental_amplitude: Amplitude of fundamental component (A0)
            wear_components: List of (frequency, amplitude) tuples for wear
            noise_amplitude: Standard deviation of Gaussian noise
            
        Returns:
            Tuple of (time_array, signal_array)
        """
        # Time vector
        N = int(self.fs * duration)
        t = np.linspace(0, duration, N, endpoint=False)
        
        # Fundamental component
        signal = fundamental_amplitude * np.sin(2 * np.pi * rotation_freq * t)
        
        # Add wear components
        if wear_components:
            for freq, amp in wear_components:
                signal += amp * np.sin(2 * np.pi * freq * t)
        
        # Add stochastic noise
        noise = np.random.normal(0, noise_amplitude, N)
        signal += noise
        
        return t, signal
    
    def generate_wear_progression(self,
                                duration: float,
                                rotation_freq: float,
                                wear_levels: List[float]) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate signals showing progression of mechanical wear.
        
        Args:
            duration: Signal duration in seconds
            rotation_freq: Fundamental rotation frequency in Hz
            wear_levels: List of wear severity levels (0 = no wear, 1 = severe)
            
        Returns:
            List of (time, signal) tuples for each wear level
        """
        signals = []
        
        for wear_level in wear_levels:
            # Define wear-related frequency components
            # Typically harmonics and sub-harmonics of rotation frequency
            wear_components = [
                (2 * rotation_freq, 0.3 * wear_level),  # 2nd harmonic
                (3 * rotation_freq, 0.2 * wear_level),  # 3rd harmonic
                (0.5 * rotation_freq, 0.15 * wear_level),  # Sub-harmonic
                (rotation_freq + 10, 0.1 * wear_level),  # Sidebands
                (rotation_freq - 10, 0.1 * wear_level)
            ]
            
            # Increase noise with wear
            noise_amp = 0.05 + 0.15 * wear_level
            
            t, signal = self.generate_signal(
                duration=duration,
                rotation_freq=rotation_freq,
                wear_components=wear_components,
                noise_amplitude=noise_amp
            )
            
            signals.append((t, signal))
            
        return signals