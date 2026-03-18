import pytest

from mqtt_topping import InvalidTopicError
from mqtt_topping import MqttTopping
from tests.client_adaptor import ClientAdaptor


@pytest.fixture(name="test_topping")
def topping_fixture():
    yield MqttTopping(ClientAdaptor())


def test_topics_with_wildcard_hash(test_topping):
    topic0 = ""

    topic1 = "test/hash/#"
    topic2 = "test/#"
    topic3 = "#"
    topic4 = "#/test"

    topic5 = "+/0/plus"
    topic6 = "test/+/plus"
    topic7 = "test/+"
    topic8 = "test/0/test"

    with pytest.raises(InvalidTopicError):
        test_topping._validate_topic(topic0)

    test_topping._validate_topic(topic1)
    test_topping._validate_topic(topic2)
    test_topping._validate_topic(topic3)

    with pytest.raises(InvalidTopicError):
        test_topping._validate_topic(topic4)

    test_topping._validate_topic(topic5)
    test_topping._validate_topic(topic6)
    test_topping._validate_topic(topic7)
    test_topping._validate_topic(topic8)
