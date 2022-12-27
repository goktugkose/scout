import graph_module as gm
import helper_functions as hf

#getProjectGraph
@hf.timing
def main(user_id, project_id):
  isProjectWide = True
  gm.main(-1, project_id, isProjectWide)
  hf.insert_actions_to_db("get_project_graph", user_id, project_id)