from oslo_db.sqlalchemy import models
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import session as orm_session
import six

try:
    import api as db_api
except Exception as e:
    print e
DeclarativeBase = declarative_base()

def get_session():
    return db_api.get_session()

class HeatBase(models.ModelBase, models.TimestampMixin):
    """Base class for Heat Models."""
    __table_args__ = {'mysql_engine': 'InnoDB'}

    def expire(self, session=None, attrs=None):
        """Expire this object ()."""
        if not session:
            session = orm_session.Session.object_session(self)
            if not session:
                session = get_session()
        session.expire(self, attrs)

    def refresh(self, session=None, attrs=None):
        """Refresh this object."""
        if not session:
            session = orm_session.Session.object_session(self)
            if not session:
                session = get_session()
        session.refresh(self, attrs)
    def delete(self, session=None):
        """Delete this object."""
        if not session:
            session = orm_session.Session.object_session(self)
            if not session:
                session = get_session()
        session.begin()
        session.delete(self)
        session.commit()

    def update_and_save(self, values, session=None):
        if not session:
            session = orm_session.Session.object_session(self)
            if not session:
                session = get_session()
        session.begin()
        for k, v in six.iteritems(values):
            setattr(self, k, v)
        session.commit()


class Product(HeatBase, DeclarativeBase):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False, index=True)
    price = Column(Integer)

    company_id = Column(Integer, ForeignKey('companies.id'), index=True)
    company = relationship("Company", back_populates="products")


class Company(HeatBase, DeclarativeBase):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False, index=True)

    products = relationship("Product", back_populates="company")
