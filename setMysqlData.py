import mysql.connector
import matplotlib.pyplot as plt
import argparse
import os
import random
import pandas as pd
import datetime
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler


def createDatabase(dataBase="smartBottle"):
	"""连接数据库，创建database"""
	mydb = mysql.connector.connect(
		host='localhost',
		user='root',
		passwd='123456'
	)
	mycursor = mydb.cursor()
	mycursor.execute(f"CREATE DATABASE {dataBase}")
	mydb.commit()
	return mydb

def connectDatabase(dataBase="smartBottle"):
	"""连接mysql"""
	mydb = mysql.connector.connect(
		host='localhost',
		user='root',
		passwd='123456',
	database=dataBase)	
	return mydb

def createTable(mydb, tableName="drinkData"):
	"""创建表"""
	mycursor = mydb.cursor()
	# mycursor.execute(f"drop table {tableName}")
	# mydb.commit()
	mycursor.execute(f"CREATE TABLE `{tableName}` \
		(`id` int(11) NOT NULL AUTO_INCREMENT,\
		`data_extract` varchar(1000),\
	  `label` varchar(1000),\
	  `saveTime` datetime,\
		`user_id` int(11),\
	  PRIMARY KEY (`id`)\
	);")
	mydb.commit()
	return mydb

def insertData(mydb, tableName = "drinkData"):
	"""插入数据"""
	mycursor = mydb.cursor()
	sql = f"INSERT INTO {tableName} (user_id, data, label, saveTime) VALUES(%s, %s, %s, %s);"
	with open('../data/80ml.txt', 'r') as f:
		con = f.readlines()
		# print(len(con)/3)
		for i in range(int(len(con)/3)):
			i *= 3
			sql = "INSERT INTO drinkData (user_id, data_y, data_z, label) VALUES(%s, %s, %s, %s);"
			y = con[i]
			z = con[i+1]
			label = con[i+2]
			val = (1, y, z, label)
			mycursor.execute(sql, val)
	mydb.commit()

def readFromExcel(mydb, path):
	files = os.scandir(path)
	mycursor = mydb.cursor()
	for f in files:
		df = pd.read_excel(f.path)
		start, end = int(df.loc[0, 'S']), int(df.loc[0, 'E'])
		drink = f.path.split('/')[-1].split('_')[0]
		if drink not in ['Stable', 'Walk']:
			if start == end:
				continue
			drink = int(drink[:-2])
		else:
			drink = 0
		y = df.loc[:, 'Y']
		z = df.loc[:, 'Z']
		y = [str(round(num/1080, 3)) for num in y]
		z = [str(round(num/1080, 3)) for num in z]
		label = ['0' for i in range(len(y))]
		for i in range(start-1, end-1):
			label[i] = str(round(drink / (end - start), 3))
		data_y = ','.join(y)
		data_z = ','.join(z)
		label  = ','.join(label)
		sql = "insert into drinkData (user_id, data_y, data_z, label) VALUES(%s, %s, %s, %s)"
		val = (1, data_y, data_z, label)
		mycursor.execute(sql, val)
	mydb.commit()
	return f'success save {len(files)} data'

def readFromExcel2(path):
	df = pd.read_excel(path)
	y = df.loc[:, 'Y']
	z = df.loc[:, 'Z']
	y = [str(round(num/1080, 3)) for num in y]
	z = [str(round(num/1080, 3)) for num in z]
	cob = np.array([y, z])
	data = featExtra(cob.T)
	print(f'data {data.shape}')
	return data.reshape(1, -1)[:, :70], y, z

def dataAug(mydb, length):
	"""
	params:
		length: data length after augrement
		num: nums of data generated
	"""
	pass

def randomDeletePointDA(data, label, length):
	"""data, label长度在dataAug中判断, """
	dataLen = len(data)
	indices = list(range(dataLen))
	random.shuffle(indices)
	remove_indices = indices[:dataLen-length]
	new_data = [data[i] for i in range(dataLen) if i not in remove_indices]
	new_label = [label[i] for i in range(dataLen) if i not in remove_indices]
	return new_data, new_label


def crossDA():
	pass

def featExtra(input):
	"""
		输入前将数据处理成numpy 
		return np
	"""
	# 创建PCA对象 感觉可以放到前面 不过先别想那么多
	pca = PCA(n_components=1)
	result = pca.fit_transform(input)
	return result.flatten()


# for j in range(10):
# 	sql = "INSERT INTO drinkData (user_id, data, label, saveTime) VALUES(%s, %s, %s, %s);"
# 	data =[str(random.randint(0, 100)) for i in range(100)]
# 	label = [str(random.choice([0, 5])) for i in range(100)]
# 	data = ','.join(data)
# 	label = ','.join(label)
# 	now = datetime.datetime.now()
# 	now = now.strftime("%Y-%m-%d %H:%M:%S")
# 	val = (1, data, label, now)
# 	mycursor.execute(sql, val)
# print(mycursor.rowcount, 'record inserted.')
# mydb.commit()

def getAllData(mydb, tableName="drinkData"):
	"""读取数据"""
	mycursor = mydb.cursor()
	mycursor.execute(f"SELECT * FROM {tableName}")
	myresult = mycursor.fetchall()
	# for x in myresult:
	# 	print(x)
	return myresult

def visual(y, z, label):
	y = y.split(',')
	z = z.split(',')
	label = label.split(',')
	y = [float(i) for i in y]
	z = [float(i) for i in z]
	label = [float(i) for i in label]
	time = [i for i in range(len(label))]
	plt.figure(1)
	plt.subplot(2, 1, 1)
	plt.plot(time, y, label='y')
	plt.plot(time, z, label='z')
	plt.xlabel("time")
	plt.ylabel("angle")
	plt.legend()

	plt.figure(1)
	plt.subplot(2, 1, 2)
	plt.plot(time, label)
	plt.xlabel("time")
	plt.ylabel("drink")
	print(f'total drink {sum(label)}')

	plt.show()

def visual2(data, label):
	time = [i for i in range(len(label))]
	plt.figure(1)
	plt.subplot(2, 1, 1)
	plt.plot(time, data, label='data')
	plt.xlabel("time")
	plt.ylabel("angle")
	plt.legend()

	plt.figure(1)
	plt.subplot(2, 1, 2)
	plt.plot(time, label)
	plt.xlabel("time")
	plt.ylabel("drink")
	print(f'total drink {sum(label)}')

	plt.show()

def list2str(arr):
	new_arr = [str(round(i,3)) for i in arr]
	return ','.join(new_arr)

def raw2new():
	"""
		delete all data in new_database, 
		raw_data -> dataAug(size=70) -> new_data
	"""

	mydb = connectDatabase("smartBottle")
	result = getAllData(mydb)

	# save data from raw_data to new_data (得处理一下之后导入都是只导入新的)
	scaler = MinMaxScaler(feature_range=(-1, 1))
	mycursor = mydb.cursor()
	# delete old database
	# sql = "delete from drinkDataEnhan"
	# mycursor.execute(sql)
	# mydb.commit()
	#
	for line in result:
		y = [float(num) for num in line[2].split(',')]
		z = [float(num) for num in line[3].split(',')]
		label = [float(num) for num in line[4].split(',')]
		data = np.array([y, z])
		data = featExtra(data.T)
		#NOTE - change data to y
		y = np.array(y)
		data = scaler.fit_transform(y.reshape(-1, 1))
		data = data.flatten().tolist()
		for i in range(30):
			if len(data) <= 70:
				break
			if len(data) != len(label):
				break
			new_data, new_label = randomDeletePointDA(data, label, 70)
			sql = "INSERT INTO drinkDataEnhan (user_id, data_extract, label) VALUES(%s, %s, %s);"
			val = (1, list2str(new_data), list2str(new_label))
			mycursor.execute(sql, val)
		mydb.commit()

def checkData():
	mydb = connectDatabase("smartBottle")
	result = getAllData(mydb, "drinkDataEnhan")
	cnt = dict()
	for line in result:
		label = [float(num) for num in line[2].split(',')]
		drink = sum(label)
		k = str(int(drink/10))
		if k in cnt.keys():
			value = cnt[k]
			cnt.update({k: value+1})
		else:
			cnt[k] = 1
		print(f'drink label {sum(label)}')
	print(f'data nums {len(result)}')
	print(f'dict {cnt}')



if __name__ == "__main__":
	# 参数
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--dataBaseName', type=str, default="smartBottle",
    #                         help='name of the database')
    # config = parser.parse_args()

	"""
	raw_data -> dataAug -> new_data
	raw_data: id, data_x, data_y, data_z, label, save_time, user_id
	new_data: id, data, label, save_time, user_id
	"""
	raw2new()
	checkData()
	

	# createTable(mydb, "drinkDataEnhan")
	# result = 
	# result = getAllData(mydb) 
	# visual(result[0][2], result[0][3], result[0][4])

