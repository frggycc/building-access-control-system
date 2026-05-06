import json, time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from awscrt import mqtt
from awsiot import mqtt_connection_builder

# GPIO Configuration; Will differ across machines
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GREEN_LED = 17
RED_LED   = 27
BUZZER    = 22
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED,   GPIO.OUT)
GPIO.setup(BUZZER,    GPIO.OUT)
GPIO.output(GREEN_LED, GPIO.LOW)
GPIO.output(RED_LED,   GPIO.LOW)
GPIO.output(BUZZER,    GPIO.LOW)

# Update these four values for each new Pi reader
READER_ID = "rpi5-door-controller-01"
LOCATION  = "Server Room"
ENDPOINT  = "YOUR_IOT_ENDPOINT.iot.us-east-1.amazonaws.com"
CERT_DIR  = "/home/YOUR_USERNAME/building-access"

SCAN_TOPIC     = "building/access/scan"
DECISION_TOPIC = "building/access/decision"

# Signal helpers for granted or denied decisions
def signal_granted():
    GPIO.output(GREEN_LED, GPIO.HIGH)
    GPIO.output(BUZZER,    GPIO.HIGH)
    time.sleep(0.6)
    GPIO.output(BUZZER,    GPIO.LOW)
    time.sleep(1.4)
    GPIO.output(GREEN_LED, GPIO.LOW)

def signal_denied():
    GPIO.output(RED_LED, GPIO.HIGH)
    GPIO.output(BUZZER,  GPIO.HIGH)
    time.sleep(0.3)
    GPIO.output(BUZZER,  GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(BUZZER,  GPIO.HIGH)
    time.sleep(0.3)
    GPIO.output(BUZZER,  GPIO.LOW)
    time.sleep(1.3)
    GPIO.output(RED_LED, GPIO.LOW)

def signal_connecting():
    for _ in range(2):
        GPIO.output(GREEN_LED, GPIO.HIGH)
        GPIO.output(RED_LED,   GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(GREEN_LED, GPIO.LOW)
        GPIO.output(RED_LED,   GPIO.LOW)
        time.sleep(0.1)

def signal_connected():
    GPIO.output(GREEN_LED, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(GREEN_LED, GPIO.LOW)

# MQTT decision callbacks
def on_decision(topic, payload, **kwargs):
    try:
        data = json.loads(payload.decode())
        if data.get("reader_id") != READER_ID:
            return
        if data.get("decision") == "GRANTED":
            print("[GRANTED] Access approved")
            signal_granted()
        else:
            print("[DENIED] Access denied")
            signal_denied()
    except Exception as e:
        print(f"ERROR in on_decision: {e}")
        signal_denied()

# Connect to AWS IoT Core; Will check the certificate here
print("Starting door controller...")
signal_connecting()
print(f"Connecting to {ENDPOINT}...")

mqtt_conn = mqtt_connection_builder.mtls_from_path(
    endpoint=ENDPOINT,
    cert_filepath=f"{CERT_DIR}/device.pem.crt",
    pri_key_filepath=f"{CERT_DIR}/private.pem.key",
    ca_filepath=f"{CERT_DIR}/root-CA.crt",
    client_id=READER_ID
)
mqtt_conn.connect().result()
print("Connected to AWS IoT Core")
signal_connected()

# Subscribe to decision topic to receive the deicisions from AWS
subscribe_future, _ = mqtt_conn.subscribe(
    topic=DECISION_TOPIC,
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=on_decision
)
subscribe_future.result()
print(f"Subscribed to {DECISION_TOPIC}")

# Main scan loop
reader = SimpleMFRC522()
print(f"Ready — hold a card near the reader [{LOCATION}]")

try:
    while True:
        uid, _ = reader.read()
        card_uid = str(uid)
        print(f"Card detected: {card_uid}")

        payload = json.dumps({
            "card_uid":  card_uid,
            "reader_id": READER_ID,
            "location":  LOCATION,
            "timestamp": int(time.time())
        })

        mqtt_conn.publish(
            topic=SCAN_TOPIC,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        print("Published scan event")
        time.sleep(1.5)

except KeyboardInterrupt:
    print("\nShutting down...")

finally:
    GPIO.cleanup()
    mqtt_conn.disconnect().result()
    print("Door controller stopped.")
