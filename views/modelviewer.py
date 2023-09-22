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
pn.extension(notifications=True)
    
    
class ModelViewer:
    
    def __init__(self, models, model_selector, performance_df=pd.DataFrame(), summary_df=pd.DataFrame(), df=pd.DataFrame(), global_vars = dict()):
        
        self.model_selector = model_selector
        self.performance_df = performance_df.copy()
        self.summary_df = summary_df
        self.df = df
        self.allModels = models
        self.globals = global_vars
        self.setup_widgets()
        self.setup_callbacks()
        self.layout = self.create_layout()
        
        

    def setup_widgets(self):
        self.spacer = pn.Spacer(width=50)
        self.spacerVertical = pn.Spacer(height=100)
        pass 
    
    def setup_callbacks(self):
        pass
 
    
    def create_layout(self):
        self.view_summary = pn.panel(pn.bind(self.show_model_info, self.model_selector), height=self.globals['info_max_height'], sizing_mode='stretch_width', scroll=True)
        self.view_plots = pn.panel(pn.bind(self.update_plots, self.model_selector))
        
        return pn.Column(self.view_summary, self.spacerVertical, self.view_plots)
    
    def view(self):
        return self.layout

    def show_model_info(self, model_id):
    
        if self.globals['current_active_tab'] != 0:  # if not "Main Content" tab
            return 
        
        if model_id in ['', None]:
            return pn.Column(pn.pane.Markdown("## No Model selected"))
        
        summary_info = self.summary_df.loc[self.summary_df['Model ID'] == model_id] 
        performance_info = self.performance_df.loc[[model_id]].reset_index()
        return pn.Column(
             pn.pane.DataFrame(performance_info, name='Model Performance'),
            self.spacer,
            pn.pane.DataFrame(summary_info, name='Model Summary')
        )
    
    def update_plots(self, model_id):
        if self.globals['current_active_tab'] != 0:  # if not "Main Content" tab
            return  # Don't make updates

        if model_id in ['', None]:
            return  

        # Create a Panel Row layout to put the In-Sample and Out-of-Sample plots side by side
        plots = pn.Row()

        for category in ['In-Sample', 'Out-of-Sample']:
            fig, ax = plt.subplots(figsize=(4, 2.5))

            # Get the data for the selected model and "Actual" based on category
            selected_data = self.df.loc[category, [model_id, 'Actual']]

            # Plot data
            ax.plot(selected_data.index, selected_data['Actual'], label="Actual")
            ax.plot(selected_data.index, selected_data[model_id], label=f"{model_id}", linestyle='--')

            # Compute the minimum and maximum values for the 'Actual' data
            min_val = self.df['Actual'].min() - 0.1 * abs(self.df['Actual'].min())
            max_val = self.df['Actual'].max() + 0.1 * abs(self.df['Actual'].max())
            ax.set_ylim([min_val, max_val])

            ax.set_title(f"{model_id} vs Actual ({category})",  fontsize=9)
            ax.set_xlabel("Date", fontsize=7)
            ax.set_ylabel("Value", fontsize=7)
            ax.legend(loc='upper left', fontsize=7)

            # Adjust the font size of the tick labels
            ax.tick_params(axis='x', labelsize=7)
            ax.tick_params(axis='y', labelsize=7)   
            plt.xticks(rotation=45)
            plt.close(fig)
            plots.append(pn.pane.Matplotlib(fig, tight=True))

        return plots

    def update_views(self, event):
        # This can be used to update other visual components or perform more actions when model_selector value changes.
        # For now, it's just a placeholder to indicate how you might handle such events.
        pass
    
    
def create_app():  
    performance_df = data.get_performace_df()
    summary_df = data.get_summary_df()
    model_ids, df = data.get_model_df()
    model_ids.remove('Actual')
    
    global_vars = {
    'current_active_tab': 0  ,
    'selected_models': [],
    
    'info_max_height': 200,
    'plot_height': 400,
    }

    modelSelectorView = ModelSelectorView(models = model_ids,
                                          performance_df = performance_df )
    
    viewTab = ModelViewer(models = model_ids, 
                          model_selector=modelSelectorView.model_selector, 
                          performance_df = performance_df, 
                          summary_df =  summary_df, 
                          df = df,
                          global_vars = global_vars)
     
    return pn.Row(modelSelectorView.view(), viewTab.view())
    
if __name__=="__main__":
    
    
    import data
    import os 

    os.environ['BOKEH_ALLOW_WS_ORIGIN'] = '10.0.0.58,localhost'
    server = pn.serve(create_app, port=8002, show=True, admin=True)
    # create_app()

 