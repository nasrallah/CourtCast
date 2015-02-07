from flask import render_template, request, make_response
from app import app
import pymysql as mdb
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
#import seaborn as sns
from a_Model import ModelIt
import socket

def plot_features(df):
    ## Transpose the series
    df = df.T
    
    ## get the list of colors we want
#    my_colors = sns.color_palette("coolwarm_r", 5)
    my_colors = [(.8,0,0),(1,.4,.4),(1,.8,.8),(.6,.8,1),(.2,.6,1)]
    my_colors = my_colors + my_colors + my_colors
    #my_colors = my_colors + [(102,102,102)]
    my_colors = my_colors + [(0.75,0.75,0.75)]
    
    df.plot(kind="barh", color=my_colors, legend=False, grid=False, xlim=(-1,1))
    plt.axhline(14.5, color='k', linestyle = ':', linewidth=1.0)            
    plt.axhline(9.5, color='k', linestyle = ':', linewidth=1.0)            
    plt.axhline(4.5, color='k', linestyle = ':', linewidth=1.0)            
    plt.tight_layout()
    #plt.show()
    
    ## get the right path
    host = socket.gethostname()
    if 'atum' in host:
        path = 'app/static/'
    else:
        path = '/home/ubuntu/app/static/'
    ## Make sure the relative path is right...the 'home' directory here is ..courtcast/db/app/
    plt.savefig(path + 'images/fig.png')


## Right now the indicator is an integer. I'm not sure how I will store unknown case outcomes. This assumes there is nothing there.
def winlose(indicator):
    if indicator == '1':
        pet = 'won'
        res = 'lost'
    elif indicator == '0':
        pet = 'lost'
        res = 'won'
    else:
        pet = '?'
        res = '?'
    return pet, res    


## Connect to the database
db = mdb.connect(user="root", password="maddox79", host="localhost", db="scotus", charset='utf8')


@app.route('/images/<path:filename>')
def return_image (filename):
    response = make_response(app.send_static_file('images/' + filename))
    response.cache_control.max_age = 0
    return response

# @app.route('/')
# @app.route('/saucy')
# def index():
#     return render_template("index.html",
#         title = 'Home', user = { 'nickname': 'Sexy' },
#         )

# @app.route('/db')
# def scotus_page():
#     with db: 
#         cur = db.cursor()
#         cur.execute("SELECT caseName FROM cases LIMIT 15;")
#         query_results = cur.fetchall()
#     items = ""
#     for result in query_results:
#         items += result[0]
#         items += "<br>"
#     return items

# @app.route("/db_fancy")
# def scotus_page_fancy():
#     with db:
#         cur = db.cursor()
#         cur.execute("SELECT docket caseName, confidence, prediction, winner FROM cases ORDER BY caseName LIMIT 15;")
#         query_results = cur.fetchall()  ## returns a list of tuples. The list is the rows, the tuple the columns.
#     ## Transform this into a list of dictionaries, keyed by the names we want.
#     items = []
#     for result in query_results:
#         items.append({'docket':result[0], 'caseName':result[1], 'confidence':result[2], 'prediction':result[3], 'winner':result[4]})
#     return render_template('scotus.html', items=items)

@app.route('/')
def scotus_input():
  return render_template("input.html")

@app.route('/output')
def scotus_output():
  #pull 'ID' from input field and store it
  docket = request.args.get('ID')

#   with db:
#     cur = db.cursor()
#     ## Get the case details to print to screen
#     cur.execute("SELECT caseName, confidence, prediction, winner, docket FROM cases WHERE docket='%s';" % docket)
#     query_results = cur.fetchall()
#     ## Get features for plot and convert to floats
#     df = pd.read_sql("SELECT cutoffs_SCALIA, cutoffs_ROBERTS, cutoffs_KENNEDY, cutoffs_BREYER, cutoffs_GINSBURG, words_SCALIA, words_ROBERTS, words_KENNEDY, words_BREYER, words_GINSBURG, sentiment_SCALIA, sentiment_ROBERTS, sentiment_KENNEDY, sentiment_BREYER, sentiment_GINSBURG, amicus from cases WHERE docket='%s';" % docket, cur)
# #    cur.execute("SELECT cutoffs_SCALIA, cutoffs_ROBERTS, cutoffs_KENNEDY, cutoffs_BREYER, cutoffs_GINSBURG, words_SCALIA, words_ROBERTS, words_KENNEDY, words_BREYER, words_GINSBURG, sentiment_SCALIA, sentiment_ROBERTS, sentiment_KENNEDY, sentiment_BREYER, sentiment_GINSBURG, amicus FROM cases WHERE docket='%s';" % docket)
# #    feature_vals = list(cur.fetchall()[0])
#  
# ### use pandas to get record from db and plot it    
# #  d.plot(kind="barh", color=my_colors)
# 
# 
#   ## Create the plot and save it to file
#   y_labels = 'cutoffs_SCALIA, cutoffs_ROBERTS, cutoffs_KENNEDY, cutoffs_BREYER, cutoffs_GINSBURG, words_SCALIA, words_ROBERTS, words_KENNEDY, words_BREYER, words_GINSBURG, sentiment_SCALIA, sentiment_ROBERTS, sentiment_KENNEDY, sentiment_BREYER, sentiment_GINSBURG, amicus'.lower().split(', ')
#   num_features = len(feature_vals)
#   plt.subplot(1,1,1)             
#   plt.barh(np.arange(num_features), feature_vals, 0.5, color='b', align='center')
#   plt.axis([-1, 1, -1, 16])
#   plt.yticks(np.arange(num_features), y_labels)
#   plt.subplots_adjust(left=0.25, right = 0.925)
#   plt.axhline(9.5, color = 'black', linewidth=1.0)            
#   #plt.title(caseName, fontsize= 8)
# 
#   ## Make sure the relative path is right...the 'home' directory here is ..courtcast/db/app/
#   plt.savefig('/Users/nasrallah/Desktop/Insight/courtcast/db/app/static/images/fig.png')
#   plt.close()

  with db:
    cur = db.cursor()
    ## Get the case details to print to screen
    cur.execute("SELECT caseName, confidence, prediction, winner, docket FROM cases WHERE docket='%s';" % docket)
    query_results = cur.fetchall()

    ### use pandas to get record from db and plot it    
    df = pd.read_sql(("SELECT cutoffs_SCALIA, cutoffs_ROBERTS, cutoffs_KENNEDY, cutoffs_BREYER, cutoffs_GINSBURG, words_SCALIA, words_ROBERTS, words_KENNEDY, words_BREYER, words_GINSBURG, sentiment_SCALIA, sentiment_ROBERTS, sentiment_KENNEDY, sentiment_BREYER, sentiment_GINSBURG, amicus from cases WHERE docket='%s';" % docket), db)

  ## Plot the features and save the plot
  plot_features(df)
      
  ## Compile the text to a list of dicts to send to the html  
  items = []
  for result in query_results:
    ## Get the petitioner and respondent names from the case name
    pet_name, res_name = result[0].split(' v. ')
    ## Get the probability of winning for each side
    pet_confidence = float(result[1])
    res_confidence = 1.0 - pet_confidence 
    pet_predict, res_predict = winlose(result[2].split('.')[0])
    pet_result, res_result = winlose(result[3].split('.')[0])
    items.append({'docket':docket, 'pet_name':pet_name, 'res_name':res_name, 'pet_confidence':pet_confidence, 'res_confidence':res_confidence, 'pet_result':pet_result, 'res_result':res_result})
  #return render_template('scotus.html', items=items)
  the_result = ''
  return render_template("output.html", items=items, the_result=the_result)  
#   if items:
#     #call a function from a_Model package. note we are only pulling one result in the query
#     #pop_input = items[0]['population']
#     #the_result = ModelIt(city, pop_input)
#     pass
#   else:
#     the_result = '*** oops, case not found!'
# #  return render_template("output.html", items = items, the_result = the_result)
#   return render_template('scotus.html', items=items)