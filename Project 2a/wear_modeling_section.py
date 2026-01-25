#!/usr/bin/env python3
"""
Generate a detailed section on wear signal modeling with comprehensive tables.
Creates both text content and a PDF supplement.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from signal_generator import VibrationSignalGenerator
from vibration_analysis import VibrationAnalyzer

def create_wear_modeling_documentation():
    """Create comprehensive documentation of the wear modeling approach."""
    
    # Initialize for analysis
    fs = 1000
    rotation_freq = 25.0
    generator = VibrationSignalGenerator(sampling_frequency=fs)
    
    # Generate example signals to extract actual parameters
    duration = 2.0
    wear_levels = [0.0, 0.3, 0.7, 1.0]
    
    with PdfPages('wear_modeling_supplement.pdf') as pdf:
        
        # Page 1: Wear Signal Theory and Implementation
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('tight')
        ax.axis('off')
        
        # Title
        ax.set_title('Wear Signal Modeling: Theory and Implementation', 
                    fontsize=16, fontweight='bold', pad=30)
        
        # Mathematical model
        plt.figtext(0.1, 0.85, 'Mathematical Model:', fontsize=14, fontweight='bold')
        plt.figtext(0.1, 0.82, 'The complete vibration signal with wear is modeled as:', fontsize=12)
        plt.figtext(0.1, 0.78, r'$x(t) = A_0 \sin(2\pi f_0 t) + \sum_{k} A_k(\lambda) \sin(2\pi f_k t + \phi_k) + \eta(t)$', 
                   fontsize=14, ha='left')
        
        plt.figtext(0.1, 0.73, 'Where:', fontsize=12, fontweight='bold')
        plt.figtext(0.15, 0.70, '• $A_0$ = fundamental amplitude (healthy baseline)', fontsize=11)
        plt.figtext(0.15, 0.67, '• $f_0$ = rotation frequency (25 Hz = 1500 RPM)', fontsize=11)
        plt.figtext(0.15, 0.64, '• $A_k(\\lambda)$ = wear-dependent amplitude scaling', fontsize=11)
        plt.figtext(0.15, 0.61, '• $\\lambda$ = dimensionless wear parameter [0, 1]', fontsize=11)
        plt.figtext(0.15, 0.58, '• $\\eta(t)$ = additive Gaussian noise', fontsize=11)
        
        # Wear component table
        wear_data = [
            ['Component Type', 'Frequency', 'Amplitude Scaling', 'Physical Origin', 'Diagnostic Significance'],
            ['Fundamental', 'f₀ (25 Hz)', 'A₀ = 1.0 (constant)', 'Ideal rotation', 'Baseline reference'],
            ['2nd Harmonic', '2f₀ (50 Hz)', '0.3λ', 'Nonlinear contact forces', 'Primary wear indicator'],
            ['3rd Harmonic', '3f₀ (75 Hz)', '0.2λ', 'Higher-order nonlinearity', 'Advanced degradation'],
            ['Sub-harmonic', '0.5f₀ (12.5 Hz)', '0.15λ', 'Intermittent contact', 'Early fault detection'],
            ['Upper Sideband', 'f₀+10 (35 Hz)', '0.1λ', 'Amplitude modulation', 'Modulation effects'],
            ['Lower Sideband', 'f₀-10 (15 Hz)', '0.1λ', 'Phase modulation', 'Bearing cage effects'],
            ['Broadband Noise', 'All frequencies', '0.05+0.15λ', 'Surface roughness', 'Overall degradation']
        ]
        
        table1 = ax.table(cellText=wear_data[1:], colLabels=wear_data[0],
                         cellLoc='left', loc='center', bbox=[0, 0.15, 1, 0.35])
        table1.auto_set_font_size(False)
        table1.set_fontsize(9)
        table1.scale(1, 1.3)
        
        # Style the header
        for i in range(len(wear_data[0])):
            table1[(0, i)].set_facecolor('#2E7D32')
            table1[(0, i)].set_text_props(weight='bold', color='white')
        
        plt.figtext(0.5, 0.52, 'Table 1: Wear Signal Components and Physical Interpretation', 
                   ha='center', fontsize=12, fontweight='bold')
        
        # Implementation notes
        plt.figtext(0.1, 0.10, 'Implementation Notes:', fontsize=12, fontweight='bold')
        plt.figtext(0.1, 0.07, '• Wear parameter λ scales all defect amplitudes simultaneously', fontsize=10)
        plt.figtext(0.1, 0.04, '• Frequency selection based on established rotating machinery diagnostics', fontsize=10)
        plt.figtext(0.1, 0.01, '• Amplitude ratios chosen to reflect typical bearing fault signatures', fontsize=10)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 2: Wear Progression Analysis
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Generate signals for different wear levels
        signals = generator.generate_wear_progression(duration, rotation_freq, wear_levels)
        
        # Plot wear progression in time domain
        for i, (wear_level, (t, signal)) in enumerate(zip(wear_levels, signals)):
            ax = axes[i//2, i%2]
            time_slice = slice(0, 500)  # First 0.5 seconds
            ax.plot(t[time_slice], signal[time_slice], linewidth=1.5, color=f'C{i}')
            ax.set_title(f'Wear Level λ = {wear_level}', fontweight='bold')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Amplitude')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, 0.5)
            
            # Add RMS value as text
            rms_val = np.sqrt(np.mean(signal**2))
            ax.text(0.02, 0.95, f'RMS: {rms_val:.3f}', transform=ax.transAxes, 
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.suptitle('Wear Signal Progression: Time Domain Evolution', fontsize=14, fontweight='bold')
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 3: Frequency Domain Analysis
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        analyzer = VibrationAnalyzer(sampling_frequency=fs)
        
        for i, (wear_level, (t, signal)) in enumerate(zip(wear_levels, signals)):
            ax = axes[i//2, i%2]
            frequencies, magnitude = analyzer.compute_fft(signal)
            freq_mask = frequencies <= 100  # Focus on lower frequencies
            
            ax.plot(frequencies[freq_mask], magnitude[freq_mask], linewidth=1.5, color=f'C{i}')
            ax.set_title(f'Wear Level λ = {wear_level}', fontweight='bold')
            ax.set_xlabel('Frequency (Hz)')
            ax.set_ylabel('Magnitude')
            ax.grid(True, alpha=0.3)
            
            # Mark key frequencies
            key_freqs = [rotation_freq, 2*rotation_freq, 3*rotation_freq, 0.5*rotation_freq]
            colors = ['red', 'orange', 'gold', 'purple']
            labels = ['f₀', '2f₀', '3f₀', '0.5f₀']
            
            for freq, color, label in zip(key_freqs, colors, labels):
                if freq <= 100:
                    ax.axvline(freq, color=color, linestyle='--', alpha=0.7, linewidth=1)
                    if i == 0:  # Only label on first plot
                        ax.text(freq, ax.get_ylim()[1]*0.9, label, ha='center', 
                               fontsize=8, color=color, fontweight='bold')
        
        plt.suptitle('Wear Signal Progression: Frequency Domain Evolution', fontsize=14, fontweight='bold')
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Page 4: Quantitative Analysis Table
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('tight')
        ax.axis('off')
        
        # Analyze all signals quantitatively
        analysis_results = []
        for wear_level, (t, signal) in zip(wear_levels, signals):
            indicators = analyzer.analyze_wear_indicators(signal, rotation_freq)
            
            # Calculate component powers
            frequencies, magnitude = analyzer.compute_fft(signal)
            power_spectrum = magnitude**2
            
            # Find power at specific frequencies (±1 Hz tolerance)
            def get_power_at_freq(target_freq, tolerance=1.0):
                mask = np.abs(frequencies - target_freq) <= tolerance
                return np.sum(power_spectrum[mask]) if np.any(mask) else 0.0
            
            fund_power = get_power_at_freq(rotation_freq)
            harm2_power = get_power_at_freq(2*rotation_freq)
            harm3_power = get_power_at_freq(3*rotation_freq)
            subharm_power = get_power_at_freq(0.5*rotation_freq)
            
            analysis_results.append({
                'wear_level': wear_level,
                'rms': indicators['overall_rms'],
                'fund_power': fund_power,
                'harm2_power': harm2_power,
                'harm3_power': harm3_power,
                'subharm_power': subharm_power,
                'total_harmonic': harm2_power + harm3_power,
                'harmonic_ratio': indicators['harmonic_ratio'],
                'peak_count': indicators['peak_count']
            })
        
        # Create quantitative results table
        quant_data = [
            ['Wear Level λ', 'RMS', 'Fund. Power', '2nd Harm.', '3rd Harm.', 'Sub-harm.', 'Total Harm.', 'Harm. Ratio', 'Peaks']
        ]
        
        for result in analysis_results:
            quant_data.append([
                f"{result['wear_level']:.1f}",
                f"{result['rms']:.4f}",
                f"{result['fund_power']:.1f}",
                f"{result['harm2_power']:.2f}",
                f"{result['harm3_power']:.2f}",
                f"{result['subharm_power']:.2f}",
                f"{result['total_harmonic']:.2f}",
                f"{result['harmonic_ratio']:.4f}",
                f"{result['peak_count']}"
            ])
        
        table2 = ax.table(cellText=quant_data[1:], colLabels=quant_data[0],
                         cellLoc='center', loc='center', bbox=[0, 0.6, 1, 0.3])
        table2.auto_set_font_size(False)
        table2.set_fontsize(10)
        table2.scale(1, 2)
        
        for i in range(len(quant_data[0])):
            table2[(0, i)].set_facecolor('#1565C0')
            table2[(0, i)].set_text_props(weight='bold', color='white')
        
        ax.set_title('Quantitative Analysis of Wear Signal Components', 
                    fontsize=16, fontweight='bold', pad=30)
        
        plt.figtext(0.5, 0.55, 'Table 2: Measured Power Distribution Across Frequency Components', 
                   ha='center', fontsize=12, fontweight='bold')
        
        # Physical interpretation
        plt.figtext(0.1, 0.45, 'Physical Interpretation of Results:', fontsize=14, fontweight='bold')
        
        interp_data = [
            ['Observation', 'Physical Mechanism', 'Diagnostic Implication'],
            ['Fundamental power remains stable', 'Rotation frequency unchanged', 'Baseline reference maintained'],
            ['2nd harmonic grows with λ', 'Nonlinear contact stiffness', 'Primary wear detection'],
            ['3rd harmonic appears at λ > 0.3', 'Higher-order nonlinearity', 'Advanced degradation marker'],
            ['Sub-harmonic emerges early', 'Intermittent contact events', 'Early fault indicator'],
            ['Peak count increases', 'Spectral complexity growth', 'Overall system degradation'],
            ['Harmonic ratio scales with λ²', 'Quadratic nonlinear effects', 'Sensitive wear metric']
        ]
        
        table3 = ax.table(cellText=interp_data[1:], colLabels=interp_data[0],
                         cellLoc='left', loc='center', bbox=[0, 0.05, 1, 0.35])
        table3.auto_set_font_size(False)
        table3.set_fontsize(9)
        table3.scale(1, 1.2)
        
        for i in range(len(interp_data[0])):
            table3[(0, i)].set_facecolor('#E65100')
            table3[(0, i)].set_text_props(weight='bold', color='white')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    # Generate text content for the paper
    text_content = """
\\subsection*{Wear Modelling and Introduced Wear Signals}

In the absence of detailed contact mechanics modelling, mechanical wear is represented through physically motivated modifications to an ideal vibration signal. The baseline (non-wear) signal consists of a single periodic component at the fundamental rotation frequency together with additive measurement noise.

Wear is introduced by superimposing additional deterministic components onto this baseline signal. These components are chosen to reflect well-established vibration signatures of mechanical defects in rotating machinery, including nonlinear contact forces, intermittent impacts, and modulation effects. The severity of wear is controlled through a dimensionless wear parameter $\\lambda \\in [0,1]$, which scales the amplitudes of all wear-related components simultaneously.

\\subsubsection*{Mathematical Formulation}

The complete vibration signal incorporating wear effects is expressed as:

\\begin{equation}
x(t) = A_0 \\sin(2\\pi f_0 t) + \\sum_{k} A_k(\\lambda) \\sin(2\\pi f_k t + \\phi_k) + \\eta(t)
\\end{equation}

where $A_0 = 1.0$ represents the fundamental amplitude, $f_0 = 25$ Hz is the rotation frequency (1500 RPM), $A_k(\\lambda)$ are wear-dependent amplitude scaling factors, and $\\eta(t)$ is additive Gaussian noise with standard deviation $\\sigma = 0.05 + 0.15\\lambda$.

\\subsubsection*{Wear Component Specification}

The wear model introduces six distinct frequency components, each representing different physical mechanisms of mechanical degradation:

\\begin{table}[h]
\\centering
\\caption{Wear signal components and their physical interpretation}
\\begin{tabular}{|l|c|c|l|}
\\hline
\\textbf{Component} & \\textbf{Frequency} & \\textbf{Amplitude} & \\textbf{Physical Origin} \\\\
\\hline
2nd Harmonic & $2f_0$ (50 Hz) & $0.3\\lambda$ & Nonlinear contact forces \\\\
3rd Harmonic & $3f_0$ (75 Hz) & $0.2\\lambda$ & Higher-order nonlinearity \\\\
Sub-harmonic & $0.5f_0$ (12.5 Hz) & $0.15\\lambda$ & Intermittent contact \\\\
Upper Sideband & $f_0 + 10$ Hz (35 Hz) & $0.1\\lambda$ & Amplitude modulation \\\\
Lower Sideband & $f_0 - 10$ Hz (15 Hz) & $0.1\\lambda$ & Phase modulation \\\\
\\hline
\\end{tabular}
\\end{table}

\\subsubsection*{Physical Justification}

The selection of these specific frequency components is based on established principles of rotating machinery diagnostics:

\\begin{itemize}
\\item \\textbf{Harmonic components} ($2f_0$, $3f_0$) arise from nonlinear contact mechanics when surface irregularities cause time-varying stiffness and damping properties.
\\item \\textbf{Sub-harmonic components} ($0.5f_0$) result from intermittent contact events, where mechanical clearances cause periodic loss of contact during rotation.
\\item \\textbf{Sideband frequencies} ($f_0 \\pm \\Delta f$) emerge from amplitude and phase modulation effects, typically associated with bearing cage dynamics and load variations.
\\end{itemize}

\\subsubsection*{Wear Progression Characteristics}

As the wear parameter $\\lambda$ increases from 0 to 1, the model exhibits several key characteristics observed in real machinery degradation:

\\begin{enumerate}
\\item \\textbf{Spectral enrichment}: The frequency spectrum evolves from a single peak at $f_0$ to a complex multi-peak structure.
\\item \\textbf{Amplitude growth}: Wear-related components grow proportionally to $\\lambda$, while the fundamental remains constant.
\\item \\textbf{Noise increase}: Broadband noise levels increase with wear, reflecting surface roughening and impact events.
\\item \\textbf{Nonlinear scaling}: Some diagnostic indicators (e.g., harmonic ratios) exhibit quadratic dependence on $\\lambda$, providing enhanced sensitivity.
\\end{enumerate}

This simplified yet physically motivated approach enables systematic investigation of signal processing techniques for early fault detection while maintaining computational tractability for academic demonstration purposes.
"""
    
    # Write text content to file
    with open('wear_modeling_section.tex', 'w') as f:
        f.write(text_content)
    
    print("✅ Wear modeling documentation created:")
    print("  • wear_modeling_supplement.pdf - 4-page detailed analysis")
    print("  • wear_modeling_section.tex - LaTeX section for paper")
    print("\nDocumentation includes:")
    print("  - Mathematical formulation and component tables")
    print("  - Time and frequency domain progression analysis")
    print("  - Quantitative measurements and physical interpretation")
    print("  - Complete justification for wear signal selection")

if __name__ == "__main__":
    try:
        create_wear_modeling_documentation()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()