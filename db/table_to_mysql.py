import numpy as np
import pandas as pd 
import pymysql as mdb

## Read in the table from a text file
infile = '/Users/nasrallah/Desktop/Insight/courtcast/db/database_table.txt'
d = pd.read_csv(infile, sep='\t', index_col=0)

## Connect to sql database
con = mdb.connect('localhost', 'root', 'maddox79', 'scotus') #host, user, password, #database

## Write contents to database
d.to_sql('cases', con=con, flavor='mysql', index_label='docket', if_exists='append')
