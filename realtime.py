import pyrealsense2 as rs
import numpy as np
import open3d as o3d

# Initialize RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()

# Configure streams
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

# Create point cloud object
pc = rs.pointcloud()

try:
    while True:
        # Wait for frames
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        if not depth_frame:
            print("No depth frame received. Skipping...")
            continue

        # Convert depth frame to numpy array
        depth_image = np.asanyarray(depth_frame.get_data())
        
        # Print full depth image shape and sample portion
        print(f"Depth image shape: {depth_image.shape}")  # Should be (480, 640)
        print(f"Depth image sample (top-left 5x5):\n{depth_image[:5, :5]}")  # Sample 5x5 portion for inspection
        
        # Visualize the depth image
        import matplotlib.pyplot as plt
        plt.imshow(depth_image, cmap='cubehelix')
        plt.title("Depth Image Visualization")
        plt.colorbar()
        plt.show()

        # Check if depth image contains valid data
        if np.all(depth_image == 0):
            print("Depth image contains only zeros! Skipping...")
            continue

        # Generate point cloud
        points = pc.calculate(depth_frame)
        vertices = np.asanyarray(points.get_vertices()).view(np.float32).reshape(-1, 3)

        # Filter out invalid points (points where depth is 0 or very far away)
        valid_points = vertices[np.all(vertices != 0, axis=1)]

        print(f"Valid Vertices shape: {valid_points.shape}")
        print(f"Sample valid vertices:\n{valid_points[:5]}")

        if valid_points.shape[0] == 0:
            print("No valid points! Skipping...")
            continue

        # Visualize with Open3D
        o3d_pc = o3d.geometry.PointCloud()
        o3d_pc.points = o3d.utility.Vector3dVector(valid_points)
        o3d.visualization.draw_geometries([o3d_pc])

finally:
    pipeline.stop()