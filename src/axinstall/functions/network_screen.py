# network_screen.py

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

import re
import subprocess
import urllib.request
from gettext import gettext as _
from gi.repository import Gtk, GLib, Adw

from axinstall.classes.axinstall_screen import AxinstallScreen
from axinstall.widgets.wifi import WifiEntry
from axinstall.utils.threading import RunAsync


@Gtk.Template(resource_path="/com/axos-project/axinstall/pages/network/network_screen.ui")
class NetworkScreen(AxinstallScreen, Adw.Bin):
    __gtype_name__ = "NetworkScreen"

    status_page = Gtk.Template.Child()
    ethernet_group = Gtk.Template.Child()
    ethernet_row = Gtk.Template.Child()
    ethernet_icon = Gtk.Template.Child()
    ethernet_spinner = Gtk.Template.Child()
    ethernet_status_icon = Gtk.Template.Child()

    wifi_group = Gtk.Template.Child()
    scan_spinner = Gtk.Template.Child()
    hidden_wifi_button = Gtk.Template.Child()
    refresh_button = Gtk.Template.Child()
    wifi_switch = Gtk.Template.Child()
    wifi_list = Gtk.Template.Child()

    def __init__(self, window, set_valid, application, **kwargs):
        super().__init__(set_valid=set_valid, **kwargs)
        self.window = window
        self.application = application

        self._is_refreshing = False
        self._is_connecting = False
        self._updating_switch = False
        self._timezone_requested = False
        self._selected_wifi_row = None
        self._is_hidden_mode = False
        self._eth_disconnected_dev = None

        # Setup Connect Dialog
        builder = Gtk.Builder.new_from_resource(
            "/com/axos-project/axinstall/pages/network/network_dialog.ui"
        )
        self.connect_dialog = builder.get_object("connect_dialog")
        self.connect_dialog.set_transient_for(self.window)
        self.connect_dialog.set_modal(True)

        self.dialog_group = builder.get_object("dialog_group")
        self.ssid_entry = builder.get_object("ssid_entry")
        self.identity_entry = builder.get_object("identity_entry")
        self.password_entry = builder.get_object("password_entry")
        self.error_label = builder.get_object("error_label")
        self.dialog_spinner = builder.get_object("dialog_spinner")
        self.cancel_button = builder.get_object("cancel_button")
        self.connect_button = builder.get_object("connect_button")

        # Connect signals
        self.refresh_button.connect("clicked", self._on_refresh_clicked)
        self.hidden_wifi_button.connect("clicked", self._on_hidden_wifi_clicked)
        self.wifi_switch.connect("state-set", self._on_wifi_switch_toggled)
        self.ethernet_row.connect("activated", self._on_ethernet_row_activated)

        self.cancel_button.connect("clicked", lambda *_: self.connect_dialog.hide())
        self.connect_button.connect("clicked", self._on_dialog_connect_clicked)
        self.password_entry.connect("entry-activated", self._on_dialog_connect_clicked)
        self.ssid_entry.connect("entry-activated", self._on_dialog_connect_clicked)
        self.identity_entry.connect("entry-activated", self._on_dialog_connect_clicked)

        # Initial background scan so data is ready when user reaches the 2nd tab
        self.refresh_network(force_rescan=False)

    def on_show(self):
        self.refresh_network(force_rescan=False)
        GLib.timeout_add_seconds(5, self._periodic_refresh)

    def _periodic_refresh(self):
        if getattr(self.window, "current_page", None) != self:
            return False
        if not self._is_refreshing and not self._is_connecting and not self.connect_dialog.get_visible():
            self.refresh_network(force_rescan=False)
        return True

    @staticmethod
    def _split_nmcli_line(line: str) -> list:
        parts = re.split(r"(?<!\\):", line)
        return [p.replace(r"\:", ":").replace(r"\\", "\\") for p in parts]

    @staticmethod
    def _run_nmcli(args: list, timeout: int = 15) -> tuple:
        cmd = ["nmcli"] + args
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
        except Exception as e:
            return 1, "", str(e)

    @staticmethod
    def _check_internet_connection() -> bool:
        rc, out, _err = NetworkScreen._run_nmcli(
            ["-t", "-f", "CONNECTIVITY", "general", "status"], timeout=3
        )
        if rc == 0 and out.strip() == "full":
            return True
        try:
            urllib.request.urlopen("https://ping.archlinux.org", timeout=2)
            return True
        except Exception:
            return False

    def _on_refresh_clicked(self, *_args):
        self.refresh_network(force_rescan=True)

    def refresh_network(self, force_rescan: bool = False):
        if self._is_refreshing:
            return
        self._is_refreshing = True
        self.scan_spinner.set_visible(True)
        self.scan_spinner.start()
        self.refresh_button.set_sensitive(False)

        def task():
            # 1. Query device statuses
            rc_dev, out_dev, _err = self._run_nmcli(
                ["-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"]
            )
            eth_devices = []
            wifi_devices = []
            if rc_dev == 0 and out_dev:
                for line in out_dev.splitlines():
                    parts = self._split_nmcli_line(line)
                    if len(parts) >= 4:
                        dev, dev_type, state, conn = parts[0], parts[1], parts[2], parts[3]
                        if dev_type == "ethernet":
                            eth_devices.append((dev, state, conn))
                        elif dev_type == "wifi":
                            wifi_devices.append((dev, state, conn))

            # 2. Query Wi-Fi radio state
            rc_radio, out_radio, _err = self._run_nmcli(["radio", "wifi"])
            wifi_enabled = rc_radio == 0 and out_radio.strip().lower() == "enabled"

            # 3. Query Wi-Fi networks if Wi-Fi adapter exists and radio is enabled
            networks = []
            if wifi_devices and wifi_enabled:
                rescan_arg = "yes" if force_rescan else "no"
                rc_wifi, out_wifi, _err = self._run_nmcli(
                    [
                        "-t",
                        "-f",
                        "IN-USE,SSID,SECURITY,SIGNAL",
                        "device",
                        "wifi",
                        "list",
                        "--rescan",
                        rescan_arg,
                    ],
                    timeout=15,
                )
                if (rc_wifi != 0 or not out_wifi.strip()) and not force_rescan:
                    rc_wifi, out_wifi, _err = self._run_nmcli(
                        [
                            "-t",
                            "-f",
                            "IN-USE,SSID,SECURITY,SIGNAL",
                            "device",
                            "wifi",
                            "list",
                            "--rescan",
                            "yes",
                        ],
                        timeout=15,
                    )
                if rc_wifi == 0 and out_wifi:
                    by_ssid = {}
                    for line in out_wifi.splitlines():
                        parts = self._split_nmcli_line(line)
                        if len(parts) < 4:
                            continue
                        in_use = parts[0].strip() == "*"
                        ssid = parts[1].strip()
                        security = parts[2].strip()
                        try:
                            signal = int(parts[3].strip())
                        except ValueError:
                            signal = 0

                        if not ssid:
                            continue

                        if ssid not in by_ssid:
                            by_ssid[ssid] = {
                                "ssid": ssid,
                                "security": security,
                                "signal": signal,
                                "in_use": in_use,
                            }
                        else:
                            entry = by_ssid[ssid]
                            if in_use:
                                entry["in_use"] = True
                            if signal > entry["signal"]:
                                entry["signal"] = signal
                            if security and not entry["security"]:
                                entry["security"] = security

                    networks = sorted(
                        by_ssid.values(),
                        key=lambda n: (not n["in_use"], -n["signal"], n["ssid"].lower()),
                    )

            # 4. Check internet connectivity
            has_internet = self._check_internet_connection()

            return {
                "eth_devices": eth_devices,
                "wifi_devices": wifi_devices,
                "wifi_enabled": wifi_enabled,
                "networks": networks,
                "has_internet": has_internet,
            }

        def on_done(result, error):
            self._is_refreshing = False
            self.scan_spinner.stop()
            self.scan_spinner.set_visible(False)
            self.refresh_button.set_sensitive(True)

            if error or not result:
                return

            self._update_ui(result)

        RunAsync(task, callback=on_done)

    def _update_ui(self, data: dict):
        eth_devices = data["eth_devices"]
        wifi_devices = data["wifi_devices"]
        wifi_enabled = data["wifi_enabled"]
        networks = data["networks"]
        has_internet = data["has_internet"]

        # Update Ethernet section
        self._eth_disconnected_dev = None
        eth_connected = False
        eth_conn_name = ""

        connected_eth = [d for d in eth_devices if d[1] == "connected"]
        connecting_eth = [d for d in eth_devices if d[1].startswith("connecting")]
        disconnected_eth = [d for d in eth_devices if d[1] == "disconnected"]
        unavailable_eth = [d for d in eth_devices if d[1] == "unavailable"]

        if connected_eth:
            dev, _state, conn = connected_eth[0]
            eth_connected = True
            eth_conn_name = conn or dev
            self.ethernet_row.set_title(f"{_('Connected')} ({eth_conn_name})")
            self.ethernet_row.set_subtitle(f"{_('Wired connection active on')} {dev}")
            self.ethernet_icon.set_from_icon_name("network-wired-symbolic")
            self.ethernet_status_icon.set_visible(True)
            self.ethernet_row.set_activatable(False)
        elif connecting_eth:
            dev, _state, _conn = connecting_eth[0]
            self.ethernet_row.set_title(f"{_('Connecting')} ({dev})...")
            self.ethernet_row.set_subtitle(_("Obtaining IP configuration..."))
            self.ethernet_icon.set_from_icon_name("network-wired-acquiring-symbolic")
            self.ethernet_status_icon.set_visible(False)
            self.ethernet_row.set_activatable(False)
        elif disconnected_eth:
            dev, _state, _conn = disconnected_eth[0]
            self._eth_disconnected_dev = dev
            self.ethernet_row.set_title(f"{_('Ethernet')} ({dev})")
            self.ethernet_row.set_subtitle(_("Cable plugged in — click to connect"))
            self.ethernet_icon.set_from_icon_name("network-wired-disconnected-symbolic")
            self.ethernet_status_icon.set_visible(False)
            self.ethernet_row.set_activatable(True)
        elif unavailable_eth:
            dev, _state, _conn = unavailable_eth[0]
            self.ethernet_row.set_title(f"{_('Ethernet')} ({dev})")
            self.ethernet_row.set_subtitle(_("Cable unplugged"))
            self.ethernet_icon.set_from_icon_name("network-wired-disconnected-symbolic")
            self.ethernet_status_icon.set_visible(False)
            self.ethernet_row.set_activatable(False)
        else:
            self.ethernet_row.set_title(_("No Ethernet Adapter"))
            self.ethernet_row.set_subtitle(_("No wired network interface detected"))
            self.ethernet_icon.set_from_icon_name("network-wired-disconnected-symbolic")
            self.ethernet_status_icon.set_visible(False)
            self.ethernet_row.set_activatable(False)

        # Update Wi-Fi controls
        has_wifi_hw = len(wifi_devices) > 0
        self.wifi_switch.set_sensitive(has_wifi_hw)
        self.refresh_button.set_sensitive(has_wifi_hw and wifi_enabled)
        self.hidden_wifi_button.set_sensitive(has_wifi_hw and wifi_enabled)

        self._updating_switch = True
        self.wifi_switch.set_active(has_wifi_hw and wifi_enabled)
        self._updating_switch = False

        # Clear existing Wi-Fi list
        while True:
            row = self.wifi_list.get_row_at_index(0)
            if row is None:
                break
            self.wifi_list.remove(row)

        wifi_connected_ssid = None
        for net in networks:
            if net["in_use"]:
                wifi_connected_ssid = net["ssid"]
                break
        if not wifi_connected_ssid:
            for _dev, state, conn in wifi_devices:
                if state == "connected" and conn:
                    wifi_connected_ssid = conn
                    break

        if not has_wifi_hw:
            empty_row = Adw.ActionRow(
                title=_("No Wi-Fi Adapter Found"),
                subtitle=_("No wireless network hardware was detected on this system."),
                activatable=False,
                selectable=False,
            )
            empty_row.add_prefix(
                Gtk.Image.new_from_icon_name("network-wireless-disabled-symbolic")
            )
            self.wifi_list.append(empty_row)
        elif not wifi_enabled:
            disabled_row = Adw.ActionRow(
                title=_("Wi-Fi is Turned Off"),
                subtitle=_("Switch on Wi-Fi above to scan for wireless networks."),
                activatable=False,
                selectable=False,
            )
            disabled_row.add_prefix(
                Gtk.Image.new_from_icon_name("network-wireless-disabled-symbolic")
            )
            self.wifi_list.append(disabled_row)
        elif not networks:
            none_row = Adw.ActionRow(
                title=_("No Wi-Fi Networks Found"),
                subtitle=_("Click the refresh button to scan again."),
                activatable=False,
                selectable=False,
            )
            none_row.add_prefix(
                Gtk.Image.new_from_icon_name("network-wireless-offline-symbolic")
            )
            self.wifi_list.append(none_row)
        else:
            for net in networks:
                entry = WifiEntry(
                    window=self.window,
                    page=self,
                    ssid=net["ssid"],
                    security=net["security"],
                    signal=net["signal"],
                    in_use=net["in_use"],
                )
                self.wifi_list.append(entry)

        # Update overall status description and page validity
        is_connected_any = has_internet or eth_connected or bool(wifi_connected_ssid)
        if has_internet:
            if eth_connected and wifi_connected_ssid:
                self.status_page.set_description(
                    f"{_('Connected via Ethernet and Wi-Fi')} ({wifi_connected_ssid}). {_('Ready to continue!')}"
                )
            elif eth_connected:
                self.status_page.set_description(
                    f"{_('Connected via Ethernet')}. {_('Ready to continue!')}"
                )
            elif wifi_connected_ssid:
                self.status_page.set_description(
                    f"{_('Connected to')} {wifi_connected_ssid}. {_('Ready to continue!')}"
                )
            else:
                self.status_page.set_description(
                    _("Connected to the internet. Ready to continue!")
                )
            self.set_valid(True)
            if self.window.timezone_screen.guessed_timezone is None:
                RunAsync(self.window.online)
        elif is_connected_any:
            self.status_page.set_description(
                _("Connected to local network, checking internet access...")
            )
            self.set_valid(False)
        else:
            self.status_page.set_description(
                _("Connect to a Wi-Fi network or plug in an Ethernet cable to continue.")
            )
            self.set_valid(False)

    def _on_ethernet_row_activated(self, *_):
        if not self._eth_disconnected_dev or self._is_connecting:
            return
        dev = self._eth_disconnected_dev
        self._is_connecting = True
        self.ethernet_spinner.set_visible(True)
        self.ethernet_spinner.start()
        self.ethernet_row.set_subtitle(_("Connecting..."))

        def task():
            return self._run_nmcli(["device", "connect", dev], timeout=20)

        def on_done(result, error):
            self._is_connecting = False
            self.ethernet_spinner.stop()
            self.ethernet_spinner.set_visible(False)
            self.refresh_network(force_rescan=False)

        RunAsync(task, callback=on_done)

    def _on_wifi_switch_toggled(self, switch, state):
        if self._updating_switch:
            return False

        def task():
            target = "on" if state else "off"
            self._run_nmcli(["radio", "wifi", target], timeout=10)

        def on_done(result, error):
            self.refresh_network(force_rescan=state)

        RunAsync(task, callback=on_done)
        return False

    def on_wifi_selected(self, wifi_row: WifiEntry):
        if self._is_connecting:
            return

        self._selected_wifi_row = wifi_row
        self._is_hidden_mode = False

        if not wifi_row.is_secured:
            # Open network: connect directly
            self._connect_open_wifi(wifi_row)
        else:
            # Secured network: open password dialog
            self.dialog_group.set_title(
                GLib.markup_escape_text(f'{_("Connect to")} "{wifi_row.ssid}"')
            )
            self.dialog_group.set_description(
                f"{_('Security')}: {wifi_row.security}"
            )
            self.ssid_entry.set_visible(False)
            self.identity_entry.set_visible(wifi_row.is_enterprise)
            self.identity_entry.set_text("")
            self.password_entry.set_text("")
            self.error_label.set_visible(False)
            self._set_dialog_busy(False)
            self.connect_dialog.present()
            if wifi_row.is_enterprise:
                self.identity_entry.grab_focus()
            else:
                self.password_entry.grab_focus()

    def _on_hidden_wifi_clicked(self, *_):
        if self._is_connecting:
            return

        self._selected_wifi_row = None
        self._is_hidden_mode = True

        self.dialog_group.set_title(_("Connect to Hidden Wi-Fi"))
        self.dialog_group.set_description(
            _("Enter the network name (SSID) and password (leave blank if open).")
        )
        self.ssid_entry.set_visible(True)
        self.ssid_entry.set_text("")
        self.identity_entry.set_visible(False)
        self.identity_entry.set_text("")
        self.password_entry.set_text("")
        self.error_label.set_visible(False)
        self._set_dialog_busy(False)
        self.connect_dialog.present()
        self.ssid_entry.grab_focus()

    def _set_dialog_busy(self, busy: bool):
        self.connect_button.set_sensitive(not busy)
        self.cancel_button.set_sensitive(not busy)
        self.ssid_entry.set_sensitive(not busy)
        self.identity_entry.set_sensitive(not busy)
        self.password_entry.set_sensitive(not busy)
        self.dialog_spinner.set_visible(busy)
        if busy:
            self.dialog_spinner.start()
        else:
            self.dialog_spinner.stop()

    def _connect_open_wifi(self, wifi_row: WifiEntry):
        self._is_connecting = True
        wifi_row.set_connecting(True)

        def task():
            return self._run_nmcli(
                ["device", "wifi", "connect", wifi_row.ssid], timeout=25
            )

        def on_done(result, error):
            self._is_connecting = False
            wifi_row.set_connecting(False)
            self.refresh_network(force_rescan=False)

        RunAsync(task, callback=on_done)

    def _on_dialog_connect_clicked(self, *_):
        if self._is_connecting:
            return

        if self._is_hidden_mode:
            ssid = self.ssid_entry.get_text().strip()
            is_enterprise = False
        else:
            if not self._selected_wifi_row:
                return
            ssid = self._selected_wifi_row.ssid
            is_enterprise = self._selected_wifi_row.is_enterprise

        password = self.password_entry.get_text()
        identity = self.identity_entry.get_text().strip()

        if not ssid:
            self.error_label.set_label(_("Please enter a network name (SSID)."))
            self.error_label.set_visible(True)
            return

        if is_enterprise and not identity:
            self.error_label.set_label(_("Please enter your username / identity."))
            self.error_label.set_visible(True)
            return

        if not self._is_hidden_mode and not password:
            self.error_label.set_label(_("Please enter the Wi-Fi password."))
            self.error_label.set_visible(True)
            return

        self._is_connecting = True
        self.error_label.set_visible(False)
        self._set_dialog_busy(True)
        if self._selected_wifi_row:
            self._selected_wifi_row.set_connecting(True)

        is_hidden = self._is_hidden_mode

        def task():
            # Remove any stale connection profile for this SSID so a previous
            # failed attempt does not block the new credentials.
            self._run_nmcli(["connection", "delete", "id", ssid], timeout=5)

            if is_enterprise:
                rc, out, err = self._run_nmcli(
                    [
                        "connection",
                        "add",
                        "type",
                        "wifi",
                        "con-name",
                        ssid,
                        "ssid",
                        ssid,
                        "wifi-sec.key-mgmt",
                        "wpa-eap",
                        "802-1x.eap",
                        "peap",
                        "802-1x.phase2-auth",
                        "mschapv2",
                        "802-1x.identity",
                        identity,
                        "802-1x.password",
                        password,
                    ],
                    timeout=10,
                )
                if rc != 0:
                    return rc, out, err
                return self._run_nmcli(
                    ["connection", "up", "id", ssid], timeout=30
                )
            else:
                args = ["device", "wifi", "connect", ssid]
                if password:
                    args += ["password", password]
                if is_hidden:
                    args += ["hidden", "yes"]
                return self._run_nmcli(args, timeout=30)

        def on_done(result, error):
            self._is_connecting = False
            self._set_dialog_busy(False)
            if self._selected_wifi_row:
                self._selected_wifi_row.set_connecting(False)

            if error:
                self.error_label.set_label(str(error))
                self.error_label.set_visible(True)
                return

            rc, out, err = result if result else (1, "", _("Connection failed"))
            if rc == 0 and "error" not in out.lower() and "error" not in err.lower():
                self.connect_dialog.hide()
                self.refresh_network(force_rescan=False)
            else:
                msg = err or out or _("Failed to connect. Please check your password and try again.")
                self.error_label.set_label(msg)
                self.error_label.set_visible(True)

        RunAsync(task, callback=on_done)

    def on_wifi_disconnect(self, wifi_row: WifiEntry):
        if self._is_connecting:
            return
        self._is_connecting = True
        wifi_row.set_connecting(True)

        def task():
            return self._run_nmcli(
                ["connection", "down", "id", wifi_row.ssid], timeout=10
            )

        def on_done(result, error):
            self._is_connecting = False
            wifi_row.set_connecting(False)
            self.refresh_network(force_rescan=False)

        RunAsync(task, callback=on_done)
