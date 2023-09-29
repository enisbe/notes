import panel as pn
import matplotlib.pyplot as plt

class ModelPlotter:
    def __init__(self, performance_collection, model_ids):
        self.performance_collection = performance_collection
        self.model_ids = model_ids
        
        self.model_selector3 = pn.widgets.Select(name='Model Selector', options=self.model_ids[:-1])
        self.data_selector2 = pn.widgets.Select(name='Data Selector', options=list(self.performance_collection.keys()))
        
    def plot_segment_data(self, df, segment, model_id):
        plots = pn.Row()
        last_index = df.index.names[-1]
        
        for sample_type in ['In-Sample', 'Out-of-Sample']:
            selected_data = df.loc[(segment, sample_type, slice(None)), [model_id, 'Actual']]
            selected_data = selected_data.reset_index().set_index(last_index)
            selected_data = selected_data.sort_values(by=last_index)
            
            fig, ax = self._prepare_plot(selected_data, model_id, sample_type, segment)
            plots.append(pn.pane.Matplotlib(fig, tight=True))
        return plots
    
    def plot_data(self, df, model_id):
        plots = pn.Row()
        last_index = df.index.names[-1]
        
        for sample_type in ['In-Sample', 'Out-of-Sample']:
            selected_data = df.loc[(sample_type, slice(None)), [model_id, 'Actual']]
            selected_data = selected_data.reset_index().set_index(last_index)
            selected_data = selected_data.sort_values(by=last_index)
            
            fig, ax = self._prepare_plot(selected_data, model_id, sample_type, "ALL")
            plots.append(pn.pane.Matplotlib(fig, tight=True))
        return plots
    
    def _prepare_plot(self, selected_data, model_id, sample_type, segment):
        fig, ax = plt.subplots(figsize=(4, 2.5))
        
        ax.plot(selected_data.index, selected_data['Actual'], label="Actual")
        ax.plot(selected_data.index, selected_data[model_id], label=f"{model_id}", linestyle='--')
        
        ax.set_title(f"{model_id} vs Actual ({sample_type} - {segment})", fontsize=9)
        ax.legend(loc='upper left', fontsize=7)
        ax.set_xlabel(selected_data.index.name, fontsize=7)
        ax.set_ylabel("Value", fontsize=7)
        
        ax.tick_params(axis='x', labelsize=7)
        ax.tick_params(axis='y', labelsize=7)   
        plt.xticks(rotation=45)
        
        plt.close(fig)
        
        return fig, ax
    
    def update_plots_for_segments(self, event1=None, event2=None):
        model_id = self.model_selector3.value
        data = self.data_selector2.value
        col = pn.Column()
        
        df = self.performance_collection[data]
        levels = len(df.index.names)
        
        if levels > 2:
            for segment in df.index.get_level_values(0).unique():
                col.append(pn.Row(pn.pane.Markdown(f"## {segment}"), self.plot_segment_data(df, segment, model_id)))
        else:
            col.append(pn.Row(pn.pane.Markdown(f"## ALL"), self.plot_data(df, model_id)))
        return col

    def third_tab_layout(self):
        top_row = pn.Row(self.model_selector3, self.data_selector2, pn.pane.Markdown("## Model Summary"))
        layout = pn.Column(top_row, pn.panel(pn.bind(self.update_plots_for_segments, self.model_selector3, self.data_selector2)))
        return layout

# Sample data
# performance_collection = ...
# model_ids = ...

viewer = ModelPlotter(performance_collection, model_ids)
third_tab = viewer.third_tab_layout()
third_tab
