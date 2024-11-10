#!/usr/bin/bash
lsblk -d -o rota $1 | grep -v ROTA