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

# Create num of econ

import pandas as pd

# Sample dataframe
df = pd.DataFrame({
    'Model_ID': ['A', 'A', 'B', 'B', 'B', 'C', 'C'],
    'FEATURE': ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7'],
    'VAR_TYPE': ['ECON', 'ACCOUNT', 'ECON', 'ACCOUNT', 'OTHER', 'ACCOUNT', 'ECON']
})

def count_type(series, var_type):
    """Custom function to count occurrences of a specific VAR_TYPE."""
    return (series == var_type).sum()

# Use groupby and aggregate to count occurrences of ECON and ACCOUNT types for each Model_ID
result = df.groupby('Model_ID').agg(
    ECON_COUNT=('VAR_TYPE', lambda x: count_type(x, 'ECON')),
    ACCOUNT_COUNT=('VAR_TYPE', lambda x: count_type(x, 'ACCOUNT'))
).reset_index()

print(result)

# Create HAS_RUN column 

import pandas as pd

# Given dataframes
performance_df = pd.DataFrame({
    'Model_ID': ['A', 'A', 'B', 'B', 'B', 'C', 'C'],
    'FEATURE': ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7'],
    'VAR_TYPE': ['ECON', 'ACCOUNT', 'ECON', 'ACCOUNT', 'OTHER', 'ACCOUNT', 'ECON']
})

data = {
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9]
}
df = pd.DataFrame(data)

# Create new column 'HAS_RUN' by checking if 'Model_ID' exists in df columns
performance_df['HAS_RUN'] = performance_df['Model_ID'].isin(df.columns)

print(performance_df)
