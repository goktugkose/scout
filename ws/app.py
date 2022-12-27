import os
import nltk
folder_name = "nltk_data"
path = os.path.join(os.getcwd(),folder_name)
nltk.data.path.append(path)

if folder_name not in os.listdir():
  nltk.download('stopwords',path)
  nltk.download('wordnet', path)
  nltk.download('omw-1.4', path)
  nltk.download('sentiwordnet', path)

folder_name="models"
if folder_name not in os.listdir():
  from sentence_transformers import SentenceTransformer
  model_name="paraphrase-mpnet-base-v2"
  model_path = os.path.join(os.getcwd(),folder_name, model_name)
  bert_model = SentenceTransformer(model_name)
  bert_model.save(model_path)

import time
import json
import itertools
import pandas as pd
from flask import Flask, request

from nltk.stem import WordNetLemmatizer
from nltk.corpus import sentiwordnet as swn
lemmatizer = WordNetLemmatizer()
next(swn.all_senti_synsets()) 

import graph_module as gm
import helper_functions as hf
import suggestion_module as sm
import noun_phrase_extraction_module as npm

app = Flask(__name__)

@app.route("/", methods=["GET"])
def homepage():
    return "Running!"

@hf.timing
@app.route("/unrelated_suggestions")
def unrelated_suggestions():
  user_id = request.args.get('user_id')
  project_id = request.args.get('project_id')
  #try:
  result = sm.gather_unrelated_suggestion(user_id, project_id)
  result_crud = sm.gather_crud_suggestions(user_id,project_id)
  result = result + result_crud
  hf.insert_actions_to_db("get_suggestions", user_id, project_id)
  df = pd.DataFrame.from_dict(result).drop(["type","sentence","visible"],1)
  df["storyID"] = df["storyID"].str.replace("user_story_","")
  hf.insert_suggestions_to_db(user_id, project_id, False, df)
  return json.dumps(sorted(result, key= lambda x : (int(x["type"]), int(x["storyID"].split("_")[-1]))))
  #except:
  #  print("An error occurred!")

@hf.timing
@app.route("/all_suggestions", methods=["GET"])
def all_suggestions():
  user_id = request.args.get('user_id')
  project_id = request.args.get('project_id')
  #try:
  result = sm.all_suggestion(user_id, project_id)
  df = pd.DataFrame.from_dict(result)#.drop("type",1)
  hf.insert_suggestions_to_db(user_id, project_id,True, df,-1)
  hf.insert_actions_to_db("get_all_suggestions", user_id, project_id)
  return json.dumps(result)
  #except:
  #  print("An error occurred!")

@hf.timing
@app.route("/get_project_graph", methods=["GET"])
def get_project_graph():
  user_id = request.args.get('user_id')
  project_id = request.args.get('project_id')
  isProjectWide = True
  gm.main(-1, project_id, isProjectWide, user_id)
  hf.insert_actions_to_db("get_project_graph", user_id, project_id)
  return "True"
 
@hf.timing
@app.route("/get_user_graph", methods=["GET"])
def get_user_graph():
  user_id = request.args.get('user_id')
  project_id = request.args.get('project_id')
  isProjectWide = False
  gm.main(user_id, project_id, isProjectWide, user_id)
  hf.insert_actions_to_db("get_user_graph", user_id, project_id)
  return "True"

@hf.timing
@app.route("/noun_phrase_extraction", methods=["GET"])
def noun_phrase_extraction():
  user_id = request.args.get('user_id')
  project_id = request.args.get('project_id')
  #try:
  #User Based NP's
  df = npm.extract_noun_phrases(npm.generate_sql(user_id, project_id))
  nps = list(set(itertools.chain.from_iterable(df.nounPhrases)))
  props = npm.apply_substring_operation(nps)
  hf.delete_files(user_id,project_id)
  hf.write_to_json("props_uid{user_id}_pid{project_id}_{t}".format(user_id=user_id, project_id=project_id, t = int(time.time())), props,"props")
  hf.insert_actions_to_db("extract_nps", user_id, project_id)
  
  #Project-wide NP's
  user_id = -1
  df = npm.extract_noun_phrases(npm.generate_sql(user_id, project_id))
  npm.update_story_nps(project_id, df)
  nps = list(set(itertools.chain.from_iterable(df.nounPhrases)))
  props = npm.apply_substring_operation(nps)
  hf.delete_files(-1,project_id)
  hf.write_to_json("props_uid{user_id}_pid{project_id}_{t}".format(user_id=user_id, project_id=project_id, t = int(time.time())), props,"props")

  return props
  #except:
  #  print("An error occurred!")


#if __name__ == "__main__":
#    app.run("0.0.0.0", port=80, debug=True)