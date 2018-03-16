import uuid
import string
import nltk
import os
import re
import json
from nltk.stem.porter import *
from collections import Counter

STOPWORDS = {"don't", 'until', "aren't", "you're", 'her', 'he', 'so', 
            'nor', 'has', "needn't", 'such', 'below', 'why', 'while',
            'not', 'what', 'now', 'because', 'needn', "hadn't", 'mustn', 
            'herself', 'is', "wouldn't", 'll', 've', 'for', 'too', "that'll", 
            'the', 'that', 'yours', 'me', 'doesn', "shouldn't", 'before', 
            'off', 'mightn', 'from', 'out', 'no', "couldn't", 'do', 'or', 
            'of', "it's", 'over', 'couldn', 'it', 'under', 'then', 
            'above', "didn't", 'between', 'and', "mightn't", 'again', 
            'was', 'where', 'about', 'own', 'weren', 'you', 'but', 'this',
            'them', 'hasn', 'if', 'shouldn', 'aren', 'she', "you've", 'how',
            'some', 'more', "mustn't", 'theirs', 'yourselves', "shan't",
            'their', 'having', 'ain', 'with', 'isn', 'than', 's', 'have',
            'hadn', 'all', 'won', 'as', 'both', "haven't", 'yourself',
            "wasn't", 'did', 'to', 'whom', 'which', 'my', 'very',
            'same', 'down', 'during', 'ma', 'an', 're', 'there', 
            'are', 'be', 'few', 'him', 'through', 'after', 'can',
            'when', 'his', 'were', 'here', 'those', "doesn't", 
            'these', 'i', 'am', 'hers', 'our', 'shan', 'o',
            'doing', "you'll", 'up', "isn't", 'its', "you'd",
            'm', 'against', 'himself', 'they', 'into', "won't",
            'ours', 'a', 'don', 'myself', 'only', 'just', 't', 
            'does', "weren't", 'any', 'in', 'most', 'd',
            "hasn't", 'being', 'wouldn', 'been', 'will', "she's", 'didn',
            'had', 'by', 'wasn', 'we', 'on', 'itself', 'should', "should've", 
            'further', 'once', 'themselves', 'at', 'who', 'ourselves', 'other',
            'haven', 'your', 'y', 'each'}

class Folder:

    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1]

    def openEveryFiles(self):
        idx = InvertedIndex()
        dlt = DocumentLengthTable()
        files = dict()
        for filename in os.listdir(self.path):
            file = File(self.path+"/"+filename)
            file.indexFile(idx, dlt)
        database = {"dirPath":self.path,"dirModifyTime":os.path.getmtime(self.path),
                    "invertedIndex":idx.index,"documentLengthTable":dlt.table}
        with open("index.json",'w') as indexFile:
            json.dump(database,indexFile,indent=4,sort_keys=True)
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
        
        for i, line in enumerate(useful_words):
            for word in line:
                # print(idx.index,i)
                idx.add(str(word),str(self.name),i)
        
        dlt.add(self.name, self.length)

    def get_document_length(self):
        with open(self.path, 'rb') as f:
            # i=i+1
            print("Indexing file: "+self.name)
            return len(re.findall(r'\w+', f.read().decode("utf8")))


    def getUsefulWords(self):
        with open(self.path, 'rb') as f:
            stemmer = PorterStemmer()
            contents = f.read().decode("utf8")
            lines = contents.split("\n")
            words = [re.findall(r'\w+', line.lower()) for line in lines]
            useful_words = [[word for word in i if word not in STOPWORDS] for i in words]
            stemmed_words = [[stemmer.stem(word) for word in i] for i in useful_words]
            return stemmed_words
        
class InvertedIndex:

    def __init__(self, index=dict()):
        self.index = index

    def __contains__(self, item):
        return item in self.index

    def __getitem__(self, item):
        return self.index[item]

    def add(self, word, docid, line):
        if word in self.index:
            if docid in self.index[word]:
                self.index[word][docid][1] = self.index[word][docid][1]+[line]
                self.index[word][docid][0] += 1
                # self.index[word][docid] = temp
            else:
                self.index[word][docid] = [1,[line]]
        else:
            d = dict()
            d[docid] = [1,[line]]
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

    def __init__(self, table=dict()):
        self.table = table

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