import uuid
import string
import nltk
import os
import re
import json
from nltk.corpus import stopwords
from nltk.stem.porter import *
from collections import Counter

class Folder:

    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1]

    def openEveryFiles(self):
        idx = InvertedIndex()
        dlt = DocumentLengthTable()
        for filename in os.listdir(self.path):
            file = File(self.path+"/"+filename)
            file.indexFile(idx, dlt)
        return idx, dlt

class File:

    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1]
        self.length = self.get_document_length()
    
    def indexFile(self, idx, dlt):
        useful_words = self.getUsefulWords()
        # words_counts = Counter(useful_words)
        # with open("index.json",'r') as index:
        #     data = json.load(index)
        #     for word,freq in words_counts.items():
        #         if word not in data:
        #             data[word]=([freq],[self.name])
        #         else:
        #             flag=0
        #             for i,search_file in enumerate(data[word][1]): 
        #                 if self.name is search_file:
        #                     data[word][0][i]=freq
        #                     flag=1
        #             if flag is 0:
        #                 data[word][0].append(freq)
        #                 data[word][1].append(self.name)
        # with open("index.json",'w') as index:
        #     json.dump(data, index, indent = 4)
        
        for word in useful_words:
            idx.add(str(word),str(self.name))
        
        dlt.add(self.name, self.length)

    def get_document_length(self):
        with open(self.path, 'r') as f:
            return len(re.findall(r'\w+', f.read().lower()))


    def getUsefulWords(self):
        with open(self.path, 'r') as f:
            stop = set(stopwords.words('english'))
            stemmer = PorterStemmer()
            words = re.findall(r'\w+', f.read().lower())
            useful_words = [i for i in words if i not in stop]
            stemmed_words = [stemmer.stem(word) for word in useful_words]
            return stemmed_words
        
class InvertedIndex:

	def __init__(self):
		self.index = dict()

	def __contains__(self, item):
		return item in self.index

	def __getitem__(self, item):
		return self.index[item]

	def add(self, word, docid):
		if word in self.index:
			if docid in self.index[word]:
				self.index[word][docid] += 1
			else:
				self.index[word][docid] = 1
		else:
			d = dict()
			d[docid] = 1
			self.index[word] = d

	#frequency of word in document
	def get_document_frequency(self, word, docid):
		if word in self.index:
			if docid in self.index[word]:
				return self.index[word][docid]
			else:
				raise LookupError('%s not in document %s' % (str(word), str(docid)))
		else:
			raise LookupError('%s not in index' % str(word))

	#frequency of word in index, i.e. number of documents that contain word
	def get_index_frequency(self, word):
		if word in self.index:
			return len(self.index[word])
		else:
			raise LookupError('%s not in index' % word)


class DocumentLengthTable:

	def __init__(self):
		self.table = dict()

	def __len__(self):
		return len(self.table)

	def add(self, docid, length):
		self.table[docid] = length

	def get_length(self, docid):
		if docid in self.table:
			return self.table[docid]
		else:
			raise LookupError('%s not found in table' % str(docid))

	def get_average_length(self):
		sum = 0
		for length in self.table.values():
			sum += length
		return float(sum) / float(len(self.table))