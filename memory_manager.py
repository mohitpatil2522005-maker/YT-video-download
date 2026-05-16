import json
import os
from typing import List, Dict, Any, Optional

class MemoryManager:
    def __init__(self, memory_file: str = "memory.json"):
        self.memory_file = memory_file
        self.data = self._load_memory()

    def _load_memory(self) -> Dict[str, Any]:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "pending": [],
            "completed": [],
            "failed": [],
            "last_processed_index": -1,
            "current_status": "idle"
        }

    def save(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)

    def set_pending(self, titles: List[str]):
        # Filter out already completed
        completed_titles = {c['query'] for c in self.data['completed']}
        self.data['pending'] = [t for t in titles if t not in completed_titles]
        self.save()

    def get_next_title(self) -> Optional[str]:
        if not self.data['pending']:
            return None
        return self.data['pending'][0]

    def mark_completed(self, query: str, title: str, url: str):
        self.data['completed'].append({
            "query": query,
            "title": title,
            "url": url,
            "timestamp": self._get_timestamp()
        })
        if query in self.data['pending']:
            self.data['pending'].remove(query)
        self.data['last_processed_index'] += 1
        self.save()

    def mark_failed(self, query: str, error: str):
        self.data['failed'].append({
            "query": query,
            "error": error,
            "timestamp": self._get_timestamp()
        })
        if query in self.data['pending']:
            self.data['pending'].remove(query)
        self.save()

    def _get_timestamp(self) -> str:
        import datetime
        return datetime.datetime.now().isoformat()

    def get_status(self) -> str:
        total = len(self.data['pending']) + len(self.data['completed']) + len(self.data['failed'])
        done = len(self.data['completed'])
        return f"Progress: {done}/{total} completed. {len(self.data['pending'])} pending."
