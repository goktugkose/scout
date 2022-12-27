import graph_module as gm
import helper_functions as hf

#getUserGraph
def main(user_id, project_id):
  isProjectWide = False
  gm.main(user_id, project_id, isProjectWide)
  hf.insert_actions_to_db("get_user_graph", user_id, project_id)