import json
import threading
import time
import pytest

from mqtt_topping import MqttTopping
from mqtt_topping.security_config import SecurityConfig


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
    message = {
        'topic': topic,
        'payload': payload
    }
    json_message = json.dumps(message).encode()

    def on_disconnect(_, __, ___, ____, _____):
        pass

    def callback_1(_, __):
        callbacks.append([1, topic, payload])

    paho_topping.connect(
        "127.0.0.1",
        1883,
        "test_client_123",
        on_disconnect=on_disconnect
    )

    paho_topping.subscribe(topic, callback_1)
    assert topic in paho_topping.subscriptions

    paho_topping.on_message(topic, json_message)
    assert callbacks[0][0] == 1
    assert callbacks[0][1] == topic
    assert callbacks[0][2] == payload

    time.sleep(1)

    paho_topping.unsubscribe(topic, callback_1)
    assert topic not in paho_topping.subscriptions

    paho_topping.disconnect()


def test_connect_reports_failure_when_broker_is_unreachable(paho_topping):
    # Port 1 is reserved and nothing listens on it, so the connection attempt
    # fails immediately instead of silently killing a background thread.
    with pytest.raises(Exception):
        paho_topping.connect("127.0.0.1", 1, "test_client_unreachable")


def test_is_connected_reflects_connection_state(paho_topping):
    assert paho_topping.is_connected() is False

    paho_topping.connect("127.0.0.1", 1883, "test_client_is_connected")
    time.sleep(0.5)
    assert paho_topping.is_connected() is True

    paho_topping.disconnect()
    assert paho_topping.is_connected() is False


def test_disconnect_before_connect_does_not_raise():
    topping = MqttTopping()
    topping.disconnect()


def test_disconnect_from_within_a_callback_does_not_raise(paho_topping):
    done = threading.Event()
    errors = []

    def on_connect(*args, **kwargs):
        try:
            paho_topping.disconnect()
        except Exception as e:
            errors.append(e)
        finally:
            done.set()

    paho_topping.connect(
        "127.0.0.1", 1883, "test_client_disconnect_in_callback", on_connect=on_connect)

    assert done.wait(timeout=5)
    assert errors == []


def test_publish_before_connect_does_not_raise():
    topping = MqttTopping()
    assert topping.client_adaptor.publish("test/0/doTest", b"hello") is None


def test_publish_returns_message_info(paho_topping):
    paho_topping.connect("127.0.0.1", 1883, "test_client_publish")
    time.sleep(0.5)
    message_info = paho_topping.client_adaptor.publish(
        "test/0/doTest", b"hello", qos=0)
    assert message_info is not None
    assert message_info.rc == 0
    paho_topping.disconnect()


def test_security_config_allows_missing_username():
    security_config = SecurityConfig()
    assert security_config.username is None
    assert security_config.password is None

    topping = MqttTopping()
    topping.connect("127.0.0.1", 1883, "test_client_no_username",
                     security_config=security_config)
    time.sleep(0.5)
    assert topping.is_connected() is True
    topping.disconnect()


def test_mqtt_thread_is_a_daemon_thread(paho_topping):
    # A caller that forgets to call disconnect() on shutdown (or an unhandled
    # exit path) must not hang the process on this thread's loop_forever().
    paho_topping.connect("127.0.0.1", 1883, "test_client_daemon_thread")
    time.sleep(0.5)
    assert paho_topping.client_adaptor.mqtt_thread.daemon is True
    paho_topping.disconnect()
