import data
import panel as pn
import numpy as np
import pandas as pd

pn.extension()
pn.extension(notifications=True)

    
class ModelSelectorView:
    def __init__(self, models =[], performance_df = pd.DataFrame(), masterFilter=[] , globs = dict() ):
        
        self.masterFilter = masterFilter
        self.performance_df = performance_df
        self.allModels = models
        self.globals = globs 
        self.displayed_models = self.allModels 
        self.selected = []
        self.setup_widgets()
        self.setup_callbacks()
        self.layout = self.create_layout()

    def setup_widgets(self):
        self.model_selector = pn.widgets.Select(name='Select Model', options=self.allModels,  size=10)
        self.sort_selector = pn.widgets.Select(name='Sort by:', options=['AIC', 'BIC', 'AUC_InS', 'AUC_OutS'], value='AIC', width=100)
        self.show_top_5_button = pn.widgets.Button(name='Top 5', button_type='primary')
        self.show_top_10_button = pn.widgets.Button(name='Top 10', button_type='primary')
        self.show_top_20_button = pn.widgets.Button(name='Top 20', button_type='primary')
        self.show_all_button = pn.widgets.Button(name='All', button_type='primary')
        self.refresh_button = pn.widgets.Button(name='Refresh', width=100)
        self.show_selected_button = pn.widgets.Button(name='Selected', button_type='warning', disabled=False, visible=True)
        self.select_button = pn.widgets.Button(name="Select", button_type="primary")
        self.remove_button = pn.widgets.Button(name="Remove", button_type="danger")
        self.remove_all_button = pn.widgets.Button(name="Remove All", button_type="warning")
        self.basket_display = pn.widgets.TextAreaInput(name='Selected Models', value='', disabled=True, height=120)

    def setup_callbacks(self):
        self.show_top_5_button.on_click(self.update_model_selector)
        self.show_top_10_button.on_click(self.update_model_selector)
        self.show_top_20_button.on_click(self.update_model_selector)
        self.show_all_button.on_click(self.update_model_selector)
        self.refresh_button.on_click(self.refresh_selector)
        self.show_selected_button.on_click(self.update_model_selector)
        self.select_button.on_click(self.add_to_basket)
        self.remove_button.on_click(self.remove_from_basket)
        self.remove_all_button.on_click(self.clear_basket)
        self.sort_selector.param.watch(self.update_model_options, 'value')
    

    def create_layout(self):
        self.model_selector_pane = pn.panel(self.model_selector)  # Wrap the widget

        return pn.Column(
            self.sort_selector,
            pn.Row(self.show_top_5_button, self.show_top_10_button, self.show_top_20_button, self.show_all_button),
            pn.Row(self.refresh_button, self.show_selected_button),
            self.model_selector_pane,
            pn.Row(self.select_button, self.remove_button, self.remove_all_button),
            self.basket_display
        )
    
    def view(self):
        return self.layout
    
    def setMasterFilter(self, filt):
        self.masterFilter = filt
        
    
    def update_model_selector(self, event): 
    
        sort_by = self.sort_selector.value
         
        sort_ascending = True if sort_by in ['AIC', 'BIC'] else False
        sorted_models = self.performance_df.sort_values(by=sort_by, ascending=sort_ascending).index.tolist()
        
        if len(self.masterFilter):
            sorted_models = [m for m in sorted_models if m in self.masterFilter]        
              
        par = event.obj.name.split()    
        if len(par) > 1:
            top = int(par[1])
            sorted_models = sorted_models[:top]
        
        if event.obj.name == 'Selected':
            self.selected_view = True            
            sorted_models = self.selected    
        else:
            self.selected_view = False
            
        self.displayed_models =  sorted_models

        self.model_selector.options = self.displayed_models
        if self.model_selector.options:
            self.model_selector.value =self.model_selector.options[0]  # Automatically select the first one
        else:
            # print("doesnt have models")
            self.model_selector.value = ''

            
    # Function to reload your data
    def refresh_selector(self, event):
        self.displayed_models = self.allModels
        self.update_model_options(event = None)        
        

    # Function to update the options of model_selector based on sort_selector
    def update_model_options(self, event = None):
        
        sort_by = event.new if event else self.sort_selector.value # The new value of sort_selector
         
        sort_ascending = True if sort_by in ['AIC', 'BIC'] else False  # Ascending for AIC and BIC, else descending

        # Sort the models based on the criterion
        sorted_models = self.performance_df.sort_values(by=sort_by, ascending=sort_ascending).index.tolist()
        self.displayed_models = sorted(self.displayed_models, key=sorted_models.index)
        
        if len(self.masterFilter):
            self.displayed_models = [m for m in self.displayed_models if m in self.masterFilter] 

        # Update the model_selector options
        self.model_selector.options = self.displayed_models

        # Explicitly set the value of model_selector to trigger an update
        self.model_selector.value = self.displayed_models[0]

        
    # Function to add the selected model to the basket
    def add_to_basket(self, event):
        current_selection = self.model_selector.value
        if current_selection not in self.selected:
            self.selected.append(current_selection)
            # Update the basket_display with the new selection
            self.basket_display.value = '\n'.join(self.selected)
            
    # Function to remove the selected model from the basket
    def remove_from_basket(self, event):
        current_selection = self.model_selector.value
        if current_selection in self.selected:
            self.selected.remove(current_selection)            
            # Update the basket_display after removal
            self.basket_display.value = '\n'.join(self.selected)          
        else:
            # Notify if the model isn't in the basket
            pn.state.notifications.warning('Not in the selected list.', duration=4000);

        
    # Function to clear the basket
    def clear_basket(self, event):
        self.selected.clear()
        self.basket_display.value = ''

def create_app():    
 
    

 
    performance_df = data.get_performace_df()
    summary_df = data.get_summary_df()
    model_ids, df = data.get_model_df()

    global_vars = {
    'current_active_tab': 0  ,
    'info_max_height': 200,
    'plot_height': 400,
    }
    modelSelectorView = ModelSelectorView(models = model_ids,
                                          performance_df = performance_df , globs = global_vars)

    return modelSelectorView.view()
    
if __name__=="__main__":
    
    
    import data
    import os 

    os.environ['BOKEH_ALLOW_WS_ORIGIN'] = '10.0.0.58,localhost'
    
    # app = create_app()
    server = pn.serve(create_app, port=8001, show=True, admin=True)
    # server = pn.serve(create_app, port=8001, show=True, admin=True)

    # modelSelectorView.view()