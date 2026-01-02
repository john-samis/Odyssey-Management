"""
Module to hold the volatile form template
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, Dict, Any


class GoogleFormTemplate:
    """
    Hold the hardcoded json for the title and the body for batchUpdate
    The change will always occur here, the template is canonical
    """
    def __init__(self, title: str, batch_update: Optional[dict] = None) -> None:
        self.title = title
        self.batch_update = batch_update or {"requests": []}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GoogleFormTemplate | None:
        if "title_header" in data:
            title = data["title_header"]["info"]["title"]
            body = data.get("form_body", {})
            batch_update = body if "requests" in body else {"requests": []}
            return cls(title=title, batch_update=batch_update)

        return None
    
    @classmethod
    def from_json_file(cls, path: Path, key: Optional[str] = None) -> "GoogleFormTemplate":
        obj = json.loads(path.read_text())
        payload = obj[key] if key else obj
        return cls.from_dict(payload)


    def __repr__(self) -> str:
        return f"GoogleFormTemplate(title={self.title}, requests={len(self.batch_update.get("requests", []))})"

    def __str__(self) -> str:
        return self.__repr__()
