from flask import Flask, Response, render_template
import cv2
from ultralytics import YOLO

app = Flask(__name__)

# Load your trained YOLOv11 model
model = YOLO("best.pt")  # or 'yolov11n.pt', 'yolov11s.pt', etc.

# Open webcam (0 = default webcam)
cap = cv2.VideoCapture(1)
if not cap.isOpened():
  print("Error: Could not open webcam.")
  exit()

def generate_frames():
  while True:
    ret, frame = cap.read()
    if not ret:
      print("Failed to grab frame.")
      break

    # Run YOLOv11 inference on the frame
    results = model.predict(source=frame, conf=0.3, verbose=False)

    # Plot results on the frame
    annotated_frame = results[0].plot()
    
    # Convert to JPEG
    _, buffer = cv2.imencode('.jpg', annotated_frame)
    frame = buffer.tobytes()

    # MJPEG stream format
    yield (b'--frame\r\n'
          b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')  # your HTML file

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000, debug=True)

#     # Display the result
#     cv2.imshow("YOLOv11 Live Inference", annotated_frame)

#     # Press 'q' to exit the live stream
#     if cv2.waitKey(1) & 0xFF == ord("q"):
#       break

# cap.release()
# cv2.destroyAllWindows()

