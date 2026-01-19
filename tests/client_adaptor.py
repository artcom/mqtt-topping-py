from mqtt_topping import MqttClientAdaptor


class ClientAdaptor(MqttClientAdaptor):

    def __init__(self, client: any):
        super(ClientAdaptor, self).__init__(client)
        self.subscription = None
        self.published = None

    def subscribe(self, topic: str, qos=2):
        self.subscription = topic

    def unsubscribe(self, topic: str):
        self.subscription = None

    def publish(self, topic: str, payload: any, qos=2, retain=True):
        self.published = [topic, payload]
