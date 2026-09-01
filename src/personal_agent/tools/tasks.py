import json
from typing import List, Dict, Any, Optional
from personal_agent.tools.auth import GoogleAuthManager

class GoogleTasksTool:
    def __init__(self, service: Optional[Any] = None, auth_manager: Optional[GoogleAuthManager] = None):
        if service:
            self.service = service
        else:
            self.auth_manager = auth_manager or GoogleAuthManager()
            try:
                self.service = self.auth_manager.build_service('tasks', 'v1')
            except Exception as e:
                print(f"[GoogleTasksTool] Could not initialize live Google Tasks service: {e}")
                self.service = None

    def list_tasks(self, tasklist_id: str = "@default", show_completed: bool = False) -> List[Dict[str, Any]]:
        if not self.service:
            return []

        try:
            results = self.service.tasks().list(
                tasklist=tasklist_id,
                showCompleted=show_completed,
                showHidden=False
            ).execute()
            items = results.get('items', [])
            return [self._normalize_task(item) for item in items]
        except Exception as e:
            print(f"[GoogleTasksTool] Error listing tasks: {e}")
            return []

    def get_task(self, task_id: str, tasklist_id: str = "@default") -> Dict[str, Any]:
        if not self.service:
            return {"error": "Google Tasks service unavailable"}

        try:
            task = self.service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
            return self._normalize_task(task)
        except Exception as e:
            return {"error": str(e)}

    def create_task(
        self,
        title: str,
        notes: Optional[str] = None,
        due: Optional[str] = None,
        tasklist_id: str = "@default"
    ) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Google Tasks service unavailable"}

        body = {
            "title": title,
            "notes": notes or ""
        }
        if due:
            # Format RFC 3339 timestamp (e.g., 2026-09-01T00:00:00.000Z)
            body["due"] = due if due.endswith("Z") else f"{due}T00:00:00.000Z"

        try:
            created_task = self.service.tasks().insert(tasklist=tasklist_id, body=body).execute()
            return {
                "status": "success",
                "task": self._normalize_task(created_task)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def complete_task(self, task_id: str, tasklist_id: str = "@default") -> Dict[str, Any]:
        if not self.service:
            return {"error": "Google Tasks service unavailable"}

        try:
            task = self.service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
            task['status'] = 'completed'
            updated = self.service.tasks().update(tasklist=tasklist_id, task=task_id, body=task).execute()
            return {
                "status": "success",
                "completed_task_id": updated.get('id'),
                "title": updated.get('title')
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        notes: Optional[str] = None,
        due: Optional[str] = None,
        tasklist_id: str = "@default"
    ) -> Dict[str, Any]:
        if not self.service:
            return {"error": "Google Tasks service unavailable"}

        try:
            task = self.service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
            if title is not None:
                task['title'] = title
            if notes is not None:
                task['notes'] = notes
            if due is not None:
                task['due'] = due if due.endswith("Z") else f"{due}T00:00:00.000Z"

            updated = self.service.tasks().update(tasklist=tasklist_id, task=task_id, body=task).execute()
            return {
                "status": "success",
                "task": self._normalize_task(updated)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _normalize_task(self, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": item.get('id'),
            "title": item.get('title', 'Untitled Task'),
            "notes": item.get('notes', ''),
            "status": item.get('status', 'needsAction'),
            "due": item.get('due'),
            "updated": item.get('updated')
        }

# Tool wrappers for Registry / LLM Runtime
def list_tasks(tasklist_id: str = "@default") -> str:
    """List current active Google tasks."""
    tool = GoogleTasksTool()
    tasks = tool.list_tasks(tasklist_id=tasklist_id)
    return json.dumps(tasks, indent=2)

def get_task(task_id: str, tasklist_id: str = "@default") -> str:
    """Get details of a specific Google task."""
    tool = GoogleTasksTool()
    task = tool.get_task(task_id=task_id, tasklist_id=tasklist_id)
    return json.dumps(task, indent=2)
