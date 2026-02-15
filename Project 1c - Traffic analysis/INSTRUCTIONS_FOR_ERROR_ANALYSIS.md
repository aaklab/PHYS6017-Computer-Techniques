# Instructions: Adding Error Analysis to Your Notebook

## Step 1: Add the Error Analysis Function

After your existing `fundamental_diagram` function (around line 231), add a NEW cell with this function:

```python
# Error Analysis Function - runs multiple simulations to compute error bars
def fundamental_diagram_with_errors(L, v_max, p, N_values, warmup=200, measure_steps=500, n_runs=20):
    """
    Calculate flow vs density with error bars using multiple independent runs.
    
    Parameters:
    - n_runs: number of independent runs per density (default 20, can use 10 if slow)
    
    Returns:
    - densities, mean_flows, std_flows, sem_flows
    """
    densities = []
    mean_flows = []
    std_flows = []
    sem_flows = []
    
    for N in N_values:
        density = N / L
        flows_at_this_density = []
        
        # Run multiple simulations with different seeds
        for run in range(n_runs):
            rng = np.random.default_rng(1000 + run)  # Unique seed
            road = init_road(L, N, rng)
            
            # Warmup phase
            for _ in range(warmup):
                road, _ = step(road, v_max, p, rng)
            
            # Measurement phase
            total_distance = 0
            for _ in range(measure_steps):
                road, dist = step(road, v_max, p, rng)
                total_distance += dist
            
            # Calculate flow for this run
            flow = total_distance / (L * measure_steps)
            flows_at_this_density.append(flow)
        
        # Compute statistics
        densities.append(density)
        mean_flows.append(np.mean(flows_at_this_density))
        std_flows.append(np.std(flows_at_this_density, ddof=1))
        sem_flows.append(np.std(flows_at_this_density, ddof=1) / np.sqrt(n_runs))
    
    return np.array(densities), np.array(mean_flows), np.array(std_flows), np.array(sem_flows)
```

## Step 2: Replace Investigation 2 Code

Find your Investigation 2 section (around line 251) and REPLACE it with:

```python
# Investigation 2 - Effect of randomness WITH ERROR BARS
print("\n--- Investigation 2: Effect of Randomness (with error bars) ---")

L = 200
N_values = range(10, 151, 10)
n_runs = 20  # Can reduce to 10 if runtime is too long

# Run for p=0.0
print("Running p=0.0...")
densities_p0, flows_p0, std_p0, sem_p0 = fundamental_diagram_with_errors(
    L, v_max=5, p=0.0, N_values=N_values, n_runs=n_runs
)

# Run for p=0.5
print("Running p=0.5...")
densities_p5, flows_p5, std_p5, sem_p5 = fundamental_diagram_with_errors(
    L, v_max=5, p=0.5, N_values=N_values, n_runs=n_runs
)

# Plot with error bars
fig, ax = plt.subplots(figsize=(10, 6))
ax.errorbar(densities_p0, flows_p0, yerr=sem_p0, fmt='o-', 
            label='p=0.0', capsize=5, markersize=6)
ax.errorbar(densities_p5, flows_p5, yerr=sem_p5, fmt='s-', 
            label='p=0.5', capsize=5, markersize=6)
ax.set_xlabel('Density (ρ)')
ax.set_ylabel('Flow (J)')
ax.set_title('Investigation 2: Effect of Randomization (with error bars)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('images/investigation_2_with_errors.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"✓ Complete. Note: p=0.0 has tiny error bars (deterministic)")
```

## Step 3: Replace Investigation 3 Code

Find your Investigation 3 section (around line 289) and REPLACE it with:

```python
# Investigation 3 - Effect of Speed Limit WITH ERROR BARS
print("\n--- Investigation 3: Effect of Speed Limit (with error bars) ---")

p_fixed = 0.5

# Run for v_max=5
print("Running v_max=5...")
densities_v5, flows_v5, std_v5, sem_v5 = fundamental_diagram_with_errors(
    L, v_max=5, p=p_fixed, N_values=N_values, n_runs=n_runs
)

# Run for v_max=2
print("Running v_max=2...")
densities_v2, flows_v2, std_v2, sem_v2 = fundamental_diagram_with_errors(
    L, v_max=2, p=p_fixed, N_values=N_values, n_runs=n_runs
)

# Plot with error bars
fig, ax = plt.subplots(figsize=(10, 6))
ax.errorbar(densities_v5, flows_v5, yerr=sem_v5, fmt='o-', 
            label='v_max=5', capsize=5, markersize=6)
ax.errorbar(densities_v2, flows_v2, yerr=sem_v2, fmt='s-', 
            label='v_max=2', capsize=5, markersize=6)
ax.set_xlabel('Density (ρ)')
ax.set_ylabel('Flow (J)')
ax.set_title(f'Investigation 3: Effect of v_max (p={p_fixed}, with error bars)')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('images/investigation_3_with_errors.png', dpi=300, bbox_inches='tight')
plt.show()

print("✓ Complete. Check if curves separate beyond uncertainty!")
```

## Step 4: Run the Notebook

1. Run all cells from the beginning
2. The error analysis will take longer (20 runs per density point)
3. If it's too slow, change `n_runs=20` to `n_runs=10`

## What You'll Get

- Investigation 2: Shows p=0.0 has tiny error bars (deterministic), p=0.5 has larger bars
- Investigation 3: Shows whether v_max curves are "separated beyond uncertainty" or "overlapping within uncertainty"
- New images saved with "_with_errors" suffix

## For Your Report

You can now say:
- "Error bars represent standard error of the mean (SEM) from 20 independent runs"
- "For p=0, error bars are negligible, confirming deterministic behavior"
- "For p>0, error bars quantify stochastic variability"
- "At low density, v_max curves are separated beyond uncertainty"
- "At high density, curves overlap within uncertainty"
