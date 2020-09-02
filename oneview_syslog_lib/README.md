# Oneview syslog library
This is a HPE oneview syslog generator. This repo will help getting the hpe oneview alerts into a syslog. This is a python based solution uses HPE OneView APIs ( REST and Message queues ( SCMB ) ) to get the alerts and stats, converts into syslog. This syslog can be forwarded and consumed by log readable monitoring solutions like splunk, prometheus, etc.,

The library is config driver, allows user to filter the alerts based on severity and hardware resources.

Primarily, this library generates syslog for
1. Events generated from oneview
2. Interconnect statistics (Port transmit/Receive/Speed/Model)
3. Enclosure statistics (Temperature/Power)
4. Server statistics (Temperature/Power/CPU frequence/CPU utilization)
5. Remote support ticket information

This library generates the syslog in standard RFC 5424 format. 

### deploying on kubernetes cluster

### How to build container images for oneview syslog lib and gok-exporter
Rub following docker command
```
docker build -t <org>/<name>:<tag> .
cd to grok_exporter
  
docker build -t <org name>/grok-exporter .
```

Then make sure you have created pk8s pv and pvc that are common directory. After then you can deployment the service.

### How to deploy as helm chart
edit the config map, secrets yaml file  ( look for the host directory mounth path, create a directory for the logs )
and then rub below command
```
helm install helm/oneview-syslog-lib
```

### How to test
When you the helm install, it should start a prod and a sevice running at 9144 port
This pod has two containers. One container ( oneview-syslog-lib ) writes the log to a volume and other
container ( grok-exporter) reads the logs from the same volume. You can see the pod  spec to know the volume
mount points

once pod is running, you can tail the log file 'oneview_syslog (it will be located under the directory you have configured in pv)



## Read below instructions if you deploy as docker or normal python process

### Getting Started

Prerequisites - 

```
OS: 
	Centos 7.3  ( basic testing was on done RHEL 7.5 and it works )
Packages: 
	python 3.6 ( not tested on Python 2.7.x )
	pip3 (to install the following modules (including HPE oneview python module)
		amqplib==1.0.2
		future==0.17.0
		requests==2.10.0
		setuptools==39.0.1
		six==1.12.0
		hponeview==4.8.0 (https://github.com/HewlettPackard/python-hpOneView)

external dependencies:
	oneview instance
		
```

Download the source and install the python dependencies:
```
1. Clone the project folder to suitable location and navigate to it. You can use the following command to clone
	$ git clone https://github.hpe.com/GSE/oneview-syslog-lib.git

2. Run the following command to install the required python modules.
	$ cd oneview-syslog-lib
	$ pip3 install -r requirements.txt
```

## Deployment
### Configuration
Input configuration for the connector can be given either through the input file or using environment variables

1. Edit the input config file with required oneview details in config.json

2. Specifying oneview ip, username and password(in base64) is mandatory.

3. Optionally you can edit the options to control and allow listening on particular alert severity or listen for particular resources.
   For example, you can set below field to allow only Critical alerts
   
   "alert_type": "Critical"
   
   Similarly you can set below field to allow only alerts coming from server-hardware
   
   "alert_hardware_category": "server-hardware"

4. If environmental variables are used, the list of supported variables:

   | Variable                 | Description                                     | Type |
   | -----------              | -----------                                     | ------ |
   | OV_HOSTNAME              | Oneview IP address/hostname                     | Mandatory |
   | OV_USERNAME              | Oneview username                                | Mandatory |
   | OV_PASSWORD              | Oneview Password                                | Mandatory |
   | OV_ALIAS_NAME            | Alias name for Oneview                          | Optional: Oneview-OV_HOSTNAME |
   | OV_AUTH_LOGIN_DOMAIN     | Oneview Authentication Domain                   | Optional: LOCAL |
   | OV_SCMB_ROUTE            | Oneview SCMB route to listen                    | Optional: 'scmb.alerts.#' |
   | OV_ALERT_TYPE            | Oneview alert types to capture                  | Optional: "Critical:Warning:Ok" |
   | OV_RESOURCE_CATEGORY     | Oneview resources to listen                     | Optional: "server-hardware:enclosures:interconnects:logical-interconnects:sas-interconnects" |
   | OV_REFRESH_INTERVAL      | Polling interval to capture statistics          | Optional: 600 |
   | OV_LOGGING_LEVEL         | Logging level for the library                   | Optional: "WARNING" |
   | OV_SYSLOG_FILEPATH       | Logging folder to capture the syslog            | Optional: "logs" |
   | OV_SYSLOG_FILE           | Name of the syslog file                         | Optional: "oneview_syslog" |
   | OV_COLLECT_STATS         | Boolean to enable/disable statistics collection | Optional: "true" |
   | OV_COLLECT_HPEOV_SERVICE | Boolean to enable HPE Remote support details    | Optional: "false" |



#### To run as a docker container
Follow [install docker](https://docs.docker.com/install/linux/docker-ee/centos/) to setup docker engine.

```
1. Edit ***docker_env*** files according to your environment.

2. Build docker images for oneview syslog lib and grok exporter

        If you are behind proxy server

        $ sudo docker build --build-arg http_proxy=http://<proxy_server>:<port> -t oneview-syslog-lib .

        Else

        $ sudo docker build -t <org name>/oneview-syslog-lib .
        cd to grok_exporter
        
        $ sudo docker build -t <org name>/grok-exporter .

3. Start docker container

        $ sudo docker run -d -v $PWD:/plugin -v $PWD/config.json:/conf/config.json --env-file docker_env --name ov_connector oneview-syslog-lib

        At the start of this container plugin, password for oneview is prompted. Once you enter password, script will
        run continuously and listen for oneview alerts and converts alerts message into syslog message
        and writes to a file `logs/oneview_syslog`

```

#### To run as standalone script

Execute as follows:

```
$ <Project_Home>python3.6 main.py -i config.json
```

Eg: $ /home/user1/oneview-syslog-lib python3.6 main.py -i config.json

Above command will continuously:
- listen for oneview alerts and converts alerts message into syslog message
- periodically poll for power and temperature stats of servers and enclosures along with port statistics

These alerts are statistics are written to a default syslog file (Default: `logs/oneview_syslog`)

### Note
Configure oneview to allow local user login if you are logging to oneview as local user.

### How to test
  - Generate alerts from oneview and ensure that the alerts are captured by the script. 
  - Verify the `logs/oneview_syslog`

### Troubleshoot
Monitor the log folder using tail command. 
```
tail -f <LOG_FILE>

Eg: $ tail -f logs/oneview_syslog

```

### TODO list
- co-relation
- bi-directional

### out of scope
TBD
