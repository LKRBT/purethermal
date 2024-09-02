import sys
import cv2
import time
import pygame
import numpy as np

from picamera2 import Picamera2
from purethermal.thermalcamera import ThermalCamera


pygame.init()
infoObject = pygame.display.Info()
size_w = infoObject.current_w
size_h = infoObject.current_h
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)

clock = pygame.time.Clock()
clock.tick(60)

class CameraHandler:
    def __init__(self, cfg):
        self.cfg = cfg
        self.picam2 = Picamera2()
        config = self.picam2.create_video_configuration(main={"size": (640, Q480), "format": "RGB888"}, 
                                                        controls={"FrameDurationLimits": (1000000 // 100, 1000000 // 100)})
        self.picam2.configure(config)
	    
        self.ircam = ThermalCamera()
        
        self.ir_res = (160, 120)
        
        self.temp_limit = 50
        self.temp_cont = None
        
    def check_for_fire(self, data, loc=None):
        temper = (data - 27315) / 100.0
        temper = temper.reshape(120, 160)
        
        _, max_val, _, max_loc = cv2.minMaxLoc(temper)
        
        if max_val > self.temp_limit:
            mask = temper > self.temp_limit
        
            self.temp_cont, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
        if loc is not None:
            val = temper[loc[1], loc[0]]
            return "{:.2f}C".format(val)
            
        return "{:.2f}C".format(0)
        
    def capture(self):
        ir = self.ircam.capture()
        rgb = self.picam2.capture_array("main")
        
        return rgb, ir
    
    def process_ir(self, frame, loc=None):
        frame = cv2.flip(frame, -1)
        
        val = self.check_for_fire(frame, loc)
            
        cv2.normalize(frame, frame, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(frame, 8, frame)
        frame = np.uint8(frame)
        frame = cv2.applyColorMap(frame, cv2.COLORMAP_PLASMA)
        frame = cv2.resize(frame, (int(size_w/2), size_h), interpolation=cv2.INTER_NEAREST)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if loc is not None:
            scale_w = int(loc[0] * size_w / 2 / self.ir_res[0])
            scale_h = int(loc[1] * size_h / self.ir_res[1])

            cv2.line(frame, (scale_w - 20, scale_h), (scale_w - 5, scale_h), (255, 255, 255), 1)
            cv2.line(frame, (scale_w + 5, scale_h), (scale_w + 20, scale_h), (255, 255, 255), 1)
            cv2.line(frame, (scale_w, scale_h - 20), (scale_w, scale_h - 5), (255, 255, 255), 1)
            cv2.line(frame, (scale_w, scale_h + 5), (scale_w, scale_h + 20), (255, 255, 255), 1)
            cv2.circle(frame, (scale_w, scale_h), 5, (255, 255, 255), 1)
            cv2.putText(frame, val, (scale_w + 20, scale_h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
        if self.temp_cont is not None:
            for contour in self.temp_cont:
                x, y, w, h = cv2.boundingRect(contour)
            
                x = int(x * size_w / 2 / self.ir_res[0])
                y = int(y * size_h / self.ir_res[1])
                w = int(w * size_w / 2 / self.ir_res[0])
                h = int(h * size_h / self.ir_res[1])
            
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
                cv2.putText(frame, "fire", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                   
            self.temp_cont = None
                
        return frame
	
    def process_rgb(self, frame):
        frame = cv2.resize(frame, (int(size_w/2), size_h), interpolation=cv2.INTER_NEAREST)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return frame

    def loop(self):
        running = True
        self.picam2.start()
        while running:
            rgb, ir = self.capture()
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_x = int((mouse_x - size_w/2)* 160 / (size_w/2))
            mouse_y = int(mouse_y * 120 / size_h)
            
            view_ir = self.process_ir(ir, loc=(mouse_x, mouse_y))
            view_rgb = self.process_rgb(rgb)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == ord('q'):
                        running = False
                    if event.key == ord('c'):
                        save_ir = cv2.cvtColor(view_ir, cv2.COLOR_RGB2BGR)
                        save_rgb = cv2.cvtColor(view_rgb, cv2.COLOR_RGB2BGR)
                        
                        cv2.imwrite(self.cfg['PI']['FILE_PATH'] + 'ir_' + str(time.time()) + '.png', save_ir)
                        cv2.imwrite(self.cfg['PI']['FILE_PATH'] + 'rgb_' + str(time.time()) + '.png', save_rgb) 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(event.button)
                    if event.button == 3:
                        running = False
            
            rgb = pygame.surfarray.make_surface(view_rgb.swapaxes(0, 1))
            ir = pygame.surfarray.make_surface(view_ir.swapaxes(0, 1))
	
            screen.fill((0, 0, 0))
            screen.blit(rgb, (0, 0))
            screen.blit(ir, (size_w/2, 0))
            pygame.display.flip()
	
            clock.tick(60)
            
        pygame.quit()
        sys.exit()
