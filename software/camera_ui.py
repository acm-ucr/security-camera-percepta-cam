import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import Label, Button
from PIL import Image, ImageTk

cap = None

# def start_camera():
# global cap
# cap = cv2.VideoCapture("https://assets.bucketlistly.blog/sites/5adf778b6eabcc00190b75b1/content_entry5adf77af6eabcc00190b75b6/6075185986d092000b192d0a/files/best-free-travel-images-main-image-hd-op.webp")
# update_frame()
# def update_frame():
# if cap is not None:
# ret, frame = cap.read()
# if ret:
# frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
# img = ImageTk.PhotoImage(Image.fromarray(frame))
# video_label.config(image=img)
# video_label.image = img
# video_label.after(10, update_frame)
def start_camera(model_path="best.pt", webcam_index=0, img_size=640, conf_thresh=0.25):
    model = YOLO(model_path)

    cap = cv2.VideoCapture(webcam_index)
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, stream=True, imgsz=img_size, conf=conf_thresh)

        for res in results:
            boxes = res.boxes.xyxy.cpu().numpy()
            confidences = res.boxes.conf.cpu().numpy()
            classes = res.boxes.cls.cpu().numpy().astype(int)

            for (x1, y1, x2, y2), conf, cls in zip(boxes, confidences, classes):
                label = f"{res.names[cls]} {conf:.2f}"
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
                cv2.putText(frame, label, (int(x1), int(y1)-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        cv2.imshow("YOLOv11 Webcam", frame)

        if cv2.waitKey(1) == 27:  # Press ESC to quit
            break

    cap.release()
    cv2.destroyAllWindows()
def stop_camera():
    global cap
    if cap:
        cap.release()

root = tk.Tk()
root.title("Security Camera")
root.geometry("900x600")

video_label = Label(root)
video_label.pack()

Button(root, text="Start Camera", command=start_camera).pack()
Button(root, text="Stop Camera", command=stop_camera).pack()

root.mainloop()