# timezone_screen.py

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


import os
import time
from gi.repository import Gtk, GLib, Adw
from gettext import gettext as _
import requests
from axinstall.classes.axinstall_screen import AxinstallScreen
from axinstall.widgets.timezone import TimezoneEntry
from axinstall.utils.gtk_helpers import set_list_text
from axinstall.utils.command import CommandUtils
from axinstall.utils.threading import RunAsync

from datetime import datetime, timedelta
from pytz import timezone
import pytz
from tzlocal import get_localzone_name


@Gtk.Template(resource_path="/com/axos-project/axinstall/pages/timezone/timezone_screen.ui")
class TimezoneScreen(AxinstallScreen, Adw.Bin):
    __gtype_name__ = "TimezoneScreen"

    event_controller = Gtk.EventControllerKey.new()

    ### Page and widgets on timezone screen
    timezone_search_button = Gtk.Template.Child()
    status_page = Gtk.Template.Child()

    region_preview_list = Gtk.Template.Child()
    location_preview_list = Gtk.Template.Child()

    preview = Gtk.Template.Child()
    preview_row = Gtk.Template.Child()

    chosen_timezone = None
    move_to_summary = False
    guessed_timezone = None
    guessed_country = None
    _is_guessing = False

    def __init__(self, window, locations, set_valid, application, **kwargs):
        super().__init__(set_valid=set_valid, **kwargs)
        self.window = window

        builder = Gtk.Builder.new_from_resource(
            "/com/axos-project/axinstall/pages/timezone/timezone_dialog.ui"
        )
        self.search_dialog = builder.get_object("search_dialog")

        self.search_dialog.set_transient_for(self.window)
        self.search_dialog.set_modal(self.window)

        self.timezone_entry_search = builder.get_object("timezone_entry_search")
        self.timezone_list = builder.get_object("timezone_list")
        self.timezone_search = builder.get_object("timezone_search")

        self.event_controller.connect("key-released", self.search_timezones)
        self.timezone_entry_search.add_controller(self.event_controller)
        self.timezone_list.connect("row-selected", self.select_timezone)
        self.timezone_search_button.connect("clicked", self.present_dialog)

        tz = get_localzone_name()

        # It is sad that ListBox does not have a .length or something
        # like that
        #
        # ˄˄ real
        self._timezone_list_length = 0

        for i in locations:
            for locale in i:
                row = TimezoneEntry(
                    window=window,
                    region=locale.region,
                    location=locale.location,
                    locale=locale.locales,
                    application=application,
                    **kwargs,
                )

                if tz == str(row):
                    self.update_from_row(row)
                    self.chosen_timezone = row
                    self.set_valid(True)

                self.timezone_list.append(row)
                self._timezone_list_length += 1

        if self.chosen_timezone is None:
            self.timezone_search_by_name("Europe", "London")

    def timezone_search_by_name(self, region, location):
        for i in range(self._timezone_list_length):
            row = self.timezone_list.get_row_at_index(i)
            if row is not None and row.region == region and row.location == location:
                self.chosen_timezone = row
                self.update_from_row(row)
                self.set_valid(True)
                break

    def on_show(self):
        if self.guessed_timezone is None and not self._is_guessing:
            RunAsync(self.ip_request_timezone)
        if self.chosen_timezone is not None:
            self.update_from_row(self.chosen_timezone)
            self.set_valid(True)

    def on_complete(self, *_):
        if self.chosen_timezone is not None:
            self.set_timezone(
                self.chosen_timezone.region, self.chosen_timezone.location
            )

    def set_timezone(self, region, location):
        tz_name = f"{region}/{location}"
        os.environ["TZ"] = tz_name
        try:
            time.tzset()
        except AttributeError:
            pass
        CommandUtils.run_command(
            [
                "sudo",
                "-E",
                "timedatectl",
                "set-timezone",
                tz_name,
            ]
        )

    def present_dialog(self, *_):
        self.search_dialog.present()

    def update_from_row(self, row):
        if row is None:
            return
        set_list_text(self.location_preview_list, row.location)
        set_list_text(self.region_preview_list, row.region)

        tz = row.get_timezone()

        utc_now = datetime.now(pytz.utc)
        tz_now = utc_now.astimezone(tz)

        self.preview.set_visible(True)
        self.preview.set_title("Preview")
        self.preview.set_description(f"Time in {tz_now.strftime('%Z (UTC %z)')}")
        self.preview_row.set_title(tz_now.strftime("%H:%M:%S"))
        self.preview_row.set_subtitle(tz_now.strftime("%a %-d %B %Y"))

    def ip_request_timezone(self):
        if self._is_guessing or self.guessed_timezone is not None:
            return
        self._is_guessing = True
        print("guessing your timezone")

        try:
            tz_str = None
            country_str = None

            for _attempt in range(3):
                try:
                    r = requests.get("http://ip-api.com/json", timeout=5)
                    data = r.json()
                    if data.get("status") == "success" and data.get("timezone"):
                        tz_str = data["timezone"]
                        country_str = data.get("country")
                        break
                except Exception:
                    pass

                try:
                    r = requests.get("https://ipwho.is/", timeout=5)
                    data = r.json()
                    if data.get("success", True) and data.get("timezone", {}).get("id"):
                        tz_str = data["timezone"]["id"]
                        country_str = data.get("country")
                        break
                except Exception:
                    pass

                time.sleep(1)

            if not tz_str or "/" not in tz_str:
                return

            self.guessed_timezone = tz_str
            self.guessed_country = country_str

            region, location = self.guessed_timezone.split("/", 1)

            for i in range(self._timezone_list_length):
                row = self.timezone_list.get_row_at_index(i)
                if row is not None and row.region == region and row.location == location:
                    self.chosen_timezone = row
                    self.set_timezone(row.region, row.location)

                    def apply_guessed_tz(r=row):
                        self.chosen_timezone = r
                        self.set_valid(True)
                        self.update_from_row(r)
                        self.status_page.set_description(
                            f"Automatically detected {r.location}."
                        )
                        return False

                    GLib.idle_add(apply_guessed_tz)

                    print(f'Guessed timezone as "{self.guessed_timezone}"!')
                    print(f'{self.guessed_country} will be used for mirrors.')
                    break
        except Exception as e:
            print("Failed to detect IP timezone!", e)
        finally:
            self._is_guessing = False

    def select_timezone(self, widget, row):
        self.search_dialog.hide()

        if row is not None and row is not self.timezone_search:
            print(row.get_title())
            self.chosen_timezone = row
            self.status_page.set_description("")
            self.update_from_row(row)
            self.set_timezone(row.region, row.location)
            self.set_valid(True)
        else:
            print("row is none!!")

    def search_timezones(self, *args):
        terms = self.timezone_entry_search.get_text()
        self.timezone_list.set_filter_func(self.filter_timezones, terms)

    @staticmethod
    def filter_timezones(row, terms=None):
        try:
            text = row.get_title()
            text = text.lower() + row.get_subtitle().lower()
            if terms.lower() in text:
                return True
        except:
            return True
        return False
