<h1>ZED2 Recording and Processing Scripts</h1>

<p>This repository provides two scripts, <code>magic.py</code> and <code>magicGeo.py</code>, designed to work with the ZED2 camera for recording <code>.svo</code> files and generating <code>.obj</code> meshes.</p>

<h2>Features</h2>

<h3>magic.py</h3>
<ul>
    <li><strong>Core functionalities:</strong>
        <ul>
            <li>Depth sensing</li>
            <li>Sensor data recording</li>
            <li>Spatial mapping</li>
        </ul>
    </li>
    <li><strong>Outputs:</strong>
        <ul>
            <li><code>.svo</code> (video recording)</li>
            <li><code>.obj</code> (3D mesh)</li>
        </ul>
    </li>
</ul>

<h3>magicGeo.py</h3>
<ul>
    <li><strong>Enhancements over <code>magic.py</code>:</strong>
        <ul>
            <li>Includes <strong>IMU geotracking</strong> capabilities for enhanced positional data</li>
        </ul>
    </li>
    <li><strong>Outputs:</strong>
        <ul>
            <li><code>.svo</code> (video recording)</li>
            <li><code>.obj</code> (3D mesh)</li>
        </ul>
    </li>
</ul>
<p><strong>Note:</strong> This script is separated to optimize memory usage during intensive recording sessions.</p>

<h2>Usage Instructions</h2>
<ol>
    <li><strong>Run the script:</strong> Simply click the green <strong>Run</strong> button to start recording.</li>
    <li><strong>Stop the script:</strong>
        <ul>
            <li>Press the <code>q</code> key, or</li>
            <li>Manually click the red <strong>Stop</strong> button.</li>
        </ul>
    </li>
</ol>

<h2>Important Notes</h2>
<ul>
    <li><strong>File Naming:</strong> Ensure to rename output files after each recording session. <strong>Existing files will be overwritten</strong> if not renamed.</li>
</ul>

<h2>Output File Formats</h2>
<ul>
    <li><code>.svo</code>: Video recording of the session</li>
    <li><code>.obj</code>: 3D mesh generated from spatial mapping</li>
</ul>
