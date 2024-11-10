#!/usr/bin/bash
lsblk -pdo name | grep -v zram | grep -v NAME | grep -v loop | grep -v sr