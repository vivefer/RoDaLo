import pyrealsense2 as rs
import numpy as np
import matplotlib.pyplot as plt
import os
import time
import threading
import shutil

# Directory for saving PNG images
output_dir = "depth_images_matplotlib"
os.makedirs(output_dir, exist_ok=True)

# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()

# Configure streams
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Start streaming
pipeline.start(config)

# Global stop flag
stop_flag = False

def stop_listener():
    """Listen for the stop command from the user."""
    global stop_flag
    input("Press Enter to stop...\n")
    stop_flag = True

# Start stop listener in a separate thread
thread = threading.Thread(target=stop_listener, daemon=True)
thread.start()

def check_disk_space():
    """Check if there's enough disk space."""
    total, used, free = shutil.disk_usage(".")
    free_mb = free // (1024 * 1024)
    print(f"Disk space available: {free_mb} MB")
    return free_mb > 100  # Require at least 100 MB free

try:
    print("Streaming started. Press Enter to stop.")
    frame_count = 0

    while not stop_flag:
        if not check_disk_space():
            print("Insufficient disk space! Stopping...")
            break

        try:
            # Wait for frames
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()

            if not depth_frame:
                print("No depth frame received. Skipping...")
                continue

            # Convert depth frame to numpy array
            depth_image = np.asanyarray(depth_frame.get_data())

            # Normalize the depth image to the range 0 to 3 meters
            depth_image_normalized = np.clip(depth_image, 0, 3000) / 1000  # Convert to meters (0-3m)

            # Save visualized depth image as PNG using Matplotlib
            depth_path = os.path.join(output_dir, f"depth_frame_{frame_count:04d}.png")
            plt.figure(figsize=(8, 6))
            plt.imshow(depth_image_normalized, cmap='cubehelix', vmin=0, vmax=3)
            plt.colorbar(label='Depth (m)')
            plt.title(f"Depth Image {frame_count}")
            plt.savefig(depth_path)
            plt.close()
            print(f"Saved depth image visualization as PNG: {depth_path}")

            frame_count += 1
            time.sleep(1)

        except Exception as e:
            print(f"Error during processing frame {frame_count}: {e}")
            continue

except Exception as e:
    print(f"Critical error: {e}")

finally:
    pipeline.stop()
    print("Streaming stopped.")
