from rabbitmq_entity import Target
from connection_pool import direct_cast


target = Target("task_exchange", "task", "task_queue")
direct_cast(target, {"data":"ni hao ma"})