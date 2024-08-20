import numpy as np

from queue import Queue
from .uvctypes import *


class ThermalCamera:
    def __init__(self):
        self.BUF_SIZE = 2
        self.streaming = False
        
        self.q = Queue(self.BUF_SIZE)
        self.ctrl = uvc_stream_ctrl()
        
        self.dev = POINTER(uvc_device)()
        self.ctx = POINTER(uvc_context)()
        self.devh = POINTER(uvc_device_handle)()
        
        self.init_thermal_data_frames()
        
        self.PTR_PY_FRAME_CALLBACK = CFUNCTYPE(None, POINTER(uvc_frame), c_void_p)(self.py_frame_callback)
    
    def init_thermal_data_frames(self):
        def handle_error(msg):
            print(msg)
            self.cleanup()
            exit(1)
        
        if libuvc.uvc_init(byref(self.ctx), 0) < 0:
            handle_error("uvc_init error")
        
        if libuvc.uvc_find_device(self.ctx, byref(self.dev), PT_USB_VID, PT_USB_PID, 0) < 0:
            handle_error("uvc_find_device error")
        
        if libuvc.uvc_open(self.dev, byref(self.devh)) < 0:
            handle_error("uvc_open error")
        
        print("device opened!")
        
        print_device_info(self.devh)
        print_device_formats(self.devh)
        set_manual_ffc(self.devh)
        
        frame_formats = uvc_get_frame_formats_by_guid(self.devh, VS_FMT_GUID_Y16)
        
        if not frame_formats:
            handle_error("device does not support Y16")
        
        libuvc.uvc_get_stream_ctrl_format_size(
            self.devh, byref(self.ctrl), UVC_FRAME_FORMAT_Y16,
            frame_formats[0].wWidth, frame_formats[0].wHeight,
            int(1e7 / frame_formats[0].dwDefaultFrameInterval))
            
    def py_frame_callback(self, frame, userptr):
        frame = frame.contents
        array_size = frame.width * frame.height
        array_pointer = cast(frame.data, POINTER(c_uint16 * array_size))
        data = np.frombuffer(array_pointer.contents, dtype=np.dtype(np.uint16)).reshape(frame.height, frame.width)
        if frame.data_bytes == 2 * array_size:
            if not self.q.full():
                self.q.put(data)
        
    def cleanup(self):
        if self.streaming:
            self.streaming = False
            libuvc.uvc_stop_streaming(self.devh)
            
        if self.dev:
            libuvc.uvc_unref_device(self.dev)
        
        if self.ctx:
            libuvc.uvc_exit(self.ctx)
    
    def __del__(self):
        self.cleanup()
    
    def capture(self):
        if not self.streaming:
            self.streaming = True
            
            res = libuvc.uvc_start_streaming(self.devh, byref(self.ctrl), self.PTR_PY_FRAME_CALLBACK, None, 0)
            if res < 0:
                print("uvc_start_streaming failed: {0}".format(res))
                exit(1)
                
        try:
            data = self.q.get(True, 500)
            if data is not None:
                return data
        except Exception as e:
            print(e)
            
            return None
            
    def performffc(self):
        perform_manual_ffc(self.devh)

    def print_shutter_info(self):
        print_shutter_info(self.devh)

    def setmanualffc(self):
        set_manual_ffc(self.devh)

    def setautoffc(self):
        set_auto_ffc(self.devh)
