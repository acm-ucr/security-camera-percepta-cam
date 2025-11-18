from ultralytics import YOLO
import cv2
#imports for sending MQTT
import paho.mqtt.client as mqtt
import time

# MQTT Configuration (emqx public broker))
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
# Topic to publish or subscribe to
MQTT_TOPIC = "forgescam/security"

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)
client.loop_start()

messege = "This is a test message for MQTT publishing."
client.publish(MQTT_TOPIC, messege)

# Allow a short time to make sure messege is sent before ending script
time.sleep(2)

# Stops background MQTT thread from earlier
client.loop_stop()
# Disconnects from the broker
client.disconnect()

# Begin train modelc code

# Load your trained YOLOv11 model
model = YOLO("best.pt")  # or 'yolov11n.pt', 'yolov11s.pt', etc.

# Open webcam (0 = default webcam)
cap = cv2.VideoCapture(1)

if not cap.isOpened():
  print("Error: Could not open webcam.")
  exit()

while True:
  ret, frame = cap.read()
  if not ret:
    print("Failed to grab frame.")
    break

  # Run YOLOv11 inference on the frame
  results = model.predict(source=frame, conf=0.3, verbose=False)

  # Plot results on the frame
  annotated_frame = results[0].plot()

  # Display the result
  cv2.imshow("YOLOv11 Live Inference", annotated_frame)

  # Press 'q' to exit the live stream
  if cv2.waitKey(1) & 0xFF == ord("q"):
    break

cap.release()
cv2.destroyAllWindows()
