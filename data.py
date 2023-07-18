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

import schedule
from functools import partial

port = "COM5"  # Serial port
baud_rate = 115200  # Baud rate
timeout_seconds = 5  # determine the end of transmission
fetch_duration_threshold = 10  # determine whether the info will be recorded
# is_stop = [False]
stop_event = threading.Event()
data, s, e = process2("./temp/received_data.txt")
data = np.array(data)
data = data.reshape(1, -1)
df = pd.DataFrame(data.T, columns=['data'])
# started_receive = False




def receive_data():
    global stop_event

    while True:
        # print(f'into receive data')
        # print(stop_event.is_set())
        # print(stop_event.is_set() is True)
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
                # print(f'Time out for: {elapsed_time}')
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

model = get_model()
res = model.predict(data[:, :70])[0] / 20

class ThreadWithReturnValue(Thread):
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        super().join()
        return self._return

def get_drink():
    global df, res
    curr = datetime.datetime.now()
    st.text(f'current time is {curr}')
    print(f'into drink draw')
    data, s, e = process2("./temp/received_data.txt")
    data = np.array(data)
    data = data.reshape(1, -1)
    df = pd.DataFrame(data.T, columns=['data'])
    print(f'data {data.shape}')
    # st.line_chart(df)
    res = model.predict(data[:, :70])
    res = res[0] / 20
    # st.line_chart(df)
    # print(f'type {type(res[0])}')
    # st.progress(res[0] * 10 / 200)
    # st.text(res)
    # a = res[0] / 20
    # st.progress(a)
    # st.success(f'you have drink {res[0] * 10} ml')


def main():

    # Title
    st.title("Smart Bottle")
    st.subheader("care you about your drink")
    st.markdown("""
        #### Description
        when you drink, it will know how much you drink.
         
        It will also remind you when and how much to drink, base on the data about your weight and amount of exercise.
        """)
    
    
    started_receive = False
    # your drinked
    t1 = Thread(target=receive_data)
    t1.start()
    # if st.checkbox("start receive"):
    #     # 创建 Thread 实例
    #     if st.button("start"):
    #         print(f'st')
    #         stop_event.clear()
            
    #     else:
    #         stop_event.set()
    
    tab1, tab2 = st.tabs(["apply", "train"])
    a = np.zeros((80, 1))
    global df, res
    # partial_get_drink = partial(get_drink, model=model)
    with tab1:
        # t2 = Thread(target=get_drink, args=(model, res))
        # t2.start()
        # st.line_chart(res[0])
        # st.progress(res[1])
        get_drink()
        st.line_chart(df)
        st.progress(res)
        # schedule.every(10).seconds.do(get_drink)
        
        # if len()
        # st.line_chart(result[0])
        # st.progress(result[1])

        # if st.checkbox("get predict"):
        #     st.subheader("Analyse Your data")
        #     if st.button("drink"):
        #         data, s, e = process2("./temp/received_data.txt")
        #         data = np.array(data)
        #         data = data.reshape(1, -1)
        #         df = pd.DataFrame(data.T, columns=['data'])
        #         print(f'data {data.shape}')
        #         st.line_chart(df)
        #         res = model.predict(data[:, :70])
        #         st.text(res)
        #         a = res[0] / 20
        #         st.progress(a)
        #         st.success(f'you have drink {res[0] * 10} ml')

    
    with tab2:
        st.header("train")

    st.sidebar.subheader("About App")
    st.sidebar.text("smartBottle")
    st.sidebar.info("good")


    st.sidebar.subheader("By")
    st.sidebar.text("Theon E.Agbe(JCharis)")
    st.sidebar.text("Theon theonyu576@gmail.com")


if __name__ == '__main__':
    main()
    while True:
 
    # Checks whether a scheduled task
    # is pending to run or not
        schedule.run_pending()

    