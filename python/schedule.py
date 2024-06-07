pip install schedule pytz

import schedule
import time
from datetime import datetime
import pytz

# Define the time zone
est = pytz.timezone('US/Eastern')

# Your task function
def job():
    print("Running scheduled task")
    # Replace this with your actual task code
    global condition_met
    if check_condition():
        condition_met = True

# Condition checking function
def check_condition():
    # Implement your condition checking logic here
    # Return True if the condition is met, else False
    return False

# Stop condition function
def stop_condition():
    current_time = datetime.now(est)
    end_time = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
    return current_time >= end_time or condition_met

condition_met = False

# Schedule the job every 5 minutes
schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    if stop_condition():
        print("Stopping scheduled task")
        break
    time.sleep(1)
