import os, subprocess, re
from PySide2.QtWidgets import (QAction, QFileDialog, QListWidget, QMenu, QSizePolicy,
						  QAbstractItemView, QTableWidget,QHeaderView, QHBoxLayout,
						  QTableWidgetItem, QComboBox, QDialog, QVBoxLayout, QLabel,
						  QLineEdit, QPushButton,QWidget)
from PySide2.QtGui import (QRegExpValidator)
from PySide2.QtCore import (Qt, QPoint, QRegExp)

from ..core import publishMetadata

reload(publishMetadata)

from ..core.publishMetadata import PublishLogKeys, PublishMeta

class LogViewerWidget(QWidget):
	def __init__(self, parent=None):
		super(LogViewerWidget, self).__init__(parent)

		self.setMinimumHeight(1)
		self.setMinimumWidth(1)

		# ------------- Main Layout --------------
		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(5,5,5,5)
		main_layout.setSpacing(5)
		main_layout.setAlignment(Qt.AlignTop)
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		# ------- Row -------
		# ----------------------------------------
		log_layout = QHBoxLayout()
		log_layout.setContentsMargins(0,0,0,0)
		log_layout.setSpacing(3)
		log_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		self.log_columns = [PublishLogKeys.VERSION, PublishLogKeys.VARIANT, PublishLogKeys.USER, PublishLogKeys.WORKFILES, PublishLogKeys.PUBLISHFILES , PublishLogKeys.RECORD]
		self.log_table = QTableWidget(0, len(self.log_columns))
		self.log_table.setHorizontalHeaderLabels(self.log_columns)
		# self.log_table.cellChanged.connect(self.assetSpace_CellChanged)
		# Style
		assetSpace_VH = self.log_table.verticalHeader()
		assetSpace_VH.hide()
		assetSpace_HH = self.log_table.horizontalHeader()
		assetSpace_HH.setSectionResizeMode(0, QHeaderView.ResizeToContents)
		assetSpace_HH.setSectionResizeMode(1, QHeaderView.Interactive)
		assetSpace_HH.setSectionResizeMode(2, QHeaderView.Interactive)
		assetSpace_HH.setSectionResizeMode(3, QHeaderView.Interactive)
		assetSpace_HH.setSectionResizeMode(4, QHeaderView.Interactive)
		# self.log_table.setContextMenuPolicy(Qt.CustomContextMenu)
		
		# self.log_table.customContextMenuRequested.connect(self.assetSpaceMenu)

		log_layout.addWidget(self.log_table)
		main_layout.addLayout(log_layout)

	def load_log(self, meta=PublishMeta):
		self.log_table.setRowCount(0)
		for log in meta.get_logs():
			index = self.log_table.rowCount()
			self.log_table.insertRow(index)
	
			# Version
			version_cell = QTableWidgetItem()
			version_cell.setText(str(log[PublishLogKeys.VERSION]))

			self.log_table.setItem(index, 0, version_cell)

			# Variant
			variant_cell = QTableWidgetItem()
			variant_cell.setText(str(log[PublishLogKeys.VARIANT]))

			self.log_table.setItem(index, 1, variant_cell)

			# User
			user_cell = QTableWidgetItem()
			user_cell.setText(str(log[PublishLogKeys.USER]))
			
			self.log_table.setItem(index, 2, user_cell)

			# Work File
			workfile_cell = QTableWidgetItem()
			workfile_cell.setText(str(log[PublishLogKeys.WORKFILES]))

			self.log_table.setItem(index, 3, workfile_cell)
			
			# Published File
			published_cell = QTableWidgetItem()
			published_cell.setText(str(log[PublishLogKeys.PUBLISHFILES]))

			self.log_table.setItem(index, 4, published_cell)
			
			# Date
			date_cell = QTableWidgetItem()
			date_cell.setText(str(log[PublishLogKeys.RECORD]))

			self.log_table.setItem(index, 5, date_cell)
		