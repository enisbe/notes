import pandas as pd

# Assuming df is your DataFrame
# Create bins for fico1 and fico2
bins = range(0, 850, 20)
df['fico1_bin'] = pd.cut(df['fico1'], bins=bins)
df['fico2_bin'] = pd.cut(df['fico2'], bins=bins)

# Create a pivot table with fico1_bin as columns and fico2_bin as index, using 'account' to count
pivot_table = pd.pivot_table(df, index='fico2_bin', columns='fico1_bin', values='account', aggfunc='count', fill_value=0)

# Calculate the percentage of row total
pivot_table_percentage = pivot_table.div(pivot_table.sum(axis=1), axis=0) * 100

# Print the result
print(pivot_table_percentage)



import pandas as pd
import matplotlib.pyplot as plt

# Assuming df is your DataFrame
# Create bins for fico1, fico2, and fico3
bins = range(0, 850, 20)
df['fico1_bin'] = pd.cut(df['fico1'], bins=bins)
df['fico2_bin'] = pd.cut(df['fico2'], bins=bins)
df['fico3_bin'] = pd.cut(df['fico3'], bins=bins)

# Create a new DataFrame with counts for each fico1 bin
result_df = df.groupby('fico1_bin').agg(
    fico2_count=pd.NamedAgg(column='fico2_bin', aggfunc='count'),
    fico3_count=pd.NamedAgg(column='fico3_bin', aggfunc='count')
).reset_index()

# Calculate the cumulative percentage for fico2 and fico3 counts
total_count = len(df)
result_df['fico2_cumulative_%'] = result_df['fico2_count'].cumsum() / total_count * 100
result_df['fico3_cumulative_%'] = result_df['fico3_count'].cumsum() / total_count * 100

# Plot the cumulative percentages
plt.plot(result_df['fico1_bin'].astype(str), result_df['fico2_cumulative_%'], label='FICO2 Cumulative %')
plt.plot(result_df['fico1_bin'].astype(str), result_df['fico3_cumulative_%'], label='FICO3 Cumulative %')
plt.xlabel('FICO Bin')
plt.ylabel('Cumulative %')
plt.legend()
plt.xticks(rotation=45)
plt.show()
