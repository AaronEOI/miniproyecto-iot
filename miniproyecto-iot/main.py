from umqtt.simple import MQTTClient
from machine import Pin, reset, unique_id
import utime
from dht import DHT22
from ubinascii import hexlify

# MQTT topic
TOPIC = b"project.test.eoi"

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

def main():
    mqtt_client.connect()

    while True:
        mqtt_client.check_msg()

        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()

        mqtt_client.publish(TOPIC, "Temperature: {} °C, Humidity: {}%".format(temperature, humidity))
        print("Temperature sent...")

        distance = measure_distance()

        if distance < 10:
            led.on()
            mqtt_client.publish(TOPIC, "Distance: {} cm".format(distance))
            print("Movement detected! Message sent...")
            utime.sleep(5)  # Keep the LED on for 5 seconds
            led.off()

        utime.sleep_ms(5000)  # Check for distance every 5 seconds

if __name__ == "__main__":
    main()
