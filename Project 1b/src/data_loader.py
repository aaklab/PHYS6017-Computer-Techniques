import yfinance as yf
import pandas as pd
import numpy as np

def load_data(config):
    """Load and clean price data from Yahoo Finance."""
    tickers = config['data']['tickers']
    start_date = config['data']['start_date']
    end_date = config['data']['end_date']
    price_field = config['data']['price_field']
    
    data = yf.download(tickers, start=start_date, end=end_date, progress=False)[price_field]
    return data.dropna()

def compute_returns(prices, return_type='log'):
    """Compute daily returns."""
    if return_type == 'log':
        return np.log(prices / prices.shift(1)).dropna()
    else:
        return (prices / prices.shift(1) - 1).dropna()
