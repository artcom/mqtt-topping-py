import pytest

from mqtt_topping import MqttTopping
from tests.client_adaptor import ClientAdaptor


@pytest.fixture(name="test_topping")
def topping_fixture():
    yield MqttTopping(ClientAdaptor())


def test_topics_with_wildcard_hash(test_topping):
    topic = "test/hash/#"
    topic0 = "test/hash/test"
    topic1 = "test/hash/0/test"
    topic2 = "test/hash"
    topic3 = "test"
    topic4 = "test/noop/1/test"

    assert test_topping._match_topic(topic0, topic) is True
    assert test_topping._match_topic(topic1, topic) is True
    assert test_topping._match_topic(topic2, topic) is True
    assert test_topping._match_topic(topic3, topic) is False
    assert test_topping._match_topic(topic4, topic) is False


def test_topics_with_wildcard_plus_start(test_topping):
    topic = "+/plus/test"
    topic0 = "0/plus/test"
    topic1 = "1/plus/test"
    topic2 = "2/plus/noop"
    topic3 = "0/noop/1/test"

    assert test_topping._match_topic(topic0, topic) is True
    assert test_topping._match_topic(topic1, topic) is True
    assert test_topping._match_topic(topic2, topic) is False
    assert test_topping._match_topic(topic3, topic) is False


def test_topics_with_wildcard_plus_middle(test_topping):
    topic = "test/plus/+/test"
    topic0 = "test/plus/0/test"
    topic1 = "test/plus/1/test"
    topic2 = "test/plus/2"
    topic3 = "noop/plus/1/test"

    assert test_topping._match_topic(topic0, topic) is True
    assert test_topping._match_topic(topic1, topic) is True
    assert test_topping._match_topic(topic2, topic) is False
    assert test_topping._match_topic(topic3, topic) is False


def test_topics_with_wildcard_plus_end(test_topping):
    topic = "test/plus/+"
    topic0 = "test/plus/0"
    topic1 = "test/plus/1"
    topic2 = "test/plus/2/more"
    topic3 = "noop/plus/1/test"

    assert test_topping._match_topic(topic0, topic) is True
    assert test_topping._match_topic(topic1, topic) is True
    assert test_topping._match_topic(topic2, topic) is False
    assert test_topping._match_topic(topic3, topic) is False
