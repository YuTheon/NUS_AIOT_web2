# import streamlit as st
# import threading
import time
# # 定义共享变量
# is_running = True

# # 定义线程函数
# def thread_function():
#     a = 0
#     st.text(f'in to thread')
#     global is_running
#     while is_running:
#         # 线程执行的逻辑
#         a += 1
#         st.text(a)
#         time.sleep(1)
#     st.text(f'out thread')

# def stop():
# # 当需要停止线程时
#     global is_running
#     if st.button('stop'):
#         is_running = False
#     if st.button('start'):
#         is_running = True

# if __name__ == "__main__":
#     # 创建线程并启动
#     thread = threading.Thread(target=thread_function)
#     thread.start()
#     stop()

import threading
# 定义共享变量
is_running = threading.Event()

# 定义线程函数
def thread_function():
    while not is_running.is_set():
        # 线程执行的逻辑
        print(1)

# 当需要停止线程时
def stop():
    is_running.set()
 
if __name__ == "__main__":

# 创建线程并启动
    thread = threading.Thread(target=thread_function)
    thread.start()
    time.sleep(1)
    stop()


stop_flag = threading.Event()

def receive_data():
    print(f'into receive data')
    while not stop_flag.is_set():
        ser = serial.Serial(port, baud_rate, timeout=1)
        received_data = []  # List to store received data
        start_time = time.time()  # Start time of data fetching
        inner_time = time.time()
        while not stop_flag.is_set():
            data = ser.readline().decode().strip()  # Read a line of data and remove whitespace
            elapsed_time = time.time() - start_time
            if data:
                print(data)
                received_data.append(data)
                inner_time = time.time()
            if time.time() - inner_time > timeout_seconds:
                print(f'Time out for: {elapsed_time}')
                break
        ser.close()
        end_time = time.time() - start_time  # duration of one cycle
        # Save received data as a text file only if it has been fetched for more than 10 seconds
        if end_time >= fetch_duration_threshold:
            file_name = f"./temp/received_data.txt"
            # Save received data to a new text file
            with open(file_name, 'w') as file:
                file.write('\n'.join(received_data))
            print('Finish one record')
        time.sleep(1)  # Wait for 1 second before restarting the loop
    print(f'end receive.')

def main():
    model = get_model()
    # your drinked
    if st.checkbox("start receive"):
        # 创建 Thread 实例
        t1 = Thread(target=receive_data)
        if st.button("start"):
            print(f'st')
            stop_flag.clear()
            # 启动线程运行
            t1.start()
        # 等待所有线程执行完毕
        if st.button("stop"):
            stop_flag.set()
            print(f'flag {stop_flag.is_set()}')

