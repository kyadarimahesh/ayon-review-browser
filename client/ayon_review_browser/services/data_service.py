import json
import sys
import os
from pprint import pprint

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from api.ayon import AyonClient
from utils.date_utils import standardize_date, filter_by_date_simple as filter_by_date


class DataService:
    def __init__(self):
        self.api = AyonClient()
        self.current_project = None

    def fetch_projects(self):
        return self.api.get_projects()

    def set_project(self, project_name):
        self.current_project = project_name

    def fetch_version_statuses(self, project_name=None):
        """Fetch dynamic version statuses for the project."""
        project = project_name or self.current_project

        if not project:
            return [{"value": "All"}]

        return self.api.get_version_statuses(project)

    def fetch_task_types(self, project_name=None):
        """Fetch dynamic task types for the project."""
        project = project_name or self.current_project

        if not project:
            return [{"value": "All"}]

        return self.api.get_task_types(project)

    def get_status_colors_dict(self, project_name=None):
        """Get status colors as a dictionary for activity display."""
        statuses = self.fetch_version_statuses(project_name)
        return {status['value']: status.get('color', '#ffffff') for status in statuses if status.get('value') != 'All'}

    def fetch_versions(self, project_name=None, date_filter="ALL"):
        project = project_name or self.current_project
        if not project:
            return []
        tasks = self.api.get_tasks(project)
        try:
            tasks_data = tasks.get("data", {}).get("project", {}).get("tasks", {}).get("edges", [])
        except AttributeError as e:
            print(f"Error accessing tasks data: {e}")
            return []
        result = []

        for task in tasks_data:
            task_node = task.get("node") or {}
            raw_task_data = task_node.get("data")

            task_data = {}
            if isinstance(raw_task_data, str):
                try:
                    # convert JSON string → dict
                    task_data = json.loads(raw_task_data)
                except Exception as e:
                    task_data = {}
                    print(e)

            if "submission_data" in task_data:
                folder = task_node.get("folder") or {}
                parent = folder.get("parent") or {}

                sequence_name = parent.get("name") if parent else "N/A"
                shot_name = folder.get("name") if folder else "N/A"
                task_id = task_node.get("id") if task_node else "N/A"
                task_name = task_node.get("name") if task_node else "N/A"
                task_type = task_node.get("type") if task_node else "N/A"
                task_status = task_node.get("status") if task_node else "N/A"
                task_thumbnail_id = task_node.get("thumbnailId") if task_node else "N/A"

                submission_data = task_data.get("submission_data", {})
                version_id = submission_data.get("version_id") or submission_data.get("workfile_version_id", "N/A")

                version = self.api.get_version_details(self.current_project, version_id=version_id)
                if isinstance(version, dict) and version.get("meta_data", {}).get("thumbnailId"):
                    thumbnail_data = self.api.get_version_thumbnail_data(self.current_project, version_id)
                else:
                    thumbnail_data = None

                result.append({
                    "sequence_name": sequence_name,
                    "shot_name": shot_name,
                    "task_name": task_name,
                    "task_type": task_type,
                    "task_status": task_status,
                    "author": submission_data.get("submitter_name", "N/A"),
                    "submission_type": submission_data.get("submission_type", "N/A"),
                    "submitted_at": standardize_date(submission_data.get("submitted_at", "N/A")),
                    "version_id": version_id,
                    "reviewer_name": submission_data.get("reviewer_name", "N/A"),
                    "versions": [version.get("meta_data", {}).get("name", "N/A")] if isinstance(version, dict) else [
                        "N/A"],
                    "product_id": version.get("meta_data", {}).get("productId", "N/A") if isinstance(version,
                                                                                                     dict) else "N/A",
                    "product": version.get("meta_data", {}).get("product", {}).get("name", "N/A") if isinstance(version,
                                                                                                                dict) else "N/A",
                    "version_status": version.get("meta_data", {}).get("status", "N/A") if isinstance(version,
                                                                                                      dict) else "N/A",
                    "task_id": task_id,
                    "thumbnail_data": thumbnail_data,
                    "representations": version.get("representations", []) if isinstance(version, dict) else [],
                    "path": version.get("meta_data", {}).get("product", {}).get("folder", {}).get("path", "N/A")
                })

        filtered_result = filter_by_date(result, date_filter)
        # Sort by date, latest first
        filtered_result.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
        return filtered_result

    def fetch_playlists(self, project_name=None):
        project = project_name or self.current_project
        if not project:
            return {}
        return self.api.get_lists(project, 'version')

    def fetch_version_activities(self, version_id, task_id=None, path=None, project_name=None,
                                 status_colors=None, update_callback=None):
        project = project_name or self.current_project
        return self.api.process_version_activities(project, version_id=version_id, task_id=task_id,
                                                   path=path, status_colors=status_colors,
                                                   update_callback=update_callback)

    def update_version_status(self, version_id: str, status: str, project_name=None) -> bool:
        """Update version status."""
        project = project_name or self.current_project
        if not project:
            return False
        return self.api.update_version_status(project, version_id, status)

    def fetch_versions_by_playlist(self, list_id, project_name=None, date_filter="ALL"):
        project = project_name or self.current_project
        if not project:
            return []
        list_versions = self.api.get_list_versions(project, list_id=list_id)
        if not list_versions or not list_versions.get("data") or not list_versions.get("data").get(
                "project") or not list_versions.get("data").get("project").get("entityList") or not list_versions.get(
            "data").get("project").get("entityList").get("items"):
            return []
        list_versions_data = list_versions.get("data").get("project").get("entityList").get("items").get("edges", [])
        result = []

        for list_version in list_versions_data:
            list_version_node = list_version.get("node")
            product = list_version_node.get("product", {})

            # Extract all versions for this product and standardize dates
            all_product_versions = []
            if product.get("versions", {}).get("edges"):
                for edge in product["versions"]["edges"]:
                    if edge.get("node"):
                        node = edge["node"].copy()
                        node['createdAt'] = standardize_date(node.get('createdAt', 'N/A'))
                        all_product_versions.append(node)

            # Process current version data
            version_data = self._process_version_data(list_version_node, all_product_versions)
            result.append(version_data)

        filtered_result = filter_by_date(result, date_filter)
        # Sort by date, latest first
        filtered_result.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return filtered_result

    def _process_version_data(self, version_node, all_product_versions):
        """Process version data and include all product versions."""
        # Get thumbnail
        if version_node.get("thumbnailId"):
            thumbnail_data = self.api.get_version_thumbnail_data(self.current_project, version_node["id"])
        else:
            thumbnail_data = None

        task = version_node.get("task") or {}
        parents = version_node.get("parents") or []

        # Process representations
        try:
            representations = [
                node["node"]["attrib"]
                for node in version_node.get("representations", {}).get("edges", [])
                if node and node.get("node") and node["node"].get("attrib")
            ]
        except (KeyError, TypeError):
            representations = []

        # Create versions list with all product versions
        versions_list = []
        for v in sorted(all_product_versions, key=lambda x: x.get('version', 0), reverse=True):
            version_name = f"v{v.get('version', 1):03d}"
            versions_list.append(version_name)

        # If no versions found, use current version
        if not versions_list:
            versions_list = [f"v{version_node.get('version', 1):03d}"]

        current_version = f"v{version_node.get('version', 1):03d}"

        return {
            "sequence_name": parents[1] if len(parents) > 1 else "N/A",
            "shot_name": parents[2] if len(parents) > 2 else "N/A",
            "task_name": task.get("name", "N/A"),
            "task_type": task.get("taskType", "N/A"),
            "task_status": task.get("status", "N/A"),
            "author": version_node.get("author", "N/A"),
            "submission_type": "N/A",
            "created_at": standardize_date(version_node.get("createdAt", "N/A")),
            "version_id": version_node.get("id", "N/A"),
            "reviewer_name": "N/A",
            "versions": versions_list,  # Now contains all product versions
            "all_product_versions": all_product_versions,  # Store full version data
            "current_version": current_version,
            "original_version": current_version,  # Track playlist's original version
            "product_id": version_node.get("productId", "N/A"),
            "product": version_node.get("product", {}).get("name", "N/A"),
            "version_status": version_node.get("status", "N/A"),
            "task_id": task.get("id", "N/A"),
            "thumbnail_data": thumbnail_data,
            "representations": representations,
            "path": version_node.get("path", "N/A"),
            "hasReviewables": version_node.get("hasReviewables")
        }


if __name__ == "__main__":
    pprint(DataService().fetch_versions_by_playlist('5b55c618557e11f09e920242ac120004', 'AY_TEST_SHOW'))
