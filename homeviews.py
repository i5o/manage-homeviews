#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013  Ignacio Rodríguez <ignacio@sugarlabs.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 021101301, USA.

from gettext import gettext as _

from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Gdk

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics import style
from sugar3.activity.widgets import ActivityButton
from sugar3.activity.widgets import StopButton
from sugar3.graphics.alert import NotifyAlert

from icondialog import IconDialog

_DESKTOP_CONF_DIR = 'org.sugarlabs.desktop'
_HOMEVIEWS_KEY = 'homeviews'


class ManageViews(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.build_toolbar()
        self.__canvas = ToolbarView(self)
        width = Gdk.Screen.width()
        self.__canvas.set_size_request(width, 55)

        fixed = Gtk.Fixed()
        center = (Gdk.Screen.height() / 2) - 55
        fixed.put(self.__canvas, 0, center)

        eventbox = Gtk.EventBox()
        eventbox.add(fixed)
        eventbox.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse('white'))

        self.set_canvas(eventbox)
        self.show_all()

    def build_toolbar(self):
        toolbox = ToolbarBox()
        toolbar = toolbox.toolbar

        activity_button = ActivityButton(self)
        toolbar.insert(activity_button, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar.insert(separator, -1)

        stopbtn = StopButton(self)
        toolbar.insert(stopbtn, -1)
        toolbar.show_all()

        self.set_toolbar_box(toolbox)

    def write_file(self, file_path):
        self.__canvas.save_to_gsettings()
        return


class ToolbarView(ToolbarBox):

    def __init__(self, activity):
        ToolbarBox.__init__(self)

        self.add_btn = ToolButton(icon_name='list-add',
                                  tooltip=_('Add new favorite view'))
        self.insert(self.add_btn, -1)
        self.add_btn.connect('clicked', self.add_view)

        self.activity = activity
        self._favorite_icons = {}
        self._view_icons = {}
        self._view_buttons = {}
        self._favorite_names = {}

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)

        self.insert(separator, -1)

        self.load_views()
        self.show_all()

    def insert(self, item, pos):
        self.toolbar.insert(item, pos)

    def remove_item(self, item):
        del(self._view_icons[item])
        del(self._favorite_icons[item])
        del(self._view_buttons[item])
        self.save_to_gsettings()
        self.toolbar.remove(item)

    def load_views(self):
        settings = Gio.Settings(_DESKTOP_CONF_DIR)
        data = settings.get_value('homeviews').unpack()

        current = 0
        for view in data:
            label = _('Favorites view %d') % (current + 1)

            print view, data
            view_icon = view['view-icon']
            favorite_icon = view['favorite-icon']

            button = ToolbarButton(label=label, icon_name=view_icon)
            page = FavoritePage(button, self, view_icon, favorite_icon, label)
            button.set_page(page)
            self.insert(button, -1)
            self._view_icons[button] = view_icon
            self._favorite_icons[button] = favorite_icon
            self._view_buttons[button] = button
            self._favorite_names[button] = label
            current += 1

    def add_view(self, widget):
        if len(self._view_icons) >= 5:
            for x in self.activity._alerts:
                self.activity.remove_alert(x)
            alert = NotifyAlert(10)
            alert.props.title = _('Limit reached')
            alert.props.msg = _('You have reached the maximum limit of '
                                'favorites views, please delete some before '
                                'continuing.')
            self.activity.add_alert(alert)
            alert.connect('response',
                          lambda x, y: self.activity.remove_alert(x))
            return

        current = len(self._view_buttons) + 1
        label = _('Favorites view %d') % current
        button = ToolbarButton(label=label, icon_name='view-radial')
        page = FavoritePage(button, self, 'view-radial', 'emblem-favorite',
                            label)
        button.set_page(page)

        self._view_icons[button] = 'view-radial'
        self._favorite_icons[button] = 'emblem-favorite'
        self._view_buttons[button] = button
        self._favorite_names[button] = label

        self.insert(button, -1)
        self.save_to_gsettings()
        self.show_all()

    def save_to_gsettings(self, icon=False, name=False):

        gsettings = Gio.Settings(_DESKTOP_CONF_DIR)
        homeviews = []

        for button in self._view_buttons:
            homeview = {'layout': 'ring-layout',
                        'view-icon': self._view_icons[button],
                        'favorite-icon': self._favorite_icons[button]}
            homeviews.append(homeview)

        variant = GLib.Variant('aa{ss}', homeviews)
        gsettings.set_value(_HOMEVIEWS_KEY, variant)
        if icon:
            for x in self.activity._alerts:
                self.activity.remove_alert(x)
            alert = NotifyAlert(5)
            alert.props.title = _('Icon')
            alert.props.msg = _('For see icons, restart sugar is needed.')
            self.activity.add_alert(alert)
            alert.connect('response',
                          lambda x, y: self.activity.remove_alert(x))
        if name:
            for x in self.activity._alerts:
                self.activity.remove_alert(x)
            alert = NotifyAlert(5)
            alert.props.title = _('View Name')
            alert.props.msg = _('For seeing View name changes, '
                                'restarting Sugar is required.')
            self.activity.add_alert(alert)
            alert.connect('response',
                          lambda x, y: self.activity.remove_alert(x))


class FavoritePage(Gtk.Toolbar):

    def __init__(self, button, toolbar, view_icon, favorite_icon, label):
        Gtk.Toolbar.__init__(self)

        self.toolbar = toolbar
        self.button = button
        self.view_icon = view_icon
        self.favorite_icon = favorite_icon

        self.set_view_icon = ToolButton(view_icon)
        self.set_view_icon.set_tooltip(_('Set toolbar icon'))
        self.set_view_icon.connect('clicked', self.set_icon, False)

        self.set_favorite_icon = ToolButton(favorite_icon)
        self.set_favorite_icon.set_tooltip(_('Set the icon of favorites list'))
        self.set_favorite_icon.connect('clicked', self.set_icon, True)

        entry_toolitem = Gtk.ToolItem()

        self.favorite_name_entry = Gtk.Entry()
        self.favorite_name_entry.set_placeholder_text(_('Favorite view name'))
        width = Gdk.Screen.width() - (style.STANDARD_ICON_SIZE * 12)
        entry_toolitem.set_size_request(width, 55)
        self.favorite_name_entry.set_text(label)
        self.favorite_name_entry.connect("activate", self.edited_view_name)
        entry_toolitem.add(self.favorite_name_entry)

        label = Gtk.Label(_('Name of favorite view') + '\t')
        label.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse('white'))
        tool_label = Gtk.ToolItem()
        tool_label.add(label)

        self.remove_btn = ToolButton('list-remove')
        self.remove_btn.set_tooltip(_('Remove favorite view'))
        self.remove_btn.connect('clicked', self.remove_view)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)

        self.insert(self.set_view_icon, -1)
        self.insert(self.set_favorite_icon, -1)
        self.insert(tool_label, -1)
        self.insert(entry_toolitem, -1)
        self.insert(separator, -1)
        self.insert(self.remove_btn, -1)
        self.show_all()

    def set_icon(self, widget, favorite=False, window=None):
        if not window:
            dialog = IconDialog()
            dialog.show_all()
            dialog.connect('destroy', self.set_icon, favorite, dialog)

        if window:
            response = window.get_icon()
            if not response:
                return
            if favorite:
                self.set_favorite_icon.set_icon_name(response)
                self.toolbar._favorite_icons[self.button] = response
            else:
                self.set_view_icon.set_icon_name(response)
                self.toolbar._view_icons[self.button] = response
                self.button.set_icon_name(response)

            self.toolbar.save_to_gsettings(True)

    def remove_view(self, widget):
        self.button.set_expanded(False)
        self.toolbar.remove_item(self.button)

    def edited_view_name(self, entry):
        label = entry.get_text()
        self.toolbar._favorite_names[self.button] = label

        self.toolbar.save_to_gsettings(False, True)
