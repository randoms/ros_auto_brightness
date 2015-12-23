#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
自动根据摄像头数据调整亮度
'''
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
from subprocess import call
import sys

imageCount = 0
currentBrightness = 600
changeBrightnessFlag = False;

def setBrightness(brightness):
    global currentBrightness
    try:
        if type(brightness) is int:
            currentBrightness = brightness
        else:
            currentBrightness = int(brightness.data)
    except ValueError or TypeError:
        print "Not a valid number"
        return
    if currentBrightness > 5000 or currentBrightness < 4:
        print "Allowed value min=4 max=5000 step=1"
        return
    # set manual mode
    # try:
    #     retcode = call("v4l2-ctl --set-ctrl=exposure_auto=1", shell=True)
    #     if retcode < 0:
    #         print >>sys.stderr, "Child was terminated by signal", -retcode
    #     else:
    #         print >>sys.stderr, "Child returned", retcode
    # except OSError as e:
    #     print >>sys.stderr, "Execution failed:", e
    try:
        retcode = call("v4l2-ctl --set-ctrl=exposure_absolute=" + str(currentBrightness), shell=True)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", -retcode
        else:
            print >>sys.stderr, "Child returned", retcode
    except OSError as e:
        print >>sys.stderr, "Execution failed:", e

def calculateBrightness(image):
    global imageCount
    global currentBrightness
    global changeBrightnessFlag
    if imageCount < 60*10 and not changeBrightnessFlag:
        imageCount += 1
        return
    else:
        imageCount = 0
    res = [0]*(len(image.data)/3)
    mcolor = [ord(value) for value in image.data]
    res = sum(mcolor)/len(mcolor)
    # 每10s执行一次
    # 计算当前对平均亮度
    print res
    print "currentBrightness:" + str(currentBrightness)
    if res < 65 and currentBrightness < 5000:
        changeBrightnessFlag = True
        setBrightness(currentBrightness + 4);
    if res > 105 and currentBrightness > 4:
        changeBrightnessFlag = True
        setBrightness(currentBrightness - 4)
    if (res > 65 and res < 105) or currentBrightness >4990 or currentBrightness < 8:
        changeBrightnessFlag = False

def listener():
    rospy.init_node("listen", anonymous=True)
    rospy.Subscriber("/usb_cam/brightness", String, setBrightness)
    rospy.Subscriber("/usb_cam/image_raw", Image, calculateBrightness)
    rospy.spin()

if __name__ == '__main__':
    listener()
