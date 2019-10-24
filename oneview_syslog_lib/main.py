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

import sys
if sys.version_info < (3, 6):
    print('Incompatible version of Python, Please use Python ver 3.6 and above..!')
    sys.exit(1)

import argparse
import logging
import signal
import base64

import multiprocessing as mp
from datetime import datetime
from os import environ

from hpOneView.oneview_client import OneViewClient
from ov_client.oneview_client import acceptEULA

import internal.config as conf
import internal.polling_processes as polling
import internal.logutils as ovlog
import internal.scmb_utils as ovscmb

##################################################################
# Registering the signal handler for CTRL+C
#
# Caption Ctrl+C - Moving signal handler to close the log file
##################################################################
def signal_handler(signal, frame):
    # print('You pressed Ctrl+C! Exiting.')
    logging.info('You pressed Ctrl+C! Exiting.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


##################################################################
# Main function.
# 
##################################################################
def main():
    parser = argparse.ArgumentParser(add_help=True, description='Usage')
    parser.add_argument('-i', '--input_file',
                        dest='input_file',
                        required=False,
                        help='Json file containing oneview details')

    # Check and parse the input arguments into python's format
    inputParser = parser.parse_args()
    inputConfig = conf.getInputConfig(inputParser.input_file)
    oneviewDetails = inputConfig["oneview_config"]

    # Initialize logging
    ovlog.initialize_logging(syslogDir=oneviewDetails.get('syslogDir'),
                             syslogFile=oneviewDetails.get('syslog'))

    # get the logging level
    if inputConfig["logging_level"]:
        logLevel = logging.getLevelName(inputConfig["logging_level"].upper())
        logging.getLogger().setLevel(logLevel)

    # Get OneView Password
    if not oneviewDetails.get('passwd'):
        if "OV_PASSWORD" in environ:
            oneviewDetails["passwd"] = environ["OV_PASSWORD"]
        else:
            raise Exception("Missing oneview password. Please define " +
                            "the password in the input file or " +
                            "export OV_PASSWORD")
    else:
        password = base64.b64decode(oneviewDetails['passwd'].encode('utf-8'))
        oneviewDetails['passwd'] = password.decode('utf-8')

    conf.validate_input(oneviewDetails)

    # Logging input details.
    logging.info('OneView args: host = %s, alias = %s, route = %s', \
        oneviewDetails["host"], oneviewDetails["alias"], oneviewDetails["route"])

    ovConfig = {
        "ip": oneviewDetails["host"],
        "credentials": {
            "userName": oneviewDetails["user"],
            "password": oneviewDetails["passwd"],
            "authLoginDomain": oneviewDetails['authLoginDomain']
        }
    }

    try:
        oneview_client = OneViewClient(ovConfig)
        acceptEULA(oneview_client)
        logging.info("Connected to OneView appliance : {}".format(oneviewDetails["host"]))
    except Exception as e:
        err = "Error connecting to appliance: {}\n Check for oneview details in the input file".format(e)
        logging.error(e)
        raise Exception(err)

    # Create certs directory for storing the OV certificates
    ovscmb.setupAmqpCerts(oneview_client, oneviewDetails["host"])
    

    if oneviewDetails['collect_stats']:
        # Creating new process for polling processes
        #pollProcess = mp.Process(target=process_threads, args=(oneview_client, conf['alertHardwareTypes'], int(refreshDuration), ))
        pollProcess = mp.Process(target=polling.process_threads,
                                 args=(oneview_client,
                                       oneviewDetails['alert_hardware_category'],
                                       oneviewDetails['refresh_interval'], ))
        pollProcess.start()

    if oneviewDetails['collect_hpeov_service_info']:
        # Creating new process for polling HPE OV Service tickets
        hpeTicketProcess = mp.Process(target=polling.collect_hpeov_service_info,
                                      args=(oneview_client, ))
        hpeTicketProcess.start()

    # Logging all active alerts to syslog
    ovlog.logAlerts(oneview_client, "activeAlerts")

    # Start listening for messages.
    ovscmb.recv(oneviewDetails["host"], oneviewDetails["route"])


##################################################################
# Code execution flow to main() routine from here. 
# 
##################################################################
if __name__ == '__main__':
    sys.exit(main())
