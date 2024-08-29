import cv2
import numpy as np


Conf_threshold = 0.1
NMS_threshold = 0.1

net = cv2.dnn.readNet('model/yolov4-tiny.weights', 'model/yolov4-tiny.cfg')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)

model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(160, 120), scale=1/255, swapRB=True)

class ObjectDetector:
    def __init__(self):
        self.fire_limit = 50
        self.fire_cont = None
        
        self.boxes = None
        self.scores = None
        self.classes = None
        
        self.detected = False
        
        self.class_name = []
        with open('model/classes.txt', 'r') as f:
            self.class_name = [cname.strip() for cname in f.readlines()]
        
        self.colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0),
                       (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    
    def detect_person(self, frame):
        self.classes, self.scores, self.boxes = model.detect(frame, Conf_threshold, NMS_threshold)
        self.detected = True
        
    def detect_fire(self, frame, data):
        if data > self.fire_limit:
            mask = frame > self.fire_limit
            self.fire_cont, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
