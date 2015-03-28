from . import BaseTokenStorage
import flask


class SessionStorage(BaseTokenStorage):
    def __init__(self, blueprint, key="{bp.name}_oauth_token"):
        super(SessionStorage, self).__init__(blueprint, key=key)
        self.key = key

    def get(self):
        key = self.key.format(bp=self.blueprint)
        return flask.session.get(key)

    def set(self, token):
        key = self.key.format(bp=self.blueprint)
        flask.session[key] = token

    def delete(self, token):
        key = self.key.format(bp=self.blueprint)
        del flask.session[key]
