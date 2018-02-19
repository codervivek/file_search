import uuid
import string
import nltk
import os
import re
import json
from nltk.corpus import stopwords
from collections import Counter

class Folder:

    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1]

    def openEveryFiles(self):
        for filename in os.listdir(self.path):
            file = File(self.path+"/"+filename)
            file.indexFile()

class File:

    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1]
    
    def indexFile(self):
        useful_words = self.getUsefulWords()
        words_counts = Counter(useful_words)
        with open("index.json",'r') as index:
            data = json.load(index)
            for word,freq in words_counts.items():
                if word not in data:
                    data[word]=([freq],[self.name])
                else:
                    flag=0
                    for i,search_file in enumerate(data[word][1]): 
                        if self.name is search_file:
                            data[word][0][i]=freq
                            flag=1
                    if flag is 0:
                        data[word][0].append(freq)
                        data[word][1].append(self.name)
        with open("index.json",'w') as index:
            json.dump(data, index, indent = 4)


    def getUsefulWords(self):
        with open(self.path, 'r') as f:
            stop = set(stopwords.words('english'))
            words = re.findall(r'\w+', f.read().lower())
            useful_words = [i for i in words if i not in stop]
            return useful_words