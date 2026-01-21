# MQTT topping for Python

Syntactical sugar on top of the MQTT client cake

## Features

### Enhanced Subscriptions

- Attach multiple callback handlers to the same topic or wildcard
- Simplified `unsubscribe` (removes specific handler)

## System requirements

- Python 3.11.x

## Usage

Create an instance of the mqtt topping with a default paho mqtt-client:

```py
from mqtt_topping import MqttTopping

mqtt_topping = MqttTopping()
mqtt_topping.connect("127.0.0.1", 1883)
```

Create an instance of the mqtt topping with a TouchDesigner mqtt-client:

```py
from mqtt_topping import MqttTopping, TouchDesignerClientAdaptor

client = op('mqttclient')
client_adaptor = TouchDesignerClientAdaptor(client)
mqtt_topping = MqttTopping(client_adaptor)
```

Subscribe to a topic:

```py

 def callback(topic, payload):
    # handle message here

mqtt_topping.subscribe("test/topic/doTest", callback)
```

Unsubscribe from a topic:

```py

 def callback(topic, payload):
    # handle message here

mqtt_topping.unsubscribe("test/topic/doTest", callback)
```

Publish a message:

```py
payload = {
    "id": 0,
    "name": "bob"
}
mqtt_topping.publish("test/topic/doTest", payload)
```

## Development

To install dev dependencies:

```sh
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements_dev.txt
```

To run unit tests:

```sh
$ python -m pytest tests
```

To release a new version:

Update the field `version` in `pyproject.toml` and tag the version.
