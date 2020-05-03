import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec


class DataBaseSession:
    __factory = None

    def __init__(self, db_file):
        self.SqlAlchemyBase = dec.declarative_base()

        if not db_file or not db_file.strip():
            raise Exception("Необходимо указать файл базы данных.")

        conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'

        print(f"Подключение к базе данных по адресу {conn_str}")

        class User(self.SqlAlchemyBase):
            __tablename__ = 'users'

            id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
            type = sqlalchemy.Column(sqlalchemy.String)
            level = sqlalchemy.Column(sqlalchemy.Integer, default=0)

            def __init__(self, id, type, permission_level):
                self.id = id
                self.type = type
                self.permission_level = permission_level

        class CommandTable(self.SqlAlchemyBase):
            __tablename__ = 'commands'

            # id = sqlalchemy.Column(sqlalchemy.Integer,
            #                        autoincrement=True,
            #                        primary_key=True)
            name = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
            activates = sqlalchemy.Column(sqlalchemy.String)
            level = sqlalchemy.Column(sqlalchemy.Integer)
            command_symbol = sqlalchemy.Column(sqlalchemy.String)
            help = sqlalchemy.Column(sqlalchemy.String, nullable=True)

            def __init__(self, name, activates, help, permission_level, sym):
                self.name = name
                self.activates = activates
                self.level = permission_level
                self.command_symbol = sym
                self.help = help

        class Settings(self.SqlAlchemyBase):
            __tablename__ = 'settings'

            set_id = sqlalchemy.Column(sqlalchemy.Integer,
                                       autoincrement=True,
                                       primary_key=True)
            user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                        sqlalchemy.ForeignKey('users.id'))
            name = sqlalchemy.Column(sqlalchemy.String)
            value = sqlalchemy.Column(sqlalchemy.String)


        self.User = User
        self.Settings = Settings
        self.CommandTable = CommandTable

        self.engine = sqlalchemy.create_engine(conn_str, echo=False)
        self.__factory = orm.sessionmaker(bind=self.engine)

        self.SqlAlchemyBase.metadata.create_all(self.engine)



    def create_session(self) -> Session:
        return self.__factory()

