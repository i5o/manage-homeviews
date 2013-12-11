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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from gi.repository import Gtk

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityButton
from sugar3.activity.widgets import StopButton


class ManageViews(activity.Activity):
	def __init__(self, handle):
		activity.Activity.__init__(self, handle)

		self.build_toolbar()

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