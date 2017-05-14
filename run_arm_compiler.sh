#!/bin/bash
set -e

docker run --rm -it -v $(pwd):${1:-/home/robot/wifi-mapper} -w ${1:-/home/robot/wifi-mapper} ev3dev/debian-jessie-cross
