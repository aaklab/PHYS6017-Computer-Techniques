import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.backends.backend_pdf import PdfPages

def create_plots(losses, risk_metrics, config):
    """Create histogram and cumulative distribution plots."""
    confidence_levels = config['risk']['confidence_levels']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Histogram
    ax1.hist(losses, bins=50, density=True, alpha=0.7, edgecolor='black')
    
    colors = ['r', 'orange', 'purple', 'green']
    for i, alpha in enumerate(confidence_levels):
        var_key = f'VaR_{int(alpha*100)}'
        if var_key in risk_metrics:
            ax1.axvline(risk_metrics[var_key], color=colors[i], linestyle='--', 
                       label=f'{var_key}: {risk_metrics[var_key]:.2f}')
        
        es_key = f'ES_{int(alpha*100)}'
        if es_key in risk_metrics:
            ax1.axvline(risk_metrics[es_key], color=colors[i], linestyle=':', 
                       label=f'{es_key}: {risk_metrics[es_key]:.2f}')
    
    ax1.set_xlabel('Portfolio Loss')
    ax1.set_ylabel('Probability Density')
    ax1.set_title('Distribution of Portfolio Losses')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Cumulative distribution
    sorted_losses = np.sort(losses)
    cumulative = np.arange(1, len(sorted_losses) + 1) / len(sorted_losses)
    ax2.plot(sorted_losses, cumulative, linewidth=2)
    
    for i, alpha in enumerate(confidence_levels):
        var_key = f'VaR_{int(alpha*100)}'
        if var_key in risk_metrics:
            ax2.axvline(risk_metrics[var_key], color=colors[i], linestyle='--', 
                       label=f'VaR ({alpha*100}%)')
            ax2.axhline(alpha, color=colors[i], linestyle=':', alpha=0.5)
    
    ax2.set_xlabel('Portfolio Loss')
    ax2.set_ylabel('Cumulative Probability')
    ax2.set_title('Cumulative Distribution of Losses')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def save_results(losses, risk_metrics, config):
    """Save plots and summary table to PDF."""
    results_dir = config['output']['results_dir']
    os.makedirs(results_dir, exist_ok=True)
    
    filename = os.path.join(results_dir, 'results.pdf')
    
    with PdfPages(filename) as pdf:
        # Summary page
        fig_summary = plt.figure(figsize=(8, 6))
        ax = fig_summary.add_subplot(111)
        ax.axis('off')
        
        risk_text = '\n'.join([f"- {k}: {v:.2f}" for k, v in risk_metrics.items()])
        
        summary_text = f"""
Monte Carlo Portfolio Risk Analysis
====================================

Simulation Parameters:
- Number of paths: {len(losses):,}
- Random seed: {config['simulation']['random_seed']}
- Horizon: {config['model']['horizon_days']} days

Portfolio:
- Tickers: {', '.join(config['data']['tickers'])}
- Weights: {config['portfolio']['weights']}

Risk Metrics:
{risk_text}

Loss Distribution Statistics:
- Mean loss: {losses.mean():.2f}
- Std deviation: {losses.std():.2f}
- Min loss: {losses.min():.2f}
- Max loss: {losses.max():.2f}
        """
        
        ax.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
                verticalalignment='center')
        pdf.savefig(fig_summary)
        plt.close()
        
        # Plots page
        if config['output']['make_plots']:
            fig_plots = create_plots(losses, risk_metrics, config)
            pdf.savefig(fig_plots)
            plt.close()
    
    # Save loss samples if requested
    if config['output']['save_loss_samples']:
        loss_file = os.path.join(results_dir, 'loss_samples.csv')
        np.savetxt(loss_file, losses, delimiter=',', header='loss', comments='')
    
    return filename
