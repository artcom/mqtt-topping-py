from mqtt_topping.mqtt_client_adaptor import MqttClientAdaptor


class TouchDesignerClientAdaptor(MqttClientAdaptor):

    def __init__(self, client):
        super(TouchDesignerClientAdaptor, self).__init__()
        self.client = client

    def connect(self, host, port):
        self.client.par.active = True
        self.client.par.reconnect.pulse()

    def disconnect(self):
        self.client.par.active = False

    def subscribe(self, topic: str, qos=2):
        self.client.subscribe(topic, qos=qos)

    def unsubscribe(self, topic: str):
        self.client.unsubscribe(topic)

    def publish(self, topic: str, payload: any, qos=2, retain=True):
        self.client.publish(topic, payload, qos=qos, retain=retain)
