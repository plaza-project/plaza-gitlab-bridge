from sqlalchemy import Column, Integer, String, MetaData, Column, ForeignKey, UniqueConstraint, Table

metadata = MetaData()

GitlabUserRegistration = Table(
    'GITLAB_USER_REGISTRATION', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('gitlab_token', String(256), unique=True),
    Column('gitlab_user_id', String(256)),
    Column('gitlab_user_name', String(256)),
    Column('gitlab_instance', String(256)))

PlazaUsers = Table(
    'PLAZA_USERS', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('plaza_user_id', String(36), unique=True))

PlazaUsersInGitlab = Table(
    'PLAZA_USERS_IN_GITLAB', metadata,
    Column('plaza_id', Integer, ForeignKey('PLAZA_USERS.id'), primary_key=True),
    Column('gitlab_id', Integer, ForeignKey('GITLAB_USER_REGISTRATION.id'), primary_key=True),
    __table_args__=(UniqueConstraint('plaza_id', 'gitlab_id')))
