import flask
import time

import Robot # Import the Robot.py file (must be in the same directory as this file!).
robot = Robot.Robot(body_id=1, left_id=3, right_id=2, left_trim=0, right_trim=0)


app = flask.Flask(__name__)

#######################################################################################
# Robot control end-point

@app.route('/base', methods = ['GET', 'PATCH'] )
def base():
    if flask.request.method == 'GET':
        return "ECHO: GET\n"

    elif flask.request.method == 'PATCH':
        arg=flask.request.json
        app.logger.debug('move base left=%s right=%s duration=%s', arg["left"],arg["right"],arg["duration"])
        robot._right_speed(int(arg["right"]))
        robot._left_speed(int(arg["left"]))
        time.sleep(float(arg["duration"]))
        robot.stop()
        return flask.json.dumps(flask.request.json)



#######################################################################################
# URL End-point for serving an off-line version of SNAP!
@app.route('/snap/')
def index():
    return flask.send_from_directory('static', 'index.html')

@app.route('/snap/<path:path>')
def show_user(path):
    return flask.send_from_directory('static', path)

if __name__ == "__main__":
    app.run(host= '0.0.0.0', port=80, debug=True)


