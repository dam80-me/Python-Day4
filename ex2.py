import time

def long_task():
    print("Long task: Starting... (This will take 3 seconds)")
    time.sleep(3) # Simulate a 3 second wait
    print("Long task: Finished!")

def short_task():
    print("Short task: Running quickly.)")
    time.sleep(0.5) # Simulate a small delay
    print("Short task: Finished!")   

print("--- Program WITHOUT Threads ---")

short_task() # Run the short task first
long_task()  # Then run the long task (program will pause here)
short_task() # Then run the short task again, after the long one finishes

print("--- Program WITHOUT Threads Done ---")