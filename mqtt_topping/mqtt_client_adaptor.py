import weakref

from mqtt_topping.security_config import SecurityConfig


class MqttClientAdaptor:

    def __init__(self):
        """
        Abstract base class for implementations client adaptors.
        """
        self.client = None
        self._mqtt_topping = None

    def connect(self, host: str, port: int, client_id: str, on_connect: any = None, on_connect_fail: any = None, on_disconnect: any = None, security_config: SecurityConfig = None):
        """
        Connect to an mqtt server

        :param host: Host of the mqtt server
        :type host: str
        :param port: Port of the mqtt server
        :type port: int
        :param client_id: Client id
        :type client_id: str
        :param on_connect: callback for successful connection
        :type on_connect: any
        :param on_connect_fail: callback for failed connection
        :type on_connect_fail: any
        :param on_disconnect: callback for disconnect
        :type on_disconnect: any
        :param security_config: configuration for login and encryption
        :type security_config: SecurityConfig
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
