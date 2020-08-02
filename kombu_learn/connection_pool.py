# _-_coding:utf-8 _-_
import abc
import os
from config import Config
import collections
import threading
import uuid
from rabbitmq_impl import Connection

MSG_ID = 'msg_id'


class Pool(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, max_size=10):
        super(Pool, self).__init__()

        self.max_size = max_size
        self._current_size = 0
        self._cond = threading.Condition()

        self._items = collections.deque()

    def put(self, item):
        """
        使用完成后，对象放入池中
        """
        with self._cond:
            self._items.appendleft(item)
            self._cond.notify()

    def get(self):

        with self._cond:
            while True:
                try:
                    # 如果池中存在，则返回
                    return self._items.popleft()
                except IndexError:
                    pass

                if self._current_size < self.max_size:
                    self._current_size += 1
                    break
                # 创建已经到最大数量对象，但是池中没有连接对象时，等待1秒
                self._cond.wait(timeout=1)
        # 不存在则创建
        with self._cond:
            try:
                return self.create()
            except Exception:
                with self._cond:
                    self._current_size -= 1
                raise

    def iter_free(self):

        with self._cond:
            while True:
                try:
                    yield self._items.popleft()
                except IndexError:
                    break

    @abc.abstractmethod
    def create(self):
        """创建连接对象"""


class ConnectionPool(Pool):
    def __init__(self, connection_cls):
        self.connection_cls = connection_cls
        self.root_path = os.getcwd()
        self.c = Config(self.root_path)
        self.c.from_pyfile("config")
        super(ConnectionPool, self).__init__(self.c.get("CONNECTION_POLL_SIZE")
                                             if self.c.get("CONNECTION_POLL_SIZE")
                                             else 100)

    def create(self):
        return self.connection_cls()

    def close(self):
        for item in self.iter_free():
            item.close()


_pool_create_lock = threading.Lock()


def get_connection_pool(connection_cls):
    with _pool_create_lock:
        if not connection_cls.pool:
            connection_cls.pool = ConnectionPool(connection_cls)
        return connection_cls.pool


class ConnectionContext(object):

    def __init__(self, connection_pool, pooled=True):

        self.connection = None
        self.connection_pool = connection_pool

        if pooled:
            self.connection = self.connection_pool.get()
        else:
            self.connection = self.connection_pool.connection_cls()

        self.pooled = pooled

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._done()

    def _done(self):

        if self.connection:
            if self.pooled:
                self.connection.reset()
                self.connection_pool.put(self.connection)
            else:
                try:
                    self.connection.close()
                except Exception:
                    pass

    def __getattr__(self, key):

        if self.connection:
            return getattr(self.connection, key)
        else:
            raise Exception("connection is None")


def _add_msg_id(msg):
    unique_id = uuid.uuid4().hex
    msg.update({MSG_ID: unique_id})


def topic_cast(target, msg, timeout=None):
    _add_msg_id(msg)
    with ConnectionContext(get_connection_pool(Connection)) as conn:
        conn.topic_send(target, msg, timeout)


def direct_cast(target, msg, timeout=None):
    _add_msg_id(msg)
    with ConnectionContext(get_connection_pool(Connection)) as conn:
        conn.direct_send(target, msg, timeout)
