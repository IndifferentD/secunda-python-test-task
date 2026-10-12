from faststream.rabbit import RabbitQueue

PAYMENTS_NEW_QUEUE = RabbitQueue("payments.new", durable=True)
