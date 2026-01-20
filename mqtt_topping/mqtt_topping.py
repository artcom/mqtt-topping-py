import json

from mqtt_topping.subscription_handler import SubscriptionHandler
from mqtt_topping.mqtt_client_adaptor import MqttClientAdaptor
from mqtt_topping.paho_client_adaptor import PahoClientAdaptor


class MqttTopping:

    def __init__(self, client_adaptor: MqttClientAdaptor = None):
        if client_adaptor is None:
            client_adaptor = PahoClientAdaptor()

        self.client_adaptor = client_adaptor
        self.client_adaptor.set_mqtt_topping(self)
        self.subscriptions = {}

    def connect(self, host, port):
        self.client_adaptor.connect(host, port)

    def disconnect(self):
        self.client_adaptor.disconnect()

    def subscribe(self, topic: str, callback, qos=2):
        needs_subscribe = False
        if topic not in self.subscriptions:
            self.subscriptions[topic] = {'handlers': []}
            needs_subscribe = True

        handler = next(
            (handler for handler in self.subscriptions[topic]
             ['handlers'] if handler.callback == callback),
            None
        )
        if handler:
            handler.qos = qos
        else:
            handler = SubscriptionHandler(qos, callback)
            self.subscriptions[topic]['handlers'].append(handler)

        if needs_subscribe:
            self.client_adaptor.subscribe(topic, qos=qos)

    def unsubscribe(self, topic: str, callback: any):
        if topic not in self.subscriptions:
            return
        subscription = self.subscriptions[topic]
        if subscription is None:
            return

        stored_handlers = subscription['handlers']
        result = filter(
            lambda handler: handler.callback != callback, subscription['handlers'])

        remaining_handlers = list(result)
        subscription['handlers'] = remaining_handlers

        if len(remaining_handlers) == len(stored_handlers):
            return

        if len(remaining_handlers) == 0:
            del self.subscriptions[topic]
            self.client_adaptor.unsubscribe(topic)

    def publish(self, topic: str, payload: any):
        retain = not self.is_event_or_command(topic)
        payload = json.dumps(payload).encode()
        self.client_adaptor.publish(topic, payload, qos=2, retain=retain)

    def is_event_or_command(self, topic: str) -> bool:
        if topic is None or not isinstance(topic, str):
            return False

        last_slash_index = topic.rfind("/")
        last_topic_level = topic[last_slash_index +
                                 1:] if last_slash_index >= 0 else topic

        if len(last_topic_level) <= 2:
            return False

        prefix = last_topic_level[:2]
        return (prefix == "on" or prefix == "do") and self.is_upper_case(last_topic_level[2:3])

    def is_upper_case(self, char: str) -> bool:
        return 'A' <= char <= 'Z'

    def on_message(self, topic, payload):
        if topic not in self.subscriptions:
            return
        if len(payload):
            payload = json.loads(payload.decode())
            for handler in self.subscriptions[topic]['handlers']:
                handler.callback(topic, payload)
