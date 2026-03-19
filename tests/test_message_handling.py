import json
import pytest

from mqtt_topping import InvalidTopicError
from mqtt_topping import MqttTopping
from tests.client_adaptor import ClientAdaptor


@pytest.fixture(name="test_topping")
def topping_fixture():
    yield MqttTopping(ClientAdaptor())


@pytest.fixture(name="payload")
def payload_fixture():
    yield "hello"


@pytest.fixture(name="json_payload")
def json_payload_fixture():
    json_payload = json.dumps("hello").encode()
    yield json_payload


@pytest.fixture(name="callbacks")
def callbacks_fixture():
    yield []


def test_subscribe(test_topping):
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

    assert test_topping.client_adaptor.performed_commands == ['subscribe']
    assert test_topping.client_adaptor.performed_subscriptions == [topic]
    assert len(test_topping.subscriptions[topic]['handlers']) == 3
    assert test_topping.subscriptions[topic]['handlers'][0].callback is callback_1
    assert test_topping.subscriptions[topic]['handlers'][1].callback is callback_2
    assert test_topping.subscriptions[topic]['handlers'][2].callback is callback_3


def test_subscribe_with_invalid_topics(test_topping):

    def callback(_, __):
        pass

    with pytest.raises(InvalidTopicError):
        test_topping.subscribe("", callback)

    with pytest.raises(InvalidTopicError):
        test_topping.subscribe("/test/test", callback)

    with pytest.raises(InvalidTopicError):
        test_topping.subscribe("//test/test", callback)

    with pytest.raises(InvalidTopicError):
        test_topping.subscribe("test//test", callback)

    with pytest.raises(InvalidTopicError):
        test_topping.subscribe("test/test//", callback)

    with pytest.raises(InvalidTopicError):
        test_topping.subscribe("#/", callback)

    with pytest.raises(InvalidTopicError):
        test_topping.subscribe("#/test", callback)


def test_refresh_subscriptions(test_topping):
    topic1 = "test/1/test"
    topic2 = "test/2/test"
    topic3 = "test/3/test"

    def callback_1(_, __):
        return

    def callback_2(_, __):
        return

    def callback_3(_, __):
        return

    def callback_4(_, __):
        return

    test_topping.subscribe(topic1, callback_1)
    test_topping.subscribe(topic1, callback_2)
    test_topping.subscribe(topic2, callback_3)
    test_topping.subscribe(topic3, callback_4)

    test_topping.refresh_subscriptions()

    assert test_topping.client_adaptor.performed_commands == [
        'subscribe', 'subscribe', 'subscribe',
        'subscribe', 'subscribe', 'subscribe'
    ]
    assert test_topping.client_adaptor.performed_subscriptions == [
        topic1, topic2, topic3,
        topic1, topic2, topic3
    ]
    assert len(test_topping.subscriptions[topic1]['handlers']) == 2
    assert len(test_topping.subscriptions[topic2]['handlers']) == 1
    assert len(test_topping.subscriptions[topic3]['handlers']) == 1
    assert test_topping.subscriptions[topic1]['handlers'][0].callback is callback_1
    assert test_topping.subscriptions[topic1]['handlers'][1].callback is callback_2
    assert test_topping.subscriptions[topic2]['handlers'][0].callback is callback_3
    assert test_topping.subscriptions[topic3]['handlers'][0].callback is callback_4


def test_unsubscribe(test_topping):
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

    test_topping.unsubscribe(topic, callback_1)
    assert test_topping.client_adaptor.performed_subscriptions == [topic]
    assert test_topping.subscriptions[topic]['handlers'][0].callback is callback_2
    assert test_topping.subscriptions[topic]['handlers'][1].callback is callback_3

    test_topping.unsubscribe(topic, callback_2)
    assert test_topping.client_adaptor.performed_subscriptions == [topic]
    assert test_topping.subscriptions[topic]['handlers'][0].callback is callback_3

    test_topping.unsubscribe(topic, callback_3)
    assert len(test_topping.client_adaptor.performed_subscriptions) == 0
    assert topic not in test_topping.subscriptions

    test_topping.unsubscribe(topic, callback_3)

    assert test_topping.client_adaptor.performed_commands == [
        'subscribe', 'unsubscribe'
    ]


def test_force_unsubscribe(test_topping):
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

    test_topping.force_unsubscribe(topic)
    assert len(test_topping.client_adaptor.performed_subscriptions) == 0
    assert topic not in test_topping.subscriptions

    test_topping.force_unsubscribe(topic)

    assert test_topping.client_adaptor.performed_commands == [
        'subscribe', 'unsubscribe'
    ]


def test_messages_empty(test_topping, payload):
    topic = "test/0/test"
    test_topping.client_adaptor.on_message(topic, payload)


def test_messages(test_topping, payload, json_payload, callbacks):
    topic = "test/0/test"

    def callback_1(topic, payload):
        callbacks.append([1, topic, payload])

    def callback_2(topic, payload):
        callbacks.append([2, topic, payload])

    def callback_3(topic, payload):
        callbacks.append([3, topic, payload])

    test_topping.subscribe(topic, callback_1)
    test_topping.subscribe(topic, callback_2)
    test_topping.subscribe(topic, callback_3)

    test_topping.client_adaptor.on_message(topic, json_payload)
    assert callbacks[0][0] == 1
    assert callbacks[0][1] == topic
    assert callbacks[0][2] == payload
    assert callbacks[1][0] == 2
    assert callbacks[1][1] == topic
    assert callbacks[1][2] == payload
    assert callbacks[2][0] == 3
    assert callbacks[2][1] == topic
    assert callbacks[2][2] == payload
    assert test_topping.client_adaptor.performed_commands == ['subscribe']


def test_messages_with_wildcard_hash(test_topping, payload, json_payload, callbacks):
    topic_hash = "test/#"
    topic0 = "test/test"
    topic1 = "test/0/test"
    topic2 = "noop/1/test"

    def callback(topic, payload):
        callbacks.append([1, topic, payload])

    test_topping.subscribe(topic_hash, callback)

    test_topping.client_adaptor.on_message(topic0, json_payload)
    test_topping.client_adaptor.on_message(topic1, json_payload)
    test_topping.client_adaptor.on_message(topic2, json_payload)

    assert callbacks[0][0] == 1
    assert callbacks[0][1] == topic0
    assert callbacks[0][2] == payload
    assert callbacks[1][0] == 1
    assert callbacks[1][1] == topic1
    assert callbacks[1][2] == payload
    assert len(callbacks) == 2


def test_messages_with_wildcard_plus(test_topping, payload, json_payload, callbacks):
    topic_plus = "test/+/test"
    topic0 = "test/0/test"
    topic1 = "test/1/test"
    topic2 = "test/2"

    def callback(topic, payload):
        callbacks.append([1, topic, payload])

    test_topping.subscribe(topic_plus, callback)

    test_topping.client_adaptor.on_message(topic0, json_payload)
    test_topping.client_adaptor.on_message(topic1, json_payload)
    test_topping.client_adaptor.on_message(topic2, json_payload)

    assert callbacks[0][0] == 1
    assert callbacks[0][1] == topic0
    assert callbacks[0][2] == payload
    assert callbacks[1][0] == 1
    assert callbacks[1][1] == topic1
    assert callbacks[1][2] == payload
    assert len(callbacks) == 2
