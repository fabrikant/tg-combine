from keys import ADMIN_ID
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    create_engine,
    ForeignKey,
)
from sqlalchemy.orm import Session, declarative_base, relationship
import logging

logger = logging.getLogger()
Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False)
    admin = Column(Boolean, nullable=False)

    def __str__(self):
        return f"name: {self.name}; id: {self.id}"

    def postprocessing(self):
        pass


def create_database(connection_string):
    engine = create_engine(connection_string, echo=True)
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    create_update_user(session, ADMIN_ID, "", admin=True)
    return session


# def get_session(connection_string):
#     engine = create_engine(connection_string)
#     return Session(bind=engine)


def create_update_user(session, id, name, admin=False):
    instance = session.query(Users).filter_by(id=id).first()
    if instance:
        if not name=='':
            instance.name = name
        instance.admin = admin
    else:
        instance = Users(id=id, name=name, admin=admin)
    instance.postprocessing()
    session.add(instance)
    session.commit()


def get_user(session, id):
    user = None
    instance = session.query(Users).filter_by(id=id).first()
    if instance:
        user = {"id": id, "name": instance.name, "admin": instance.admin}
    return user
