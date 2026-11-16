# wifi.py

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


@Gtk.Template(resource_path="/com/axos-project/axinstall/widgets/wifi.ui")
class WifiEntry(Adw.ActionRow):
    __gtype_name__ = "WifiEntry"

    signal_icon = Gtk.Template.Child()
    connecting_spinner = Gtk.Template.Child()
    lock_icon = Gtk.Template.Child()
    status_icon = Gtk.Template.Child()
    disconnect_button = Gtk.Template.Child()

    def __init__(
        self,
        window,
        page,
        ssid: str,
        security: str,
        signal: int,
        in_use: bool,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.window = window
        self.page = page
        self.ssid = ssid
        self.security = security if security and security != "--" else ""
        self.signal = signal
        self.in_use = in_use
        self.is_secured = bool(self.security)
        self.is_enterprise = "802.1X" in self.security.upper()

        self.set_title(self.ssid)

        security_label = self.security if self.is_secured else _("Open")
        if self.in_use:
            self.set_subtitle(f"{_('Connected')} • {security_label} ({self.signal}%)")
        else:
            self.set_subtitle(f"{security_label} • {self.signal}%")

        self.signal_icon.set_from_icon_name(self._get_signal_icon(self.signal))
        self.lock_icon.set_visible(self.is_secured)
        self.status_icon.set_visible(self.in_use)
        self.disconnect_button.set_visible(self.in_use)

        self.connect("activated", self._on_activated)
        self.disconnect_button.connect("clicked", self._on_disconnect_clicked)

    @staticmethod
    def _get_signal_icon(signal: int) -> str:
        if signal >= 80:
            return "network-wireless-signal-excellent-symbolic"
        elif signal >= 60:
            return "network-wireless-signal-good-symbolic"
        elif signal >= 40:
            return "network-wireless-signal-ok-symbolic"
        elif signal >= 20:
            return "network-wireless-signal-weak-symbolic"
        return "network-wireless-signal-none-symbolic"

    def set_connecting(self, connecting: bool):
        self.connecting_spinner.set_visible(connecting)
        if connecting:
            self.connecting_spinner.start()
            self.set_subtitle(_("Connecting..."))
        else:
            self.connecting_spinner.stop()

    def _on_activated(self, *_):
        if not self.in_use:
            self.page.on_wifi_selected(self)

    def _on_disconnect_clicked(self, *_):
        self.page.on_wifi_disconnect(self)
