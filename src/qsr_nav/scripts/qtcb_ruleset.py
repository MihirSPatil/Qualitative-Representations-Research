#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
import rospy
from qsr_nav.msg import *

class qtcb_ruleset:
    def __init__(self):
        self.qtcb_sub = rospy.Subscriber("qtcb_realtionship",QsrMsg,self.ruleset_callback)
        self.control_pub = rospy.Publisher("velocity_controller",VelMsg,queue_size = 2)


    def ruleset_callback(self,data):
        marker1 = data.marker_id1
        marker2 = data.marker_id2
        obj1, obj2 = data.objects.split(',')
        control_msg = VelMsg()

        if marker1 == data.marker_left:
                object_left = 'object_1'
                object_right = 'object_2'

        if marker1 == data.marker_right:
                object_left = 'object_2'
                object_right = 'object_1'


        relationship = data.relationship.replace(" ", "")
        relationship = relationship.strip('{}')
        # print('==========================================')
        # print(data)
        # print('==========================================')

        if(relationship.find(data.selected_qsr) >= 0):
            calculi,relation = relationship.split(':')
            # {-,+,0} = [towards, away, stable], these are the actual interpretation when the robot is considered to be moving and the objects as stationary, but in our case the robot is considered to be stationary and the objects to be moving around it hence the relations are inverted.
            if relation == "'0,0'":
                rel1 = 'Stable'
                rel2 = 'Stable'
                vel_cmd = 'Move Forward'

            if relation == "'0,-'":
                rel1 = 'Stable'
                rel2 = 'Away'
                if obj1 == object_left:
                    vel_cmd = 'Move Forward'
                else:
                    vel_cmd = 'Move Forward'

            if relation == "'0,+'":
                rel1 = 'Stable'
                rel2 = 'Towards'
                if obj1 == object_left:
                    vel_cmd = 'Move Right'
                else:
                    vel_cmd = 'Move Left'

            if relation == "'+,0'":
                rel1 = 'Towards'
                rel2 = 'Stable'
                if obj1 == object_left:
                    vel_cmd = 'Move Right'
                else:
                    vel_cmd = 'Move Left'

            if relation == "'-,0'":
                rel1 = 'Away'
                rel2 = 'Stable'
                if obj1 == object_left:
                    vel_cmd = 'Move Forward'
                else:
                    vel_cmd = 'Move Forward'

            if relation == "'-,-'":
                rel1 = 'Away'
                rel2 = 'Away'
                vel_cmd = 'Move Forward'

            if relation == "'-,+'":
                rel1 = 'Away'
                rel2 = 'Towards'
                if obj1 == object_left:
                    vel_cmd = 'Move Left'
                else:
                    vel_cmd = 'Move Right'

            if relation == "'+,+'":
                rel1 = 'Towards'
                rel2 = 'Towards'
                vel_cmd = "Move Forward" #can also be changed to move backward

            if relation == "'+,-'":
                rel1 = 'Towards'
                rel2 = 'Away'
                if obj1 == object_left:
                    vel_cmd = 'Move Right'
                else:
                    vel_cmd = 'Move Left'

            control_msg.vel_cmd = vel_cmd
            self.control_pub.publish(control_msg)

            # print("object_1:{}, value:{}, object_2:{}, value:{}".format(marker1, rel1, marker2, rel2))
            # print('_________________________________________________________________________________')
            # print(vel_cmd)


def main(args):
  qr = qtcb_ruleset()
  rospy.init_node('qtcb_ruleset')
  try:
    rospy.spin()
  except rospy.ROSInterruptException:
    print("Shutting down")

if __name__ == '__main__':
    main(sys.argv)
