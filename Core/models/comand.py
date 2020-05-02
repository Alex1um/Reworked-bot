import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm

class CommandTable(SqlAlchemyBase):
    __tablename__ = 'commands'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           autoincrement=True,
                           primary_key=True)
    Name = sqlalchemy.Column(sqlalchemy.String)
    activates = sqlalchemy.Column(sqlalchemy.String)
