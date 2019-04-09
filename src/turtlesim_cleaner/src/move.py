#!/usr/bin/env python
import rospy
import copy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import numpy as np

import cv2
from cv_bridge import CvBridge, CvBridgeError

import time


WIDTH = 640
HEIGHT = 480

KINECT_RED = 2
KINECT_GREEN = 1
KINECT_BLUE = 0

RED = 0
GREEN = 1
BLUE = 2

PIXEL_LENGTH = 3

update_rate = 20
frame_count = 0

color = [0x98, 0x1D, 0x1E]
tolerance = 0x30
lower_red = np.array([
    color[RED] - tolerance,
    color[GREEN] - tolerance,
    color[BLUE] - tolerance
])
upper_red = np.array([
    color[RED] + tolerance,
    color[GREEN] + tolerance,
    color[BLUE] + tolerance
])

mask = None
lower_area = 1000
upper_area = 10000

bridge = CvBridge()

x_center = y_center = count = None

def image_callback(msg):
    global mask, count, x_center, y_center

    try:
       # Convert your ROS Image message to OpenCV2
       cv2_img = bridge.imgmsg_to_cv2(msg, "bgr8")
    except CvBridgeError, e:
       print(e)
    rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    
    mask = cv2.inRange(rgb, lower_red, upper_red)

    # From https://stackoverflow.com/q/38933566
    # Computes the centroid of the blob.
    count = (255 == mask).sum()
    y_center, x_center = np.argwhere(255 == mask).sum(0) / count

    # This code displays the blob on the window.
    cv2.imshow('mask', mask)
    cv2.waitKey(0x10);

def move():
    # Starts a new node
    rospy.init_node('robot_cleaner', anonymous=True)
    velocity_publisher = rospy.Publisher('/cmd_vel_mux/input/navi', Twist, queue_size=10)

    # Subscribe to camera sensor data.
    image_sub = rospy.Subscriber("/camera/rgb/image_color", Image, image_callback)

    rate = rospy.Rate(update_rate)
    center_tolerance = 100

    while not rospy.is_shutdown():
        vel_msg = Twist()
        
        center = 320
        linear_speed = 0.1
        angular_speed = 0.5
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = 0
        
        if x_center and y_center and lower_area < count < upper_area:
            vel_msg.linear.x = linear_speed
            if center - center_tolerance > x_center:
                vel_msg.angular.z = angular_speed 
            elif center + center_tolerance < x_center:
                vel_msg.angular.z = -angular_speed 
        else:
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = 0

        velocity_publisher.publish(vel_msg)

        rate.sleep()

if __name__ == '__main__':
    try:
        #Testing our function
        move()
    except rospy.ROSInterruptException: pass
