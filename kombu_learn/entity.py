from kombu import Queue, Exchange
from kombu.messaging import Producer

__all__ = ['Target', 'DirectPublisher', 'TopicPublisher', 'DirectConsumer', 'TopicConsumer']


class Target(object):

    def __init__(self, exchange_name, routing_key, queue_name):
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.queue_name = queue_name


class BasePublisher(object):
    EXCHANGE_TYPE = None

    def __init__(self, conn, target):
        self.conn = conn
        self.target = target
        self.channel = conn.channel()

    def publish(self, data):
        p = Producer(channel=self.channel,
                     exchange=Exchange(self.target.exchange_name, type=self.EXCHANGE_TYPE),
                     routing_key=self.target.routing_key)
        p.publish(data)


class DirectPublisher(BasePublisher):
    EXCHANGE_TYPE = 'direct'


class TopicPublisher(BasePublisher):
    EXCHANGE_TYPE = 'topic'


class BaseConsumer(object):
    EXCHANGE_TYPE = None

    def __init__(self, conn, target):
        self.conn = conn
        self.target = target
        self.channel = conn.channel()

    def consume(self, callback):
        q = Queue(self.target.queue_name,
                  exchange=Exchange(self.target.exchange_name, type=self.EXCHANGE_TYPE),
                  routing_key=self.target.routing_key,
                  channel=self.channel)
        q.declare()
        q.consume(callback=callback)

    def get_channel(self):
        return self.channel

    def run(self):
        while True:
            try:
                self.conn.drain_events()
            except Exception as e:
                print("stop:%s" % str(e))
                break


class DirectConsumer(BaseConsumer):
    EXCHANGE_TYPE = 'direct'


class TopicConsumer(BaseConsumer):
    EXCHANGE_TYPE = 'topic'
