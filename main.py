#!/usr/bin/python
import os
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QDockWidget, QLabel)

import core
import widgets

from widgets import handsFreeMainWindow
from core import mayaHelper, env_handler

reload(handsFreeMainWindow)
reload(mayaHelper)
reload(env_handler)

from core.mayaHelper import get_MayaWindow, create_WorkSpaceControl, get_MayaControl, delete_WorkSpaceControl, restore_WorkSpaceControl
from core.env_handler import check_hfp_file, check_hfp_env
from widgets.handsFreeMainWindow import HandsFreeMainWindow

#Widget
class HFWidget(QWidget):
	instances = list()
	TITLE = "HandsFree v2.1.1-BETA"
	def __init__(self, parent=get_MayaWindow(), projectfile=str(), edit=bool(False),  *args, **kwargs):
		super(HFWidget, self).__init__(parent=parent, *args, **kwargs)
		self.setMinimumWidth(400)
		self.setWindowTitle(self.TITLE)

		projectfile = check_hfp_file(projectfile=projectfile)
		if not projectfile:
			projectfile = check_hfp_env()

		self.layout = QHBoxLayout(self)
		self.layout.setContentsMargins(0,0,0,0)
		self.project = HandsFreeMainWindow(parent=None, projectfile=projectfile, edit=edit)
		self.layout.addWidget(self.project)

		self.setWindowFlags(Qt.Window)
		self.setAttribute(Qt.WA_DeleteOnClose)
		self.resize(400, 720)


def viewMode(hfp_path=str()):
	return HFWidget(parent=get_MayaWindow(), projectfile=hfp_path, edit=False)

def editMode(hfp_path=str()):
	return HFWidget(parent=get_MayaWindow(), projectfile=hfp_path, edit=True)

