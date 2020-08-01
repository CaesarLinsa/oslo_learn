from rabbitmq_entity import Target
from rabbitmq_impl import Connection


target = Target("task_exchange", "task", "task_queue")
conn = Connection()
conn.direct_send(target, "ni hao ma")