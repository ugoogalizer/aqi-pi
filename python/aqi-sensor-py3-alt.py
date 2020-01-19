#!/usr/bin/python
# -*- coding=utf-8 -*-
# "DATASHEET": http://cl.ly/ekot
# https://pypi.org/project/sds011/
# https://github.com/menschel/sds011
#from sds011 import SDS011
from sds011 import sds011
import time, json
import logging
import os
from os.path import exists
from datetime import datetime
from dateutil.tz import tzlocal

sleep_sec = 60 #frequency of measurements (60sec = 1 minute)
read_sec = 15 # how many seconds to read for
data_limit = 10000 # how many measurements to maintain in json

baudrate = 9600

# pi zero w
port = "/dev/ttyUSB0"
json_path='/var/www/html/aqi.json'
csv_path ='/var/www/html/aqi.csv'

# win debug
#port = "COM7"
#json_path = '..\\html\\aqi.json'
#csv_path = "..\\html\\aqi.csv"


def initiate_json(file_path):
    """
    Check to see if the aqi.json exists in the html directory and add it if not
    """
    if not exists(file_path):
        with open(file_path,"w") as fresh_file:
            fresh_file.write('[]')

if __name__ == '__main__':

    #sensor = SDS011(port,baudrate=baudrate,use_query_mode=True)
    #sensor.sleep()
    print("Connecting to SDS011 and printing some stats:")
    sds = SDS011(port=port)
    print("Stats:")
    print(sds)
    sds.sleep()
        
    firmware = sds.get_firmware_version()
    print("Firmware ver: ", firmware)

    #Set the working period: 
    sds.set_working_period(rate=5)
    

    #initiate_json()
    initiate_json(json_path)
    
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        filename='aqi.log', level=logging.DEBUG)
    logging.info('AQI Monitor has been started!')

    # how many failed readings can we tolerate
    failure_tolerance = 3

    loop_forever = True
    
    try:
        while loop_forever:
            logging.info('collection is starting')
            #firmwareVer = sensor.get_firmware_version()
            #print("Firmware version:", firmwareVer)
            failures = 0

            # turn on diode and fans, get a reading
            #sensor.sleep(sleep=False)
            sds.wakeup()
            print("reading for %s seconds" % read_sec)
            time.sleep(read_sec)
            #values = sensor.query()
            values = sds.read_measurement()

            # create timestamp
            aqi_tsp = datetime.now(tzlocal()).isoformat()               

            if values is not None and len(values)>0:
                print(aqi_tsp,", PM2.5: ", values[0], ", PM10: ", values[1])
                logging.debug("values: PM2.5: {0}, PM10: {1}".format(values[0], values[1]))
                # time.sleep(2)
                # reset failures
                failures = 0
    
                # open stored data
                logging.debug('Opening aqi.json')
                with open(json_path) as json_data:
                    data = json.load(json_data)

                # csv
                logging.debug('Opening aqi.csv')
                csv_file = open(csv_path, 'a')
                csv_file.write("{0},{1},{2}\n".format(values[0],values[1],aqi_tsp))
                csv_file.close()
                logging.debug('Closed aqi.csv')

                # check if length is more than data_limit and delete first element
                if len(data) > data_limit:
                    data.pop(0)

                # append new values
                newdata = { 'time': aqi_tsp} 
                if len(values)>0:
                    newdata['pm25'] = values[0]
                    newdata['pm10'] = values[1]
                    # only append if we have new values
                    data.append(newdata)

                # save it
                with open(json_path, 'w') as outfile:
                    json.dump(data, outfile)
            else:
                print("no reading, will retry")
              
                failures +=1 # update failure count
                if failures > failure_tolerance:
                    print("too many failures")
                    break

            print("Going to sleep for %s seconds..." % str(sleep_sec - read_sec))
            logging.info('sleeping for %s seconds' % str(sleep_sec - read_sec))

            #sensor.sleep() # turn off fan and diode
            sds.sleep()
            time.sleep(sleep_sec - read_sec)

    except KeyboardInterrupt:
        loop_forever = False
        pass
    finally:
        print("turning off sensor, saving data")
        #sensor.sleep()
        sds.sleep()
        # save json
        with open(json_path, 'w') as outfile:
            json.dump(data, outfile)
        