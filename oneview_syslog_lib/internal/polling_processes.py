#!/usr/bin/python
# -*- coding: utf-8 -*-###
# Copyright (2018) Hewlett Packard Enterprise Development LP
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

#from common.utils import *
import multiprocessing as mp
from time import sleep,strftime,localtime
from datetime import datetime

import internal.logutils as ovlog 
from ov_client.oneview_client import get_hosts_status,get_port_statistics
import logging

###########################################################################################
# Function which uses multiprocessing for updating hosts status, interconnects ports status 
# and enclosure power stats
###########################################################################################
def process_threads(oneview_client, hardwareCategory, refreshDuration=600):
    threadPool = mp.Pool(6)

    # Filtering interested hardwares for status update.
    hardwareCategory = [hardware for hardware in hardwareCategory if hardware not in ('sas-interconnects','logical-interconnects')]
    while True:
        logging.info("Calling update enclosure in thread")
        threadPool.apply_async(update_enclosures_stats, args=(oneview_client,))

        logging.info("Calling update ports status in thread.")
        threadPool.apply_async(update_ports_status, args=(oneview_client,))

        logging.info("Calling update server stats in thread.")
        threadPool.apply_async(update_server_stats, args=(oneview_client,))

        for hardware in hardwareCategory:
            logging.info("Calling update {} status in thread.".format(hardware))
            threadPool.apply_async(update_all_hosts_status, args=(oneview_client, hardware))

        sleep(refreshDuration)

    threadPool.close()
    threadPool.join()

###########################################################################################
# Function which uses multiprocessing for updating hosts status, interconnects ports status 
# and enclosure power stats
###########################################################################################
def collect_hpeov_service_info(oneview_client, refreshDuration=120):
    threadPool = mp.Pool(6)

    while True:
        ovlog.logAlerts(oneview_client, "hpeOVRSAlerts")
        sleep(refreshDuration)

    threadPool.close()
    threadPool.join()

###########################################################################################
# Function to update all ports status
# 
###########################################################################################
def update_ports_status(oneview_client):
    allPortStats = get_port_statistics(oneview_client)

    logging.info("Updating all ports status in logfile.")
    data = {}
    for interconnect in allPortStats:
        data['name'] = interconnect["interconnectName"]

        for port in interconnect['linkedPorts']:
            data['timestamp'] = datetime.now().isoformat()[:-3] + "Z"
            data['portName']  = port["portName"]
            data['status'] = port["members"]["Status"]
            data['speed']  = port["members"]["Speed"]
            data['adapterPort'] = port["members"]["adopterPort"]
            data['recv_octets'] = port["members"]["IfInOctets"]
            data['transmit_octets'] = port["members"]["IfOutOctets"]
            data['transmit_errors'] = port["members"]["IfOutErrors"]
            data['recv_errors'] = port["members"]["IfInErrors"]

            msg = ("<{status}> {timestamp} {oneview_ip} oneview PortStats [{interconnect}] "
                  "[{port}|Transmit={transmit}|Receive={receive}|TransmitErr={transmitErr}|"
                  "ReceiveErr={receiveErr}|Speed={speed}|AdaptorPort={adapter}]\n").format(
                  timestamp=data["timestamp"],
                  status=ovlog.syslogStatusMap[data["status"].upper()],
                  interconnect=data['name'], port=data['portName'],
                  transmit=data["transmit_octets"], receive=data["recv_octets"],
                  transmitErr=data['transmit_errors'], receiveErr=data['recv_errors'],
                  speed=data['speed'], adapter=data['adapterPort'],
                  oneview_ip=oneview_client.connection.get_host())
            ovlog.writeToSyslog(msg)
            sleep(0.3)


###########################################################################################
# Function to update stats of all enclosures.
# 
###########################################################################################
def update_enclosures_stats(oneview_client):
    # Get all enclosures
    enclosures = oneview_client.enclosures.get_all()

    # Update stats of each enclosure
    logging.info('Updating enclosure powerstats. ')
    for enclosure in enclosures:
        process_enclosure_stats(enclosure["name"], enclosure["uri"], oneview_client)
        sleep(0.3)

###########################################################################################
# Function to get and proceess enclosure stats
# 
###########################################################################################
def process_enclosure_stats(enclName, URI, oneview_client):
    enclPowerStats = oneview_client.enclosures.get_utilization(URI)
    fullMetrics = enclPowerStats["metricList"]    
    allEnclosuresStats = []
    encStats = {}
    for metrics in fullMetrics:
        encStats["metricName"] = metrics["metricName"]
        epochTimeStamp = metrics["metricSamples"][0][0]/1000 # Timestamp is in millisec.
        encStats["timeStamp"] = strftime('%Y-%m-%dT%H:%M:%SZ', localtime(epochTimeStamp))
        encStats["value"] = metrics["metricSamples"][0][1]
        allEnclosuresStats.append(encStats)
        encStats = {}

    if allEnclosuresStats:
        status = ("<6> {timestamp} {hostname} oneview EnclosureStats [{encName}] "
                 "[AmbientTemperature={ambTemp} dec C|AveragePower={avgPower} watts|"
                 "PeakPower={peakPower} watts]\n").format(
                  timestamp = allEnclosuresStats[0]["timeStamp"],
                  hostname  = oneview_client.connection.get_host(),
                  encName   = enclName,
                  ambTemp   = allEnclosuresStats[0]["value"],
                  avgPower  = allEnclosuresStats[1]["value"],
                  peakPower = allEnclosuresStats[2]["value"])
        ovlog.writeToSyslog(status)


###########################################################################################
# Function to update all hosts status.
# 
###########################################################################################
def update_all_hosts_status(oneview_client, hardwareCategory):
    logging.info('Updating {} status in logfile.'.format(hardwareCategory))
    response = get_hosts_status(oneview_client,hardwareCategory)
    if response:
        for entity in response:
            hostname = entity['hostname']
            status = entity['status']
            corrAction = entity['state']
            description = entity['model']
            update_host_status(hostname,status,corrAction,description)


###########################################################################################
# Function to update individual hosts status.
# Called by update_all_hosts_status()
#
###########################################################################################
def update_host_status(hostName, status,description='Updating status in logfile.',corrAction='None'):

    # Empty JSON to hold all relevant information
    data = {}
    status = status.upper()
    data["timestamp"] = datetime.now().isoformat()[:-3] + "Z"
    data["resource_name"] = hostName
    data["correctiveAction"] = corrAction

    if status in nodeStatusMap:
        data["description"] = description
        data["status"] = status
    else:
        logging.error("Check host status :- " + hostName + ". Its not OK.")
        data["description"] = 'Node not in valid status. Check. '

        # Node unreachable
        data["status"] = "UNKNOWN"

    msg = ("<{status}> {timestamp} {oneview_ip} oneview NodeStats "
          "[{hostname}] [{action}|{model}|None]\n").format(
           timestamp = data["timestamp"],
           status    = ovlog.syslogStatusMap[data["status"].upper()],
           hostname  = hostName,
           model  = data["description"],
           action = data["correctiveAction"],
           oneview_ip = oneview_client.connection.get_host())
            
    ovlog.writeToSyslog(msg)


###########################################################################################
# Function to update server stats.
# 
###########################################################################################
def update_server_stats(oneview_client):
    servers = oneview_client.server_hardware.get_all()
    for server in servers:
        serverStatsResponse = oneview_client.server_hardware.get_utilization(server["uri"])
        fullMetrics = serverStatsResponse["metricList"]    
        serverAllStats = []
        serverStats = {}
        for metrics in fullMetrics:
            serverStats["metricName"] = metrics["metricName"]
            epochTimeStamp = metrics["metricSamples"][0][0]/1000 # Timestamp is in millisec.
            serverStats["timeStamp"] = strftime('%Y-%m-%dT%H:%M:%SZ', localtime(epochTimeStamp))
            serverStats["value"] = metrics["metricSamples"][0][1]
            sleep(3)
            serverAllStats.append(serverStats)
            serverStats = {}
            
        if serverAllStats:
            status = ("<6> {timestamp} {ipAddr} oneview ServerStats [{serverName}] "
                     "[AmbientTemperature={ambTemp} dec C|AveragePower={avgPower} watts|"
                     "CpuAverageFreq={cpuAvgFreq} Hz|CpuUtilization={cpuUtil} %|"
                     "PeakPower={peakPower} watts|PowerCap={powerCap}]\n").format(
                     timestamp  = serverAllStats[0]["timeStamp"],
                     ipAddr     = oneview_client.connection.get_host(),
                     serverName = server["name"],
                     ambTemp    = serverAllStats[0]["value"],
                     avgPower   = serverAllStats[1]["value"],
                     cpuAvgFreq = serverAllStats[2]["value"],
                     cpuUtil    = serverAllStats[3]["value"],
                     peakPower  = serverAllStats[4]["value"],
                     powerCap   = serverAllStats[5]["value"] )
            ovlog.writeToSyslog(status)

