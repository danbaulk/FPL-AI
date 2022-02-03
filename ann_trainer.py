"""this module will be used to train the ANN models"""
import ANN

myann = ANN.ANN(5)
myann.printModel()
myann.saveModel("myfirstann")

mynewann = ANN.ANN("myfirstann")
mynewann.printModel()