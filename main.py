#!/usr/bin/python

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QWidget, QHBoxLayout, QDockWidget, QLabel)

from widgets import handsFreeMainWindow
reload(handsFreeMainWindow)
from core import mayaHelper
reload(mayaHelper)

from core.mayaHelper import get_MayaWindow, create_WorkSpaceControl, get_MayaControl, delete_WorkSpaceControl, restore_WorkSpaceControl
from widgets.handsFreeMainWindow import HandsFreeMainWindow

#Widget
class HFWidget(QWidget):
	instances = list()
	TITLE = "HandsFree v1.0.0-BETA"
	def __init__(self, parent=get_MayaWindow(), projectfile=str(), edit=bool(False),  *args, **kwargs):
		super(HFWidget, self).__init__(parent=parent, *args, **kwargs)
		self.setMinimumWidth(400)
		self.setWindowTitle(self.TITLE)

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
