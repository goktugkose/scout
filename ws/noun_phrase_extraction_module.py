import time
import textacy
import pyodbc
import pandas as pd
import json
import itertools
import helper_functions as hf
import en_core_web_md
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.corpus import sentiwordnet as swn
from helper_functions import get_config

nlp = en_core_web_md.load()
lemmatizer = WordNetLemmatizer()
stop_words_l=stopwords.words('english')

#Allow multi-threaded NLTK
next(swn.all_senti_synsets()) 

def unify_nps(phrases_a, phrases_b):
    """
      Drop duplicate noun chunks generated by combining textacy and spacy outputs.
    """
    to_del = set()
    for el in phrases_a:
        for el2 in phrases_b:
            if el in el2 and el != el2:
                to_del.add(el)
    val = phrases_a - to_del
    return set([x for x in val if x not in stop_words_l])

def create_np_list(phrases_a, phrases_c):
    """
      Applies lemmatization to clean list of noun chunks and distinguish noun phrases starts with stop words.
    """
    a = unify_nps(phrases_c, phrases_c)
    lst = a.union(unify_nps(phrases_a, a))

    tmp = []
    for el in lst:
        x = el.split()[0]
        if x in stop_words_l:
            new = " ".join(el.split()[1:])
            tmp.append(new) if len(new.split()) > 1 else tmp.append(lemmatizer.lemmatize(new))        
        else:
            tmp.append(el) if len(el.split()) > 1 else tmp.append(lemmatizer.lemmatize(el))
    return tmp

def return_verbs(sentence):
    """
      Benefits from textacy to extract verbs from sentences using pattern matching.
      For more information about pattern matching @ 
      https://textacy.readthedocs.io/en/0.12.0/api_reference/extract.html#textacy.extract.matches.token_matches
    """
    pattern = r"POS:VERB:+"
    doc = textacy.make_spacy_doc(sentence, lang='en_core_web_md')
    lists = textacy.extract.token_matches(doc, pattern)
    verbs =  []
    for list in lists:
        verbs.append(list.text)
    return verbs

def extract_crud_ops(phrases, nc, doc, verbs,crud_verbs):
    """
      Benefits from spacy dependency tree to extract verb phrases.
      For more information about dependency tree @ 
      https://spacy.io/usage/linguistic-features#navigating-around
    """
    try:
        v = doc[nc.root.left_edge.i-1].text
        if v in verbs and v in list(itertools.chain(*crud_verbs.values())):
            np = doc[nc.root.left_edge.i:nc.root.right_edge.i+1].text
            tmp = []
            for el in [np]:
                x = el.split()[0]
                if x in stop_words_l:
                    new = " ".join(el.split()[1:])
                    tmp.append(new) if len(new.split()) > 1 else tmp.append(lemmatizer.lemmatize(new))        
                else:
                    tmp.append(el) if len(el.split()) > 1 else tmp.append(lemmatizer.lemmatize(el))
            np = tmp[0]
            try:
              np = " ".join([lemmatizer.lemmatize(w) for w in np.split() if wn.synsets(w)[0].pos() != 'v'])
            except:
              np = " ".join([lemmatizer.lemmatize(w) for w in np.split()])
            if len(np) > 0:
              phrases.setdefault(np,{"op" : [], "verbs" : []})
              tmp = phrases[np]["op"]
              tmp.append([x[0] for x in crud_verbs.items() if v in x[1]][0])
              phrases[np]["op"] = list(set(tmp))
              phrases[np]["verbs"].append(v)
    except:
        pass
    return phrases

def extract_nps(sentence):
    """
      Prevents excluding some noun chunks unintentionally by combining textacy and spacy outputs.
      Generates noun phrases and verb phrases for a given user story set.
    """
    phrases_a = set()
    phrases_b = set()
    phrases_c = set()
    doc = nlp(sentence.lower())
    verbs = return_verbs(sentence)
    crud_verbs = hf.read_from_json("crud_verbs", "files")
    phrases = {}
    for nc in doc.noun_chunks:
        phrases_a.add(nc.text)
        phrases_b.add(doc[nc.root.left_edge.i:nc.root.right_edge.i+1].text)
        phrases_c = phrases_b - phrases_a
        phrases = extract_crud_ops(phrases, nc, doc, verbs, crud_verbs)
    return phrases_a, phrases_c, phrases

@hf.timing
def extract_noun_chunks(concepts):
  """
    Tries to eliminate verbs from noun chunks using Wordnet synsets.
    Generates noun and verb phrase lists.
  """
  nps = []
  vps = []
  for element in concepts:
    spacy_lst = []
    element = " ".join([w.lower() for w in element.split()])
    #doc = nlp(element)
    phrases_a, phrases_c, p = extract_nps(element)
    noun_chunks = create_np_list(phrases_a, phrases_c)
    if len(list(noun_chunks)) > 0 :
        for chunk in noun_chunks:
            try:
              spacy_lst.append(" ".join([lemmatizer.lemmatize(w) for w in chunk.split() if wn.synsets(w)[0].pos() != 'v']))
            except:
              spacy_lst.append(" ".join([lemmatizer.lemmatize(w) for w in chunk.split()]))
    else:
        spacy_lst.append(element)
    nps.append(spacy_lst)
    vps.append(p)
  return nps, vps

@hf.timing
def extract_noun_phrases(user_stories):
  """
    Applies case-folding then other pre-processing steps to user story column of dataframe.
  """
  df = pd.DataFrame(user_stories)
  df["userStoryModified"] = df["userStory"].apply(lambda x: " ".join(w.lower() for w in x.split()))  # if len(w) > 1.translate(str.maketrans(string.punctuation.replace("|",""), " "*len(string.punctuation.replace("|","")))) and w not in stop_words_l
  df["userStoryModified"] = df["userStoryModified"].apply(lambda x : str(x.lstrip()))
  result = extract_noun_chunks(df["userStoryModified"])
  df["nounPhrases"] = result[0]
  df["verbPhrases"] = result[1]
  return df

def len_func(e):
  """
    Created for clean coding.
  """
  return len(e.split())
@hf.timing
def substr_op(concepts):
  """
      Benefits from set operations to merge noun phrases with matching substrings.
      Reduces the complexity of further steps.
  """
  lst_substr = []
  dict_related = {}
  lst_extr = []
  concepts.sort(key=len_func, reverse=False)
  for idx in range(len(concepts)):
    element = concepts[idx]
    for idy in range(len(concepts)):  
      element_2 = concepts[idy]
      if idx != idy:
        if len(element.split()) > 1:
          if len(set(element.split()).intersection(set(element_2.split()))) > 1:
            if element not in lst_substr:
                lst_substr.append(element_2)
                dict_related.setdefault(element,[]).append(element_2)
        else:
          if len(set(element.split()).intersection(set(element_2.split()))) > 0:
            dict_related.setdefault(element,[]).append(element_2)
            lst_extr.append(element_2)
  for i in lst_extr:
    lst_substr.append(i)
  for k in dict_related.keys():
    lst_substr.remove(k) if k in lst_substr else 1
  return list(set(concepts) - set(lst_substr)), dict_related 

@hf.timing
def apply_substring_operation(new_concept_chunks):
  """
    Apply substring operation.
    Construct a dictionary of clean and merged noun phrases.
  """
  result = substr_op(new_concept_chunks)
  new_concept_chunks = result[0]

  new_misaligned_concepts = list((set(new_concept_chunks)).union(set(result[1].keys()))) 
  candidate_concepts = list(set(new_misaligned_concepts))
  
  props = {}
  covered_concepts = []
  different_concepts = []
  for c in candidate_concepts:
    if c in list(result[1].keys()):
      if len(set(result[1].get(c))) != 0 :
        props.setdefault(c,[]).extend(list(set(result[1].get(c))))
      covered_concepts.append(c)
    else:
      different_concepts.append(c)
      props.setdefault(c,[]).extend(list(set(result[1].get(c,[]))))
  b4 = different_concepts
  different_concepts, dict_props = substr_op(different_concepts)
  after = different_concepts
  for k,v in dict_props.items():
    tmp = list(set(props.get(k,[])+ v))
    props[k] = tmp
  for k in list(set(b4)-set(after)):
    props.pop(k)
  for k,v in props.items():
    props[k] = sorted(v)
  return props

@hf.timing
def generate_sql(user_id, project_id):
  """
    Retrieve user stories from SQL Server DB.
  """
  conn = pyodbc.connect(f'Driver={get_config("sql_server_driver")};\
  Server={get_config("sql_server_address")};\
  Database={get_config("sql_server_db")};\
  uid={get_config("sql_server_user")};pwd={get_config("sql_server_password")};')
  query = "SELECT storyID, userID, projectID, userStory FROM Stories where isDeleted = 0 and userID = {user_id} and projectID = {project_id}".format(user_id=user_id, project_id=project_id) \
    if user_id != -1 else "SELECT storyID, userID, projectID, userStory FROM Stories where isDeleted = 0 and projectID = {project_id}".format(project_id=project_id)
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

@hf.timing
def update_story_nps(project_id, df):
  """
    Updates SQL Server DB with extracted noun phrases for each user story.
  """
  conn = pyodbc.connect(f'Driver={get_config("sql_server_driver")};\
  Server={get_config("sql_server_address")};\
  Database={get_config("sql_server_db")};\
  uid={get_config("sql_server_user")};pwd={get_config("sql_server_password")};')
  
  for id, np, vp in df[["storyID", "nounPhrases", "verbPhrases"]].values:
    query = "UPDATE Stories SET nounPhrases = '{np}', verbPhrases = '{vp}' where storyID = {story_id} and projectID = {project_id}".format(
      story_id = id, np = json.dumps(list(map(lambda x : x.replace("'","''"), np))), project_id = project_id, vp = json.dumps(vp).replace("'","''"))
    conn.cursor().execute(query)

  conn.commit()

@hf.timing
def main(user_id, project_id):
  """
      Executes noun phrase extraction pipeline.
      Stores extracted dictionaries in the disk.
  """
  #User Based NP's
  df = extract_noun_phrases(generate_sql(user_id, project_id))
  nps = list(set(itertools.chain.from_iterable(df.nounPhrases)))
  props = apply_substring_operation(nps)
  #hf.delete_files(user_id,project_id)
  hf.write_to_json("props_uid{user_id}_pid{project_id}_{t}".format(user_id=user_id, project_id=project_id, t = int(time.time())), props,"props")
  hf.insert_actions_to_db("extract_nps", user_id, project_id)
  
  #Project-wide NP's
  user_id = -1
  df = extract_noun_phrases(generate_sql(user_id, project_id))
  update_story_nps(project_id, df)
  nps = list(set(itertools.chain.from_iterable(df.nounPhrases)))
  props = apply_substring_operation(nps)
  #hf.delete_files(-1,project_id)
  hf.write_to_json("props_uid{user_id}_pid{project_id}_{t}".format(user_id=user_id, project_id=project_id, t = int(time.time())), props,"props")

  return props