from neo4j import GraphDatabase
import threading
from datetime import datetime

class Node():
    def __init__(self, key, user_id, project_id, user_story, is_active, expiry_date, operating_user_id):
        self.key = key
        self.user_id = user_id
        self.project_id = project_id
        self.user_story = user_story
        self.is_active = is_active
        self.expiry_date = expiry_date
        self.operating_user_id = operating_user_id

    def to_dict(self):
        output = {
            "key": self.key, 
            "user_id": self.user_id,
            "project_id": self.project_id, 
            "user_story": self.user_story, 
            "is_active": self.is_active,
            "expiry_date": self.expiry_date,
            "operating_user_id": self.operating_user_id
        }
        return output

class db():
    def __init__(self, uri, user, password, db, user_id):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.db = db
        self.loggedUserId = user_id
        self.lock = threading.RLock()

    def close(self):
        self.driver.close()
                
    @staticmethod    
    def _add_nodes(tx, nodes):
        for source,target in nodes:
            result = tx.run(
                "MERGE (source:Node {key: $key_s, user_id: $user_id_s, project_id: $project_id_s, is_active: $is_active_s, expiry_date: $expiry_date_s, operating_user_id: $operating_user_id_s}) " 
                "ON MATCH SET source.user_story = source.user_story + [el in $user_story_s WHERE NOT el IN source.user_story] ON CREATE SET source.user_story = $user_story_s "
                "MERGE (target:Node {key: $key_t, user_id: $user_id_t, project_id: $project_id_t, is_active: $is_active_t, expiry_date: $expiry_date_t, operating_user_id: $operating_user_id_t}) "
                "ON MATCH SET target.user_story = target.user_story + [el in $user_story_t WHERE NOT el IN target.user_story] ON CREATE SET target.user_story = $user_story_t "
                "MERGE (source)-[r:RELATED_TO]->(target)",
                key_s =source.key, user_id_s = source.user_id, user_story_s = source.user_story, project_id_s = source.project_id, is_active_s = source.is_active, expiry_date_s = source.expiry_date, operating_user_id_s = source.operating_user_id,
                key_t =target.key, user_id_t = target.user_id, user_story_t = target.user_story, project_id_t = target.project_id, is_active_t = target.is_active, expiry_date_t = target.expiry_date, operating_user_id_t = target.operating_user_id )
        return result 

    @staticmethod
    def _get_self_links(tx, user_id, project_id, operating_user_id):
        list = []
        for record in tx.run("MATCH (n:Node)-[r:RELATED_TO]->(n) where n.is_active=true and n.user_id = $user_id and n.project_id = $project_id and n.operating_user_id = $operating_user_id RETURN n.key",
        user_id = int(user_id), project_id = int(project_id), operating_user_id = int(operating_user_id)):
            list.append(record["n.key"])
        return list

    @staticmethod
    def _get_source_target_mappings(tx, user_id, project_id, operating_user_id):
        list = []
        for record in tx.run("MATCH (source:Node)-[r:RELATED_TO]->(target:Node) WHERE "
        "source.project_id = $project_id and target.project_id = $project_id and source.user_id = $user_id and target.user_id = $user_id and "
        "source.is_active = true and target.is_active = true and "
        "source.operating_user_id = $operating_user_id and target.operating_user_id = $operating_user_id "
        "RETURN {source:source.key, target:target.key} AS links", project_id=int(project_id), user_id=int(user_id), operating_user_id=int(operating_user_id)):
            list.append(record["links"])
        return list

    @staticmethod
    def _delete_source_target_mappings(tx, user_id, project_id, operating_user_id):
        #result = tx.run("MATCH (n:Node) WHERE n.project_id = $project_id and n.user_id = $user_id "
        #"DETACH DELETE n", project_id=int(project_id), user_id=int(user_id))
        result = tx.run("MATCH (n:Node) WHERE n.project_id = $project_id and n.user_id = $user_id "
        "and n.is_active = true and n.operating_user_id = $operating_user_id "
        "SET n.is_active = false, n.expiry_date = $expiry_date",project_id=int(project_id),operating_user_id=int(operating_user_id), user_id=int(user_id),
        expiry_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return result

    @staticmethod
    def _get_user_story_count(tx, user_id, project_id, operating_user_id, limit):
        dict = {}
        for record in tx.run("MATCH (n:Node) WHERE n.project_id = $project_id and n.user_id = $user_id "
        "and n.is_active = true and n.operating_user_id = $operating_user_id "
        "return n.key as key, size(n.user_story) as cnt order by cnt desc, n.key asc limit $limit", project_id=int(project_id), user_id=int(user_id), operating_user_id=int(operating_user_id), limit=limit):
            dict[record["key"]] = record["cnt"]
        return dict

    def get_user_story_count(self, user_id, project_id, operating_user_id, limit):
        with self.driver.session(database=self.db) as session:
            result = session.read_transaction(self._get_user_story_count, user_id, project_id, operating_user_id, limit)
        return result

    def delete_source_target_mappings(self, user_id, project_id, operating_user_id):
        with self.driver.session(database=self.db) as session:
            result = session.write_transaction(self._delete_source_target_mappings, user_id, project_id, operating_user_id)
        return result

    def get_source_target_mappings(self, user_id, project_id, operating_user_id):
        with self.driver.session(database=self.db) as session:
            result = session.read_transaction(self._get_source_target_mappings, user_id, project_id, operating_user_id)
        return result
    
    def get_self_links(self, user_id, project_id, operating_user_id):
        with self.driver.session(database=self.db) as session:
            result = session.read_transaction(self._get_self_links, user_id, project_id, operating_user_id)
        return result

    def add_nodes(self, nodes):
        with self.driver.session(database=self.db) as session:
            result = session.write_transaction(self._add_nodes, nodes)
        return result

    def insert_op(self, df, user_id, project_id, operating_user_id):
        nodes = []
        self.delete_source_target_mappings(user_id,project_id,operating_user_id)
        for source,target,appearence_source,appearence_target in df[["source", "target", "appearence_source", "appearence_target"]].values:
            #self.add_nodes(Node(source,int(user_id),int(project_id),appearence_source,int(1),int(1),int(operating_user_id)), Node(target,int(user_id),int(project_id),appearence_target,int(1),int(1),int(operating_user_id)))
            nodes.append((Node(source,int(user_id),int(project_id),appearence_source,True,"9999-12-31 23:59:59",int(operating_user_id)), Node(target,int(user_id),int(project_id),appearence_target,True,"9999-12-31 23:59:59",int(operating_user_id))))
        print("Nodes created!")
        self.add_nodes(nodes)