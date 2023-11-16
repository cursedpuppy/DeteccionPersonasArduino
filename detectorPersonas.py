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

email_sender = "losshupaia@gmail.com"
password = os.getenv("PASSWORD")
email_receiver = "vicente.scheihing@gmail.com"

subject = "Aviso cámara de seguridad!"
body = """
    Se ha visto a una persona sospechosa en el establecimiento. Tomar chela o precaucion, la wea que querai.
"""

em = EmailMessage()
em["From"] = email_sender
em["To"] = email_receiver
em["Subject"] = subject
em.set_content(body)

context = ssl.create_default_context()

ZONE_POLYGON = np.array([
    [0, 0],
    [1280, 0],
    [1250, 720],
    [0, 720]
])

def count_people(detections, model):
    return sum(1 for _, confidence, class_id, _ in detections if model.model.names[class_id] == "person")

def send_email():
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

def main():
    cap = cv2.VideoCapture(0)
    
    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=2,
        text_scale=1
    )

    model = YOLO("yolov8n.pt")

    zone = sv.PolygonZone(polygon=ZONE_POLYGON, frame_resolution_wh=(1280, 720))
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

        count = count_people(detections, model)
        cv2.putText(frame, f"People: {count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        zone.trigger(detections=detections)
        frame = zone_annotator.annotate(scene=frame)

        cv2.imshow("yolov8", frame)

        if count > 0:
            person_count += 1

        if person_count >= 10:
            print("------------------Correo enviado xd---------------")
            print("------------------Cuenta reiniciad------------------")
            person_count = 0
            send_email()

            

        if cv2.waitKey(1000) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
