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

from axinstall.classes.axinstall_screen import AxinstallScreen


@Gtk.Template(resource_path="/com/axos-project/axinstall/pages/misc_screen.ui")
class MiscScreen(AxinstallScreen, Adw.Bin):
    __gtype_name__ = "MiscScreen"

    hostname_entry = Gtk.Template.Child()
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
    swap_filled = True

    MIN_SWAP_MB = 256
    MAX_SWAP_MB = 32768

    def __init__(self, window, application, **kwargs):
        super().__init__(**kwargs)
        self.window = window

        self.set_valid(True)

        self.swap_entry.connect("insert-text", self.on_swap_insert_text)
        self.swap_entry.connect("changed", self.on_swap_changed)

    def on_swap_insert_text(self, entry, text, length, position):
        if not text.isdigit():
            entry.stop_emission("insert-text")

    def on_swap_changed(self, entry):
        text = entry.get_text()

        if text == "":
            # Empty means swap = 0 (valid)
            entry.remove_css_class("error")
            self.swap_filled = True
            self.swap_value = 0
        elif text.isdigit():
            value = int(text)
            if self.MIN_SWAP_MB <= value <= self.MAX_SWAP_MB:
                entry.remove_css_class("error")
                self.swap_filled = True
                self.swap_value = value
            else:
                entry.add_css_class("error")
                self.swap_filled = False
        else:
            entry.add_css_class("error")
            self.swap_filled = False

        self.verify_continue()

    def on_complete(self, *_):
        self.hostname = self.hostname_entry.get_text()
        self.nvidia_enabled = self.nvidia_switch.get_state()
        self.artist_uk_enabled = self.artist_uk_switch.get_state()
        self.devel_uk_enabled = self.devel_uk_switch.get_state()
        self.hacker_uk_enabled = self.hacker_uk_switch.get_state()
        self.office_uk_enabled = self.office_uk_switch.get_state()
        self.entertainment_uk_enabled = self.entertainment_uk_switch.get_state()

    def verify_continue(self):
        self.set_valid(self.swap_filled)
