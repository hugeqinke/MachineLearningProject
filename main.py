import json
import os

class Bill(object):
    # Takes in jstring
    def __init__(self, jstr):
        self.json_info = self.set_json(jstr)

    # Load the string (read from the file) into the json_info
    def set_json(self, s):
        return json.loads(s)

class Bills(object):
    def __init__(self):
        self.bills = []


class Reader(object):
    def __init__(self):
        self.congresses = [112] # Refers to specific congress (leave empty for all congresses)
        self.specifiers = ['hr'] # Any specific subdirectories (empty gets all subdirectories)
        self.data_directory = './congress/data'

    # Read data from each congresses, given a text file with paths
    def read_congresses(self, path_file):
        bills_t = Bills()
        paths = [path.strip() for path in open(path_file, 'r').readlines()]
        for path in paths:
            bill_t = Bill(open(path, 'r').read())
            bills_t.bills.append(bill_t)
        return bills_t

    # List all documents that we want to read and save them to a file,
    # so that we don't have to traverse the file system every time we run the program
    def serialize_paths(self, target_file):
        serialize_file = open(target_file, "a") # append, don't overwrite!
        for congress in self.congresses:
            for specifier in self.specifiers:
                # find and iterate througha ll directories
                directory = self.data_directory + "/" + str(congress) + "/bills/"
                for subdir in os.listdir(directory):
                    if subdir == '.DS_Store':
                        continue
                    bill_dirs = os.listdir(directory+subdir)
                    for bill_dir in bill_dirs:
                        if bill_dir == '.DS_Store':
                            continue
                        serialize_file.write(directory + subdir + "/" + bill_dir + "/data.json\n")

class Algorithm(object):
    pass



if __name__ == "__main__":
    print("called")
    r = Reader()
    # r.serialize_paths("112json.txt")
    bt = r.read_congresses("112json.txt")
    print(bt.bills)