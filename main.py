import json
import os
import csv
import sys
import urllib2
import StringIO

from bs4 import BeautifulSoup

ATTRIBUTES = []

# A resource container for all the websites we want to use
class Websites(object):
    @staticmethod
    def govtrack_congress_url(congress_n):
        return "https://www.govtrack.us/api/v2/bill?congress=" + str(congress_n)


class Bill(object):
    # Takes in jstring
    def __init__(self, jstr, type):
        if type == "JSON":
            self.json_info = self.set_json(jstr)
        elif type == "CSV":
            pass 
        self.attributes = [] 

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
    
    # Creates a mass of bills, but using mass input from the api scraper
    def create_bills_json(json):
       pass         

class Reader(object):
    def __init__(self):
        self.congresses = [112] # Refers to specific congress (leave empty for all congresses)
        self.specifiers = ['hr'] # Any specific subdirectories (empty gets all subdirectories)
        self.data_directory = './congress/data'

    # Read parsed data of congress, should be in csv format
    def read_parsed_congresses(self, path_file):
        bills_t = Bills()

    # Read data from each congresses, given a text file with paths without any selelction\
    # Preferably, we want to use scrape_by_congress, but let's keep this hee for now
    # Reads JSON
    def read_raw_congresses(self, path_file):
        bills_t = Bills()
        paths = [path.strip() for path in open(path_file, 'r').readlines()]
        for path in paths:
            bill_t = Bill(open(path, 'r').read(), "JSON")
            bills_t.bills.append(bill_t)
        return bills_t


    # This method sends a request to GovTrack and retrieves the json info
    # @params:
    # 1. congress_n: the number of congress that we want to get bils for
    # 2. write: specifies whether or not we'd like to write our results to a document
    def scrape_by_congress(self, congress_n, write):
        url = Websites.govtrack_congress_url(congress_n) 
        page = urllib2.urlopen(url).read()
        # Before the write, we need to remove the three line metadata
        res = {"bills": json.loads(page)["objects"]}
        if write:
            f = open("./bills/congress" + str(congress_n), "w+")
            f.write(json.dumps(res, ensure_ascii=True))
            f.close()
        return res

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

    # Scrapes in bulk for now
    if cmd == "scrape":
        r = Reader()
        if len(sys.argv) != 3 and len(sys.argv) != 2:
            print("Usage: python main.py scrape [file with congress numbers and write/not write]")

        if len(sys.argv) == 2:
            congress_rules = "./bills/congress-rules.txt"
        else:
            congress_rules = sys.argv[2]

        f = open(congress_rules, "r+")
        congresses = f.readlines()
        successes = ""
        for congress in congresses:
            l = congress.split()
            congress_n = int(l[0])
            write_indicator = l[1]
            should_write = (write_indicator.lower() == "true")
            if r.scrape_by_congress(congress_n, should_write) and should_write:
                successes += str(congress_n) + " " + str(not should_write).lower() + "\n"
            if not should_write:  # Already written, should not write again
                successes += str(congress_n) + " " + str(should_write).lower() + "\n"
        f.close()
        f = open(congress_rules, "w+")
        # automatically rewrite congress rules
        f.write(successes)


    # csvfile = open("112data.csv", "wb")
    # w = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # ATTRIBUTES = [path.strip() for path in open("attributes.txt", "r").readlines()]
    # r.serialize_paths("112json.txt")
    # bt = r.read_raw_congresses("112json.txt")
    # for bill in bt.bills:
    #    bill.serialize_attributes(w)
    # r.scrape_by_congress(112, True)
