# Rolling Hedge Ratio Feature

## Overview
The pairs trading notebook now supports **rolling hedge ratio calculation** as a configurable option. This allows the strategy to adapt to changing market relationships between the two assets over time.

## Configuration

In the configuration cell at the top of the notebook, you'll find these new parameters:

```python
# Hedge ratio calculation method
USE_ROLLING_HEDGE_RATIO = True  # True = recalculate beta on rolling basis, False = static beta
HEDGE_RATIO_WINDOW = 252        # Days for rolling hedge ratio calculation (252 = 1 year)
```

## How It Works

### Static Hedge Ratio (Original Method)
When `USE_ROLLING_HEDGE_RATIO = False`:
- Calculates a single beta (β) using the entire historical dataset
- Uses this constant hedge ratio for all trades
- Assumes the relationship between assets is stable over time

**Formula:**
```
β = OLS(Asset1, Asset2) using all data
spread(t) = Asset1(t) - β × Asset2(t)
```

### Rolling Hedge Ratio (New Method)
When `USE_ROLLING_HEDGE_RATIO = True`:
- Recalculates beta every day using the previous N days (default: 252 days = 1 year)
- Adapts to changing market conditions and regime shifts
- More robust to structural breaks in the cointegration relationship

**Formula:**
```
For each day t:
    β(t) = OLS(Asset1[t-252:t], Asset2[t-252:t])
    spread(t) = Asset1(t) - β(t) × Asset2(t)
```

## Benefits of Rolling Hedge Ratio

1. **Adapts to Market Changes**: The relationship between assets can change due to:
   - Market regime shifts
   - Changes in company fundamentals
   - Sector rotation
   - Macroeconomic events

2. **More Accurate Spread Calculation**: Uses recent data to determine the current relationship

3. **Better Risk Management**: Prevents using outdated hedge ratios that may no longer be valid

4. **Improved Performance**: Can lead to better returns when the asset relationship evolves over time

## Trade-offs

### Advantages:
- More adaptive to changing market conditions
- Better reflects current asset relationships
- Can improve performance in non-stationary environments

### Disadvantages:
- Requires more data (first 252 days have no hedge ratio)
- Slightly more complex calculation
- May be more sensitive to short-term noise
- Can lead to more frequent rebalancing

## Recommended Settings

### Conservative (Slower Adaptation):
```python
USE_ROLLING_HEDGE_RATIO = True
HEDGE_RATIO_WINDOW = 504  # 2 years
```

### Moderate (Balanced):
```python
USE_ROLLING_HEDGE_RATIO = True
HEDGE_RATIO_WINDOW = 252  # 1 year (default)
```

### Aggressive (Faster Adaptation):
```python
USE_ROLLING_HEDGE_RATIO = True
HEDGE_RATIO_WINDOW = 126  # 6 months
```

### Static (Original Method):
```python
USE_ROLLING_HEDGE_RATIO = False
```

## Visualization

When rolling hedge ratio is enabled, the notebook will display:
1. A plot showing how the hedge ratio evolves over time
2. Statistics on hedge ratio variability (mean, std, min, max)
3. The spread calculated using the time-varying hedge ratio

## Example Output

```
======================================================================
ROLLING HEDGE RATIO CALCULATION
======================================================================
Window: 252 days (~1.0 years)
Calculating rolling beta for each day...

Hedge Ratio Statistics:
Mean: 1.0234
Std Dev: 0.0156
Min: 0.9845
Max: 1.0678
Latest: 1.0312
======================================================================
```

## Technical Details

The rolling hedge ratio is calculated using Ordinary Least Squares (OLS) regression:

```python
for i in range(HEDGE_RATIO_WINDOW, len(df)):
    window_data = df.iloc[i-HEDGE_RATIO_WINDOW:i]
    model = sm.OLS(window_data['close_Asset1'], window_data['close_Asset2'])
    results = model.fit()
    hedge_ratio[i] = results.params[0]
```

The spread is then calculated using the time-varying hedge ratio:
```python
spread(t) = Asset1(t) - hedge_ratio(t) × Asset2(t)
```

## Comparison with Static Method

You can easily compare both methods by running the notebook twice:
1. First with `USE_ROLLING_HEDGE_RATIO = False`
2. Then with `USE_ROLLING_HEDGE_RATIO = True`

Compare the final performance metrics to see which works better for your asset pair.

## Notes

- The first `HEDGE_RATIO_WINDOW` days will have NaN values for the hedge ratio
- Trading signals will only be generated after sufficient data is available
- The rolling hedge ratio plot helps visualize relationship stability
- If the hedge ratio is highly variable, the cointegration relationship may be weak

## Questions?

If you have questions about this feature or need help optimizing the parameters for your specific asset pair, please refer to the main notebook documentation or the cointegration analysis section.
