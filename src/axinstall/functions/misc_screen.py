# misc_screen.py

#
# Copyright 2025 Ardox

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

from gi.repository import Gtk, Adw
from gettext import gettext as _

from psutil import swap_memory
from regex import F, T
from axinstall.classes.axinstall_screen import AxinstallScreen


@Gtk.Template(resource_path="/com/axos-project/axinstall/pages/misc_screen.ui")
class MiscScreen(AxinstallScreen, Adw.Bin):
    __gtype_name__ = "MiscScreen"

    hostname_entry = Gtk.Template.Child()
    #ipv_switch = Gtk.Template.Child()
    #timeshift_switch = Gtk.Template.Child()
    #zramd_switch = Gtk.Template.Child()
    swap_entry = Gtk.Template.Child()
    nvidia_switch = Gtk.Template.Child()
    artist_uk_switch = Gtk.Template.Child()
    devel_uk_switch = Gtk.Template.Child()
    hacker_uk_switch = Gtk.Template.Child()
    office_uk_switch = Gtk.Template.Child()
    entertainment_uk_switch = Gtk.Template.Child()

    hostname = "axos"
    swap_value = 0
    move_to_summary = False
    nvidia_enabled = False
    artist_uk_enabled = False
    devel_uk_enabled = False
    hacker_uk_enabled = False
    office_uk_enabled = False
    entertainment_uk_enabled = False

    def __init__(self, window, application, **kwargs):
        super().__init__(**kwargs)
        self.window = window

        self.set_valid(True)

    def on_complete(self, *_):
        self.hostname = self.hostname_entry.get_text()      
        self.swap_value = self.swap_entry.get_text()
        self.swap_entry.connect("changed", self.check_swap_value)
        self.nvidia_enabled = self.nvidia_switch.get_state()
        self.artist_uk_enabled = self.artist_uk_switch.get_state()
        self.devel_uk_enabled = self.devel_uk_switch.get_state()
        self.hacker_uk_enabled = self.hacker_uk_switch.get_state()
        self.office_uk_enabled = self.office_uk_switch.get_state()
        self.entertainment_uk_enabled = self.entertainment_uk_switch.get_state()
        
    def check_swap_value(self):
        input = self.swap_entry.get_text()
        if not input:
            self.swap_value = "0"
            self.swap_filled = True
            self.swap_entry.remove_css_class("error")
        else:            
            if not input.isdigit() or int(input) < 8000:
                print("Bad entry: must be a INT and < 8G")
                self.swap_entry.add_css_class("error")
                self.swap_filled = False
            else:
                print("Valid entry")
                self.swap_entry.remove_css_class("error")
                self.swap_filled = True
                self.swap_value = input