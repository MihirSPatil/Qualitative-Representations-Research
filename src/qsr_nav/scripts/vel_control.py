#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import rospy
from qsr_nav.msg import *
from geometry_msgs.msg import *


class vel_control:
    def __init__(self):
        self.qtcb_sub = rospy.Subscriber("velocity_controller",VelMsg,self.vel_callback)
        self.vel_pub = rospy.Publisher("twist2", Twist, queue_size = 5)

    def vel_callback(self,data):
        control_cmd = data.vel_cmd
        twist = Twist()

        if control_cmd == 'Move Forward':
            twist.linear.x = 0.1
            twist.linear.y = 0
        if control_cmd == 'Move Left':
            print('in left')
            twist.linear.x = 0.1
            twist.linear.y = 0.06
        if control_cmd == 'Move Left Slowly':
            twist.linear.x = 0.1
            twist.linear.y = 0.04
        if control_cmd == 'Move Left Quickly':
            twist.linear.x = 0.1
            twist.linear.y = 0.08
        if control_cmd == 'Move Right':
            twist.linear.x = 0.1
            twist.linear.y = -0.06
        if control_cmd == 'Move Right Slowly':
            twist.linear.x = 0.1
            twist.linear.y = -0.04
        if control_cmd == 'Move Right Quickly':
            twist.linear.x = 0.1
            twist.linear.y = -0.08

        print('Vel control: {}, twist: {}'.format(control_cmd, twist))

        self.vel_pub.publish(twist)



def main(args):
  vc = vel_control()
  rospy.init_node('vel_control')
  try:
    rospy.spin()
  except rospy.ROSInterruptException:
    print("Shutting down")

if __name__ == '__main__':
    main(sys.argv)
