
import time
import random
import threading
import os
import csv

# Global variable to control the emulation
is_running = True

# Ensure the data folder exists
os.makedirs("data", exist_ok=True)

def generate_data():
    """Function to generate data every 10 seconds and save it to a CSV file.""" 
    global is_running
    while is_running:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        dust_level = round(random.uniform(10, 50), 2)  # Simulating dust level between 10 and 50
        print(f"Timestamp: {timestamp}, Dust Level: {dust_level}")
        
        # Save data to a CSV file
        file_path = f"data/data_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        with open(file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Timestamp", "Dust_Level"])
            csv_writer.writerow([timestamp, dust_level])
        
        time.sleep(10)

def start_emulation():
    """Starts the data emulation in a separate thread.""" 
    global is_running
    is_running = True
    emulation_thread = threading.Thread(target=generate_data, daemon=True)
    emulation_thread.start()

def stop_emulation():
    """Stops the data emulation.""" 
    global is_running
    is_running = False
    print("Emulation paused.")

if __name__ == "__main__":
    print("Starting data emulator. Press Ctrl+C to stop.")
    try:
        start_emulation()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_emulation()
        print("Emulator stopped.")
