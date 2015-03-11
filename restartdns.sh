#!/bin/bash

pkill -9 dnsmasq
nohup dnsmasq -d -C /etc/dnsmasq.conf &
