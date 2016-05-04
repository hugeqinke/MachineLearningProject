import sklearn
import sys

import random

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


class RandomForest(SupervisedAlgorithms):
    def __init__(self, train_x, train_y, test_x, test_y):
        super(RandomForest, self).__init__(train_x, train_y, test_x, test_y)

    def run(self, args={}):
        from sklearn import ensemble
        rfc = ensemble.RandomForestClassifier(**args)
        rfc.fit(self.train_x, self.train_y)
        hpy_y = rfc.predict(self.test_x)
        errors = self.compare(hpy_y, self.test_y)

        print "There were", errors, "errors using random forests"

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

    def run(self, args={}):
        from sklearn import tree
        # First, parse any specified arguments
        # Then, pass the arguments into the decision tree
        clf = tree.DecisionTreeClassifier(**args)
        clf = clf.fit(self.train_x, self.train_y)
        hyp_y = clf.predict(self.test_x)
        errors = self.compare(hyp_y, self.test_y)

        with  open("./dt_results.txt", "a") as f:
            writeL = ""
            if "max_depth" in args:
                writeL += "max_depth: " + str(args["max_depth"]) + " "
            if "min_samples_leaf" in args:
                writeL += "min_samples_leaf: " + str(args["min_samples_leaf"]) + " "
            writeL += "errors: " + str(errors) + " "
            writeL += "percent: " + str(float(errors)/len(self.test_y)) + "\n"
            f.write(writeL)

    def find_optimal(self):
        mds = range(1, 35)
        mls = range(1, 35)
        count = 0
        percent = 0.25
        for md in mds:
            if count/(35*35) >= 0.25:
                percent += 0.25
                print "Done", percent, "percent left"
            for ml in mls:
                count += 1
                self.run({'max_depth': md, 'min_samples_leaf':ml})

class DataDivider(object):
    # Doesn't have test_n yet...allocate that separately
    # Splits training data and validation data into two categories
    def __init__(self, bls, ratio):
        random.shuffle(bls.bills)
        train_n = int(len(bls.bills) * ratio)
        validate_n = len(bls.bills)
        self.train = bls.bills[:train_n]
        self.validate = bls.bills[train_n:validate_n]

        self.train_x = []
        self.train_y = []
        self.validate_x = []
        self.validate_y = []

        self.listifyTrain()
        self.listifyValidate()


    def listifyTrain(self):
        print("Transforming training data into a list...")
        progress = 0.25
        count = 0
        for t in self.train:
            if count / len(self.train) >= progress:
                progress += 0.25
                print "Completed", progress * 100, "percent"
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
            count += 1

    def listifyValidate(self):
        print("Transforming validation data into a list...")
        progress = 0.25
        count = 0
        for t in self.validate:
            if count / len(self.validate) >= progress:
                progress += 0.25
                print "Completed", progress * 100, "percent"
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
            count += 1

    # def fillMissing(self):
    #     from scipy import stats
    #     import numpy as np
    #
    #     print("Computing modes and filling missing values...")
    #     # a = np.array(self.train_x)
    #     # m = stats.mode(a=a, nan_policy='omit')
    #     # print("Done computing modes...")


if __name__ == "__main__":
    path = "/Users/TYang/Desktop/vectors.csv"
    if len(sys.argv) < 2:
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
        if len(sys.argv) == 3 and sys.argv[2] == "opt":
            dt.find_optimal()
        else:
            dt.run()

    if sys.argv[1] == "random_forests":
        print("Running random forests")
        rf = RandomForest(dd.train_x, dd.train_y, dd.validate_x, dd.validate_y)
        rf.run()