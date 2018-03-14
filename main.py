from src.indexing import File, Folder, InvertedIndex, DocumentLengthTable
# from src.config import connect
from src.ranking import QueryProcessor
import operator
import pprint
import json
import os
# con, meta = connect()

def xyz():
    pp = pprint.PrettyPrinter(indent=4)
    database = ""
    # folderName = input("Enter dir path: ")
    folderPath = "/home/vivek/Documents/test"
    with open("index.json") as indexFile:
        database = json.load(indexFile)
    if database["dirPath"] != folderPath or database["dirModifyTime"] != os.path.getmtime(folderPath):
        folder = Folder(folderPath)    
        index, dlt = folder.openEveryFiles()
        
        pp.pprint(index.index)
    else:
        index, dlt = InvertedIndex(index=database["invertedIndex"]), DocumentLengthTable(table=database["documentLengthTable"])
    # pp.pprint(index.index)
    # pp.pprint(dlt.table)
    query = input("Enter the search query: ")
    qp = QueryProcessor([query], index, dlt)
    results = qp.run()
    qid = 0
    # pp.pprint(results)
    for result in results:
        sorted_x = sorted(result.items(), key=operator.itemgetter(1))
        sorted_x.reverse()
        for (file, result) in sorted_x:
            print("File name: ",folderPath+"/"+file)
            print("BM25 score: ",result[0])
            print("Frequency of word: ",result[1])
            print("Document length: ",result[2])
            print("Ratio: ",result[2]/result[1],"\n\n")
            
xyz()
