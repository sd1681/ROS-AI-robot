#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist


WIDTH = 640
HEIGHT = 480

BLUE = 0
GREEN = 1
RED = 2

count = 0

x = 0
y = 0

color = [0x1D, 0x98, 0x1E]
tolerance = 0x20


found = False
def image_callback(data):
    global found 
    global count

    red = ord(data.data[WIDTH * y + x + RED])
    green = ord(data.data[WIDTH * y + x + GREEN])
    blue = ord(data.data[WIDTH * y + x + BLUE])

    # # Averaging code
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

    count += 1

    found = (color[RED] - tolerance <= red <= color[RED] + tolerance) and \
            (color[GREEN] - tolerance <= green <= color[GREEN] + tolerance) and \
            (color[BLUE] - tolerance <= blue <= color[BLUE] + tolerance)

    print found, hex(red), hex(green), hex(blue)


def move():
    # Starts a new node
    rospy.init_node('robot_cleaner', anonymous=True)
    velocity_publisher = rospy.Publisher('/cmd_vel_mux/input/navi', Twist, queue_size=10)

    # Subscribe to camera sensor data.
    image_sub = rospy.Subscriber("/camera/rgb/image_raw", Image, image_callback)

    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        vel_msg = Twist()
        
        speed = 0.05
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = 0
        
        if found:
            vel_msg.linear.x = speed

        velocity_publisher.publish(vel_msg)

        rate.sleep()

if __name__ == '__main__':
    try:
        #Testing our function
        move()
    except rospy.ROSInterruptException: pass
