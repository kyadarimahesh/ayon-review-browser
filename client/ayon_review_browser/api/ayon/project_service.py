from typing import Optional, List, Dict, Any
from .base_client import BaseAyonClient


class ProjectService(BaseAyonClient):
    def get_projects(self) -> List[Dict[str, Any]]:
        if self.ayon_connection is None:
            print(f"Connection error: {self.connection_error}")
            return []
        try:
            return [project['name'] for project in list(self.ayon_connection.get_projects())]
        except Exception as e:
            print(f"Error getting projects: {e}")
            return []

    def get_lists(self, project_name: str, entity_type: Optional[str] = "version") -> Dict[str, str]:
        if self.ayon_connection is None:
            print(f"Connection error: {self.connection_error}")
            return {}

        query = """ 
           query ($project: String!) {
               project(name: $project) {
                   entityLists {
                       edges { 
                           node { 
                               id 
                               active
                               label 
                               entityType
                           } 
                       }
                   }
               }
           }"""

        try:
            result = self.graphql_query(query, {"project": project_name})
            lists = {
                node["node"]["label"]: node["node"]["id"]
                for node in result["data"]["project"]["entityLists"]["edges"]
                if entity_type is None or node["node"]["entityType"] == entity_type
            }
            return lists
        except Exception as e:
            print(f"Failed to fetch lists for '{project_name}': {e}")
            return {}

    def get_list_items(self, project_name: str, list_id: str) -> List[Dict[str, Any]]:
        if self.ayon_connection is None:
            print(f"Connection error: {self.connection_error}")
            return []
        try:
            response = self.ayon_connection.get(f"/projects/{project_name}/lists/{list_id}/entities")
            return response.data
        except Exception as e:
            print(f"Error getting list items for list {list_id}: {e}")
            return []

    def get_list_versions(self, project_name: str, list_id: str) -> Dict[str, Any]:
        query = """query ($project: String!, $list_id: String!) {
                       project(name: $project) {
                        entityList(id: $list_id) {
                          entityType
                          items {
                            edges {
                              node {
                                name
                                ... on VersionNode {
                                  id
                                  name
                                  path
                                  parents
                                  status
                                  createdAt
                                  productId
                                  author
                                  thumbnailId
                                  version
                                  product{
                                    name
                                    versions {
                                      edges {
                                        node {
                                          id
                                          name
                                          path
                                          parents
                                          status
                                          createdAt
                                          productId
                                          author
                                          thumbnailId
                                          version
                                          task {
                                            name
                                            id
                                            taskType
                                            status
                                          }
                                          hasReviewables
                                          representations {
                                            edges {
                                              node {
                                                attrib {
                                                  path
                                                  description
                                                  frameEnd
                                                  frameStart
                                                  handleEnd
                                                  handleStart
                                                  fps
                                                }
                                              }
                                            }
                                          }
                                        }
                                      }
                                    }
                                  }
                                  task{
                                    name
                                    id
                                    taskType
                                    status
                                  }
                                  hasReviewables
                                  representations {
                                    edges {
                                      node {
                                        attrib {
                                          path
                                          description
                                          frameEnd
                                          frameStart
                                          handleEnd
                                          handleStart
                                          fps
                                        }
                                      }
                                    }
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                    """
        return self.graphql_query(query, {"project": project_name, "list_id": list_id})