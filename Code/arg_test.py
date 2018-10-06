#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
import csv
import sys
import argparse
from qsrlib.qsrlib import QSRlib, QSRlib_Request_Message
from qsrlib_io.world_trace import Object_State, World_Trace
#check for a few more import statements needed for the ROS functionality
#also consider adding a main function


#================================Creating a function to print out the results==================================#

def pretty_print_world_qsr_trace(which_qsr, qsrlib_response_message):

    print(which_qsr, "request was made at ", str(qsrlib_response_message.req_made_at)
          + " and received at " + str(qsrlib_response_message.req_received_at)
          + " and finished at " + str(qsrlib_response_message.req_finished_at))
    print("---")
    print("Response is:")
    for t in qsrlib_response_message.qsrs.get_sorted_timestamps():
        # This line is for printing the colons after the timestamp
        foo = str(t) + " :: "
        for k, v in zip(qsrlib_response_message.qsrs.trace[t].qsrs.keys(),
                        qsrlib_response_message.qsrs.trace[t].qsrs.values()):
            #this line adds the keys(objects) and their values(relations) to the foo object
            foo += str(k) + ":" + str(v.qsr) + "; "
        print(foo)

#==============================================================================================================#



#=================This section deals with parsing the user input from the terminal===============================#

#create a Qsrlib() object
qsrlib = QSRlib()

#creates a argparse object, which will be used to read from the terminal as well as check the arguments
parser = argparse.ArgumentParser(description='Get a Qualitative Spatial Representation ')

#we use 'add_argument' to tell the parser object what type of input we expect from the terminal
parser.add_argument('qsr', type=str, nargs='+', help='enter a qsr from the already listed ones')

#this reads the input from the terminal by using the parse_args() function
#this only accepts arguments of the type specified in the add_argument() function and can work with lists as well as individual arguments
args = parser.parse_args()

#We can print out the input from using terminal using print(args)

#This contains the implemented calcluli from the QSRlib library
options = sorted(qsrlib.qsrs_registry.keys())

#Use print statement to see what are the possible calculi that can be used to obtain spatial relationships from the QSRlib
# print ("These are the options available for matching", options)

#create a list of the calculi obtained from the user's input
this_qsr = args.qsr
#==============================================================================================================#



#=================================Mock up data for testing=====================================================#
# creating input data, he basic data structure used in QSRlib is the World_Trace object
world = World_Trace()

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

#==============================================================================================================#



#============We calculate the spatial relationships in these section===========================================#
#creating a list to store the request messagest to QSRlib
qsrlib_request_message = list()
#
# #creating a list to store the response from the QSRlib
qsrlib_response_message = list()

#iterating over the entire list to obtain all the individual calculi for which the spatial relationships will be calculated
for i in range(len(this_qsr)):

    #performs a check to see if the input qsr's are present in the QSRlib library
    if this_qsr[i] in options:
        #printing them out in a readable format, just for clarity
        print("These are the requested qsr's:%s"%(this_qsr[i]) + ", this is the qsr id:%i"%(i))

        #creating a message to the QSRlib for calculating the relationships
        # qsrlib_request_message.append(QSRlib_Request_Message(this_qsr[i], world))
        qsrlib_request_message.append(QSRlib_Request_Message(this_qsr[i], world))


        #parsing the received arguments
        # qsrlib_response_message.append(qsrlib.request_qsrs(req_msg=qsrlib_request_message[i]))
        qsrlib_response_message.append(qsrlib.request_qsrs(req_msg=qsrlib_request_message[i]))


        #print the received arguments
        pretty_print_world_qsr_trace(this_qsr[i], qsrlib_response_message[i])

    else :
        print('didn\'t find the qsr')

#==============================================================================================================#
