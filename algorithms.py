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

    def run(self, args):
        from sklearn import tree
        # First, parse any specified arguments
        dt_args = dict(tuple(e.split('=')) for e in args.split(','))
        # Then, pass the arguments into the decision tree
        clf = tree.DecisionTreeClassifier(**dt_args)
        clf = clf.fit(self.train_x, self.train_y)
        hyp_y = clf.predict(self.test_x)
        errors = self.compare(hyp_y, self.test_y)
        print("There were", errors, "using decision trees")


class DataDivider(object):
    # Doesn't have test_n yet...allocate that separately
    # Splits training data and validation data into two categories
    def __init__(self, bls, train_n, validate_n, ratio):
        train_n = len(bls.bills) * ratio
        validate_n = len(bls.bills) - train_n
        self.train = bls.bills[:train_n]
        self.validate = bls.bills[train_n:validate_n]

    def returnData(self):
        return self.train, self.validate



if __name__ == "__main__":
    path = "./feature_vectors.csv"
    if len(sys.argv) !=3:
        print("usage: python algorithms.py algname")
        exit(1)

    vr = Main.VectorReader()
    bls = vr.readFinalVector(path)
    train, validate = bls.returnData()

    train_x = []
    train_y = []
    for t in train:
        if t.vector is None or t.label is None:
            print("Invalid bill")
            exit()

        train_x.append(t.vector)
        train_y.append(t.label)  # Make sure that t.label isn't null

    validate_x = []
    validate_y = []
    for v in validate:
        if v.vector is None or v.label is None:
            print("Invalid bill")
            exit()

        validate_x.append(v.vector)
        validate_y.append(v.label)

    if sys.argv[2] == "perceptron":
        p = Perceptron(train_x, train_y, validate_x, validate_y)
        p.run()

    if sys.argv[2] == "sgd":
        sgd = SubgradientDescent(train_x, train_y, validate_x, validate_y)
        sgd.run()

    if sys.argv[2] == "decision_trees":
        dt = DecisionTree(train_x, train_y, validate_x, validate_y)
        dt.run()
        
    if sys.argv[2] == "random_forests":
        pass