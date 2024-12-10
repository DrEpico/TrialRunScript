import pyzed.sl as sl
import time
import keyboard
import sys
import math

# Function to calculate GPS-like coordinates
def calculate_new_gps(lat, lon, dx, dy):
    earth_radius = 6378137  # Earth radius in meters

    new_lat = lat + (dy / earth_radius) * (180 / math.pi)
    new_lon = lon + (dx / (earth_radius * math.cos(math.pi * lat / 180))) * (180 / math.pi)

    return new_lat, new_lon


# Initialize camera
zed = sl.Camera()

# Configure camera
init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD1080
init_params.depth_mode = sl.DEPTH_MODE.ULTRA
init_params.coordinate_units = sl.UNIT.METER
init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

# Open the camera
if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
    print("Camera initialization failed.")
    exit(1)

# Enable SVO recording
recording_params = sl.RecordingParameters("output.svo", sl.SVO_COMPRESSION_MODE.H264)
if zed.enable_recording(recording_params) != sl.ERROR_CODE.SUCCESS:
    print("Recording initialization failed.")
    zed.close()
    exit(1)

# Enable positional tracking
tracking_params = sl.PositionalTrackingParameters(_init_pos=sl.Transform())
if zed.enable_positional_tracking(tracking_params) != sl.ERROR_CODE.SUCCESS:
    print("Positional tracking initialization failed.")
    zed.close()
    exit(1)

# Enable spatial mapping
mapping_params = sl.SpatialMappingParameters(map_type=sl.SPATIAL_MAP_TYPE.MESH)
if zed.enable_spatial_mapping(mapping_params) != sl.ERROR_CODE.SUCCESS:
    print("Spatial mapping initialization failed.")
    zed.close()
    exit(1)

# Initialize runtime and data holders
runtime_params = sl.RuntimeParameters()
image = sl.Mat()
depth = sl.Mat()
pose = sl.Pose()
mesh = sl.Mesh()
sensors_data = sl.SensorsData()

# Initial GPS coordinates (starting point)
current_lat = 54.5742  # Example latitude (Teesside University area)
current_lon = -1.2353  # Example longitude

print("Recording started... Press 'q' to stop.")

try:
    while not keyboard.is_pressed('q'):
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            # Capture image and depth
            zed.retrieve_image(image, sl.VIEW.LEFT)
            zed.retrieve_measure(depth, sl.MEASURE.DEPTH)

            # Get position and orientation
            zed.get_position(pose, sl.REFERENCE_FRAME.WORLD)
            translation = pose.get_translation(sl.Translation()).get()
            rotation = pose.get_orientation(sl.Orientation()).get()

            # Retrieve sensor data
            zed.get_sensors_data(sensors_data, sl.TIME_REFERENCE.CURRENT)
            imu_data = sensors_data.get_imu_data()
            acceleration = imu_data.get_linear_acceleration()
            angular_velocity = imu_data.get_angular_velocity()
            magnetometer_data = sensors_data.get_magnetometer_data()
            magnetic_field = magnetometer_data.get_magnetic_field_calibrated
            barometer_data = sensors_data.get_barometer_data()
            pressure = barometer_data.pressure

            # Calculate simulated GPS-like coordinates
            new_lat, new_lon = calculate_new_gps(current_lat, current_lon, translation[0], translation[2])

            # Log position, orientation, sensor, and geo data
            print(f"Position: x={translation[0]:.2f}, y={translation[1]:.2f}, z={translation[2]:.2f}")
            print(f"Rotation: {rotation}")
            print(f"Acceleration: {acceleration}")
            print(f"Angular Velocity: {angular_velocity}")
            print(f"Magnetic Field: {magnetic_field}")
            print(f"Pressure: {pressure:.2f} hPa")
            print(f"Simulated GPS: Lat={new_lat:.6f}, Lon={new_lon:.6f}\n")

            # Update current GPS
            current_lat, current_lon = new_lat, new_lon

            # Get spatial mapping state
            mapping_state = zed.get_spatial_mapping_state()
            sys.stdout.write(f"Spatial Mapping State: {mapping_state}\033[K\r")
            sys.stdout.flush()

            time.sleep(0.1)

except KeyboardInterrupt:
    print("\nRecording stopped manually.")

# Finalize and save the mesh
print("\nExtracting Mesh...")
if zed.extract_whole_spatial_map(mesh) == sl.ERROR_CODE.SUCCESS:
    print("Filtering Mesh...")
    mesh.filter(sl.MeshFilterParameters())  # Filter out unwanted vertices

    print("Saving Mesh to 'mesh.obj'...")
    if mesh.save("mesh.obj") == sl.ERROR_CODE.SUCCESS:
        print("Mesh saved successfully.")
    else:
        print("Mesh saving failed.")
else:
    print("Mesh extraction failed.")

# Cleanup
zed.disable_spatial_mapping()
zed.disable_positional_tracking()
zed.disable_recording()
zed.close()
