import pyzed.sl as sl
import time

# Initialize camera
zed = sl.Camera()

# Configure camera
init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD1080
init_params.depth_mode = sl.DEPTH_MODE.ULTRA
init_params.coordinate_units = sl.UNIT.METER
init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP

mapping_parameters = sl.SpatialMappingParameters(map_type=sl.SPATIAL_MAP_TYPE.MESH)
zed.enable_spatial_mapping(mapping_parameters)

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
tracking_params = sl.PositionalTrackingParameters()
if zed.enable_positional_tracking(tracking_params) != sl.ERROR_CODE.SUCCESS:
    print("Positional tracking initialization failed.")
    zed.close()
    exit(1)

# Prepare runtime and data holders
runtime_params = sl.RuntimeParameters()

image = sl.Mat()
pose = sl.Pose()

print("Recording started... Press Ctrl+C or 'q' to stop.")

try:
    while True:
        if zed.grab(runtime_params) == sl.ERROR_CODE.SUCCESS:
            # Capture image
            zed.retrieve_image(image, sl.VIEW.LEFT)

            # Get position
            zed.get_position(pose, sl.REFERENCE_FRAME.WORLD)

            # Extract translation and rotation
            translation = pose.get_translation(sl.Translation()).get()
            rotation = pose.get_orientation(sl.Orientation()).get()

            print(f"Position: x={translation[0]:.2f}, y={translation[1]:.2f}, z={translation[2]:.2f}")
            print(f"Rotation: {rotation}\n")

            time.sleep(0.1)

except KeyboardInterrupt:
    print("Recording stopped.")

# Cleanup
zed.disable_recording()
zed.close()
