from src.indexing import File, Folder, InvertedIndex, DocumentLengthTable
# from src.config import connect
from src.ranking import QueryProcessor
from nltk.stem.porter import *
import operator
import pprint
import json
import os
import re
# con, meta = connect()

DEBUG = False
RESULT_SIZE = 10
DISPLAY_LINES = True
CACHE_SIZE = 10

def main():
    # pp = pprint.PrettyPrinter(indent=4)
    database = ""
    # folderName = input("Enter dir path: ")
    folderPath = "/home/vivek/Documents/test"
    with open("index.json") as indexFile:
        database = json.load(indexFile)
    if database["dirPath"] != folderPath or database["dirModifyTime"] != os.path.getmtime(folderPath):
        folder = Folder(folderPath)    
        index, dlt = folder.openEveryFiles()
        # pp.pprint(index.index)
    else:
        index, dlt = InvertedIndex(index=database["invertedIndex"]), DocumentLengthTable(table=database["documentLengthTable"])
    flag=1
    while (flag==1):
        query = input("Enter the search query: ").lower()
        with open("cache.json") as f:
            cache = json.load(f)
            if query in cache:
                print(cache[query][1])
                again = input("Do you want search again?: ").lower()
                if again != "yes" and again != "y":
                    flag=0
                continue
        words = query.split()
        stemmer = PorterStemmer()
        stemmed_words = [stemmer.stem(word) for word in words]
        qp = QueryProcessor([stemmed_words], index, dlt)
        results = qp.run()
        # pp.pprint(results)
        qid = 0
        if not results[0]:
            print("--------------------------------------\nNo results found\n--------------------------------------")
        for k,result in enumerate(results):
            sorted_x = sorted(result.items(), key=operator.itemgetter(1))
            sorted_x.reverse()
            ans=""
            for i, (file, result) in enumerate(sorted_x):
                if i>RESULT_SIZE-1:
                    break
                # ans=""
                ans+="--------------------------------------\nRank "+str(i+1)+"\nFile name: file://"+folderPath+"/"+file+"\n"
                if DISPLAY_LINES:
                    ans+="Found in:\n"
                    with open(folderPath+"/"+file,'r') as f:
                        lines = f.read().split("\n")
                        # for j, line in enumerate(lines):
                        #     l_words = re.findall(r'\w+',line.lower())
                        #     l_stemmer = PorterStemmer()
                        #     l_stemmed_words = [l_stemmer.stem(l_word) for l_word in l_words]
                        #     for word in stemmed_words:
                        #         if word.lower() in l_stemmed_words:
                        #             soln = "Line "+str(j+1)+" : "+line+"\n"
                        #             soln = soln.replace(word.lower(),'\033[92m'+word+'\033[0m')
                        #             ans+=soln
                        # for line in result
                        # print(result)
                        for line in result[1]:
                            for l in line[0][1]:
                                soln = lines[l]
                                for q_word in stemmed_words:
                                    x = re.compile(q_word, re.IGNORECASE)
                                    soln=x.sub('\033[1m\033[92m'+q_word.upper()+'\033[0m',soln)
                            # soln = "Line "+ str(line+1) +" : "+soln+"\n"
                                ans+="Line "+ str(l+1) +" : "+soln+"\n"
                if DEBUG:
                    ans+="BM25 score: "+str(result[0])+"\n"
                    ans+="Frequency and Document length: "+str(result[1])+"\n"
                ans+="--------------------------------------\n"
            print(ans)
            new_cache=dict()
            new_cache[query]=[1,ans]
            for key,value in cache.items():
                if value[0] < CACHE_SIZE:
                    new_cache[key] = [value[0]+1,value[1]]
            with open("cache.json",'w') as cachefile:
                json.dump(new_cache,cachefile,indent=4,sort_keys=True)
        again = input("Do you want search again?: ").lower()
        if again != "yes" and again != "y":
            flag=0
            
if __name__ == '__main__':
	main()