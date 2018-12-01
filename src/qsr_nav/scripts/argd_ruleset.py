#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
import rospy
import re
from qsr_nav.msg import *
from geometry_msgs.msg import *

class argd_ruleset:
    def __init__(self):
        self.argd_sub = rospy.Subscriber("argd_realtionship",QsrMsg,self.ruleset_callback)

    def ruleset_callback(self,data):

        marker1 = data.marker_id1
        marker2 = data.marker_id2
        timestamp, objects = data.objects.split('=')
        object_pair2, object_pair1,_ = objects.split(';')
        print(object_pair1, object_pair2)
        print('=========================================')

        _,relation_sets = data.relationship.split('=')
        relation_sets = relation_sets.replace(" ", "")
        relation_sets = relation_sets.replace("}", ";")
        relation_sets = relation_sets.replace("{", "")

        relation2, relation1,_ = relation_sets.split(';')
        print(relation1, relation2)
        print('-----------------------------------------')

        if(relation1.find(data.selected_qsr) >= 0 and relation2.find(data.selected_qsr) >= 0):
            calculi1,rel1 = relation1.split(':')
            calculi2, rel2 = relation2.split(':')

            # print('calculi{} with relation{}'.format(calculi, relation))
            if (rel1 == "'Near'" and rel2 == "'Near'"):
                vel_cmd = 'Move Forward'
            if (rel1 == "'Near'" and rel2 == "'Medium'"):
                vel_cmd = 'Move Right Slowly'
            if (rel1 == "'Near'" and rel2 == "'Far'"):
                vel_cmd = 'Move Right Quickly'
            if (rel1 == "'Medium'" and rel2 == "'Near'"):
                vel_cmd = 'Move Left Slowly'
            if (rel1 == "'Medium'" and rel2 == "'Medium'"):
                vel_cmd = 'Move Forward'
            if (rel1 == "'Medium'" and rel2 == "'Far'"):
                vel_cmd = 'Move Right Slowly'
            if (rel1 == "'Far'" and rel2 == "'Near'"):
                vel_cmd = 'Move Left Quickly'
            if (rel1 == "'Far'" and rel2 == "'Medium'"):
                vel_cmd = 'Move Left Slowly'
            if (rel1 == "'Far'" and rel2 == "'Far'"):
                vel_cmd = 'Move Forward'

            print(vel_cmd)
            print('******************************************')
            print("marker1:{}, marker2:{}".format(marker1,marker2))



def main(args):
  ar = argd_ruleset()
  rospy.init_node('argd_ruleset')
  try:
    rospy.spin()
  except rospy.ROSInterruptException:
    print("Shutting down")

if __name__ == '__main__':
    main(sys.argv)
