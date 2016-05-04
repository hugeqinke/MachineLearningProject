import sklearn
import sys

import main as Main

from sklearn.linear_model import SGDClassifier

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
    def __init__(self, train_x, train_y, test_x, test_y):
        super(Perceptron, self).__init__(train_x, train_y, test_x, test_y )

    def run(self):
        estimator = sklearn.linear_model.perceptron(self.train_x, self.train_y)
        hyp_y = estimator.predict(self.test_x)
        errors = self.compare(hyp_y, self.test_y)
        print("There were", errors, "using Perceptron")


class SubgradientDescent(SupervisedAlgorithms):
    def __init__(self, train_x, train_y, test_x, test_y):
        super(SubgradientDescent, self).__init__(train_x, train_y, test_x, test_y)

    # TODO: run with different step sizes
    def run(self):
        clf = SGDClassifier(loss="hinge")
        clf.fit(self.train_x, self.train_y)
        hyp_y = clf.predict(self.test_x)
        errors = self.compare(hyp_y, self.test_y)
        print("There were", errors, "using Pegasos")


class SVM(SupervisedAlgorithms):
    def __init__(self, train_x, train_y, test_x, test_y):
        super(SVM, self).__init__(train_x, train_y, test_x, test_y)

    def run(self):
        from sklearn.svm import SVC
        cls = SVC()
        cls.fit(self.train_x, self.train_y)
        hyp_y = cls.predict(self.test_x)
        errors = self.compare(hyp_y, self.test_y)
        print("There were", errors, "using support vector machines")


class DecisionTree(SupervisedAlgorithms):
    def __init__(self, train_x, train_y, test_x, test_y):
        super(DecisionTree, self).__init__(train_x, train_y, test_x, test_y)

    def run(self, args=None):
        from sklearn import tree
        # First, parse any specified arguments
        if args is not None:
            dt_args = dict(tuple(e.split('=')) for e in args.split(','))
        # Then, pass the arguments into the decision tree
        clf = tree.DecisionTreeClassifier()
        clf = clf.fit(self.train_x, self.train_y)
        hyp_y = clf.predict(self.test_x)
        errors = self.compare(hyp_y, self.test_y)
        print("There were", errors, "errors using decision trees")


class DataDivider(object):
    # Doesn't have test_n yet...allocate that separately
    # Splits training data and validation data into two categories
    def __init__(self, bls, ratio):
        # train_n = int(len(bls.bills) * ratio)
        # validate_n = len(bls.bills) - train_n
        train_n = 1
        validate_n = train_n + 200
        self.train = bls.bills[:train_n]
        self.validate = bls.bills[train_n:validate_n]

        self.train_x = []
        self.train_y = []
        self.validate_x = []
        self.validate_y = []

        self.listifyTrain()
        self.listifyValidate()


    def listifyTrain(self):
        for t in self.train:
            if t.vector is None or t.label is None:
                    print("Invalid bill")
                    exit()
                # Go through the vector, turn them into floats, and fill out missing values
            for i, val in enumerate(t.vector):
                if val != 'nan':
                    t.vector[i] = int(float(val.strip()))
                else:
                    t.vector[i] = 0

            self.train_x.append(t.vector)
            self.train_y.append(t.label)  # Make sure that t.label isn't null

    def listifyValidate(self):
         for t in self.validate:
            if t.vector is None or t.label is None:
                    print("Invalid bill")
                    exit()
                # Go through the vector, turn them into floats, and fill out missing values
            for i, val in enumerate(t.vector):
                if val != 'nan':
                    t.vector[i] = int(float(val.strip()))
                else:
                    t.vector[i] = 0

            self.validate_x.append(t.vector)
            self.validate_y.append(t.label)  # Make sure that t.label isn't null

    # def fillMissing(self):
    #     from scipy import stats
    #     import numpy as np
    #
    #     print("Computing modes and filling missing values...")
    #     # a = np.array(self.train_x)
    #     # m = stats.mode(a=a, nan_policy='omit')
    #     # print("Done computing modes...")





    def returnData(self):
        return self.train, self.validate


if __name__ == "__main__":
    path = "/Users/TYang/Desktop/vectors.csv"
    if len(sys.argv) !=2:
        print("usage: python algorithms.py algname")
        exit(1)

    vr = Main.VectorReader()
    bls = vr.readFinalVector(path)
    dd = DataDivider(bls, 0.8)


    if sys.argv[1] == "perceptron":
        p = Perceptron(dd.train_x, dd.train_y, dd.validate_x, dd.validate_y)
        p.run()

    if sys.argv[1] == "sgd":
        sgd = SubgradientDescent(dd.train_x, dd.train_y, dd.validate_x, dd.validate_y)
        sgd.run()

    if sys.argv[1] == "decision_trees":
        print("Running decision trees")
        dt = DecisionTree(dd.train_x, dd.train_y, dd.validate_x, dd.validate_y)
        dt.run()

    if sys.argv[1] == "random_forests":
        pass