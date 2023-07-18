import threading
from threading import Thread
from time import sleep, ctime

import serial
import time
# Core Pkgs
import streamlit as st
import os
from datetime import datetime
from again import process, process2
import pandas as pd

from setMysqlData import *
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn import svm

port = "COM5"  # Serial port
baud_rate = 115200  # Baud rate
timeout_seconds = 5  # determine the end of transmission
fetch_duration_threshold = 10  # determine whether the info will be recorded
# is_stop = [False]
stop_event = threading.Event()
# started_receive = False

def receive_data():
    global stop_event

    while True:
        print(f'into receive data')
        print(stop_event.is_set())
        print(stop_event.is_set() is True)
        if stop_event.is_set() is True:
            print("here")
            break
        # if is_stop[0] is True:
        #     return
        # print(f'first whlie {stop_flag.is_set()}')
        ser = serial.Serial(port, baud_rate, timeout=1)

        received_data = []  # List to store received data
        start_time = time.time()  # Start time of data fetching
        inner_time = time.time()

        while True:
            # global is_stop
            # print("seocnd while running:{}".format(is_stop))

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

            # Create a timestamp for the file name
            # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Generate the file name
            file_name = f"./temp/received_data.txt"

            # Save received data to a new text file
            with open(file_name, 'w') as file:
                file.write('\n'.join(received_data))

            print('Finish one record')

        time.sleep(1)  # Wait for 1 second before restarting the loop
    print(f'end receive.')

def process_data(folder):
    process(folder)

rng = np.random.RandomState(0)
def get_model():
    mydb = connectDatabase("smartBottle")
    result = getAllData(mydb, "drinkDataEnhan")
    x = list()
    y = list()
    for line in result:
        data = [float(num) for num in line[1].split(',')]
        label = [float(num) for num in line[2].split(',')]
        x.append(data)
        y.append(int(sum(label)/10))
    X = np.array(x)
    Y = np.array(y)
    # X_train, X_test, y_train, y_test = train_test_split(X, Y, train_size=0.8, random_state=rng)
    # (100, 70) (20, 70) (100,) (20,)
    clf = svm.SVC()
    clf.fit(X, Y)
    # pre = clf.predict(X_test)
    # print(pre)
    # print(y_test)
    # count = sum(x == y for x, y in zip(pre, y_test))
    # print(f'acc {count / len(pre)}')
    return clf

def main():
    
    """
    1. show drinked
    2. reminds when data received, and save to txt
        when received, transfer data to database
        get id from database, and transfer it to model
        show the amount of drink
    3. show times to drink
    others:get info from xiaomi, 微信步数
    """
    # Title
    st.title("Smart Bottle")
    st.subheader("care you about your drink")
    st.markdown("""
        #### Description
        when you drink, it will know how much you drink.
         
        It will also remind you when and how much to drink, base on the data about your weight and amount of exercise.
        """)
    
    model = get_model()
    started_receive = False
    # your drinked
    if st.checkbox("start receive"):
        # 创建 Thread 实例
        t1 = Thread(target=receive_data)
        if st.button("start"):
            print(f'st')
            stop_event.clear()
            t1.start()
        else:
            stop_event.set()
            # stop_flag.clear()
            # 启动线程运行
            
            # print("started_receive: {}".format(started_receive))
            # print("stop event {}".format(stop_event.is_set()))
            # if started_receive :
            #     print("setting stop event")
            #     stop_event.set()
            # else:
            #     print("clearing stop event")
            #     stop_event.clear()
            #     t1.start()

            # started_receive = ~ started_receive
            # print(f'start_rece {started_receive}')

            # stop_flag.set()
            # print(f'flag {stop_flag.is_set()}')
            # receive_data()
            # t1.join()
        # 等待所有线程执行完毕
        # if st.button("stop"):
        #     stop_event.set()
        #     print("stop event set")
        #     print(stop_event.is_set())
        #     print(stop_event.is_set() is True)
            # print(stop_event.is_set())
            # is_stop[0] = True
            # print("stop set: {}".format(is_stop))
            # stop_flag.set()
            # print(f'flag {stop_flag.is_set()}')
            
            # t1.join()  # join() 等待线程终止，要不然一直挂起

    # transfer txt to excel
    if st.checkbox("start transfer"):
        st.subheader("Analyse Your Text")
        rece = st.text_input("receive file name")
        gene = st.text_input("generate file name")
        if st.button("Analyze"):
            process("./temp")
            st.success("good")

    if st.checkbox("get predict"):
        st.subheader("Analyse Your data")
        if st.button("drink"):
            data, s, e = process2("./temp/received_data.txt")
            data = np.array(data)
            data = data.reshape(1, -1)
            df = pd.DataFrame(data)
            st.line_chart(df)
            print(f'data {data.shape}')
            res = model.predict(data[:, :70])
            st.text(res)
            a = res[0] / 200
            st.progress(a)
            st.success("good")


    # transfer excel to data
    if st.checkbox("get drink"):
        files = os.scandir("./temp")
        data = None
        for file in files:
            if file.is_file():
                if file.name.endswith('xlsx'):
                    data, y, z = readFromExcel2(file.path)
                    break
        
        y = np.array(y)
        z = np.array(z)
        y = y.reshape(1, -1)
        z = z.reshape(1, -1)
        print(f'data in to {data.shape}')
        df = pd.DataFrame(y.reshape(-1))
        yz = np.array([y, z])
        df_yz = pd.DataFrame(yz.reshape(-1, 2))
        print(f'data in to {data.shape}')
        st.line_chart(df)
        st.line_chart(df_yz)
        res = model.predict(y[:, :70])

        st.text(res)


    st.sidebar.subheader("About App")
    st.sidebar.text("smartBottle")
    st.sidebar.info("good")


    st.sidebar.subheader("By")
    st.sidebar.text("Theon E.Agbe(JCharis)")
    st.sidebar.text("Theon theonyu576@gmail.com")


if __name__ == '__main__':
    main()

    