#!/usr/bin/python
# -*- coding: utf-8 -*-###
# Copyright (2019) Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

import logging
import json
import os
import multiprocessing as mp
from datetime import datetime

# Multiprocessing lock for writing to syslog
lock = mp.Lock()

# No mapping available for UNKNOWN (Assuming the priority of Notice as UNKNOWN)
syslogStatusMap = {'CRITICAL':2, 'ERROR': 3, 'WARNING':4, 'UNKNOWN': 5, 'OK':6, 'DEBUG':7}
EXECUTION_LOG = "activity.log"
OV_ALERT_PARAMS = {"activeAlerts": ["alertState", "Active", ".timestamp"], "hpeOVRSAlerts": ["serviceEventSource", "true", ".serviceInfoTimestamp"]}

##################################################################
# Initialize for the logging.
#
##################################################################
def initialize_logging(syslogDir, syslogFile):
    global syslog_file

    # Initialize the log file path, log format and log level
    #logfiledir = os.getcwd() + os.sep + "oneview_logs"
    if not syslogDir:
       syslogDir = os.getcwd() + os.sep + "logs"

    if not syslogFile:
       syslogFile = "oneview_syslog"

    if not os.path.isdir(syslogDir):
        os.makedirs(syslogDir)

    syslog_file = syslogDir + os.sep + syslogFile
    print ("Oneview syslog is available in the file {}\n".format(syslog_file))

    # Initialize the log file path, log format and log level
    logfile = os.getcwd() + os.sep + EXECUTION_LOG

    # Init the logging module with default log level to INFO.
    logging.basicConfig(filename=logfile,
                        format='%(asctime)s - %(levelname)-5s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%d-%m-%Y:%H:%M:%S',
                        level=logging.WARNING)

###########################################################################################
# Function to write message to a log file
# 
###########################################################################################
def writeToSyslog(message):
    lock.acquire()
    try:
        with open(syslog_file, 'a+')  as logFile:
            logFile.write(message)
            logFile.write("\n")

    finally:
        lock.release()


##################################################################
# Function to convert oneview alerts into syslog format
# 
##################################################################
def createSyslog(alertObj, oneviewHost):
    created_date = alertObj['created']
    severity = alertObj['severity'].upper()
    alertId = alertObj['uri'].split('/')[-1]

    #print (alertObj)
    resource_type = alertObj['physicalResourceType']
    resource_name = alertObj['associatedResource']['resourceName']
    serviceEventInfo = alertObj['serviceEventDetails']

    if alertObj['serviceEventSource']:
       serviceEventInfo = "{}|{}|{}".format(serviceEventInfo['caseId'],
                                              serviceEventInfo['primaryContact'],
                                              str(serviceEventInfo['remoteSupportState']))
       serviceEventInfo = "{" + serviceEventInfo + "}"

    alert_info = "{}|{}|{}|{}|{}".format(alertId, alertObj['healthCategory'],
                                         alertObj['alertState'],
                                         alertObj['assignedToUser'],
                                         serviceEventInfo)
    
    childEvents = []
    if alertObj['childAlerts']:
        for element in alertObj['childAlerts']:
            #print(element)
            tempChildId = int(element.split('/')[-1])
            childEvents.append(tempChildId)
            
    alert_info = "{}|{}|{}|{}|{}|{}".format(alertId, 
                                         alertObj['healthCategory'],
                                         alertObj['alertState'],
                                         alertObj['assignedToUser'],
                                         serviceEventInfo, 
                                         childEvents)


    if alertObj['correctiveAction']:
        desc = alertObj['description'] + alertObj['correctiveAction']
    else:
        desc = alertObj['description']

    msg = "<{status}> {timestamp} {oneviewHost} oneview {resource_type} [{resource_name}] [{alert_info}] [{msg_info}]".format(timestamp=created_date, status=syslogStatusMap[severity], resource_type=resource_type, resource_name=resource_name, alert_info=alert_info, msg_info=desc, oneviewHost=oneviewHost)

    writeToSyslog(msg)


##################################################################
# Function to log active alerts triggered/updated after the 
# the last logged time
# 
##################################################################
def logAlerts(oneview_client, alertIdentifier):

    alertParams = OV_ALERT_PARAMS[alertIdentifier]
    activeAlerts = oneview_client.alerts.get_by(alertParams[0], alertParams[1])
    lastTimestamp = None
    newTimestamp = None

    try:
        with open(alertParams[2], 'r') as timestampFile:
            lastTimestamp = timestampFile.readlines()
            if lastTimestamp:
                lastTimestamp = datetime.strptime(lastTimestamp[0], '%Y-%m-%dT%H:%M:%S.%fZ')
    except IOError as error:
        print("File not present, collecting all the running {} alerts".format(alertIdentifier))

    for alert in activeAlerts:
        alertModTime = datetime.strptime(alert['modified'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if lastTimestamp and (alertModTime >= lastTimestamp):
            continue

        newTimestamp = alert['modified']
        createSyslog(alert, oneview_client.connection.get_host())

    if newTimestamp:
        writeTimestamp(newTimestamp, alertParams[2])

##################################################################
# Function to update the timestamp file from the last received
# message from SCMB
# 
##################################################################
def writeTimestamp(timestamp, fileName):
    with open(fileName, 'w') as timestampFile:
        timestampFile.write(timestamp)

