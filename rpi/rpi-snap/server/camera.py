import time
import picamera
import picamera.array
import io
import threading
import datetime
import numpy as np
import PIL.Image

minimum_still_interval = 5


       
    
class NullOutput(object):
    def write(self, buf):
        pass

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = threading.Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = bytearray(self.buffer.getvalue())
                if len(self.frame)>0:  # Ignore empty image as Chrome doesn't handle it                    
                    self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)
    
    def get_frame(self):
        with self.condition:           
            self.condition.wait()
            frame = self.frame
        return frame



 

# From https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons/33201#33201
class Singleton(type):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls.instance = None 

    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance

class MyClass(object):
    __metaclass__ = Singleton

    
    

class Camera(object):
    client_count=0
    motion_output=None
    front_camera=None
    output_stream  = StreamingOutput()
    output_stream2 = StreamingOutput()
    motion_detected = False
    motion_magnitude = None
    last_still_capture_time = datetime.datetime.now()
    motion=0.0

    # The 'analyse' method gets called on every frame processed while picamera
    # is recording h264 video.
    # It gets an array (see: "a") of motion vectors from the GPU.
    class DetectMotion(picamera.array.PiMotionAnalysis):
        def analyse(self, a):
            if datetime.datetime.now() > Camera.last_still_capture_time + \
                datetime.timedelta(seconds=minimum_still_interval):
                Camera.motion_magnitude = np.sqrt((np.square(a['x'].astype(np.float)) +np.square(a['y'].astype(np.float))
                                           )*255.0/85).clip(0, 255).astype(np.uint8)
                Camera.motion = Camera.motion_magnitude.sum()
                
                #Camera.motion_magnitude = (a['sad']/4).clip(0, 255).astype(np.uint8)
                #amera.motion_magnitude = (a['x']).astype(np.uint8)
                #Camera.motion_magnitude = np.sqrt(
                #            np.square(a['x'].astype(np.float)) +
                #            np.square(a['y'].astype(np.float))
                #            ).clip(0, 255).astype(np.uint8)
                
                #Camera.motion_magnitude = np.dstack((a['x'],a['x'],a['y']))
                  
                #rgbArray = np.zeros((320/16,240/16,3), 'uint8')
                #rgbArray[..., 0] = 1*256
                #rgbArray[..., 1] = 2*256
                #rgbArray[..., 2] = 3*256
                #Camera.motion_magnitude = rgbArray
                
                # experiment with the following "if" as it may be too sensitive ???
                # if there're more than 10 vectors with a magnitude greater
                # than 60, then motion was detected:
                if Camera.motion > 200:
                    Camera.motion_detected = True
                else:
                    Camera.motion_detected = False
                    
    def open_camera(): 
        if Camera.front_camera is not None: return
        try:
            Camera.front_camera = picamera.PiCamera(resolution = (640, 480), framerate = 6)
            Camera.motion_output = Camera.DetectMotion(Camera.front_camera)
            Camera.front_camera.start_recording(Camera.output_stream, format='mjpeg', resize=(320, 240), splitter_port=1)
            Camera.front_camera.start_recording(Camera.output_stream2, format='mjpeg', resize=(160, 120), splitter_port=3)
            Camera.front_camera.start_recording(NullOutput(), format='h264', 
                                                motion_output=Camera.motion_output, splitter_port=2)
            print("Camera Starting recording")
            Camera.front_camera.wait_recording(1)
            #Camera.front_camera.annotate_text = "R2D2"
            #Camera.front_camera.annotate_background = picamera.Color('black')

        except:
            if Camera.front_camera is not None:
                Camera.front_camera.close()
                Camera.front_camera = None
           
        
    def __init__(self):
        Camera.open_camera()
        Camera.client_count += 1
        print(Camera.client_count)


    def __del__(self):
        Camera.client_count -= 1        
        print(Camera.client_count)
        if Camera.client_count <= 0:
            Camera.client_count = 0 
            #Camera.front_camera.stop_recording(splitter_port=1)
            #Camera.front_camera.stop_recording(splitter_port=2)
            #print("Camera Stopping recording")
        
    def get_frame(self, mode='320x240'):
        if mode=='320x240':
            frame = Camera.output_stream.get_frame()
        elif mode=='160x120':
            frame = Camera.output_stream2.get_frame()
        elif mode=='motion' or mode=='motion-saturated':
            with Camera.output_stream.condition:           
                Camera.output_stream.condition.wait()
                #print(Camera.motion_magnitude.shape)
                if mode=='motion':
                    img = PIL.Image.fromarray(Camera.motion_magnitude)
                else:
                    img = PIL.Image.fromarray(np.where(Camera.motion_magnitude>0,255,0))
                buffer = io.BytesIO()
                buffer.seek(0)           
                img.save(buffer, format="jpeg")
                buffer.truncate()
                frame = buffer.getvalue()
        else:
            frame = None
        return frame
    