import time
import threading # We need this for threads!

def long_task_threaded():
    print("Long task: Running Starting... (This will take 3 seconds)")
    time.sleep(3) # Simulate a 3 second wait
    print("Long task: Finished!")

def short_task_threaded():
    print("Short task: Running quickly.)")
    time.sleep(0.5) # Simulate a small delay
    print("Short task: Finished in main programm.")   

print("--- Program WITH Threads ---")
# 1. Create a new thread to run our long task
background_thread = threading.Thread(target=long_task_threaded)

# 2. Start the new thread. It begins running CONCURRENTLY !
background_thread.start()

# 3. Meanwhile, the main programme continues running other things
short_task_threaded() 
short_task_threaded() # Run it again to show it's not blocked

# 4. Wait for the background thread to finish before the main program
background_thread.join()

print("--- Program WITH Threads Done ---")