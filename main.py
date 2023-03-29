#!/usr/bin/python
import os
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QDockWidget, QLabel)
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

import core
import widgets

from widgets import handFreeMainWindow
from core import env_handler

reload(handFreeMainWindow)
reload(env_handler)

from core.env_handler import check_hfp_file, check_hfp_env
from widgets.handFreeMainWindow import HandFreeMainWindow

OBJECT_NAME = "HandFreeCustomWindow"
TITLE = "HandFree v4.2.0"

class HFWidget(MayaQWidgetDockableMixin, QWidget):
	def __init__(self, parent=None, projectfile=str(), edit=bool(),  *args, **kwargs):
		super(HFWidget, self).__init__(parent=parent, *args, **kwargs)
		self.setWindowTitle(TITLE)

		projectfile = check_hfp_file(projectfile=projectfile)
		if not projectfile:
			projectfile = check_hfp_env()

		self.layout = QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.project = HandFreeMainWindow(parent=None, projectfile=projectfile, edit=edit)
		self.layout.addWidget(self.project)

		self.setWindowFlags(Qt.Window)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.resize(400, 720)

def launchHandFree(projectfile=str(), edit=bool()):
	handFreeWindow = HFWidget(projectfile=projectfile, edit=edit)
	handFreeWindow.show(dockable=True)
	return handFreeWindow

