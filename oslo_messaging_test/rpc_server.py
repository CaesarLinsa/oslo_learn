from oslo.config import cfg
import oslo.messaging
import sys
import time

argv = sys.argv

cfg.CONF(argv[1:])


class TestEndPoint():

    def test(self,ctxt):
        return "from server"


endpoints = [TestEndPoint(), ]

tansport = oslo.messaging.get_transport(cfg.CONF)
target = oslo.messaging.Target(topic="rpc", server="server")
server = oslo.messaging.get_rpc_server(tansport, target, endpoints, executor="blocking")

server.start()

while True:
    time.sleep(1)

server.stop()

server.wait()
