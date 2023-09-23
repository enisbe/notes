
import pandas as pd
import data
import panel as pn
import numpy as np
import pandas as pd
from datetime import datetime 

pn.extension()
pn.extension('tabulator')
pn.extension(notifications=True)

class FormSidebar:
    def __init__(self, model, features_df, process_queue = pd.DataFrame()):
        self.model = model
        self.features_df = features_df
        self.process_queue = process_queue
        self.model_options = self.features_df['Model ID'].unique().tolist()
        self.all_features  = self.features_df['Variable'].unique().tolist()
        
        self.add_options = []
        self.remove_options = []
        self.add_features = []
        self.remove_features = []
        

        self.setup_widgets()
        self.setup_callbacks()
        self.layout = self.create_layout()
        self.set_model_features(self.model)
        self.features_options()
        
        
    def setup_widgets(self):
        self.model_id_text = pn.widgets.Select(name='Model ID', options =self.model_options, value=self.model, disabled=True)
        self.change = pn.widgets.Button(name='Change', width=100)
 
        self.add_features_input = pn.widgets.MultiChoice(name='Add Features (CSV)', value=[], options=self.add_options)
        self.remove_features_input = pn.widgets.MultiChoice(name='Remove Features (CSV)',  value=[], options=self.remove_options)
        self.preview_button = pn.widgets.Button(name='Preview', width=100)
        self.ok_button = pn.widgets.Button(name='OK', width=100)
        self.cancel_button = pn.widgets.Button(name='Cancel', width=100)
        self.preview_output = pn.pane.Markdown("### Model Preview")
        self.df_display = pn.widgets.Tabulator(self.get_current_model(self.model), show_index=False) 
                                               # show_index=False, width =200,
                                               # fit_columns=True ,text_align='center', align='center')


    def setup_callbacks(self): 
        self.model_id_text.param.watch(self.update_model, 'value')
        self.preview_button.on_click(self.preview_changes)
        self.ok_button.on_click(self.ok_func)
        self.cancel_button.on_click(self.cancel_func)
        self.change.on_click(self.change_model)

    def create_layout(self):
        col1 = pn.Column(
            self.model_id_text,
            self.change,
            self.add_features_input,
            self.remove_features_input,
            self.preview_button,                        
            pn.Row(self.ok_button, self.cancel_button),
            visible=True
        )
        col2 = pn.Column(self.preview_output, self.df_display)
        return pn.Row(col1, col2)
    
    def view(self):
        return self.create_layout()
    
    def get_current_model(self, model):
        model_vars  = self.features_df[self.features_df['Model ID'] == model][['Variable']]
        model_vars.columns =  [model]      
        return model_vars

    def update_model(self, model):        
        self.model =  model.new
        # self.df_display.object = self.get_current_model(self.model) # For Pandas Dataframe

        self.df_display.value = self.get_current_model(self.model)
        self.set_model_features(self.model)
        self.features_options()
        self.model_id_text.disabled = True
        
    def set_model_features(self, model):
        self.model_features =  self.features_df[self.features_df['Model ID'] == self.model]['Variable'].tolist()
        
    def features_options(self):
        self.add_options =  list(set(self.all_features) - set(self.model_features))
        self.remove_options = self.model_features
        self.add_features_input.options = self.add_options
        self.remove_features_input.options  = self.remove_options
    
    def change_model(self, event):
        if self.model_id_text.disabled:
            self.model_id_text.disabled = False
        else:
            self.model_id_text.disabled = True
        
    def preview_changes(self, event):
        
        current_features = self.get_current_model(self.model)
        current_vars =current_features[self.model].tolist()
    
        add_features = self.add_features_input.value
        remove_features = self.remove_features_input.value
        
        for f in add_features:
            if f not in current_vars:
                current_vars.append(f)
        for f in remove_features:
            if f in remove_features:
                current_vars.remove(f)
        
        new_id = self.model + "_1"
        
        new_model =  pd.DataFrame(current_vars, columns = [new_id])                 
        
        preview_df = current_features.merge(new_model , left_on=[self.model] ,how='outer', right_on =[new_id] )
        
        self.df_display.value = preview_df
    
    
    def clear_and_disable(self, event=None):
        # Here you can add code to enable all fields of the form
        # return_value = self.model_id_text.value         
        # self.model_id_text.value = return_value
        self.add_features_input.value = []
        self.remove_features_input.value = [] 
        # self.preview_output.visible = False
        self.df_display.value = self.get_current_model(self.model_id_text.value)
      

    def ok_func(self, event):

        current_features = self.get_current_model(self.model)
        current_vars =current_features[self.model].tolist()
    
        add_features = self.add_features_input.value
        remove_features = self.remove_features_input.value
        
        for f in add_features:
            if f not in current_vars:
                current_vars.append(f)
        for f in remove_features:
            if f in remove_features:
                current_vars.remove(f)
        
        new_id = self.model + "_1"
        
        # record = {
        # "model_id": [new_id],
        # "features": [current_vars],
        # }
        
        #  = pd.concat([self.process_queue, new_model], ignore_index=True)
        # new_model =  pd.DataFrame(record)                 
        
        added_to_queue = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        index = len(self.process_queue)
        
        self.process_queue.loc[index] = [new_id, 'run_new_model', current_vars, added_to_queue] 
        pn.state.notifications.success(f'{new_id} Added to Queue .', duration=2000)
        self.clear_and_disable()
        
        
    def cancel_func(self, event):
        self.clear_and_disable()

        
        
        
def create_app():
    import data
    performance_df = data.get_performace_df()
    summary_df = data.get_summary_df()
    model_ids, df = data.get_model_df()

    global_vars = {
    'current_active_tab': 0  ,
    'info_max_height': 200,
    'plot_height': 400,
    }
    process_queue = pd.DataFrame(columns=["model_id", "features"])

    form = FormSidebar('101', summary_df, process_queue)
    return form 

     
    
if __name__=="__main__":
    
    
    import data
    import os 

    os.environ['BOKEH_ALLOW_WS_ORIGIN'] = '10.0.0.58,localhost'
    
    # app = create_app()
    # server = pn.serve(create_app, port=8001, show=True, admin=True)
    # server = pn.serve(create_app, port=8001, show=True, admin=True)

    # modelSelectorView.view()        

    a = FormSidebar('101', summary_df)
    a.view()