from umqtt.simple import MQTTClient
from machine import Pin, reset, unique_id
import utime

from dht import DHT22
from ubinascii import hexlify

# MQTT topic
TOPIC = b"iot-project"

# Pin assignments
TRIGGER_PIN = 13
ECHO_PIN = 12
LED_PIN = 25
DHT_PIN = 27

# Initialize the DHT sensor
dht_sensor = DHT22(Pin(DHT_PIN))

# Initialize the ultrasonic sensor
trigger = Pin(TRIGGER_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# Initialize the LED
led = Pin(LED_PIN, Pin.OUT)

# Generate unique client ID
client_id = hexlify(unique_id()).decode()

# Initialize the MQTT client
mqtt_client = MQTTClient(client_id, "broker.hivemq.com")

# Function to measure distance using ultrasonic sensor
def measure_distance():
    trigger.off()
    utime.sleep_us(2)
    trigger.on()
    utime.sleep_us(10)
    trigger.off()

    pulse_start = 0
    pulse_end = 0

    while echo.value() == 0:
        pulse_start = utime.ticks_us()

    while echo.value() == 1:
        pulse_end = utime.ticks_us()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 0.0343 / 2
    return distance

# Function to measure temperature and humidity using DHT sensor
def measure_temperature_humidity():
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    return temperature, humidity

# Callback function for MQTT message received event
def mqtt_callback(topic, msg):
    if topic == TOPIC:
        if msg == b"measurements":
            distance = measure_distance()
            if distance < 10:
                temperature, humidity = measure_temperature_humidity()
                message = "Distance: " + str(round(distance)) + " cm | Temperature: " + str(temperature) + "°C | Humidity: " + str(humidity) + "%"
                mqtt_client.publish(TOPIC, message)
                print("Measurements sent:\n", message)
                led.on()
                utime.sleep(5)
                led.off()

# Set the MQTT callback function
mqtt_client.set_callback(mqtt_callback)

def main():
    mqtt_client.connect()
    mqtt_client.subscribe(TOPIC)  # Subscribe to the MQTT topic
    while True:
        mqtt_client.check_msg()  # Check for MQTT messages

if __name__ == "__main__":
    main()
