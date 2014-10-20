from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils import JSONType, UUIDType, ChoiceType, ScalarListType
try:
    from babel import lazy_gettext as _
except ImportError:
    _ = lambda s: s


class FlaskDanceMixin(object):
    @declared_attr
    def __tablename__(cls):
        return "flask_dance_{}".format(cls.__name__.lower())


class OAuthConsumerMixin(FlaskDanceMixin):
    """
    A :ref:`SQLAlchemy declarative mixin <sqlalchemy:declarative_mixins>` with
    some suggested columns for a model to store OAuth tokens:

    ``id``
        an integer primary key
    ``provider``
        a short name to indicate which OAuth provider issued
        this token
    ``created_on``
        an automatically generated datetime that indicates when
        the OAuth provider issued this token
    ``token``
        a :class:`JSON <sqlalchemy_utils.types.json.JSONType>` field to store
        the actual token received from the OAuth provider
    """
    id = Column(Integer, primary_key=True)
    provider = Column(String(50))
    created_on = Column(DateTime, default=datetime.utcnow)
    token = Column(MutableDict.as_mutable(JSONType))

    def __repr__(self):
        parts = []
        parts.append(self.__class__.__name__)
        if self.id:
            parts.append("id={}".format(self.id))
        if self.provider:
            parts.append('provider="{}"'.format(self.provider))
        return "<{}>".format(" ".join(parts))


GRANT_TYPES = (
    ("authorization_code", _("Authorization Code Grant")),
    ("password", _("Resource Owner Password Credentials Grant")),
    ("client_credentials", _("Client Credentials Grant")),
)
RESPONSE_TYPES = (
    ("code", _("Authorization code")),
)
def in_one_hour():
    return datetime.utcnow() + timedelta(hours=1)
def in_ten_minutes():
    return datetime.utcnow() + timedelta(minutes=10)


class OAuth2ProviderClientMixin(FlaskDanceMixin):
    id = Column(UUIDType, primary_key=True)
    grant_type = Column(ChoiceType(GRANT_TYPES))
    response_type = Column(ChoiceType(RESPONSE_TYPES))
    scopes = Column(ScalarListType)
    default_scopes = Column(ScalarListType)
    redirect_uris = Column(ScalarListType)
    default_redirect_uri = Column(String(80))
    # to add: reference to User


class OAuth2ProviderBearerTokenMixin(FlaskDanceMixin):
    id = Column(Integer, primary_key=True)
    scopes = Column(ScalarListType)
    access_token = Column(String(100), unique=True)
    refresh_token = Column(String(100), unique=True)
    expires_at = Column(DateTime, default=in_one_hour)
    # to add: reference to Client, User


class OAuth2ProviderAuthorizationCodeMixin(FlaskDanceMixin):
    id = Column(Integer, primary_key=True)
    scopes = Column(ScalarListType)
    code = Column(String(100), unique=True)
    expires_at = Column(DateTime, default=in_ten_minutes)
    # to add: reference to Client, User
