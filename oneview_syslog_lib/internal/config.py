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

##################################################################
# List of parameters that would be imported
#    OV_HOSTNAME - Mandatory
#    OV_USERNAME - Mandatory
#    OV_PASSWORD - Mandatory
#    OV_ALIAS_NAME        - Optional: Oneview-OV_HOSTNAME
#    OV_AUTH_LOGIN_DOMAIN - Optional: LOCAL
#    OV_SCMB_ROUTE        - Optional: 'scmb.alerts.#'
#    OV_ALERT_TYPE        - Optional: "Critical:Warning:Ok"
#    OV_RESOURCE_CATEGORY - Optional: "server-hardware:enclosures:interconnects:logical-interconnects:sas-interconnects"
#    OV_COLLECT_STATS     - Optional: "true"
#    OV_COLLECT_HPEOV_SERVICE     - Optional: "false"
#    OV_REFRESH_INTERVAL  - Optional: 600
#    OV_SYSLOG_FILEPATH   - Optional: "logs"
#    OV_SYSLOG_FILE       - Optional: "oneview_syslog"
#    OV_LOGGING_LEVEL     - Optional: "WARNING"
##################################################################

CONFIG_DEFAULTS = {
    'alert_type': "Critical:Warning:Ok",
    'alert_hardware_category': "server-hardware:enclosures:interconnects:logical-interconnects:sas-interconnects",
    'authLoginDomain': "LOCAL",
    'route': "scmb.alerts.#",
    'syslog_dir': "logs",
    "collect_stats": "true",
    "collect_hpeov_service_info": "false",
    "refresh_interval": 600,
    'syslog_file': "oneview_syslog",
    'logging_level': "WARNING"
}

# Valid alert types sent by Oneview. This is used to compare the user input "alert_type" from oneview.json file
SUPPORTED_TYPES = {
    'alerts': ['Ok','Warning','Critical','Unknown'],
    'hardwares': ['server-hardware','enclosures','interconnects','sas-interconnects','logical-interconnects']
}

def importReqVars():
    inputConfig = {}
    oneview_config = {}

    mandatory_envs = ["OV_HOSTNAME", "OV_USERNAME"]

    if not all(key in os.environ for key in mandatory_envs):
        err = "Missing one or all the mandatory parameters in exported variables: {}".format(mandatory_envs)
        raise Exception(err)

    oneview_config['host']   = os.environ['OV_HOSTNAME']
    oneview_config['user']   = os.environ['OV_USERNAME']
    inputConfig['oneview_config'] = oneview_config

    return inputConfig

def fillMissingVars(inputConfig):
    # Optional Parameters
    oneview_config = inputConfig['oneview_config']

    if not oneview_config.get('alias'):
        oneview_config['alias'] = os.environ.get('OV_ALIAS_NAME', '{}-{}'.format("HPEOneview", oneview_config["host"]))

    if not oneview_config.get('route'):
        oneview_config['route'] = os.environ.get('OV_SCMB_ROUTE', CONFIG_DEFAULTS['route'])

    if not oneview_config.get('alert_type'):
        oneview_config['alert_type'] = os.environ.get('OV_ALERT_TYPE', CONFIG_DEFAULTS['alert_type'])

    if not oneview_config.get('authLoginDomain'):
        oneview_config['authLoginDomain'] = os.environ.get('OV_AUTH_LOGIN_DOMAIN', CONFIG_DEFAULTS['authLoginDomain'])

    if not oneview_config.get('alert_hardware_category'):
        oneview_config['alert_hardware_category'] = os.environ.get('OV_RESOURCE_CATEGORY', CONFIG_DEFAULTS['alert_hardware_category'])

    if not oneview_config.get('collect_stats'):
        oneview_config['collect_stats'] = os.environ.get('OV_COLLECT_STATS', CONFIG_DEFAULTS['collect_stats'])
    
    if oneview_config['collect_stats'].lower() == "true":
        oneview_config['collect_stats'] = True
    else:
        oneview_config['collect_stats'] = False

    if not oneview_config.get('collect_hpeov_service_info'):
        oneview_config['collect_hpeov_service_info'] = os.environ.get('OV_COLLECT_HPEOV_SERVICE', CONFIG_DEFAULTS['collect_hpeov_service_info'])
    
    if oneview_config['collect_hpeov_service_info'].lower() == "true":
        oneview_config['collect_hpeov_service_info'] = True
    else:
        oneview_config['collect_hpeov_service_info'] = False

    if not oneview_config.get('refresh_interval'):
        oneview_config['refresh_interval'] = os.environ.get('OV_REFRESH_INTERVAL', CONFIG_DEFAULTS['refresh_interval'])
    
    if not oneview_config.get('syslogDir'):
        oneview_config['syslogDir'] = os.environ.get('OV_SYSLOG_FILEPATH', CONFIG_DEFAULTS['syslog_dir'])

    if not oneview_config.get('syslog'):
        oneview_config['syslog'] = os.environ.get('OV_SYSLOG_FILE', CONFIG_DEFAULTS['syslog_file'])

    if not inputConfig.get('logging_level'):
        inputConfig["logging_level"] = os.environ.get('OV_LOGGING_LEVEL', CONFIG_DEFAULTS['logging_level'])

    inputConfig['oneview_config'] = oneview_config
    return inputConfig

def getInputConfig(configFile):
    if configFile:
        with open(configFile) as data_file:    
            try:
                 inputConfig = json.load(data_file)
            except Exception as e:
                 error = "Failed to load JSON file {file}: {traceback}".format(file=configFile, traceback=e)
                 raise Exception(error)
    else:
        print("Failed to load input configuration, check using environment variables")
        inputConfig = importReqVars()

    if not inputConfig.get("oneview_config"):
        err = "Missing oneview information. Check the config file or export the OV_* variables"
        logging.error(err)
        raise Exception(e)

    inputConfig = fillMissingVars(inputConfig)
    return inputConfig

##################################################################
# Validate Json config file
# 
##################################################################
def validate_input(oneViewDetails):
    validate_oneview_details(oneViewDetails)
    validate_hardware_category(oneViewDetails)
    validate_alert_types(oneViewDetails)

    logging.info("Successfully validated input file")


##################################################################
# Validate OneView appliance details.
# Function needs to be added with new parameters when updated in Json
##################################################################
def validate_oneview_details(oneViewDetails):
    required_fields = ('host','user', 'passwd')
    # Validate inputs
    if not all(keys in oneViewDetails for keys in required_fields):
        err = "Oneview details incomplete. Please ensure following values present in input json file:- host, user, passwd"
        logging.error(err)
        raise Exception(err)


##################################################################
# Validate hardware types give in input file
# Function needs to be added with new parameters when updated in Json
##################################################################
def validate_hardware_category(oneViewDetails):
    # Get hardware category as list
    hardwareType = oneViewDetails["alert_hardware_category"]
    alertHardwareTypes = hardwareType.split(':')
    # config['alertHardwareTypes'] = alertHardwareType

    for hardware in alertHardwareTypes:        
        if not hardware in SUPPORTED_TYPES['hardwares']:
            err = "Hardware type - \"{}\" is not permissible. Valid types - {} \nExiting.. ".format(hardware, SUPPORTED_TYPES['hardwares'])
            logging.error(err)
            raise Exception(err)
        elif not hardware:
            err = "Enter interested hardware types in config file. Exiting..."
            logging.error(err)
            raise Exception(err)


##################################################################
# Validate Validate alert types give in input file
# Function needs to be added with new parameters when updated in Json
##################################################################
def validate_alert_types(oneViewDetails):
    ## Validating the alert type to be logged for sending to upstream monitoring s/w
    #
    inputAlertTypes = oneViewDetails["alert_type"].split(':')
    inputAlertTypes = [x.lower() for x in inputAlertTypes] # User interested alert types
    # config['inputAlertTypes'] = inputAlertTypes

    alertTypes = [a.lower() for a in SUPPORTED_TYPES['alerts']] # List of permissible alerts

    ## All of the alert types entered by user should match with actual alert types.
    ## If there is any mismatch, the same is printed in the log file and program will exit. 
    for alertType in inputAlertTypes:        
        if not alertType in alertTypes:
            err = "Alert type mismatch : " + alertType + ". Kindly review and restart the plugin."
            logging.error(err)
            raise Exception(err)
        elif not alertType:
            err = "Enter interested alert types in config file. Exiting..."
            logging.error(err)
            raise Exception(err)

