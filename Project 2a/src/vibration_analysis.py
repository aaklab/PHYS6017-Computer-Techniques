"""
Core vibration analysis module implementing signal processing techniques
for mechanical wear detection.
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq
from typing import Tuple, Optional

class VibrationAnalyzer:
    """
    Implements computational methods for vibration signal analysis including
    FFT, digital filtering, and quantitative indicators.
    """
    
    def __init__(self, sampling_frequency: float):
        self.fs = sampling_frequency
    
    def preprocess_signal(self, 
                         signal_data: np.ndarray, 
                         remove_mean: bool = True,
                         window_function: Optional[str] = None) -> np.ndarray:
        """
        Pre-process signal by removing mean and applying window function.
        
        Args:
            signal_data: Input signal array
            remove_mean: Whether to remove DC component
            window_function: Window type ('hann', 'hamming', 'blackman', etc.)
            
        Returns:
            Preprocessed signal
        """
        processed = signal_data.copy()
        
        if remove_mean:
            processed = processed - np.mean(processed)
        
        if window_function:
            window = signal.get_window(window_function, len(processed))
            processed = processed * window
            
        return processed
    
    def compute_fft(self, signal_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute FFT and return frequency and magnitude spectrum.
        
        Args:
            signal_data: Input signal
            
        Returns:
            Tuple of (frequencies, magnitude_spectrum)
        """
        N = len(signal_data)
        
        # Compute FFT
        fft_result = fft(signal_data)
        frequencies = fftfreq(N, 1/self.fs)
        
        # Take positive frequencies only
        positive_freq_idx = frequencies >= 0
        frequencies = frequencies[positive_freq_idx]
        magnitude = np.abs(fft_result[positive_freq_idx])
        
        return frequencies, magnitude
    
    def apply_filter(self, 
                    signal_data: np.ndarray,
                    filter_type: str,
                    cutoff_freq: float,
                    order: int = 4) -> np.ndarray:
        """
        Apply digital filter to isolate frequency regions of interest.
        
        Args:
            signal_data: Input signal
            filter_type: 'lowpass', 'highpass', or 'bandpass'
            cutoff_freq: Cutoff frequency (or tuple for bandpass)
            order: Filter order
            
        Returns:
            Filtered signal
        """
        nyquist = self.fs / 2
        
        if filter_type == 'lowpass':
            sos = signal.butter(order, cutoff_freq/nyquist, btype='low', output='sos')
        elif filter_type == 'highpass':
            sos = signal.butter(order, cutoff_freq/nyquist, btype='high', output='sos')
        elif filter_type == 'bandpass':
            if isinstance(cutoff_freq, (list, tuple)) and len(cutoff_freq) == 2:
                low, high = cutoff_freq
                sos = signal.butter(order, [low/nyquist, high/nyquist], 
                                  btype='band', output='sos')
            else:
                raise ValueError("Bandpass filter requires two cutoff frequencies")
        else:
            raise ValueError("Filter type must be 'lowpass', 'highpass', or 'bandpass'")
        
        filtered_signal = signal.sosfilt(sos, signal_data)
        return filtered_signal
    
    def compute_rms(self, signal_data: np.ndarray) -> float:
        """
        Compute Root Mean Square (RMS) vibration amplitude.
        
        Args:
            signal_data: Input signal
            
        Returns:
            RMS value
        """
        return np.sqrt(np.mean(signal_data**2))
    
    def compute_band_power(self, 
                          frequencies: np.ndarray, 
                          magnitude: np.ndarray,
                          freq_band: Tuple[float, float]) -> float:
        """
        Compute power in a specific frequency band.
        
        Args:
            frequencies: Frequency array from FFT
            magnitude: Magnitude spectrum from FFT
            freq_band: Tuple of (low_freq, high_freq)
            
        Returns:
            Band-limited power
        """
        low_freq, high_freq = freq_band
        band_mask = (frequencies >= low_freq) & (frequencies <= high_freq)
        
        if not np.any(band_mask):
            return 0.0
        
        # Power is proportional to magnitude squared
        power_spectrum = magnitude**2
        band_power = np.sum(power_spectrum[band_mask])
        
        return band_power
    
    def detect_peaks(self, 
                    frequencies: np.ndarray, 
                    magnitude: np.ndarray,
                    height_threshold: Optional[float] = None,
                    prominence: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect peaks in frequency spectrum for wear-related features.
        
        Args:
            frequencies: Frequency array
            magnitude: Magnitude spectrum
            height_threshold: Minimum peak height
            prominence: Minimum peak prominence
            
        Returns:
            Tuple of (peak_frequencies, peak_magnitudes)
        """
        peak_indices, _ = signal.find_peaks(magnitude, 
                                          height=height_threshold,
                                          prominence=prominence)
        
        peak_frequencies = frequencies[peak_indices]
        peak_magnitudes = magnitude[peak_indices]
        
        return peak_frequencies, peak_magnitudes
    
    def analyze_wear_indicators(self, 
                              signal_data: np.ndarray,
                              rotation_freq: float) -> dict:
        """
        Comprehensive analysis to extract wear-related indicators.
        
        Args:
            signal_data: Input vibration signal
            rotation_freq: Fundamental rotation frequency
            
        Returns:
            Dictionary of wear indicators
        """
        # Preprocess signal
        processed_signal = self.preprocess_signal(signal_data, window_function='hann')
        
        # Compute FFT
        frequencies, magnitude = self.compute_fft(processed_signal)
        
        # Overall RMS
        overall_rms = self.compute_rms(signal_data)
        
        # Band-limited analysis
        fundamental_band = (rotation_freq - 2, rotation_freq + 2)
        harmonic_band = (2*rotation_freq - 5, 3*rotation_freq + 5)
        high_freq_band = (100, self.fs/2 - 50)
        
        fundamental_power = self.compute_band_power(frequencies, magnitude, fundamental_band)
        harmonic_power = self.compute_band_power(frequencies, magnitude, harmonic_band)
        high_freq_power = self.compute_band_power(frequencies, magnitude, high_freq_band)
        
        # Peak detection
        peak_freqs, peak_mags = self.detect_peaks(frequencies, magnitude, 
                                                prominence=np.max(magnitude)*0.1)
        
        return {
            'overall_rms': overall_rms,
            'fundamental_power': fundamental_power,
            'harmonic_power': harmonic_power,
            'high_frequency_power': high_freq_power,
            'harmonic_ratio': harmonic_power / (fundamental_power + 1e-10),
            'high_freq_ratio': high_freq_power / (fundamental_power + 1e-10),
            'peak_count': len(peak_freqs),
            'frequencies': frequencies,
            'magnitude': magnitude,
            'peak_frequencies': peak_freqs,
            'peak_magnitudes': peak_mags
        }