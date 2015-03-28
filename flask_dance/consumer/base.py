from __future__ import unicode_literals, print_function

import six
from abc import ABCMeta, abstractmethod
from distutils.version import StrictVersion
import flask
from flask.signals import Namespace
from flask_dance.consumer.storage.session import SessionStorage


_signals = Namespace()
oauth_authorized = _signals.signal('oauth-authorized')
oauth_error = _signals.signal('oauth-error')


class BaseOAuthConsumerBlueprint(six.with_metaclass(ABCMeta, flask.Blueprint)):
    def __init__(self, name, import_name,
            static_folder=None, static_url_path=None, template_folder=None,
            url_prefix=None, subdomain=None, url_defaults=None, root_path=None,
            login_url=None, authorized_url=None,
            token_storage=None, token_storage_class=None):

        bp_kwargs = dict(
            name=name,
            import_name=import_name,
            static_folder=static_folder,
            static_url_path=static_url_path,
            template_folder=template_folder,
            url_prefix=url_prefix,
            subdomain=subdomain,
            url_defaults=url_defaults,
            root_path=root_path,
        )
        # `root_path` didn't exist until 1.0
        if StrictVersion(flask.__version__) < StrictVersion('1.0'):
            del bp_kwargs["root_path"]
        flask.Blueprint.__init__(self, **bp_kwargs)

        login_url = login_url or "/{bp.name}"
        authorized_url = authorized_url or "/{bp.name}/authorized"

        self.add_url_rule(
            rule=login_url.format(bp=self),
            endpoint="login",
            view_func=self.login,
        )
        self.add_url_rule(
            rule=authorized_url.format(bp=self),
            endpoint="authorized",
            view_func=self.authorized,
        )

        self.user = None
        self.user_id = None

        token_storage_class = token_storage_class or SessionStorage
        self.token_storage = token_storage or token_storage_class(self)

        self.logged_in_funcs = []
        self.from_config = {}
        self.before_app_request(self.load_config)
        self.before_app_request(self.load_token)

    def load_config(self):
        """
        Used to dynamically load variables from the Flask application config
        into the blueprint. To tell this blueprint to pull configuration from
        the app, just set key-value pairs in the ``from_config`` dict. Keys
        are the name of the local variable to set on the blueprint object,
        and values are the variable name in the Flask application config.
        For example:

            blueprint["session.client_id"] = "GITHUB_OAUTH_CLIENT_ID"

        """
        for local_var, config_var in self.from_config.items():
            value = flask.current_app.config.get(config_var)
            if value:
                if "." in local_var:
                    # this is a dotpath -- needs special handling
                    body, tail = local_var.rsplit(".", 1)
                    obj = getattrd(self, body)
                    setattr(obj, tail, value)
                else:
                    # just use a normal setattr call
                    setattr(self, local_var, value)

    @abstractmethod
    def load_token(self):
        raise NotImplementedError()

    @abstractmethod
    def login(self):
        raise NotImplementedError()

    @abstractmethod
    def authorized(self):
        raise NotImplementedError()

    def get_token(self, *args, **kwargs):
        return self.token_storage.get(*args, **kwargs)

    def set_token(self, *args, **kwargs):
        return self.token_storage.set(*args, **kwargs)

    def delete_token(self, *args, **kwargs):
        return self.token_storage.delete(*args, **kwargs)

    token = property(get_token, set_token, delete_token)

