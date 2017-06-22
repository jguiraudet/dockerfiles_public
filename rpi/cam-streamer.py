import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
import signal
import numpy as np
import picamera
import picamera.array
import datetime
import logging
import PIL.Image


logging.basicConfig(level=logging.INFO, format="%(message)s")
LOG = logging.getLogger("capture_motion")

def signal_term_handler(signal, frame):
  LOG.info('shutting down ...')
  # this raises SystemExit(0) which fires all "try...finally" blocks:
  sys.exit(0)

# this is useful when this program is started at boot via init.d
# or an upstart script, so it can be killed: i.e. kill some_pid:
signal.signal(signal.SIGTERM, signal_term_handler)

minimum_still_interval = 5
motion_detected = False
last_still_capture_time = datetime.datetime.now()



# The 'analyse' method gets called on every frame processed while picamera
# is recording h264 video.
# It gets an array (see: "a") of motion vectors from the GPU.
class DetectMotion(picamera.array.PiMotionAnalysis):
  def analyse(self, a):
    global minimum_still_interval, motion_detected, last_still_capture_time, motion_magnitude
    if datetime.datetime.now() > last_still_capture_time + \
        datetime.timedelta(seconds=minimum_still_interval):
      #motion_magnitude = np.sqrt(np.square(a['x'].astype(np.float)) +np.square(a['y'].astype(np.float))
      #        ).clip(0, 255).astype(np.uint8)
      motion_magnitude = (a['sad']/8).clip(0, 255).astype(np.uint8)
      # experiment with the following "if" as it may be too sensitive ???
      # if there're more than 10 vectors with a magnitude greater
      # than 60, then motion was detected:
      if (motion_magnitude > 60).sum() > 10:
        LOG.info('motion detected at: %s' % datetime.datetime.now().strftime('%Y-%m-%dT%H.%M.%S.%f'))
        motion_detected = True

        
        



PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="stream.mjpg" width="640" height="480" />
</body>
</html>
"""

class NullOutput(object):
    def write(self, buf):
        pass

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

    
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        elif self.path == '/capture.jpg':
            self.jpeg_header()
            with output.condition:
                output.condition.wait()
                frame = output.frame
            self.wfile.write(frame)
        elif self.path == '/640x480.jpg':
            self.do_capture(640, 480)
        elif self.path == '/320x240.jpg':
            self.do_capture(320, 240)
        elif self.path == '/motion.jpg':
            self.do_motion()
        elif self.path == '/motion_stream.mjpg':
            self.do_motion_stream()
        else:
            self.send_error(404)
            self.end_headers()

    def jpeg_header(self):
        self.send_response(200)
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type', 'image/jpeg')
        self.end_headers()
        
    def do_capture(self, resx, resy):
        self.jpeg_header()
        camera.capture(self.wfile, 'jpeg', resize=(resx, resy))
        
    def do_motion(self):
        self.jpeg_header()
        img = PIL.Image.fromarray(motion_magnitude)
        img.save(self.wfile, format="jpeg")
        

    def do_motion_stream(self):
        buffer = io.BytesIO()
        self.send_response(200)
        self.send_header('Age', 0)
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
        self.end_headers()
        try:
            while True:
                with output.condition:
                    output.condition.wait()              
                img = PIL.Image.fromarray(motion_magnitude)
                buffer.seek(0)           
                img.save(buffer, format="jpeg")
                buffer.truncate()
                frame = buffer.getvalue()
                
                self.wfile.write(b'--FRAME\r\n')
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Length', len(frame))
                self.end_headers()
                self.wfile.write(frame)
                self.wfile.write(b'\r\n')
        except Exception as e:
            logging.warning('Removed streaming client %s: %s',
                            self.client_address, str(e))


        
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    with DetectMotion(camera) as motion_output:
        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg', splitter_port=1)
        camera.start_recording(NullOutput(), format='h264', motion_output=motion_output, splitter_port=2)
        try:
            address = ('', 8000)
            server = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            camera.stop_recording(splitter_port=1)
            camera.stop_recording(splitter_port=2)
