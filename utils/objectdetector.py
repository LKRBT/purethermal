import cv2
import numpy as np


class ObjectDetector:
    def __init__(self):
        self.fire_limit = 50
        self.fire_cont = None
        
        self.human_cont = []
        self.human_limit = (32, 42)
        
        self.area_limit = 1000
        
    def detect_person(self, frame):
        mask = cv2.inRange(frame, self.human_limit[0], self.human_limit[1])
        conts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cont in conts:
            area = cv2.contourArea(cont)
            if area > self.area_limit:
                self.human_cont.append(cont)
    
    def detect_fire(self, frame, data):
        if data > self.fire_limit:
            mask = frame > self.fire_limit
            self.fire_cont, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
