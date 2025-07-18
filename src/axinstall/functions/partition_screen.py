# partition_screen.py

#
# Copyright 2025 Ardox

#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess, shutil
from gi.repository import Gtk, Adw
from gettext import gettext as _
from axinstall.utils import disks
from axinstall.utils.command import CommandUtils
from axinstall.widgets.partition import PartitionEntry
from axinstall.classes.partition import Partition
from axinstall.classes.axinstall_screen import AxinstallScreen


@Gtk.Template(resource_path="/com/axos-project/axinstall/pages/partition_screen.ui")
class PartitionScreen(AxinstallScreen, Adw.Bin):
    __gtype_name__ = "PartitionScreen"

    disk_list = Gtk.Template.Child()
    open_bash = Gtk.Template.Child()
    open_gparted = Gtk.Template.Child()
    partition_list = Gtk.Template.Child()
    reload_partitions = Gtk.Template.Child()
    manual_partitioning = Gtk.Template.Child()
    automatic_partitioning = Gtk.Template.Child()
    manual_partitioning_page = Gtk.Template.Child()
    automatic_partitioning_page = Gtk.Template.Child()

    selected_partition = None
    move_to_summary = False

    def __init__(self, window, application, **kwargs):
        super().__init__(**kwargs)
        self.window = window
        self.disk_list.connect("row_selected", self.row_selected)
        self.manual_partitioning.connect("clicked", self.switch_manual_partitioning)
        self.reload_partitions.connect("clicked", self.check_partitions)
        self.automatic_partitioning.connect(
            "clicked", self.switch_automatic_partitioning
        )
        self.open_bash.connect("clicked", self.bash)
        self.open_gparted.connect("clicked", self.gparted)

    def gparted(self, widget):
        CommandUtils.run_command(["sudo", "-E", "gparted"])

    def bash(self, widget):
        CommandUtils.run_command(["kgx", "-e", "/usr/bin/bash"])

    def check_partitions(self, widget):
        self.partition_list.select_all()
        print(self.partition_list.get_row_at_index(2))
        for i in range(0, len(self.window.available_partitions)):
            self.partition_list.remove(self.partition_list.get_row_at_index(0))
        self.available_partitions = disks.get_partitions()
        self.window.available_partitions = self.available_partitions
        for partition in self.available_partitions:
            self.partition_list.append(
                PartitionEntry(
                    window=self,
                    partition=Partition(
                        partition=partition,
                        mountpoint="",
                        filesystem="",
                        size=disks.get_disk_size(partition),
                    ),
                    application=None,
                )
            )

    def switch_automatic_partitioning(self, widget):
        self.automatic_partitioning_page.set_visible(True)
        self.manual_partitioning_page.set_visible(False)
        self.set_valid(False)
        self.window.partition_mode = "Auto"

    def switch_manual_partitioning(self, widget):
        self.automatic_partitioning_page.set_visible(False)
        self.manual_partitioning_page.set_visible(True)
        self.set_valid(True)
        self.window.partition_mode = "Manual"

    def row_selected(self, widget, row):
        if row is not None:
            print(row.get_title())
            row.select_button.set_active(True)
            self.selected_partition = row

            self.set_valid(True)
        else:
            print("ERROR: invalid row slected")
