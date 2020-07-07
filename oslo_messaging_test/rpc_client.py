from oslo.config import cfg
import oslo.messaging
import sys

argv = sys.argv
cfg.CONF(argv[1:])

transport = oslo.messaging.get_transport(cfg.CONF)
target = oslo.messaging.Target(topic="rpc", server="server")
RPCClient = oslo.messaging.RPCClient(transport, target)
RPCClient.call({}, "test")
