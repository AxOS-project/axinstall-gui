# keyboard_Screen.py

#
# Copyright 2025 Ardox

#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from axinstall.classes import keymap
from axinstall.locales.locales_list import locations
from axinstall.widgets.layout import KeyboardLayout
from axinstall.classes.axinstall_screen import AxinstallScreen
from axinstall.utils.gtk_helpers import set_list_text
from gi.repository import Gtk, Adw
from gettext import gettext as _
from axinstall.utils.command import CommandUtils
import os


@Gtk.Template(resource_path="/com/axos-project/axinstall/pages/keyboard/keyboard_screen.ui")
class KeyboardScreen(AxinstallScreen, Adw.Bin):
    __gtype_name__ = "KeyboardScreen"

    event_controller = Gtk.EventControllerKey.new()

    preview = Gtk.Template.Child()
    keyboard_search_button = Gtk.Template.Child()
    country_preview_list = Gtk.Template.Child()
    variant_preview = Gtk.Template.Child()
    variant_preview_list = Gtk.Template.Child()

    layout = None
    variant = ""
    move_to_summary = False

    def __init__(self, window, keymaps, set_valid, application, **kwargs):
        super().__init__(set_valid=set_valid, **kwargs)
        self.window = window

        builder = Gtk.Builder.new_from_resource(
            "/com/axos-project/axinstall/pages/keyboard/keyboard_dialog.ui"
        )
        self.search_dialog = builder.get_object("search_dialog")

        self.search_dialog.set_transient_for(self.window)
        self.search_dialog.set_modal(self.window)

        self.keyboard_entry_search = builder.get_object("keyboard_entry_search")
        self.layout_list = builder.get_object("layout_list")
        self.keyboard_search = builder.get_object("keyboard_search")
        self.select_variant_button = builder.get_object("select_variant_button")

        self.event_controller.connect("key-released", self.search_keyboards)
        self.keyboard_entry_search.add_controller(self.event_controller)

        self.keyboard_search_button.connect("clicked", self.present_dialog)
        self.select_variant_button.connect("clicked", self.confirm_selection)

        for keymap in keymaps:
            layout = KeyboardLayout(
                window=window,
                country=keymap.layout,
                country_shorthand=keymap.backend_layout,
                application=application,
                keymap=keymap,
                **kwargs,
            )
            self.layout_list.append(layout)

            for row in layout.rows:
                if row.country_shorthand == "us" and row.variant == "normal":
                    self.variant = layout
                    self.select_variant(row)

                    break

    def confirm_selection(self, *_):
        self.search_dialog.hide()

    def select_variant(self, variant, *_):
        self.variant = variant

        self.variant_preview.set_visible(variant.variant != "normal")

        set_list_text(self.country_preview_list, variant.country)
        set_list_text(self.variant_preview_list, variant.variant)

        self.preview.set_description(
            f'Test "{variant.country_shorthand} - {variant.variant}"'
        )

        self.set_xkbmap(variant.country_shorthand, variant.variant)

        self.set_valid(True)

    def set_xkbmap(self, layout, variant=None):
        
        is_wayland = os.environ.get("WAYLAND_DISPLAY") is not None
        is_sleex = os.environ.get("XDG_CURRENT_DESKTOP") == "Sleex"

        if is_sleex:
            CommandUtils.run_command(
                [
                    "hyprctl",
                    "keyword",
                    "input:kb_layout",
                    layout,
                ]
            )
        else: # The fact that this part doesn't even works because the user needs to relogin...
            if is_wayland:
                if variant is None or variant == "normal":
                    CommandUtils.run_command(
                        [
                            "localectl",
                            "set-keymap",
                            layout,
                        ]
                    )
                else:
                    CommandUtils.run_command(
                        [
                            "localectl",
                            "set-keymap",
                            "{}+{}".format(layout, variant),
                        ]
                    )
            else:  # for Xorg
                if variant is None or variant == "normal":
                    CommandUtils.run_command(
                        [
                            "setxkbmap",
                            layout,
                        ]
                    )
                else:
                    CommandUtils.run_command(
                        [
                            "setxkbmap",
                            layout,
                            "-variant",
                            variant,
                        ]
                    )


    def present_dialog(self, *_):
        self.search_dialog.present()

    def search_keyboards(self, *_):
        terms = self.keyboard_entry_search.get_text()
        self.layout_list.set_filter_func(self.filter_layouts, terms)

    @staticmethod
    def filter_layouts(row, terms=None):
        try:
            text = row.get_title()
            text = text.lower() + row.get_subtitle().lower()
            if terms.lower() in text:
                return True
        except:
            return True
        return False
