from oslo_config import cfg
from oslo_db import api as db_api


_BACKEND_MAPPING = {'sqlalchemy': 'oslo_db_learn.db.sqlachemy.api'}


IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING)


def configure(conf):
    IMPL.configure(conf)

def get_engine():
    return IMPL.get_engine()


def get_session():
    return IMPL.get_session()

# CRUD operations
def create_company(data):
    return IMPL.create_company(data)

