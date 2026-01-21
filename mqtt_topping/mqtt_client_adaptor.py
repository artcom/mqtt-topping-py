import weakref


class MqttClientAdaptor(object):

    def __init__(self):
        """
        Abstract base class for implementations client adaptors.
        """
        self.client = None
        self._mqtt_topping = None

    def connect(self, host: str, port: int):
        """
        Connect to an mqtt server

        :param host: Host of the mqtt server
        :type host: str
        :param port: Port of the mqtt server
        :type port: int
        """
        return

    def disconnect(self):
        """
        Disconnect from an mqtt server
        """
        return

    def set_mqtt_topping(self, mqtt_topping):
        """
        Sets a weak reference to the parent MqttTopping object

        :param mqtt_topping: the parent MqttTopping object
        """
        self._mqtt_topping = weakref.ref(mqtt_topping)

    def subscribe(self, topic: str, qos: int = 2):
        """
        Subscribe to a topic

        :param topic: the topic to subscribe to
        :type topic: str
        :param qos: the Quality of Service level
        :type topic: int
        """
        return

    def unsubscribe(self, topic: str):
        """
        Unubscribe to a topic

        :param topic: the topic to unsubscribe from
        :type topic: str
        """
        return

    def publish(self, topic: str, payload: any, qos: int = 2, retain: bool = True):
        """
        Publish a message with a payload to a specific topic

        :param topic: the topic to publish to
        :type topic: str
        :param payload: the payload to publish
        :type payload: any
        :param qos: the Quality of Service level
        :type qos: int
        :param retain: indicates whether the message should be retained
        :type retain: bool
        """
        return

    def on_message(self, topic: str, payload: any):
        """
        Handles the reception of a message

        :param topic: the topic the message was received under
        :type topic: str
        :param payload: the payload of the received message
        :type payload: any
        """
        self._mqtt_topping().on_message(topic, payload)
