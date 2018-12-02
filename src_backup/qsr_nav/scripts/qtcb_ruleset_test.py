#!/usr/bin/env python
# -*- coding: utf-8 -*-
# this approach of getting all the relations together doesn't work very well,
# especially since not all markers are noticed at all the time
from __future__ import print_function, division
import rospy
from qsr_nav.msg import *
from geometry_msgs.msg import *

class qtcb_ruleset:
    def __init__(self):
        self.qtcb_sub = rospy.Subscriber("qtcb_realtionship",QsrMsg,self.ruleset_callback)
        # self.vel_sub = rospy.Subscriber("cmd_vel",Twist)

    def ruleset_callback(self,data):
        marker1 = data.marker_id1
        marker2 = data.marker_id2
        # {-,+,0} = [towards, away, stable], these are the actual interpretation when the robot is considered to be moving and the objects as stationary, but in our case the robot is considered to be stationary and the objects to be moving around it hence the relations are inverted.
        # Since we do not want a relation involving only a single object we check the length, as the length of an
        # relation involving two or more objects is greater than 30 we use this value as a cutoff;
        # length of a relation involving only a single object is 28
        if (len(data.objects) > 30):
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
            print('_________________________________________')

            if(relation1.find(data.selected_qsr) >= 0 and relation2.find(data.selected_qsr) >= 0):
                calculi1,rel1 = relation1.split(':')
                calculi2, rel2 = relation2.split(':')
                # print(rel1, rel2)
                
                if rel1 == "'0,0'" and rel2 == "'0,0'":
                    object_val1 = 'Stable'
                    object_val2 = 'Stable'

                if rel1 == "'0,0'" and rel2 == "'0,-'":
                    object_val1 = 'Stable'
                    object_val2 = 'Stable'

                if rel1 == "'0,0'" and rel2 == "'0,+'":
                    object_val1 = 'Stable'
                    object_val2 = 'Stable'

                if rel1 == "'0,0'" and rel2 == "'-,0'":
                    object_val1 = 'Stable'
                    object_val2 = 'Stable'

                if rel1 == "'0,0'" and rel2 == "'+,0'":
                    object_val1 = 'Stable'
                    object_val2 = 'Stable'
        #
        #         if relation == "'+,0'":
        #             object_val1 = 'Towards'
        #             object_val2 = 'Stable'
        #
        #         if relation == "'-,0'":
        #             object_val1 = 'Away'
        #             object_val2 = 'Stable'
        #
        #         if relation == "'-,-'":
        #             object_val1 = 'Away'
        #             object_val2 = 'Away'
        #
        #         if relation == "'-,+'":
        #             object_val1 = 'Away'
        #             object_val2 = 'Towards'
        #
        #         if relation == "'+,+'":
        #             object_val1 = 'Away'
        #             object_val2 = 'Away'
        #
        #         if relation == "'+,-'":
        #             object_val1 = 'Away'
        #             object_val2 = 'Towards'
        # #
        # #     print("object_1:{}, value:{}, object_2:{}, value:{}".format(marker1, object_val1, marker2, object_val2))


def main(args):
  qr = qtcb_ruleset()
  rospy.init_node('qtcb_ruleset')
  try:
    rospy.spin()
  except rospy.ROSInterruptException:
    print("Shutting down")

if __name__ == '__main__':
    main(sys.argv)
