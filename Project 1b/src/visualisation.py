import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
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
                       label=f'{var_key}: ${risk_metrics[var_key]:.2f}')
        
        es_key = f'ES_{int(alpha*100)}'
        if es_key in risk_metrics:
            ax1.axvline(risk_metrics[es_key], color=colors[i], linestyle=':', 
                       label=f'{es_key}: ${risk_metrics[es_key]:.2f}')
    
    ax1.set_xlabel('Portfolio Loss ($)')
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
    
    ax2.set_xlabel('Portfolio Loss ($)')
    ax2.set_ylabel('Cumulative Probability')
    ax2.set_title('Cumulative Distribution of Losses')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def create_price_paths_plot(paths, config, n_paths_to_plot=50):
    """Create spaghetti plot of simulated price paths."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    tickers = config['data']['tickers']
    n_assets = len(tickers)
    n_paths_total = paths.shape[0]
    H = paths.shape[1]
    
    # Plot subset of paths for each asset
    n_plot = min(n_paths_to_plot, n_paths_total)
    colors = ['blue', 'red', 'green', 'orange']
    
    for asset_idx in range(n_assets):
        for path_idx in range(n_plot):
            cumulative_returns = np.cumsum(paths[path_idx, :, asset_idx])
            prices = 100 * np.exp(cumulative_returns)  # Normalized to 100
            ax.plot(prices, color=colors[asset_idx], alpha=0.1, linewidth=0.5)
    
    # Add legend with dummy lines
    for asset_idx in range(n_assets):
        ax.plot([], [], color=colors[asset_idx], label=tickers[asset_idx], linewidth=2)
    
    ax.set_xlabel('Time Step (days)')
    ax.set_ylabel('Price (normalized to 100)')
    ax.set_title(f'Simulated Price Paths ({n_plot} paths per asset)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return fig

def save_results(losses, risk_metrics, config, mu, sigma, R, prices, paths):
    """Save plots and summary table to PDF."""
    results_dir = config['output']['results_dir']
    os.makedirs(results_dir, exist_ok=True)
    
    filename = os.path.join(results_dir, 'results.pdf')
    
    with PdfPages(filename) as pdf:
        # Page 1: Simulation Parameters (Table 1)
        fig_params = plt.figure(figsize=(8.5, 11))
        ax = fig_params.add_subplot(111)
        ax.axis('off')
        
        tickers = config['data']['tickers']
        weights = config['portfolio']['weights']
        
        # Calculate annualized statistics
        mu_annual = mu * 252
        sigma_annual = sigma * np.sqrt(252)
        
        params_text = f"""
Monte Carlo Portfolio Risk Analysis
====================================

Table 1: Simulation Parameters
-------------------------------
Parameter                    Value
-----------                  -----
N (assets)                   {len(tickers)}
Tickers                      {', '.join(tickers)}
Portfolio weights (w_i)      {weights}
Time step (Δt)               {config['model']['dt']} trading day
Horizon (H)                  {config['model']['horizon_days']} days
Number of paths (N_paths)    {config['simulation']['n_paths']:,}
Random seed                  {config['simulation']['random_seed']}
Confidence levels (α)        {config['risk']['confidence_levels']}

Estimated Parameters from Historical Data
------------------------------------------
Data period: {config['data']['start_date']} to {config['data']['end_date']}

Daily mean returns (μ_i):
"""
        for i, ticker in enumerate(tickers):
            params_text += f"  {ticker}: {mu[i]:.6f} ({mu_annual[i]*100:.2f}% annualized)\n"
        
        params_text += "\nDaily volatilities (σ_i):\n"
        for i, ticker in enumerate(tickers):
            params_text += f"  {ticker}: {sigma[i]:.6f} ({sigma_annual[i]*100:.2f}% annualized)\n"
        
        params_text += f"\nCorrelation matrix (R):\n"
        for i, ticker_i in enumerate(tickers):
            row = "  " + ticker_i + ": "
            for j in range(len(tickers)):
                row += f"{R[i,j]:.4f}  "
            params_text += row + "\n"
        
        ax.text(0.05, 0.95, params_text, fontsize=9, family='monospace',
                verticalalignment='top', transform=ax.transAxes)
        pdf.savefig(fig_params)
        plt.close()
        
        # Page 2: Empirical Results
        fig_results = plt.figure(figsize=(8.5, 11))
        ax = fig_results.add_subplot(111)
        ax.axis('off')
        
        risk_text = ""
        for k, v in risk_metrics.items():
            risk_text += f"  {k}: ${v:.2f}\n"
        
        results_text = f"""
Section 5: Results
==================

Risk Metrics
------------
{risk_text}
Loss Distribution Statistics
-----------------------------
  Mean loss: ${losses.mean():.2f}
  Median loss: ${np.median(losses):.2f}
  Std deviation: ${losses.std():.2f}
  Min loss: ${losses.min():.2f}
  Max loss: ${losses.max():.2f}
  
Interpretation
--------------
The 95% Value at Risk (VaR) of ${risk_metrics.get('VaR_95', 0):.2f} indicates that 
with 95% confidence, the portfolio loss will not exceed this amount over 
the {config['model']['horizon_days']}-day horizon.

The 95% Expected Shortfall (ES) of ${risk_metrics.get('ES_95', 0):.2f} represents 
the average loss in the worst 5% of scenarios, providing insight into 
tail risk beyond the VaR threshold.

Portfolio Composition
---------------------
"""
        for i, ticker in enumerate(tickers):
            last_price = prices.iloc[-1, i]
            results_text += f"  {ticker}: weight={weights[i]:.1%}, last price=${last_price:.2f}\n"
        
        ax.text(0.05, 0.95, results_text, fontsize=10, family='monospace',
                verticalalignment='top', transform=ax.transAxes)
        pdf.savefig(fig_results)
        plt.close()
        
        # Page 3: Loss Distribution Plots
        if config['output']['make_plots']:
            fig_plots = create_plots(losses, risk_metrics, config)
            pdf.savefig(fig_plots)
            plt.close()
        
        # Page 4: Price Paths
        if config['output']['make_plots']:
            fig_paths = create_price_paths_plot(paths, config, n_paths_to_plot=50)
            pdf.savefig(fig_paths)
            plt.close()
    
    # Save loss samples if requested
    if config['output']['save_loss_samples']:
        loss_file = os.path.join(results_dir, 'loss_samples.csv')
        np.savetxt(loss_file, losses, delimiter=',', header='loss', comments='')
    
    return filename
