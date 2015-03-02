from __future__ import division, print_function
from sklearn.ensemble import RandomForestClassifier
from sklearn import tree 

from sklearn import preprocessing
from sklearn import metrics
from sklearn import svm
from sklearn.cross_validation import train_test_split, cross_val_score
from sklearn import tree
import numpy as np
import pandas as pd




def auc_shuffle(y, pred_y, ntimes):
    y_s = y.copy()
    permuted_auc = np.array([])
    for i in range(ntimes):
        shuffle(y_s)
        permuted_auc = np.append(permuted_auc, metrics.roc_auc_score(y_s, pred_y))
    return permuted_auc



####### Plot some AUC permutations
a = pd.Series(auc_shuffle(y, svm_pred_self, 1000))
a.hist()
plt.axis([0.25, 0.75, 0, 300])
#plt.axvline(0.683897166585, color='k', linewidth=1.0)            
plt.arrow( 0.684, 50.0, 0.0, -30, fc="k", ec="k", head_width=0.02, head_length=20 )

b = pd.Series(auc_shuffle(z, svm_pred, 5000))
b.hist()
plt.axis([0.25, 0.75, 0, 1500])
#plt.axvline(0.0.696117804552, color='k', linewidth=1.0)            
plt.arrow( 0.696, 100.0, 0.0, -50, fc="k", ec="k", head_width=0.015, head_length=50 )
plt.title('AUC permutation test')
plt.ylabel('count', fontsize=14, labelpad=10)
plt.xlabel('AUC', fontsize=14, labelpad=10)
plt.tight_layout()
########



def main():

    infile = '/Users/nasrallah/Desktop/Insight/courtcast/db/feature_table_2.txt'

    ## Kennedy's words carry low weight among the justices, indicating that perhaps his speech is the least predictive of the outcome. Doesn't reveal much. That is IF the order is preserved...
    feature_names = ['amicus', 'argYear', 'argMonth', 'cutoffs_ALL', 'cutoffs_BREYER', 'cutoffs_GINSBURG', 'cutoffs_KENNEDY', 'cutoffs_ROBERTS', 'cutoffs_SCALIA', 'words_BREYER', 'words_GINSBURG', 'words_KENNEDY', 'words_ROBERTS', 'words_SCALIA', 'sentiment_BREYER', 'sentiment_GINSBURG', 'sentiment_KENNEDY', 'sentiment_ROBERTS', 'sentiment_SCALIA']
    #print(feature_names)

    ## get the feature table and partition into a 'gold' testing set and a training set (rest)
    d = pd.read_csv(infile, sep='\t', index_col=0)    
    #print(d.head())
    #print(d.shape)

    ## Break into decided and undecided cases
    dU = d[pd.isnull(d.winner)]
    dD = d[pd.notnull(d.winner)]
    
    ## Break the decided cases into training and testing sets
    dX = dD[dD.argYear < 2013]
    dW = dD[dD.argYear >= 2013]
       
    ## Save the outcomes for these groups
    y = dX.winner
    z = dW.winner
    
    ## Extract only the features for each dataset
    X = dX[feature_names]
    W = dW[feature_names]
    U = dU[feature_names]
    
    ## store the indices for recombining later????
    X_i = X.index
    W_i = W.index
    U_i = U.index
    
    ## Pull out the winners of the test and train set
    y = preprocessing.LabelEncoder().fit_transform(y)
    z = preprocessing.LabelEncoder().fit_transform(z)
           
    ## Get a numpy ndarray X (2d) of just the case features for train and test set
    X = X.values.astype(np.float)    
    W = W.values.astype(np.float)    
    U = U.values.astype(np.float)    
    


    ## Define a scoring function with the Matthew correlation coefficient for cross-validation with unbalanced data
    mc_scorer = metrics.make_scorer(metrics.matthews_corrcoef)

    ##################### Random Forest #####################
    print('\nRandom Forest analyses:')   
    RF = RandomForestClassifier(n_estimators=80)
    RF_fit = RF.fit(X,y)
    RF_pred = RF_fit.predict(W)
    RF_prob = RF_fit.predict_proba(W)      ## Average outcome of all trees

    ## Classification probabilities
    #print('RF Prediction probabilities:')
    #for i,j in zip(RF_pred,RF_prob): print(i,j)

    ## Feature importances are helpful
    print('RF feature_importances:')
    for i, j in zip(feature_names, RF_fit.feature_importances_): print(i,j)
    
    print(metrics.classification_report(z, RF_pred))
    print(metrics.confusion_matrix(z, RF_pred))
    print('Test Accuracy:', RF_fit.score(W,z))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(z, RF_pred))
    
    RF_scores = cross_val_score(RF, X, y, cv=5, scoring=mc_scorer)
    #print('\nCross-validation scores:', RF_scores)
    print("CV Avg Matthews CC: %0.2f (+/- %0.2f)" % (RF_scores.mean(), RF_scores.std() * 2))    
    print('-'*20)
    ## Transform removes the lower-importance features from the dataset and returns a trimmed input dataset. 
    ## In this case it removed the interruptions, but we already saw that removing them lowered performance.
    ## Was I overfitting?
    #print(RF.transform(X))



    ##################### SVM #####################

#### class_weight='auto'

    print('\n' + '#'*15 + ' SVM ' + '#'*15)
    my_svm = svm.SVC(C=1.0, kernel='linear', probability=True, class_weight='auto')
    svm_fit = my_svm.fit(X, y)
    svm_pred = svm_fit.predict(W)
    svm_prob = svm_fit.predict_proba(W)            ## Class probabilities, based on log regression on distance to hyperplane.
    svm_dist = svm_fit.decision_function(W)        ## Distance from hyperplane for each point
    #SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3, gamma=0.0, kernel='rbf', max_iter=-1, probability=False, random_state=None, shrinking=True, tol=0.001, verbose=False)

    ## Classification probabilities
    #print('SVM Prediction probabilities:')
    #for i,j,k in zip(svm_pred, svm_prob, svm_dist): print(i,j,k)    

    print(metrics.classification_report(z, svm_pred))
    print(metrics.confusion_matrix(z, svm_pred))
    print('Test Accuracy:', svm_fit.score(W,z))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(z, svm_pred))
    print('AUC:', metrics.roc_auc_score(z,svm_pred))
    
    SVM_scores = cross_val_score(my_svm, X, y, cv=5, scoring=mc_scorer)
    #print('\nCross-validation scores:', SVM_scores)
    print("CV Avg Matthews CC: %0.2f (+/- %0.2f)" % (SVM_scores.mean(), SVM_scores.std() * 2))    
    
    #print(my_svm.predict([[-1, 1]]))

    ## Predict outcomes of the training data to see if do much better than cv data (overfitting)
    svm_pred_self = svm_fit.predict(X)
    print(metrics.classification_report(y, svm_pred_self))
    print(metrics.confusion_matrix(y, svm_pred_self))
    print('Test Accuracy:', svm_fit.score(X, y))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(y, svm_pred_self))
    print('AUC:', metrics.roc_auc_score(y,svm_pred_self))
    print('-'*20)


    ##################### Logistic Regression #####################


    print('\nLR analyses:')
    from sklearn.linear_model import LogisticRegression
    # Train
    LR = LogisticRegression(penalty='l2',C=1.0, fit_intercept=True, class_weight='auto')
    LR_fit = LR.fit(X, y) 


    LR_pred = LR_fit.predict(W)
    LR_prob = LR_fit.predict_proba(W)            ## Class probabilities, based on log regression on distance to hyperplane.



    print(metrics.classification_report(z, LR_pred))
    print(metrics.confusion_matrix(z, LR_pred))
    print('Test Accuracy:', LR_fit.score(W,z))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(z, LR_pred))
    print('AUC:', metrics.roc_auc_score(z, LR_pred))
   
    LR_scores = cross_val_score(LR_fit, X, y, cv=5, scoring=mc_scorer)
    #print('\nCross-validation scores:', LR_scores)
    print("CV Avg Matthews CC: %0.2f (+/- %0.2f)" % (LR_scores.mean(), LR_scores.std() * 2))    
    
    #print(LR_fit.predict([[-1, 1]]))

    ## Predict outcomes of the training data to see if do much better than cv data (overfitting)
    LR_pred_self = LR_fit.predict(X)
    print(metrics.classification_report(y, LR_pred_self))
    print(metrics.confusion_matrix(y, LR_pred_self))
    print('Test Accuracy:', LR_fit.score(X, y))
    print('Test Matthews corrcoef', metrics.matthews_corrcoef(y, LR_pred_self))
    print('AUC:', metrics.roc_auc_score(y,LR_pred_self))
    print('-'*20)



    #### **************

    ## Append training and testing sets
    XW = np.append(X,W, axis=0)
    yz = np.append(y,z)

    my_svm = svm.SVC(C=0.2, kernel='linear', probability=True)
    svm_fit = my_svm.fit(XW,yz)

    ## Do some cross validation on the whole training
    svm_scores = cross_val_score(svm_fit, XW, yz, cv=5)
    #print('\nCross-validation scores:', svm_scores) 
    
    #SVC(C=1.0, cache_size=200, class_weight=None, coef0=0.0, degree=3, gamma=0.0, kernel='rbf', max_iter=-1, probability=False, random_state=None, shrinking=True, tol=0.001, verbose=False)


    ## Once I've picked a model, test all cases and save the predictions and probabilities
    ## along with the case features as a database_table to put into mysql
    ## get the predictions for the training data, the test data, and the undecided cases
    svm_XW_predictions = svm_fit.predict(XW)
    svm_U_predictions = svm_fit.predict(U)

    ## get distances tot he hyperplane
    svm_XW_distances = svm_fit.decision_function(XW) 
    svm_U_distances = svm_fit.decision_function(U) 

    ## get the classification probability tuples for each of these 
    svm_XW_probabilities = svm_fit.predict_proba(XW)
    svm_U_probabilities = svm_fit.predict_proba(U)
    
    ## Get max of each probability tuple
    svm_XW_probabilities = np.apply_along_axis(max, arr=svm_XW_probabilities,axis=1)
    svm_U_probabilities = np.apply_along_axis(max, arr=svm_U_probabilities,axis=1)
    
    ## Recombine the original two divided dataframes to match these predictions
    dXW = dX.append(dW)
 
    ## Add to the original split data frames
    dXW['prediction'] = pd.Series(svm_XW_predictions, index=dXW.index)
    dXW['confidence'] = pd.Series(svm_XW_probabilities, index=dXW.index)
    dU['prediction'] = pd.Series(svm_U_predictions, index=dU.index)
    dU['confidence'] = pd.Series(svm_U_probabilities, index=dU.index)

    ## Combine these two now complete dataframes
    dXWU = dXW.append(dU)
 
    ## Replace missing values with something for the database
    dXWU.fillna('?', inplace=True)
 
    ## Save the case info, features, SVM predictions and probabilities to file      
    outfile = '/Users/nasrallah/Desktop/Insight/courtcast/db/database_table.txt'
#    dXWU.to_csv(outfile, sep='\t')
    
    
if __name__ == '__main__':
    main()
