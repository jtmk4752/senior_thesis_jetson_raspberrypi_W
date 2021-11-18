#!/bin/bash

raspivid -t 0 -w 1024 -h 768 -fps 5 -b 2000000 -awb auto -n -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! tcpserversink host=0.0.0.0 port=8554
#raspivid -t 0 -w 1024 -h 768 -fps 5 -b 2000000 -awb auto -n -o - | gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! gdppay ! udpsink host=192.168.200.1 port=8554
