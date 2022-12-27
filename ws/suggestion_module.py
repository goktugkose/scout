import time
import string
import pyodbc
import pandas as pd
import networkx as nx
import json
import helper_functions as hf
import graph_op as graph
from nltk.stem import WordNetLemmatizer
from nltk.corpus import sentiwordnet as swn
from helper_functions import get_config

lemmatizer = WordNetLemmatizer()
next(swn.all_senti_synsets()) 

@hf.timing
def configure_graph_db():
  db_name = get_config("neo4j_db")#"project-graphs" if isProjectWide else "user-graphs"
  db = graph.db(get_config("neo4j_address"),get_config("neo4j_user"), get_config("neo4j_password"), db_name,0)
  return db

@hf.timing
def generate_sql(user_id, project_id):
  conn = pyodbc.connect(f'Driver={get_config("sql_server_driver")};\
  Server={get_config("sql_server_address")};\
  Database={get_config("sql_server_db")};\
  uid={get_config("sql_server_user")};pwd={get_config("sql_server_password")};')
  with conn.cursor().execute("SELECT storyID, nounPhrases FROM Stories where isDeleted = 0 and userID = {user_id} and projectID = {project_id}".format(user_id=user_id, project_id=project_id)) as cursor:
    columns = [column[0] for column in cursor.description]
    data = cursor.fetchall()
  results = []
  for row in data:
    results.append(dict(zip(columns, row)))
  return results

#Comparison done!
@hf.timing
def gather_unrelated_suggestion(user_id, project_id):
    start_time = time.time()
    db = configure_graph_db()
    json_data = generate_sql(user_id, project_id)
    json_data_temp = [json.loads(x["nounPhrases"]) for x in json_data]    
    idxes = []
    df = pd.DataFrame(db.get_source_target_mappings(user_id,project_id, user_id))
    #sentence = "We can't find any relation about the term "
    sentence = "Isolated concept "
    for term in [x for x in db.get_self_links(user_id, project_id, user_id) if x != ""]: 
      for idx in range(len(json_data_temp)):
        #print(term, json_data_temp[idx].split(), len(set(json_data_temp[idx].split()).intersection(set(term.split()))) == len(set(term.split())))
        if term in json_data_temp[idx]:
          idxes.append({"storyID": "user_story_{id}".format(id=json_data[idx]["storyID"]),"type" : 0, "term": term, "sentence": sentence,  "suggestionGroup" : "isolated", "visible" :True}) #, "suggestionExp" : "Isolated Concepts"
    vague_terms = df[df.source != df.target]
    vague_terms = list(set(vague_terms[vague_terms.target.str.split().str.len().gt(3)].target))
    vague_terms = [x for x in vague_terms if "and" in x.split(" ") or "or" in x.split(" ")]
    #sentence = "You might want to consider rewriting this term "
    sentence = "Quality issue (e.g. lack of atomicity)"
    db.close()
    for term in vague_terms: 
      for idx in range(len(json_data_temp)):
        if term in json_data_temp[idx]:
          idxes.append({"storyID": "user_story_{id}".format(id=json_data[idx]["storyID"]),"type" : 1, "term": term, "sentence": sentence, "suggestionGroup" : "atomic", "visible" :True}) # , "suggestionExp" : "Non-Atomic User Stories"
    return idxes
    #print("---Func:{name} -- {sec} seconds ---".format(name = "gather_unrelated_suggestion", sec=(time.time() - start_time)))

#Comparison done!
@hf.timing
def graph_relevance(user_id, project_id, operating_user_id, graph, n, cutoff):
  top_n_dict = configure_graph_db().get_user_story_count(user_id, project_id, operating_user_id, n)
  top_n_words = list(top_n_dict.keys())
  related_terms = {}
  for w in top_n_words:
      related_terms.setdefault(w,sorted([n for n in (nx.single_source_shortest_path_length(graph, w, cutoff=cutoff).keys()) if not ("and" in n.split(" ") or "or" in n.split(" ")) and n!=w])) #len(n.split()) < 3 and
  print(user_id, project_id, related_terms, top_n_words)
  return related_terms

#Comparison done!
@hf.timing
def assess_relavance(rel_usr, rel_proj, G_proj):
  top_words_difference = list(set(rel_proj.keys()).difference(set(rel_usr.keys())))
  top_words_intersection = list(set(rel_proj.keys()).intersection(set(rel_usr.keys())))
  usr_top_words_difference = list(set(rel_usr.keys()).difference(set(rel_proj.keys())))
  relavent_node_difference = {}
  relavent_node_extra = {}
  phrase = []
  if len(top_words_difference) == 0:
    for k in rel_usr.keys():
      relavent_node_difference.setdefault(k,list(set(rel_proj[k]).difference(rel_usr[k])))
    if any(len(x) > 0 for x in relavent_node_difference.values()):
      phrase.append({"term": relavent_node_difference, "suggestionGroup" : "incomplete"}) if len(relavent_node_difference) > 0 else None
    else:
      phrase.append({"term":[""],"suggestionGroup":"complete"})
  else:
    phrase.append({"term": top_words_difference, "suggestionGroup" :"pop-zero"}) if len(top_words_difference) > 0 else None
    #phrase.append({"storyID" : "user_story_-1","term": usr_top_words_difference, "sentence" : "Benim popülerlerim ", "type" : 2})
    for k in top_words_intersection:
      relavent_node_difference.setdefault(k,list(set(rel_proj[k]).difference(rel_usr[k])))
    phrase.append({"term": relavent_node_difference, "suggestionGroup" : "pop-one"}) if any(a != [] for a in relavent_node_difference.values()) else None
    for k in top_words_intersection:
      relavent_node_extra.setdefault(k,list(set(rel_usr[k]).difference(rel_proj[k])))    
    phrase.append({"term": relavent_node_extra, "suggestionGroup" : "pop-two"}) if any(a != [] for a in relavent_node_extra.values()) else None
    different_nodes_from_usr = {}
    for k in usr_top_words_difference:
      try:
        lst_ = list(nx.single_source_shortest_path_length(G_proj, k, cutoff=2).keys())
        lst_.remove(k)
        lst_ = list(set(lst_) - set(rel_usr[k]))
        different_nodes_from_usr[k] = lst_
      except:
        pass      
    phrase.append({"term": different_nodes_from_usr, "suggestionGroup" : "pop-three"}) if any(a != [] for a in different_nodes_from_usr.values()) else None
  return phrase

@hf.timing
def generate_crud_sql(user_id, project_id):
  conn = pyodbc.connect(f'Driver={get_config("sql_server_driver")};\
  Server={get_config("sql_server_address")};\
  Database={get_config("sql_server_db")};\
  uid={get_config("sql_server_user")};pwd={get_config("sql_server_password")};')
  query = "SELECT storyID, verbPhrases FROM Stories where isDeleted = 0 and userID = {user_id} and projectID = {project_id} and verbPhrases <> '{{}}'".format(user_id=user_id, project_id=project_id) \
    if user_id != -1 else "SELECT storyID, verbPhrases FROM Stories where isDeleted = 0 and projectID = {project_id} and verbPhrases <> '{{}}'".format(project_id=project_id)
  try:
    with conn.cursor().execute(query) as cursor:
      columns = [column[0] for column in cursor.description]
      data = cursor.fetchall()
    results = []
    for row in data:
      results.append(dict(zip(columns, row)))
    return results
  except:
    print("Error from query: ",query)

def gather_crud_suggestions(user_id, project_id):
  available_ops = {"C" : "create","R": "read","U" : "update","D" : "delete"}
  results = generate_crud_sql(user_id,project_id)
  idxes = []
  for d in results:
    id = d["storyID"]
    vps = json.loads(d["verbPhrases"])
    for k,v in vps.items():
      term = k
      tmp = list(set(available_ops.keys()) - set(v["op"]))
      #for op in tmp:
      #  op_str = ""
      #  if len(v["op"]) == 1:
      #    op_str = available_ops[v["op"][0]]
      #  elif len(v["op"]) == 2:
      #    op_str = " and".join(v["op"])
      #  else:
      #    op_str = " ,".join(v["op"])
      #sentence = "You mentioned {op} event about the term \"{term}\". You might also want to mention about {op_p} event of this term".format(op=json.dumps(v["op"]),term=term,op_p=json.dumps(tmp))
      lst = [d["term"] for d in idxes]
      if term not in lst:
        sentence = "[{op},{op_p}]".format(op=json.dumps(v["op"]),term=term,op_p=json.dumps(tmp))
        idxes.append({"storyID": "user_story_{id}".format(id=id), "term": term,"type" : 2, "sentence": sentence, "suggestionGroup" : "crud", "visible" : True})    
      else:
        ix = idxes.index([x for x in idxes if x["term"] == term][0])
        d = json.loads(idxes[ix]["sentence"])
        if v["op"][0] not in d[0]:
          d[0].append(v["op"][0])
          d[1].remove(v["op"][0])
        idxes[ix]["sentence"] = json.dumps(d)
        idxes.append({"storyID": "user_story_{id}".format(id=id), "term": term, "type" : 2, "sentence": idxes[ix]["sentence"], "suggestionGroup" : "crud", "visible" : False})     # "suggestionExp" : "CRUD Operation Issues",
  return idxes

#Comparison done!
@hf.timing
def all_suggestion(user_id, project_id):
  n = 5
  cutoff = 2
  db = configure_graph_db()

  df_proj  = pd.DataFrame(db.get_source_target_mappings(-1, project_id, user_id)).sort_values(by=['source', 'target'])#pd.read_csv("./temp_graph_files/suggestion_project.csv",index_col=0)
  df_user = pd.DataFrame(db.get_source_target_mappings(user_id, project_id, user_id)).sort_values(by=['source', 'target'])#pd.read_csv("./temp_graph_files/suggestion.csv", index_col=0)

  G_user = nx.from_pandas_edgelist(df_user,source="source", target = "target")
  G_proj = nx.from_pandas_edgelist(df_proj,source="source", target = "target")  
  
  rel_usr = graph_relevance(user_id, project_id, user_id, G_user, n, cutoff)
  rel_proj = graph_relevance(-1, project_id, user_id, G_proj, n, cutoff)
  
  #phrase, relavent_node_difference = assess_relavance(rel_usr, rel_proj)
  phrase = assess_relavance(rel_usr, rel_proj, G_proj)

  lst_ = list(set(db.get_self_links(-1,project_id, user_id)).difference(set(db.get_self_links(user_id,project_id,user_id))))
  if len(lst_) > 0:
    phrase.append({"term": lst_, "suggestionGroup" : "lucky"})

  """for k,v in relavent_node_difference.items():
    if len(v) > 0:
      for el in v:
        phrase.append(str(k+" --> "+el))"""
  
  return phrase

@hf.timing
def unrelated_suggestions(user_id, project_id):
  #try:
  result = gather_unrelated_suggestion(user_id, project_id)
  result_crud = gather_crud_suggestions(user_id,project_id)
  result = result + result_crud
  hf.insert_actions_to_db("get_suggestions", user_id, project_id)
  df = pd.DataFrame.from_dict(result).drop(["type","sentence","visible"],1)
  df["storyID"] = df["storyID"].str.replace("user_story_","")
  df.to_csv("result_2.csv", index=False)
  hf.insert_suggestions_to_db(user_id, project_id, False, df)
  return json.dumps(sorted(result, key= lambda x : (int(x["type"]), int(x["storyID"].split("_")[-1]))))
  #except:
  #  print("An error occurred!")

@hf.timing
def all_suggestions(user_id, project_id):
  #try:
  result = all_suggestion(user_id, project_id)
  df = pd.DataFrame.from_dict(result)#.drop("type",1)
  df.to_csv("result.csv", index=False)
  hf.insert_suggestions_to_db(user_id, project_id,True, df,-1)
  hf.insert_actions_to_db("get_all_suggestions", user_id, project_id)
  return json.dumps(result)
  #except:
  #  print("An error occurred!")