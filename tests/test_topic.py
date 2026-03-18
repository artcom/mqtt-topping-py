import pytest

from mqtt_topping import InvalidTopicError
from mqtt_topping import MqttTopping
from tests.client_adaptor import ClientAdaptor


@pytest.fixture(name="test_topping")
def topping_fixture():
    yield MqttTopping(ClientAdaptor())


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


def test_validate_with_wildcard_hash(test_topping):

    test_topping.validate_topic("test/hash/#")
    test_topping.validate_topic("test/#")
    test_topping.validate_topic("#")

    test_topping.validate_topic("+/0/plus")
    test_topping.validate_topic("test/+/plus")
    test_topping.validate_topic("test/+")
    test_topping.validate_topic("test/0/test")

    with pytest.raises(InvalidTopicError):
        test_topping.validate_topic("")

    with pytest.raises(InvalidTopicError):
        test_topping.validate_topic("/test/test")

    with pytest.raises(InvalidTopicError):
        test_topping.validate_topic("//test/test")

    with pytest.raises(InvalidTopicError):
        test_topping.validate_topic("test//test")

    with pytest.raises(InvalidTopicError):
        test_topping.validate_topic("test/test//")

    with pytest.raises(InvalidTopicError):
        test_topping.validate_topic("#/")

    with pytest.raises(InvalidTopicError):
        test_topping.validate_topic("#/test")


def test_match_with_wildcard_hash(test_topping):
    topic = "test/hash/#"
    assert test_topping.match_topic("test/hash/test", topic) is True
    assert test_topping.match_topic("test/hash/0/test", topic) is True
    assert test_topping.match_topic("test/hash", topic) is True
    assert test_topping.match_topic("test", topic) is False
    assert test_topping.match_topic("test/noop/1/test", topic) is False


def test_match_with_wildcard_plus_start(test_topping):
    topic = "+/plus/test"
    assert test_topping.match_topic("0/plus/test", topic) is True
    assert test_topping.match_topic("1/plus/test", topic) is True
    assert test_topping.match_topic("2/plus/noop", topic) is False
    assert test_topping.match_topic("0/noop/1/test", topic) is False


def test_match_with_wildcard_plus_middle(test_topping):
    topic = "test/plus/+/test"
    assert test_topping.match_topic("test/plus/0/test", topic) is True
    assert test_topping.match_topic("test/plus/1/test", topic) is True
    assert test_topping.match_topic("test/plus/2", topic) is False
    assert test_topping.match_topic("noop/plus/1/test", topic) is False


def test_topics_with_wildcard_plus_end(test_topping):
    topic = "test/plus/+"
    assert test_topping.match_topic("test/plus/0", topic) is True
    assert test_topping.match_topic("test/plus/1", topic) is True
    assert test_topping.match_topic("test/plus/2/more", topic) is False
    assert test_topping.match_topic("noop/plus/1/test", topic) is False
