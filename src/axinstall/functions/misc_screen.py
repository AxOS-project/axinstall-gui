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

from regex import F
from axinstall.classes.axinstall_screen import AxinstallScreen


@Gtk.Template(resource_path="/com/axos-project/axinstall/pages/misc_screen.ui")
class MiscScreen(AxinstallScreen, Adw.Bin):
    __gtype_name__ = "MiscScreen"

    hostname_entry = Gtk.Template.Child()
    #ipv_switch = Gtk.Template.Child()
    #timeshift_switch = Gtk.Template.Child()
    #zramd_switch = Gtk.Template.Child()
    nvidia_switch = Gtk.Template.Child()
    artist_uk_switch = Gtk.Template.Child()
    devel_uk_switch = Gtk.Template.Child()
    hacker_uk_switch = Gtk.Template.Child()

    hostname = "axos"
    #ipv_enabled = False
    #zramd_enabled = False
    #timeshift_enabled = False
    move_to_summary = False
    nvidia_enabled = False
    artist_uk_enabled = False
    devel_uk_enabled = False
    hacker_uk_enabled = False

    def __init__(self, window, application, **kwargs):
        super().__init__(**kwargs)
        self.window = window

        self.set_valid(True)

    def on_complete(self, *_):
        self.hostname = self.hostname_entry.get_text()
        #self.ipv_enabled = self.ipv_switch.get_state()
        #self.zramd_enabled = self.zramd_switch.get_state()
        #self.timeshift_enabled = self.timeshift_switch.get_state()
        self.nvidia_enabled = self.nvidia_switch.get_state()
        self.artist_uk_enabled = self.artist_uk_switch.get_state()
        self.devel_uk_enabled = self.devel_uk_switch.get_state()
        self.hacker_uk_enabled = self.hacker_uk_switch.get_state()