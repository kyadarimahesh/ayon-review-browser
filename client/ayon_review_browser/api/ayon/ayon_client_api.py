from typing import Optional, List, Dict, Any

from .project_service import ProjectService
from .version_service import VersionService
from .task_service import TaskService
from .file_service import FileService


class AyonClient:
    def __init__(self) -> None:
        self.project_service = ProjectService()
        self.version_service = VersionService()
        self.task_service = TaskService()
        self.file_service = FileService()

    # Project operations
    def get_projects(self) -> List[Dict[str, Any]]:
        return self.project_service.get_projects()

    def get_lists(self, project_name: str, entity_type: Optional[str] = "version") -> Dict[str, str]:
        return self.project_service.get_lists(project_name, entity_type)

    def get_list_items(self, project_name: str, list_id: str) -> List[Dict[str, Any]]:
        return self.project_service.get_list_items(project_name, list_id)

    def get_list_versions(self, project_name: str, list_id: str) -> Dict[str, Any]:
        return self.project_service.get_list_versions(project_name, list_id)

    # Version operations
    def get_version_thumbnail_to_local(self, project_name: str, version_id: str) -> Optional[str]:
        return self.version_service.get_version_thumbnail_to_local(project_name, version_id)

    def get_version_thumbnail_data(self, project_name: str, version_id: str) -> Optional[bytes]:
        return self.version_service.get_version_thumbnail_data(project_name, version_id)

    def get_versions_for_product(self, project_name: str, product_id: str) -> List[Dict[str, Any]]:
        return self.version_service.get_versions_for_product(project_name, product_id)

    def get_version_details(self, project_name: str, version_id: str) -> Dict[str, Any]:
        return self.version_service.get_version_details(project_name, version_id)

    # Task operations
    def get_tasks(self, project_name: str) -> Dict[str, Any]:
        return self.task_service.get_tasks(project_name)

    def get_recent_tasks_count(self, project_name: str, days: int = 7) -> int:
        return self.task_service.get_recent_tasks_count(project_name, days)

    # File operations
    @staticmethod
    def upload_file(project_name: str, file_path: str, activity_id: str = None) -> Optional[str]:
        return FileService.upload_file(project_name, file_path, activity_id)

    # Status operations
    def get_version_statuses(self, project_name: str) -> List[Dict[str, str]]:
        """Get available version statuses for a project with colors."""
        query = """
        query GetVersionStatuses($projectName: String!) {
            project(name: $projectName) {
                statuses {
                    name
                    color
                    icon
                    shortName
                    state
                    scope
                }
            }
        }
        """
        variables = {"projectName": project_name}
        result = self.graphql_query(query, variables)

        if result and "data" in result and result["data"]["project"]:
            statuses = result["data"]["project"]["statuses"]

            version_statuses = [
                {"value": status["name"], "color": status["color"]}
                for status in statuses
                if "version" in status["scope"]
            ]

            return [{"value": "All"}] + version_statuses

        return [{"value": "All"}]

    # Task type operations
    def get_task_types(self, project_name: str) -> List[Dict[str, str]]:
        """Get available task types for a project with colors and icons."""
        query = """
        query GetTaskTypes($projectName: String!) {
            project(name: $projectName) {
                taskTypes {
                    icon
                    name
                    shortName
                    color
                }
            }
        }
        """
        variables = {"projectName": project_name}
        result = self.graphql_query(query, variables)

        if result and "data" in result and result["data"]["project"]:
            task_types = result["data"]["project"]["taskTypes"]

            task_type_items = [
                {"value": task_type["name"], "color": task_type["color"]}
                for task_type in task_types
            ]

            return [{"value": "All"}] + task_type_items

        return [{"value": "All"}]

    # Version status update
    def update_version_status(self, project_name: str, version_id: str, status: str) -> bool:
        """Update version status."""
        return self.version_service.update_version_status(project_name, version_id, status)

    # GraphQL operations
    @staticmethod
    def graphql_query(query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        from .base_client import BaseAyonClient
        return BaseAyonClient.graphql_query(query, variables)
