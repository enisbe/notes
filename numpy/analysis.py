import numpy as np
import pandas as pd

# Example data
new_process = pd.Series([100, 200, 300, np.nan, 500], index=['a', 'b', 'c', 'd', 'e'])
old_process = pd.Series([99.9, 201, np.nan, 400, 500], index=['a', 'b', 'c', 'f', 'e'])

# Combine series into a DataFrame for easier comparison
df = pd.DataFrame({'new_process': new_process, 'old_process': old_process})

# Calculate absolute difference
df['abs_diff'] = abs(df['new_process'] - df['old_process'])

# Calculate relative difference (percentage)
df['rel_diff'] = (df['abs_diff'] / df['new_process']) * 100

# Filter approximate matches (difference ≤ 0.1%)
approx_matches = df[df['rel_diff'] <= 0.1]

# Largest differences
largest_diff = df.sort_values('abs_diff', ascending=False).dropna(subset=['abs_diff']).iloc[0]

# Smallest differences (excluding exact matches)
smallest_diff = df[df['abs_diff'] > 0].sort_values('abs_diff').iloc[0]

# Handle NAs (rows with no match)
no_match = df[df['new_process'].isna() | df['old_process'].isna()]

# Output results
print("Approximate matches (≤ 0.1%):")
print(approx_matches)
print("\nLargest difference:")
print(largest_diff)
print("\nSmallest difference:")
print(smallest_diff)
print("\nNo match (NAs):")
print(no_match)
