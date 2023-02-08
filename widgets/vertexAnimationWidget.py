from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFileDialog,
								QSizePolicy, QLabel, QPushButton, QLineEdit, QSpinBox)
from PySide2.QtCore import Qt

class VertexAnimationWidget(QWidget):
	def __init__(self, parent=None):
		super(VertexAnimationWidget, self).__init__(parent=parent)
	
		self.setMinimumHeight(1)
		self.setMinimumWidth(1)
		label_width=100

		# ------------- Main Layout --------------
		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(5,5,5,5)
		main_layout.setSpacing(5)
		main_layout.setAlignment(Qt.AlignTop)
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		# ------- Mesh Row -------
		# ----------------------------------------
		basic_layout = QHBoxLayout()
		basic_layout.setContentsMargins(0,0,0,0)
		basic_layout.setSpacing(10)
		basic_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		basic_label = QLabel(u"Mesh:")
		basic_label.setFixedWidth(label_width)
		basic_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		self.Mesh_in = QLineEdit()
		self.Mesh_in.setReadOnly(True)
		self.Mesh_in.setEnabled(False)
		basic_btn = QPushButton("Pick")
		basic_btn.clicked.connect(self.pick_SelectedMesh)

		basic_layout.addWidget(basic_label)
		basic_layout.addWidget(self.Mesh_in)
		basic_layout.addWidget(basic_btn)
		main_layout.addLayout(basic_layout)

		# ------- Mesh Row -------
		# ----------------------------------------
		basic_layout = QHBoxLayout()
		basic_layout.setContentsMargins(0,0,0,0)
		basic_layout.setSpacing(10)
		basic_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		basic_label = QLabel(u"Frames:")
		basic_label.setFixedWidth(label_width)
		basic_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		self.startFrame_spin = QSpinBox()
		self.startFrame_spin.setMinimum(0)
		self.startFrame_spin.setMaximum(9999999)
		self.startFrame_spin.setSingleStep(1)
		self.endFrame_spin = QSpinBox()
		self.endFrame_spin.setMinimum(0)
		self.endFrame_spin.setMaximum(9999999)
		self.endFrame_spin.setSingleStep(1)

		basic_layout.addWidget(basic_label)
		basic_layout.addWidget(self.startFrame_spin)
		basic_layout.addWidget(self.endFrame_spin)
		main_layout.addLayout(basic_layout)

		# ------- Destination Row -------
		# ----------------------------------------
		basic_layout = QHBoxLayout()
		basic_layout.setContentsMargins(0,0,0,0)
		basic_layout.setSpacing(10)
		basic_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		basic_label = QLabel('Destination:')
		basic_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		basic_label.setFixedWidth(label_width)
		self.dest_in = QLineEdit()
		basic_btn = QPushButton("Browse")
		basic_btn.clicked.connect(self.pick_ExportDirectory)

		basic_layout.addWidget(basic_label)
		basic_layout.addWidget(self.dest_in)
		basic_layout.addWidget(basic_btn)
		main_layout.addLayout(basic_layout)

		# ------- Action Row -------
		# ----------------------------------------
		basic_layout = QHBoxLayout()
		basic_layout.setContentsMargins(0,0,0,0)
		basic_layout.setSpacing(3)
		basic_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		basic_btn = QPushButton(u"Bake to Texture")
		basic_btn.clicked.connect(self.bake)

		basic_layout.addWidget(basic_btn)
		main_layout.addLayout(basic_layout)

	def pick_ExportDirectory(self):
		'''Pick Export Directory'''
		pickedDir = QFileDialog.getExistingDirectory(self,"Pick Export Directory",self.dest_in.text())
		if pickedDir:
			self.dest_in.setText(pickedDir)

	def pick_SelectedMesh(self):
		print("Picking")
		pass

	def bake(self):
		print("Baking...")
		pass
