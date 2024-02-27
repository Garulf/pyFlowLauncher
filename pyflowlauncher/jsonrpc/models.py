from typing import TypedDict


class JsonRPCRequest(TypedDict):
    id: int
    jsonrpc: str
    method: str
    parameters: list


class JsonRPCResponse(TypedDict):
    id: int
    jsonrpc: str
    result: list
