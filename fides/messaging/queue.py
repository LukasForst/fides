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
