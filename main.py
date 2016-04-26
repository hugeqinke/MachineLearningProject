import json
import os

class Bill(object):
    # Takes in jstring
    def __init__(self, jstr, type):
        if type == "JSON":
            self.json_info = self.set_json(jstr)
        elif type == "CSV":
            pass 
        attributes = []  # TODO: insert which things we want in the feature vector

    # Load the string (read from the file) into the json_info
    def set_json(self, s):
        return json.loads(s)

    # Save selected attributes into a text file (preferrably in csv)
    def serialize_attributes(self, path_file):
        pass

class Bills(object):
    def __init__(self):
        self.bills = []


class Reader(object):
    def __init__(self):
        self.congresses = [112] # Refers to specific congress (leave empty for all congresses)
        self.specifiers = ['hr'] # Any specific subdirectories (empty gets all subdirectories)
        self.data_directory = './congress/data'

    # Read parsed data of congress, should be in csv format
    def read_parsed_congresses(self, path_file):
        bills_t = Bills()

    # Read data from each congresses, given a text file with paths without any selelction\
    # Reads JSON
    def read_raw_congresses(self, path_file):
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
                # find and iterate through all directories
                directory = self.data_directory + "/" + str(congress) + "/bills/"
                for subdir in os.listdir(directory):
                    if subdir == '.DS_Store':
                        continue
                    bill_dirs = os.listdir(directory+subdir)
                    for bill_dir in bill_dirs:
                        if bill_dir == '.DS_Store':
                            continue
                        serialize_file.write(directory + subdir + "/" + bill_dir + "/data.json\n")

# Put pegasos and whatever in here
class Algorithms(object):
    pass



if __name__ == "__main__":
    print("called")
    r = Reader()
    # r.serialize_paths("112json.txt")
    bt = r.read_raw_congresses("112json.txt")
    for bill in bt.bills:
        print(bill.json_info)