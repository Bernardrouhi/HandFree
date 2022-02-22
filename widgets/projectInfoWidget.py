from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
								QSizePolicy, QLabel, QPushButton)
from PySide2.QtCore import Qt

from ..core.pipeline_handler import Pipeline

class ProjectInfo(QWidget):
	def __init__(self, parent=None):
		super(ProjectInfo, self).__init__(parent)
	
		self.setMinimumHeight(1)
		self.setMinimumWidth(1)
		space=100

		# ------------- Main Layout --------------
		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(5,5,5,5)
		main_layout.setSpacing(5)
		main_layout.setAlignment(Qt.AlignTop)
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		# ------- Row -------
		# ----------------------------------------
		project_Layout = QHBoxLayout()
		project_Layout.setContentsMargins(0,0,0,0)
		project_Layout.setSpacing(10)
		project_Layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		projectLabel = QLabel(u"Project:")
		projectLabel.setFixedWidth(space)
		projectLabel.setAlignment(Qt.AlignRight)
		self.project_txt = QLabel(u"None")

		project_Layout.addWidget(projectLabel)
		project_Layout.addWidget(self.project_txt)
		main_layout.addLayout(project_Layout)
		# ------- Row -------
		# ----------------------------------------
		assetType_Layout = QHBoxLayout()
		assetType_Layout.setContentsMargins(0,0,0,0)
		assetType_Layout.setSpacing(10)
		assetType_Layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetTypeLabel = QLabel(u"Asset Type:")
		assetTypeLabel.setFixedWidth(space)
		assetTypeLabel.setAlignment(Qt.AlignRight)
		self.assetType_txt = QLabel(u"None")

		assetType_Layout.addWidget(assetTypeLabel)
		assetType_Layout.addWidget(self.assetType_txt)
		main_layout.addLayout(assetType_Layout)
		# ------- Row -------
		# ----------------------------------------
		assetContainer_Layout = QHBoxLayout()
		assetContainer_Layout.setContentsMargins(0,0,0,0)
		assetContainer_Layout.setSpacing(10)
		assetContainer_Layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetContainerLabel = QLabel(u"Asset Container:")
		assetContainerLabel.setFixedWidth(space)
		assetContainerLabel.setAlignment(Qt.AlignRight)
		self.assetContainer_txt = QLabel(u"None")

		assetContainer_Layout.addWidget(assetContainerLabel)
		assetContainer_Layout.addWidget(self.assetContainer_txt)
		main_layout.addLayout(assetContainer_Layout)

		# ------- Row -------
		# ----------------------------------------
		assetSpace_Layout = QHBoxLayout()
		assetSpace_Layout.setContentsMargins(0,0,0,0)
		assetSpace_Layout.setSpacing(10)
		assetSpace_Layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetSpaceLabel = QLabel(u"Asset Space:")
		assetSpaceLabel.setFixedWidth(space)
		assetSpaceLabel.setAlignment(Qt.AlignRight)
		self.assetSpace_txt = QLabel(u"None")

		assetSpace_Layout.addWidget(assetSpaceLabel)
		assetSpace_Layout.addWidget(self.assetSpace_txt)
		main_layout.addLayout(assetSpace_Layout)

		# ------- Row -------
		# ----------------------------------------
		assetName_Layout = QHBoxLayout()
		assetName_Layout.setContentsMargins(0,0,0,0)
		assetName_Layout.setSpacing(10)
		assetName_Layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetNameLabel = QLabel(u"Asset Name:")
		assetNameLabel.setFixedWidth(space)
		assetNameLabel.setAlignment(Qt.AlignRight)
		self.assetName_txt = QLabel(u"None")

		assetName_Layout.addWidget(assetNameLabel)
		assetName_Layout.addWidget(self.assetName_txt)
		main_layout.addLayout(assetName_Layout)

		# ------- Row -------
		# ----------------------------------------
		rowLayout_04 = QHBoxLayout()
		rowLayout_04.setContentsMargins(0,0,0,0)
		rowLayout_04.setSpacing(3)
		rowLayout_04.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		refresh_btn = QPushButton(u"Refresh")
		refresh_btn.clicked.connect(self.update_information)

		rowLayout_04.addWidget(refresh_btn)
		main_layout.addLayout(rowLayout_04)

		self.update_information()

	def update_information(self):
		_pm = Pipeline()
		projectName = _pm.get_ProjectName()
		assetType = _pm.get_AssetType()
		assetContainer = _pm.get_AssetContainer()
		assetSpace = _pm.get_AssetSpace()
		assetName = _pm.get_AssetName()

		self.project_txt.setText(projectName)
		self.assetType_txt.setText(assetType)
		self.assetContainer_txt.setText(assetContainer)
		self.assetSpace_txt.setText(assetSpace)
		self.assetName_txt.setText(assetName)
