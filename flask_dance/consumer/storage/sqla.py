from sqlalchemy.orm.exc import NoResultFound
from flask_dance.utils import FakeCache, first, getattrd
from flask_dance.consumer.storage import BaseTokenStorage
try:
    from flask_login import AnonymousUserMixin
except ImportError:
    AnonymousUserMixin = None


class SQLAlchemyStorage(BaseTokenStorage):
    def __init__(self, blueprint, model, session,
                 user=None, user_id=None, anon_user=None, cache=None):
        super(SessionStorage, self).__init__(blueprint)
        self.model = model
        self.session = session
        self.user = user
        self.user_id = user_id
        self.anon_user = anon_user or AnonymousUserMixin
        self.cache = cache or FakeCache()

    def make_cache_key(name=None, user=None, user_id=None):
        uid = first([user_id, self.user_id, self.blueprint.user_id])
        if not uid:
            u = first(_get_real_user(ref, self.anon_user)
                      for ref in (user, self.user, self.blueprint.user))
            uid = getattr(u, "id", u)
        return "flask_dance_token|{name}|{user_id}".format(
            name=self.blueprint.name, user_id=uid,
        )

    @self.cache.memoize()
    def get(self, user=None, user_id=None):
        query = (
            self.session.query(self.model)
            .filter_by(provider=self.blueprint.name)
        )
        uid = first([user_id, self.user_id, self.blueprint.user_id])
        u = first(_get_real_user(ref, self.anon_user)
                  for ref in (user, self.user, self.blueprint.user))
        # check for user ID
        if hasattr(self.model, "user_id") and uid:
            query = query.filter_by(user_id=uid)
        # check for user (relationship property)
        elif hasattr(self.model, "user") and u:
            query = query.filter_by(user=u)
        # if we have the property, but not value, filter by None
        elif hasattr(self.model, "user_id"):
            query = query.filter_by(user_id=None)
        # run query
        try:
            return query.one().token
        except NoResultFound:
            return None
    get_token.make_cache_key = make_cache_key

    def set(self, token, user=None, user_id=None):
        # if there was an existing model, delete it
        existing_query = (
            self.session.query(self.model)
            .filter_by(provider=self.blueprint.name)
        )
        # check for user ID
        has_user_id = hasattr(self.model, "user_id")
        if has_user_id:
            uid = first([user_id, self.user_id, self.blueprint.user_id])
            if uid:
                existing_query = existing_query.filter_by(user_id=uid)
        # check for user (relationship property)
        has_user = hasattr(self.model, "user")
        if has_user:
            u = first(_get_real_user(ref, self.anon_user)
                      for ref in (user, self.user, self.blueprint.user))
            if u:
                existing_query = existing_query.filter_by(user=u)
        # queue up delete query -- won't be run until commit()
        existing_query.delete()
        # create a new model for this token
        kwargs = {
            "provider": self.blueprint.name,
            "token": token,
        }
        if has_user_id and uid:
            kwargs["user_id"] = uid
        if has_user and u:
            kwargs["user"] = u
        self.session.add(self.model(**kwargs))
        # commit to delete and add simultaneously
        self.session.commit()
        # invalidate cache
        self.cache.delete_memoized(self.get)

    def delete(self, user=None, user_id=None):
        query = (
            self.session.query(self.model)
            .filter_by(provider=self.blueprint.name)
        )
        uid = first([user_id, self.user_id, self.blueprint.user_id])
        u = first(_get_real_user(ref, self.anon_user)
                  for ref in (user, self.user, self.blueprint.user))
        # check for user ID
        if hasattr(self.model, "user_id") and uid:
            query = query.filter_by(user_id=uid)
        # check for user (relationship property)
        elif hasattr(self.model, "user") and u:
            query = query.filter_by(user=u)
        # if we have the property, but not value, filter by None
        elif hasattr(self.model, "user_id"):
            query = query.filter_by(user_id=None)
        # run query
        query.delete()
        self.session.commit()
        # invalidate cache
        self.cache.delete_memoized(self.get)


def _get_real_user(user, anon_user=None):
    """
    set_token_storage_sqlalchemy() has a user parameter that can be called with:

    * a real user object
    * a function that returns a real user object
    * a LocalProxy to a real user object (like Flask-Login's ``current_user``)

    This function returns the real user object, regardless of which we have.
    """
    if hasattr(user, "_get_current_object"):
        # this is a proxy
        user = user._get_current_object()
    if callable(user):
        # this is a function
        user = user()
    if anon_user and isinstance(user, anon_user):
        return None
    return user
