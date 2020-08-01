from rabbitmq_entity import Target
from rabbitmq_impl import Connection

target = Target("task_exchange", "task", "task_queue")
conn = Connection()


def process_data(message):
    msg = conn.channel.message_to_python(message)
    print(msg.body)
    msg.ack()


conn.declare_direct_consumer(target, process_data)
conn.consume()