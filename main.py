from src.indexing import File, Folder
# from src.config import connect
from src.ranking import QueryProcessor
import operator
import pprint
# con, meta = connect()

def xyz():
    # folder = Folder(input("Enter dir path: "))
    folder = Folder("/home/vivek/Documents/test")
    index, dlt = folder.openEveryFiles()
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(index.index)
    pp.pprint(dlt.table)
    query = input("Enter the search query: ")
    qp = QueryProcessor([query], index, dlt)
    results = qp.run()
    qid = 0
    for result in results:
        sorted_x = sorted(result.items(), key=operator.itemgetter(1))
        sorted_x.reverse()
        index = 0
        for i in sorted_x[:100]:
            tmp = (qid, i[0], index, i[1])
            print('{:>1}\tQ0\t{:>4}\t{:>2}\t{:>12}\tNH-BM25'.format(*tmp))
            index += 1
        qid += 1
xyz()
