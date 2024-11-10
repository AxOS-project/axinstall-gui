#!/usr/bin/bash
lsblk -pdbo MODEL $1 | grep -v MODEL