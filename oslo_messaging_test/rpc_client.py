from oslo.config import cfg
import oslo.messaging
import sys

argv = sys.argv
CONF=cfg.CONF
CONF(argv[1:])

transport = oslo.messaging.get_transport(CONF)
target = oslo.messaging.Target(topic="rpc", server="server")
RPCClient = oslo.messaging.RPCClient(transport, target)
RPCClient.call({}, "test")
