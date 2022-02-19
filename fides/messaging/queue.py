from typing import Callable


class Queue:
    """
    Wrapper around actual implementation of queue.

    Central point used for communication with the network layer and another peers.
    """

    def send(self, serialized_data: str):
        """Sends serialized data to the queue."""
        raise NotImplemented('This is interface. Use implementation.')

    def listen(self, on_message: Callable[[str], None]):
        """Starts listening, executes :param: on_message when new message arrives.
        This method is not blocking.
        """
        raise NotImplemented('This is interface. Use implementation.')


class RedisDuplexQueue(Queue):
    """
    Implementation of Queue interface that uses single Redis queue
    for duplex communication (sending and listening on the same channel).
    """

    def __init__(self, queue):
        self.__queue = queue

    def send(self, serialized_data: str):
        # TODO: [!] check correct method for the queue
        self.__queue.send(serialized_data)

    def listen(self, on_message: Callable[[str], None]):
        # TODO: [!] check correct method for the queue
        self.__queue.listen(on_message)


class RedisSimplexQueue(Queue):
    """
    Implementation of Queue interface that uses two Redis queues.
    One for sending data and one for listening.
    """

    def __init__(self, send_queue, receive_queue):
        self.__send_queue = send_queue
        self.__receive_queue = receive_queue

    def send(self, serialized_data: str):
        # TODO: [!] check correct method for the queue
        self.__send_queue.send(serialized_data)

    def listen(self, on_message: Callable[[str], None]):
        # TODO: [!] check correct method for the queue
        self.__receive_queue.listen(on_message)
