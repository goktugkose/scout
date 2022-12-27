import time
import json
import os
import pyodbc
import itertools
from datetime import datetime

def write_to_json(filename, obj, folder="temp_files"):
  with open('./{folder}/{filename}.json'.format(filename=filename, folder=folder), 'w') as f:
    json.dump(obj, f)

def read_from_json(filename, folder="temp_files"):
  with open('./{folder}/{filename}.json'.format(filename=filename, folder=folder), 'r') as f:
    return json.load(f)

def delete_file(filename, folder="temp_files"):
  os.remove("./{folder}/{filename}".format(filename=filename, folder=folder))

def delete_files(user_id, project_id, folder="props"):
  for file in [x for x in os.listdir(folder) if "uid{user_id}_pid{project_id}".format(user_id=user_id,project_id=project_id) in x]:
    os.remove("./{folder}/{file}".format(folder=folder, file=file))

def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        print('The function {:s} took {:.3f} s'.format(f.__name__, (time2-time1)))
        return ret
    return wrap

def get_config(key):
  with open('config.json','r') as f:
    data = json.load(f)
  return data[key]

def insert_actions_to_db(type, user_id, project_id):
  conn = pyodbc.connect(f'Driver={get_config("sql_server_driver")};\
  Server={get_config("sql_server_address")};\
  Database={get_config("sql_server_db")};\
  uid={get_config("sql_server_user")};pwd={get_config("sql_server_password")};')
  query = "INSERT INTO Actions ([type],[actionTime],[userID],[projectID]) VALUES({type},{action_time},{user_id},{project_id})".format(
    type = "'"+type+"'", action_time = "'"+datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]+"'", user_id = user_id, project_id = project_id)
  try:
    conn.cursor().execute(query)
  except:
    print("Error from query: ",query)
  conn.commit()

def insert_suggestions_to_db(user_id, project_id,isProjectWide,df,story_id=0):
  conn = pyodbc.connect(f'Driver={get_config("sql_server_driver")};\
  Server={get_config("sql_server_address")};\
  Database={get_config("sql_server_db")};\
  uid={get_config("sql_server_user")};pwd={get_config("sql_server_password")};')

  dt_string = "'"+datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]+"'"

  if story_id == 0:
    query = "INSERT INTO Suggestions ([userID],[projectID],[storyID],[term],[suggestionGroup],[saveDate],[isProjectWide]) VALUES({user_id},{project_id},?,?,?,{dt},{isProjectWide})"\
    .format(user_id=user_id, project_id=project_id,dt=dt_string,isProjectWide=int(isProjectWide))
  else:
    query = "INSERT INTO Suggestions ([userID],[projectID],[storyID],[mainTerm],[term],[suggestionGroup],[saveDate],[isProjectWide]) VALUES({user_id},{project_id},{story_id},?,?,?,{dt},{isProjectWide})"\
    .format(user_id=user_id, project_id=project_id,dt=dt_string,isProjectWide=int(isProjectWide),story_id=story_id)   

  #try:
  cursor=conn.cursor()
  #cursor.fast_executemany = True
  print(df.columns)
  if story_id == -1:
    df["term"] = df.term.apply(lambda x: list(itertools.chain(*[list(map(lambda p: (k,p),v)) for (k,v) in x.items()])) if type(x) == type({}) else x)
    df = df.explode('term')
    #df.to_csv("asdasd.csv",index=False)
    df["mainTerm"] = df.term.apply(lambda x : x[0] if type(x) != type("") and type(x) != type(None) else None)
    df.term= df.term.apply(lambda x : x[1] if type(x) != type("") else x)
    df = df[["mainTerm","term","suggestionGroup"]]
  cursor.executemany(query,df.values.tolist())   
  #except:
  #  print("Error from query: ",query)
  conn.commit()
  cursor.close()
  conn.close()