import sklearn
import sys

# Put pegasos and whatever in here
class SupervisedAlgorithms(object):
    def __init__(self, train_x, train_y, test_x, test_y):
        self.train_x = train_x
        self.train_y = train_y
        self.test_x = test_x
        self.test_y = test_y

    def compare(self, hyp_y, real_y):
        if len(hyp_y) != len(real_y):
            print("Invalid vector lengths")

        errors = 0
        for hyp, real in zip(hyp_y, real_y):
            if hyp != real:
                errors += 1
        return errors

class Perceptron(SupervisedAlgorithms):
    def __init__(self, train_x, train_y, test_x, test_y ):
        pass

    def run(self):
        estimator = sklearn.linear_model.perceptron(self.train_x, self.train_y)
        hyp_y = estimator.predict(self.test_x)
        errors = self.compare(hyp_y, self.test_y)
        print("There were", errors, "using Perceptron")

    def find_optimal_params(self):
        pass


class Pegasos(SupervisedAlgorithms):
    def __init__(self, train_x, train_y, test_x, test_y):
        pass
    
if __name__ == "__main__":
    if len(sys.argv) !=3:
        print("usage: python algorithms.py algname")

    elif sys.argv[2] == "perceptron":
        pass

    elif sys.argv[2] == "pegasos":
        pass

    elif sys.argv[2] == "decision_trees":
        pass

    elif sys.argv[2] == "random_forests":
        pass