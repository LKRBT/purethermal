import sys
import cv2
import time
import pygame

from .camerahandler import CameraHandler

    
class ViewHandler:
    def __init__(self, cfg):
        self.cfg =cfg
    
        pygame.init()
        infoObject = pygame.display.Info()
        self.size = (infoObject.current_w, infoObject.current_h)
        self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        
        self.cam = CameraHandler(self.size)
        
    def run(self):
        running = True
        self.cam.picam2.start()
        while running:
            rgb, ir = self.cam.capture()
            
            view_ir = self.cam.process_ir(ir)
            view_rgb = self.cam.process_rgb(rgb)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == ord('q'):
                        running = False
                    if event.key == ord('c'):
                        save_rgb = cv2.cvtColor(view_rgb, cv2.COLOR_RGB2BGR)
                        save_ir = cv2.cvtColor(view_ir, cv2.COLOR_RGB2BGR)
                        
                        cv2.imwrite(self.cfg['PI']['FILE_PATH'] + 'ir_' + str(time.time()) + '.png', save_ir)
                        cv2.imwrite(self.cfg['PI']['FILE_PATH'] + 'rgb_' + str(time.time()) + '.png', save_rgb)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(event.button)
                    if event.button == 3:
                        running = False

            rgb = pygame.surfarray.make_surface(view_rgb.swapaxes(0, 1))
            ir = pygame.surfarray.make_surface(view_ir.swapaxes(0, 1))
	
            self.screen.fill((0, 0, 0))
            self.screen.blit(rgb, (0, 0))
            self.screen.blit(ir, (self.size[0] / 2, 0))
            pygame.display.flip()
	
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()
