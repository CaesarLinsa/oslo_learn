import sys

from oslo_config import cfg
from oslo_db.sqlalchemy import enginefacade
from oslo_db import options
from oslo_db_learn.db.sqlachemy import models
from oslo_db.sqlalchemy import session as db_session

storage_context_manager = enginefacade.transaction_context()

_facade = None

CONF = cfg.CONF


class RecordNotFoundException(Exception):
    pass

def get_facade():
    global _facade
    if not _facade:
        _facade = db_session.EngineFacade.from_config(CONF)

    if not _facade:
        _facade = db_session.EngineFacade.from_config(CONF)

    return _facade


def configure(conf):
    config = {'connection':'mysql+pymysql://root:123@localhost:3306/test',}
    config.update(conf)

    options.set_defaults(cfg.CONF, connection=config['connection'])
    storage_context_manager.configure(**config)
    models.DeclarativeBase.metadata.create_all(get_engine())
    print storage_context_manager


def get_backend():
    return sys.modules[__name__]


get_engine = lambda: get_facade().get_engine()
get_session = lambda: get_facade().get_session()

def create_company(data):
    company = models.Company()
    company.update(data)
    if 'id' in data:
        del data['id']
    company.save(get_session())
    return company
