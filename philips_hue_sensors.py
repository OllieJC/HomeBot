#!/usr/bin/python

import os, time, json
import hue_shared, slack_shared, homebot

LOOP_TIME = 5
MOTION_TIMEOUT = 180

hue_sensor_fname = "website_dynamic/PHILIPS_HUE_SENSORS.txt"

readings_array = []

def id_in_readings(id):
    counter = 0
    for reading in readings_array:
        if reading["id"] == id:
            return counter
        counter += 1
    return ""

def get_last_update(id):
    index = id_in_readings(id)
    if index != "":
        return readings_array[index]["lu"]
    return ""
    
def set_last_update(id, lastupdate, name):
    motion_detected = 0

    lastupdate_epoch = time.mktime(time.strptime(lastupdate, '%Y-%m-%dT%H:%M:%S'))
    obj = {"id":id, "lu":lastupdate_epoch, "name":name, "motion_detected": 0}

    index = id_in_readings(id)
    if index != "":
        #print(readings_array[index])
        previous_epoch = readings_array[index]["lu"]
        if previous_epoch != "":
            time_diff = lastupdate_epoch - previous_epoch
            if time_diff == 0:
                motion_detected = 0
                #print("No change in motion.")
            elif time_diff < MOTION_TIMEOUT:
                motion_detected = 0
                #print("* motion sensed again within 2.5 minutes - {0}".format(time_diff))
            else:
                print("Motion detected!")
                motion_detected = 1
                readings_array[index]["lu"] = lastupdate_epoch
                readings_array[index]["name"] = name
                readings_array[index]["motion_detected"] = motion_detected
    else:
        print("New presense object.")
        readings_array.append(obj)

    obj["motion_detected"] = motion_detected
    return obj

def update_readings_array():
    sensor_readings = hue_shared.get_sensors()
    
    with open (hue_sensor_fname, "w") as f:
        f.write(json.dumps(sensor_readings))
        
    for sensor in sensor_readings:
        if sensor["type"] == "presence":
            res = set_last_update(sensor["id"], sensor["lastupdated"], sensor["name"])
            if res["motion_detected"] == 1:
                msg = "*{0}* \nMotion detected at {1}".format(sensor["name"], sensor["lastupdated"].replace("T", " "))
                homebot_status = homebot.arm_status()
                print("Arming status: {0} - Message: {1}".format(homebot_status, msg))
                if homebot_status: # if armed, send message
                    slack_shared.message(msg, 1)

#print("Starting hue watcher!")
#slack_shared.message("Starting hue watcher!", 1)

while 1==1:
    update_readings_array()
    time.sleep(LOOP_TIME)
