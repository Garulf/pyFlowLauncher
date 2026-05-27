from dataclasses import dataclass, field
import json
from typing import Self
from pathlib import Path

from .models.plugin_manifest import FILE_NAME, PluginMetadata


@dataclass
class Manifest:
    id: str
    name: str
    author: str
    version: str
    language: str
    description: str
    website: str
    execute_file_name: str
    ico_path: str
    action_keyword: str
    action_keywords: list[str] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: Path) -> Self:
        """Load the manifest from a JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)

    @classmethod
    def from_dir(cls, dir_path: Path) -> Self:
        """Load the manifest from a directory containing a plugin.json file."""
        return cls.from_file(Path(dir_path) / FILE_NAME)

    def to_json(self) -> PluginMetadata:
        """Convert the manifest to a JSON-serializable dictionary."""
        return PluginMetadata(
            ID=self.id,
            Name=self.name,
            Author=self.author,
            Version=self.version,
            Language=self.language,
            Description=self.description,
            Website=self.website,
            ExecuteFileName=self.execute_file_name,
            IcoPath=self.ico_path,
            ActionKeyword=self.action_keyword,
            ActionKeywords=self.action_keywords,
        )

    def save(self, path: str) -> None:
        """Save the manifest to a JSON file."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_json(), f, ensure_ascii=False, indent=4)
