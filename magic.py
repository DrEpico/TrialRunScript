import sys
import pyzed.sl as sl
from signal import signal, SIGINT
import argparse
import os
# import ogl_viewer.tracking_viewer as gl
import ogl_viewer as gl
print(gl.__file__)
import pyzed.sl as sl
import argparse
import time

cam = sl.Camera()

def parse_args(init):
    if len(opt.input_svo_file) > 0 and opt.input_svo_file.endswith(".svo"):
        init.set_from_svo_file(opt.input_svo_file)
        print("[Sample] Using SVO File input: {0}".format(opt.input_svo_file))
    elif len(opt.ip_address) > 0 :
        ip_str = opt.ip_address
        if ip_str.replace(':','').replace('.','').isdigit() and len(ip_str.split('.'))==4 and len(ip_str.split(':'))==2:
            init.set_from_stream(ip_str.split(':')[0],int(ip_str.split(':')[1]))
            print("[Sample] Using Stream input, IP : ",ip_str)
        elif ip_str.replace(':','').replace('.','').isdigit() and len(ip_str.split('.'))==4:
            init.set_from_stream(ip_str)
            print("[Sample] Using Stream input, IP : ",ip_str)
        else :
            print("Unvalid IP format. Using live stream")
    if ("resolution" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.HD2K
        print("[Sample] Using Camera in resolution HD2K")
    elif ("HD1200" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.HD1200
        print("[Sample] Using Camera in resolution HD1200")
    elif ("HD1080" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.HD1080
        print("[Sample] Using Camera in resolution HD1080")
    elif ("HD720" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.HD720
        print("[Sample] Using Camera in resolution HD720")
    elif ("SVGA" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.SVGA
        print("[Sample] Using Camera in resolution SVGA")
    elif ("VGA" in opt.resolution):
        init.camera_resolution = sl.RESOLUTION.VGA
        print("[Sample] Using Camera in resolution VGA")
    elif len(opt.resolution)>0:
        print("[Sample] No valid resolution entered. Using default")
    else :
        print("[Sample] Using default resolution")

# Handler to deal with CTRL+C properly
def handler(signal_received, frame):
    cam.disable_recording()
    cam.close()
    sys.exit(0)


signal(SIGINT, handler)


def main():
    init = sl.InitParameters(camera_resolution=sl.RESOLUTION.HD720,
                                 coordinate_units=sl.UNIT.METER,
                                 coordinate_system=sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP)
    parse_args(init)#pass init params
    init.depth_mode = sl.DEPTH_MODE.PERFORMANCE
    init.async_image_retrieval = False;  # This parameter can be used to record SVO in camera FPS even if the grab loop is running at a lower FPS (due to compute for ex.)

    status = cam.open(init)
    if status != sl.ERROR_CODE.SUCCESS:
        print("Camera Open", status, "Exit program.")
        exit(1)

    recording_param = sl.RecordingParameters(opt.output_svo_file,
                                             sl.SVO_COMPRESSION_MODE.H264)  # Enable recording with the filename specified in argument
    err = cam.enable_recording(recording_param)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Recording ZED : ", err)
        exit(1)



    runtime = sl.RuntimeParameters()
    camera_pose = sl.Pose()
    print("SVO is Recording, use Ctrl-C to stop.")  # Start recording SVO, stop with Ctrl-C command
    frames_recorded = 0

    # If there is a part of the image containing a static zone, the tracking accuracy will be significantly impacted
    # The region of interest auto detection is a feature that can be used to remove such zone by masking the irrelevant area of the image.
    # The region of interest can be loaded from a file :
    roi = sl.Mat()
    roi_name = "roi_mask.png"
    #roi.read(roi_name)
    #zed.set_region_of_interest(roi, [sl.MODULE.POSITIONAL_TRACKING])
    # or alternatively auto detected at runtime:
    roi_param = sl.RegionOfInterestParameters()

    if opt.roi_mask_file == "":
        roi_param.auto_apply_module = {sl.MODULE.DEPTH, sl.MODULE.POSITIONAL_TRACKING}
        cam.start_region_of_interest_auto_detection(roi_param)
        print("[Sample]  Region Of Interest auto detection is running.")

    camera_info = cam.get_camera_information()
    # Create OpenGL viewer
    viewer = gl.GLViewer()
    viewer.init(camera_info.camera_model)
    py_translation = sl.Translation()
    pose_data = sl.Transform()

    text_translation = ""
    text_rotation = ""

    roi_state = sl.REGION_OF_INTEREST_AUTO_DETECTION_STATE.NOT_ENABLED

    # while viewer.is_available():
    #     if cam.grab(runtime) == sl.ERROR_CODE.SUCCESS:
    #         tracking_state = cam.get_position(camera_pose,sl.REFERENCE_FRAME.WORLD) #Get the position of the camera in a fixed reference frame (the World Frame)
    #         tracking_status = cam.get_positional_tracking_status()
    #
    #         #Get rotation and translation and displays it
    #         if tracking_state == sl.POSITIONAL_TRACKING_STATE.OK:
    #             rotation = camera_pose.get_rotation_vector()
    #             translation = camera_pose.get_translation(py_translation)
    #             text_rotation = str((round(rotation[0], 2), round(rotation[1], 2), round(rotation[2], 2)))
    #             text_translation = str((round(translation.get()[0], 2), round(translation.get()[1], 2), round(translation.get()[2], 2)))
    #
    #         pose_data = camera_pose.pose_data(sl.Transform())
    #         # Update rotation, translation and tracking state values in the OpenGL window
    #         viewer.updateData(pose_data, text_translation, text_rotation, tracking_status)
    #
    #         # If the region of interest auto-detection is running, the resulting mask can be saved and reloaded for later use
    #         if opt.roi_mask_file == "" and roi_state == sl.REGION_OF_INTEREST_AUTO_DETECTION_STATE.RUNNING and cam.get_region_of_interest_auto_detection_status() == sl.REGION_OF_INTEREST_AUTO_DETECTION_STATE.READY:
    #             print("Region Of Interest detection done! Saving into {}".format(roi_name))
    #             cam.get_region_of_interest(roi, sl.Resolution(0,0), sl.MODULE.POSITIONAL_TRACKING)
    #             roi.write(roi_name)
    #
    #         roi_state = cam.get_region_of_interest_auto_detection_status()
    #     else :
    #         time.sleep(0.001)
    # viewer.exit()
    # cam.close()

    while True:
        if cam.grab(runtime) == sl.ERROR_CODE.SUCCESS:  # Check that a new image is successfully acquired
            frames_recorded += 1
            print("Frame count: " + str(frames_recorded), end="\r")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_svo_file', type=str, help='Path to the SVO file that will be written', required=True)

    parser.add_argument('--input_svo_file', type=str, help='Path to an .svo file, if you want to replay it', default='')
    parser.add_argument('--ip_address', type=str,
                        help='IP Adress, in format a.b.c.d:port or a.b.c.d, if you have a streaming setup', default='')
    parser.add_argument('--resolution', type=str,
                        help='Resolution, can be either HD2K, HD1200, HD1080, HD720, SVGA or VGA', default='')
    parser.add_argument('--roi_mask_file', type=str, help='Path to a Region of Interest mask file', default='')

    opt = parser.parse_args()
    if not opt.output_svo_file.endswith(".svo") and not opt.output_svo_file.endswith(".svo2"):
        print("--output_svo_file parameter should be a .svo file but is not : ", opt.output_svo_file, "Exit program.")
        exit()

    if (len(opt.input_svo_file) > 0 and len(opt.ip_address) > 0):
        print("Specify only input_svo_file or ip_address, or none to use wired camera, not both. Exit program")
        exit()

    main()