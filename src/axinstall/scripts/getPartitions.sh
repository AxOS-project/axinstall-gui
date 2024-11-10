#!/usr/bin/bash
blkid -o device | grep -v zram | grep -v loop | grep -v sr