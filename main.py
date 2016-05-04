import json
import os
import csv
import sys
import numpy as np
import time

import sklearn

ATTRIBUTES = []
ATT_FILES = {}
MIN_NUM = 25
MAX_NUM = 200

class Bill(object):
    # Takes in jstring
    def __init__(self, jstr, type):
        self.id = ""
        self.attributes = None
        self.label = None
        self.vector = []
        if type.lower() == "json":
            self.json_info = self.set_json(jstr)
        elif type.lower() == "csv":
            self.attributes = jstr.split(",")

    # Load the string (read from the file) into the json_info
    def set_json(self, s):
        return json.loads(s)


    # Save selected attributes and final vector
    def serialize_attributes(self, vocabs):
        vector = np.zeros((1, 1))
        data_array = np.zeros((1, 1))
        for attribute in ATTRIBUTES:
            data = self.json_info
            for path in attribute.split(","):
                if data != None:
                    data = data[path]
            if attribute == "amendments" or attribute == "actions" or attribute == "cosponsors":  # Count amendments, actions and cosponsors
                data = len(data)
                data_array[0] = data
                vector = np.concatenate((vector, data_array))
            elif vocabs.has_key(attribute):
                vocab = vocabs[attribute]
                lil_vec = np.zeros([len(vocab), 1])
                if data != None:
                    if attribute != "subjects" and attribute != "committees":
                        data = str(data.strip().encode('utf8', 'ignore')).translate(None, "\"\',.;:/?[]{}\()&%$!")
                        data = data.replace("\n", " ")
                        for word in data.strip().split(" "):
                            word = word.lower()
                            if word in vocab:
                                lil_vec[vocab[word]] += 1
                    else:
                        for item in data:
                            if attribute == "committees":
                                if item["committee_id"] in vocab:
                                    lil_vec[vocab[item["committee_id"]]] = 1
                            else:
                                for word in item.split(" "):
                                    word = word.strip(" \"\',.;:/?'[]{}\()&%$!").lower()
                                    if word in vocab:
                                        lil_vec[vocab[word]] += 1
                vector = np.concatenate((vector, lil_vec))
            elif attribute == "bill_id":
                self.id = data
            elif attribute == "introduced_at":
                pattern = "%Y-%m-%d"
                data_array[0] = int(time.mktime(time.strptime(data, pattern)))
                vector = np.concatenate((vector, data_array))
            else:
                data_array[0] = data
                vector = np.concatenate((vector, data_array))
        self.vector = vector.flat[:]


class Bills(object):
    def __init__(self):
        self.bills = []
        self.total_num = 0


class Writer(object):
    def __init__(self, files, output):
        self.file_dict = files  # Dictionary of attribute name to file name (where the voacb for each attribute is)
        self.bill_output = output
        self.qualifier = "w"

    # Attribute is a string, bills is an array of bills
    def bag_of_words(self, attribute, bills):
        print("Creating vocabulary for " + attribute + "...")

        if attribute != "subjects" and attribute != "committees":
            vocab = {}
            for bill in bills:
                line = bill.json_info
                for path in attribute.split(","):
                    if line != None:
                        line = line[path]
                if line != None:
                    line = str(line.strip().encode('utf8', 'ignore')).translate(None, "\"\',.;:/?[]{}\()&%$!")
                    line = line.replace("\n", " ")
                    for word in line.strip().split(" "):
                        word = word.lower()
                        if word not in vocab:
                            vocab[word] = 1
                        else:
                            vocab[word] += 1
        else:
            vocab = {}
            for bill in bills:
                for item in bill.json_info[attribute]:
                    if attribute == "committees":
                        word = item["committee_id"]
                        if word not in vocab:
                            vocab[word] = 1
                        else:
                            vocab[word] += 1

                    else:
                        for word in item.split(" "):
                            word = word.strip(" \"\',.;:/?'[]{}\()&%$!").lower()
                            if word not in vocab:
                                vocab[word] = 1
                            else:
                                vocab[word] += 1
        if vocab.has_key(""):
            del vocab[""]
        new_vocab = {}
        i = 0
        for word in vocab:
            if vocab[word] > MIN_NUM and vocab[word] < MAX_NUM:
                new_vocab[word] = i
                i += 1
        w = csv.writer(self.file_dict[attribute], delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for key, value in new_vocab.items():
            w.writerow([key, value])
        self.file_dict[attribute].close()
        return new_vocab

    def save_vectors(self, bt):
        bills = bt.bills
        progress = 0.25
        w = csv.writer(self.bill_output, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        i = 1.0
        # total_bum = bt.total_num
        for bill in bills:
            # if i / total_num >= progress:
            #     print(str(progress * 100) + "% done...")
            #     progress += 0.25
            w.writerow(bill.vector)
            i += 1

    def writeValues(self, path, append, values):
        if append:
            self.qualifier = "a"
        else:
            self.qualifier = "w"
        f = open(path, self.qualifier)
        f.writelines(values)


class Reader(object):
    def __init__(self):
        # I guess values would only work for one path, then...
        self.values = None

    def readFile(self, doc):
        with open(doc, 'r') as f:
            self.values = f.readlines()


# Read the CSV files
# Use this only after all the feature vectors have been succesfully parsed and stuff
class VectorReader(Reader):
    def __init__(self):
        super(VectorReader, self).__init__()

    def readFinalVector(self, pathFile):
        bls = Bills()
        self.readFile(pathFile)  # Read the csv file
        for file in self.values:
            with open(file, "r") as f:
                contents = f.readlines()
                for content in contents:
                    b = Bill(content, "csv")
                    self.readID(b)
                    self.readLabel(b)  # Next, from the file, read the labels
                    self.readFV(b)  # And finally, read all the attributes
                    self.removeAttribute(b)
                    bls.bills.append(b)
        return bls

    # We will use this to write to somewhere else
    def readRawVector(self, pathFile):
        # Use neatifying algorithm here
        bls = Bills()
        self.readFile(pathFile)
        for file in self.values:
            with open(file, "r") as f:
                contents = f.readlines()
                for content in contents:
                    b = Bill(content, "csv")
                    self.readID(b)
                    self.readLabel(b)
                    self.readFV(b)
                    # Apply algorithm change here
        pass

    def readID(self, b):
        b.id = b.attributes[0]

    def readLabel(self, b):
        b.label = b.attributes[1]

    def readFV(self, b):
        b.vector = b.attributes[2:]

    def removeAttribute(self, b):
        b.attributes = None




class CongressBillReader(Reader):
    def __init__(self, pathFile, requestType):
        super(CongressBillReader, self).__init__()
        if requestType.lower() == "json":
            self.bill_o = self.readBillFiles(pathFile)
        elif requestType.lower() == "csv":
            self.bill_o = self.readBillFilesCSV(pathFile)

    # returns an array of Bill Clintons
    # Reads the bills in JSON format initially, unless otherwise specified
    def readBillFiles(self, pathFile):
        self.readFile(pathFile)
        bs = Bills()
        for value in self.values:
            value = value.strip() # Get rid of annoying \n at the end
            with open(value, "r") as f:
                json_content = ""
                contents = json_content.join(f.readlines())
                b = Bill(contents, "JSON")
                bs.bills.append(b)
        return bs

    def readBillFilesCSV(self, pathFile):
        self.readFile(pathFile)
        bs = Bills()
        for value in self.values:
            value = value.strip()
            b = Bill(value, "CSV")
            bs.bills.append(b)
        return bs


class CongressPathReader(Reader):
    def __init__(self, metadata_path, billDirectoryPath):
        super(CongressPathReader, self).__init__()
        self.metadataFile = metadata_path
        self.identifications = ["hconres", "hjres", "hr", "hres", "s", "sconres", "sjres", "sres"]
        self.BILL_DIR = billDirectoryPath
        # need this to write results
        self.writer = Writer("", "")
        self.paths = None

    # Reads the paths and notify the metadata file congress-status that things have been changed
    def readPaths(self):
        statuses = []
        self.readFile(self.metadataFile)
        for value in self.values:
            splitValue = value.split()
            congress_number = splitValue[0]
            isLoaded = (splitValue[1].lower() == "true")
            if not isLoaded:
                self.loadFiles(congress_number)
            statuses.append(congress_number + " true\n")
        self.writer.writeValues(self.metadataFile, False, statuses)

    # loads the data.json path into a list of all data.json paths
    def loadFiles(self, congress_n):
        pathList = []
        path = self.BILL_DIR + "/bills/" + str(congress_n) + "/bills/"
        for identification in self.identifications:
            temp_path = path + identification + "/"
            bill_ids = os.listdir(temp_path)
            for bill_id in bill_ids:
                dataPath = temp_path + str(bill_id) + "/data.json\n"
                pathList += [dataPath]
        self.writer.writeValues("./metadata/datafiles.txt", True, pathList)


# How to use scraping API:
#   call python main.py scrape
#   [optional argument after scrape indicating file with desired congress numbers]
#   default congress number file is ./bills/congress-rules.txt
#   the scrape call will automatically check the file and obtain any congress number with "true" after it
#   it will automatically replace it with false after all congress bills have been written

if __name__ == "__main__":
    cmd = ""
    if len(sys.argv) > 1:
        cmd = sys.argv[1]

    # Only searches for relavent json files in a specific congress
    # Will compare text files to see if approprate files have been removed
    if cmd == "search":
        if len(sys.argv) != 3:
            print("usage: python main.py search billhomedirectory")
        else:
            cpReader = CongressPathReader("./metadata/congress-status.txt", sys.argv[2])
            cpReader.readPaths()

    if cmd == "csvread":
        if len(sys.argv) != 3:
            print("usage: python main.py csvread congresscsvfile")
        else:
            r = CongressBillReader(sys.argv[2], "csv")
            # Then run any algorithms here I guess, or call this from another function

    if cmd == "csvify":
        r = CongressBillReader("./metadata/datafiles.txt", "json")
        # Objects for csv file with data vectors
        csvfile = open("112data.csv", "w+")
        # Vocab file paths
        ATTRIBUTES = [path.strip() for path in open("attributes.txt", "r").readlines()]
        for line in open("att_files.txt", "r").readlines():  # Load in vocab file locations
            line = line.strip().split("|")
            ATT_FILES[line[0]] = open(line[1], "w")
        vec_writer = Writer(ATT_FILES, csvfile)
        # r.serialize_paths("112json.txt")
        print("Loading bill data...")
        bt = r.bill_o
        vocabs = {}
        for att in ATT_FILES.keys():
            vocabs[att] = vec_writer.bag_of_words(att, bt.bills)
        print("Vectorizing bills...")
        progress = 0.25
        i = 1.0
        # total_num = bt.total_num
        for bill in bt.bills:
            # if i / total_num >= progress:
            #     print(str(progress * 100) + "% done...")
            #     progress += 0.25
            bill.serialize_attributes(vocabs)
            i += 1
        # Write vectors to csv file
        print("Saving bills to file...")
        vec_writer.save_vectors(bt)
