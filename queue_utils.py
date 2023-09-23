import panel as pn
import pandas as pd
from datetime import datetime
import time
import threading
import logging

pn.extension('tabulator')

logging.basicConfig(level=logging.INFO)

class QueueTracker:

    def __init__(self, process_queue):
        self.process_queue = process_queue
        self.processed_queue = pd.DataFrame(columns=["model_id", 'function', "features", 'added_to_queue', 'start_time',  "completed_time"])

        # Tabulator tables
        self.process_table = pn.widgets.Tabulator(self.process_queue,layout ='fit_data')
        self.processed_table = pn.widgets.Tabulator(self.processed_queue, layout ='fit_data')

        # Start the periodic callback
        self.callback_id = pn.state.add_periodic_callback(self.update_tables, period=1000)  # Update every second

    def update_tables(self):
        # Update process_table
        self.process_table.value = self.process_queue.copy()
        
        # Update processed_table
        self.processed_table.value = self.processed_queue.copy()

    def mark_processed(self, record, startTime):
        """
        Mark a record as processed. It will remove the record from process_queue and 
        add it to the processed_queue with the time of completion.
        """
       
        # Add to processed_queue
        print(record)
        record['start_time'] = startTime
        record['completed_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        proccesed =  pd.DataFrame([record])    
       
        self.processed_queue = pd.concat([self.processed_queue, proccesed], ignore_index=True)
 

    def view(self):
        """Display the tables."""
        return pn.Column(
            pn.pane.Markdown("## Process Queue"),
            self.process_table,
            pn.pane.Markdown("## Processed Queue"),
            self.processed_table
        )


class QueueProcessor:

    def __init__(self, queue, tracker):
    
        self.queue = queue
        self.tracker = tracker
        self.stop_event = threading.Event()

    def process(self):
        while not self.stop_event.is_set():
            if not self.queue.empty:
                # Process the first row (or use the last row based on your preference)
                record = self.queue.iloc[0].to_dict()
                
                startTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                self.process_record(record)
                
                # Notify QueueTracker
                self.tracker.mark_processed(record, startTime)
                
                # Remove the processed row from the queue
                self.queue.drop(self.queue.index[0], inplace=True)
            else:
                # logging.info("Queue is empty. Sleeping...")
                time.sleep(5)  # Sleep for a while if the queue is empty

    def process_record(self, record):
        # Your processing logic here
        time.sleep(2)
        logging.info("enter_processor")
        logging.info(record)
        time.sleep(5)  # For simulation, you can remove this later
        logging.info("Process Completed")
        
        
    def start(self):
        self.thread = threading.Thread(target=self.process)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()
        
        
if __name__ == "__main__":
    
    
    from  formviewer import *
    import data
    performance_df = data.get_performace_df()
    summary_df = data.get_summary_df()
    model_ids, df = data.get_model_df()

    global_vars = {
    'current_active_tab': 0  ,
    'info_max_height': 200,
    'plot_height': 400,
    }
    
    process_queue = pd.DataFrame(columns=["model_id", "function", "features", "added_to_queue"])
 
    tracker = QueueTracker(process_queue)

    if 'processor' in globals():
        processor.stop()
    
    processor = QueueProcessor(process_queue, tracker)
    processor.start()
    
    tracker.view()
 

    index = len(process_queue)
    process_queue.loc[index] = ['Model_1', 'new_run',['var1', 'var3'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')] 
