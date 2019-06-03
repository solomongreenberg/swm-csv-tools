#!/usr/bin/env python3

import glob
import string
from datetime import datetime
import os, sys
import json

def usage():
    print("Usage: ./parse.py in_dir out_dir")
    sys.exit(0)

if len(sys.argv) != 3:
    usage()
if not os.path.exists(sys.argv[1]):
    usage()
if not os.path.exists(sys.argv[2]):
    os.mkdir(sys.argv[2])

folder_in = sys.argv[1]
folder_out = sys.argv[2]

files = glob.glob(os.path.join(folder_in, '*.csv'))


csvs = {}
for i in files:
    with open(i, 'r') as f:
        csvs[i.split('/')[-1].split('.csv')[0]] = ''.join([i for i in filter(lambda x: x in set(string.printable), f.read())])

files = list(csvs.keys())

data = {}

for src in files:
    content = csvs[src]
    header, body = content.split('\n')[0], content.split('\n')[1:-1]
    dataSources = [i.replace('\"','') for i in header.split(',')[1:]]
    numDataSources = len(dataSources)
    time = [int(x) for x in (lambda x: [(i-x[0]).total_seconds() for i in x])([datetime.strptime(j.replace('\"',''), '%Y-%m-%d %H:%M:%S') for j in [i.split(',')[0] for i in body]])]

    for t_idx in range(len(time)):
        for s_idx in range(numDataSources):
            if not (dataSources[s_idx] in data.keys() and type(data[dataSources[s_idx]]) is dict):
                data[dataSources[s_idx]] = {'data': {}, 'startTime': [j.replace('\"','') for j in [i.split(',')[0] for i in body]][0]}
            try:
                data[dataSources[s_idx]]['data'][time[t_idx]] = float(body[t_idx].split(',')[1:][s_idx])
            except Exception as e:
                if type(e) != ValueError and type(e) != IndexError:
                    raise e


sensors = list(data.keys())

for sensorName in sensors:
    filename = sensorName + '.json'
    #startTime = data[sensorName]['startTime']
    #times = sorted(data[sensorName]['data'].keys())
    #temperatures = [data[sensorName]['data'][t] for t in times]
    #csv = ""
    #csv += "Sensor: {}\nT=0: {}\n".format(sensorName, startTime)
    #csv += "total_seconds,temperature\n"
    #for time,temp in zip(times,temperatures):
    #    csv += "{},{}\n".format(time,temp)

    with open(os.path.join(folder_out,filename), 'w') as f:
        json.dump(data[sensorName], f)
