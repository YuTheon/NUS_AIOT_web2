import serial
import time
from datetime import datetime

port = "COM5"  # Serial port
baud_rate = 115200  # Baud rate
timeout_seconds = 5  # determine the end of transmission
fetch_duration_threshold = 10  # determine whether the info will be recorded

while True:
    ser = serial.Serial(port, baud_rate, timeout=1)

    received_data = []  # List to store received data
    start_time = time.time()  # Start time of data fetching
    inner_time = time.time()

    while True:
        data = ser.readline().decode().strip()  # Read a line of data and remove whitespace
        elapsed_time = time.time() - start_time

        if data:
            print(data)
            received_data.append(data)
            inner_time = time.time()

        if time.time() - inner_time > timeout_seconds:
            print('Time out for:', elapsed_time)
            break

    ser.close()

    end_time = time.time() - start_time  # duration of one cycle

    # Save received data as a text file only if it has been fetched for more than 10 seconds
    if end_time >= fetch_duration_threshold:

        # Create a timestamp for the file name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate the file name
        file_name = f"./datadata/received_data.txt"

        # Save received data to a new text file
        with open(file_name, 'w') as file:
            file.write('\n'.join(received_data))

        print('Finish one record')

    time.sleep(1)  # Wait for 1 second before restarting the loop
