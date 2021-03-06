import base64
import csv
import gc
import time
try:
   import cPickle as pickle
except:
   import pickle

import numpy as np
from numpy import *

from sklearn.decomposition import RandomizedPCA

from sklearn.linear_model import LogisticRegression
from sklearn import cross_validation
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

from sklearn.svm import SVC
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import BernoulliRBM

import skimage.io as io
import skimage.transform as trans

def image_predict(userIds):
	f = open("image_features.bin", "rb")
	oriData = pickle.load(f)
	f.close()

	f = open("image_fileMap.bin", "rb")
	fileMap = pickle.load(f)
	f.close()

	f = open("image_classifiers.bin", "rb")
	genderClassifier = pickle.load(f)
	ageClassifier = pickle.load(f)
	f.close()

	decomp = RandomizedPCA(n_components = 25)
	oriData  = decomp.fit_transform(oriData)

	test = []
	user = []

	for i in range (0, 4113):
		userId = fileMap[i]
		if userId in userIds:
			user.append(userId)
			test.append(oriData[i])

	gP = genderClassifier.predict(test)
	aP = ageClassifier.predict(test)

	result = []
	for u in userIds:

		male = 0
		fem = 0
		a = 0
		b = 0
		c = 0
		d = 0
		e = 0
		for i in range(0, len(user)):
			if u == user[i]:
				if gP[i] == "MALE":
					male+=1
				else:
					fem+=1

				age = aP[i]
				if age == "18-24":
					a+=1
				elif age == "25-34":
					b+=1
				elif age == "35-49":
					c+=1
				elif age == "50-64":
					d+=1
				else:
					e+=1

		if fem==0 and male==0:
			result.append(("none", "none"))
			continue

		if fem > male:
			gender = "FEMALE"
		else:
			gender = "MALE"

		aList = [(a,"18-24"),(b, "25-34"),(c, "35-49"),(d, "50-64"),(e, "65-xx")]
		aList.sort()
		age = aList[4][1]
		result.append((gender, age))

	return result


def image_train_and_predict(userIds, genders, ages, targets):
	f = open("image_features.bin", "rb")
	oriData = pickle.load(f)
	f.close()

	f = open("image_fileMap.bin", "rb")
	fileMap = pickle.load(f)
	f.close()

	userMap = {}
	train = []
	test = []
	user = []
	g_train = []
	a_train = []

	decomp = RandomizedPCA(n_components = 25)
	oriData  = decomp.fit_transform(oriData)

	for i in range(0, len(userIds)):
		userMap[userIds[i]] = (genders[i], ages[i])

	for i in range (0, 4113):
		userId = fileMap[i]
		if userId in userIds:
			train.append(oriData[i])
			g_train.append(userMap[userId][0])
			a_train.append(userMap[userId][1])
		elif userId in targets:
			user.append(userId)
			test.append(oriData[i])

	train = np.array(train)
	test = np.array(test)

	genderClassifier = SVC()
	ageClassifier = SVC()

	genderClassifier.fit(train, g_train)
	ageClassifier.fit(train, a_train)

	gP = genderClassifier.predict(test)
	aP = ageClassifier.predict(test)

	result = []

	for u in targets:
		male = 0
		fem = 0
		a = 0
		b = 0
		c = 0
		d = 0
		e = 0
		for i in range(0, len(user)):
			if u == user[i]:
				if gP[i] == "MALE":
					male+=1
				else:
					fem+=1

				age = aP[i]
				if age == "18-24":
					a+=1
				elif age == "25-34":
					b+=1
				elif age == "35-49":
					c+=1
				elif age == "50-64":
					d+=1
				else:
					e+=1

		if fem==0 and male==0:
			result.append(("none", "none"))
			continue

		if fem > male:
			gender = "FEMALE"
		else:
			gender = "MALE"

		aList = [(a,"18-24"),(b, "25-34"),(c, "35-49"),(d, "50-64"),(e, "65-xx")]
		aList.sort()
		age = aList[4][1]
		result.append((gender, age))

	return result
