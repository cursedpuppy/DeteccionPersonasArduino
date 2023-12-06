import tkinter as tk
from tkinter import messagebox
from threading import Thread
import cv2
import numpy as np
import time
import os
from dotenv import load_dotenv
from email.message import EmailMessage
import ssl
import smtplib
import pyrebase
from hikvisionapi import Client
from ultralytics import YOLO
import supervision as sv
from firebase_admin import firestore, credentials, initialize_app
load_dotenv()
# Configuración de Firebase
firebaseConfig = {
    "apiKey": "AIzaSyB2MlSOiq4ZB0ChuTytP7B12oouO13hx-A",
    "authDomain": "securitycameraia.firebaseapp.com",
    "projectId": "securitycameraia",
    "storageBucket": "securitycameraia.appspot.com",
    "messagingSenderId": "154010826465",
    "appId": "1:154010826465:web:bcd4f05ecc7278afd569a0",
    "measurementId": "G-FZET9WEE3H",
    "serviceAccount": "securitycameraia-firebase-adminsdk-h6reg-bc82044a45.json",
    "databaseURL": "gs://securitycameraia.appspot.com"
}

# Configuración de Firebase para el almacenamiento
firebase = pyrebase.initialize_app(firebaseConfig)

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
        self.root.geometry("200x200")

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
        # Configuración de la cámara Hikvision
        camera_ip = "192.168.4.46"
        camera_username = "admin"
        camera_password = "3d0s2094"

        # Crear una instancia del cliente Hikvision
        cam = Client(f'http://{camera_ip}', camera_username, camera_password)

        # Configurar el canal de transmisión
        channel = 1  # Ajusta el número del canal según tu configuración
        cam.Streaming.channels[channel].mode = 0  # Modo de transmisión: 0 para video

        cap = cv2.VideoCapture(0)
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=2,
            text_scale=1
        )

        model = YOLO("yolov8n.pt")

        person_count = 0
        max_person_count = 10  # Ajusta este valor según tus necesidades

        while True:
            try:
                # Obtener la imagen en formato JPEG de la cámara Hikvision
                image_data = cam.Streaming.channels[channel].picture(method='get', type='opaque_data').content

                # Decodificar la imagen y mostrarla
                frame = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)

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

                cv2.imshow("yolov8", frame)

                if count > 0:
                    person_count += 1
                    if person_count >= max_person_count:
                        print("------------------Correo enviado xd---------------")
                        print("------------------Conteo reiniciado------------------")
                        person_count = 0
                        image_url = self.upload_image_to_storage(frame)
                        self.send_email(email_receiver, image_url)
                        self.save_data_to_firestore(email_receiver, image_url)

                if cv2.waitKey(1000) == 27:
                    break

            except Exception as e:
                print(f"Error al obtener o mostrar la imagen: {e}")

        cap.release()
        cv2.destroyAllWindows()

    def upload_image_to_storage(self, frame):
        # Configurar el cliente de almacenamiento
        storage = firebase.storage()

        # Guardar la imagen localmente
        file_path = "temp_image.jpg"
        cv2.imwrite(file_path, frame)

        # Subir la imagen al almacenamiento
        cloudfilename = f"images/{int(time.time())}.jpg"
        storage.child(cloudfilename).put(file_path)

        # Obtener la URL de la imagen
        url = storage.child(cloudfilename).get_url(None)

        # Eliminar el archivo local
        os.remove(file_path)

        return url

    def count_people(self, detections, model):
        return sum(1 for _, confidence, class_id, _ in detections if model.model.names[class_id] == "person")

    def send_email(self, email_receiver, image_url):
        em = EmailMessage()
        em["From"] = "losshupaia@gmail.com"
        em["To"] = email_receiver
        em["Subject"] = "Aviso cámara de seguridad!"
        em.set_content(f"""
            Se ha visto a una persona sospechosa en el establecimiento. Tomar precaución.

            Imagen de la persona: {image_url}
        """)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login("losshupaia@gmail.com", os.getenv("PASSWORD"))
            smtp.sendmail("losshupaia@gmail.com", email_receiver, em.as_string())

    def save_data_to_firestore(self, email_receiver, image_url):
        # Configuración de Firebase para el almacenamiento
        cred = credentials.Certificate("securitycameraia-firebase-adminsdk-h6reg-bc82044a45.json")
        initialize_app(cred, {'storageBucket': 'securitycameraia.appspot.com'})

        detections_ref = firestore.client().collection('detections')

        detections_ref.add({
            'timestamp': int(time.time()),
            'correo': email_receiver,
            'imageUrl': image_url,
        })


def main():
    root = tk.Tk()
    app = SecurityApp(root)

    root.mainloop()

if __name__ == "__main__":
    main()
