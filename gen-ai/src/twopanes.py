import panel as pn
import glob 
from collections import OrderedDict
import src.doc_processing as processing 
import os 
from src.panetexteditor import PaneTextEditorToggle

class TwoPanes:
    def __init__(self, location, queue):
        self.location = location
        self.q = queue  
        
        # Define widgets and button action
        self.dropdown1 = pn.widgets.Select(name='Document', options=[os.path.splitext(file)[0] for file in self.get_filenames(['html'])])
        self.dropdown2 = pn.widgets.Select(name='Prompt', options=['Summarize with images', 'Summarize concise', 'Summarize detailed'])
        self.run_button = pn.widgets.Button(name='Summarize', button_type='primary')
        self.clear_button = pn.widgets.Button(name='Clear', button_type='primary')

        self.run_button.on_click(self.on_run_click)
        self.clear_button.on_click(self.on_clear_click)

        # Update whenever the dropdown value changes
        self.dropdown1.param.watch(lambda event: self.update_left_pane_content(), 'value')

        self.left_content = "<p>Left Pane Content...</p>"
        self.right_content = "<p>Summary Place Holder...</p>"
        # Content panes
        self.left_pane_content = pn.panel(self.left_content, 
                                          sizing_mode='stretch_both', 
                                          styles={'border-radius': '8px', 'overflow': 'auto'}, 
                                          min_height=150,
                                          margin=(5,5))

        # self.right_pane_content = pn.panel(self.right_content, 
        #                                    sizing_mode='stretch_both', 
        #                                    # styles={'background': '#f0f0f0', 'border-radius': '8px', 'overflow': 'auto'}, 
        #                                     styles={ 'border-radius': '8px', 'overflow': 'auto'}, 
        #                                    min_height=150,
        #                                    margin=(5,5)
        # )
        
        self.right_pane_content = PaneTextEditorToggle(self.right_content)
        
        self.update_left_pane_content()

    def get_filenames(self, extensions): 
        files = [file for ext in extensions for file in glob.glob(f"{self.location}/*.{ext}")]
        filenames  = OrderedDict()
        for file in files:
            filenames[os.path.basename(file)] = file
        return filenames  

    def update_left_pane_content(self):
        print("Update Left pane Content")
        file_path = os.path.join(f'{self.location}/{self.dropdown1.value}.html')
        with open(file_path, 'r', encoding='utf-8') as file:
            self.left_content = file.read()
        self.left_pane_content.object = self.left_content


    def _get_processing_content(self):
        return self.left_content

    def _get_right_content(self):
        return self.right_content        
 

    def on_run_click(self, event):   
        print("Clicked Run")
        self.right_pane_content.object = "<p><strong>Summarizing...</strong></p>"
    
        self.doc_parsed = processing.parse_html(self._get_processing_content())        
        self.right_pane_content.object = self.left_pane_content.object
        # processing.process_content_stream(self.doc_parsed , processing.text_processing, self.q)
        self.right_content = self.right_pane_content.object
        print("Done summarizing")
 
    def on_clear_click(self, event):
        self.right_pane_content.object = "<p>Summary Place Holder...</p>"
        
    def get_pane_layout(self):
        # Logic to get the final pane layout 
        run_button_col = pn.Column(pn.Spacer(height=10), 
                                   pn.Row(self.run_button, self.clear_button) , align="end", 
                                   sizing_mode='stretch_width')

        top_row = pn.Row(self.dropdown1, self.dropdown2, run_button_col,  align="end", sizing_mode='stretch_width')

        left_column = pn.Column(top_row, pn.layout.Divider(), self.left_pane_content, sizing_mode='stretch_both', margin=(5,5))
        right_column = pn.Column(self.right_pane_content, sizing_mode='stretch_both', margin=(5,5))

        tab1 = pn.GridSpec(sizing_mode='stretch_both', ncols=12, nrows=1,)
        tab1[0, :6] = left_column
        tab1[0, 6:] = right_column

        return tab1

    def view(self):
        return self.get_pane_layout()


class SimpleTwoPanes:
    
    def __init__(self, model):
        
        # Define widgets
        self.dropdown1 = pn.widgets.Select(name='Model', options=['text-bison'])       
        self.run_button = pn.widgets.Button(name='Submit', button_type='primary')
        self.run_button.on_click(self.on_run_click)
        
        # Left and Right Panes
        self.text_input_area = pn.widgets.TextAreaInput(name="Text Input", 
                                                        placeholder='Enter your text here...', 
                                                        min_width=600,      # Width in pixels
                                                        min_height=400,    # Height in pixels
                                                        sizing_mode='stretch_both')
        
        self.right_content = "<p>Response...</p>"
        
        self.right_panel_content =  pn.panel(self.right_content, 
                                              styles={'border-radius': '8px', 'overflow': 'auto'}, 
                                              sizing_mode='stretch_both')
        
        self.right_pane_container = pn.Column(pn.pane.Markdown("## Response:"), 
                                              pn.layout.Divider(),
                                              self.right_panel_content
                                            )
        
        self.model = model
        
    def on_run_click(self, event):
        self.right_panel_content.object = "<div></div>"
        self.right_panel_content.object = self.model.predict(self.text_input_area.value)

    def view(self):
        top_row = pn.Row(self.dropdown1, self.run_button, align="end", sizing_mode='stretch_width')
        layout = pn.Row(
            pn.Column(top_row, self.text_input_area, sizing_mode='stretch_both'),
            self.right_pane_container,
            sizing_mode='stretch_both'
        )
        return layout


class PaneTextEditorToggle(pn.Column):
    def __init__(self, initial_content, **params):
        # The text content that'll be used in the editor and shown in the pane
        self.content = initial_content

        # The editor where text can be edited
        self.editor = pn.widgets.TextEditor(value=self.content,                                             
                                            min_height=800,
                                            margin=(5,5))
        
        # The static pane view of the content
        self.pane_view = pn.panel(self.content, 
                                  styles={ 'border-radius': '8px', 'overflow': 'auto'}, 
                                  min_height=150,
                                 margin=(5,5))

        # Button to toggle between the two views

        self.toggle_button = pn.widgets.Button(name="Edit", width=100)
        # self.toggle_button_row = pn.Row(pn.HSpacer(), self.toggle_button)
        self.toggle_button_row = pn.Row(self.toggle_button, align='end')

        self.toggle_button.on_click(self.toggle_view)

        # Starting with the pane view by default
        super().__init__(self.toggle_button_row, self.pane_view)
        
    # This allows the parent class or any other classes to set or get the 'object' attribute of our custom class.
    @property
    def object(self):
        if self[1] == self.editor:
            return self.editor.value
        else:
            return self.pane_view.object

    @object.setter
    def object(self, value):
        self.content = value
        if self[1] == self.editor:
            self.editor.value = value
        else:
            self.pane_view.object = value

    def toggle_view(self, event):
        if self.toggle_button.name == "Edit":
            self.editor.value = self.pane_view.object
            self[1] = self.editor
            self.toggle_button.name = "View"
        else:
            # Update the pane view to reflect the current content of the editor
            self.pane_view.object = self.editor.value
            self[1] = self.pane_view
            self.toggle_button.name = "Edit"
        