from rabbitmq_entity import Target
from connection import cast

target = Target("task_exchange", "task", "task_queue")
cast(target, "test")
