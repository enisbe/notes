import pandas as pd

# Sample dataframe
df = pd.DataFrame({
    'GROUP': ['A', 'A', 'B', 'B', 'B', 'C', 'C'],
    'FEATURE': ['var1', 'bar', 'var2', 'sar', 'tar', 'bar', 'var3']
})

def contains_substring(series, substring):
    """Custom aggregation function to check if any string in the series contains the given substring."""
    return any(substring in feature for feature in series)

def group_contains_feature(df, group_col, feature_col, substring):
    """Function to determine if each group contains any features with the given substring."""
    result = df.groupby(group_col)[feature_col].agg(contains_substring, substring=substring).reset_index()
    result.columns = [group_col, f'CONTAINS_{substring.upper()}']
    return result

# Call the function, searching for groups containing the substring "var"
result = group_contains_feature(df, 'GROUP', 'FEATURE', 'var')
print(result)
