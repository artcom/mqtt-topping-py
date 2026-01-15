from dataclasses import dataclass


@dataclass
class SubscriptionHandler:
    qos: int
    callback: any

    def __init__(self, qos: int, callback: any):
        self.qos = qos
        self.callback = callback
