from mqtt_topping.mqtt_client_adaptor import MqttClientAdaptor
from mqtt_topping.security_config import SecurityConfig


class TouchDesignerClientAdaptor(MqttClientAdaptor):

    def __init__(self, client):
        """
        Creates a client adaptor for TouchDesigner mqttclient class.

        :param client: TouchDesigner mqttclient instance
        """
        super(TouchDesignerClientAdaptor, self).__init__()
        self.client = client

    def connect(self, host: str, port: int, client_id: str, on_connect: any = None, on_connect_fail: any = None, on_disconnect: any = None, security_config: SecurityConfig = None):
        """
        Activates the TouchDesigner mqttclient DAT.

        Note: unlike other adaptors, host, port, client_id, the on_connect/on_connect_fail/
        on_disconnect callbacks and security_config are not used here. The mqttclient DAT is
        configured exclusively through its own TouchDesigner parameters (broker address,
        client id, username/password, TLS); connection lifecycle callbacks are delivered via
        the DAT's own callback DAT rather than through the arguments passed to this method.
        """
        self.client.par.active = True
        self.client.par.reconnect.pulse()

    def disconnect(self):
        self.client.par.active = False

    def is_connected(self) -> bool:
        return bool(self.client.par.active)

    def subscribe(self, topic: str, qos: int = 2):
        self.client.subscribe(topic, qos=qos)

    def unsubscribe(self, topic: str):
        self.client.unsubscribe(topic)

    def publish(self, topic: str, payload: any, qos: int = 2, retain: bool = True):
        self.client.publish(topic, payload, qos=qos, retain=retain)
