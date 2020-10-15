#!/usr/bin/env python

import sys
import rospy
from std_msgs.msg import Float64

def run():

	rospy.init_node('mySuperNode')

	pub = rospy.Publisher('/ar601/RKneePitch_position_controller/command', Float64, queue_size=1)
	rate= rospy.Rate(5)
	i = 0
	while i < 10:
		pub.publish(20)
		rate.sleep()
		i = i+1

if __name__ == "__main__":

	run()
