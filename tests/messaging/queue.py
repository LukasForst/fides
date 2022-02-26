from typing import Callable

from fides.messaging.queue import Queue


class TestQueue(Queue):

    def __init__(self):
        def ex(x):
            raise Exception(f'Not set! Called with data: {x}.')

        self.on_send_called: Callable[[str], None] = ex
        self.send_message: Callable[[str], None] = ex

    def send(self, serialized_data: str, **argv):
        self.on_send_called(serialized_data)

    def listen(self, on_message: Callable[[str], None], **argv):
        self.send_message = on_message
