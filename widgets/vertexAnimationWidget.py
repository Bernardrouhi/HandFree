import os, time
from random import randrange
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFileDialog,
								QSizePolicy, QLabel, QPushButton, QLineEdit, QSpinBox)
from PySide2.QtCore import Qt
from PySide2.QtGui import QImage, QColor
from  ..core import mayaHelper

reload(mayaHelper)

from ..core.mayaHelper import (getActiveItems, get_playback_min, set_currentFrame,
								get_playback_max, get_shape)

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
		self.startFrame_spin.setMaximum(9999999)
		self.startFrame_spin.setSingleStep(1)
		self.endFrame_spin = QSpinBox()
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
		self.dest_in.setReadOnly(True)
		self.dest_in.setEnabled(False)
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

		self.init()

	def init(self):
		items = getActiveItems()
		if items : self.Mesh_in.setText(items[0])
		self.startFrame_spin.setValue(get_playback_min())
		self.endFrame_spin.setValue(get_playback_max())


	def pick_ExportDirectory(self):
		'''Pick Export Directory'''
		fileName = QFileDialog.getSaveFileName(self, "Save F:xile", self.dest_in.text(), "Images (*.png)")
		if fileName:
			filePath = fileName[0]
			if filePath:
				self.dest_in.setText(os.path.normpath(filePath))

	def pick_SelectedMesh(self):
		items = getActiveItems()
		if items : self.Mesh_in.setText(items[0])

	def convert_vertex_to_rgb(self, VertexIndex=int):
		# location = 
		pixel_color = QColor(randrange(255), randrange(255), randrange(255), 255)
		return pixel_color

	def bake(self):
		shapes = get_shape(NodeName=self.Mesh_in.text())
		endFrame = self.endFrame_spin.value()
		startFrame = self.startFrame_spin.value()
		filePath = self.dest_in.text()

		if shapes:
			shape = shapes[0]
			UV = dict()
			for vertex_id, vertex in enumerate(shape.vtx):
				Us, Vs, FaceIds = vertex.getUVs()
				vertexUV = zip(Us, Vs)
				UV[vertex_id] = list(set(vertexUV))
			VertexNumber = len(UV)
			img = QImage(VertexNumber, endFrame, QImage.Format_ARGB32)
			img.fill(0)

			frames = 1 + endFrame - startFrame
			for frame in range(0, frames):
				set_currentFrame(frame)
				for VertexIndex in range(VertexNumber):
					pixel_color = self.convert_vertex_to_rgb(VertexIndex=VertexIndex)
					img.setPixelColor(VertexIndex, frame, pixel_color)

			img.save(filePath, 'PNG')

