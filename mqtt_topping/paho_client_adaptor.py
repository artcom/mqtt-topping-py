import threading
import paho.mqtt.client as paho


from mqtt_topping.mqtt_client_adaptor import MqttClientAdaptor
from mqtt_topping.security_config import SecurityConfig


class PahoClientAdaptor(MqttClientAdaptor):

    def __init__(self):
        """
        Creates a client adaptor for Paho mqtt client class.

        :param client: Paho mqttclient instance
        """
        super(PahoClientAdaptor, self).__init__()
        self.client = None
        self.mqtt_thread = None
        self._should_terminate = False

    def connect(self, host: str, port: int, client_id: str, on_connect: any = None, on_connect_fail: any = None, on_disconnect: any = None, security_config: SecurityConfig = None):
        self.client = paho.Client(
            paho.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            clean_session=True,
        )
        if security_config:
            if security_config.use_tls:
                self.client.tls_set(certfile=security_config.certfile,
                                    keyfile=security_config.keyfile,
                                    cert_reqs=security_config.cert_reqs)
            self.client.username_pw_set(username=security_config.username,
                                        password=security_config.password)

        def on_message(_, __, msg):
            self.on_message(msg.topic, msg.payload)

        def _on_disconnect(one, two, three, four, rc):
            if self._should_terminate:
                self.mqtt_thread.join()
            on_disconnect(one, two, three, four, rc)

        def run_mqtt():
            self.client.on_connect = on_connect
            self.client.on_connect_fail = on_connect_fail
            self.client.on_disconnect = _on_disconnect
            self.client.on_message = on_message
            self.client.connect(host, port)
            self.client.loop_forever()

        self.mqtt_thread = threading.Thread(target=run_mqtt)
        self.mqtt_thread.start()

    def disconnect(self):
        self._should_terminate = True
        self.client.disconnect()

    def subscribe(self, topic: str, qos: int = 2):
        self.client.subscribe(topic, qos=qos)

    def unsubscribe(self, topic: str):
        self.client.unsubscribe(topic)

    def publish(self, topic: str, payload: any, qos: int = 2, retain: bool = True):
        self.client.publish(topic, payload, qos=qos, retain=retain)
