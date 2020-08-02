import os
import time
import socket
import itertools
import functools
from kombu import connection

from config import Config
from rabbitmq_entity import (TopicConsumer,
                             DirectConsumer,
                             TopicPublisher,
                             DirectPublisher)


class Connection(object):
    pool = None

    def __init__(self, connection_url=None):
        self.consumers = []
        self.root_path = os.getcwd()
        self.c = Config(self.root_path)
        self.c.from_pyfile("config")
        self.connection_url = connection_url if connection_url \
            else self.c.get("RABBITMQ_CONNECTION_URL")
        if not self.connection_url:
            raise Exception("connection url can't be None")
        self.reconnect()

    def _connect(self):
        try:
            self.connection = connection.Connection(self.connection_url)
            self.connection_errors = self.connection.connection_errors
            self.channel = self.connection.channel()
            self.connection.connect()
            self.consumer_num = itertools.count(1)
            for consumer in self.consumers:
                consumer.reconnect(self.channel)
        except Exception as e:
            print("connect broker caught an exception:%s" % str(e))
            raise e

    def reconnect(self, timeout=None):

        attempt = 0
        while True:
            try:
                self._connect()
                return
            except (IOError, self.connection_errors) as e:
                pass
            except Exception as e:
                if 'timeout' not in str(e):
                    raise
            attempt += 1
            if timeout is None:
                time.sleep(2)
            else:
                time.sleep(timeout)

    def ensure(self, error_callback, method, *args, **kwargs):
        while True:
            try:
                return method(*args, **kwargs)
            except (self.connection_errors, socket.timeout, IOError) as e:
                if error_callback:
                    error_callback(e)
            except Exception as e:
                if 'timeout' not in str(e):
                    raise
                if error_callback:
                    error_callback(e)
            self.reconnect()

    def declare_consumer(self, consumer_cls, target, callback):

        def _connect_error(exc):
            print("caught an error %s" % str(exc))

        def _declare_consumer():
            consumer = consumer_cls(self.channel, target, callback)
            self.consumer_num.next()
            self.consumers.append(consumer)
            return consumer

        return self.ensure(_connect_error, _declare_consumer)

    def iterconsume(self, limit=None, timeout=None):
        """Return an iterator that will consume from all queues/consumers."""

        def _error_callback(exc):
            if isinstance(exc, socket.timeout):
                print('Timed out waiting for RPC response: %s' % str(exc))
                raise exc
            else:
                print('Failed to consume message from queue: %s' % str(exc))
                self.do_consume = True

        def _consume():
            queues_head = self.consumers[:-1]
            queues_tail = self.consumers[-1]
            for queue in queues_head:
                queue.consume(nowait=True)
            queues_tail.consume(nowait=False)
            self.do_consume = False
            return self.connection.drain_events(timeout=timeout)

        for iteration in itertools.count(0):
            if limit and iteration >= limit:
                raise StopIteration
            yield self.ensure(_error_callback, _consume)

    def publisher_send(self, cls, target, msg, timeout=None):
        """Send to a publisher based on the publisher class."""

        def _error_callback(exc):
            print("Failed to publish message to topic "
                  "'%s" % str(exc))

        def _publish():
            publisher = cls(self.channel, target)
            publisher.publish(msg, timeout)

        self.ensure(_error_callback, _publish)

    def declare_direct_consumer(self, target, callback):
        self.declare_consumer(DirectConsumer, target, callback)

    def declare_topic_consumer(self, topic, callback=None, queue_name=None,
                               exchange_name=None, ack_on_error=True):
        self.declare_consumer(functools.partial(TopicConsumer,
                                                name=queue_name,
                                                exchange_name=exchange_name,
                                                ack_on_error=ack_on_error,
                                                ),
                              topic, callback)

    def direct_send(self, target, msg, timeout=None):
        self.publisher_send(DirectPublisher, target, msg, timeout)

    def topic_send(self, target, msg, timeout=None):
        self.publisher_send(TopicPublisher, target, msg, timeout)

    def consume(self, limit=None, timeout=None):
        it = self.iterconsume(limit=limit, timeout=timeout)
        while True:
            try:
                it.next()
            except StopIteration:
                return

    def close(self):
        self.connection.release()
        self.connection = None

    def reset(self):
        self.channel.close()
        self.channel = self.connection.channel()
        self.consumers = []
