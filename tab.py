import panel as pn
import pandas as pd
import threading

class TabulatorView:
    def __init__(self, filter_callback, runModels_callback, data1, data2):
        self.data1 = data1
        self.data2 = data2
        self.alert_placeholder = pn.Column(min_height=80, sizing_mode='stretch_width')
        self.table1 = pn.widgets.Tabulator(value=data1, layout="fit_columns")
        self.table2 = pn.widgets.Tabulator(value=pd.DataFrame(), layout="fit_columns", visible=False)
        
        self.btn = pn.widgets.Button(name="Filter and Show Details", button_type="primary")
        self.runModels = pn.widgets.Button(name="Run Models", button_type="primary")
        self.applyFilter = pn.widgets.Button(name="Apply Filter", button_type="primary")
        
        
        self.btn.on_click(self.filter_data)
        self.applyFilter.on_click(self._callback_filter)
        self.runModels.on_click(self._callback_runmodels)
        
        self.applyfilter_callback = filter_callback
        self.runModels_callback = runModels_callback
        
        
      
    def show_alert(self, message, alert_type, duration=None):
        alert = pn.pane.Alert(message, alert_type=alert_type, width_policy='max')
        self.alert_placeholder.append(alert)
        
        if duration:
            timer = threading.Timer(duration, self.hide_alert, args=[alert])
            timer.start()
        
    def filter_data(self, event):
        if len(self.table1.selection) > 1:
            self.show_alert('**Warning:** More Than 1 Model is selected', 'danger', 5)
            self.table2.visible = False
            return
        
        selected_rows = self.table1.selected_dataframe
        if not selected_rows.empty:
            selected_id = selected_rows.iloc[0]['ID']
            filtered_data = self.data2[self.data2['ID'] == selected_id]
            self.table2.visible = True
            self.table2.value = filtered_data

    def _callback_filter(self, event):
        print("here")
        self.applyfilter_callback(self.table1.selected_dataframe.index.values)
    
    def _callback_runmodels(self, event):
        
        self.runModels_callback(self.table1.selected_dataframe.index.values)
        
            


    def hide_alert(self, alert):
        self.alert_placeholder.remove(alert)

    def view(self):
        return pn.Column(self.alert_placeholder, 
                         self.table1, 
                         pn.Row(self.btn, self.applyFilter, self.runModels), 
                         self.table2)

if __name__ == "__main__":
    # Sample data
    data1 = pd.DataFrame({
        'Name': ['John', 'Alice', 'Bob'],
        'ID': [1, 2, 3]
    })

    data2 = pd.DataFrame({
        'ID': [1, 1, 2, 2, 3, 3],
        'Details': ['A', 'B', 'C', 'D', 'E', 'F']
    })
    
    def func1(models):
        print("C1", models, type(models))
        
    def func2(models):
        print('C2', models)
        
    dashboard = Dashboard(func1, func2, data1=data1, data2 = data2)
    # dashboard.view().servable()
