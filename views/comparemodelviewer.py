import matplotlib
matplotlib.use('agg')

import data
import panel as pn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from modelselector import * 
plt.style.use('ggplot')
pn.extension()
 
 

class CompareModelViewer:
    def __init__(self, models,selected_models, df, performance_df, globs):
        self.model_ids = models 
        self.selected_models = selected_models
        self.df = df
        self.performance_df = performance_df
        self.globals = globs
 
        
        # Setup widgets
        self.setup_widgets()

        # Attach callbacks
        self.setup_callbacks()
        
    def setup_widgets(self):
        self.model_cross_selector = pn.widgets.CrossSelector(
            name='Select Models',
            options=self.selected_models,
            value=[]
        )
        self.sort_selector  = pn.widgets.Select(
            name='Sort by:',
            options=['AIC', 'BIC', 'AUC_InS', 'AUC_OutS'],
            value='AIC',
            width=100
        )
        self.summary_table  = pn.pane.DataFrame(pd.DataFrame(), name="Summary Table")
        
    def setup_callbacks(self):
        self.model_cross_selector.param.watch(self.update_dashboard, 'value')
        self.sort_selector.param.watch(self.update_model_sort, 'value')
        
 
        # Define callback functions to update the summary table and the plots
    def update_dashboard(self, event):
        if self.globals['current_active_tab'] != 1:
            return
        # Update summary table
        selected_models = event.new    

        performance_df_filtered = self.performance_df[self.performance_df.index.isin(selected_models)].reset_index() 

        sort_by = event.new if event else self.sort_selector.value # The new value of sort_selector
        sort_ascending = False if sort_by in ['AIC', 'BIC'] else True
        self.summary_table.object =performance_df_filtered.sort_values(by=self.sort_selector.value, ascending=sort_ascending)


    def update_model_sort(self, event=None):    
        if self.globals['current_active_tab'] != 1:
            return
        sort_by = event.new if event else self.sort_selector.value # The new value of sort_selector  
        sort_ascending = True if sort_by in ['AIC', 'BIC'] else False  # Ascending for AIC and BIC, else descending 
        selected_models = self.model_cross_selector.value     
        performance_df_filtered = self.performance_df[self.performance_df.index.isin(selected_models)].reset_index()
        self.summary_table.object = performance_df_filtered.sort_values(by=self.sort_selector.value, ascending=sort_ascending)

    
        
        
    def update_plots(self, selected_models):
        
        if self.globals['current_active_tab'] != 1:
            return
        
        plots = pn.Row()
        for category in ['In-Sample', 'Out-of-Sample']:
            fig, ax = plt.subplots(figsize=(4, 2.5))

            # Get the data for the "Actual" values based on category
            actual_data = self.df.loc[category, 'Actual']

            # Plot "Actual" data
            ax.plot(actual_data.index, actual_data, label="Actual")

            # Iterate over the selected models and plot each
            for model_id in selected_models:
                model_data = self.df.loc[category, model_id]
                ax.plot(model_data.index, model_data, label=f"{model_id}", linestyle='--')

            # Compute the minimum and maximum values for the 'Actual' data
            min_val = self.df['Actual'].min() - 0.1 * abs(self.df['Actual'].min())
            max_val = self.df['Actual'].max() + 0.1 * abs(self.df['Actual'].max())
            ax.set_ylim([min_val, max_val])

            ax.set_title(f"Models vs Actual ({category})",  fontsize=9)
            ax.set_xlabel("Date", fontsize=7)
            ax.set_ylabel("Value",  fontsize=7)
            ax.legend(loc='upper left', fontsize=7)

            # Adjust the font size of the tick labels
            ax.tick_params(axis='x', labelsize=7)
            ax.tick_params(axis='y', labelsize=7)   
            plt.xticks(rotation=45)
            plt.close(fig)
            plots.append(pn.pane.Matplotlib(fig, tight=True))

        return plots
        
    def view(self):
        return pn.Column(
            self.sort_selector ,
            pn.Row(self.model_cross_selector, self.summary_table ),
            pn.bind(self.update_plots, self.model_cross_selector)
        )

    
def create_app():  
    performance_df = data.get_performace_df()
    summary_df = data.get_summary_df()
    model_ids, df = data.get_model_df()
    model_ids.remove('Actual')
    
    global_vars = {
    'current_active_tab': 1  ,
    'info_max_height': 200,
    'plot_height': 400,
    }
    
    modelSelector = ModelSelectorView(models = model_ids,
                                          performance_df = performance_df )

    modelSelector.selected = ['101', '102']
    
    compareView = CompareModelViewer(models = model_ids,
                                     selected_models = modelSelector.selected, 
                                     df=df,
                                     performance_df = performance_df, 
                                     globs = global_vars)
    return compareView.view()

if __name__=="__main__":
    
    
    import data
    import os 

    os.environ['BOKEH_ALLOW_WS_ORIGIN'] = '10.0.0.58,localhost'
    server = pn.serve(create_app, port=8003, show=True, admin=True)
    # server.stop()
    # create_app()

 