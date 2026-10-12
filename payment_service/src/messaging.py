from uuid import UUID

from faststream.rabbit import QueueType, RabbitBroker, RabbitQueue
from pydantic import BaseModel


class PaymentMessage(BaseModel):
    payment_id: UUID


PAYMENTS_DEAD_QUEUE = RabbitQueue("payments.dead", durable=True)
PAYMENTS_NEW_QUEUE = RabbitQueue(
    "payments.new",
    durable=True,
    queue_type=QueueType.QUORUM,
    arguments={
        "x-delivery-limit": 3,
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": PAYMENTS_DEAD_QUEUE.name,
    },
)


async def declare_payment_queues(broker: RabbitBroker) -> None:
    await broker.declare_queue(PAYMENTS_DEAD_QUEUE)
    await broker.declare_queue(PAYMENTS_NEW_QUEUE)
