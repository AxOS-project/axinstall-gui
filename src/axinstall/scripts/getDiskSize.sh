#!/usr/bin/bash
lsblk -pdbo SIZE $1 | grep -v SIZE