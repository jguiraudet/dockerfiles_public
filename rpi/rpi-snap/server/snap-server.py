#!/usr/bin/env python
from camera import Camera
import time
import flask
import robot # Import the robot.py file (must be in the same directory as this file!).

robot = robot.Robot(body_id=1, left_id=3, right_id=2, left_trim=0, right_trim=0)


app = flask.Flask(__name__)

#######################################################################################
# Camera end-point


def gen(camera, mode='320x240'):
    next_refresh=0
    while True:
        frame = camera.get_frame(mode)
        # Drop the frames for 1 sec. if no motion detected
        if camera.motion_detected or next_refresh<time.time():
            next_refresh=time.time()+1.0
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.route('/camera/')
def camera():
    return flask.render_template('index.html')

@app.route('/camera/320x240.jpg')
def camera_320x240():
    return flask.Response(Camera().get_frame(mode='320x240'), mimetype='image/jpeg')

@app.route('/camera/160x120.jpg')
def camera_160x120():
    return flask.Response(Camera().get_frame(mode='160x120'), mimetype='image/jpeg')

@app.route('/camera/motion.jpg')
def camera_motion():
    return flask.Response(Camera().get_frame(mode='motion'), mimetype='image/jpeg')

@app.route('/camera/320x240.mjpg')
def video_feed_320x240():
    return flask.Response(gen(Camera(),mode='320x240'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera/160x120.mjpg')
def video_feed_160x120():
    return flask.Response(gen(Camera(),mode='160x120'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera/motion.mjpg')
def video_feed_motion():
    return flask.Response(gen(Camera(),mode='motion'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera/motion-saturated.mjpg')
def video_feed_motion_saturated():
    return flask.Response(gen(Camera(),mode='motion'),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/snap/camera/motion')
def video_motion():
    return flask.Response(str(Camera.motion),
                    mimetype='text/plain')


@app.route('/snap/camera/recording', methods = ['GET', 'POST'] )
def recording():
    if flask.request.method == 'GET':
        return "ECHO: GET\n"
    elif flask.request.method == 'POST':
        if request.headers['Content-Type'] == 'text/plain':
            Camera.recording(request.data)


#######################################################################################
# Robot control end-point

@app.route('/snap/led/<int:index>', methods = ['GET', 'PATCH'] )
def led(index):
    if flask.request.method == 'GET':
        return str(robot.get_led(index))
    elif flask.request.method == 'PATCH':
        arg=flask.request.json
        if 0<= index <=3:
            value=max(0,min(4096,int(arg["value"])))
            robot.set_led(index, value)
            return flask.json.dumps(flask.request.json)
        else:
            flask.abort(404)


@app.route('/snap/base', methods = ['GET', 'PATCH'] )
def base():
    if flask.request.method == 'GET':
        return "ECHO: GET\n"

    elif flask.request.method == 'PATCH':
        arg=flask.request.json
        app.logger.debug('move base left=%s right=%s duration=%s', arg["left"],arg["right"],arg["duration"])
        duration = float(arg["duration"])
        
        robot._right_speed(int(arg["right"]))
        robot._left_speed(int(arg["left"]))
        if 0<duration and duration<20.0:
            time.sleep(duration)
            robot.stop()
        elif duration==0:
            # Infinite motion
            pass
        return flask.json.dumps(flask.request.json)

@app.route('/snap/body', methods = ['GET', 'PATCH'] )
def body():
    if flask.request.method == 'GET':
        return "ECHO: GET\n"

    elif flask.request.method == 'PATCH':
        arg=flask.request.json
        app.logger.debug('move body speed=%s position=%s', arg["speed"],arg["position"])
        robot.body(int(arg["speed"]), int(arg["position"]))
        return flask.json.dumps(flask.request.json)



#######################################################################################
# URL End-point for Network management
# /proc/net/wireless

#######################################################################################
# URL End-point for serving an off-line version of SNAP!
@app.route('/snap/')
def snap():
    return flask.send_from_directory('static', 'index.html')

@app.route('/snap/<path:path>')
def snap_static(path):
    return flask.send_from_directory('static', path)

#######################################################################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
