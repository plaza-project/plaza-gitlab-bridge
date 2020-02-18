import re
import os
from xdg import XDG_DATA_HOME

import sqlalchemy

from . import models

DB_PATH_ENV = 'PLAZA_GITLAB_BRIDGE_DB_PATH'

if os.getenv(DB_PATH_ENV, None) is None:
    _DATA_DIRECTORY = os.path.join(XDG_DATA_HOME, "plaza", "bridges", "gitlab")
    CONNECTION_STRING = "sqlite:///{}".format(os.path.join(_DATA_DIRECTORY, 'db.sqlite3'))
else:
    CONNECTION_STRING = os.getenv(DB_PATH_ENV)


class EngineContext:
    def __init__(self, engine):
        self.engine = engine
        self.connection = None

    def __enter__(self):
        self.connection = self.engine.connect()
        return self.connection

    def __exit__(self, exc_type, exc_value, tb):
        self.connection.close()

class StorageEngine:
    def __init__(self, engine):
        self.engine = engine

    def _connect_db(self):
        return EngineContext(self.engine)

    def register_user(self, gitlab_user, plaza_user):
        with self._connect_db() as conn:
            gitlab_id = self._get_or_add_gitlab_user(conn, gitlab_user)
            plaza_id = self._get_or_add_plaza_user(conn, plaza_user)

            check = conn.execute(
                sqlalchemy.select([models.PlazaUsersInGitlab.c.plaza_id])
                .where(
                    sqlalchemy.and_(
                        models.PlazaUsersInGitlab.c.plaza_id == plaza_id,
                        models.PlazaUsersInGitlab.c.gitlab_id == gitlab_id))
            ).fetchone()

            if check is not None:
                return

            insert = models.PlazaUsersInGitlab.insert().values(plaza_id=plaza_id,
                                                               gitlab_id=gitlab_id)
            conn.execute(insert)

    def get_gitlab_users(self, plaza_user):
        with self._connect_db() as conn:
            plaza_id = self._get_or_add_plaza_user(conn, plaza_user)

            join = sqlalchemy.join(models.GitlabUserRegistration, models.PlazaUsersInGitlab,
                                   models.GitlabUserRegistration.c.id
                                   == models.PlazaUsersInGitlab.c.gitlab_id)
            results = conn.execute(
                sqlalchemy.select([
                    models.GitlabUserRegistration.c.gitlab_user_id,
                    models.GitlabUserRegistration.c.gitlab_instance,
                    models.GitlabUserRegistration.c.gitlab_user_name,
                    models.GitlabUserRegistration.c.gitlab_token,
                ])
                .select_from(join)
                .where(models.PlazaUsersInGitlab.c.plaza_id == plaza_id)
            ).fetchall()

            return [
                dict(zip(["user_id", "instance", "user_name", "token"], row))
                for row in results
            ]

    def _get_or_add_gitlab_user(self, conn, gitlab_user):
        user_id = gitlab_user["user_id"]
        gitlab_instance = gitlab_user["instance"]
        token = gitlab_user["token"]
        username = gitlab_user["username"]

        check = conn.execute(
            sqlalchemy.select([models.GitlabUserRegistration.c.id])
            .where(models.GitlabUserRegistration.c.gitlab_token == token)
        ).fetchone()

        if check is not None:
            return check.id

        insert = models.GitlabUserRegistration.insert().values(gitlab_token=token,
                                                               gitlab_user_id=user_id,
                                                               gitlab_user_name=username,
                                                               gitlab_instance=gitlab_instance)
        result = conn.execute(insert)
        return result.inserted_primary_key[0]

    def _get_or_add_plaza_user(self, conn, plaza_user):
        check = conn.execute(
            sqlalchemy.select([models.PlazaUsers.c.id])
            .where(models.PlazaUsers.c.plaza_user_id == plaza_user)
        ).fetchone()

        if check is not None:
            return check.id

        insert = models.PlazaUsers.insert().values(plaza_user_id=plaza_user)
        result = conn.execute(insert)
        return result.inserted_primary_key[0]

def get_engine():
    # Create path to SQLite file, if its needed.
    if CONNECTION_STRING.startswith('sqlite'):
        db_file = re.sub("sqlite.*:///", "", CONNECTION_STRING)
        os.makedirs(os.path.dirname(db_file), exist_ok=True)

    engine = sqlalchemy.create_engine(CONNECTION_STRING, echo=True)
    metadata = models.metadata
    metadata.create_all(engine)

    return StorageEngine(engine)
