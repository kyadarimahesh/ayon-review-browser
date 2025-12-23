from datetime import datetime, timedelta
from typing import Dict, Any
from .base_client import BaseAyonClient


class TaskService(BaseAyonClient):
    def get_tasks(self, project_name: str) -> Dict[str, Any]:
        query = """
                query ($project: String!) {
                    project(name: $project) {
                        tasks (first: 10000){
                            edges {
                                node {
                                    data
                                    type
                                    name 
                                    status
                                    id
                                    thumbnailId
                                    folder {
                                        id
                                        name
                                        path
                                        type
                                        parent {
                                            id
                                            name
                                            path
                                            type
                                            parent {
                                                id
                                                name
                                                path
                                                type
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                """
        return self.graphql_query(query, {"project": project_name})

    def get_recent_tasks_count(self, project_name: str, days: int = 7) -> int:
        date_filter = (datetime.now() - timedelta(days=days)).isoformat() + "Z"

        query = """
           query ($project: String!, $filter: String!) {
               project(name: $project) {
                   tasks(filter: $filter, first:1000) {
                       edges {
                           node {
                               id
                               name
                               updatedAt
                           }
                       }
                   }
               }
           }
           """

        filter_json = f'{{"conditions":[{{"key":"updatedAt","operator":"gte","value":"{date_filter}"}}]}}'

        try:
            result = self.graphql_query(query, {"project": project_name, "filter": filter_json})
            if result and "data" in result and result["data"] and "project" in result["data"]:
                project_data = result["data"]["project"]
                if project_data and "tasks" in project_data and project_data["tasks"]:
                    return len(project_data["tasks"]["edges"])
            return 0
        except Exception as e:
            print(f"Error getting recent tasks count: {e}")
            return 0


if __name__ == "__main__":
    client = TaskService()
    project = "space_project"
    tasks = client.get_tasks(project)
    print(tasks)
    recent_count = client.get_recent_tasks_count(project, days=100)
    print(f"Recent tasks in last 7 days: {recent_count}")