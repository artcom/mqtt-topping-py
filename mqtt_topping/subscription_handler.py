from dataclasses import dataclass


@dataclass
class SubscriptionHandler:
    qos: int
    callback: any

    def __init__(self, qos: int, callback: any):
        """
        Creates a subscription handler object

        :param qos: Quality of Service level
        :type qos: int
        :param callback: a callback function which gets executed when a message is received
        :type callback: any
        """
        self.qos = qos
        self.callback = callback
