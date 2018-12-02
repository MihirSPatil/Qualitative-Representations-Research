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


class qtc_interpreter:
    def __init__(self):

        self.world = World_Trace()
        self.options = sorted(QSRlib().qsrs_registry.keys())
        self.calculi = self.options[6]
        # quantisation_factor represents the minimum change that should be considered to assume that the object has moved
        self.dynamic_args = {"qtcbs": {"no_collapse":True,"quantisation_factor": 0.01}, "qtcbs": {"qsrs_for": [("object_1","robot"), ("object_2","robot")]}}
        self.prev_timestamp = 0
        self.prev_pose_x1 = self.prev_pose_y1 = 0
        self.prev_pose_x2 = self.prev_pose_y2 = 0
        self.prev_robot_pose_x = self.prev_robot_pose_y = 0

        self.relationship_pub = rospy.Publisher("qtcb_realtionship", QsrMsg, queue_size = 10)
        self.pose_sub1 = message_filters.Subscriber("extracted_pose1",PoseMsg)
        self.pose_sub2 = message_filters.Subscriber("extracted_pose2",PoseMsg)
        self.cln = QSRlib_ROS_Client()
        # the update rate for the ApproximateTimeSynchronizer is 0.1 and the queue_size is 10
        self.ts = message_filters.ApproximateTimeSynchronizer([self.pose_sub1, self.pose_sub2], 10, 0.1)
        self.ts.registerCallback(self.relations_callback)

    def relations_callback(self,extracted_pose1,extracted_pose2):
        qtc_relation_msg = QsrMsg()
        print("extracted_pose1",extracted_pose1.pose_vec.position)
        print("marker1", extracted_pose1.marker_id)
        print('==========================================')
        print("extracted_pose2",extracted_pose2.pose_vec.position)
        print("marker2", extracted_pose2.marker_id)
        print("##########################################")


        o1 = [Object_State(name="object_1", timestamp=self.prev_timestamp, x=self.prev_pose_x1, y=self.prev_pose_y1),
              Object_State(name="object_1", timestamp=extracted_pose1.header.stamp.secs, x=extracted_pose1.pose_vec.position.x, y=extracted_pose1.pose_vec.position.z)]
        o2 = [Object_State(name="robot", timestamp=self.prev_timestamp, x=self.prev_robot_pose_x, y=self.prev_robot_pose_y),
              Object_State(name="robot", timestamp=extracted_pose1.header.stamp.secs, x=0, y=0)]
        o3 = [Object_State(name="object_2", timestamp=self.prev_timestamp, x=self.prev_pose_x2, y=self.prev_pose_y2),
              Object_State(name="object_2", timestamp=extracted_pose1.header.stamp.secs, x=extracted_pose2.pose_vec.position.x, y=extracted_pose2.pose_vec.position.z)]
        self.world.add_object_state_series(o1)
        self.world.add_object_state_series(o2)
        self.world.add_object_state_series(o3)


        self.prev_timestamp = extracted_pose1.header.stamp.secs
        self.prev_pose_x1 = extracted_pose1.pose_vec.position.x
        self.prev_pose_y1 = extracted_pose1.pose_vec.position.z
        self.prev_pose_x2 = extracted_pose2.pose_vec.position.x
        self.prev_pose_y2 = extracted_pose2.pose_vec.position.z
        self.prev_robot_pose_x = 0
        self.prev_robot_pose_y = 0


        qsrlib_request_message = QSRlib_Request_Message(which_qsr=self.calculi, input_data=self.world, dynamic_args=self.dynamic_args)
        req = self.cln.make_ros_request_message(qsrlib_request_message)
        res = self.cln.request_qsrs(req)
        qsrlib_response_message = pickle.loads(res.data)


        qtc_relation_msg.selected_qsr = str(self.calculi)
        qtc_relation_msg.marker_id1 = extracted_pose1.marker_id
        qtc_relation_msg.marker_id2 = extracted_pose2.marker_id

        for time in qsrlib_response_message.qsrs.get_sorted_timestamps():
            qtc_relation_msg.message_time = extracted_pose1.header.stamp.secs
            object_key = str(extracted_pose1.header.stamp.secs) + " = "
            value_key = str(extracted_pose1.header.stamp.secs) + " = "

            for key, value in zip(qsrlib_response_message.qsrs.trace[time].qsrs.keys(),
                            qsrlib_response_message.qsrs.trace[time].qsrs.values()):
                            object_key += str(key) + ';'
                            qtc_relation_msg.objects = object_key
                            value_key += str(value.qsr)
                            qtc_relation_msg.relationship = value_key
            self.relationship_pub.publish(qtc_relation_msg)
            print(qtc_relation_msg)

        # print('timestamp1',extracted_pose1.header.stamp)
        # print('Marker1',str(extracted_pose1.marker_id))
        # print("object 1",self.world.trace[extracted_pose1.header.stamp.secs].objects['object_1'].x)
        # print('timestamp2',extracted_pose2.header.stamp)
        # print('Marker2',str(extracted_pose2.marker_id))
        # print('odom_timestamp',odom_pose.header.stamp)
        # print("object 2",self.world.trace[extracted_pose2.header.stamp.secs].objects['object_2'].x)
        # print("robot",self.world.trace[odom_pose.header.stamp.secs].objects['robot'].x)
        # print(self.multiple_calculi)

def main(args):
  qi = qtc_interpreter()
  rospy.init_node('qtc_interpreter')
  try:
    rospy.spin()
  except rospy.ROSInterruptException:
    print("Shutting down")

if __name__ == '__main__':
    main(sys.argv)
