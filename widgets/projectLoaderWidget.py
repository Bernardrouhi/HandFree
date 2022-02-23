import os, subprocess
from PySide2.QtWidgets import (QWidget, QComboBox, QVBoxLayout, QHBoxLayout,
								QSizePolicy, QLabel, QLineEdit, QSpacerItem,
								QListView, QMenu, QPushButton, QDialog, QGridLayout,
								QAction, QFileSystemModel, QAbstractItemView,
								QTreeView, QListWidget, QSpinBox, QTreeView)
from PySide2.QtGui import (QStandardItemModel, QStandardItem, QMouseEvent)
from PySide2.QtCore import (Qt, Signal, QEvent, QPoint, QSortFilterProxyModel,
							QItemSelection, QDir, QModelIndex)

from  ..core import pipeline_handler, mayaHelper, projectMetaData

reload(mayaHelper)
reload(pipeline_handler)

from ..core.pipeline_handler import Pipeline
from ..core.mayaHelper import (open_scene, set_MayaProject, create_EmptyScene,
								copy_workspace, get_workspaceName, save_Scene,
								rename_Scene,reference_FileToScene, import_FileToScene)
from ..core.projectMetaData import ProjectMeta, ProjectKeys, AssetSpaceKeys

class AssetLoaderWidget(QWidget):
	'''Manage project assets'''
	onUpdate = Signal()
	def __init__(self, parent=None, edit=bool(False), project=ProjectMeta()):
		super(AssetLoaderWidget, self).__init__(parent)

		self._edit = edit
		self._project = project
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
		assetTypeLayout = QHBoxLayout()
		assetTypeLayout.setContentsMargins(0,0,0,0)
		assetTypeLayout.setSpacing(3)
		assetTypeLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetTypeLabel = QLabel("Asset Type:")
		assetTypeLabel.setFixedWidth(65)
		assetTypeLabel.setAlignment(Qt.AlignTop|Qt.AlignRight)
		self.assetType_combo = QComboBox()
		self.assetType_combo.currentIndexChanged.connect(self.assetType_IndexChanged)
		self.assetType_combo.setFixedWidth(150)

		assetTypeLayout.addWidget(assetTypeLabel)
		assetTypeLayout.addWidget(self.assetType_combo)

		main_layout.addLayout(assetTypeLayout)
		# ------- Row -------
		# ----------------------------------------
		assetSpaceLayout = QHBoxLayout()
		assetSpaceLayout.setContentsMargins(0,0,0,0)
		assetSpaceLayout.setSpacing(3)
		assetSpaceLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetSpaceLabel = QLabel("Asset Space:")
		assetSpaceLabel.setFixedWidth(65)
		assetSpaceLabel.setAlignment(Qt.AlignTop|Qt.AlignRight)
		self.assetSpace_combo = QComboBox()
		self.assetSpace_combo.setFixedWidth(150)
		self.assetSpace_combo.currentIndexChanged.connect(self.assetSpace_IndexChanged)

		assetSpaceLayout.addWidget(assetSpaceLabel)
		assetSpaceLayout.addWidget(self.assetSpace_combo)

		main_layout.addLayout(assetSpaceLayout)

		# ------- Row -------
		# ----------------------------------------
		assetsLayout = QHBoxLayout()
		assetsLayout.setContentsMargins(0,0,0,0)
		assetsLayout.setSpacing(3)
		assetsLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetLabel = QLabel("")
		assetLabel.setFixedWidth(65)
		assetLabel.setAlignment(Qt.AlignTop|Qt.AlignRight)
		self.asset_search = QLineEdit()
		self.asset_search.textChanged.connect(self.filter_AssetContainer)
		asset_btn = QPushButton("New")
		asset_btn.clicked.connect(self.show_AssetCreationDialog)
		asset_btn.setVisible(self._edit)

		assetsLayout.addWidget(assetLabel)
		assetsLayout.addWidget(self.asset_search)
		assetsLayout.addWidget(asset_btn)

		main_layout.addLayout(assetsLayout)

		# ------- Row -------
		# ----------------------------------------
		assetslistLayout = QHBoxLayout()
		assetslistLayout.setContentsMargins(0,0,0,0)
		assetslistLayout.setSpacing(3)
		assetslistLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetSpacer = QLabel("Asset Name:")
		assetSpacer.setFixedWidth(65)
		assetSpacer.setAlignment(Qt.AlignTop|Qt.AlignRight)
		self.assetContainer_list = AssetTreeView()
		self.assetContainer_list.setHeaderHidden(True)
		self.assetContainer_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.assetContainer_list.setContextMenuPolicy(Qt.CustomContextMenu)
		self.assetContainer_list.customContextMenuRequested.connect(self.assetMenu)
		self.assetContainer_model = QStandardItemModel()
		self.assetContainer_filter = QSortFilterProxyModel()
		self.assetContainer_filter.setSourceModel(self.assetContainer_model)
		self.assetContainer_filter.setRecursiveFilteringEnabled(True)
		self.assetContainer_list.setModel(self.assetContainer_filter)

		self.assetContainer_list.selectionModel().selectionChanged.connect(self.asset_selectionChanged)

		assetslistLayout.addWidget(assetSpacer)
		assetslistLayout.addWidget(self.assetContainer_list)

		main_layout.addLayout(assetslistLayout)

		# ------- Row -------
		# ----------------------------------------
		directoryLayout = QHBoxLayout()
		directoryLayout.setContentsMargins(0,0,0,0)
		directoryLayout.setSpacing(3)
		directoryLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		directoryLabel = QLabel("Directory:")
		directoryLabel.setFixedWidth(65)
		directoryLabel.setAlignment(Qt.AlignTop|Qt.AlignRight)
		self.assetSpace_list = AssetTreeView()
		# self.assetSpace_list.setSelectionMode(QAbstractItemView.SingleSelection)
		self.assetSpace_list.setContextMenuPolicy(Qt.CustomContextMenu)
		self.assetSpace_list.customContextMenuRequested.connect(self.assetSpaceMenu)
		self.assetSpace_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

		self.assetSpace_model = QStandardItemModel()

		self.assetSpace_filter = QSortFilterProxyModel()
		self.assetSpace_filter.setSourceModel(self.assetSpace_model)

		self.assetSpace_list.setModel(self.assetSpace_filter)
		self.assetSpace_list.OnDoubleClick.connect(self.assetSpace_doubleclicked)

		directoryLayout.addWidget(directoryLabel)
		directoryLayout.addWidget(self.assetSpace_list)

		main_layout.addLayout(directoryLayout)

		# ------- Row -------
		# ----------------------------------------
		actionLayout = QHBoxLayout()
		actionLayout.setContentsMargins(0,0,0,0)
		actionLayout.setSpacing(3)
		actionLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		save_btn = QPushButton("Save")
		save_btn.setStatusTip("Save the current scene")
		save_btn.clicked.connect(self.save_file)
		savePlus_btn = QPushButton("Save+")
		savePlus_btn.setStatusTip("Save the current scene with a new version")
		savePlus_btn.clicked.connect(self.saveplus_file)
		publish_btn = QPushButton("Publish")
		publish_btn.setStatusTip("Publish the current scene")
		publish_btn.clicked.connect(self.publish_file)

		actionLayout.addWidget(save_btn)
		actionLayout.addWidget(savePlus_btn)
		actionLayout.addWidget(publish_btn)

		main_layout.addLayout(actionLayout)

		self.reload_assetTypes()

	def show_AssetCreationDialog(self):
		assetTypeDialog = Asset_Dialog(title = "New Asset Name")
		if assetTypeDialog.exec_() == QDialog.Accepted:
			assetContainer = assetTypeDialog.AssetContainer
			assetTypeName = self.assetType_combo.currentText()
			self.create_New_AssetContainer(assetContainer=assetContainer, assetTypeName=assetTypeName)
			self.reload_assetContainerList()

	def create_New_AssetContainer(self, assetContainer=str, assetTypeName=str):
		'''Creating a new Asset'''
		# workfile directory
		workDir = self._project.get_WorkDirectory()
		assetTypeDir = os.path.normpath(os.path.join(workDir,assetTypeName))
		if os.path.isdir(assetTypeDir):
			assetTypes = self._project.get_AssetTypes()
			assetSpaces = assetTypes[assetTypeName]
			assetPath = os.path.normpath(os.path.join(assetTypeDir,assetContainer))
			for assetData in assetSpaces:
				workspace = assetData[ProjectKeys.WorkSpace]
				assetSpace = assetData[ProjectKeys.AssetSpace]
				# Final Path
				assetSpace = os.path.normpath(os.path.join(assetPath,assetSpace))
				if not os.path.exists(assetSpace):
					os.makedirs(assetSpace)
				if workspace == AssetSpaceKeys.Maya:
					copy_workspace(destination=assetSpace)
			print(assetPath)

	def assetType_IndexChanged(self, Index=int):
		self.reload_assetSpace()

	def assetSpace_IndexChanged(self, Index=int):
		self.reload_assetContainerList()
		self.reload_assetWorkspaceList()

	def assetMenu(self, point=QPoint):
		if self.assetContainer_list.selectedIndexes():
			self.assetTMenu = QMenu()

			browse_action = QAction("Browse Folder", self)
			browse_action.setStatusTip('Browse into asset directory.')
			browse_action.triggered.connect(self.browse_asset_directory)
			self.assetTMenu.addAction(browse_action)

			fix_action = QAction("Fix AssetSpace", self)
			fix_action.setStatusTip('Check/fix missing AssetSpace and workspace.')
			fix_action.triggered.connect(self.fix_assetSpace)
			self.assetTMenu.addAction(fix_action)

			self.assetTMenu.move(self.assetContainer_list.viewport().mapToGlobal(point))
			self.assetTMenu.show()

	def browse_asset_directory(self):
		'''Browse into Asset Folder'''
		assetTypeName  = self.assetType_combo.currentText()
		workDirectory = self._project.get_WorkDirectory()
		if os.path.isdir(workDirectory):
			assetContainer = self.get_selectedAssetContainer()
			assetTypePath = os.path.normpath(os.path.join(workDirectory,assetTypeName,assetContainer,""))
			if os.path.isdir(assetTypePath):
				subprocess.Popen(r'explorer /select,"{path}"'.format(path=assetTypePath))

	def fix_assetSpace(self):
		assetTypeName  = self.assetType_combo.currentText()
		workDirectory = self._project.get_WorkDirectory()
		assetSpaceName = self.assetSpace_combo.currentText()
		if os.path.isdir(workDirectory):
			itemModel = self.get_selectedAssetContainerItem()
			if itemModel and not itemModel.hasChildren():
				assetContainer = self.get_selectedAssetContainer()
				self.create_New_AssetContainer(assetContainer=assetContainer,assetTypeName=assetTypeName)
				print("Done")
				self.reload_assetWorkspaceList()

	def assetSpaceMenu(self, point=QPoint):
		if self.assetSpace_list.currentIndex().row() >= 0:
			# selected file
			fileName = self.assetSpace_list.currentIndex().data()

			self.newMenu = QMenu()
			if fileName.lower().endswith(".ma") or fileName.lower().endswith(".mb"):

				open_action = QAction("Open scene", self)
				open_action.setStatusTip('Open the scene file.')
				open_action.triggered.connect(self.open_file)
				self.newMenu.addAction(open_action)

				self.newMenu.addSeparator()
			save_action = QAction("Save+ Current Scene into", self)
			save_action.setStatusTip('Save the current scene into selected asset with new version.')
			save_action.triggered.connect(self.external_save)
			self.newMenu.addAction(save_action)

			if fileName.lower().endswith(".ma") or fileName.lower().endswith(".mb"):
				publish_action = QAction("Publish the file", self)
				publish_action.setStatusTip('Publish the selected scene.')
				publish_action.triggered.connect(self.publish_file)
				self.newMenu.addAction(publish_action)

				self.newMenu.addSeparator()

				reference_action = QAction("Create Reference", self)
				reference_action.setStatusTip('Create a reference of this file in the scene.')
				reference_action.triggered.connect(self.reference_file)
				self.newMenu.addAction(reference_action)

				import_action = QAction("Import to...", self)
				import_action.setStatusTip('Import the file into the scene.')
				import_action.triggered.connect(self.import_file)
				self.newMenu.addAction(import_action)

			self.newMenu.addSeparator()

			# directory
			new_action = QAction("Create a new Scene", self)
			new_action.setStatusTip('Create a new scene.')
			new_action.triggered.connect(self.create_scene)
			self.newMenu.addAction(new_action)

			# directory
			opendir_action = QAction("Show in Explorer", self)
			opendir_action.setStatusTip('Open the directory in explorer.')
			opendir_action.triggered.connect(self.browse_workspace_file)
			self.newMenu.addAction(opendir_action)

			self.newMenu.move(self.assetSpace_list.viewport().mapToGlobal(point))
			self.newMenu.show()

	def reference_file(self):
		workdir = Pipeline().get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.assetSpace_combo.currentText()
		assetContainer = self.get_selectedAssetContainer()
		fileName = self.assetSpace_list.currentIndex().data()
		
		file_path = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace,fileName))
		raw_name, extension = os.path.splitext(fileName)
		reference_FileToScene(file_path=file_path, namespace=raw_name)

	def import_file(self):
		workdir = Pipeline().get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.assetSpace_combo.currentText()
		assetContainer = self.get_selectedAssetContainer()
		fileName = self.assetSpace_list.currentIndex().data()

		file_path = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace,fileName))
		raw_name, extension = os.path.splitext(fileName)
		import_FileToScene(file_path=file_path, namespace=raw_name)

	def open_file(self):
		workdir = Pipeline().get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.assetSpace_combo.currentText()
		assetContainer = self.get_selectedAssetContainer()
		assetName = self.assetContainer_list.currentIndex().data()
		fileName = self.assetSpace_list.currentIndex().data()

		dirPath = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace))
		filePath = os.path.normpath(os.path.join(dirPath,fileName))

		set_MayaProject(directory=dirPath)
		open_scene(scene_path=filePath)
		Pipeline().set_AssetType(assetType)
		Pipeline().set_AssetContainer(assetContainer)
		Pipeline().set_AssetSpace(assetSpace)
		Pipeline().set_AssetName(assetName)
		self.onUpdate.emit()
		
	def external_save(self):
		workdir = self._project.get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.assetSpace_combo.currentText()
		assetContainer = self.get_selectedAssetContainer()
		assetName = self.assetContainer_list.currentIndex().data()

		dirPath = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace))
		print(dirPath)

		all_files = os.walk(dirPath).next()[2]
		nameTemp = "{}_".format(assetName)
		versions = list()
		for each in all_files:
			if each.startswith(nameTemp):
				raw_name, extension = os.path.splitext(each)
				extra = raw_name.replace(nameTemp,"")
				if extra.isdigit():
					versions.append(int(extra))
		if versions:
			newVersion = max(versions)+1
		else:
			newVersion = 1
		newFileName = "{}_{:03d}".format(assetName,newVersion)

		set_MayaProject(directory=dirPath)
		rename_Scene(name="{}.ma".format(newFileName))
		save_Scene()

		Pipeline().set_AssetType(assetType)
		Pipeline().set_AssetContainer(assetContainer)
		Pipeline().set_AssetSpace(assetSpace)
		Pipeline().set_AssetName(assetName)
		self.onUpdate.emit()
		self.reload_assetWorkspaceList()

	def publish_file(self):
		print("not implemented yet!!")

	def save_file(self):
		save_Scene()

	def saveplus_file(self):
		workdir = self._project.get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.assetSpace_combo.currentText()
		assetContainer = self.get_selectedAssetContainer()

		if workdir and assetType and assetSpace and assetContainer:
			dirPath = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace))
			if os.path.isdir(dirPath):
				assetName = self.assetContainer_list.currentIndex().data()
				index = self.assetSpace_filter.mapToSource(self.assetSpace_list.currentIndex())
				file_path = self.assetSpace_model.filePath(index)
				print(os.path.basename(file_path))


				all_files = os.walk(dirPath).next()[2]
				nameTemp = "{}_".format(assetName)
				versions = list()
				for each in all_files:
					if each.startswith(nameTemp):
						raw_name, extension = os.path.splitext(each)
						extra = raw_name.replace(nameTemp,"")
						if extra.isdigit():
							versions.append(int(extra))
				if versions:
					newVersion = max(versions)+1
				else:
					newVersion = 1
				newFileName = "{}_{:03d}".format(assetName,newVersion)

				set_MayaProject(directory=dirPath)
				rename_Scene(name="{}.ma".format(newFileName))
				save_Scene()

				Pipeline().set_AssetType(assetType)
				Pipeline().set_AssetContainer(assetContainer)
				Pipeline().set_AssetSpace(assetSpace)
				Pipeline().set_AssetName(assetName)
				self.onUpdate.emit()
				self.reload_assetWorkspaceList()

	def assetSpace_doubleclicked(self):
		fileName = self.assetSpace_list.currentIndex().data()
		if fileName.lower().endswith(".ma"):
			self.open_file()

	def create_scene(self):
		workdir = self._project.get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.assetSpace_combo.currentText()
		assetContainer = self.get_selectedAssetContainer()
		assetName = self.assetContainer_list.currentIndex().data()

		dirPath = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace))
		print(dirPath)

		all_files = os.walk(dirPath).next()[2]
		nameTemp = "{}_".format(assetName)
		versions = list()
		for each in all_files:
			if each.startswith(nameTemp):
				raw_name, extension = os.path.splitext(each)
				extra = raw_name.replace(nameTemp,"")
				if extra.isdigit():
					versions.append(int(extra))
		if versions:
			newVersion = max(versions)+1
		else:
			newVersion = 1
		newFileName = "{}_{:03d}".format(assetName,newVersion)

		create_EmptyScene()
		set_MayaProject(directory=dirPath)
		rename_Scene(name="{}.ma".format(newFileName))
		save_Scene()

		Pipeline().set_AssetType(assetType)
		Pipeline().set_AssetContainer(assetContainer)
		Pipeline().set_AssetSpace(assetSpace)
		Pipeline().set_AssetName(assetName)
		self.onUpdate.emit()
		self.reload_assetWorkspaceList()

	def browse_workspace_file(self):
		workdir = Pipeline().get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.assetSpace_combo.currentText()
		assetContainer = self.get_selectedAssetContainer()

		dirPath = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace))

		assetName = self.assetSpace_list.currentIndex().data()

		filePath = os.path.normpath(os.path.join(dirPath,assetName))
		print(filePath)
		subprocess.Popen(r'explorer /select,"{path}"'.format(path=filePath))

	def asset_selectionChanged(self, index=QItemSelection()):
		self.reload_assetWorkspaceList()
		
	def reload_assetWorkspaceList(self):
		itemModel = self.get_selectedAssetContainerItem()
		if itemModel and not itemModel.hasChildren():
			assetContainer = self.get_selectedAssetContainer()
			workdir = Pipeline().get_WorkDirectory()
			assetType = self.assetType_combo.currentText()
			assetSpace = self.assetSpace_combo.currentText()
			assetPath = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace))
			if os.path.isdir(assetPath):
				self.assetSpace_model = QFileSystemModel()
				# self.assetSpace_model.setFilter(QDir.NoDotAndDotDot | QDir.Dirs)
				self.assetSpace_filter.setSourceModel(self.assetSpace_model)
				# self.assetSpace_filter.setFilterRegExp(r"^([^.])$")
				self.assetSpace_list.setModel(self.assetSpace_filter)
				self.assetSpace_list.setRootIndex(self.assetSpace_filter.mapFromSource(self.assetSpace_model.setRootPath(assetPath)))
				self.assetSpace_list.hideColumn(1)
				self.assetSpace_list.hideColumn(2)
				self.assetSpace_list.hideColumn(3)
				self.assetSpace_list.setHeaderHidden(True)
		else:
			self.assetSpace_model = QStandardItemModel()
			self.assetSpace_list.setModel(self.assetSpace_model)

	def get_selectedAssetContainerItem(self):
		'''get selected QStandardItem

			Return:
				(QStandardItem): True if exists, otherwise False.
		'''
		currentAssetIndex = self.assetContainer_list.currentIndex()
		source_index = self.assetContainer_filter.mapToSource(currentAssetIndex)
		return self.assetContainer_model.itemFromIndex(source_index)

	def get_selectedAssetContainer(self):
		'''get select asset path'''
		def collect_name(item=QStandardItem):
			item_parent = item.parent()
			if item_parent:
				name = item.text()
				return os.path.normpath(os.path.join(collect_name(item=item_parent), name))
			else:
				return item.text()
		itemModel = self.get_selectedAssetContainerItem()
		return collect_name(item=itemModel)
		
	def reload_assetTypes(self):
		'''Reload the Asset Type'''
		if self._project:
			self.assetType_combo.clear()
			# get Categories
			assetType_dir = self._project.get_WorkDirectory()
			if os.path.isdir(assetType_dir):
				AssetTypes = self._project.get_AssetTypes().keys()
				for assetT in AssetTypes:
					assetTPath = os.path.normpath(os.path.join(assetType_dir,assetT))
					if os.path.isdir(assetTPath):
						self.assetType_combo.addItem(assetT)
	
	def reload_assetSpace(self):
		if self._project:
			self.assetSpace_combo.clear()
			assetTypeName = self.assetType_combo.currentText()
			assetTypes = self._project.get_AssetTypes()
			if assetTypeName in assetTypes.keys():
				assetSpaces = assetTypes[assetTypeName]
				for assetS in assetSpaces:
					self.assetSpace_combo.addItem(assetS[ProjectKeys.AssetSpace])

	def reload_assetContainerList(self):
		'''Reload the assets'''
		def dirs_to_dict(list_dir=list):
			# {"parent":{"Tree":{"":""}}}
			final = dict()
			for each_dir in list_dir:
				dirs = each_dir.split(os.sep)
				add_subs(file_names=dirs, data=final)
			return final

		def add_subs(file_names=list, data=dict):
			if file_names:
				newitem = file_names.pop(0)
				if newitem not in data:
					data[newitem] = dict()
				add_subs(file_names, data[newitem])
			else:
				return

		def make_child_StandardItem(data=dict , item=QStandardItem):
			if data:
				for name in data.keys():
					newitem = QStandardItem(name)
					item.appendRow(newitem)
					make_child_StandardItem(data=data[name], item=newitem)

		# workfile directory
		workDir = os.path.normpath(Pipeline().get_WorkDirectory())
		# Asset Type Name
		assetTypeName = self.assetType_combo.currentText()
		if assetTypeName:
			assetTypeDir = os.path.normpath(os.path.join(workDir,assetTypeName))

			assetSpaceName = self.assetSpace_combo.currentText()
			self.assetContainer_model.clear()
			files_dict = {}
			dir_collection = list()
			for root, dirs, files in os.walk(assetTypeDir):
				if assetSpaceName in dirs:
					assetContainer = root.replace(assetTypeDir, "")
					dir_collection.append(assetContainer[1:])
			# cleaning up dir
			new_collection = dirs_to_dict(list_dir = dir_collection)
			
			# create QStandardItem 
			for name in new_collection.keys():
				parent_item = QStandardItem(name)
				self.assetContainer_model.appendRow(parent_item)
				make_child_StandardItem(data=new_collection[name] , item=parent_item)

			self.assetContainer_model.sort(Qt.AscendingOrder)

	def filter_AssetContainer(self, text=str):
		self.assetContainer_filter.setFilterFixedString(self.asset_search.text())

	def set_project(self, project=ProjectMeta):
		self._project = project

class AssetTreeView(QTreeView):
	OnDoubleClick = Signal()
	def __init__(self):
		super(AssetTreeView, self).__init__()

	def mouseDoubleClickEvent(self, event=QMouseEvent):
		self.OnDoubleClick.emit()
		QTreeView.mouseDoubleClickEvent(self, event)

class Asset_Dialog(QDialog):
	def __init__(self, title=str, parent=None):
		super(Asset_Dialog, self).__init__(parent=parent)

		mainLayout = QGridLayout(self)
		mainLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
		mainLayout.setColumnStretch(0,0)
		mainLayout.setColumnStretch(1,1)
		mainLayout.setColumnStretch(2,1)
		mainLayout.setColumnStretch(3,1)
		self.setLayout(mainLayout)

		namelabel = QLabel('Asset Name:')
		namelabel.setAlignment(Qt.AlignRight)
		self.name_in = QLineEdit()
		mainLayout.addWidget(namelabel, 0, 0)
		mainLayout.addWidget(self.name_in, 0, 1, 1, 3)

		ok_btn = QPushButton("Create")
		ok_btn.clicked.connect(self.accept)
		cancel_btn = QPushButton("Cancel")
		cancel_btn.clicked.connect(self.reject)

		mainLayout.addWidget(ok_btn, 1, 1, 1, 1)
		mainLayout.addWidget(cancel_btn, 1, 3, 1, 1)
		self.setWindowTitle(title)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)

	def get_AssetContainer(self):
		return self.name_in.text()
	AssetContainer = property(get_AssetContainer)
