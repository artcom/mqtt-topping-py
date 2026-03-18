import pytest

from mqtt_topping import MqttTopping
from tests.client_adaptor import ClientAdaptor


@pytest.fixture(name="test_topping")
def topping_fixture():
    yield MqttTopping(ClientAdaptor())


def test_messages_with_wildcard_hash(test_topping):
    topic_hash = "test/hash/#"
    topic0 = "test/hash/test"
    topic1 = "test/hash/0/test"
    topic2 = "test/hash"
    topic3 = "test"
    topic4 = "test/noop/1/test"

    assert test_topping._match_topic(topic0, topic_hash) is True
    assert test_topping._match_topic(topic1, topic_hash) is True
    assert test_topping._match_topic(topic2, topic_hash) is True
    assert test_topping._match_topic(topic3, topic_hash) is False
    assert test_topping._match_topic(topic4, topic_hash) is False


def test_messages_with_wildcard_plus(test_topping):
    topic_plus = "test/+/test"
    topic0 = "test/0/test"
    topic1 = "test/1/test"
    topic2 = "test/2"
    topic3 = "noop/1/test"

    assert test_topping._match_topic(topic0, topic_plus) is True
    assert test_topping._match_topic(topic1, topic_plus) is True
    assert test_topping._match_topic(topic2, topic_plus) is False
    assert test_topping._match_topic(topic3, topic_plus) is False
