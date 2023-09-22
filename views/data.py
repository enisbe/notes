import pandas as pd
import numpy as np


def get_model_df():
    # Create the sample DataFrame with 15 models
    np.random.seed(0)
    dates = pd.date_range("2021-01-01", periods=12, freq='M')
    model_ids = [str(i) for i in range(101, 116)]  # Model IDs from 101 to 115
    model_ids.append('Actual')  # Add 'Actual' to model_ids
    categories = ['In-Sample', 'Out-of-Sample']

    multi_index = pd.MultiIndex.from_product([categories, dates], names=['Category', 'Date'])
    df = pd.DataFrame(np.random.rand(len(multi_index), len(model_ids)), index=multi_index, columns=model_ids)
    df['Actual'] = df[model_ids[:-1]].mean(axis=1)  # Compute 'Actual' as the mean of other model columns
    return model_ids, df

def get_performace_df():

    # Create a DataFrame to hold performance summary for each of the 15 models
    np.random.seed(0)
    performance_data = {
        'Model ID': [str(i) for i in range(101, 116)],  # Model IDs from 101 to 115
        'AUC_InS': np.random.rand(15),
        'AUC_OutS': np.random.rand(15),
        'AIC': np.random.rand(15) * 20,
        'BIC': np.random.rand(15) * 20
    }

    performance_df = pd.DataFrame(performance_data).set_index('Model ID')

    # Add rank columns to the performance DataFrame
    performance_df['Rank AUC_InS'] = performance_df['AUC_InS'].rank(ascending=False)
    performance_df['Rank AUC_OutS'] = performance_df['AUC_OutS'].rank(ascending=False)
    performance_df['Rank AIC'] = performance_df['AIC'].rank(ascending=True)
    performance_df['Rank BIC'] = performance_df['BIC'].rank(ascending=True)
    return performance_df

def get_summary_df():
        # Create a DataFrame to hold summary information for each of the 15 models
    np.random.seed(0)
    summary_data = {
        'Model ID': [str(i) for i in range(101, 116)],  # Model IDs from 101 to 115
        'Variable1': np.random.rand(15),
        'Variable2': np.random.rand(15),
        'Variable3': np.random.rand(15)
    }

    summary_df = pd.DataFrame(summary_data).set_index('Model ID')
  
 

    # Initialize an empty list to collect data
    data_rows = []

    # Randomly generate data for 15 models
    np.random.seed(0)  # for reproducibility
    for model_id in range(101, 116):
        # Randomly decide the number of variables for this model (between 1 and 5)
        n_vars = np.random.randint(1, 6)

        # Randomly select variable names for this model
        variables = [f"var{np.random.randint(1, 16)}" for _ in range(n_vars)]

        # Generate mock data for each variable
        for variable in variables:
            coefficient = np.random.rand()
            p_value = np.random.rand()
            vif = np.random.rand() * 10  # just for example

            # Append the data row
            data_rows.append([str(model_id), variable, coefficient, p_value, vif])

    # Create a DataFrame
    summary_df = pd.DataFrame(data_rows, columns=["Model ID", "Variable", "Coefficient", "P-Value", "VIF"])
    return summary_df


performance_df = get_performace_df()
summary_df = get_summary_df()
model_ids, df_bydate = get_model_df()