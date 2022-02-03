"""this class will be used to represent an ANN object"""
import decimal
import random
import pickle

def ranWeight(n):
    """Return a random weight between [-2/n, 2/n] where n = num of inputs"""
    weight = float(decimal.Decimal(random.randrange(int(-200/n),int(200/n)))/100)
    return weight

class ANN:
    def __init__(self, arg):
        """constructor for ANN with 1 hidden layer, 10 inputs and 1 output.
        pass an integer x, to create a random model with x num nodes in the hidden layer
        pass a string y, which is a name of a saved model to load it"""
        
        # if argument is an int, then create the model using random numbers
        if isinstance(arg, int):
            self.weights2hidden = [[ranWeight(10) for x in range(10)] for y in range(arg)]
            self.weights2output = [ranWeight(arg) for x in range(arg)]
            self.hiddenBiases = [ranWeight(10) for x in range(arg)]
            self.outputBias = ranWeight(arg)
            self.p = 0.1

        # elif the argument is a str, load the model from the saved models
        elif isinstance(arg, str):
            loadedModel = pickle.load(open('Models/' + arg, 'rb'))
            self.weights2hidden = loadedModel.weights2hidden
            self.weights2output = loadedModel.weights2output
            self.hiddenBiases = loadedModel.hiddenBiases
            self.outputBias = loadedModel.outputBias
            self.p = loadedModel.outputBias

    def printModel(self):
        """display the model"""
        print("Weights to hidden layer:\n", self.weights2hidden)
        print("Hidden layer biases:\n", self.hiddenBiases)
        print("Weights to output layer:\n", self.weights2output)
        print("Output node bias:\n", self.outputBias)
        print("Step size:\n", self.p)
    
    def saveModel(self, name):
        """save the model with given name"""
        pickle.dump(self, open('Models/' + name, 'wb'))
