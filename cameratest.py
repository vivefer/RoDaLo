import pyrealsense2 as rs
import numpy as np
import time

# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()

# Configure streams
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

try:
    # Start streaming
    pipeline.start(config)
    print("RealSense pipeline started. Press Ctrl+C to stop.")
    
    while True:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            print("No depth frame received. Skipping...")
            continue

        # Convert depth frame to numpy array
        depth_image = np.asanyarray(depth_frame.get_data())
        
        # Print a summary of the depth image
        print(f"Frame captured. Depth image shape: {depth_image.shape}")
        
        # Wait a second to simulate saving or processing
        time.sleep(1)

except Exception as e:
    print(f"Error: {e}")
finally:
    pipeline.stop()
    print("RealSense pipeline stopped.")
