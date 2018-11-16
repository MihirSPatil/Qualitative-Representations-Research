#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
import csv
import sys
import argparse
from qsrlib.qsrlib import QSRlib, QSRlib_Request_Message
from qsrlib_io.world_trace import Object_State, World_Trace
import sys
try:
    import cPickle as pickle
except:
    import pickle


#================================Creating a function to print out the results==================================#

def pretty_print_world_qsr_trace(which_qsr, qsrlib_response_message):

    print(which_qsr, "request was made at ", str(qsrlib_response_message.req_made_at)
          + " and received at " + str(qsrlib_response_message.req_received_at)
          + " and finished at " + str(qsrlib_response_message.req_finished_at))
    print("---")
    print("Response is:")
    for t in qsrlib_response_message.qsrs.get_sorted_timestamps():
        # This line is for printing the colons after the timestamp
        foo = str(t) + " => "
        for k, v in zip(qsrlib_response_message.qsrs.trace[t].qsrs.keys(),
                        qsrlib_response_message.qsrs.trace[t].qsrs.values()):
            #this line adds the keys(objects) and their values(relations) to the foo object
            foo += str(k) + ":" + str(v.qsr) + "; "
        print(foo)

#==============================================================================================================#


#============================================Main function=====================================================#

#make sure the qsrlib_ros_server is running before running this code

if __name__ == "__main__":

    #adding a new option to the already registered QSR's
    options = sorted(QSRlib().qsrs_registry.keys())+["multiple"]
    print("These are the implemented set of qualitative calculi:\n", options)

    #one way of defining multiple qsr's for computing spatial relationships, if using this method add '+["multiple"]' to options line above
    # multiple = options[:]; multiple.remove("multiple"); multiple.remove("argprobd"); multiple.remove("cardir"); multiple.remove("mwe"); multiple.remove("qtcbs"); multiple.remove("qtccs"); multiple.remove("rcc2"); multiple.remove("rcc3"); multiple.remove("rcc4"); multiple.remove("ra"); multiple.remove("tpcc"); multiple.remove("rcc8");

    #defining the qsr's for which to calculate the spatial realtionships, can change the selected qsr's by just changing the index nos.
    multiple = [options[0], options[6], options[7]]

    #converting the tuple to a list
    multiple = list(multiple)
    print("These are the selected qualitative calculi:\n",multiple)

    #creates a argparse object, which will be used to read from the terminal as well as check the arguments
    parser = argparse.ArgumentParser()

    #we use 'add_argument' to tell the parser object what type of input we expect from the terminal
    parser.add_argument("qsr", help="choose qsr: %s" % options, type=str)

    #this argument tells the code to use the user defined path to a  csv file containing the data
    parser.add_argument("-i", "--input", help="file from which to read object states", type=str)

    #this argument is to verify that the spatial relations are valid
    parser.add_argument("--validate", help="validate state chain. Only QTC", action="store_true")

    #this argument is used to specify the distance threshold at which the switch from qtcb to qtcc should occur
    parser.add_argument("--distance_threshold", help="distance threshold for qtcb <-> qtcc transition. Only QTCBC", type=float)

    #argument that provides the option of running the code using ROS
    parser.add_argument("--ros", action="store_true", default=False, help="Use ROS eco-system")

    #this reads the input from the terminal by using the parse_args() function
    #this only accepts arguments of the type specified in the add_argument() function and can work with lists as well as individual arguments
    args = parser.parse_args()

    # we check if the user's argument is the same as we are expecting
    if args.qsr == "multiple":
        input_qsr = multiple

        # creating input data, he basic data structure used in QSRlib is the World_Trace object
        world = World_Trace()

        #check if the user has specified a csv file to read the input data from
        if args.input:

            #creating a empty list to which we will append the data
            obj = []

            with open(args.input) as csvfile:

                # creating a csv object to parse the info from the csv file
                file = csv.DictReader(csvfile)
                print("Reading file '%s':" % args.input)

                for idx,row in enumerate(file):

                    # using the column headers to determine the object names and their pose and timestamp, the inbuilt csv index is used as a timestamp
                    obj.append(Object_State(
                        name=row['agent1'],
                        timestamp=idx,
                        x=float(row['x1']),
                        y=float(row['y1'])
                    ))
                    obj.append(Object_State(
                        name=row['agent2'],
                        timestamp=idx,
                        x=float(row['x2']),
                        y=float(row['y2'])
                    ))

            #adding the objects(spatial entities) to the created World_Trace object
            world.add_object_state_series(obj)

        else:

            #creating mulitple spatial entities with their respective poses, ids and sizes for mulitple timestamp everything is in terms of pixels
            o1 = [Object_State(name="o1", timestamp=0, x=226, y=287., xsize=5., ysize=8.),
                  Object_State(name="o1", timestamp=1, x=308., y=289., xsize=5., ysize=8.),
                  Object_State(name="o1", timestamp=2, x=330., y=324., xsize=5., ysize=8.),
                  Object_State(name="o1", timestamp=3, x=387., y=349., xsize=5., ysize=8.)]

            #creating a second spatial entity with different poses
            o2 = [Object_State(name="o2", timestamp=0, x=500, y=330, xsize=5., ysize=8.),
                  Object_State(name="o2", timestamp=1, x=1026., y=262., xsize=5., ysize=8.),
                  Object_State(name="o2", timestamp=2, x=1144., y=247., xsize=5., ysize=8.),
                  Object_State(name="o2", timestamp=3, x=1268., y=262., xsize=5., ysize=8.)]

            o3 = [Object_State(name="o3", timestamp=0, x=640., y=360., xsize=10, ysize=10),
                  Object_State(name="o3", timestamp=1, x=640, y=360., xsize=10, ysize=10),
                  Object_State(name="o3", timestamp=2, x=640., y=360, xsize=10, ysize=10),
                  Object_State(name="o3", timestamp=3, x=640., y=360., xsize=10, ysize=10)]

            #adding the objects(spatial entities) to the created World_Trace object
            world.add_object_state_series(o1)
            world.add_object_state_series(o2)
            world.add_object_state_series(o3)


        #setting the distance values to be used with the argd qualitative calculi
        distance = {"touch": 8., "near": 16., "medium": 32., "far":64.}

        # setting dynamic arguments for the argd qualitative calculi
        dynamic_args = {"argd": {"qsr_relations_and_values":distance},
                        "qtcbcs":{"distance_threshold":args.distance_threshold,
                                  "validate":args.validate}}

        #creating the request message containing the data about the selected qsr and the world
        qsrlib_request_message = QSRlib_Request_Message(which_qsr=input_qsr, input_data=world, dynamic_args=dynamic_args)

    else:
        print ("this code only accepts 'multiple' as an input argument, and outputs a combination of spatial realtionships")
    #check if the user has specified to run with ROS
    if args.ros:
        #import the required ROS libraries
        try:
            import rospy
            from qsrlib_ros.qsrlib_ros_client import QSRlib_ROS_Client
        except ImportError:
            raise ImportError("ROS not found")

        #creating a client node using the pre-defined example
        client_node = rospy.init_node("qsr_lib_ros_client_example")
        # creating a client
        cln = QSRlib_ROS_Client()

        #creating the request message
        req = cln.make_ros_request_message(qsrlib_request_message)

        #creating the response message
        res = cln.request_qsrs(req)
        print ('created the response and the request')
        qsrlib_response_message = pickle.loads(res.data)
    else:
        qsrlib = QSRlib()
        qsrlib_response_message = qsrlib.request_qsrs(req_msg=qsrlib_request_message)

    #calling the pretty print method to print everything in a readable format
    pretty_print_world_qsr_trace(input_qsr, qsrlib_response_message)

#==============================================================================================================#
