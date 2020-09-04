1. Introduction
 
Our goal for this project is to implement a TurtleBot to follow a colored object. The robot uses its camera sensor to identify and approach a moving red object in its field of view.
Subgoals for the project are:
The robot stops when close enough to the target.
The robot finds the target when not in the field of view of the camera.
      3   On finding a target in the visible range, the robot approaches the target.
The robot uses the reactive paradigm to achieve these goals. The finite state machine defines three states: find target, approach, and stop. “far” indicates an undetected object. “btwn” indicates that the object is in range, and “close” indicates that the object is too close to the target. “invalid” marks the contradiction when the object is too close and too far.

2. Methods
2.1 Setting Up ROS Package
	Setup a new ROS package, and copy follow.py into the scripts directory.
roslaunch turtlebot_bringup minimal.launch
	This loads the ROS nodes necessary to run the program on the Turtlebot. To use the Kinect camera, use the OpenNI package to connect to the camera:
roslaunch openni_launch openni.launch
	Finally, to launch our code:
roslaunch [your_package_name] follow.py

2.2 Turtlebot as Wireless Access Point
We found that we can improve our productivity working on the Turtlebot by remotely working on the netbook from our laptops. We setup the netbook as a wireless access point, plugged it into the network, and used the secure shell (SSH) to make edits to the source code. We only needed to physically interact with the robot when we needed to open a GNU screen session to see the mask window. This drastically decreased time spent between builds of our robot code.
2.2.1 Instructions for Setting Up Wireless Access Point
Go to WiFi settings on the netbook
Click on create WiFi
Create a Host hotspot network
Connect the host hotspot with the remote workstation
On remote workstation open terminal and type command ssh turtlebot @<ip address>
(Make sure you have the ssh service up on the workstation)

2.3 ROS Topics
Most code online refers to Turtlebot 1 topics. Since we were using Turtlebot 2, we had to identify the topics needed to get sensor data and publish control commands:
Navigation topic: /cmd_vel_mux/input/navi
Camera sensor topic: /camera/rgb/image_color
We were unable to recover depth information from the Kinect, but after watching student presentations it seems that we may not have had the to correct command sequence to do so.

2.4 Processing and Using Camera Sensor Data
In order to use the camera sensor, a callback must be defined that takes the percept as an argument. We used CvBridge2 to process that percept into the 24-bit BGR colorspace, and converted it into the RGB colorspace.
The robot is drawn towards an object with the color red, but how does one determine the encoding for that color? Camera inputs are noisy, so the sensor readings were averaged over a twenty second period over a pixel known to contain the desired color. A tolerance was 

