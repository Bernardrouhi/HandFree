import os, subprocess, re
from PySide2.QtWidgets import (QAction, QFileDialog, QListWidget, QMenu, QSizePolicy,
						  QAbstractItemView, QTableWidget,QHeaderView, QHBoxLayout,
						  QTableWidgetItem, QComboBox, QDialog, QVBoxLayout, QLabel,
						  QLineEdit, QPushButton)
from PySide2.QtGui import (QRegExpValidator)
from PySide2.QtCore import (Qt, QPoint, QRegExp)

from ...core import projectMetadata

reload(projectMetadata)

from ...core.projectMetadata import ProjectMeta, AssetSpaceKeys, ProjectKeys
from ..validateWidget import ValidateWidget, ValidationKeys

class ProjectSetupDialog(QDialog):
	def __init__(self, parent=None, ProjectName=str, WorkDirectory=str, PublishDirectory=str, AssetTypes=dict):
		super(ProjectSetupDialog, self).__init__(parent=parent)

		self._assetTypes = AssetTypes

		self.setFixedSize(500, 500)

		mainLayout = QVBoxLayout(self)
		mainLayout.setContentsMargins(5,5,5,5)
		mainLayout.setSpacing(5)
		mainLayout.setAlignment(Qt.AlignTop)
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		# ------- Row -------
		# ----------------------------------------
		projectLayout = QHBoxLayout()
		projectLayout.setContentsMargins(0,0,0,0)
		projectLayout.setSpacing(3)
		projectLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		projectlabel = QLabel('Project Name:')
		projectlabel.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		projectlabel.setFixedWidth(100)
		self.projectName_in = QLineEdit()
		self.projectName_in.setText(ProjectName)

		projectLayout.addWidget(projectlabel)
		projectLayout.addWidget(self.projectName_in)

		mainLayout.addLayout(projectLayout)

		# ------- Row -------
		# ----------------------------------------
		workLayout = QHBoxLayout()
		workLayout.setContentsMargins(0,0,0,0)
		workLayout.setSpacing(3)
		workLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		worklabel = QLabel('Work directory:')
		worklabel.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		worklabel.setFixedWidth(100)
		self.work_in = QLineEdit()
		self.work_in.setText(WorkDirectory)
		work_btn = QPushButton("Browse")
		work_btn.clicked.connect(self.pick_WorkDirectory)

		workLayout.addWidget(worklabel)
		workLayout.addWidget(self.work_in)
		workLayout.addWidget(work_btn)

		mainLayout.addLayout(workLayout)

		# ------- Row -------
		# ----------------------------------------
		publish_layout = QHBoxLayout()
		publish_layout.setContentsMargins(0,0,0,0)
		publish_layout.setSpacing(3)
		publish_layout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		publish_label = QLabel('Publish directory:')
		publish_label.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		publish_label.setFixedWidth(100)
		self.publish_in = QLineEdit()
		self.publish_in.setText(PublishDirectory)
		publish_btn = QPushButton("Browse")
		publish_btn.clicked.connect(self.pick_PublishDirectory)

		publish_layout.addWidget(publish_label)
		publish_layout.addWidget(self.publish_in)
		publish_layout.addWidget(publish_btn)

		mainLayout.addLayout(publish_layout)

		# ------- Row -------
		# ----------------------------------------
		assetTypeLayout = QHBoxLayout()
		assetTypeLayout.setContentsMargins(0,0,0,0)
		assetTypeLayout.setSpacing(3)
		assetTypeLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetTypelabel = QLabel('Asset Types:')
		assetTypelabel.setAlignment(Qt.AlignRight|Qt.AlignTop)
		assetTypelabel.setFixedWidth(100)
		self.assetType_list = QListWidget()
		self.assetType_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.assetType_list.setContextMenuPolicy(Qt.CustomContextMenu)
		self.assetType_list.customContextMenuRequested.connect(self.assetTypeMenu)
		# self.assetType_list.itemClicked.connect(self.assetType_Selected)
		self.assetType_list.itemSelectionChanged.connect(self.assetType_Selected)

		assetTypeLayout.addWidget(assetTypelabel)
		assetTypeLayout.addWidget(self.assetType_list)

		mainLayout.addLayout(assetTypeLayout)

		# ------- Row -------
		# ----------------------------------------
		assetTypeEditLayout = QHBoxLayout()
		assetTypeEditLayout.setContentsMargins(0,0,0,0)
		assetTypeEditLayout.setSpacing(3)
		assetTypeEditLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetTypelabel = QLabel('AssetType Name:')
		assetTypelabel.setAlignment(Qt.AlignRight|Qt.AlignCenter)
		assetTypelabel.setFixedWidth(100)
		self.assetType_in = QLineEdit()
		# self.assetType_in.setValidator(QRegExpValidator(QRegExp(r"^(\w){15}")))
		self.assetType_in.editingFinished.connect(self.assetType_Edit)
		self.assetType_in.textChanged.connect(self.assetTypeName_Check)
		self.assetTypeValidator = ValidateWidget()

		assetTypeEditLayout.addWidget(assetTypelabel)
		assetTypeEditLayout.addWidget(self.assetType_in)
		assetTypeEditLayout.addWidget(self.assetTypeValidator)

		mainLayout.addLayout(assetTypeEditLayout)

		# ------- Row -------
		# ----------------------------------------
		assetSpaceLayout = QHBoxLayout()
		assetSpaceLayout.setContentsMargins(0,0,0,0)
		assetSpaceLayout.setSpacing(3)
		assetSpaceLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetSpacelabel = QLabel('AssetSpace List:')
		assetSpacelabel.setAlignment(Qt.AlignRight|Qt.AlignTop)
		assetSpacelabel.setFixedWidth(100)
		self.assetSpace_columns = ['AssetSpace', 'Workspace']
		self.assetSpace_table = AssetSpaceTable(0,len(self.assetSpace_columns))
		self.assetSpace_table.setHorizontalHeaderLabels(self.assetSpace_columns)
		self.assetSpace_table.cellChanged.connect(self.assetSpace_CellChanged)
		# Style
		assetSpace_VH = self.assetSpace_table.verticalHeader()
		assetSpace_VH.hide()
		assetSpace_VH = self.assetSpace_table.horizontalHeader()
		assetSpace_VH.setSectionResizeMode(0, QHeaderView.Stretch)
		assetSpace_VH.setSectionResizeMode(1, QHeaderView.Fixed)
		self.assetSpace_table.setContextMenuPolicy(Qt.CustomContextMenu)
		
		self.assetSpace_table.customContextMenuRequested.connect(self.assetSpaceMenu)

		assetSpaceLayout.addWidget(assetSpacelabel)
		assetSpaceLayout.addWidget(self.assetSpace_table)

		mainLayout.addLayout(assetSpaceLayout)

		# ------- Row -------
		# ----------------------------------------
		actionLayout = QHBoxLayout()
		actionLayout.setContentsMargins(0,0,0,0)
		actionLayout.setSpacing(3)
		actionLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		ok_btn = QPushButton("Store")
		ok_btn.clicked.connect(self.accept)
		cancel_btn = QPushButton("Cancel")
		cancel_btn.clicked.connect(self.reject)

		actionLayout.addWidget(ok_btn)
		actionLayout.addWidget(cancel_btn)

		mainLayout.addLayout(actionLayout)

		self.setWindowTitle("Setup Project")

		self.reload_assetTypes()

	def assetTypeMenu(self, point=QPoint):
		self.assetTMenu = QMenu()
		# directory
		add_action = QAction("Add Asset Type", self)
		add_action.setStatusTip('Add new asset type to the project.')
		add_action.triggered.connect(self.new_asseType)
		self.assetTMenu.addAction(add_action)

		remove_action = QAction("Remove Asset Type", self)
		remove_action.setStatusTip('Remove the selected asset type with it settings from project.')
		remove_action.triggered.connect(self.remove_assetType)
		self.assetTMenu.addAction(remove_action)

		self.assetTMenu.addSeparator()

		browse_action = QAction("Browse Folder", self)
		browse_action.setStatusTip('Browse into assetType directory.')
		browse_action.triggered.connect(self.browse_assetType_directory)
		self.assetTMenu.addAction(browse_action)

		self.assetTMenu.addSeparator()

		createAll_action = QAction("Create Selected Folder", self)
		createAll_action.setStatusTip('Create all the asset type folders')
		createAll_action.triggered.connect(self.create_assetType_folder)
		self.assetTMenu.addAction(createAll_action)

		create_action = QAction("Create All Folders", self)
		create_action.setStatusTip('Create all the asset type folders')
		create_action.triggered.connect(self.create_assetTypes_folder)
		self.assetTMenu.addAction(create_action)

		self.assetTMenu.move(self.assetType_list.viewport().mapToGlobal(point))
		self.assetTMenu.show()

	def new_asseType(self):
		'''Create a new asset type'''
		assetTypeNames = self._assetTypes.keys()
		# extract numbers from assetTypes
		numbers = list()
		for each in assetTypeNames:
			numbers += re.findall(r'\d+', each)
		numbers = [int(s) for s in numbers]
		assetNumber = (max(numbers)+1) if numbers else 0

		newAssetTypeName = "NewAssetType_{:02d}".format(assetNumber)
		self.assetType_list.addItem(newAssetTypeName)
		self._assetTypes[newAssetTypeName] = list()
	
	def remove_assetType(self):
		'''Remove the asset type'''
		if self.assetType_list.currentRow() >= 0 :
			del self._assetTypes[self.assetType_list.currentItem().text()]
			self.assetType_list.takeItem(self.assetType_list.currentRow())

	def browse_assetType_directory(self):
		'''Browse into AssetType Folder'''
		if self.assetType_list.currentRow() >= 0 :
			assetTypeName  = self.assetType_list.currentItem().text()
			workDirectory = os.path.normpath(self.work_in.text())
			if os.path.isdir(workDirectory):
				assetTypePath = os.path.normpath(os.path.join(workDirectory,assetTypeName))
				if os.path.isdir(assetTypePath):
					subprocess.Popen(r'explorer /select,"{path}"'.format(path=assetTypePath))
				else:
					print ("AssetType is not created.")
			else:
				print ("Work directory doesn't exists.")
		else:
			print ("AssetType is no selected.")

	def create_assetType_folder(self):
		'''Create selected assetType folder'''
		if self.assetType_list.currentRow() >= 0 :
			assetTypeName  = self.assetType_list.currentItem().text()
			workDirectory = os.path.normpath(self.work_in.text())
			if os.path.isdir(workDirectory):
				assetTypePath = os.path.normpath(os.path.join(workDirectory,assetTypeName))
				# Make directory if doesn't exists
				if not os.path.isdir(assetTypePath):
					os.makedirs(assetTypePath)

	def create_assetTypes_folder(self):
		'''Create all assetType folders'''
		workDirectory = os.path.normpath(self.work_in.text())
		if os.path.isdir(workDirectory):
			for index in range(self.assetType_list.count()):
				assetTypeName = self.assetType_list.item(index).data(0)
				assetTypePath = os.path.normpath(os.path.join(workDirectory,assetTypeName))
				# Make directory if doesn't exists
				if not os.path.isdir(assetTypePath):
					os.makedirs(assetTypePath)

	def assetType_Selected(self):
		if self.assetType_list.currentRow() >= 0 :
			selected_assetType = self.assetType_list.currentItem().text()
			# Update the edit view
			self.assetType_in.setText(selected_assetType)
			self.assetSpace_table.setRowCount(0)
			for assetTypeData in self._assetTypes[selected_assetType]:
				assetSpace = assetTypeData[ProjectKeys.AssetSpace]
				workSpace = assetTypeData[ProjectKeys.WorkSpace]
				self.create_AssetSpace(name=assetSpace, workspace=workSpace)

	def assetType_Edit(self):
		'''On editing the assetType name'''
		if self.assetType_list.currentRow() >= 0 :
			result = self.assetTypeValidator.get_status()
			if result != ValidationKeys.Valid:
				self.assetType_in.setText(self.assetType_list.currentItem().text())
			else:
				# Collect Data
				old_AssetTypeName = self.assetType_list.currentItem().text()
				new_AssetTypeName = self.assetType_in.text()
				# Change Backend
				if new_AssetTypeName != old_AssetTypeName:
					self._assetTypes[new_AssetTypeName] = self.get_assetSpace_data()
					del self._assetTypes[old_AssetTypeName]
					# Change View
					self.assetType_list.currentItem().setText(new_AssetTypeName)

	def assetTypeName_Check(self, text=str):
		'''Check the assetType name and confirm it uniqueness'''
		if self.assetType_list.currentRow() >= 0 :
			entered_text = str(text)
			if text:
				assetTypeList = self._assetTypes.keys()
				assetTypeList.remove(self.assetType_list.currentItem().text())
				if text not in assetTypeList:
					self.assetTypeValidator.set_Valid()
				else:
					self.assetTypeValidator.set_Invalid()
			else:
				self.assetTypeValidator.set_Invalid()

	def assetSpaceMenu(self, point=QPoint):
		'''AssetSapce custom Menu'''
		self.assetSMenu = QMenu()
		# directory
		add_action = QAction("Create AssetSpace", self)
		add_action.setStatusTip('Add a new AssetSpace to the AssetType.')
		add_action.triggered.connect(self.new_AssetSpace)
		self.assetSMenu.addAction(add_action)

		remove_action = QAction("Remove AssetSpace", self)
		remove_action.setStatusTip('Remove the selected AssetSpace from AssetType.')
		remove_action.triggered.connect(self.remove_AssetSpace)
		self.assetSMenu.addAction(remove_action)

		self.assetSMenu.move(self.assetSpace_table.viewport().mapToGlobal(point))
		self.assetSMenu.show()

	def assetSpace_CellChanged(self, row=int, column=int):
		if self.assetType_list.currentRow() >= 0 :
			assetTypeName = self.assetType_list.currentItem().text()
			data = self._assetTypes[assetTypeName][row]
			# AssetSpace Name
			if column == 0:
				assetSpaceData = self.assetSpace_table.item(row, column).text()
				data[ProjectKeys.AssetSpace] = assetSpaceData
			# AssetSpace Workspace 
			elif column == 1:
				assetSpaceData = self.assetSpace_table.cellWidget(row, column).currentText()
				data[ProjectKeys.WorkSpace] = assetSpaceData
			# print("Updated [row:{0},column:{1}]".format(row,column))

	def reload_assetTypes(self):
		assetTypes = self._assetTypes.keys()
		self.assetType_list.addItems(assetTypes)
		self.assetType_list.sortItems(order=Qt.AscendingOrder)

	def get_assetSpace_data(self):
		'''Get all assetSpace data'''
		data = list()
		for eachRowNum in range(0,self.assetSpace_table.rowCount()):
			assetSpaceName = self.assetSpace_table.item(eachRowNum, 0)
			assetSpaceWorkspace = self.assetSpace_table.cellWidget(eachRowNum, 1)
			# Get AssetSpace MetaData
			rawData = ProjectMeta().ASSETSPACE_METADATA().copy()
			rawData[ProjectKeys.AssetSpace] = assetSpaceName.text()
			rawData[ProjectKeys.WorkSpace] = assetSpaceWorkspace.currentText()
			data.append(rawData)
		return data

	def get_ProjectName(self):
		'''Get Project Name'''
		return self.projectName_in.text()

	def get_WorkDirectory(self):
		'''Get WorkDirectory'''
		return self.work_in.text()

	def get_PublishDirectory(self):
		'''Get WorkDirectory'''
		return self.publish_in.text()

	def get_AssetTypes(self):
		return self._assetTypes

	def pick_WorkDirectory(self):
		'''Pick Work Directory'''
		work_Dir = QFileDialog.getExistingDirectory(self,"Pick Work Directory Folder",self.work_in.text())
		if work_Dir:
			self.work_in.setText(os.path.normpath(work_Dir))

	def pick_PublishDirectory(self):
		'''Pick Publish Directory'''
		publish_dir = QFileDialog.getExistingDirectory(self,"Pick Publish Directory Folder",self.publish_in.text())
		if publish_dir:
			self.publish_in.setText(os.path.normpath(publish_dir))

	def new_AssetSpace(self):
		if self.assetType_list.currentRow() >= 0 :
			assetTypeName = self.assetType_list.currentItem().text()
			name = "New"
			workspace = AssetSpaceKeys().Empty
			# register the data
			newAssetSpace = ProjectMeta().ASSETSPACE_METADATA().copy()
			newAssetSpace[ProjectKeys.AssetSpace] = name
			newAssetSpace[ProjectKeys.WorkSpace] = workspace
			self._assetTypes[assetTypeName].append(newAssetSpace)
			self.create_AssetSpace(name=name, workspace=workspace)

	def remove_AssetSpace(self):
		if self.assetType_list.currentRow() >= 0 :
			assetTypeName = self.assetType_list.currentItem().text()
			rows = list()
			for eachcell in self.assetSpace_table.selectedIndexes():
				rows.append(eachcell.row())
			rows = list(dict.fromkeys(rows))
			rows.sort(reverse=True)

			for row in rows:
				self._assetTypes[assetTypeName].pop(row)
				self.assetSpace_table.removeRow(row)

	def create_AssetSpace(self, name=str, workspace=str):
		if self.assetType_list.currentRow() >= 0 :
			# creating QTableWidgetItem
			column_01 = QTableWidgetItem()
			column_01.setText(name)
			
			option_list = [
				AssetSpaceKeys().Empty,
				AssetSpaceKeys().Maya,
				AssetSpaceKeys().SusbtancePainter
			]
			column_combo = QComboBox()
			column_combo.addItems(option_list)
			if workspace in option_list:
				column_combo.setCurrentIndex(column_combo.findText(workspace))
			column_combo.currentIndexChanged.connect(self.assetSpace_ComboIndexChanged)
			index = self.assetSpace_table.rowCount()
			self.assetSpace_table.insertRow(index)

			self.assetSpace_table.setItem(index, 0, column_01)
			self.assetSpace_table.setCellWidget(index, 1, column_combo)

	def assetSpace_ComboIndexChanged(self, index=int):
		if self.assetType_list.currentRow() >= 0 :
			workspaceName = self.sender().currentText()
			assetSpace_cell = self.assetSpace_table.currentIndex()
			self.assetSpace_CellChanged(row=assetSpace_cell.row(), column=assetSpace_cell.column())

class AssetSpaceTable(QTableWidget):
    def __init__(self, parent = None, *args, **kwargs):
        super(AssetSpaceTable, self).__init__(parent, *args, **kwargs)
 
        rowHeight = self.fontMetrics().height()
        self.verticalHeader().setDefaultSectionSize(rowHeight)
