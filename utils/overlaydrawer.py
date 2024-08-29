import cv2


class OverlayDrawer:
    @staticmethod
    def temper(frame, loc, value):
        color=(255, 255, 255)
        
        x, y = loc
        
        cv2.line(frame, (x - 20, y), (x - 5, y), color, 1)
        cv2.line(frame, (x + 5, y), (x + 20, y), color, 1)
        cv2.line(frame, (x, y - 20), (x, y - 5), color, 1)
        cv2.line(frame, (x, y + 5), (x, y + 20), color, 1)
        
        cv2.circle(frame, (x, y), 5, color, 1)
        
        cv2.putText(frame, value, (x + 20, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    @staticmethod
    def bbox(frame, bbox, label, color=(255, 0, 0)):
        (x, y), (w, h) = bbox
            
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 1)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
