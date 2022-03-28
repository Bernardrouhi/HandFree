import os, getpass, json, re, shutil
from PySide2.QtWidgets import (QAction, QFileDialog, QListWidget, QMenu, QSizePolicy,
						  QAbstractItemView, QTableWidget,QHeaderView, QHBoxLayout,
						  QTableWidgetItem, QComboBox, QDialog, QVBoxLayout, QLabel,
						  QLineEdit, QPushButton, QGroupBox, QStackedLayout, QFrame,
						  QCheckBox, QTabWidget, QWidget)
from PySide2.QtGui import (QRegExpValidator)
from PySide2.QtCore import (Qt, QPoint, QRegExp)

from ...core import projectMetadata, publishMetadata, mayaHelper
from . import copyDialog

reload(projectMetadata)
reload(publishMetadata)
reload(mayaHelper)
reload(copyDialog)

from ...core.projectMetadata import ProjectMeta, AssetSpaceKeys, ProjectKeys
from ...core.publishMetadata import PublishMeta, PublishLogKeys, PUBLISH_FILE
from ...core.mayaHelper import get_MayaVersion
from ..validateWidget import ValidateWidget, ValidationKeys
from .copyDialog import CopyProgressDialog

class PublishCore(QDialog):
	def __init__(self, parent=None, project=ProjectMeta(), assetType=str, assetContainer=str, assetSpace=str, assetName=str, filePath=str):
		super(PublishCore, self).__init__(parent=parent)

		self._project = project
		self._publish = PublishMeta()
		self._assetType = assetType
		self._assetContainer = assetContainer
		self._assetSpace = assetSpace
		self._assetName = assetName
		self._workDirectory = os.path.dirname(filePath)
		self._workFile = os.path.basename(filePath)
		self._publishDirectory = self.get_publish_relativePath()
		self._publishFile = ""
		self._extension = os.path.splitext(self._workFile)[-1].lower()

	def get_AssetInformation(self):
		# ------- Group -------
		# ----------------------------------------
		asset_grp = QGroupBox("Asset Information")
		assetgrp_layout = QVBoxLayout()
		assetgrp_layout.setContentsMargins(5,5,5,5)
		assetgrp_layout.setSpacing(3)
		assetgrp_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
		

		asset_grp.setLayout(assetgrp_layout)

		# ------- Row -------
		# ----------------------------------------
		project_layout = QHBoxLayout()
		project_layout.setContentsMargins(0,0,0,0)
		project_layout.setSpacing(3)
		project_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		project_label = QLabel('Project Name:')
		project_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		project_label.setFixedWidth(100)
		project_txt = QLabel(self._project.get_ProjectName())

		project_layout.addWidget(project_label)
		project_layout.addWidget(project_txt)

		assetgrp_layout.addLayout(project_layout)

		# ------- Row -------
		# ----------------------------------------
		assetType_layout = QHBoxLayout()
		assetType_layout.setContentsMargins(0,0,0,0)
		assetType_layout.setSpacing(3)
		assetType_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetType_label = QLabel('Asset Type:')
		assetType_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		assetType_label.setFixedWidth(100)
		assetType_txt = QLabel(self._assetType)

		assetType_layout.addWidget(assetType_label)
		assetType_layout.addWidget(assetType_txt)

		assetgrp_layout.addLayout(assetType_layout)

		# ------- Row -------
		# ----------------------------------------
		assetContainer_layout = QHBoxLayout()
		assetContainer_layout.setContentsMargins(0,0,0,0)
		assetContainer_layout.setSpacing(3)
		assetContainer_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetContainer_label = QLabel('Asset Container:')
		assetContainer_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		assetContainer_label.setFixedWidth(100)
		assetContainer_txt = QLabel(self._assetContainer)

		assetContainer_layout.addWidget(assetContainer_label)
		assetContainer_layout.addWidget(assetContainer_txt)

		assetgrp_layout.addLayout(assetContainer_layout)

		# ------- Row -------
		# ----------------------------------------
		assetSpace_layout = QHBoxLayout()
		assetSpace_layout.setContentsMargins(0,0,0,0)
		assetSpace_layout.setSpacing(3)
		assetSpace_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetSpace_label = QLabel('Asset Space:')
		assetSpace_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		assetSpace_label.setFixedWidth(100)
		assetSpace_txt = QLabel(self._assetSpace)

		assetSpace_layout.addWidget(assetSpace_label)
		assetSpace_layout.addWidget(assetSpace_txt)

		assetgrp_layout.addLayout(assetSpace_layout)

		# ------- Row -------
		# ----------------------------------------
		assetName_layout = QHBoxLayout()
		assetName_layout.setContentsMargins(0,0,0,0)
		assetName_layout.setSpacing(3)
		assetName_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetName_label = QLabel('Asset Name:')
		assetName_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		assetName_label.setFixedWidth(100)
		assetName_txt = QLabel(self._assetName)

		assetName_layout.addWidget(assetName_label)
		assetName_layout.addWidget(assetName_txt)

		assetgrp_layout.addLayout(assetName_layout)

		return asset_grp

	def get_WorkInformation(self):
		asset_grp = QGroupBox("Work Asset")
		assetgrp_layout = QVBoxLayout()
		assetgrp_layout.setContentsMargins(5,5,5,5)
		assetgrp_layout.setSpacing(3)
		assetgrp_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
		
		asset_grp.setLayout(assetgrp_layout)

		# ------- Row -------
		# ----------------------------------------
		workDir_layout = QHBoxLayout()
		workDir_layout.setContentsMargins(0,0,0,0)
		workDir_layout.setSpacing(3)
		workDir_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		workDir_label = QLabel('Directory:')
		workDir_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		workDir_label.setFixedWidth(100)
		self.workDir_txt = QLabel(self._project.get_WorkDirectory())

		workDir_layout.addWidget(workDir_label)
		workDir_layout.addWidget(self.workDir_txt)

		assetgrp_layout.addLayout(workDir_layout)

		# ------- Row -------
		# ----------------------------------------
		workPath_layout = QHBoxLayout()
		workPath_layout.setContentsMargins(0,0,0,0)
		workPath_layout.setSpacing(3)
		workPath_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		workPath_label = QLabel('File Path:')
		workPath_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		workPath_label.setFixedWidth(100)
		self.workPath_txt = QLabel(self._workDirectory)

		workPath_layout.addWidget(workPath_label)
		workPath_layout.addWidget(self.workPath_txt)

		assetgrp_layout.addLayout(workPath_layout)

		# ------- Row -------
		# ----------------------------------------
		workFile_layout = QHBoxLayout()
		workFile_layout.setContentsMargins(0,0,0,0)
		workFile_layout.setSpacing(3)
		workFile_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		workFile_label = QLabel('File Name:')
		workFile_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		workFile_label.setFixedWidth(100)
		self.workFile_txt = QLabel(self._workFile)

		workFile_layout.addWidget(workFile_label)
		workFile_layout.addWidget(self.workFile_txt)

		assetgrp_layout.addLayout(workFile_layout)

		return asset_grp

	def get_PublishInformation(self):
		asset_grp = QGroupBox("Publish Asset")

		assetgrp_layout = QVBoxLayout()
		assetgrp_layout.setContentsMargins(5,5,5,5)
		assetgrp_layout.setSpacing(3)
		assetgrp_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		asset_grp.setLayout(assetgrp_layout)

		# ------- Row -------
		# ----------------------------------------
		publishDir_layout = QHBoxLayout()
		publishDir_layout.setContentsMargins(0,0,0,0)
		publishDir_layout.setSpacing(3)
		publishDir_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		publishDir_label = QLabel('Directory:')
		publishDir_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		publishDir_label.setFixedWidth(100)
		self.publishDir_txt = QLabel(self._project.get_PublishDirectory())

		publishDir_layout.addWidget(publishDir_label)
		publishDir_layout.addWidget(self.publishDir_txt)

		assetgrp_layout.addLayout(publishDir_layout)

		# ------- Row -------
		# ----------------------------------------
		publishPath_layout = QHBoxLayout()
		publishPath_layout.setContentsMargins(0,0,0,0)
		publishPath_layout.setSpacing(3)
		publishPath_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		publishPath_label = QLabel('File Path:')
		publishPath_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		publishPath_label.setFixedWidth(100)
		self.publishPath_txt = QLabel(self._publishDirectory)

		publishPath_layout.addWidget(publishPath_label)
		publishPath_layout.addWidget(self.publishPath_txt)

		assetgrp_layout.addLayout(publishPath_layout)

		# ------- Row -------
		# ----------------------------------------
		publishVariant_layout = QHBoxLayout()
		publishVariant_layout.setContentsMargins(0,0,0,0)
		publishVariant_layout.setSpacing(3)
		publishVariant_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		publishVariant_label = QLabel('Variant:')
		publishVariant_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		publishVariant_label.setFixedWidth(100)
		self.publishVariant_txt = QLabel('')

		publishVariant_layout.addWidget(publishVariant_label)
		publishVariant_layout.addWidget(self.publishVariant_txt)

		assetgrp_layout.addLayout(publishVariant_layout)

		# ------- Row -------
		# ----------------------------------------
		publishFile_layout = QHBoxLayout()
		publishFile_layout.setContentsMargins(0,0,0,0)
		publishFile_layout.setSpacing(3)
		publishFile_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		publishFile_label = QLabel('File Name:')
		publishFile_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		publishFile_label.setFixedWidth(100)
		self.publishFile_txt = QLabel(self._publishFile)

		publishFile_layout.addWidget(publishFile_label)
		publishFile_layout.addWidget(self.publishFile_txt)

		assetgrp_layout.addLayout(publishFile_layout)

		return asset_grp

	def get_PublishedVariants(self):

		# ------- Row -------
		# ----------------------------------------
		variant_layout = QHBoxLayout()
		variant_layout.setContentsMargins(0,0,0,0)
		variant_layout.setSpacing(3)
		variant_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		self.variant_list = QListWidget()

		variant_layout.addWidget(self.variant_list)

		return asset_grp

	def get_publish_relativePath(self):
		'''Get publish relative path
		
			Return: {AssetType}/{AssetContainer}/{AssetSpace}
		'''
		return os.path.join(self._assetType, self._assetContainer, self._assetSpace)

	def get_publish_directory(self):
		'''Get publish directory
		
			Return: {PublishDir}/{AssetType}/{AssetContainer}/{AssetSpace}
		'''
		return os.path.join(self._project.get_PublishDirectory(), self.get_publish_relativePath())

	def get_publishfile_path(self):
		'''Get publish file path
		
			Return: {PublishDir}/{AssetType}/{AssetContainer}/{AssetSpace}/{PublishFileName}.{Extension}
		'''
		return os.path.join(self.get_publish_directory(), self.publishFile_txt.text())

	def get_workfile_path(self):
		'''Load the Work file

			Return: {WorkDir}/{AssetType}/{AssetContainer}/{AssetSpace}/{WorkFileName}.{Extension}
		'''
		return os.path.join(self._project.get_WorkDirectory(), self._workDirectory, self._workFile)

	def load_publishFile(self):
		'''Load the Publish file
		
		'''
		pass

	def publish_asset(self):
		'''Publish the asset'''
		pass
	
	def print_logs(self):
		print (json.dumps(self._publish.get_data(), indent=4))

class PublishDialog(PublishCore):
	def __init__(self, **kw):
		super(PublishDialog, self).__init__(**kw)
		self._version = 1

		self.setFixedSize(500, 500)

		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(5,5,5,5)
		main_layout.setSpacing(5)
		main_layout.setAlignment(Qt.AlignTop)
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		main_layout.addWidget(self.get_AssetInformation())
		main_layout.addWidget(self.get_WorkInformation())
		main_layout.addWidget(self.get_PublishInformation())

		# ------- Group -------
		# ----------------------------------------
		publish_grp = QGroupBox("Publish")
		publishgrp_layout = QVBoxLayout()
		publishgrp_layout.setContentsMargins(5,5,5,5)
		publishgrp_layout.setSpacing(3)
		publishgrp_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
		

		publish_grp.setLayout(publishgrp_layout)
		main_layout.addWidget(publish_grp)

		# ------- Row -------
		# ----------------------------------------
		new_layout = QHBoxLayout()
		new_layout.setContentsMargins(0,0,0,0)
		new_layout.setSpacing(3)
		new_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		new_label = QLabel('')
		new_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		new_label.setFixedWidth(100)
		self.new_check = QCheckBox("New Variant?")

		new_layout.addWidget(new_label)
		new_layout.addWidget(self.new_check)

		publishgrp_layout.addLayout(new_layout)

		# ------- Row -------
		# ----------------------------------------
		variant_layout = QHBoxLayout()
		variant_layout.setContentsMargins(0,0,0,0)
		variant_layout.setSpacing(3)
		variant_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		variant_label = QLabel('Variant Name:')
		variant_label.setAlignment(Qt.AlignRight|Qt.AlignTop)
		variant_label.setFixedWidth(100)
		
		# Widget 1
		widget1 = QWidget()
		widget_layout = QHBoxLayout()
		widget_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
		widget_layout.setContentsMargins(0,0,0,0)
		widget_layout.setSpacing(3)
		self.variant_in = QLineEdit()
		self.variant_in.textChanged.connect(self.update_fileName)
		widget_layout.addWidget(self.variant_in)
		widget1.setLayout(widget_layout)
		# Widget 2
		self.variant_list = QListWidget()
		self.variant_list.itemClicked.connect(self.variant_Selected)

		self.stackedLayout = QStackedLayout()
		self.stackedLayout.addWidget(self.variant_list)
		self.stackedLayout.addWidget(widget1)

		frame = QFrame()
		frame.setMinimumHeight(10)
		frame.setLayout(self.stackedLayout)
		
		variant_layout.addWidget(variant_label)
		variant_layout.addWidget(frame)

		publishgrp_layout.addLayout(variant_layout)

		# ------- Row -------
		# ----------------------------------------
		user_layout = QHBoxLayout()
		user_layout.setContentsMargins(0,0,0,0)
		user_layout.setSpacing(3)
		user_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		user_label = QLabel('User:')
		user_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		user_label.setFixedWidth(100)
		self.user_in = QLineEdit()
		self.user_in.setText(getpass.getuser())

		user_layout.addWidget(user_label)
		user_layout.addWidget(self.user_in)

		publishgrp_layout.addLayout(user_layout)

		# ------- Row -------
		# ----------------------------------------
		action_layout = QHBoxLayout()
		action_layout.setContentsMargins(0,0,0,0)
		action_layout.setSpacing(3)
		action_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		publish_btn = QPushButton("Publish")
		publish_btn.clicked.connect(self.accept)
		cancel_btn = QPushButton("Cancel")
		cancel_btn.clicked.connect(self.reject)

		action_layout.addWidget(publish_btn)
		action_layout.addWidget(cancel_btn)

		main_layout.addLayout(action_layout)

		self.setWindowTitle("Publish Asset")

		self.new_check.stateChanged.connect(self.switch_stack)

		self.load_publishFile()

	def update_fileName(self, name=str):
		variant_txt = re.sub("\W",'', name)
		if variant_txt:
			var = "{Name}_{Variant}".format(Name=self._assetName, Variant=variant_txt)
			self._version = self._publish.get_variant_version(variant=var)+1
			self.publishFile_txt.setText("{Name}_{Variant}_{Version:03d}{Extention}".format(
														Name=self._assetName, 
														Variant=variant_txt, 
														Version=self._version, 
														Extention=self._extension))
			self.publishVariant_txt.setText("{Name}_{Variant}".format(
														Name=self._assetName, 
														Variant=variant_txt))
		else:
			self._version = self._publish.get_variant_version(variant=self._assetName)+1
			self.publishFile_txt.setText("{Name}_{Version:03d}{Extention}".format(
														Name=self._assetName, 
														Version=self._version, 
														Extention=self._extension))
			self.publishVariant_txt.setText(self._assetName)

	def load_publishFile(self):
		'''Load the Publish file
		
		'''
		publish_path = os.path.join(self.get_publish_directory(), PUBLISH_FILE)
		self._publish.load(directory=publish_path)
		if os.path.exists(publish_path):
			self._version = self._publish.get_variant_version(variant=self._assetName) + 1
		else:
			self._version = 1
		self.update_fileName(name="")
		self.load_variants()

	def switch_stack(self, state=bool):
		if state:
			self.stackedLayout.setCurrentIndex(1)
			self.reload_filename()
		else:
			self.stackedLayout.setCurrentIndex(0)
			self.variant_Selected()

	def variant_Selected(self):
		'''registed variant selected from ListWidget
		'''
		if self.variant_list.currentRow() >= 0:
			selected = self.variant_list.currentItem().text()
			self._version = self._publish.get_variant_version(variant=selected)+1
			self.publishFile_txt.setText("{Name}_{Version:03d}{Extention}".format(
														Name=selected, 
														Version=self._version, 
														Extention=self._extension))
			self.publishVariant_txt.setText(selected)

	def reload_filename(self):
		name = self.variant_in.text()
		self.update_fileName(name=name)

	def load_variants(self):
		variants = self._publish.get_variants()
		self.variant_list.addItems(variants)

	def get_PublishedFile(self):
		return self.publishFile_txt.text()

	def publish_asset(self):
		if os.path.exists(self._project.get_PublishDirectory()):
			publish_path = self.get_publish_directory()
			if not os.path.exists(publish_path):
				os.makedirs(publish_path)
			copyProgress = CopyProgressDialog(self, source=self.get_workfile_path(), destination=self.get_publishfile_path())
			if copyProgress.exec_() == copyProgress.Accepted:
				self._publish.create_new_log(
					username=self.user_in.text(),
					variant=self.publishVariant_txt.text(),
					workfiles=[self._workFile],
					publishfiles=[self.publishFile_txt.text()],
					app=get_MayaVersion(),
					description="Auto Publish by HandsFree")
				self._publish.set_PublishNode(
					assetType=self._assetType,
					assetContainer=self._assetContainer,
					assetSpace=self._assetSpace,
					assetName=self._assetName
				)
				# shutil.copy(self.get_workfile_path(), self.get_publishfile_path())
				self._publish.save(directory=publish_path)
				return True
		return False

class PublishGameDialog(PublishCore):
	def __init__(self, **kw):
		super(PublishGameDialog, self).__init__(**kw)
		self._assetSpace = "{}_Game".format(self._assetSpace)
		self._publishDirectory = self.get_publish_relativePath()

		self.setFixedSize(500, 500)

		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(5,5,5,5)
		main_layout.setSpacing(5)
		main_layout.setAlignment(Qt.AlignTop)
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		main_layout.addWidget(self.get_AssetInformation())
		main_layout.addWidget(self.get_WorkInformation())
		main_layout.addWidget(self.get_PublishInformation())
		# main_layout.addWidget(self.get_PublishedVariants())

		# ------- Group -------
		# ----------------------------------------
		publish_grp = QGroupBox("Publish")
		publishgrp_layout = QVBoxLayout()
		publishgrp_layout.setContentsMargins(5,5,5,5)
		publishgrp_layout.setSpacing(3)
		publishgrp_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
		

		publish_grp.setLayout(publishgrp_layout)
		main_layout.addWidget(publish_grp)

		# ------- Row -------
		# ----------------------------------------
		new_layout = QHBoxLayout()
		new_layout.setContentsMargins(0,0,0,0)
		new_layout.setSpacing(3)
		new_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		new_label = QLabel('')
		new_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		new_label.setFixedWidth(100)
		self.new_check = QCheckBox("New Variant?")

		new_layout.addWidget(new_label)
		new_layout.addWidget(self.new_check)

		publishgrp_layout.addLayout(new_layout)

		# ------- Row -------
		# ----------------------------------------
		variant_layout = QHBoxLayout()
		variant_layout.setContentsMargins(0,0,0,0)
		variant_layout.setSpacing(3)
		variant_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		variant_label = QLabel('Variant Name:')
		variant_label.setAlignment(Qt.AlignRight|Qt.AlignTop)
		variant_label.setFixedWidth(100)
		
		# Widget 1
		widget1 = QWidget()
		widget_layout = QHBoxLayout()
		widget_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
		widget_layout.setContentsMargins(0,0,0,0)
		widget_layout.setSpacing(3)
		self.variant_in = QLineEdit()
		self.variant_in.textChanged.connect(self.update_fileName)
		widget_layout.addWidget(self.variant_in)
		widget1.setLayout(widget_layout)
		# Widget 2
		self.variant_list = QListWidget()
		self.variant_list.itemClicked.connect(self.variant_Selected)

		self.stackedLayout = QStackedLayout()
		self.stackedLayout.addWidget(self.variant_list)
		self.stackedLayout.addWidget(widget1)

		frame = QFrame()
		frame.setMinimumHeight(10)
		frame.setLayout(self.stackedLayout)
		
		variant_layout.addWidget(variant_label)
		variant_layout.addWidget(frame)

		publishgrp_layout.addLayout(variant_layout)

		# ------- Row -------
		# ----------------------------------------
		user_layout = QHBoxLayout()
		user_layout.setContentsMargins(0,0,0,0)
		user_layout.setSpacing(3)
		user_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		user_label = QLabel('User:')
		user_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		user_label.setFixedWidth(100)
		self.user_in = QLineEdit()
		self.user_in.setText(getpass.getuser())

		user_layout.addWidget(user_label)
		user_layout.addWidget(self.user_in)

		publishgrp_layout.addLayout(user_layout)

		# ------- Row -------
		# ----------------------------------------
		action_layout = QHBoxLayout()
		action_layout.setContentsMargins(0,0,0,0)
		action_layout.setSpacing(3)
		action_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		publish_btn = QPushButton("Publish")
		publish_btn.clicked.connect(self.accept)
		cancel_btn = QPushButton("Cancel")
		cancel_btn.clicked.connect(self.reject)

		action_layout.addWidget(publish_btn)
		action_layout.addWidget(cancel_btn)

		main_layout.addLayout(action_layout)

		self.setWindowTitle("Publish Game Asset")

		self.new_check.stateChanged.connect(self.switch_stack)

		self.load_publishFile()

	def update_fileName(self, name=str):
		variant_txt = re.sub("\W",'', name)
		if variant_txt:
			self.publishFile_txt.setText("{Name}_{Variant}{Extention}".format(
														Name=self._assetName, 
														Variant=variant_txt,
														Extention=self._extension))
			self.publishVariant_txt.setText("{Name}_{Variant}".format(
														Name=self._assetName, 
														Variant=variant_txt))
		else:
			self.publishFile_txt.setText((self._assetName+self._extension))
			self.publishVariant_txt.setText(self._assetName)

	def load_publishFile(self):
		publish_path = os.path.join(self.get_publish_directory(), PUBLISH_FILE)
		self._publish.load(directory=publish_path)
		self.update_fileName(name="")
		self.load_variants()

	def switch_stack(self, state=bool):
		if state:
			self.stackedLayout.setCurrentIndex(1)
			self.reload_filename()
		else:
			self.stackedLayout.setCurrentIndex(0)
			self.variant_Selected()

	def variant_Selected(self):
		if self.variant_list.currentRow() >= 0:
			selected = self.variant_list.currentItem().text()
			self.publishFile_txt.setText((selected+self._extension))
			self.publishVariant_txt.setText(selected)
	
	def reload_filename(self):
		name = self.variant_in.text()
		self.update_fileName(name=name)

	def load_variants(self):
		variants = self._publish.get_variants()
		self.variant_list.addItems(variants)

	def get_PublishedFile(self):
		return self.publishFile_txt.text()

	def publish_asset(self):
		if os.path.exists(self._project.get_PublishDirectory()):
			# make sure publish path exists
			publish_path = self.get_publish_directory()
			if not os.path.exists(publish_path):
				os.makedirs(publish_path)
			# Copy publish file
			copyProgress = CopyProgressDialog(self, source=self.get_workfile_path(), destination=self.get_publishfile_path())
			if copyProgress.exec_() == copyProgress.Accepted:
				# create a new log
				self._publish.create_new_log(
					username=self.user_in.text(),
					variant=self.publishVariant_txt.text(),
					workfiles=[self._workFile],
					publishfiles=[self.publishFile_txt.text()],
					app=get_MayaVersion(),
					description="Auto Publish by HandsFree"
				)
				self._publish.set_PublishNode(
					assetType=self._assetType,
					assetContainer=self._assetContainer,
					assetSpace=self._assetSpace,
					assetName=self._assetName
				)
				# shutil.copy(self.get_workfile_path(), self.get_publishfile_path())
				# Save the info
				self._publish.save(directory=publish_path)
				return True
		return False