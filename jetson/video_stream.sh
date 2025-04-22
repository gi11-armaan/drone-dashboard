#!/bin/bash
mjpg_streamer -i "input_uvc.so -r 640x480 -f 30" -o "output_http.so -w ./www -p 8080"
