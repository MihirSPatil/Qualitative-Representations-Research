#!/usr/bin/env python
from __future__ import print_function

import roslib
roslib.load_manifest('qsr_nav')
import sys
import rospy
import cv2 as cv
import numpy as np
import cv2.aruco as aruco
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from qsr_nav.msg import PoseMsg

class pose_extractor:

  def __init__(self):
    self.image_pub = rospy.Publisher("image_topic",Image,queue_size=2)
    self.markerpose_pub1 = rospy.Publisher('extracted_pose1',PoseMsg,queue_size=2)
    self.markerpose_pub2 = rospy.Publisher('extracted_pose2',PoseMsg,queue_size=2)

    self.bridge = CvBridge()
    self.image_sub = rospy.Subscriber("arm_cam3d/rgb/image_raw",Image,self.img_callback)
    self.prev_marker_id = None
    self.pub_flag = True
    # marker length in meters
    self.marker_length = .22
    self.distortion_coeffs = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
    self.intrinsic_camera_mat = np.array([[570.3422241210938, 0.0, 319.5], [0.0, 570.3422241210938, 239.5], [0.0, 0.0, 1.0]])
    self.aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
    self.parameters =  aruco.DetectorParameters_create()

  def img_callback(self,data):
    try:
      frame = self.bridge.imgmsg_to_cv2(data, "bgr8")
    except CvBridgeError as e:
      print(e)

    corners, ids, rejectedImgPoints = aruco.detectMarkers(frame, self.aruco_dict, parameters=self.parameters)
    if corners or ids:
        # print ('marker detected')
        marked = aruco.drawDetectedMarkers(frame, corners,ids)
        rvec, tvec, _ = aruco.estimatePoseSingleMarkers(corners,self.marker_length,self.intrinsic_camera_mat, self.distortion_coeffs)
        poseExtracted = PoseMsg()

        poseExtracted.pose_vec.position.x = tvec[0][0][0]
        poseExtracted.pose_vec.position.y = tvec[0][0][1]
        poseExtracted.pose_vec.position.z = tvec[0][0][2]
        # poseExtracted.header.stamp = rospy.Time.now()
        poseExtracted.header = data.header

        if (self.prev_marker_id is None and self.pub_flag is True):
            poseExtracted.marker_id = ids[0][0]
            self.prev_marker_id = ids[0][0]
            self.markerpose_pub1.publish(poseExtracted)
            self.pub_flag = False
            # print(self.pub_flag)
            # print("publisher 1 id:", poseExtracted.marker_id)
            # print('prev_marker_id',self.prev_marker_id)

        elif (self.prev_marker_id is not None and self.prev_marker_id != ids[0][0] and self.pub_flag is False):
            poseExtracted.marker_id = ids[0][0]
            self.prev_marker_id = ids[0][0]
            self.markerpose_pub2.publish(poseExtracted)
            self.pub_flag = True
            # print(self.pub_flag)
            # print("publisher 2 id:", poseExtracted.marker_id)
            # print('prev_marker_id',self.prev_marker_id)

        elif (self.prev_marker_id is not None and self.prev_marker_id != ids[0][0] and self.pub_flag is True):
            poseExtracted.marker_id = ids[0][0]
            self.prev_marker_id = ids[0][0]
            self.markerpose_pub1.publish(poseExtracted)
            self.pub_flag = False
            # print(self.pub_flag)
            # print("publisher 1 id:", poseExtracted.marker_id)
            # print('prev_marker_id',self.prev_marker_id)

        print(poseExtracted)

    '''commment the following lines to stop seeing the image output in a seperate window'''

    cv.imshow("Image window", frame)
    self.keystroke = cv.waitKey(1)
    if 32 <= self.keystroke and self.keystroke < 128:
        cc = chr(self.keystroke).lower()
        if cc == 'q':
            # The user has press the q key, so exit
            rospy.signal_shutdown("User hit q key to quit.")


def main(args):
  pc = pose_extractor()
  rospy.init_node('pose_extractor')
  try:
    rospy.spin()
  except rospy.ROSInterruptException:
    print("Shutting down")
  # cv.destroyAllWindows()

if __name__ == '__main__':
    main(sys.argv)
