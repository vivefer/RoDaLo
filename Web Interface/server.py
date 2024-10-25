from flask import Flask, render_template
from flask_socketio import SocketIO
import socket
import tkinter as tk
from tkinter import messagebox
import random
import numpy as np
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode = "threading")

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
# Function to show a dialog box with the IP address
def show_ip_dialog(ip_address):
    # Create a Tkinter root window and hide it (we only want the dialog)
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    
    # Show the messagebox with the IP address and connection info
    message = f"Connect to {ip_address}:5000 to view the page."
    messagebox.showinfo("Web Server Info", message)

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
     # Get the Raspberry Pi's IP address
    local_ip = get_local_ip()

    # Show the IP address dialog box on the Raspberry Pi
    show_ip_dialog(local_ip)

    # Run Flask-SocketIO with the Pi's IP address
    socketio.run(app, host='0.0.0.0', port=5000)
