# can be tested on thonny in resbery pi and micropython(local)
from umqtt.simple import MQTTClient
from machine import reset
from time import sleep, time
from json import dumps

# recive msg from Mqtt topic_sub 
def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'homeassistant/sub/some_topic_name' and msg == b'received':
    print('ESP received hello message')

def connect_and_subscribe():
  global client_id, mqtt_server_ip, topic_sub
  topic_sub = b'homeassistant/sub/some_topic_name'
  client_id="vegepod_client" # mqtt client name
  mqtt_server_ip="10.0.7.99", # mqtt server ip

  client = MQTTClient(client_id, mqtt_server_ip) # port='mqtt_port', user='mqtt_user', password='mqtt_password')
  client.set_callback(sub_cb) # call when get topic_sub
  client.connect()
  client.subscribe(topic_sub) # subscribe for this topic msg
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server_ip, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  sleep(10)
  reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

topic_pub = b'homeassistant/pub/some_topic_name'
counter = 0
message_interval_sec = 10
send = {}
# main Mqtt loop
while True:
  try:
    client.check_msg() # check_msg minimum evry 1 sec
    # sending mqtt msg evry 10 seconds
    if (time() - last_time_message) > message_interval_sec: 
      msg = 'Hello #%d' % counter
      send['some_msg'] = msg
      # publish mqtt topic as json
      client.publish(topic_pub, dumps(send))
      last_time_message = time()
      counter += 1
    sleep(1)
  except OSError as e:
    restart_and_reconnect()

# https://www.home-assistant.io/docs/mqtt/discovery/
# https://www.rototron.info/projects/micropython-vegetable-garden-automation-tutorial/
# in homeassistant yaml:
# which is located at /var/packages/homeassistant/target/var/config/configuration.yaml

# mqtt:
#   discovery: false

# sensor:
#   - platform: mqtt
#     device_class: "temperature"
#     state_topic: "homeassistant/sensor/vegepod/state"
#     name: "Vegepod Temperature"
#     unique_id: "vegepod_temperature"
#     unit_of_measurement: "°F"
#     value_template: "{{ value_json.temperature | round(1)}}"
#   - platform: mqtt
#     state_topic: "homeassistant/sensor/vegepod/state"
#     name: "Vegepod Water Level"
#     unique_id: "vegepod_level"
#     value_template: "{{ value_json.level}}"

# for binary_sensor only sending 'ON' or 'OFF' not json
# binary_sensor:
#   - platform: mqtt
#     state_topic: "homeassistant/binary_sensor/vegepod/state"
#     name: "Vegepod Canopy"
#     unique_id: "vegepod_canopy"