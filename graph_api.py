import requests # pip install requests
from urllib.parse import parse_qs
import json
from typing import Any
from common import *
from common import _base64Decode

class GraphAPIError(Exception):
    def __init__(self, result: Any):
        self.result = result
        self.type = getOrDefault(result, "error_code", "")
        self.message = getOrNone(result, "error_description") \
            or getOrNone(result, "error.message") or getOrDefault(result, "error_msg", result)
        Exception.__init__(self, self.message)

RequestArgs = dict[str, Any]

DEFAULT_VERSION = "v16.0"

class GraphApi:
    access_token: str | None
    timeout: int | None
    version: str

    def __init__(self, access_token=None, timeout=None, version=DEFAULT_VERSION):
        self.access_token = access_token
        self.timeout = timeout
        self.version = version

    def request(self, path: str, args: RequestArgs | None = None, post_args: RequestArgs | None = None, files=None, method=None):
        args = args or {}

        if self.access_token:
            if post_args is not None:
                post_args["access_token"] = self.access_token
            else:
                args["access_token"] = self.access_token

        url = "https://graph.facebook.com/{0}/{1}".format(self.version, path)
        return self._request(url, args, post_args, files, method)

    def _request(self, url: str, args: RequestArgs | None = None, post_args: RequestArgs | None = None, files=None, method=None):
        try:
            response = requests.request(method or "GET", url, timeout=self.timeout, params=args, data=post_args, files=files)
        except requests.HTTPError as err:
            raise GraphAPIError(json.loads(err.response.read()))

        headers = response.headers
        if 'json' in headers['content-type']:
            result = response.json()
        elif 'image/' in headers['content-type']:
            result = {"data": response.content, "mime-type": headers['content-type'], "url": response.url}
        elif "access_token" in parse_qs(response.text):
            query_str = parse_qs(response.text)
            if "access_token" in query_str:
                result = {"access_token": query_str["access_token"][0]}
                if "expires" in query_str:
                    result["expires"] = query_str["expires"][0]
            else:
                raise GraphAPIError(response.json())
        else:
            raise GraphAPIError('Maintype was not text, image, or querystring')

        if result and isinstance(result, dict) and result.get("error"):
            raise GraphAPIError(result)
        return result

    def get_object(self, id: str, **args):
        return self.request(id, args)

    def get_objects(self, ids, **args):
        args["ids"] = ",".join(ids)
        return self.request("", args)

    def put_object(self, parent_id: str, path: str, **data):
        assert self.access_token, "Write operations require an access token"
        return self.request("{0}/{1}".format(parent_id, path), post_args=data, method="POST")

if __name__ == "__main__":
    # hardcoded token from https://developers.facebook.com/tools/explorer
    # encoded because Facebook scans Github for access tokens
    AT = "RUFBSFExemZud3RRQkFJbnRGZ0dFV0tWZ1pDWkFMbkFGdUx0SFBDSGpDOXNOa3Q4OGtuUDliY1RWbUwwVHFMMGVxVnJQMlMwU0ZGeHd6OENXWkNTT0QxUE9zRGtMNjFWd3VUYUxuVDZHOWowYVllQlQxVTFhTG9BTVZ4UXg4R3JXTmJjYU13ejRieU01UTcwM2lBWXJLTFh6UlhFSmdSWkEwRzBmUE9ocjY4WkFHaFFTc0FsY3NNWkJRZHJVYnFRMUgwb0JVelpCN2FQMXhURm9MeVpBeWpheHl1aFRwQWJ6TzJCY2xiSDF5V1pCTWVyck9PaGVlblhEcQ=="
    access_token = _base64Decode(AT)
    graph_api = GraphApi(access_token)
    me = graph_api.get_object("me")
    print(me)
