import panel as pn

class PaneTextEditorToggle(pn.Column):
    def __init__(self, initial_content, **params):
        # The text content that'll be used in the editor and shown in the pane
        self.content = initial_content

        # The editor where text can be edited
        self.editor = pn.widgets.TextEditor(value=self.content,                                             
                                            min_height=150,
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