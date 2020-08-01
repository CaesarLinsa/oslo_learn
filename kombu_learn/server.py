from kombu import Connection
from entity import Target, DirectConsumer

target = Target("task_exchange", "task", "task_queue")
conn = Connection("amqp://guest:guest@196.168.1.120:5672/")
c = DirectConsumer(conn, target)


def process_data(message):
    msg = c.get_channel().message_to_python(message)
    print(msg.body)
    msg.ack()


c.consume(process_data)
c.run()

