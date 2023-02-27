from typing import *
import base64

T = TypeVar("T")

def getOrNone(obj: Any, path: str) -> Any:
    try:
        acc = obj
        for step in path.split("."):
            acc = acc[step]
        return acc
    except:
        return None

def getOrDefault(obj: Any, path: str, default: T) -> T:
    return getOrNone(obj, path) or default

def base64Decode(encoded: str) -> bytes:
    return base64.urlsafe_b64decode(encoded + "=" * (4 - (len(encoded) % 4)))
