import json
from typing import List, Optional

from . import JSONRPC_VER, ids
from .models import JsonRPCRequest


def create_request(
        method: str,
        parameters: Optional[List] = None,
        id: Optional[int] = None,
        jsonrpc: str = JSONRPC_VER
) -> JsonRPCRequest:
    return {
        "jsonrpc": jsonrpc,
        "method": method,
        "parameters": parameters or [],
        "id": id or next(ids)
    }


def request_from_string(
    method: str,
    parameters: Optional[List] = None,
    id: Optional[int] = None,
) -> str:
    return json.dumps(
        create_request(method, parameters, id)
    )


def send_request(request: JsonRPCRequest) -> None:
    print(json.dumps(request))
