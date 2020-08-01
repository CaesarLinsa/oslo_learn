from entity import DirectPublisher, Target
from kombu import Connection


target = Target("task_exchange", "task", "task_queue")
conn = Connection("amqp://guest:guest@196.168.1.120:5672//")
m = DirectPublisher(conn, target)
m.publish("hello world")