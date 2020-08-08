#!/usr/bin/python3
#encoding:utf-8


# Simple MQTT publishing from Ultrasonic distance sensor jsn-sr04t on RPI
#
# Written and (C) 2020 by Lubomir Kamensky <lubomir.kamensky@gmail.com>
# Provided under the terms of the MIT license
#
# Requires:
# - Eclipse Paho for Python - http://www.eclipse.org/paho/clients/python/

import argparse
import logging
import logging.handlers
import time
import paho.mqtt.client as mqtt
import sys
import configparser
import RPi.GPIO as GPIO 
import time
import statistics


GPIO.setmode(GPIO.BCM)                                 #Set GPIO pin numbering 
    
parser = argparse.ArgumentParser(description='Bridge between Ultrasonic distance sensor jsn-sr04t and MQTT')
parser.add_argument('--mqtt-host', default='localhost', help='MQTT server address. \
                     Defaults to "localhost"')
parser.add_argument('--mqtt-port', default='1883', type=int, help='MQTT server port. \
                    Defaults to 1883')
parser.add_argument('--mqtt-topic', default='gardenopenhub', help='Topic prefix to be used for \
                    subscribing/publishing. Defaults to "gardenopenhub/"')
parser.add_argument('--configuration', default='/home/pi/rpi_jsn-sr04t_mqtt/rpi.ini', help='Sensor configuration file. Defaults to "rpi"')
parser.add_argument('--frequency', default='60', help='How often is the source \
                    checked for the changes, in seconds. Only integers. Defaults to 60')
parser.add_argument('--only-changes', default='False', help='When set to True then \
                    only changed values are published')

args=parser.parse_args()

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

topic=args.mqtt_topic
if not topic.endswith("/"):
    topic+="/"
frequency=int(args.frequency)

lastValue = {}

config = configparser.ConfigParser()
config.read(args.configuration)

TRIG = int(config['GpioPins']['trig'])
ECHO = int(config['GpioPins']['echo'])
CALIBRATION = float(config['Calibration']['calibration'])

class Element:
    def __init__(self,row):
        self.topic=row[0]
        self.value=row[1]

    def publish(self):
        try:
            if self.value!=lastValue.get(self.topic,0) or args.only_changes == 'False':
                lastValue[self.topic] = self.value
                fulltopic=topic+self.topic
                logging.info("Publishing " + fulltopic)
                mqc.publish(fulltopic,self.value,qos=0,retain=False)

        except Exception as exc:
            logging.error("Error reading "+self.topic+": %s", exc)

try:
    mqc=mqtt.Client()
    mqc.connect(args.mqtt_host,args.mqtt_port,10)
    mqc.loop_start()

    print("Distance measurement in progress")
    GPIO.setup(TRIG,GPIO.OUT)                          #Set pin as GPIO out
    GPIO.setup(ECHO,GPIO.IN)                           #Set pin as GPIO in

    while True:
        close_time=time.time()+frequency
        reading=[]

        while True:
            if time.time()>close_time:
                data = []
                row = ["distance"]
                row.insert(1,statistics.median(reading))
                data.append(row)
                elements=[]

                for row in data:
                    e=Element(row)
                    elements.append(e)

                for e in elements:
                    e.publish()

                break

            GPIO.output(TRIG, False)                    #Set TRIG as LOW
            print("Waiting For Sensor To Settle")
            time.sleep(2)                               #Delay of 2 seconds

            GPIO.output(TRIG, True)                     #Set TRIG as HIGH
            time.sleep(0.00001)                         #Delay of 0.00001 seconds
            GPIO.output(TRIG, False)                    #Set TRIG as LOW

            while GPIO.input(ECHO)==0:                  #Check if Echo is LOW
                pulse_start = time.time()               #Time of the last  LOW pulse

            while GPIO.input(ECHO)==1:                  #Check whether Echo is HIGH
                pulse_end = time.time()                 #Time of the last HIGH pulse 

            pulse_duration = pulse_end - pulse_start    #pulse duration to a variable

            distance = pulse_duration * 17150           #Calculate distance
            distance = round(distance, 2)               #Round to two decimal points
            

            if distance > 25 and distance < 450:        #Is distance within range
                print("Distance:",round(distance - CALIBRATION,2),"cm")  #Distance with calibration
                reading.append(round(distance - CALIBRATION,2))
            else:
                print("Out Of Range")                   #display out of range


except Exception as e:
    logging.error("Unhandled error [" + str(e) + "]")
    sys.exit(1)
    
