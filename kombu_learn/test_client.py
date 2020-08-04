from rabbitmq_entity import Target
from connection import call, cast

target = Target("task_exchange", "task", "task_queue")
cast(target, "test")
print("######################")
print(call(target, "test"))
