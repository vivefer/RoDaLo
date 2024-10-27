import serial
import random
import socket
import io
import base64
from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
import plotly.io as pio
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D

# Initialize Flask app
app = Flask(__name__)

# Serial ports for Arduinos (if connected)
try:
    arduino_ultrasonic = serial.Serial('COM6', 9600, timeout=1)
except:
    arduino_ultrasonic = None  # No Arduino connected

try:
    arduino_lidar = serial.Serial('COM7', 9600, timeout=1)
except:
    arduino_lidar = None  # No Arduino connected

# Gantry settings and initial plot data
gantry_dimensions = {'x': 100, 'y': 1000, 'z': 50}
data_step_settings = {'x_step': 5, 'y_step': 5}
plot_data = {'x': [], 'y': [], 'z': []}  # Store points for real-time plot

# Function to read serial data or generate random data
def read_serial_data():
    data_source = {'ultrasonic': 'random', 'lidar': 'random'}
    if arduino_ultrasonic and arduino_ultrasonic.in_waiting > 0:
        ultrasonic_data = float(arduino_ultrasonic.readline().decode('utf-8').strip())
        data_source['ultrasonic'] = 'sensor'
    else:
        ultrasonic_data = random.uniform(0, gantry_dimensions['z'] / 2)

    if arduino_lidar and arduino_lidar.in_waiting > 0:
        lidar_data = float(arduino_lidar.readline().decode('utf-8').strip())
        data_source['lidar'] = 'sensor'
    else:
        lidar_data = ultrasonic_data + random.uniform(0, gantry_dimensions['z'] / 2)

    z_axis_height = lidar_data - ultrasonic_data
    return ultrasonic_data, lidar_data, z_axis_height, data_source

# Route for home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for data page
@app.route('/data')
def data():
    return render_template('data.html', dimensions=gantry_dimensions, steps=data_step_settings)

# Route for plot page
@app.route('/plot')
def plot():
    return render_template('plot.html')

# Route for updating gantry dimensions
@app.route('/update-dimensions', methods=['POST'])
def update_dimensions():
    gantry_dimensions.update({key: int(val) for key, val in request.form.items()})
    return jsonify(status='success', dimensions=gantry_dimensions)

# Route to get sensor data
# Route to get sensor data with x and y stepping pattern
@app.route('/get-data', methods=['GET'])
def get_data():
    ultrasonic, lidar, z_height, source = read_serial_data()

    # Update x and y according to step pattern
    x_count = len(plot_data['x']) % (gantry_dimensions['x'] // data_step_settings['x_step'])
    y_count = len(plot_data['x']) // (gantry_dimensions['x'] // data_step_settings['x_step']) % (gantry_dimensions['y'] // data_step_settings['y_step'])

    # Calculate new x and y positions
    x_position = x_count * data_step_settings['x_step']
    y_position = y_count * data_step_settings['y_step']
    
    # Append new data points in the sequence of y-steps for each x-step
    plot_data['x'].append(x_position)
    plot_data['y'].append(y_position)
    plot_data['z'].append(z_height)

    return jsonify(
        ultrasonic=ultrasonic, lidar=lidar, z_axis_height=z_height,
        data_source=source, plot_data=plot_data
    )

# Route to generate and get the scatter plot image with adjusted x-y orientation
@app.route('/plot-image', methods=['POST'])
def plot_image():
    width = int(request.json.get('width', 800))
    height = int(request.json.get('height', 600))

    fig = go.Figure()
    # Swapping x and y for scatter plot to match surface plot orientation
    fig.add_trace(go.Scatter3d(
        x=plot_data['y'],  # swapped x and y
        y=plot_data['x'],  # swapped x and y
        z=plot_data['z'],
        mode='markers',
        marker=dict(size=5, color='blue')
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Y-axis (mm)',  # Adjusted titles for new orientation
            yaxis_title='X-axis (mm)',
            zaxis_title='Z-axis (mm)',
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=1)
        ),
        width=width,
        height=height,
        title='Real-Time 3D Scatter Plot with Adjusted Orientation'
    )

    buf = io.BytesIO()
    pio.write_image(fig, buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf8')

    return jsonify(image='data:image/png;base64,' + image_base64)

@app.route('/surface-plot-image', methods=['POST'])
def surface_plot_image():
    width = int(request.json.get('width', 800))
    height = int(request.json.get('height', 600))

    # Only proceed if there are enough points to start forming a surface
    if len(plot_data['x']) < 3:
        return jsonify(image='data:image/png;base64,' + '')

    fig = go.Figure()

    # Creating a Mesh3d plot, updating with available data
    fig.add_trace(go.Mesh3d(
        x=plot_data['x'],
        y=plot_data['y'],
        z=plot_data['z'],
        color='lightblue',
        opacity=0.6,
        alphahull=5,  # Smooths the mesh by creating a tighter hull around points
    ))

    fig.update_layout(
        scene=dict(
            xaxis_title='X-axis (mm)',
            yaxis_title='Y-axis (mm)',
            zaxis_title='Z-axis (mm)',
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.5)  # Adjusted z aspect ratio for better viewing
        ),
        width=width,
        height=height,
        title='Incremental Real-Time 3D Surface Plot'
    )

    buf = io.BytesIO()
    pio.write_image(fig, buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf8')

    return jsonify(image='data:image/png;base64,' + image_base64)
# Function to get local IP address
def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = 'localhost'
    finally:
        s.close()
    return ip_address

# Run the application
if __name__ == '__main__':
    host_ip = get_ip_address()
    print(f"Server starting... Access the interface at http://{host_ip}:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
