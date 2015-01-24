from __future__ import division, print_function
from sklearn.ensemble import RandomForestClassifier
import pymysql as mdb
import numpy as np
import pandas as pd


def main():

    db = mdb.connect(user="root", host="localhost", db="scotus", charset='utf8')
    d = query_results = pd.read_sql("""SELECT docket, interrupted, amicus, winner 
        FROM cases ORDER BY docket;""", con=db)

    #text_file = '/Users/nasrallah/Desktop/Insight/scotus_predict/db/database_table.txt'
    #d = pd.DataFrame.from_csv(text_file, header=1, sep='\t', index_col=0)
    print(d)
    

if __name__ == '__main__':
    main()
