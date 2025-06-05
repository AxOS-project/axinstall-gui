#!/usr/bin/bash
set -uo pipefail

logfile="/tmp/axinstall-output.txt"
echo "Running reflector to sort for fastest mirrors" | tee -a "$logfile"
if ! pkexec reflector --latest 5 --sort rate --save /etc/pacman.d/mirrorlist | tee -a "$logfile"; then
    echo "Warning: Reflector failed, continuing with default mirrors" | tee -a "$logfile"
fi

set -e # Now we can exit because now we are moving to critical stuff

echo "Initializing pacman keyring" | tee -a "$logfile"
pkexec pacman-key --init | tee -a "$logfile"
pkexec pacman-key --populate archlinux | tee -a "$logfile"

echo "Starting installation" | tee -a "$logfile"
pkexec axinstall-cli config ~/.config/axinstall.json | tee -a "$logfile"
