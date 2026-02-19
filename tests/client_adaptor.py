from mqtt_topping import MqttClientAdaptor


class ClientAdaptor(MqttClientAdaptor):

    def __init__(self):
        super(ClientAdaptor, self).__init__()
        self.subscription = None
        self.published = None
        self.executed_commands = []

    def subscribe(self, topic: str, qos=2):
        self.subscription = topic
        self.executed_commands.append('subscribe')

    def unsubscribe(self, topic: str):
        self.subscription = None
        self.executed_commands.append('unsubscribe')

    def publish(self, topic: str, payload: any, qos=2, retain=True):
        self.published = [topic, payload]
        self.executed_commands.append('publish')
