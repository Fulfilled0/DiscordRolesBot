import configparser
from contextlib import contextmanager
import sqlalchemy
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Configure tables
Base = declarative_base()


class Settings(Base):
    __tablename__ = "settings"

    key = Column(Text, primary_key=True)
    value = Column(Text)


class UserRoles(Base):
    __tablename__ = "user roles"

    id = Column(Integer, primary_key=True)
    role_id = Column(Text)
    user_id = Column(Text)
    user_name = Column(Text)
    admin_id = Column(Text)
    admin_name = Column(Text)
    mins_left = Column(Integer)


# Read from config file
parser = configparser.ConfigParser()
parser.read("config.cfg")

# Create database
engine = sqlalchemy.create_engine(parser["database"]["connection_string"])
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
