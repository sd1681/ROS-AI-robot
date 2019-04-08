#!/usr/bin/env python
import rospy
import copy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist


WIDTH = 640
HEIGHT = 480

KINECT_RED = 2
KINECT_GREEN = 1
KINECT_BLUE = 0

RED = 0
GREEN = 1
BLUE = 2

PIXEL_LENGTH = 3

count = 0

x = 0
y = 0

found = False

def in_color_range(pixel, color, tolerance):
    print color
    print pixel
    return (color[RED] - tolerance <= pixel[RED] <= color[RED] + tolerance) and \
           (color[GREEN] - tolerance <= pixel[GREEN] <= color[GREEN] + tolerance) and \
           (color[BLUE] - tolerance <= pixel[BLUE] <= color[BLUE] + tolerance)

def image_callback(data):
    global found 
    global count

    # # Averaging code for color calibration. May replace with HSL values in
    # # the future.
    # if 0 == count:
    #     average_r = red
    #     average_g = green
    #     average_b = blue
    # else:
    #     average_r -= average_r / count
    #     average_r += red / count

    #     average_g -= average_g / count
    #     average_g += green / count

    #     average_b -= average_b / count
    #     average_b += blue / count

    color = [0x98, 0x1D, 0x1E]
    found = in_color_range(
        [ord(data.data[KINECT_RED]),
         ord(data.data[KINECT_GREEN]),
         ord(data.data[KINECT_BLUE])],
        color,
        0x20
    )
    image_map = [0] * (len(data.data) / PIXEL_LENGTH)
    print data.encoding

    for i in range(0, len(image_map), PIXEL_LENGTH):
        None


def move():
    # Starts a new node
    rospy.init_node('robot_cleaner', anonymous=True)
    velocity_publisher = rospy.Publisher('/cmd_vel_mux/input/navi', Twist, queue_size=10)

    # Subscribe to camera sensor data.
    image_sub = rospy.Subscriber("/camera/rgb/image_color", Image, image_callback)

    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        vel_msg = Twist()
        
        speed = 0.1
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = 0
        
        if found:
            vel_msg.linear.x = speed

        velocity_publisher.publish(vel_msg)

        if found:
            exit()
        rate.sleep()

if __name__ == '__main__':
    try:
        #Testing our function
        move()
    except rospy.ROSInterruptException: pass
