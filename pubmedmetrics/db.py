import os
import logging
from contextlib import contextmanager
from sqlite3 import dbapi2 as sqlite
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.sqlite import (BLOB, BOOLEAN, CHAR, DATE, DATETIME,
    DECIMAL, FLOAT, INTEGER, NUMERIC, SMALLINT, TEXT, TIME, TIMESTAMP,
    VARCHAR)

logger = logging.getLogger('db')
engine = create_engine("sqlite+pysqlite:///pubmed.db",
    execution_options={"sqlite_raw_colnames": True}, module=sqlite)
Session = sessionmaker(bind=engine)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as ex:
        logger.error(ex)
        session.rollback()
        raise
    finally:
        session.close()

Base = declarative_base()
class PubMed(Base):
    __tablename__ = 'pubmed'

    pmid = Column(String(64), primary_key=True)
    title = Column(String(256), nullable=False)
    authors = Column(String(256))
    summary = Column(String(256))
    summary_detail = Column(String(256))
    link = Column(String(256))
    tags = Column(String(256))
    key = Column(String(256))
    create_dt = Column(DATETIME)

    def __repr__(self):
        return "<PubMed(pmid=%s,title=%s)>" % (self.pmid, self.title)

class Metric(Base):
    __tablename__ = 'metric'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    pmid = Column(String(64))
    altmetric = Column(FLOAT)
    create_dt = Column(DATETIME)

    def __repr__(self):
        return "<Metric(pmid=%s, metric=%s)>" % (self.pmid, self.altmetric)

Base.metadata.create_all(engine)

if __name__ == '__main__':
    import datetime as dt
    Base.metadata.create_all(engine)
    with session_scope() as session:
        pubmed = PubMed(
            pmid='000000',
            title='title',
            authors='authors',
            create_dt=dt.datetime.now()
        )
        session.merge(pubmed)
        pubmed = PubMed(
            pmid='000000',
            title='title',
            authors='authors2',
            create_dt=dt.datetime.now()
        )
        session.merge(pubmed)
