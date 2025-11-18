import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk

# Global variable to hold and run YOLO detection
cap = None

"""
  Starts the webcam, runs YOLO object detection on each frame, and displays it in a window.
  Parameters:
  - model_path: path to the trained YOLO model
  - webcam_index: camera index (0 is default webcam)
  - img_size: size to resize images for YOLO
  - conf_thresh: confidence threshold for object detection
"""
def start_camera(model_path="best.pt", webcam_index=0, img_size=640, conf_thresh=0.35):

# add confidence measure

  # load the YOLO model
  model = YOLO(model_path)

  # open the webcam
  cap = cv2.VideoCapture(webcam_index)
  # if webcan cannot be opened, print error
  if not cap.isOpened():
    print("Error: Cannot open webcam")
    return

  while True:
    # Read a fram from the webcam
    ret, frame = cap.read()
    # exit if frame is not read successfully
    if not ret:
      break

    # run YOLO detection 
    results = model(frame, stream=True, imgsz=img_size, conf=conf_thresh)

    # iterate over results
    for res in results:
      # Get bounding boxes, confidences, and class IDs
      boxes = res.boxes.xyxy.cpu().numpy()
      confidences = res.boxes.conf.cpu().numpy()
      classes = res.boxes.cls.cpu().numpy().astype(int)

    # Draw bounding boxes and labels on the frame
    for (x1, y1, x2, y2), conf, cls in zip(boxes, confidences, classes):
      label = f"{res.names[cls]} {conf:.2f}"
      cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
      cv2.putText(frame, label, (int(x1), int(y1)-10),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    # display the fram with detections
    cv2.imshow("YOLOv11 Webcam", frame)

    # exit loop if ESC is pressed
    if cv2.waitKey(1) == 27:  # Press ESC to quit
      break

  # release resources after exiting the loop
  cap.release()
  cv2.destroyAllWindows()

# stop camera function
def stop_camera():
    # releases the webcam if it is still running
    global cap
    if cap:
      cap.release()

# ---------------------
# GUI using Tkinter
# ---------------------
root = tk.Tk()
root.title("Security Camera")
root.geometry("900x600")

# label to display video
video_label = Label(root)
video_label.pack()

# buttons to start and stop camera
Button(root, text="Start Camera", command=start_camera).pack()
Button(root, text="Stop Camera", command=stop_camera).pack()

# start the Tkinter main loop
root.mainloop()