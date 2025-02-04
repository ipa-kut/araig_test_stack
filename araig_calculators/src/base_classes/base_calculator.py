#!/usr/bin/env python
import sys
import rospy
import threading

"""supprot subscribe mix 3 topics
    if need more, only need to add as
    function callback_1""" 
class CallbackList():
    def callback_0(self, msg, args):
        BaseCalculator.MSG[args] = None
        with BaseCalculator.LOCK[args]:
            BaseCalculator.MSG[args] = msg

    def callback_1(self, msg, args):
        BaseCalculator.MSG[args] = None
        with BaseCalculator.LOCK[args]:
            BaseCalculator.MSG[args] = msg
    
    def callback_2(self, msg, args):
        BaseCalculator.MSG[args] = None
        with BaseCalculator.LOCK[args]:        
            BaseCalculator.MSG[args] = msg

""" pub_dict = {"event topic": "data_type", ...}
    sub_dict = {"topic_1": "data_type", "topic_2": "data_type" ...}
    rosparam""" 
class BaseCalculator(object):
    MSG = {}
    LOCK = {}

    def __init__(self,
        pub_dict = None,
        sub_dict = None,
        callback_module = CallbackList(), # class CallbackList
        rate = None):

        if pub_dict == None:
            rospy.logerr("{}:  Please provide output(pub) topic and data type".format(rospy.get_name()))
                
        if sub_dict == None:
            rospy.logerr("{}:  Please provide input(sub) topic and data type".format(rospy.get_name()))

        if rate == None:
            rospy.logerr("{}:  Please provide rate".format(rospy.get_name()))
        self._rate = rospy.Rate(rate)

        self.SubDict = sub_dict
        self.PubDict = pub_dict

        self.callback_module = callback_module

        self.pub_init()
        self.sub_init()

        # init FLAG and LOCK
        for topic in self.SubDict.keys():
            BaseCalculator.MSG[topic] = None
            BaseCalculator.LOCK[topic] = threading.Lock()
                
        self.main()

    def pub_init(self):
        self.PubDiag = {}

        for topic in self.PubDict.keys():
            data_type_module = self.PubDict[topic]

            self.PubDiag[topic] = rospy.Publisher(
                topic, 
                data_type_module, 
                latch = True, 
                queue_size=10
                )
    
    def sub_init(self):
        self.sub_diag = {}
        self.sub_dict = {}

        for counter, topic in enumerate(self.SubDict.keys()):
            data_type_module = self.SubDict[topic]
            # call_back_name = topic.replace('/','_')
            callback = getattr(self.callback_module, 'callback_'+ str(counter))
            self.sub_diag[topic] = rospy.Subscriber(topic, data_type_module, callback, (topic))
    
    #  should be inherit
    def calculate(self):
        pass

    def main(self):
        try:
            while not rospy.is_shutdown():        
                
                self.calculate() 
                self._rate.sleep()

        except rospy.ROSException:
            pass    