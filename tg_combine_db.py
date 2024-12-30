from keys import ADMIN_ID, ADMIN_NAME
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
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False)
    admin = Column(Boolean, nullable=False)
    blocked = Column(Boolean, nullable=False)

    def __str__(self):
        return f"name: {self.name}; id: {self.id}"

    def postprocessing(self):
        pass


def create_database(connection_string):
    engine = create_engine(connection_string, echo=True)
    Base.metadata.create_all(engine)
    session = Session(bind=engine)
    get_or_create(
        session, Users, True, id=ADMIN_ID, name=ADMIN_NAME, admin=True, blocked=False
    )
    return session


def get_or_create(session, model, update, **kwargs):
    instance = session.query(model).filter_by(id=kwargs["id"]).first()

    if instance:
        logger.debug(f"FOUND in the database - type: {model}; {instance}")
        if update:
            for key, value in kwargs.items():
                setattr(instance, key, value)
                instance.postprocessing()
            session.add(instance)
            session.commit()
            logger.debug(f"UPDATE - type: {model}; {instance}")
    else:
        instance = model(**kwargs)
        instance.postprocessing()
        session.add(instance)
        session.commit()
        logger.debug(f"CREATED - type: {model}; {instance}")

    return instance


def get_user(session, id):
    return session.query(Users).filter_by(id=id).first()

def user_is_valid(session, id):
    db_user = get_user(session, id)
    if db_user == None:
        return False
    else:
        return not db_user.blocked

def user_is_admin(session, id):
    db_user = get_user(session, id)
    if db_user == None:
        return False
    else:
        return not db_user.blocked and db_user.admin
    
    
def user_is_blocked(session, id):
    db_user = get_user(session, id)
    if db_user == None:
        return False
    else:
        return db_user.blocked    