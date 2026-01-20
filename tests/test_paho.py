import json
import logging
import time

import pytest
from mqtt_topping import MqttTopping

LOGGER = logging.getLogger(__name__)


@pytest.fixture(name="paho_topping")
def paho_fixture():
    yield MqttTopping()


@pytest.fixture(name="callbacks")
def callbacks_fixture():
    yield []


def test_paho(paho_topping, callbacks):
    assert paho_topping is not None

    topic = "test/0/test"
    payload = "hello"
    json_payload = json.dumps(payload).encode()

    def callback_1(_, __):
        callbacks.append([1, topic, payload])

    paho_topping.connect("127.0.0.1", 1883)
    paho_topping.subscribe(topic, callback_1)

    assert topic in paho_topping.subscriptions

    paho_topping.on_message(topic, json_payload)

    assert callbacks[0][0] == 1
    assert callbacks[0][1] == topic
    assert callbacks[0][2] == payload

    time.sleep(1)

    paho_topping.unsubscribe(topic, callback_1)
    assert topic not in paho_topping.subscriptions

    paho_topping.disconnect()
