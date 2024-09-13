from flask import Flask, render_template
from flask_socketio import SocketIO
import random
import numpy as np
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Automatically get Raspberry Pi's local IP address
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external IP to get the local IP address
        s.connect(('8.8.8.8', 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = '127.0.0.1'  # Fallback to localhost if it fails
    finally:
        s.close()
    return ip_address

@app.route('/')
def index():
    local_ip = get_local_ip()  # Get the Pi's local IP address
    return render_template('index.html', ip_address=local_ip)


def generate_data():
    while True:
        # Simulate sensor data
        flow_rate = random.uniform(0, 10)
        x_coord = random.uniform(0, 100)
        y_coord = random.uniform(0, 100)
        z_coord = random.uniform(0, 100)

        # Simulate sand bed data
        X, Y = np.linspace(0, 1, 100).tolist(), np.linspace(0, 0.5, 50).tolist()
        Z = (np.random.rand(50, 100) * 0.1).tolist()

        # Send data to the client
        socketio.emit('sensor_data', {
            'flow_rate': flow_rate,
            'coordinates': {'x': x_coord, 'y': y_coord, 'z': z_coord},
            'sand_bed': {'X': X, 'Y': Y, 'Z': Z}
        })

        # Simulate delay
        time.sleep(1)

@socketio.on('connect')
def on_connect():
    socketio.start_background_task(generate_data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
    '''we need to enter real time raspberry ip address for now, both here and in the index file'''
