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


def test_messages_empty(test_topping, json_payload):
    topic = "test/0/test"
    test_topping.client_adaptor.on_message(topic, json_payload)


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


def test_messages_no_parsing(test_topping, payload, json_payload, callbacks):
    topic = "test/0/test"

    def callback_1(topic, payload):
        callbacks.append([1, topic, payload])

    def callback_2(topic, payload):
        callbacks.append([2, topic, payload])

    def callback_3(topic, payload):
        callbacks.append([3, topic, payload])

    test_topping.subscribe(topic, callback_1, parse=False)
    test_topping.subscribe(topic, callback_2, parse=True)
    test_topping.subscribe(topic, callback_3, parse=False)

    test_topping.client_adaptor.on_message(topic, json_payload)
    assert callbacks[0][0] == 1
    assert callbacks[0][1] == topic
    assert callbacks[0][2] == json_payload
    assert callbacks[1][0] == 2
    assert callbacks[1][1] == topic
    assert callbacks[1][2] == payload
    assert callbacks[2][0] == 3
    assert callbacks[2][1] == topic
    assert callbacks[2][2] == json_payload
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


def test_messages_empty_payload_parsed_as_none(test_topping, callbacks):
    topic = "test/0/test"

    def callback(topic, payload):
        callbacks.append([topic, payload])

    test_topping.subscribe(topic, callback)
    test_topping.client_adaptor.on_message(topic, b'')

    assert callbacks[0][0] == topic
    assert callbacks[0][1] is None


def test_messages_empty_payload_unparsed_stays_raw(test_topping, callbacks):
    topic = "test/0/test"

    def callback(topic, payload):
        callbacks.append([topic, payload])

    test_topping.subscribe(topic, callback, parse=False)
    test_topping.client_adaptor.on_message(topic, b'')

    assert callbacks[0][0] == topic
    assert callbacks[0][1] == b''


def test_callback_exception_does_not_stop_other_handlers_or_later_messages(test_topping, json_payload, callbacks):
    topic = "test/0/test"

    def failing_callback(_, __):
        raise ValueError("boom")

    def callback(topic, payload):
        callbacks.append([topic, payload])

    test_topping.subscribe(topic, failing_callback)
    test_topping.subscribe(topic, callback)

    test_topping.client_adaptor.on_message(topic, json_payload)
    assert len(callbacks) == 1

    test_topping.client_adaptor.on_message(topic, json_payload)
    assert len(callbacks) == 2


def test_callback_exception_invokes_on_callback_error_hook():
    errors = []

    def on_callback_error(topic, payload, error):
        errors.append((topic, payload, error))

    test_topping = MqttTopping(ClientAdaptor(), on_callback_error=on_callback_error)
    topic = "test/0/test"

    def failing_callback(_, __):
        raise ValueError("boom")

    test_topping.subscribe(topic, failing_callback)
    test_topping.client_adaptor.on_message(topic, json.dumps("hello").encode())

    assert len(errors) == 1
    assert errors[0][0] == topic
    assert isinstance(errors[0][2], ValueError)


def test_parse_error_invokes_on_parse_error_hook():
    errors = []

    def on_parse_error(topic, payload, error):
        errors.append((topic, payload, error))

    test_topping = MqttTopping(ClientAdaptor(), on_parse_error=on_parse_error)
    topic = "test/0/test"

    def callback(_, __):
        pass

    test_topping.subscribe(topic, callback)
    test_topping.client_adaptor.on_message(topic, b"not json")

    assert len(errors) == 1
    assert errors[0][0] == topic


def test_disconnect_clears_subscriptions(test_topping):
    topic = "test/0/test"

    def callback(_, __):
        return

    test_topping.subscribe(topic, callback)
    assert topic in test_topping.subscriptions

    test_topping.disconnect()
    assert test_topping.subscriptions == {}


def test_is_connected_delegates_to_adaptor(test_topping):
    assert test_topping.is_connected() is False
    test_topping.connect("127.0.0.1", 1883, "test_client")
    assert test_topping.is_connected() is True
    test_topping.disconnect()
    assert test_topping.is_connected() is False


def test_reconnect_resubscribes_all_topics():
    adaptor = ClientAdaptor()
    test_topping = MqttTopping(adaptor)

    topics = ["test/1/test", "test/2/test", "test/3/test", "test/4/test"]

    def callback(_, __):
        return

    def on_connect(*args, **kwargs):
        for topic in topics:
            test_topping.subscribe(topic, callback)

    test_topping.connect("127.0.0.1", 1883, "test_client", on_connect=on_connect)

    adaptor.on_connect()
    assert adaptor.performed_commands.count('subscribe') == 4

    adaptor.on_connect()
    assert adaptor.performed_commands.count('subscribe') == 8


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
