import cv2
from ultralytics import YOLO

def run_webcam(model_path="best.pt", webcam_index=0, img_size=640, conf_thresh=0.25):
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


if __name__ == "main":
    run_webcam(r"C:\Users\16262\Downloads\best.pt", webcam_index=0)