from . import BaseTokenStorage
import flask


class SessionStorage(BaseTokenStorage):
    """
    The default storage backend. Stores and retrieves OAuth tokens using
    the :ref:`Flask session <flask:sessions>`.
    """
    def __init__(self, blueprint, key="{bp.name}_oauth_token"):
        """
        Args:
            blueprint: The Flask-Dance blueprint.
            key (str): The name to use as a key for storing the OAuth token in the
                Flask session. This string will have ``.format(bp=self.blueprint)``
                called on it before it is used. so you can refer to information
                on the blueprint as part of the key. For example, ``{bp.name}``
                will be replaced with the name of the blueprint.
        """
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
