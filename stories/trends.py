from __future__ import division, print_function
import numpy as np
import pandas as pd
import operator
import os
import re
import matplotlib.pyplot as plt

def get_year_and_month(datestring):
    if datestring != 'NA':
        argYear, argMonth, argDay = datestring.split('-')
        return argYear, argMonth
    else:
        return 'NA', 'NA'



def get_SCDB_info(infile):
    ''' Takes as input the Supreme Court Database file and returns 
        a DataFrame indexed by docket number and columns the case properties
    '''
    ## Create a dictionary to store info
    d = {}
    ## open the file and read the header
    f = open(infile, 'r')
    header = f.next().split('\t')
    ## Find index of columns of interest.
    dcol = header.index('docket')
    ncol = header.index('caseName')
    wcol = header.index('partyWinning')
    majcol = header.index('majVotes')
    mincol = header.index('minVotes')
    issuecol = header.index('issueArea')
    decdatecol = header.index('dateDecision')
    argdatecol = header.index('dateArgument')
    reargdatecol = header.index('dateRearg')
    
    for line in f:
        sl = line.split('\t')
        docket = sl[dcol]
        caseName = sl[ncol]
        winner = 'Pet' if sl[wcol] == '1' else 'Res'
        majority_votes = sl[majcol]
        minority_votes = sl[mincol]
        decDate = sl[decdatecol]        ## Change to datetime object?
        argDate = sl[argdatecol]        ## same
        reargDate = sl[reargdatecol]
        if reargDate != 'NA':
            argDate = reargDate
        ## If we still don't have an argument date, just use the decision date
        if argDate == 'NA':
            argDate = decDate
        argYear, argMonth = get_year_and_month(argDate)

        if docket not in d:
            d[docket] = {}
            d[docket]['caseName'] = caseName
            d[docket]['partyWinning'] = winner
            d[docket]['majVotes'] = majority_votes
            d[docket]['minVotes'] = minority_votes 
            d[docket]['argDate'] = argDate  
            d[docket]['decDate'] = decDate
            d[docket]['argMonth'] = argMonth  
            d[docket]['argYear'] = argYear 
    f.close()
    return pd.DataFrame.from_dict(d,orient='index')





scdb_file = '/Users/nasrallah/Desktop/Insight/courtcast/data/SCDB/SCDB_2014_01_justiceCentered_Citation_tab.txt'
scdb = get_SCDB_info(scdb_file)


g = scdb.groupby('argYear')





import pandas as pd
d = pd.read_csv('/Users/nasrallah/Desktop/Insight/courtcast/db/database_table.txt', sep='\t', index_col=0) 
## drop undecided cases
d = d[d.winner != '?']
## change type of minVotes col to int
d[['minVotes']] = d[['minVotes']].astype(float).astype(int)
d[['winner']] = d[['winner']].astype(float).astype(int)

## get a smaller more manageable data frame
v = d[['minVotes', 'argYear', 'winner']]
## get just the subset where minVotes == 0
v_uni = v[v.minVotes == 0]
v_res = v[v.winner == 0]

## group by year
uni = v_uni.groupby('argYear').count()
res = v_res.groupby('argYear').count()
tot = v.groupby('argYear').count()
prop_uni = (uni/tot).minVotes
prop_res = (res/tot).winner
prop = prop_res.join(prop_uni)
prop_uni = prop_uni.dropna()
prop_res = prop_res.dropna()

prop_uni = prop_uni[prop_uni.index != 2005]
prop_res = prop_res[prop_res.index != 2005]

prop_uni.plot()


plt.plot(prop_uni.index,prop_uni.minVotes)
plt.axis([2005, 2014, 0, 1])
plt.xaxis.set_ticklabels(uni.index)

