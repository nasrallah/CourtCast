from flask import render_template, request
from app import app
import pymysql as mdb
import pandas as pd
from a_Model import ModelIt


## Right now the indicator is an integer. I'm not sure how I will store unknown case outcomes. This assumes there is nothing there.
def winlose(indicator):
    if indicator == 1:
        pet = 'won'
        res = 'lost'
    elif indicator == 0:
        pet = 'lost'
        res = 'won'
    else:
        pet = '?'
        res = '?'
    return pet, res    


## Connect to the database
db = mdb.connect(user="root", password="maddox79", host="localhost", db="scotus", charset='utf8')


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

  with db:
    cur = db.cursor()
    #just select the city from the world_innodb that the user inputs
    #cur.execute("SELECT caseName, prediction, P(Pet_win|features), winner FROM cases WHERE docket='%s';" % docket)
    cur.execute("SELECT caseName, confidence, prediction, winner, docket FROM cases WHERE docket='%s';" % docket)
    query_results = cur.fetchall()

  items = []
  for result in query_results:
    ## Get the petitioner and respondent names from the case name
    pet_name, res_name = result[0].split(' v. ')
    ## Get the probability of winning for each side
    pet_confidence = float(result[1])
    res_confidence = 1.0 - pet_confidence 
    pet_predict, res_predict = winlose(int(result[2]))
    pet_result, res_result = winlose(int(result[3]))
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