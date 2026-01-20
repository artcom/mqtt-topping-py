import threading
import paho.mqtt.client as paho


from mqtt_topping.mqtt_client_adaptor import MqttClientAdaptor


class PahoClientAdaptor(MqttClientAdaptor):

    def __init__(self):
        super(PahoClientAdaptor, self).__init__()
        self.client = paho.Client(paho.CallbackAPIVersion.VERSION2)
        self.mqtt_thread = None

    def connect(self, host, port):

        def on_message(_, topic, msg):
            self.on_message(topic, msg)

        def run_mqtt():
            self.client.on_message = on_message
            self.client.connect(host, port)
            self.client.loop_start()

        self.mqtt_thread = threading.Thread(target=run_mqtt)
        self.mqtt_thread.start()

    def disconnect(self):
        self.client.loop_stop()
        self.mqtt_thread.join()

    def subscribe(self, topic: str, qos=2):
        self.client.subscribe(topic, qos=qos)

    def unsubscribe(self, topic: str):
        self.client.unsubscribe(topic)

    def publish(self, topic: str, payload: any, qos=2, retain=True):
        self.client.publish(topic, payload, qos=qos, retain=retain)
