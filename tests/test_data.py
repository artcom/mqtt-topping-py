import json
import pytest

from mqtt_topping import MqttTopping
from tests.client_adaptor import ClientAdaptor


@pytest.fixture(name="test_topping")
def topping_fixture():
    yield MqttTopping(ClientAdaptor({}))


@pytest.fixture(name="paho_topping")
def paho_fixture():
    yield MqttTopping()


@pytest.fixture(name="callbacks")
def callbacks_fixture():
    yield []


def test_event_or_command(test_topping):
    assert test_topping.is_event_or_command("d") is False
    assert test_topping.is_event_or_command("do") is False
    assert test_topping.is_event_or_command("d123") is False
    assert test_topping.is_event_or_command("dont") is False
    assert test_topping.is_event_or_command("doW") is True
    assert test_topping.is_event_or_command("doWork") is True

    assert test_topping.is_event_or_command("o") is False
    assert test_topping.is_event_or_command("on") is False
    assert test_topping.is_event_or_command("o123") is False
    assert test_topping.is_event_or_command("one") is False
    assert test_topping.is_event_or_command("onE") is True
    assert test_topping.is_event_or_command("onEvent") is True

    assert test_topping.is_event_or_command("a") is False
    assert test_topping.is_event_or_command("a1") is False
    assert test_topping.is_event_or_command("something") is False


def test_subscription(test_topping):
    topic = "test/0/test"

    def callback_1(_, __):
        return

    def callback_2(_, __):
        return

    def callback_3(_, __):
        return

    test_topping.subscribe(topic, callback_1)
    test_topping.subscribe(topic, callback_2)
    test_topping.subscribe(topic, callback_3)
    test_topping.subscribe(topic, callback_3)

    assert test_topping.client.subscription == topic
    assert len(test_topping.subscriptions[topic]['handlers']) == 3
    assert test_topping.subscriptions[topic]['handlers'][0].callback is callback_1
    assert test_topping.subscriptions[topic]['handlers'][1].callback is callback_2
    assert test_topping.subscriptions[topic]['handlers'][2].callback is callback_3
    assert test_topping.client.subscription == topic

    test_topping.unsubscribe(topic, callback_1)
    assert test_topping.client.subscription == topic
    assert test_topping.subscriptions[topic]['handlers'][0].callback is callback_2
    assert test_topping.subscriptions[topic]['handlers'][1].callback is callback_3

    test_topping.unsubscribe(topic, callback_2)
    assert test_topping.client.subscription == topic
    assert test_topping.subscriptions[topic]['handlers'][0].callback is callback_3

    test_topping.unsubscribe(topic, callback_3)
    assert test_topping.client.subscription is None
    assert topic not in test_topping.subscriptions

    test_topping.unsubscribe(topic, callback_3)


def test_messages(test_topping, callbacks):
    topic = "test/0/test"
    payload = "hello"
    json_payload = json.dumps(payload).encode()

    def callback_1(topic, payload):
        callbacks.append([1, topic, payload])

    def callback_2(topic, payload):
        callbacks.append([2, topic, payload])

    def callback_3(topic, payload):
        callbacks.append([3, topic, payload])

    test_topping.subscribe(topic, callback_1)
    test_topping.subscribe(topic, callback_2)
    test_topping.subscribe(topic, callback_3)

    test_topping.client.on_message(topic, json_payload)
    assert callbacks[0][0] == 1
    assert callbacks[0][1] == topic
    assert callbacks[0][2] == payload
    assert callbacks[1][0] == 2
    assert callbacks[1][1] == topic
    assert callbacks[1][2] == payload
    assert callbacks[2][0] == 3
    assert callbacks[2][1] == topic
    assert callbacks[2][2] == payload


def test_paho(paho_topping):
    assert paho_topping is not None
    paho_topping.subscribe("foo", None)
    paho_topping.unsubscribe("foo", None)
    paho_topping.on_message("foo", None)
