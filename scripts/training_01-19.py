from __future__ import division, print_function
import numpy as np
#import pandas as pd
#import operator
#import os
#import re
import string
#import sys


def get_justice_votes(vote_file):
    votes = {}
    with open(vote_file, 'r') as f:
        for line in f:
            sl = line.strip().split(' +++$+++ ')
            docket = sl[0]
            for i in range(1,10):
                 justice, vote = sl[i].split('::')
                 votes[(docket, justice)] = vote
    return votes


def get_winners(win_file):
    winners = {}
    with open(win_file, 'r') as f:
        for line in f:
            docket, winner = line.strip().split(' +++$+++ ')
            winners[docket] = winner
    return winners
  

def get_justice_text(text_file):
    text = {}
    with open(text_file, 'r') as f:
        for line in f:
            sl = line.strip().split(' +++$+++ ')
            if sl[4] == 'NOT JUSTICE':
                continue
            vote = sl[5]
            presenter = sl[6]
            if vote == presenter:
                ## Categorize as 'for' or 'pos'
            else:
                ## Categorize as 'against' or 'neg'
            print(sl[4])
            
            
         
def main():
 
    vote_file = '/Users/nasrallah/Desktop/supreme_court_dialogs_corpus_v1.01/supreme.votes.txt'
    votes = get_justice_votes(vote_file)
#    for v in votes: print(v, votes[v])
    
    win_file = '/Users/nasrallah/Desktop/supreme_court_dialogs_corpus_v1.01/supreme.outcome.txt'
    winners = get_winners(win_file)
#    for w in winners: print(w, winners[w])

    text_file = '/Users/nasrallah/Desktop/supreme_court_dialogs_corpus_v1.01/supreme.conversations.txt'
    get_justice_text(text_file)

if __name__ == '__main__':
    main()
