#!/bin/bash
set -e

docker run --rm -it -v $(pwd):${1:-/home/robot/wifi-slam-robot} -w ${1:-/home/robot/wifi-slam-robot} ev3dev/debian-jessie-cross
