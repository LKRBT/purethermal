import cv2
import numpy as np

from picamera2 import Picamera2
from purethermal.thermalcamera import ThermalCamera

from .overlaydrawer import OverlayDrawer
from .objectdetector import ObjectDetector

                
class CameraHandler:
    def __init__(self, size):
        self.size_w, self.size_h = size
        
        self.obj = ObjectDetector()

        self.picam2 = Picamera2()
        self.ircam = ThermalCamera()
        
        self.ir_dims = (160, 120)
        self.new_dims = (int(self.size_w/2), self.size_h)
    
    def check_for_fire(self, data):
        temper = (data - 27315) / 100.0
        temper = temper.reshape(120, 160)
        
        _, max_val, _, max_loc = cv2.minMaxLoc(temper)
        
        self.obj.detect_person(temper)
        self.obj.detect_fire(temper, max_val)
                    
        return "{:.2f}C".format(max_val), max_loc
    
    def capture(self):
        ir = self.ircam.capture()
        rgb = self.picam2.capture_array("main")
        
        return rgb, ir
    
    def scale_loc(self, loc):
        return int(loc[0] * self.size_w / 2 / self.ir_dims[0]), int(loc[1] * self.size_h / self.ir_dims[1])
    
    def scale_bbox(self, bbox):
        return self.scale_loc((bbox[0], bbox[1])), self.scale_loc((bbox[2], bbox[3]))
        
    def process_ir(self, frame):
        frame = cv2.flip(frame, -1)
        
        val, loc = self.check_for_fire(frame)
        
        cv2.normalize(frame, frame, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(frame, 8, frame)
        frame = np.uint8(frame)
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_PLASMA)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, self.new_dims, interpolation=cv2.INTER_NEAREST)
        
        OverlayDrawer.temper(frame, 
                             self.scale_loc(loc), 
                             val)
        
        if self.obj.fire_cont:
            for contour in self.obj.fire_cont:
                OverlayDrawer.bbox(frame, 
                                   self.scale_bbox(cv2.boundingRect(contour)), 
                                   "fire")
                   
            self.obj.fire_cont = None
        
        if self.obj.human_cont:
            for contour in self.obj.human_cont:
                OverlayDrawer.bbox(frame, 
                                   self.scale_bbox(cv2.boundingRect(contour)), 
                                   "person")
                
            self.obj.human_cont = []
            
        return frame
	
    def process_rgb(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
        frame = cv2.resize(frame, self.new_dims, interpolation=cv2.INTER_NEAREST)
        
        return frame
