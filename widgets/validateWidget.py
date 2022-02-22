from PySide2.QtWidgets import (QHBoxLayout, QLabel, QWidget)
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt, QSize

from ..core.style_handler import icon_path

class ValidationKeys:
	Valid = "VALID"
	Invalid = "INVALID"
	Idle = "IDLE"

class ValidateWidget(QWidget):
	'''Manage project assets'''
	def __init__(self, parent=None, size=QSize(16,16)):
		super(ValidateWidget, self).__init__(parent)
		self._size = size

		main_layout = QHBoxLayout(self)
		main_layout.setContentsMargins(0,0,0,0)
		main_layout.setSpacing(0)
		self.pixmap = QPixmap()
		self._status = ValidationKeys.Idle

		self.dummy_label = QLabel()
		self.dummy_label.setPixmap(self.pixmap)

		main_layout.addWidget(self.dummy_label)
		self.set_idle()
		self.setLayout(main_layout)

	def set_Valid(self):
		self.pixmap.load(icon_path('check_icon', 'svg'))
		self.dummy_label.setPixmap(self.pixmap)
		self.pixmap = self.pixmap.scaled(self._size, Qt.KeepAspectRatio)
		self._status = ValidationKeys.Valid

	def set_Invalid(self):
		self.pixmap.load(icon_path('cancel_icon', 'svg'))
		self.dummy_label.setPixmap(self.pixmap)
		self.pixmap = self.pixmap.scaled(self._size, Qt.KeepAspectRatio)
		self._status = ValidationKeys.Invalid

	def set_idle(self):
		self.pixmap.load(icon_path('dotdot_icon', 'svg'))
		self.dummy_label.setPixmap(self.pixmap)
		self.pixmap = self.pixmap.scaled(self._size, Qt.KeepAspectRatio)
		self._status = ValidationKeys.Idle

	def get_status(self):
		return self._status
