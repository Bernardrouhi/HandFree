import os
from PySide2.QtWidgets import (QFileDialog, QSizePolicy, QAbstractItemView, 
							QHBoxLayout, QDialog, QVBoxLayout, QLabel,
						  	QLineEdit, QPushButton, QTreeWidget)
from PySide2.QtCore import (Qt)

from ...core import projectMetadata

reload(projectMetadata)

from ...core.projectMetadata import ProjectMeta, AssetSpaceKeys, ProjectKeys

class ExportDialog(QDialog):
	def __init__(self, parent=None, project=ProjectMeta()):
		super(ExportDialog, self).__init__(parent=parent)

		self._project = project

		label_width = 100

		self.setFixedSize(500, 500)

		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(5,5,5,5)
		main_layout.setSpacing(5)
		main_layout.setAlignment(Qt.AlignTop)
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		# ------- Row -------
		# ----------------------------------------
		dest_layout = QHBoxLayout()
		dest_layout.setContentsMargins(0,0,0,0)
		dest_layout.setSpacing(3)
		dest_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		dest_label = QLabel('Destination:')
		dest_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		dest_label.setFixedWidth(label_width)
		self.dest_in = QLineEdit()
		dest_btn = QPushButton("Browse")
		dest_btn.clicked.connect(self.pick_ExportDirectory)


		dest_layout.addWidget(dest_label)
		dest_layout.addWidget(self.dest_in)
		dest_layout.addWidget(dest_btn)

		main_layout.addLayout(dest_layout)

		# ------- Row -------
		# ----------------------------------------
		published_layout = QHBoxLayout()
		published_layout.setContentsMargins(0,0,0,0)
		published_layout.setSpacing(3)
		published_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		published_label = QLabel("Published:")
		published_label.setFixedWidth(label_width)
		published_label.setAlignment(Qt.AlignTop|Qt.AlignRight)
		self.published_columns = ['Directory']
		self.published_list = QTreeWidget()
		self.published_list.setHeaderLabels(self.published_columns)
		self.published_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.published_list.setContextMenuPolicy(Qt.CustomContextMenu)

		published_layout.addWidget(published_label)
		published_layout.addWidget(self.published_list)

		main_layout.addLayout(published_layout)

		# ------- Row -------
		# ----------------------------------------
		action_layout = QHBoxLayout()
		action_layout.setContentsMargins(0,0,0,0)
		action_layout.setSpacing(3)
		action_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		ok_btn = QPushButton("Export")
		ok_btn.clicked.connect(self.accept)
		close_btn = QPushButton("Close")
		close_btn.clicked.connect(self.reject)

		action_layout.addWidget(ok_btn)
		action_layout.addWidget(close_btn)

		main_layout.addLayout(action_layout)

		self.setWindowTitle("Export Assets")

		self.load_PublishDirectory()

	def pick_ExportDirectory(self):
		'''Pick Export Directory'''
		pickedDir = QFileDialog.getExistingDirectory(self,"Pick Export Directory",self.dest_in.text())
		if pickedDir:
			self.dest_in.setText(pickedDir)
	
	def load_PublishDirectory(Self):
		pass
