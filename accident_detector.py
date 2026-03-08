import cv2
from ultralytics import YOLO
import time
import os
import math
from telegram_alert import send_alert

model = YOLO("model/yolov8n.pt")

cap = cv2.VideoCapture(0)

folder = "accidents"

if not os.path.exists(folder):
    os.makedirs(folder)

vehicle_classes = [2,3,5,7]

previous_centers = {}

def check_collision(box1, box2):

    x1,y1,x2,y2 = box1
    x1b,y1b,x2b,y2b = box2

    if x1 < x2b and x2 > x1b and y1 < y2b and y2 > y1b:
        return True
    return False

while True:

    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame)

    boxes_list = []
    centers = []

    for r in results:

        if r.boxes is not None:

            for box in r.boxes:

                cls = int(box.cls[0])

                if cls in vehicle_classes:

                    x1,y1,x2,y2 = map(int, box.xyxy[0])

                    boxes_list.append((x1,y1,x2,y2))

                    cx = int((x1+x2)/2)
                    cy = int((y1+y2)/2)

                    centers.append((cx,cy))

                    cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)

    # COLLISION DETECTION
    collision = False

    for i in range(len(boxes_list)):
        for j in range(i+1,len(boxes_list)):

            if check_collision(boxes_list[i],boxes_list[j]):
                collision = True

    # SPEED DETECTION
    high_speed = False

    for i,center in enumerate(centers):

        if i in previous_centers:

            px,py = previous_centers[i]

            dist = math.sqrt((center[0]-px)**2 + (center[1]-py)**2)

            if dist > 50:   # speed threshold
                high_speed = True

        previous_centers[i] = center

    # ACCIDENT CONDITION
    if collision and high_speed:

        filename = f"{folder}/accident_{int(time.time())}.jpg"

        cv2.imwrite(filename, frame)

        print("🚨 Accident detected")

        send_alert("🚨 Accident Detected!", filename)

        time.sleep(10)

    cv2.imshow("Accident Detection AI", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()