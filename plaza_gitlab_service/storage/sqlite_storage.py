import os
import sqlite3
from xdg import XDG_DATA_HOME

DB_PATH_ENV = 'PLAZA_GITLAB_BRIDGE_DB_PATH'
if os.getenv(DB_PATH_ENV, None) is None:
    DATA_DIRECTORY = os.path.join(XDG_DATA_HOME, "plaza", "bridges", "gitlab")
    DEFAULT_PATH = os.path.join(DATA_DIRECTORY, 'db.sqlite3')
else:
    DEFAULT_PATH = os.getenv(DB_PATH_ENV)
    DATA_DIRECTORY = os.path.dirname(DEFAULT_PATH)


class DBContext:
    def __init__(self, db, close_on_exit=True):
        self.db = db
        self.close_on_exit = close_on_exit

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, tb):
        if self.close_on_exit:
            self.db.close()


class SqliteStorage:
    def __init__(self, path, multithread=True):
        self.path = path
        self.db = None
        self.multithread = multithread
        self._create_db_if_not_exists()

    def _open_db(self):
        if not self.multithread:
            if self.db is None:
                self.db = sqlite3.connect(self.path)
                self.db.execute("PRAGMA foreign_keys = ON;")
            db = self.db
        else:
            db = sqlite3.connect(self.path)
            db.execute("PRAGMA foreign_keys = ON;")

        return DBContext(db, close_on_exit=not self.multithread)

    def _create_db_if_not_exists(self):
        os.makedirs(DATA_DIRECTORY, exist_ok=True)
        with self._open_db() as db:
            c = db.cursor()
            c.execute(
                """
            CREATE TABLE IF NOT EXISTS GITLAB_USER_REGISTRATION (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gitlab_token VARCHAR(256) UNIQUE,
                gitlab_user_id VARCHAR(256),
                gitlab_user_name VARCHAR(256),
                gitlab_instance VARCHAR(256)
            );
            """
            )

            c.execute(
                """
            CREATE TABLE IF NOT EXISTS PLAZA_USERS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plaza_user_id VARCHAR(36) UNIQUE
            );
            """
            )

            c.execute(
                """
            CREATE TABLE IF NOT EXISTS PLAZA_USERS_IN_GITLAB (
                plaza_id INTEGER,
                gitlab_id INTEGER,
                UNIQUE(plaza_id, gitlab_id),
                FOREIGN KEY(plaza_id) REFERENCES PLAZA_USERS(id),
                FOREIGN KEY(gitlab_id) REFERENCES GITLAB_USER_REGISTRATION(id)
            );
            """
            )
            db.commit()
            c.close()

    def is_gitlab_user_registered(self, user_id):
        with self._open_db() as db:
            c = db.cursor()
            c.execute(
                """
            SELECT count(1)
            FROM GITLAB_USER_REGISTRATION
            WHERE gitlab_user_id=?
            ;
            """,
                (user_id,),
            )
            result = c.fetchone()[0]

            c.close()

            return result > 0

    def get_plaza_user_from_gitlab(self, user_id):
        ## Warning: Untested!
        with self._open_db() as db:
            c = db.cursor()
            c.execute(
                """
            SELECT plaza_user_id
            FROM PLAZA_USERS as p
            JOIN PLAZA_USERS_IN_GITLAB as plaza_in_gitlab
            ON plaza_in_gitlab.plaza_id = p.id
            JOIN GITLAB_USER_REGISTRATION as m
            ON plaza_in_gitlab.gitlab_id = m.id
            WHERE m.gitlab_user_id=?
            ;
            """,
                (user_id,),
            )
            results = c.fetchall()

            c.close()
            assert 0 <= len(results) <= 1
            if len(results) == 0:
                raise Exception("User (gitlab:{}) not found".format(user_id))
            return results[0][0]

    def _get_or_add_gitlab_user(self, cursor, gitlab_user):

        user_id = gitlab_user["user_id"]
        gitlab_instance = gitlab_user["instance"]
        token = gitlab_user["token"]
        username = gitlab_user["username"]

        cursor.execute(
            """
        SELECT id
        FROM GITLAB_USER_REGISTRATION
        WHERE gitlab_token=?
        ;
        """,
            (token,),
        )

        results = cursor.fetchall()
        if len(results) == 0:  # New user
            cursor.execute(
                """
            INSERT INTO GITLAB_USER_REGISTRATION (
                gitlab_token,
                gitlab_user_id,
                gitlab_user_name,
                gitlab_instance
            ) VALUES(?, ?, ?, ?);
            """,
                (token, user_id, username, gitlab_instance),
            )
            return cursor.lastrowid
        elif len(results) == 1:  # Existing user
            return results[0][0]
        else:  # This shouldn't happen
            raise Exception(
                "Integrity error, query by UNIQUE returned multiple values: {}".format(
                    cursor.rowcount
                )
            )

    def _get_or_add_plaza_user(self, cursor, plaza_user):
        cursor.execute(
            """
        SELECT id
        FROM PLAZA_USERS
        WHERE plaza_user_id=?
        ;
        """,
            (plaza_user,),
        )

        results = cursor.fetchall()
        if len(results) == 0:  # New user
            cursor.execute(
                """
            INSERT INTO PLAZA_USERS (plaza_user_id) VALUES(?);
            """,
                (plaza_user,),
            )
            return cursor.lastrowid
        elif len(results) == 1:  # Existing user
            return results[0][0]
        else:  # This shouldn't happen
            raise Exception(
                "Integrity error, query by UNIQUE returned multiple values: {}".format(
                    cursor.rowcount
                )
            )

    def register_user(self, gitlab_user, plaza_user):
        with self._open_db() as db:
            c = db.cursor()
            gitlab_id = self._get_or_add_gitlab_user(c, gitlab_user)
            plaza_id = self._get_or_add_plaza_user(c, plaza_user)
            c.execute(
                """
            INSERT OR REPLACE INTO 
            PLAZA_USERS_IN_GITLAB (plaza_id, gitlab_id)
            VALUES (?, ?)
            """,
                (plaza_id, gitlab_id),
            )
            c.close()
            db.commit()

    def get_gitlab_users(self, plaza_user):
        with self._open_db() as db:
            c = db.cursor()
            plaza_id = self._get_or_add_plaza_user(c, plaza_user)
            c.execute(
                """
            SELECT gitlab_u.gitlab_user_id, 
                   gitlab_u.gitlab_instance,
                   gitlab_u.gitlab_token,
                   gitlab_u.gitlab_user_name
            FROM GITLAB_USER_REGISTRATION gitlab_u
            JOIN PLAZA_USERS_IN_GITLAB plaza_in_gitlab
            ON gitlab_u.id=plaza_in_gitlab.gitlab_id
            WHERE plaza_in_gitlab.plaza_id=?
            ;
            """,
                (plaza_id,),
            )
            results = c.fetchall()
            c.close()
            return [
                dict(zip(["user_id", "instance", "token", "user_name"], row))
                for row in results
            ]


def get_default():
    return SqliteStorage(DEFAULT_PATH)
