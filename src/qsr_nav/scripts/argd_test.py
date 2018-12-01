#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
import rospy
import math
import message_filters
from qsrlib.qsrlib import QSRlib, QSRlib_Request_Message
from qsrlib_ros.qsrlib_ros_client import QSRlib_ROS_Client
from qsrlib_io.world_trace import Object_State, World_Trace
from qsr_nav.msg import *
from geometry_msgs.msg import *
from nav_msgs.msg import Odometry
try:
    import cPickle as pickle
except:
    import pickle


class argd_interpreter:
    def __init__(self):

        self.world = World_Trace()
        self.options = sorted(QSRlib().qsrs_registry.keys())
        self.calculi = self.options[0]
        # any value in between goes to the upper bound
        self.dynamic_args = {"argd": {"qsr_relations_and_values":{"Near": 0.36, "Medium":.40, "Far":.45 }}}

        self.relationship_pub = rospy.Publisher("argd_realtionship", QsrMsg,queue_size = 2)
        self.pose_sub1 = rospy.Subscriber("extracted_pose1",PoseMsg, self.relations_callback)
        self.cln = QSRlib_ROS_Client()
        # the update rate for the ApproximateTimeSynchronizer is 0.1 and the queue_size is 10

    def relations_callback(self,extracted_pose1):
        print('------------------------')
        print(extracted_pose1)
        print("========================")
        o1 = [Object_State(name="object_1", timestamp=extracted_pose1.header.stamp.secs, x=extracted_pose1.pose_vec.position.x, y=extracted_pose1.pose_vec.position.z)]
        o2 = [Object_State(name="robot", timestamp=extracted_pose1.header.stamp.secs, x=0, y=0)]

        self.world.add_object_state_series(o1)
        self.world.add_object_state_series(o2)


        qsrlib_request_message = QSRlib_Request_Message(which_qsr=self.calculi, input_data=self.world, dynamic_args=self.dynamic_args)
        req = self.cln.make_ros_request_message(qsrlib_request_message)
        res = self.cln.request_qsrs(req)
        qsrlib_response_message = pickle.loads(res.data)


        argd_relation_msg = QsrMsg()
        argd_relation_msg.selected_qsr = str(self.calculi)
        argd_relation_msg.marker_id1 = extracted_pose1.marker_id

        for time in qsrlib_response_message.qsrs.get_sorted_timestamps():
            argd_relation_msg.message_time = extracted_pose1.header.stamp.nsecs

            for key, value in zip(qsrlib_response_message.qsrs.trace[time].qsrs.keys(),
                            qsrlib_response_message.qsrs.trace[time].qsrs.values()):
                            argd_relation_msg.objects = key
                            argd_relation_msg.relationship = str(value.qsr)
                            self.relationship_pub.publish(argd_relation_msg)
                            print(argd_relation_msg)


def main(args):
  ai = argd_interpreter()
  rospy.init_node('argd_interpreter')
  try:
    rospy.spin()
  except rospy.ROSInterruptException:
    print("Shutting down")

if __name__ == '__main__':
    main(sys.argv)
