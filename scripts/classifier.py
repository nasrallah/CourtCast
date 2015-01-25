from __future__ import division, print_function
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree 

from sklearn import preprocessing
from sklearn import metrics
from sklearn import svm
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree
import pymysql as mdb
import numpy as np
import pandas as pd

def main():

    db = mdb.connect(user="root", host="localhost", db="scotus", charset='utf8')
    d = pd.read_sql("""SELECT docket, interrupted, amicus, words_BREYER, words_GINSBURG, 
        words_KENNEDY, words_ROBERTS, words_SCALIA, winner 
        FROM cases ORDER BY docket;""", con=db)
    
    gold_test_start = d.shape[0] * 0.8
    d = d.drop(d.index[gold_test_start:])
    #print(d.head())
    
    feature_names = ['interrupted', 'words_BREYER', 'words_GINSBURG', 'words_KENNEDY', 'words_ROBERTS', 'words_SCALIA']
#    feature_names = ['amicus','interrupted']
#    feature_names = ['amicus']
#    feature_names = ['interrupted']
## After adding the word counts, removing amicus seems to improve the estimates.
## Interruptions do not have high feature weight (0.029) but removing them lowers precision, recall, and F1 across the board. 
## Kennedy's words carry the least weight among the justices, indicating that perhaps his speech is the least predictive of the outcome. Doesn't reveal much. That is IF the order is preserved...

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


    print('\nRandom Forest analyses:')   
    RF = RandomForestClassifier(n_estimators=100).fit(X_train,y_train)
    RF_pred = RF.predict(X_test)

    ## Feature importances are helpful
    print(RF.feature_importances_)
    
    ## These could be useful to see the actual predictions and their probabilities. 
    ## But why are all the class probabilities in increments of 0.2? 
    #print(RF.predict(X_test))
    #print(RF.predict_proba(X_test))    
    ## The score is useful as well, the average accuracy. Here it is 0.678
    
    print('score:', RF.score(X_test,y_test))
    print(metrics.classification_report(y_test, RF_pred))
    print(metrics.confusion_matrix(y_test, RF_pred))
    print('cv_score:', cross_val_score(RF, X, y))
    
    ## Transform removes the lower-importance features from the dataset and returns a trimmed input dataset. 
    ## In this case it removed the interruptions, but we already saw that removing them lowered performance.
    ## Was I overfitting?
    #print(RF.transform(X))

    print('\nDecision Tree analyses:')
    DT = tree.DecisionTreeClassifier(max_depth=None, min_samples_split=1, random_state=0).fit(X_train, y_train)
    DT_predict = DT.predict(X_test)

    print('score:', DT.score(X_test,y_test))
    print(metrics.classification_report(y_test, DT_predict))
    print(metrics.confusion_matrix(y_test, DT_predict))
    print('cv_score:', cross_val_score(DT, X, y))
    #tree.export_graphviz(DT, out_file='tree.dot', feature_names=feature_names, max_depth=5) 


    ## SVM
    print('\nSVM analyses:')
    my_svm = svm.SVC(kernel='linear', probability=True).fit(X_train, y_train)
    svm_pred = my_svm.predict(X_test)
    #SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3, gamma=0.0, kernel='rbf', max_iter=-1, probability=False, random_state=None, shrinking=True, tol=0.001, verbose=False)

    print('score:', my_svm.score(X_test,y_test))
    print(metrics.classification_report(y_test, svm_pred))
    print(metrics.confusion_matrix(y_test, svm_pred))
    print('cv_score:', cross_val_score(my_svm, X, y))
    
    #print(my_svm.predict([[-1, 1]]))


    
if __name__ == '__main__':
    main()
