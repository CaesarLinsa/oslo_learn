from listener import AMQPListener


class Server(object):
    def __init__(self, connection, target, endpoints):
        self.conn = connection
        self.listener = AMQPListener(self.conn, target)
        self.target = target
        self.endpoints = endpoints
        self.running = False

    def start(self):
        self.conn.declare_topic_consumer(self.target, self.listener)
        self.running = True
        while self.running:
            self._dispatch(self.listener.poll())

    def stop(self):
        self.running = False

    def _dispatch(self, msg_handler):
        for endpoint in self.endpoints:
            message = msg_handler.msg
            method = message.get("method")
            args = message.get("args", {})
            if hasattr(endpoint, method):
                return self.__dispatch(endpoint, method, args)

    def __dispatch(self, endpoint, method, args):
        new_args = dict()
        for argname, arg in args.iteritems():
            new_args[argname] = arg
        result = getattr(endpoint, method)(**new_args)
        return result
