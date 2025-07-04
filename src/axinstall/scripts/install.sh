#!/usr/bin/bash
set -uo pipefail

log() {
    local level="$1"; shift
    local color reset
    case "$level" in
        INFO)  color='\e[36m' ;;
        WARN)  color='\e[33m' ;;
        ERROR) color='\e[31m' ;;
        *)     color='\e[0m'  ;;
    esac
    reset='\e[0m'
    message="[$level] $*"

    # printing to term
    echo -e "${color}${message}${reset}"

    # printing to logfile
    echo "$message" >> "$logfile"
}

run() {
    "$@" | tee -a "$logfile"
    local status=${PIPESTATUS[0]}
    if [ $status -ne 0 ]; then
        log ERROR "Command failed: $*"
        exit $status
    fi
}

logfile="/tmp/axinstall-output.txt"
log INFO "Running reflector to sort for fastest mirrors"
# not using run here because "warn" wont be reached
if ! pkexec reflector --latest 5 --sort rate --save /etc/pacman.d/mirrorlist | tee -a "$logfile"; then
    log WARN "Reflector failed, continuing with default mirrors"
fi

set -e # Now we can exit because now we are moving to critical stuff

log INFO "Initializing pacman keyring"
run pkexec pacman-key --init
run pkexec pacman-key --populate archlinux

log INFO "Starting installation"
run pkexec axinstall-cli config ~/.config/axinstall.json
