import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from threading import Thread
import cv2
import supervision as sv
from ultralytics import YOLO
import numpy as np
import time
import os
from dotenv import load_dotenv
from email.message import EmailMessage
import ssl
import smtplib

load_dotenv()

class SecurityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Security App")

        # Variable para almacenar el correo
        self.email_var = tk.StringVar()

        # Entrada para el correo
        self.email_label = tk.Label(root, text="Correo para notificaciones:")
        self.email_entry = tk.Entry(root, textvariable=self.email_var)
        

        # Botón para iniciar la detección
        self.start_button = tk.Button(root, text="Iniciar Detección", command=self.start_detection)

        # Disposición de los widgets
        self.email_label.pack(pady=10)
        self.email_entry.pack(pady=10)
        self.start_button.pack(pady=20)

    def start_detection(self):
        # Obtener el correo desde la entrada
        email_receiver = self.email_var.get()

        # Validar que se haya ingresado un correo
        if not email_receiver:
            messagebox.showerror("Error", "Ingresa una dirección de correo válido.")
            return

        # Iniciar el hilo para la detección
        detection_thread = Thread(target=self.run_detection, args=(email_receiver,))
        detection_thread.start()

    def run_detection(self, email_receiver):
        # El código de detección original va aquí

        cap = cv2.VideoCapture(0)
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=2,
            text_scale=1
        )

        model = YOLO("yolov8n.pt")

        zone_polygon = np.array([
            [0, 0],
            [1280, 0],
            [1250, 720],
            [0, 720]
        ])
        zone = sv.PolygonZone(polygon=zone_polygon, frame_resolution_wh=(1280, 720))
        zone_annotator = sv.PolygonZoneAnnotator(zone=zone, color=sv.Color.red())

        person_count = 0

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

            count = self.count_people(detections, model)
            cv2.putText(frame, f"People: {count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            zone.trigger(detections=detections)
            frame = zone_annotator.annotate(scene=frame)

            cv2.imshow("yolov8", frame)

            if count > 0:
                person_count += 1

            if person_count >= 10:
                print("------------------Correo enviado xd---------------")
                print("------------------Conteo reiniciada------------------")
                person_count = 0
                self.send_email(email_receiver)

            if cv2.waitKey(1000) == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    def count_people(self, detections, model):
        return sum(1 for _, confidence, class_id, _ in detections if model.model.names[class_id] == "person")

    def send_email(self, email_receiver):
        em = EmailMessage()
        em["From"] = "losshupaia@gmail.com"
        em["To"] = email_receiver
        em["Subject"] = "Aviso cámara de seguridad!"
        em.set_content("""
            Se ha visto a una persona sospechosa en el establecimiento. Tomar precaución.
        """)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login("losshupaia@gmail.com", os.getenv("PASSWORD"))
            smtp.sendmail("losshupaia@gmail.com", email_receiver, em.as_string())

def main():
    root = tk.Tk()
    app = SecurityApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
