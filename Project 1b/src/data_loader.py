import yfinance as yf
import pandas as pd
import numpy as np
import os
import hashlib

def _get_cache_filename(config):
    """Generate cache filename based on config parameters."""
    cache_key = f"{config['data']['tickers']}_{config['data']['start_date']}_{config['data']['end_date']}_{config['data']['price_field']}"
    hash_key = hashlib.md5(cache_key.encode()).hexdigest()
    return f"data_cache_{hash_key}.csv"

def load_data(config):
    """Load and clean price data from Yahoo Finance with caching."""
    cache_dir = "data_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    cache_file = os.path.join(cache_dir, _get_cache_filename(config))
    
    # Try to load from cache
    if os.path.exists(cache_file):
        print(f"Loading data from cache: {cache_file}")
        data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
    else:
        # Download from Yahoo Finance
        print("Downloading data from Yahoo Finance...")
        tickers = config['data']['tickers']
        start_date = config['data']['start_date']
        end_date = config['data']['end_date']
        
        # Download each ticker separately and combine
        price_series = []
        for ticker in tickers:
            print(f"  Downloading {ticker}...")
            ticker_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if ticker_data.empty:
                raise ValueError(f"No data returned for {ticker}")
            
            # Extract the adjusted close price
            if 'Adj Close' in ticker_data.columns:
                series = ticker_data['Adj Close']
            elif 'Close' in ticker_data.columns:
                series = ticker_data['Close']
            else:
                raise ValueError(f"Could not find price data for {ticker}")
            
            series.name = ticker
            price_series.append(series)
        
        # Combine into DataFrame
        data = pd.concat(price_series, axis=1)
        data = data.dropna()
        
        # Save to cache
        data.to_csv(cache_file)
        print(f"Data cached to: {cache_file}")
    
    return data

def compute_returns(prices, return_type='log'):
    """Compute daily returns."""
    if return_type == 'log':
        return np.log(prices / prices.shift(1)).dropna()
    else:
        return (prices / prices.shift(1) - 1).dropna()
