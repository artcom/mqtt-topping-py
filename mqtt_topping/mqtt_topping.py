import json

from mqtt_topping.subscription_handler import SubscriptionHandler
from mqtt_topping.mqtt_client_adaptor import MqttClientAdaptor
from mqtt_topping.paho_client_adaptor import PahoClientAdaptor
from mqtt_topping.invalid_topic_error import InvalidTopicError


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
        Connect to an mqtt server.

        :param host: Host of the mqtt server
        :type host: str
        :param port: Port of the mqtt server
        :type port: int
        """
        self.client_adaptor.connect(host, port)

    def disconnect(self):
        """
        Disconnect from an mqtt server.
        """
        self.client_adaptor.disconnect()

    def subscribe(self, topic: str, callback: any, qos: int = 2):
        """
        Subscribe to a topic
        Throws an InvalidTopicError when the topic is not valid.

        :param topic: the topic to subscribe to
        :type topic: str
        :param callback: a callback function which gets executed when a message is received
        :type callback: any
        :param qos: the Quality of Service level:param qos: Description
        :type qos: int
        """
        self.validate_topic(topic)
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
        Unubscribe a specified callback from a topic.

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
        Unubscribe all callbacks from a topic.

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
        Publish a message with a payload to a specific topic.
        Throws an InvalidTopicError when the topic is not valid.

        :param topic: the topic to publish to
        :type topic: str
        :param payload: the payload to publish
        :type payload: any
        """
        self.validate_topic_for_publish(topic)
        retain = not self.is_event_or_command(topic)
        payload = json.dumps(payload).encode()
        self.client_adaptor.publish(topic, payload, qos=2, retain=retain)

    def is_event_or_command(self, topic: str) -> bool:
        """
        Returns true when a given topic is an event or a command.

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
        Returns true if the given chat is uppercase.

        :param char: the char to inspect
        :type char: str
        :return: true, if the char is uppercase
        :rtype: bool
        """
        return 'A' <= char <= 'Z'

    def on_message(self, topic: str, payload: any):
        """
        Handles the reception of a message.

        :param topic: the topic the message was received under
        :type topic: str
        :param payload: the payload of the received message
        :type payload: any
        """
        if topic in self.subscriptions:
            self.process_handlers_for_topic(topic, topic, payload)

        for subscription_topic in self.subscriptions:
            if "+" not in subscription_topic and "#" not in subscription_topic:
                continue

            if self.match_topic(topic, subscription_topic) is True:
                self.process_handlers_for_topic(
                    subscription_topic, topic, payload)

    def validate_topic(self, topic):
        """
        Validates a topic.
        Throws an InvalidTopicError when the topic is not valid.

        :param topic: the topic to validate
        :type topic: str
        """
        if len(topic) == 0:
            raise InvalidTopicError("topic must be a non-empty string")

        if "#" in topic and topic[-1] != "#" and topic != "#":
            raise InvalidTopicError(
                "wildcard '#' must occupy an entire level and be the last character (e.g., 'foo/#' or '#')")

        parts = topic.split("/")
        for part in parts:
            if "+" in part and part != "+":
                raise InvalidTopicError(
                    "wildcard '+' must occupy an entire level (e.g., 'foo/+/bar')")

            if len(part) == 0 and topic != "/" and topic != "":
                raise InvalidTopicError(
                    "topic must not contain empty levels (e.g., 'foo//bar')")

    def validate_topic_for_publish(self, topic: str):
        """
        Validates a topic for publishing.
        Throws an InvalidTopicError when the topic is not valid.

        :param topic: the topic to validate
        :type topic: str
        """
        if "#" in topic or "+" in topic:
            raise InvalidTopicError(
                "publishing to wildcard topics ('#' or '+') is not allowed")

    def process_handlers_for_topic(self, subscription_topic: str, topic: str, payload: any):
        """
        Executes the associated subscription handlers for the given topic.

        :param subscription_topic: the topic subscribed to
        :type subscription_topic: str
        :param topic: the topic the message was received under
        :type topic: str
        :param payload: the payload of the received message
        :type payload: any
        """
        if len(payload):
            payload = json.loads(payload.decode())
            if subscription_topic not in self.subscriptions:
                return
            for handler in self.subscriptions[subscription_topic]['handlers']:
                handler.callback(topic, payload)

    def match_topic(self, topic: str, subscription: str) -> bool:
        """
        Parses the given subscription topic for wildcards and checks if the given topic matches the wildcard pattern.
        Wildcards can be '+' and '#'.
        Returns True if the subscription contains wildcards and the topic matches the pattern.

        :param topic: the topic to match
        :type topic: str
        :param subscription: the subscription to match the topic to
        :type subscription: str
        :return: true, if the topic matches the wildcard pattern
        :rtype: bool
        """
        if subscription == topic:
            return True

        subscription_levels = subscription.split("/")
        subscription_len = len(subscription_levels)
        topic_levels = topic.split("/")

        has_hash = subscription_levels[-1] == "#"
        has_plus = "+" in subscription
        has_wildcards = has_hash or has_plus

        if not has_wildcards:
            return False

        last_index = (subscription_len - 1) if has_hash else subscription_len

        if last_index > len(topic_levels):
            return False

        for i in range(0, last_index):
            sub = subscription_levels[i]
            top = topic_levels[i]
            if sub != "+" and sub != top:
                return False

        if has_hash:
            return len(topic_levels) >= subscription_len-1

        return len(subscription_levels) == len(topic_levels) and "" not in topic_levels
