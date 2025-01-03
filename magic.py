import pyzed.sl as sl
import time
import keyboard
import sys

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

# Prepare runtime and data holders
runtime_params = sl.RuntimeParameters()
image = sl.Mat()
depth = sl.Mat()
pose = sl.Pose()
mesh = sl.Mesh()
sensors_data = sl.SensorsData()

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

            barometer_data = sensors_data.get_barometer_data()
            pressure = barometer_data.pressure

            # Log position and orientation
            print(f"Position: x={translation[0]:.2f}, y={translation[1]:.2f}, z={translation[2]:.2f}")
            print(f"Rotation: {rotation}")
            print(f"Acceleration: {acceleration}")
            print(f"Angular Velocity: {angular_velocity}")
            print(f"Pressure: {pressure:.2f} hPa\n")

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
    mesh.filter(sl.MeshFilterParameters())  # Filter out unnecessary vertices

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
