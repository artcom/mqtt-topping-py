import json

from mqtt_topping.subscription_handler import SubscriptionHandler
from mqtt_topping.mqtt_client_adaptor import MqttClientAdaptor
from mqtt_topping.paho_client_adaptor import PahoClientAdaptor


class MqttTopping:

    def __init__(self, client_adaptor: MqttClientAdaptor = None):
        """
        Creates an MqttTopping object.

        :param client_adaptor: the client adaptor to use. Defaults to paho.
        :type client_adaptor: MqttClientAdaptor
        """
        if client_adaptor is None:
            client_adaptor = PahoClientAdaptor()

        self.client_adaptor = client_adaptor
        self.client_adaptor.set_mqtt_topping(self)
        self.subscriptions = {}

    def connect(self, host: str, port: int):
        """
        Connect to an mqtt server

        :param host: Host of the mqtt server
        :type host: str
        :param port: Port of the mqtt server
        :type port: int
        """
        self.client_adaptor.connect(host, port)

    def disconnect(self):
        """
        Disconnect from an mqtt server
        """
        self.client_adaptor.disconnect()

    def subscribe(self, topic: str, callback: any, qos: int = 2):
        """
        Subscribe to a topic

        :param topic: the topic to subscribe to
        :type topic: str
        :param callback: a callback function which gets executed when a message is received
        :type callback: any
        :param qos: the Quality of Service level:param qos: Description
        :type qos: int
        """
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

    def refresh_subscriptions(self):
        """
        Re-subscribes to all registered topics. Handlers will stay valid.
        """
        for topic, subscription in self.subscriptions.items():
            handler = subscription['handlers'][0]
            qos = handler.qos
            self.client_adaptor.subscribe(topic, qos=qos)

    def unsubscribe(self, topic: str, callback: any):
        """
        Unubscribe a specified callback from a topic

        :param topic: the topic to unsubscribe from
        :type topic: str
        :param callback: the callback to remove
        :type callback: any
        """
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

    def force_unsubscribe(self, topic: str):
        """
        Unubscribe all callbacks from a topic

        :param topic: the topic to unsubscribe from
        :type topic: str
        """
        if topic not in self.subscriptions:
            return
        subscription = self.subscriptions[topic]
        if subscription is None:
            return

        del self.subscriptions[topic]
        self.client_adaptor.unsubscribe(topic)

    def publish(self, topic: str, payload: any):
        """
        Publish a message with a payload to a specific topic

        :param topic: the topic to publish to
        :type topic: str
        :param payload: the payload to publish
        :type payload: any
        """
        retain = not self.is_event_or_command(topic)
        payload = json.dumps(payload).encode()
        self.client_adaptor.publish(topic, payload, qos=2, retain=retain)

    def is_event_or_command(self, topic: str) -> bool:
        """
        Returns true when a given topic is an event or a command

        :param topic: the topic to inspect
        :type topic: str
        :return: true, if the topic is an event or a command
        :rtype: bool
        """
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
        """
        Returns true if the given chat is uppercase

        :param char: the char to inspect
        :type char: str
        :return: true, of the char is uppercase
        :rtype: bool
        """
        return 'A' <= char <= 'Z'

    def on_message(self, topic: str, payload: any):
        """
        Handles the reception of a message

        :param topic: the topic the message was received under
        :type topic: str
        :param payload: the payload of the received message
        :type payload: any
        """
        if topic in self.subscriptions:
            self._process_handlers_for_topic(topic, payload)

        for subscription_topic in self.subscriptions:
            if "+" not in subscription_topic and "#" not in subscription_topic:
                continue

            if self._match_topic(topic, subscription_topic) is True:
                self._process_handlers_for_topic(subscription_topic, payload)

    def _process_handlers_for_topic(self, topic: str, payload: any):
        """
        Executes the associated subscription handlers if the payload is valid.

        :param topic: the topic the message was received under
        :type topic: str
        :param payload: the payload of the received message
        :type payload: any
        """
        if len(payload):
            payload = json.loads(payload.decode())
            for handler in self.subscriptions[topic]['handlers']:
                handler.callback(topic, payload)

    def _match_topic(self, topic: str, subscription: str) -> bool:
        """
        Parses the given subscription topic for wildcards and checks if the given topic matches the wildcard pattern.
        Wildcards can be '+' and '#'.
        Returns True if the subscription contains wildcards and the topic matches the pattern.

        :param topic: the topic the message was received under
        :type topic: str
        :param payload: the payload of the received message
        :type payload: any
        :return: true, if the topic matches the wildcard pattern
        :rtype: bool
        """
        toplevels = topic.split("/")
        sublevels = subscription.split("/")
        sublen = len(sublevels)

        has_hash = sublevels[-1] == "#"
        has_plus = "+" in subscription
        has_wildcards = has_hash or has_plus

        comparison_end_index = (sublen - 1) if has_hash else sublen
        if subscription == topic:
            return True

        if not has_wildcards:
            return False

        if comparison_end_index > len(toplevels):
            return False

        for i in range(0, comparison_end_index):
            sub = sublevels[i]
            top = toplevels[i]
            if sub != "+" and sub != top:
                return False

        if has_hash:
            return len(toplevels) >= sublen-1

        return len(sublevels) == len(toplevels) and "" not in toplevels
