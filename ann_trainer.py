"""this module will be used to train the ANN models"""
import csv
import ANN
import numpy as np

# read data into a list
with open('Data/GK.csv', newline='') as Data:
    reader = csv.reader(Data)
    DataSet = list(reader)

# split the data into the different sets based on the ratio
ratio = [0.6, 0.2, 0.2]
training_r, validation_r, data_r = ratio
indicies_for_splitting = [int(len(DataSet) * training_r), int(len(DataSet) * (training_r + validation_r))]
TrainingData, ValidationData, TestData = np.split(DataSet, indicies_for_splitting)
