# installer_Screen.py

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

import subprocess, os, shutil
import asyncio
from gi.repository import Gtk, GLib, Adw, Vte, Pango
from gettext import gettext as _
from axinstall.utils.command import CommandUtils
from axinstall.classes.axinstall_screen import AxinstallScreen
import time


@Gtk.Template(resource_path="/com/axos-project/axinstall/pages/install_screen.ui")
class InstallScreen(AxinstallScreen, Adw.Bin):
    __gtype_name__ = "InstallScreen"

    log_box = Gtk.Template.Child()

    def __init__(self, window, application, **kwargs):
        super().__init__(**kwargs)
        self.window = window

        # Vte instance
        self.vte_instance = Vte.Terminal()
        self.vte_instance.set_cursor_blink_mode(Vte.CursorBlinkMode.ON)
        self.vte_instance.set_mouse_autohide(True)
        self.vte_instance.set_font(Pango.FontDescription("Monospace 12"))
        self.log_box.append(self.vte_instance)
        self.vte_instance.connect("child-exited", self.on_vte_child_exited)

        self.set_valid(False)

    def on_show(self):
        prefs = self.window.summary_screen.installprefs.generate_json()
        with open(os.getenv("HOME") + "/.config/axinstall.json", "w") as f:
            f.write(prefs)

        prefs = self.window.summary_screen.installprefs.generate_json()

        try:
            self.vte_instance.spawn_async(
            Vte.PtyFlags.DEFAULT,
            ".",  # working directory
            ["bash", "/usr/share/axinstall/axinstall/scripts/install.sh"],
            [],  # environment
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            None,
            )
        except Exception as e:
            print(f"Installation failed: {str(e)}")
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Installation failed: {str(e)}"
            )
            dialog.connect("response", lambda dialog, response: dialog.destroy())
            dialog.show()
            
    def on_vte_child_exited(self, terminal, exit_status):
        if exit_status != 0:
            print(f"Installation failed with exit status {exit_status}")
            dialog = Gtk.MessageDialog(
                transient_for=self.window,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Installation failed with exit status {exit_status}"
            )
            dialog.connect("response", lambda dialog, response: dialog.destroy())
            dialog.show()
        else:
            self.set_valid(True)