from typing import Dict, Any, List, Optional
from personal_agent.workspace.workspace_connector import NormalizedWorkspaceItem

class UnifiedWorkspaceIndex:
    def __init__(self):
        self.items_by_id: Dict[str, NormalizedWorkspaceItem] = {}
        self.items_by_source: Dict[str, List[NormalizedWorkspaceItem]] = {}
        self.items_by_type: Dict[str, List[NormalizedWorkspaceItem]] = {}

    def add_item(self, item: NormalizedWorkspaceItem):
        self.items_by_id[item.item_id] = item
        self.items_by_source.setdefault(item.source_system, []).append(item)
        self.items_by_type.setdefault(item.item_type, []).append(item)

    def search_index(self, query: str) -> List[NormalizedWorkspaceItem]:
        q = query.lower()
        results = []
        for item in self.items_by_id.values():
            if q in item.title.lower() or q in item.content.lower() or (item.author and q in item.author.lower()):
                results.append(item)
        return results

    def get_items_by_source(self, source_system: str) -> List[NormalizedWorkspaceItem]:
        return self.items_by_source.get(source_system, [])

    def get_items_by_type(self, item_type: str) -> List[NormalizedWorkspaceItem]:
        return self.items_by_type.get(item_type, [])
