#!/usr/bin/env python
import rospy
import copy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import numpy as np

import cv2
from cv_bridge import CvBridge, CvBridgeError

import time

# Finite state machine states.
STATE_STOP = 0
STATE_FIND_TARGET = 1
STATE_APPROACH_TARGET = 2

# Current state.
cur_state = STATE_STOP

RED = 0
GREEN = 1
BLUE = 2

# ROS update rate.
update_rate = 20

# Number of pixels left and right of the center of the sensor image that
# indicates the robot is bearing down on target.
center_tolerance = 100

# Color of the target. The camera is noisy, so I averaged this over time by
# holding the object so pixel (0, 0) had the value of the color.
color = [0x98, 0x1D, 0x1E]
tolerance = 0x20

# Lower bound of the color.
lower_red = np.array([
    color[RED] - tolerance,
    color[GREEN] - tolerance,
    color[BLUE] - tolerance
])

# Upper bound of the color.
upper_red = np.array([
    color[RED] + tolerance,
    color[GREEN] + tolerance,
    color[BLUE] + tolerance
])

# Lower bound on pixel count that indicates the target is in view.
lower_area = 1000
# Upper bound on pixel count that indicates the robot is at target.
upper_area = 10000

# Center pixel on the X axis.
center = 320

linear_speed = 0.1
angular_speed = 0.5

# X and Y coordinates of centroid.
x_center = y_center = None
# Area of the blob.
count = None

def image_callback(msg):
    global count, x_center, y_center

    try:
        bridge = CvBridge()
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
    cv2.imshow('Turtlebot Kinect View', mask)
    cv2.waitKey(0x10);


def no_target():
    return lower_area > count

def target_in_view():
    return x_center and y_center and lower_area < count < upper_area

def at_target():
    return count > upper_area


def move():
    global cur_state

    # Starts a new node
    rospy.init_node("follower", anonymous=True)
    velocity_publisher = rospy.Publisher('/cmd_vel_mux/input/navi', Twist, queue_size=10)

    # Subscribe to camera sensor data.
    image_sub = rospy.Subscriber("/camera/rgb/image_color", Image, image_callback)

    rate = rospy.Rate(update_rate)

    while not rospy.is_shutdown():
        vel_msg = Twist()
        
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = 0.0
        
        if STATE_STOP == cur_state:
            if target_in_view():
                cur_state = STATE_APPROACH_TARGET

        elif STATE_APPROACH_TARGET == cur_state:
            if at_target():
                cur_state = STATE_STOP
            elif no_target():
                cur_state = STATE_STOP
            else:
                vel_msg.linear.x = linear_speed

                if center - center_tolerance > x_center:
                    vel_msg.angular.z = angular_speed 
                elif center + center_tolerance < x_center:
                    vel_msg.angular.z = -angular_speed 

        velocity_publisher.publish(vel_msg)

        rate.sleep()

if __name__ == '__main__':
    try:
        move()
    except rospy.ROSInterruptException: pass

