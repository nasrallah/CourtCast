from __future__ import division, print_function
from nltk import stem
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.classify import NaiveBayesClassifier
import nltk.classify.util
import numpy as np
import random
#import pandas as pd
#import operator
#import os
#import re
import string
#import sys




def create_feature_dict(words):
    return dict([(word, True) for word in words])

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
  

def extract_word_features(text, tokenizer, stemmer, stopper):
    ''' Takes a string and returns a dictionary with keys the words and the value True '''
    words = tokenizer.tokenize(text)
    words = [stemmer.stem(w) for w in words]    
    #words = [i for i in stemmed_words if i not in stopper]
    #print words
    return create_feature_dict(words)


def extract_word_features2(text, tokenizer, lemmer, stopper):
    ''' Takes a string and returns a dictionary with keys the words and the value True '''
    words = tokenizer.tokenize(text)
    words = [lemmer.lemmatize(w) for w in words]    
    #words = [i for i in stemmed_words if i not in stopper]
    #print words
    return create_feature_dict(words)
    

def get_training_features(text_file):
    ''' Takes a compiled text file of utterances from oral arguments, returns a list of tuples [(feature_dict, label)]
        It ignores which Justice is speaking, using them all as training data. '''
    tokenizer = RegexpTokenizer(r'\b\w\w+\b')
    stemmer = stem.snowball.EnglishStemmer()
    wnl = stem.WordNetLemmatizer()
    stopper = stopwords.words('english')
    features = []
    with open(text_file, 'r') as f:
        for line in f:
            sl = line.strip().split(' +++$+++ ')
            ## Skip things the lawyers say
            if sl[4] == 'NOT JUSTICE':
                continue
            vote = sl[5]
            presenter = sl[6]
            ## skip the phrase if the justice did not vote ('NA') or was an announcement ('')
            if vote == 'NA' or presenter == '':
                #print('*'*30,line, vote)
                continue
            ## determine its polarity (for or against)
            polarity = 'pos' if vote == presenter else 'neg'
            phrase = sl[7]
            #print(vote, presenter, polarity)
            ## phrase --> cleaned list of words --> feature dictionary
            #word_feature_dict = extract_word_features(phrase, tokenizer, stemmer, stopper)
            word_feature_dict = extract_word_features2(phrase, tokenizer, wnl, stopper)
            ## create tuple of the (dict, polarity) & add it to the list of tuples
            features.append((word_feature_dict, polarity))
    return features

     
def main():
 
#    vote_file = '/Users/nasrallah/Desktop/Insight/scotus_predict/data/supreme_court_dialogs_corpus_v1.01/supreme.votes.txt'
#    votes = get_justice_votes(vote_file)
#    for v in votes: print(v, votes[v])
    
#    win_file = '/Users/nasrallah/Desktop/Insight/scotus_predict/data/supreme_court_dialogs_corpus_v1.01/supreme.outcome.txt'
#    winners = get_winners(win_file)
#    for w in winners: print(w, winners[w])

    text_file = '/Users/nasrallah/Desktop/Insight/scotus_predict/data/supreme_court_dialogs_corpus_v1.01/supreme.conversations.txt'
    #text_file = '/Users/nasrallah/Desktop/some_text.txt'
    
    ## Extract the feature sets
    feature_sets = get_training_features(text_file)
    
    ## Shuffle the features to mix up pos and neg
    #random.shuffle(feature_sets)
    
    ## Separate into train and test sets 
    cutoff = int(len(feature_sets)*3/4)
    train_feature_sets = feature_sets[:cutoff]
    test_feature_sets = feature_sets[cutoff:]
    print('train on %d instances, test on %d instances' % (len(train_feature_sets), len(test_feature_sets)))
 
    classifier = NaiveBayesClassifier.train(train_feature_sets)
    print('accuracy:', nltk.classify.util.accuracy(classifier, test_feature_sets))
    classifier.show_most_informative_features()  



if __name__ == '__main__':
    main()
