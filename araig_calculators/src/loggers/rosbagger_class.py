#!/usr/bin/env python
# license removed for brevity
import rospy
import subprocess, shlex
from araig_msgs.msg import BoolStamped
import threading

class RosbaggerClass(object):
    def __init__(self,  start_topic = "/start",
                        stop_topic = "/stop",
                        stop_offset = 2,
                        filename ="test"):
        self.filename_ = filename 
        self._stop_offset = stop_offset
        self.start_mutex_ = threading.Lock()
        self.stop_mutex_ = threading.Lock()
        self._start_recording = False
        self._stop_recording_ = False
        self._rate = rospy.Rate(10)

        rospy.Subscriber(start_topic, BoolStamped, self.start_callback)
        rospy.Subscriber(stop_topic, BoolStamped, self.stop_callback)

        list_of_topics = rospy.get_published_topics()
        list_of_topics.sort()

        self._topics_string = ""
        for topic, msg in list_of_topics:
            if "/image_raw" in topic:
                if (not "/image_raw/compressed" in topic) or ("compressedDepth" in topic) :
                    rospy.loginfo(rospy.get_name() + ": Ignoring topic - {}".format(topic))
                    continue
                else:
                    self._topics_string = self._topics_string + topic + " "
            else:
                self._topics_string = self._topics_string + topic + " "

        # Prepare command
        self._command = "rosbag record -o " + self.filename_ + " " + self._topics_string
        # rospy.loginfo(rospy.get_name() + ": Ready to execute: " + self._command)
        self.main_loop()
        rospy.spin()

    def __del__(self):
        rospy.loginfo(rospy.get_name() + ": Destructor killing process {}".format(self._rosbag_proc))
        self._rosbag_proc.send_signal(subprocess.signal.SIGINT)

    def stop_callback(self, msg):
            with self.stop_mutex_:
                self._stop_recording_ = msg.data

    def start_callback(self, msg):
            with self.start_mutex_:
                self._start_recording = msg.data

    def main_loop(self):
        rospy.loginfo(rospy.get_name() + ": Waiting for start signal...")
        # Wait for start signal
        start = False
        while not start and not rospy.is_shutdown():
            self._rate.sleep()
            with self.stop_mutex_:
                start = self._start_recording
        
        rospy.loginfo(rospy.get_name() + ": Starting recording now!")
            
        command = shlex.split(self._command)
        self._rosbag_proc = subprocess.Popen(command)

        # Wait for stop signal
        with self.stop_mutex_:
                stop = self._stop_recording_
        while not stop:
            self._rate.sleep()
            with self.stop_mutex_:
                stop = self._stop_recording_
            if rospy.is_shutdown():
                rospy.loginfo(rospy.get_name() + ": Got kill signal, ending process {}".format(self._rosbag_proc))
                self._rosbag_proc.send_signal(subprocess.signal.SIGINT)
                rospy.loginfo(rospy.get_name() + ": Process killed")
                return
        rospy.loginfo(rospy.get_name() + ": Got kill signal, ending process {} after {}s"
                                        .format(self._rosbag_proc, self._stop_offset))
        rospy.sleep(rospy.Duration(self._stop_offset))
        self._rosbag_proc.send_signal(subprocess.signal.SIGINT)
        rospy.loginfo(rospy.get_name() + ": Process killed")