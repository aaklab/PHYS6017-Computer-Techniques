#!/usr/bin/env python3
"""
Create a comprehensive PDF report combining all figures, plots, and parameter tables.
This creates a complete documentation of the vibration analysis project.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# Import from same directory (src)
from signal_generator import VibrationSignalGenerator
from vibration_analysis import VibrationAnalyzer

def create_complete_report():
    """Create comprehensive report with all figures and tables."""
    
    print("Creating comprehensive vibration analysis report...")
    
    # Ensure reporting directory exists in the parent directory (Project 2a root)
    import os
    reporting_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reporting")
    os.makedirs(reporting_dir, exist_ok=True)
    
    # Set matplotlib parameters for high-quality output
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['figure.figsize'] = (12, 8)
    
    # Initialize components
    fs = 1000
    generator = VibrationSignalGenerator(sampling_frequency=fs)
    analyzer = VibrationAnalyzer(sampling_frequency=fs)
    
    # Signal parameters
    duration = 2.0
    rotation_freq = 25.0
    wear_levels = [0.0, 0.3, 0.7, 1.0]
    wear_labels = ['Initial State', 'Light Wear', 'Moderate Wear', 'Severe Wear']
    
    print("Generating signals and analyzing data...")
    signals = generator.generate_wear_progression(duration, rotation_freq, wear_levels)
    
    # Analyze all signals for tables
    results = []
    for i, (t, signal) in enumerate(signals):
        indicators = analyzer.analyze_wear_indicators(signal, rotation_freq)
        results.append({
            'wear_level': wear_levels[i],
            'rms': indicators['overall_rms'],
            'harmonic_ratio': indicators['harmonic_ratio'],
            'hf_ratio': indicators['high_freq_ratio'],
            'peak_count': indicators['peak_count'],
            'fundamental_power': indicators['fundamental_power'],
            'harmonic_power': indicators['harmonic_power'],
            'hf_power': indicators['high_frequency_power']
        })
    
    pdf_filename = os.path.join(reporting_dir, 'complete_vibration_analysis_report.pdf')
    print(f"Creating comprehensive PDF: {pdf_filename}")
    
    with PdfPages(pdf_filename) as pdf:
        
        # TITLE PAGE
        print("Creating title page...")
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        
        # Title and header
        plt.figtext(0.5, 0.85, 'Vibration Signal Analysis', ha='center', fontsize=24, fontweight='bold')
        plt.figtext(0.5, 0.80, 'Early Detection of Mechanical Wear in Rotating Machinery', ha='center', fontsize=16)
        plt.figtext(0.5, 0.75, 'Complete Analysis Report', ha='center', fontsize=14, style='italic')
        
        # Project details
        plt.figtext(0.5, 0.65, 'PHYS6017 - Computer Techniques for Physics', ha='center', fontsize=14, fontweight='bold')
        plt.figtext(0.5, 0.60, 'Assignment Two', ha='center', fontsize=12)
        plt.figtext(0.5, 0.55, f'Generated: December 30, 2025', ha='center', fontsize=10)
        
        # Contents
        plt.figtext(0.1, 0.45, 'Report Contents:', fontsize=14, fontweight='bold')
        contents = [
            '1. Parameter Settings and Configuration Tables',
            '2. Time Domain Signal Analysis',
            '3. Frequency Domain Analysis (FFT)',
            '4. Digital Filtering Demonstration',
            '5. Quantitative Wear Progression Indicators',
            '6. Detailed Frequency Comparison',
            '7. Parameter Sensitivity Analysis',
            '8. Computational Methods Summary',
            '9. Performance Metrics and Validation'
        ]
        
        for i, item in enumerate(contents):
            plt.figtext(0.15, 0.40 - i*0.03, item, fontsize=11)
        
        # Summary box
        plt.figtext(0.1, 0.15, 'Key Findings:', fontsize=12, fontweight='bold')
        plt.figtext(0.1, 0.11, '• RMS amplitude increases systematically with wear progression', fontsize=10)
        plt.figtext(0.1, 0.08, '• Harmonic content shows dramatic growth (>10x increase)', fontsize=10)
        plt.figtext(0.1, 0.05, '• High-frequency content indicates surface degradation', fontsize=10)
        plt.figtext(0.1, 0.02, '• Frequency-domain analysis enables early fault detection', fontsize=10)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 1: PARAMETER TABLES
        print("Creating parameter tables...")
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('tight')
        ax.axis('off')
        
        # Main parameters table
        main_params = [
            ['Parameter', 'Symbol', 'Value', 'Units', 'Description'],
            ['Sampling Frequency', 'fs', '1000', 'Hz', 'Digital sampling rate'],
            ['Signal Duration', 'T', '2.0', 's', 'Length of each signal'],
            ['Number of Samples', 'N', '2000', '-', 'fs × T'],
            ['Rotation Frequency', 'f₀', '25.0', 'Hz', 'Fundamental frequency (1500 RPM)'],
            ['Fundamental Amplitude', 'A₀', '1.0', '-', 'Base vibration amplitude'],
            ['Noise Amplitude', 'σ', '0.05-0.25', '-', 'Gaussian noise std deviation'],
            ['Wear Levels Tested', '-', '0.0, 0.3, 0.7, 1.0', '-', 'Dimensionless wear severity'],
            ['Filter Order', '-', '4', '-', 'Butterworth filter order'],
            ['Low-pass Cutoff', 'fc_low', '50', 'Hz', 'Low-pass filter frequency'],
            ['High-pass Cutoff', 'fc_high', '50', 'Hz', 'High-pass filter frequency'],
            ['Band-pass Range', 'fc_band', '40-80', 'Hz', 'Band-pass filter range']
        ]
        
        table1 = ax.table(cellText=main_params[1:], colLabels=main_params[0],
                         cellLoc='left', loc='center', bbox=[0, 0.55, 1, 0.4])
        table1.auto_set_font_size(False)
        table1.set_fontsize(9)
        table1.scale(1, 1.5)
        
        for i in range(len(main_params[0])):
            table1[(0, i)].set_facecolor('#4CAF50')
            table1[(0, i)].set_text_props(weight='bold', color='white')
        
        ax.set_title('Parameter Settings and Configuration', fontsize=16, fontweight='bold', pad=20)
        
        # Wear component parameters
        wear_params = [
            ['Wear Component', 'Frequency', 'Amplitude Scaling', 'Physical Meaning'],
            ['2nd Harmonic', '2f₀ (50 Hz)', '0.3 × wear_level', 'Nonlinear bearing response'],
            ['3rd Harmonic', '3f₀ (75 Hz)', '0.2 × wear_level', 'Higher-order nonlinearity'],
            ['Sub-harmonic', '0.5f₀ (12.5 Hz)', '0.15 × wear_level', 'Intermittent contact'],
            ['Upper Sideband', 'f₀ + 10 Hz (35 Hz)', '0.1 × wear_level', 'Modulation effects'],
            ['Lower Sideband', 'f₀ - 10 Hz (15 Hz)', '0.1 × wear_level', 'Modulation effects']
        ]
        
        table2 = ax.table(cellText=wear_params[1:], colLabels=wear_params[0],
                         cellLoc='left', loc='center', bbox=[0, 0.15, 1, 0.25])
        table2.auto_set_font_size(False)
        table2.set_fontsize(9)
        table2.scale(1, 1.5)
        
        for i in range(len(wear_params[0])):
            table2[(0, i)].set_facecolor('#2196F3')
            table2[(0, i)].set_text_props(weight='bold', color='white')
        
        plt.figtext(0.5, 0.45, 'Wear-Related Frequency Components', ha='center', fontsize=14, fontweight='bold')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 2: TIME DOMAIN ANALYSIS
        print("Creating time domain analysis...")
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes = axes.flatten()
        
        for i, ((t, signal), label) in enumerate(zip(signals, wear_labels)):
            axes[i].plot(t[:500], signal[:500], linewidth=1.5, color=f'C{i}')
            axes[i].set_title(f'{label}', fontweight='bold')
            axes[i].set_xlabel('Time (s)')
            axes[i].set_ylabel('Amplitude')
            axes[i].grid(True, alpha=0.3)
            axes[i].set_xlim(0, 0.5)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 3: FREQUENCY DOMAIN ANALYSIS
        print("Creating frequency domain analysis...")
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        axes = axes.flatten()
        
        for i, ((t, signal), label) in enumerate(zip(signals, wear_labels)):
            frequencies, magnitude = analyzer.compute_fft(signal)
            freq_mask = frequencies <= 200
            
            axes[i].plot(frequencies[freq_mask], magnitude[freq_mask], linewidth=1.5, color=f'C{i}')
            axes[i].set_title(f'{label}', fontweight='bold')
            axes[i].set_xlabel('Frequency (Hz)')
            axes[i].set_ylabel('Magnitude')
            axes[i].grid(True, alpha=0.3)
            
            # Mark key frequencies
            axes[i].axvline(rotation_freq, color='red', linestyle='--', alpha=0.7, linewidth=1)
            axes[i].axvline(2*rotation_freq, color='orange', linestyle='--', alpha=0.7, linewidth=1)
            axes[i].axvline(3*rotation_freq, color='gold', linestyle='--', alpha=0.7, linewidth=1)
            
            if i == 0:
                axes[i].text(rotation_freq, axes[i].get_ylim()[1]*0.9, 'f₀', ha='center', fontsize=8, color='red')
                axes[i].text(2*rotation_freq, axes[i].get_ylim()[1]*0.8, '2f₀', ha='center', fontsize=8, color='orange')
                axes[i].text(3*rotation_freq, axes[i].get_ylim()[1]*0.7, '3f₀', ha='center', fontsize=8, color='gold')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 4: DIGITAL FILTERING
        print("Creating digital filtering demonstration...")
        t, worn_signal = signals[2]  # Moderate wear signal
        
        lowpass_signal = analyzer.apply_filter(worn_signal, 'lowpass', 50)
        highpass_signal = analyzer.apply_filter(worn_signal, 'highpass', 50)
        bandpass_signal = analyzer.apply_filter(worn_signal, 'bandpass', [40, 80])
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        time_slice = slice(0, 500)
        
        axes[0,0].plot(t[time_slice], worn_signal[time_slice], 'b-', linewidth=1.5)
        axes[0,0].set_title('Original Signal', fontweight='bold')
        axes[0,0].set_xlabel('Time (s)')
        axes[0,0].set_ylabel('Amplitude')
        axes[0,0].grid(True, alpha=0.3)
        
        axes[0,1].plot(t[time_slice], lowpass_signal[time_slice], 'g-', linewidth=1.5)
        axes[0,1].set_title('Low-pass Filtered (< 50 Hz)', fontweight='bold')
        axes[0,1].set_xlabel('Time (s)')
        axes[0,1].set_ylabel('Amplitude')
        axes[0,1].grid(True, alpha=0.3)
        
        axes[1,0].plot(t[time_slice], highpass_signal[time_slice], 'r-', linewidth=1.5)
        axes[1,0].set_title('High-pass Filtered (> 50 Hz)', fontweight='bold')
        axes[1,0].set_xlabel('Time (s)')
        axes[1,0].set_ylabel('Amplitude')
        axes[1,0].grid(True, alpha=0.3)
        
        axes[1,1].plot(t[time_slice], bandpass_signal[time_slice], 'm-', linewidth=1.5)
        axes[1,1].set_title('Band-pass Filtered (40-80 Hz)', fontweight='bold')
        axes[1,1].set_xlabel('Time (s)')
        axes[1,1].set_ylabel('Amplitude')
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 5: QUANTITATIVE INDICATORS
        print("Creating quantitative indicators...")
        rms_values = [ind['rms'] for ind in results]
        harmonic_ratios = [ind['harmonic_ratio'] for ind in results]
        high_freq_ratios = [ind['hf_ratio'] for ind in results]
        peak_counts = [ind['peak_count'] for ind in results]
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        axes[0,0].plot(wear_levels, rms_values, 'bo-', linewidth=2, markersize=8)
        axes[0,0].set_title('RMS Vibration Amplitude', fontweight='bold')
        axes[0,0].set_xlabel('Wear Level')
        axes[0,0].set_ylabel('RMS Amplitude')
        axes[0,0].grid(True, alpha=0.3)
        
        axes[0,1].plot(wear_levels, harmonic_ratios, 'ro-', linewidth=2, markersize=8)
        axes[0,1].set_title('Harmonic Content Ratio', fontweight='bold')
        axes[0,1].set_xlabel('Wear Level')
        axes[0,1].set_ylabel('Harmonic/Fundamental Power')
        axes[0,1].grid(True, alpha=0.3)
        
        axes[1,0].plot(wear_levels, high_freq_ratios, 'go-', linewidth=2, markersize=8)
        axes[1,0].set_title('High Frequency Content', fontweight='bold')
        axes[1,0].set_xlabel('Wear Level')
        axes[1,0].set_ylabel('HF/Fundamental Power')
        axes[1,0].grid(True, alpha=0.3)
        
        axes[1,1].plot(wear_levels, peak_counts, 'mo-', linewidth=2, markersize=8)
        axes[1,1].set_title('Number of Spectral Peaks', fontweight='bold')
        axes[1,1].set_xlabel('Wear Level')
        axes[1,1].set_ylabel('Peak Count')
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 6: DETAILED COMPARISON
        print("Creating detailed comparison...")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        t_healthy, signal_healthy = signals[0]
        t_severe, signal_severe = signals[3]
        
        freq_healthy, mag_healthy = analyzer.compute_fft(signal_healthy)
        freq_severe, mag_severe = analyzer.compute_fft(signal_severe)
        
        freq_mask = freq_healthy <= 150
        
        ax1.plot(freq_healthy[freq_mask], mag_healthy[freq_mask], 'b-', linewidth=2, label='Initial State')
        ax1.plot(freq_severe[freq_mask], mag_severe[freq_mask], 'r-', linewidth=2, label='Severe Wear')
        ax1.set_title('Frequency Spectrum Comparison', fontweight='bold')
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Magnitude')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        for freq, label, color in [(rotation_freq, 'f₀', 'red'), (2*rotation_freq, '2f₀', 'orange'), (3*rotation_freq, '3f₀', 'gold')]:
            ax1.axvline(freq, color=color, linestyle='--', alpha=0.5)
            ax1.text(freq, ax1.get_ylim()[1]*0.9, label, ha='center', fontsize=8)
        
        ax2.semilogy(freq_healthy[freq_mask], mag_healthy[freq_mask], 'b-', linewidth=2, label='Initial State')
        ax2.semilogy(freq_severe[freq_mask], mag_severe[freq_mask], 'r-', linewidth=2, label='Severe Wear')
        ax2.set_title('Frequency Spectrum (Log Scale)', fontweight='bold')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Magnitude (log scale)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 7: PARAMETER SENSITIVITY
        print("Creating parameter sensitivity analysis...")
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        test_cases = [
            {'wear': 0.2, 'noise': 0.05, 'title': 'Low Wear, Low Noise'},
            {'wear': 0.8, 'noise': 0.05, 'title': 'High Wear, Low Noise'},
            {'wear': 0.2, 'noise': 0.25, 'title': 'Low Wear, High Noise'},
            {'wear': 0.8, 'noise': 0.25, 'title': 'High Wear, High Noise'}
        ]
        
        for i, case in enumerate(test_cases):
            wear_components = [
                (2 * rotation_freq, 0.3 * case['wear']),
                (3 * rotation_freq, 0.2 * case['wear']),
                (0.5 * rotation_freq, 0.15 * case['wear']),
                (rotation_freq + 10, 0.1 * case['wear']),
                (rotation_freq - 10, 0.1 * case['wear'])
            ]
            
            t, signal = generator.generate_signal(
                duration=duration,
                rotation_freq=rotation_freq,
                wear_components=wear_components,
                noise_amplitude=case['noise']
            )
            
            frequencies, magnitude = analyzer.compute_fft(signal)
            freq_mask = frequencies <= 150
            
            ax = axes[i//2, i%2]
            ax.plot(frequencies[freq_mask], magnitude[freq_mask], linewidth=1.5, color=f'C{i}')
            ax.set_title(case['title'], fontweight='bold')
            ax.set_xlabel('Frequency (Hz)')
            ax.set_ylabel('Magnitude')
            ax.grid(True, alpha=0.3)
            
            ax.axvline(rotation_freq, color='red', linestyle='--', alpha=0.7, linewidth=1)
            ax.text(rotation_freq + 5, ax.get_ylim()[1]*0.8, 'f₀', fontsize=8, color='red')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 8: RESULTS TABLE
        print("Creating results table...")
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('tight')
        ax.axis('off')
        
        results_data = [
            ['Wear Level', 'RMS Amplitude', 'Harmonic Ratio', 'HF Ratio', 'Peak Count', 'Fund. Power', 'Harm. Power', 'HF Power']
        ]
        
        for r in results:
            results_data.append([
                f"{r['wear_level']:.1f}",
                f"{r['rms']:.4f}",
                f"{r['harmonic_ratio']:.4f}",
                f"{r['hf_ratio']:.4f}",
                f"{r['peak_count']}",
                f"{r['fundamental_power']:.1f}",
                f"{r['harmonic_power']:.2f}",
                f"{r['hf_power']:.2f}"
            ])
        
        table3 = ax.table(cellText=results_data[1:], colLabels=results_data[0],
                         cellLoc='center', loc='center', bbox=[0, 0.6, 1, 0.35])
        table3.auto_set_font_size(False)
        table3.set_fontsize(10)
        table3.scale(1, 2)
        
        for i in range(len(results_data[0])):
            table3[(0, i)].set_facecolor('#FF9800')
            table3[(0, i)].set_text_props(weight='bold', color='white')
        
        ax.set_title('Quantitative Analysis Results', fontsize=16, fontweight='bold', pad=20)
        
        # Computational methods table
        methods_data = [
            ['Analysis Method', 'Implementation', 'Key Parameters', 'Output'],
            ['Signal Generation', 'Superposition of sinusoids', 'Frequencies, amplitudes, noise', 'Time series x(t)'],
            ['Preprocessing', 'Mean removal, windowing', 'Window type (Hann)', 'Conditioned signal'],
            ['FFT Analysis', 'scipy.fft.fft()', 'N samples, fs sampling rate', 'Frequency spectrum'],
            ['Digital Filtering', 'Butterworth filters', 'Order=4, cutoff frequencies', 'Filtered signals'],
            ['RMS Calculation', 'sqrt(mean(x²))', 'Full signal length', 'Overall amplitude'],
            ['Band Power', 'Sum of |X(f)|² in band', 'Frequency band limits', 'Power in band'],
            ['Peak Detection', 'scipy.signal.find_peaks()', 'Height, prominence thresholds', 'Peak locations']
        ]
        
        table4 = ax.table(cellText=methods_data[1:], colLabels=methods_data[0],
                         cellLoc='left', loc='center', bbox=[0, 0.05, 1, 0.45])
        table4.auto_set_font_size(False)
        table4.set_fontsize(9)
        table4.scale(1, 1.4)
        
        for i in range(len(methods_data[0])):
            table4[(0, i)].set_facecolor('#9C27B0')
            table4[(0, i)].set_text_props(weight='bold', color='white')
        
        plt.figtext(0.5, 0.52, 'Computational Methods and Implementation', ha='center', fontsize=14, fontweight='bold')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 9: PERFORMANCE METRICS
        print("Creating performance metrics...")
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('tight')
        ax.axis('off')
        
        # Sensitivity analysis
        sensitivity_data = [
            ['Metric', 'Initial→Light', 'Light→Moderate', 'Moderate→Severe', 'Overall Change'],
            ['RMS Amplitude', 
             f"{((rms_values[1]-rms_values[0])/rms_values[0]*100):.1f}%",
             f"{((rms_values[2]-rms_values[1])/rms_values[1]*100):.1f}%", 
             f"{((rms_values[3]-rms_values[2])/rms_values[2]*100):.1f}%",
             f"{((rms_values[3]-rms_values[0])/rms_values[0]*100):.1f}%"],
            ['Harmonic Ratio',
             f"{((harmonic_ratios[1]-harmonic_ratios[0])/max(harmonic_ratios[0],1e-6)*100):.1f}%",
             f"{((harmonic_ratios[2]-harmonic_ratios[1])/harmonic_ratios[1]*100):.1f}%",
             f"{((harmonic_ratios[3]-harmonic_ratios[2])/harmonic_ratios[2]*100):.1f}%",
             f"{(harmonic_ratios[3]/max(harmonic_ratios[0],1e-6)):.1f}x increase"]
        ]
        
        table5 = ax.table(cellText=sensitivity_data[1:], colLabels=sensitivity_data[0],
                         cellLoc='center', loc='center', bbox=[0, 0.7, 1, 0.25])
        table5.auto_set_font_size(False)
        table5.set_fontsize(10)
        table5.scale(1, 2)
        
        for i in range(len(sensitivity_data[0])):
            table5[(0, i)].set_facecolor('#F44336')
            table5[(0, i)].set_text_props(weight='bold', color='white')
        
        ax.set_title('Performance Metrics and Sensitivity Analysis', fontsize=16, fontweight='bold', pad=20)
        
        # Frequency band analysis
        band_data = [
            ['Frequency Band', 'Range (Hz)', 'Physical Significance', 'Diagnostic Value'],
            ['Fundamental', '23-27', 'Primary rotation frequency', 'Baseline reference'],
            ['Low Harmonics', '45-85', '2nd and 3rd harmonics', 'Nonlinear response'],
            ['Sub-harmonics', '10-15', 'Intermittent contact', 'Early wear indicator'],
            ['Sidebands', '15-35', 'Modulation effects', 'Advanced wear features'],
            ['High Frequency', '100-500', 'Impulsive events', 'Surface roughness'],
            ['Broadband Noise', '0-500', 'Random excitation', 'Overall degradation']
        ]
        
        table6 = ax.table(cellText=band_data[1:], colLabels=band_data[0],
                         cellLoc='left', loc='center', bbox=[0, 0.15, 1, 0.45])
        table6.auto_set_font_size(False)
        table6.set_fontsize(9)
        table6.scale(1, 1.5)
        
        for i in range(len(band_data[0])):
            table6[(0, i)].set_facecolor('#607D8B')
            table6[(0, i)].set_text_props(weight='bold', color='white')
        
        plt.figtext(0.5, 0.62, 'Frequency Band Analysis and Diagnostic Significance', ha='center', fontsize=12, fontweight='bold')
        
        # Summary statistics
        plt.figtext(0.1, 0.08, 'Summary Statistics:', fontsize=12, fontweight='bold')
        plt.figtext(0.1, 0.05, f'• Total signal length: {len(signals[0][1])} samples', fontsize=10)
        plt.figtext(0.1, 0.02, f'• Frequency resolution: {fs/len(signals[0][1]):.2f} Hz', fontsize=10)
        plt.figtext(0.5, 0.05, f'• Nyquist frequency: {fs/2} Hz', fontsize=10)
        plt.figtext(0.5, 0.02, f'• Maximum detectable frequency: {fs/2} Hz', fontsize=10)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print(f"✅ Complete report created: {pdf_filename}")
    print("The comprehensive PDF contains:")
    print("  • Title page with project overview")
    print("  • Parameter settings and configuration tables")
    print("  • All 6 types of analysis figures")
    print("  • Quantitative results tables")
    print("  • Computational methods documentation")
    print("  • Performance metrics and validation")
    print(f"Total pages: 9")

if __name__ == "__main__":
    try:
        create_complete_report()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()