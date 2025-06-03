# install_prefs.py
#
# Copyright 2022
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-only

from axinstall.utils import disks
import json


class InstallPrefs:
    def __init__(
        self,
        timezone,
        locale,
        layout,
        variant,
        username,
        password,
        enable_sudo,
        disk,
        hostname,
        nvidia_enabled,
        artist_uk_enabled,
        devel_uk_enabled,
        hacker_uk_enabled,
        office_uk_enabled,
        entertainment_uk_enabled,
        desktop,
        kernel,
        partition_mode,
        partitions,
    ):
        self.timezone = timezone
        self.locale = locale
        self.layout = layout
        self.variant = variant
        self.username = username
        self.password = password
        self.enable_sudo = enable_sudo
        if partition_mode.lower() != "manual":
            self.disk = disk.disk
        else:
            self.disk = ""
        self.hostname = hostname if len(hostname) != 0 else "axos"
        self.nvidia_enabled = nvidia_enabled
        self.artist_uk_enabled = artist_uk_enabled
        self.devel_uk_enabled = devel_uk_enabled
        self.hacker_uk_enabled = hacker_uk_enabled
        self.office_uk_enabled = office_uk_enabled
        self.entertainment_uk_enabled = entertainment_uk_enabled
        self.desktop = desktop
        self.kernel = kernel
        self.partition_mode = partition_mode
        self.partitions = partitions
        self.is_efi = disks.get_uefi()
        self.bootloader_type = "grub-efi" if self.is_efi else "grub-legacy"
        self.bootloader_location = "/boot/efi/" if self.is_efi else self.disk

    def generate_json(self):
        prefs = {
            "partition": {
                "device": self.disk,
                "mode": self.partition_mode,
                "efi": self.is_efi,
                "partitions": self.partitions,
            },
            "bootloader": {
                "type": self.bootloader_type,
                "location": self.bootloader_location,
            },
            "locale": {
                "locale": self.locale,
                "keymap": self.layout.country_shorthand,
                "timezone": self.timezone.region + "/" + self.timezone.location,
            },
            "networking": {"hostname": self.hostname, "ipv6": False},
            "users": [
                {
                    "name": self.username,
                    "password": self.password,
                    "hasroot": self.enable_sudo,
                    "shell": "bash",
                }
            ],
            "rootpass": self.password,
            "desktop": self.desktop.lower(),
            "kernel": self.kernel.lower(),
            "extra_packages": [],
            "nvidia": self.nvidia_enabled,
            "artist_uk": self.artist_uk_enabled,
            "devel_uk": self.devel_uk_enabled,
            "hacker_uk": self.hacker_uk_enabled,
            "office_uk": self.office_uk_enabled,
            "entertainment_uk": self.entertainment_uk_enabled,
        }
        return json.dumps(prefs)
