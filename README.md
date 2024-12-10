magic.py script records in .svo while enabling the important ZED2 features such as depth sensing, sensors and spatial mapping.
magicGeo.py has IMU geotracking on top of that. It is a separate script in case it consumed too much memory. 

Both files output .svo and mesh .obj files for each recording.
Both files can be run by clicling on the green Run button and can be stopped by pressing "q" or manually clicking the red Stop button.
Attention: output file names must be changed after every recording session. Existing files will be overwritten otherwise.

