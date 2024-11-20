import pyrealsense2 as rs
import numpy as np
import cv2
import os
import time
import threading
import shutil

# Directory for saving PNG images
output_dir = "depth_images_png"
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

            # Normalize depth image to 0-255 range for saving as PNG
            depth_image_normalized = cv2.normalize(depth_image, None, 0, 255, cv2.NORM_MINMAX)
            depth_image_normalized = depth_image_normalized.astype(np.uint8)

            # Save depth image as PNG
            depth_path = os.path.join(output_dir, f"depth_frame_{frame_count:04d}.png")
            cv2.imwrite(depth_path, depth_image_normalized)
            print(f"Saved depth image as PNG: {depth_path}")

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
