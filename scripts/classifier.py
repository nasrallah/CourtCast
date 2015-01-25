from __future__ import division, print_function
from sklearn.ensemble import RandomForestClassifier
from sklearn import preprocessing
from sklearn import metrics
from sklearn import svm
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pymysql as mdb
import numpy as np
import pandas as pd

def main():

    db = mdb.connect(user="root", host="localhost", db="scotus", charset='utf8')
    d = pd.read_sql("""SELECT docket, interrupted, amicus, winner 
        FROM cases ORDER BY docket;""", con=db)
    
    gold_test_start = d.shape[0] * 0.8
    d = d.drop(d.index[gold_test_start:])
    #print(d.head())
    
    feature_names = ['amicus','interrupted']
#    feature_names = ['amicus']
#    feature_names = ['interrupted']

    print(feature_names)

    X = d[feature_names].values.astype(np.float)    
    y = preprocessing.LabelEncoder().fit_transform(d.winner)
    
    ## Split into training and testing sets
#    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)    

    this_test_start = X.shape[0] * 0.75 
    X_train = X[:this_test_start,]
    X_test = X[this_test_start:,]
    y_train = y[:this_test_start]
    y_test = y[this_test_start:]
    
    RF = RandomForestClassifier(n_estimators=100)
    RF_fit = RF.fit(X_train,y_train)
    RF_pred = RF_fit.predict(X_test)
    
    print(metrics.classification_report(y_test, RF_pred))
    print(metrics.confusion_matrix(y_test, RF_pred))

    my_svm = svm.SVC()
    my_svm.fit(X_train, y_train)
    #SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3, gamma=0.0, kernel='rbf', max_iter=-1, probability=False, random_state=None, shrinking=True, tol=0.001, verbose=False)

    print(my_svm.predict([[-1, 1]]))


    
if __name__ == '__main__':
    main()
