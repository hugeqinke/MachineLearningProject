import json
import os
import csv
import sys

from bs4 import BeautifulSoup

ATTRIBUTES = []

class Bill(object):
    # Takes in jstring
    def __init__(self, jstr, type):
        self.id = ""
        self.attributes = None
        if type.lower() == "json":
            self.json_info = self.set_json(jstr)
        elif type.lower() == "csv":
            self.attributes = jstr.split()


    # Load the string (read from the file) into the json_info
    def set_json(self, s):
        return json.loads(s)

     # Save selected attributes into a text file (preferrably in csv)
    def serialize_attributes(self, csv_file):
        for attribute in ATTRIBUTES:
            json_data = self.json_info
            for path in attribute.split(","):
                if json_data != None:
                    json_data = json_data[path]
                    # Count amendments, actions and cosponsors
            if attribute == "amendments" or attribute == "actions" or attribute == "cosponsors":
                count = 0
                for item in json_data:
                    count += 1
                json_data = count
            if isinstance(json_data, basestring):
                self.attributes.append(json_data.encode('utf-8').strip())
            else:
                self.attributes.append(json_data)
        csv_file.writerow(self.attributes)


class Bills(object):
    def __init__(self):
        self.bills = []


class Reader(object):
    def __init__(self):
        # I guess values would only work for one path, then...
        self.values = None

    def readFile(self, doc):
        with open(doc, 'r') as f:
            self.values = f.readlines()


class Writer(object):
    def __init__(self):
        self.qualifier = "w"

    def writeValues(self, path, append, values):
        if append:
            self.qualifier = "a"
        else:
            self.qualifier = "w"
        f = open(path, self.qualifier)
        f.writelines(values)


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
        self.writer = Writer()

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
                dataPath = temp_path +  str(bill_id) + "/data.json\n"
                pathList += [dataPath]
        self.writer.writeValues("./metadata/datafiles.txt", True, pathList)


# Put pegasos and whatever in here
class Algorithms(object):
    def decision_tree(self, fv):
        pass


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
        csvfile = open("./metadata/112data.csv", "wb")
        w = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        ATTRIBUTES = [path.strip() for path in open("./metadata/attributes.txt", "r").readlines()]
        r = CongressBillReader("./metadata/datafiles.txt", "json")
        for b in  r.bill_o.bills:
            b.serialize_attributes(w)