import json
import os
import csv
import sys
import numpy as np
import time


ATTRIBUTES = []
ATT_FILES = {}
MIN_NUM = 25
MAX_NUM =200

class Bill(object):
    # Takes in jstring
    def __init__(self, jstr, type):
 	self.id = ""
        if type.lower() == "json":
            self.json_info = self.set_json(jstr)
        elif type.lower() == "csv":
            pass 
	self.vector = []

    # Load the string (read from the file) into the json_info
    def set_json(self, s):
        return json.loads(s)

    # Save selected attributes and final vector
    def serialize_attributes(self, vocabs):
    	vector = np.zeros((1,1))
	data_array = np.zeros((1,1))
    	for attribute in ATTRIBUTES:
		data = self.json_info
		for path in attribute.split(","):
			if data != None:
				data = data[path]
		if attribute == "amendments" or attribute == "actions" or attribute == "cosponsors": # Count amendments, actions and cosponsors
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
		self.file_dict = files # Dictionary of attribute name to file name (where the voacb for each attribute is)
		self.bill_output = output
	# Attribute is a string, bills is an array of bills
	def bag_of_words(self, attribute, bills):
		print "Creating vocabulary for " + attribute + "..."
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
		total_bum = bt.total_num
		for bill in bills:
			if i/total_num >= progress:
				print (str(progress*100) + "% done...")
				progress += 0.25
			w.writerow(bill.vector)			
			i += 1

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
	i = 0
        for path in paths:
            bill_t = Bill(open(path, 'r').read(), "JSON")
            bills_t.bills.append(bill_t)
	    i += 1 
	bills_t.total_num = i
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
    # Objects for csv file with data vectors
    csvfile = open("112data.csv", "w+") 
    # Vocab file paths
    ATTRIBUTES = [path.strip() for path in open("attributes.txt", "r").readlines()]
    for line in open("att_files.txt","r").readlines(): #Load in vocab file locations
    	line = line.strip().split("|")
	ATT_FILES[line[0]] = open(line[1], "w")
    vec_writer = Writer(ATT_FILES, csvfile)
    # r.serialize_paths("112json.txt")
    print("Loading bill data...")
    bt = r.read_raw_congresses("112json.txt")
    vocabs = {}
    for att in ATT_FILES.keys():
    	vocabs[att] = vec_writer.bag_of_words(att, bt.bills)
    print("Vectorizing bills...")
    progress = 0.25
    i = 1.0
    total_num = bt.total_num
    for bill in bt.bills:
	if i/total_num >= progress:
		print(str(progress*100)+"% done...")
		progress += 0.25
        bill.serialize_attributes(vocabs)
	i += 1
    # Write vectors to csv file
    print("Saving bills to file...")
    vec_writer.save_vectors(bt)
