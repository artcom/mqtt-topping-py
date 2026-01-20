import weakref
import paho.mqtt.client as mqtt

from mqtt_topping.mqtt_client_adaptor import MqttClientAdaptor


class PahoClientAdaptor(MqttClientAdaptor):

    def __init__(self, client: any):
        super(PahoClientAdaptor, self).__init__(client)

    # def set_mqtt_topping(self, mqtt_topping):
    #     self._mqtt_topping = weakref.ref(mqtt_topping)

    # def subscribe(self, topic: str, qos=2):
    #     return

    # def unsubscribe(self, topic: str):
    #     return

    # def publish(self, topic: str, payload: any, qos=2, retain=True):
    #     return

    # def on_message(self, topic: str, payload: any):
    #     self._mqtt_topping().on_message(topic, payload)
