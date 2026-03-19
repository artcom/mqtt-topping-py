from dataclasses import dataclass


@dataclass
class SubscriptionHandler:
    qos: int
    callback: any

    def __init__(self, parse: bool, qos: int, callback: any):
        """
        Creates a subscription handler object.

        :param parse: True if the parsed payload is preferred
        :type parse: bool
        :param qos: Quality of Service level
        :type qos: int
        :param callback: a callback function which gets executed when a message is received
        :type callback: any
        """
        self.parse = parse
        self.qos = qos
        self.callback = callback
