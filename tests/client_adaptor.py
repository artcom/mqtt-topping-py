from mqtt_topping import MqttClientAdaptor


class ClientAdaptor(MqttClientAdaptor):

    def __init__(self):
        super(ClientAdaptor, self).__init__()
        self.performed_subscriptions = []
        self.published = None
        self.performed_commands = []
        self.on_connect = None
        self.connected = False
        self.disconnected = False

    def connect(self, host: str, port: int, client_id: str, on_connect=None, on_connect_fail=None, on_disconnect=None, security_config=None):
        self.on_connect = on_connect
        self.connected = True

    def disconnect(self):
        self.disconnected = True
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected

    def subscribe(self, topic: str, qos=2):
        self.performed_subscriptions.append(topic)
        self.performed_commands.append('subscribe')

    def unsubscribe(self, topic: str):
        self.performed_subscriptions.remove(topic)
        self.performed_commands.append('unsubscribe')

    def publish(self, topic: str, payload: any, qos=2, retain=True):
        self.published = [topic, payload]
        self.performed_commands.append('publish')
