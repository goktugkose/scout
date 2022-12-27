import time
import pyodbc
import pandas as pd
import os
import helper_functions as hf
import graph_op as graph
from urllib import response
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
from helper_functions import get_config
import torch
import gc

torch.set_num_threads(4)
bert_model = SentenceTransformer("./models/paraphrase-mpnet-base-v2", device="cpu")
kw_model = KeyBERT(bert_model) 
print("models loaded")


#Comparison done!
@hf.timing
def sentence_embedding_heuristic(props):
  start_time = time.time()
  document_embeddings = bert_model.encode(list(props.keys()), device="cpu")
  pairwise_similarities=cosine_similarity(document_embeddings)
  props_new = {}
  threshold= 0.4

  print("---Func:{name} -- {sec} seconds ---".format(name = "sentence_embedding_heuristic_1", sec=(time.time() - start_time)))
  start_time = time.time()

  for word in props.keys(): 
    idx = list(props.keys()).index(word)
    sim = -1
    cls = ""
    for i in range(pairwise_similarities.shape[1]):
      if i != idx:
        if sim < pairwise_similarities[idx,i] and pairwise_similarities[idx,i] > threshold:
          sim = pairwise_similarities[idx,i]
          cls = list(props.keys())[i]

    if len(word.split()) >1 and len(cls.split())>1:
      doc = " ".join([word,cls])
      keywords = kw_model.extract_keywords(doc,keyphrase_ngram_range=(1,1))
      if len(keywords) > 0:
        cls = keywords[0][0]

    if word in props_new.keys() and cls in props_new.values():  
      props_new.setdefault(word,[]).append(cls)
    elif cls =="":
      props_new.setdefault(word,[]) 
    else:
      props_new.setdefault(cls,[]).append(word) 
  print("---Func:{name} -- {sec} seconds ---".format(name = "sentence_embedding_heuristic_2", sec=(time.time() - start_time)))
  gc.collect()
  return props_new  

#Comparison done!
@hf.timing
def create_knowledge_graph(data):
  df = data
  df['check_string'] = df.apply(lambda row: ' '.join(sorted([row['source'], row['target']], key=lambda x: len(x))), axis=1)
  df = df.sort_values(by=["source"], key=lambda x: x.str.len())
  df = df.drop_duplicates('check_string',keep="first")
  df = df.drop("check_string", axis=1)   
  return df

#Comparison done!
@hf.timing
def create_result(props, props_new,flag=False):
  result_dict = {}
  for d in [props,props_new]:
    for k, v in d.items():
      result_dict.setdefault(k, []).extend(x for x in v if x not in result_dict[k])
  if flag:
    for k in list(result_dict.keys()):
      if k in [item for sublist in result_dict.values() for item in sublist] and len(result_dict[k]) == 0:
        del result_dict[k]
  return result_dict

@hf.timing
def generate_sql(user_id, project_id):
  conn = pyodbc.connect(f'Driver={get_config("sql_server_driver")};\
  Server={get_config("sql_server_address")};\
  Database={get_config("sql_server_db")};\
  uid={get_config("sql_server_user")};pwd={get_config("sql_server_password")};')
  query = "SELECT storyID, nounPhrases FROM Stories where isDeleted = 0 and userID = {user_id} and projectID = {project_id}".format(user_id=user_id, project_id=project_id) if user_id != -1 \
    else "SELECT storyID, nounPhrases FROM Stories where isDeleted = 0 and projectID = {project_id}".format(project_id=project_id)
  with conn.cursor().execute(query) as cursor:
    columns = [column[0] for column in cursor.description]
    data = cursor.fetchall()
  results = []
  for row in data:
    results.append(dict(zip(columns, row)))
  return results

#Comparsion done!
@hf.timing
def get_graph(props, user_id, project_id, isProjectWide, operatingUserId):
    props_new = sentence_embedding_heuristic(props)
    gls = create_result(props, props_new)
    gls_2 = sentence_embedding_heuristic(gls)
    gls_3 = create_result(gls, gls_2,True)
    d = []
    elements =  [gls_3.items()]
    for i in range(len(elements)):
      for k,v in elements[i]:
        if len(v) > 0:
          for el in v:
            d.append({"source": k, "target" : el})
        else:
            d.append({"source": k, "target" : k})
    df = pd.DataFrame(d)
    df = create_knowledge_graph(df)
    results = generate_sql(user_id, project_id)
    df_results = pd.DataFrame(results)
   
    df["appearence_source"] = df["source"].apply(lambda a : [x[1] for x in 
    filter(lambda x : x[0] == True,list(map(lambda x : (a in x[1], x[0]),
    df_results.values)))])

    df["appearence_target"] = df["target"].apply(lambda a : [x[1] for x in 
    filter(lambda x : x[0] == True,list(map(lambda x : (a in x[1], x[0]),
    df_results.values)))])

    add_to_graph_db(df,user_id,project_id,isProjectWide,operatingUserId)
    return response,df

@hf.timing
def add_to_graph_db(df, user_id, project_id, isProjectWide, operatingUserId):
  global db
  db_name = get_config("neo4j_db")#"project-graphs" if isProjectWide else "user-graphs"
  try:
    if db.loggedUserId == user_id and db.db == db_name:
      print(db.db, db.loggedUserId)
    else:
      print("Not matched! Creating connection to db:",db_name,"for user: ",user_id)
  except:
    db = graph.db(get_config("neo4j_address"), get_config("neo4j_user"), get_config("neo4j_password"),db_name, user_id)  
    print("Not available! Creating connection to db:",db_name,"for user: ",user_id)
  db.insert_op(df,user_id, project_id,operatingUserId)

@hf.timing
def main(user_id, project_id,isProjectWide, operatingUserId):
  print("--INIT--")
  start_time = time.time()
  #try:
  try:
    filtered_files = list(filter(lambda x : "uid{user_id}_pid{project_id}".format(user_id=user_id,project_id=project_id) in x, os.listdir("props")))
    sorted_files = sorted(filtered_files, reverse=True, key=(lambda x : "uid{user_id}pid{project_id}".format(user_id=user_id,project_id=project_id) in x))
    file = sorted_files[0]
  except:
    print("File does not exist.")
  props = hf.read_from_json(file.split(".")[0],"props")
  #hf.delete_file(file,"props")
  print("---Func:{name} -- {sec} seconds ---".format(name = "getprops", sec=(time.time() - start_time)))
  get_graph(props, user_id, project_id, isProjectWide, operatingUserId)
  return props
  #except:
  #  print("An error occurred!")

#if __name__ == "__main__":
#  bert_model = SentenceTransformer('paraphrase-mpnet-base-v2')
#  bert_model.save("./models/paraphrase-mpnet-base-v2")