# rpi_jsn-sr04t_mqtt
Simple MQTT publishing from Ultrasonic distance sensor jsn-sr04t on RPI. (C) 2020 Lubomir Kamensky lubomir.kamensky@gmail.com

Dependencies
------------
* Eclipse Paho for Python - http://www.eclipse.org/paho/clients/python/

Example use
-----------
python3 rpi_jsn-sr04t_mqtt.py

Example use pm2 usage
---------------------
pm2 start /usr/bin/python3 --name "rpi_jsn-sr04t_mqtt" -- /home/pi/rpi_jsn-sr04t_mqtt/rpi_jsn-sr04t_mqtt.py --configuration studna.ini

pm2 save
