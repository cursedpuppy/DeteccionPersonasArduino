import cv2
import supervision as sv
from ultralytics import YOLO
import numpy as np
import tkinter as tk
from tkinter import ttk

ZONE_POLYGON = np.array([
    [0, 0],
    [1280, 0],
    [1250, 720],
    [0, 720]
])

def count_people(detections, model):
    return sum(1 for _, confidence, class_id, _ in detections if model.model.names[class_id] == "person")

def start_detection():
    cap = cv2.VideoCapture(0)
    
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )

    model = YOLO("yolov8n.pt")

    zone = sv.PolygonZone(polygon=ZONE_POLYGON, frame_resolution_wh=(1280, 720))
    zone_annotaor = sv.PolygonZoneAnnotator(zone=zone, color=sv.Color.red())

    while True:
        ret, frame = cap.read()
        result = model(frame)[0]
        detections = sv.Detections.from_yolov8(result)
        labels = [
            f"{model.model.names[class_id]} {confidence:0.2f}"
            for _, confidence, class_id, _
            in detections
        ]
        frame = box_annotator.annotate(scene=frame, detections=detections, labels=labels)

        count = count_people(detections, model)
        cv2.putText(frame, f"People: {count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        zone.trigger(detections=detections)
        frame = zone_annotaor.annotate(scene=frame)

        cv2.imshow("yolov8", frame)

        if (cv2.waitKey(1000) == 27):
            break

    cap.release()
    cv2.destroyAllWindows()

# Crear la ventana de tkinter
root = tk.Tk()
root.title("Detección de Personas")
root.geometry("200x100")

# Crear el botón
start_button = ttk.Button(root, text="Iniciar Detección", command=start_detection)
start_button.pack(pady=20)

# Ejecutar la aplicación de tkinter
root.mainloop()
