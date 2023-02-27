from common import *
from graph_api import DEFAULT_VERSION, GraphAPIError, GraphApi
from urllib.parse import urlencode
import hmac
import hashlib
import json

class AuthError(GraphAPIError):
    pass

Cookies = dict[str, str]

DEFAULT_REDIRECT = "https://example.com/"

class GraphApiAuth:
    access_token: bytes

    def __init__(self, app_id: str, app_secret: str, redirect_uri: str | None = None, version=DEFAULT_VERSION):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri or DEFAULT_REDIRECT
        self.version = version

    def get_auth_url(self, perms: str | None = None, **kwargs):
        url = "https://www.facebook.com/{0}/dialog/oauth?".format(self.version)
        kvps = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': perms or "public_profile",
            **kwargs,
        }
        return url + urlencode(kvps)

    def get_access_token_from_code(self, code, **kwargs):
        args = {"code": code, "redirect_uri": self.redirect_uri, "client_id": self.app_id, "client_secret": self.app_secret}
        args.update(**kwargs)

        return GraphApi(version=self.version).request("oauth/access_token", args)

    def extend_access_token(self):
        args = {
            "client_id": self.app_id,
            "client_secret": self.app_secret,
            "grant_type": "fb_exchange_token",
            "fb_exchange_token": self.access_token,
        }

        return GraphApi(version=self.version).request("oauth/access_token", args)

if __name__ == "__main__":
    FOOBAR = {"id": "1188538135358142", "secret": "58bd3e9660cf9487763cd4a0d89a4a60"}
    FAZBEAR = {"id": "511097751192276", "secret": "35a3ae140472af3bd2d1c8a852570b64"}

    app = FAZBEAR
    auth = GraphApiAuth(app["id"], app["secret"])
    print(auth.get_auth_url("public_profile,email,user_likes,user_birthday,user_gender"))
    auth_code = input("Enter auth code: ")
    access_token = auth.get_access_token_from_code(auth_code)["access_token"]
    print(access_token)

    graph_api = GraphApi(access_token)
    me = graph_api.get_object("me")
    print(me)
