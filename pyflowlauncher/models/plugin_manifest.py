from typing import TypedDict, List


FILE_NAME = 'plugin.json'


class PluginMetadata(TypedDict):
    ID: str
    Name: str
    Author: str
    Version: str
    Language: str
    Description: str
    Website: str
    ExecuteFileName: str
    IcoPath: str
    ActionKeyword: str
    ActionKeywords: List[str]
