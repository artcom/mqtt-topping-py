import json
import pytest

from mqtt_topping import MqttTopping
from tests.client_adaptor import ClientAdaptor


@pytest.fixture(name="topping")
def topping_fixture():
    yield MqttTopping(ClientAdaptor({}))


@pytest.fixture(name="callbacks")
def callbacks_fixture():
    yield []


def test_event_or_command(topping):
    assert topping.is_event_or_command("d") is False
    assert topping.is_event_or_command("do") is False
    assert topping.is_event_or_command("d123") is False
    assert topping.is_event_or_command("dont") is False
    assert topping.is_event_or_command("doW") is True
    assert topping.is_event_or_command("doWork") is True

    assert topping.is_event_or_command("o") is False
    assert topping.is_event_or_command("on") is False
    assert topping.is_event_or_command("o123") is False
    assert topping.is_event_or_command("one") is False
    assert topping.is_event_or_command("onE") is True
    assert topping.is_event_or_command("onEvent") is True

    assert topping.is_event_or_command("a") is False
    assert topping.is_event_or_command("a1") is False
    assert topping.is_event_or_command("something") is False


def test_subscription(topping):
    topic = "test/0/test"

    def callback_1(_, __):
        return

    def callback_2(_, __):
        return

    def callback_3(_, __):
        return

    topping.subscribe(topic, callback_1)
    topping.subscribe(topic, callback_2)
    topping.subscribe(topic, callback_3)
    topping.subscribe(topic, callback_3)

    assert topping.client.subscription == topic
    assert len(topping.subscriptions[topic]['handlers']) == 3
    assert topping.subscriptions[topic]['handlers'][0].callback is callback_1
    assert topping.subscriptions[topic]['handlers'][1].callback is callback_2
    assert topping.subscriptions[topic]['handlers'][2].callback is callback_3
    assert topping.client.subscription == topic

    topping.unsubscribe(topic, callback_1)
    assert topping.client.subscription == topic
    assert topping.subscriptions[topic]['handlers'][0].callback is callback_2
    assert topping.subscriptions[topic]['handlers'][1].callback is callback_3

    topping.unsubscribe(topic, callback_2)
    assert topping.client.subscription == topic
    assert topping.subscriptions[topic]['handlers'][0].callback is callback_3

    topping.unsubscribe(topic, callback_3)
    assert topping.client.subscription is None
    assert topic not in topping.subscriptions

    topping.unsubscribe(topic, callback_3)


def test_messages(topping, callbacks):
    topic = "test/0/test"
    payload = "hello"
    json_payload = json.dumps(payload).encode()

    def callback_1(topic, payload):
        callbacks.append([1, topic, payload])

    def callback_2(topic, payload):
        callbacks.append([2, topic, payload])

    def callback_3(topic, payload):
        callbacks.append([3, topic, payload])

    topping.subscribe(topic, callback_1)
    topping.subscribe(topic, callback_2)
    topping.subscribe(topic, callback_3)

    topping.on_message(topic, json_payload)
    assert callbacks[0][0] == 1
    assert callbacks[0][1] == topic
    assert callbacks[0][2] == payload
    assert callbacks[1][0] == 2
    assert callbacks[1][1] == topic
    assert callbacks[1][2] == payload
    assert callbacks[2][0] == 3
    assert callbacks[2][1] == topic
    assert callbacks[2][2] == payload
