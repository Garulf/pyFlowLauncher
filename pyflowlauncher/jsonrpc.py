import json
import sys
from typing import Any, Dict, Mapping, TypedDict, NotRequired


class JsonRPCRequest(TypedDict):
    method: str
    parameters: list
    settings: NotRequired[Dict[Any, Any]]


Response = Dict[Any, Any]


class JsonRPCClient:

    def send(self, data: Mapping) -> None:
        json.dump(data, sys.stdout)

    def recieve(self) -> JsonRPCRequest:
        try:
            return json.loads(sys.argv[1])
        except IndexError:
            return {'method': 'query', 'parameters': ['']}
