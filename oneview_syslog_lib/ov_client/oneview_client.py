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

import logging
from time import sleep
from datetime import datetime, timedelta

##################################################################
# Accept OneView Eula.
# 
##################################################################
def acceptEULA(oneview_client):
    logging.info('acceptEULA')

    eula_status = oneview_client.connection.get_eula_status()
    try:
        if eula_status is True:
            oneview_client.connection.set_eula('no')
    except Exception as e:
        logging.error('EXCEPTION:')
        logging.error(e)


##################################################################
# Process ports status 
#  
##################################################################
def get_port_statistics(oneview_client):

    data = []

    # Get all interconnects and parse them one by one
    interconnects = oneview_client.interconnects.get_all()

    for interconnect in interconnects:
        interconnectName = interconnect['name']
        linkedPorts = []
        unlinkedPorts = []
        # Get all ports in an interconnect
        interconnect_ports = oneview_client.interconnects.get_ports(interconnect['uri'])

        # get port statistics
        for port in interconnect_ports:
            if port['portStatus'] == "Linked":
                portName = port['portName']
                members = {}
                members['Status'] = port['status']
                advanced_stats = oneview_client.interconnects.get_statistics(interconnect['uri'],portName)
                if port['operationalSpeed']:
                    members['Speed'] = port['operationalSpeed']
                else:
                    members['Speed'] = None
                if port['neighbor']:
                    if port['neighbor']['remotePortId']:
                        members['adopterPort'] = port['neighbor']['remotePortId']
                    else:
                        members['adopterPort'] = None
                    if port['neighbor']['remoteMgmtAddress']:
                        members['macAddress'] = port['neighbor']['remoteMgmtAddress']
                    else:
                        members['macAddress'] = None
                else:
                     members['adopterPort'] = None
                     members['macAddress'] = None
                
                if advanced_stats and advanced_stats['commonStatistics']:
                    members['IfInOctets'] = advanced_stats['commonStatistics']['rfc1213IfInOctets']
                    members['IfOutOctets'] = advanced_stats['commonStatistics']['rfc1213IfOutOctets']

                    # Errors in Transmit/Receive
                    members['IfInErrors']  = advanced_stats['commonStatistics']['rfc1213IfInErrors']
                    members['IfOutErrors'] = advanced_stats['commonStatistics']['rfc1213IfOutErrors']
                else:
                    members['IfInOctets']  = None
                    members['IfOutOctets'] = None
                    members['IfInErrors']  = None
                    members['IfOutErrors'] = None

                linkedPorts.append({'portName':portName,'members': members})
            elif port['portStatus'] == "Unlinked":
                unlinkedPorts.append(port['portName'])
        data.append({'interconnectName' : interconnectName, 'linkedPorts' : linkedPorts ,'unlinkedPorts' : unlinkedPorts})
    return data

##################################################################
# Get the host's status to update in log file when required.
#  
##################################################################
def get_hosts_status(oneview_client,hostCategory):
    hosts_status = []

    if hostCategory == "interconnects":
        #Get all interconnects
        response  = []
        interconnects = oneview_client.interconnects.get_all()
        # Extending the list with interconnects
        response.extend(interconnects)
        # TODO - To be validated in DCS
        sas_interconnects = oneview_client.sas_interconnects.get_all()
        if sas_interconnects:
            # Extending the list with sas-interconnects
            response.extend(sas_interconnects)
        logical_interconnects = oneview_client.logical_interconnects.get_all()
        if logical_interconnects:
            # Extending the list with logical-interconnects
            response.extend(logical_interconnects)
            
    if hostCategory == 'enclosures':
        # Get all enclosures
        response = oneview_client.enclosures.get_all()

    if hostCategory == 'server-hardware':
        # Get all server hardwares
        response = oneview_client.server_hardware.get_all()

    for member in response:
        data = {}
        #Construct data body
        hostName = trim_name(member['name'])
        data['hostname'] = hostName.replace(' ','_')
        data['status'] = member['status']
        data['state'] = member['state']
        try:
        # if member['category'] == 'logical-interconnects':
            data['model'] = member['model']
        # else:
        except KeyError:
            data['model'] = 'N.A'
        hosts_status.append(data)
    return hosts_status
