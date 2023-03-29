import os, subprocess, shutil
from PySide2.QtWidgets import (QWidget, QComboBox, QVBoxLayout, QHBoxLayout,
								QSizePolicy, QLabel, QLineEdit, QSpacerItem,
								QListView, QMenu, QPushButton, QDialog, QGridLayout,
								QAction, QFileSystemModel, QAbstractItemView,
								QTreeView, QSpinBox, QTreeView,
								QHeaderView, QTreeWidget, QTreeWidgetItem, 
								QWidgetAction,QMessageBox)
from PySide2.QtGui import (QStandardItemModel, QStandardItem, QMouseEvent, QWheelEvent)
from PySide2.QtCore import (Qt, Signal, QEvent, QPoint, QSortFilterProxyModel,
							QItemSelection, QDir, QModelIndex)
from dialogs import publishAssetDialog
from dialogs import publishViewerDialog
from  ..core import pipeline_handler, mayaHelper, projectMetadata

reload(mayaHelper)
reload(pipeline_handler)
reload(publishAssetDialog)
reload(publishViewerDialog)

from ..core.pipeline_handler import Pipeline
from ..core.mayaHelper import (open_scene, set_MayaProject, create_EmptyScene,
								copy_workspace, get_workspaceName, save_Scene,
								rename_Scene,reference_FileToScene, import_FileToScene,
								set_worldspace, isSceneModified, getCurrentSceneName,
								set_defaultSceneSettings, show_grid, default_grid, 
								is_custom_grid, run_standalone, get_maya_script)
from ..core.projectMetadata import ProjectMeta, ProjectKeys, AssetSpaceKeys
from dialogs.publishAssetDialog import PublishDialog, PublishGameDialog
from dialogs.publishViewerDialog import PublishViewerDialog

class AssetLoaderWidget(QWidget):
	'''Manage project assets'''
	onUpdate = Signal()
	def __init__(self, parent=None, edit=bool(False), project=ProjectMeta()):
		super(AssetLoaderWidget, self).__init__(parent)

		self._edit = edit
		self._project = project
		self.setMinimumHeight(1)
		self.setMinimumWidth(1)

		_leftSpace = 100

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
		assetTypeLabel.setFixedWidth(_leftSpace)
		assetTypeLabel.setAlignment(Qt.AlignTop|Qt.AlignRight)
		self.assetType_combo = QComboBox()
		self.assetType_combo.currentIndexChanged.connect(self.assetType_IndexChanged)
		self.assetType_combo.setFixedWidth(150)
		published_assets = QPushButton("Get Published File")
		published_assets.clicked.connect(self.show_publishedDialog)

		assetTypeLayout.addWidget(assetTypeLabel)
		assetTypeLayout.addWidget(self.assetType_combo)
		assetTypeLayout.addWidget(published_assets)

		main_layout.addLayout(assetTypeLayout)

		# ------- Row -------
		# ----------------------------------------
		assetslistLayout = QHBoxLayout()
		assetslistLayout.setContentsMargins(0,0,0,0)
		assetslistLayout.setSpacing(3)
		assetslistLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)

		assetSpacer = QLabel("Asset Name:")
		assetSpacer.setFixedWidth(_leftSpace)
		assetSpacer.setAlignment(Qt.AlignTop|Qt.AlignRight)
		self.assetContainer_columns = ['AssetContainer','AssetSpace']
		self.assetContainer_list = QTreeWidget()
		self.assetContainer_list.setHeaderLabels(self.assetContainer_columns)
		self.assetContainer_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.assetContainer_list.setContextMenuPolicy(Qt.CustomContextMenu)
		self.assetContainer_list.customContextMenuRequested.connect(self.assetMenu)

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
		directoryLabel.setFixedWidth(_leftSpace)
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
		# savePlus_btn = QPushButton("Save+")
		# savePlus_btn.setStatusTip("Save the current scene with a new version")
		# savePlus_btn.clicked.connect(self.saveplus_file)
		# publish_btn = QPushButton("Publish")
		# publish_btn.setStatusTip("Publish the current scene")
		# publish_btn.clicked.connect(self.publish_file)
		default_btn = QPushButton("Set Defaults")
		default_btn.setStatusTip("set Default settings")
		default_btn.clicked.connect(self.set_SceneDefaults)
		grid_btn = QPushButton("Toggle Grids")
		grid_btn.setStatusTip("Toggle Grids")
		grid_btn.clicked.connect(self.toggle_grids)


		actionLayout.addWidget(save_btn)
		actionLayout.addWidget(default_btn)
		actionLayout.addWidget(grid_btn)
		# actionLayout.addWidget(publish_btn)

		main_layout.addLayout(actionLayout)

		self.reload_assetTypes()

	def show_publishedDialog(self):
		publishViewDialog = PublishViewerDialog(project=self._project)
		publishViewDialog.onWorkfileChanged.connect(self.reload_assetTypes)
		publishViewDialog.requestWorkspaceCreation.connect(self.request_creating_workspace)
		if publishViewDialog.exec_() == QDialog.Accepted:
			print ("Done")

	def request_creating_workspace(self, assetContainer=str, assetTypeName=str,):
		self.create_New_AssetContainer(assetContainer=assetContainer,assetTypeName=assetTypeName)
		self.reload_assetContainerList()

	def show_AssetCreationDialog(self):
		assetTypeDialog = Asset_Dialog(title = "New Asset Name")
		if assetTypeDialog.exec_() == QDialog.Accepted:
			assetContainer = assetTypeDialog.AssetContainer
			assetTypeName = self.assetType_combo.currentText()
			self.create_New_AssetContainer(assetContainer=assetContainer, assetTypeName=assetTypeName)
			self.reload_assetContainerList()

	def create_New_AssetContainer(self, assetContainer=str, assetTypeName=str):
		'''Create a new AssetContainer

			It gets workdirecotry from project, and create sets of assetSpaces with their workspace
			from given assetContainer and assetTypeName.
		'''
		# get workfile directory from project
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
		self.reload_assetContainerList()

	def assetMenu(self, point=QPoint):
		self.assetTMenu = QMenu()
		
		newAsset_action = QAction("Create Asset", self)
		newAsset_action.setStatusTip('Create a new Asset in workspace.')
		newAsset_action.triggered.connect(self.show_AssetCreationDialog)
		self.assetTMenu.addAction(newAsset_action)

		if self.assetContainer_list.selectedIndexes():
			
			item = self.get_selectedAssetContainerItem()

			self.assetTMenu.addSeparator()

			browse_action = QAction("Browse Work Folder", self)
			browse_action.setStatusTip('Browse into asset directory.')
			browse_action.triggered.connect(self.browse_asset_directory)
			self.assetTMenu.addAction(browse_action)

			# if item:
			# 	log_action = QAction("View Publish Logs", self)
			# 	log_action.setStatusTip('View published files histories.')
			# 	log_action.triggered.connect(self.view_published_logs)
			# 	self.assetTMenu.addAction(log_action)

			self.assetTMenu.addSeparator()

			if item:
				assetSpace = self.get_selectedAssetSpace()

				new_action = QAction("Create a new Scene", self)
				new_action.setStatusTip('Create a new scene.')
				new_action.triggered.connect(self.create_scene)
				self.assetTMenu.addAction(new_action)

				# self.assetTMenu.addSection(assetSpace)
				# # list of published files
				# self.assetTMenu.addMenu(self.get_copy_PublishedFile_Menu())
				# self.assetTMenu.addMenu(self.get_reference_PublishedFile_Menu())

				self.assetTMenu.addSeparator()

			fix_action = QAction("Fix AssetSpace", self)
			fix_action.setStatusTip('Check/fix missing AssetSpace and workspace.')
			fix_action.triggered.connect(self.fix_assetSpace)
			self.assetTMenu.addAction(fix_action)

		self.assetTMenu.move(self.assetContainer_list.viewport().mapToGlobal(point))
		self.assetTMenu.show()

	def get_reference_PublishedFile_Menu(self):
		publishMenu = QMenu()
		publishMenu.setTitle('Create Reference')
		publishMenu.setStatusTip("Create Reference from published files.")

		publish_path = self.get_published_directory()
		if os.path.exists(publish_path):
			for each in os.walk(publish_path).next()[2]:
				if each.lower().endswith((".ma",".mb")):
					new_action = QAction(each, publishMenu)
					new_action.triggered.connect(self.create_reference)
					publishMenu.addAction(new_action)
		#None
		new_action = QAction("...", publishMenu)
		new_action.setDisabled(True)
		# new_action.setStatusTip('Create a new scene.')
		# new_action.triggered.connect(self.create_scene)

		publishMenu.addAction(new_action)

		return publishMenu

	def get_copy_PublishedFile_Menu(self):
		publishMenu = QMenu()
		publishMenu.setTitle('Copy to Workdirectory')
		publishMenu.setStatusTip("Copy publish file into workdirectory.")

		publish_path = self.get_published_directory()
		if os.path.exists(publish_path):
			for each in os.walk(publish_path).next()[2]:
				if each.lower().endswith((".ma",".mb")):
					new_action = QAction(each, publishMenu)
					new_action.triggered.connect(self.copy_publish_to_workdirectory)
					publishMenu.addAction(new_action)
		#None
		new_action = QAction("...", publishMenu)
		new_action.setDisabled(True)
		# new_action.setStatusTip('Create a new scene.')
		# new_action.triggered.connect(self.create_scene)

		publishMenu.addAction(new_action)

		return publishMenu

	def copy_publish_to_workdirectory(self):
		publish_path = self.get_published_directory()
		fileName = self.sender().text()
		published_file = os.path.join(publish_path,fileName)

		work_path = ""
		work_path = self._project.get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.get_selectedAssetSpace()
		if assetSpace:
			assetContainer = self.get_selectedAssetContainer()
			assetName = self.get_selectedAssetContainerItem().text(0)
			work_path = os.path.join(work_path,assetType,assetContainer,assetSpace)
		
		if os.path.exists(publish_path):
			print(publish_path)
		if os.path.exists(work_path):
			print(work_path)

		new_workfile = os.path.join(work_path, "Published_{}".format(fileName))

		shutil.copy(published_file, new_workfile)


	def create_reference(self):
		publish_path = self.get_published_directory()
		fileName = self.sender().text()
		published = os.path.join(publish_path,fileName)
		raw_name, extension = os.path.splitext(fileName)
		groupName = "{}_grp".format(raw_name)
		reference_FileToScene(file_path=published,group_name=groupName,namespace_name=raw_name)

	def get_published_directory(self):
		publish_path = str()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.get_selectedAssetSpace()
		item = self.get_selectedAssetContainerItem()
		if item:
			assetName = item.text(0)
			assetContainer = self.get_selectedAssetContainer()
			publish_path = os.path.join(self._project.get_PublishDirectory(),assetType,assetContainer,assetSpace)
		return publish_path

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
		if os.path.isdir(workDirectory):
			item = self.get_selectedAssetContainerItem()
			if item:
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
				publish_action = QAction("Publish Asset...", self)
				publish_action.setStatusTip('Publish the selected asset.')
				publish_font = publish_action.font()
				publish_font.setBold(True)
				publish_action.setFont(publish_font)
				publish_action.triggered.connect(self.publish_file)
				# publish_action.setDisabled(True)
				self.newMenu.addAction(publish_action)

				self.newMenu.addSeparator()

				# # Have to get from publish directory
				# reference_action = QAction("Create Reference", self)
				# reference_action.setStatusTip('Create a reference of this file in the scene.')
				# reference_action.triggered.connect(self.reference_file)
				# reference_action.setDisabled(True)
				# self.newMenu.addAction(reference_action)

				# Have to get from publish directory
				script_action = QAction("Run Script...", self)
				script_action.setStatusTip('Run custom Script on the file.')
				script_action.triggered.connect(self.run_custom_script)
				script_action.setDisabled(not self._edit)
				self.newMenu.addAction(script_action)

				# fixReference_action = QAction("Fix References...", self)
				# fixReference_action.setStatusTip('Fix references within the file.')
				# fixReference_action.triggered.connect(self.fix_references)
				# fixReference_action.setDisabled(True)
				# self.newMenu.addAction(fixReference_action)

				import_action = QAction("Import to...", self)
				import_action.setStatusTip('Import the file into the scene.')
				import_action.triggered.connect(self.import_file)
				self.newMenu.addAction(import_action)

			if fileName.lower().endswith(".fbx"):
				gamePublish_action = QAction("Publish Game Asset...", self)
				gamePublish_action.setStatusTip('Publish the selected asset to game engine.')
				gamePublish_font = gamePublish_action.font()
				gamePublish_font.setBold(True)
				gamePublish_action.setFont(gamePublish_font)
				gamePublish_action.triggered.connect(self.publish_game_file)
				# publish_action.setDisabled(True)
				self.newMenu.addAction(gamePublish_action)

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

	def run_custom_script(self):
		workdir = Pipeline().get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.get_selectedAssetSpace()
		assetContainer = self.get_selectedAssetContainer()
		fileName = self.assetSpace_list.currentIndex().data()

		file_path = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace,fileName))
		# script_path = os.path.normpath(get_maya_script(script_name="SimpleCube"))
		# # Run Script
		# run_standalone(file_path=file_path,script_path=script_path)

	def reference_file(self):
		workdir = Pipeline().get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.get_selectedAssetSpace()
		if assetSpace:
			assetContainer = self.get_selectedAssetContainer()
			fileName = self.assetSpace_list.currentIndex().data()
			
			file_path = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace,fileName))
			raw_name, extension = os.path.splitext(fileName)
			groupName = "{}_grp".format(raw_name)
			reference_FileToScene(file_path=file_path,group_name=groupName,namespace_name=raw_name)

	def fix_references(self):
		pass

	def import_file(self):
		workdir = Pipeline().get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.get_selectedAssetSpace()
		if assetSpace:
			assetContainer = self.get_selectedAssetContainer()
			fileName = self.assetSpace_list.currentIndex().data()

			file_path = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace,fileName))
			raw_name, extension = os.path.splitext(fileName)
			import_FileToScene(file_path=file_path, namespace=raw_name)

	def open_file(self):
		workdir = Pipeline().get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.get_selectedAssetSpace()
		if assetSpace:
			assetContainer = self.get_selectedAssetContainer()
			assetItem = self.get_selectedAssetContainerItem()
			if assetItem:
				assetName = assetItem.text(0)
				fileName = self.assetSpace_list.currentIndex().data()

				dirPath = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace))
				filePath = os.path.normpath(os.path.join(dirPath,fileName))

				if isSceneModified():
					saveCheck = QMessageBox()
					result = saveCheck.warning(self,'Save Changes', "Save changes to {}?".format(getCurrentSceneName()), QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel)
					if result == QMessageBox.Save:
						save_Scene()
					elif result == QMessageBox.Cancel:
						return

				set_worldspace()
				set_MayaProject(directory=dirPath)
				open_scene(scene_path=filePath)
				set_defaultSceneSettings()
				default_grid()
				Pipeline().set_AssetType(assetType)
				Pipeline().set_AssetContainer(assetContainer)
				Pipeline().set_AssetSpace(assetSpace)
				Pipeline().set_AssetName(assetName)
				self.onUpdate.emit()

	def view_published_logs(self):
		pass
		
	def external_save(self):
		workdir = self._project.get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.get_selectedAssetSpace()
		if assetSpace:
			assetContainer = self.get_selectedAssetContainer()
			assetItem = self.get_selectedAssetContainerItem()
			if assetItem:
				assetName = assetItem.text(0)
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
		assetType = self.assetType_combo.currentText()
		assetSpace = self.get_selectedAssetSpace()
		item = self.get_selectedAssetContainerItem()
		# Get selected file path
		index = self.assetSpace_filter.mapToSource(self.assetSpace_list.currentIndex())
		file_path = os.path.normpath(self.assetSpace_model.filePath(index))
		file_path = file_path.replace(self._project.get_WorkDirectory(),"").strip("\\")
		if item:
			assetName = item.text(0)
			assetContainer = self.get_selectedAssetContainer()

			publish_dialog = PublishDialog(
						assetType=assetType,
						assetContainer=assetContainer,
						assetSpace=assetSpace,
						assetName=assetName,
						filePath=file_path)
			if publish_dialog.exec_() == publish_dialog.Accepted:
				result = publish_dialog.publish_asset()
				if result:
					msg = QMessageBox()
					msg.information(self, 'Published', '{} File is Published.'.format(publish_dialog.get_PublishedFile()), QMessageBox.Ok)
				else:
					msg = QMessageBox()
					msg.critical(self, 'ERROR', "Couldn't publish the asset!", QMessageBox.Ok)

	def publish_game_file(self):
		assetType = self.assetType_combo.currentText()
		assetSpace = self.get_selectedAssetSpace()
		item = self.get_selectedAssetContainerItem()
		# Get selected file path
		index = self.assetSpace_filter.mapToSource(self.assetSpace_list.currentIndex())
		file_path = os.path.normpath(self.assetSpace_model.filePath(index))
		file_path = file_path.replace(self._project.get_WorkDirectory(),"").strip("\\")
		if item:
			assetName = item.text(0)
			assetContainer = self.get_selectedAssetContainer()
			publish_dialog = PublishGameDialog(
						assetType=assetType,
						assetContainer=assetContainer,
						assetSpace=assetSpace,
						assetName=assetName,
						filePath=file_path)

			if publish_dialog.exec_() == publish_dialog.Accepted:
				result = publish_dialog.publish_asset()
				if result:
					msg = QMessageBox()
					msg.information(self, 'Published', '"{}" file is Published.'.format(publish_dialog.get_PublishedFile()), QMessageBox.Ok)
				else:
					msg = QMessageBox()
					msg.critical(self, 'ERROR', "Couldn't publish the game asset!", QMessageBox.Ok)

	def save_file(self):
		save_Scene()

	def saveplus_file(self):
		workdir = self._project.get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.get_selectedAssetSpace()
		if assetSpace:
			assetContainer = self.get_selectedAssetContainer()

			if workdir and assetType and assetSpace and assetContainer:
				dirPath = os.path.normpath(os.path.join(workdir,assetType,assetContainer,assetSpace))
				if os.path.isdir(dirPath):
					assetItem = self.get_selectedAssetContainerItem()

					if assetItem:
						assetName = assetItem.text(0)
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
		if self.assetSpace_list.currentIndex().row() >= 0:
			fileName = self.assetSpace_list.currentIndex().data()
			if fileName.lower().endswith(".ma"):
				self.open_file()

	def create_scene(self):
		workdir = self._project.get_WorkDirectory()
		assetType = self.assetType_combo.currentText()
		assetSpace = self.get_selectedAssetSpace()
		if assetSpace:
			assetContainer = self.get_selectedAssetContainer()
			assetItem = self.get_selectedAssetContainerItem()

			if assetItem:
				assetName = assetItem.text(0)
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

				if isSceneModified():
					saveCheck = QMessageBox()
					result = saveCheck.warning(self,'Save Changes', "Save changes to {}?".format(getCurrentSceneName()), QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel)
					if result == QMessageBox.Save:
						save_Scene()
					elif result == QMessageBox.Cancel:
						return
				set_worldspace()
				create_EmptyScene()
				set_worldspace()
				set_MayaProject(directory=dirPath)
				rename_Scene(name="{}.ma".format(newFileName))
				set_defaultSceneSettings()
				default_grid()
				save_Scene()

				Pipeline().set_AssetType(assetType)
				Pipeline().set_AssetContainer(assetContainer)
				Pipeline().set_AssetSpace(assetSpace)
				Pipeline().set_AssetName(assetName)
				self.onUpdate.emit()
				self.reload_assetWorkspaceList()

	def browse_workspace_file(self):
		if self.assetSpace_list.currentIndex().row() >= 0:
			index = self.assetSpace_filter.mapToSource(self.assetSpace_list.currentIndex())
			file_path = self.assetSpace_model.filePath(index)
			if file_path and os.path.exists(file_path):
				file_path = os.path.normpath(file_path)
				print(file_path)
				subprocess.Popen(r'explorer /select,"{path}"'.format(path=file_path))

	def asset_selectionChanged(self, index=QItemSelection()):
		self.reload_assetWorkspaceList()
		
	def reload_assetWorkspaceList(self):
		item = self.get_selectedAssetContainerItem()
		if item:
			assetContainer = self.get_selectedAssetContainer()
			workdir = Pipeline().get_WorkDirectory()
			assetType = self.assetType_combo.currentText()
			assetSpace = self.get_selectedAssetSpace()
			if assetSpace:
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
					return
		# in case everything failed
		self.assetSpace_model = QStandardItemModel()
		self.assetSpace_list.setModel(self.assetSpace_model)

	def get_selectedAssetContainerItem(self):
		'''get selected AssetContainer

			Return:
				(QTreeWidgetItem): True if exists, otherwise False.
		'''
		item = self.assetContainer_list.currentItem()
		if not item or item.childCount() > 0:
			return None
		return item

	def get_selectedAssetSpace(self):
		item = self.assetContainer_list.currentItem()
		if item:
			itemWidget = self.assetContainer_list.itemWidget(item,1)
			if itemWidget and type(itemWidget) is type(AssetSpaceCombo()):
				return itemWidget.currentText()
		return None

	def get_selectedAssetContainer(self):
		'''get select asset path'''
		def collect_names(file_path=str(), item=QTreeWidgetItem):
			if item.parent():
				return collect_names(file_path=os.path.join(item.text(0),file_path),item=item.parent())
			else:
				return os.path.normpath(os.path.join(item.text(0),file_path))

		item = self.assetContainer_list.currentItem()
		if item.parent():
			return collect_names(item=item)
		else:
			return item.text(0)
		
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

		def make_child_TreeWidgetItem(data=dict , item=QTreeWidgetItem):
			if data:
				for name in data.keys():
					newitem = QTreeWidgetItem(item,[name])
					make_child_TreeWidgetItem(data=data[name], item=newitem)
			else:
				assetTypeName = self.assetType_combo.currentText()
				assetTypes = self._project.get_AssetTypes()
				# ComboBox Options
				option_list = list()
				if assetTypeName in assetTypes.keys():
					assetSpaces = assetTypes[assetTypeName]
					for assetS in assetSpaces:
						option_list.append(assetS[ProjectKeys.AssetSpace])

				column_combo = AssetSpaceCombo()
				column_combo.setFocusPolicy(Qt.StrongFocus)
				column_combo.addItems(option_list)
				column_combo.currentIndexChanged.connect(self.assetSpace_ComboIndexChanged)
				self.assetContainer_list.setItemWidget(item, 1, column_combo)

		self.assetContainer_list.clear()

		# workfile directory
		workDir = os.path.normpath(Pipeline().get_WorkDirectory())
		# Asset Type Name
		assetTypeName = self.assetType_combo.currentText()
		if assetTypeName:
			assetTypeDir = os.path.normpath(os.path.join(workDir,assetTypeName))

			assetTypes = self._project.get_AssetTypes()
			if assetTypeName in assetTypes.keys():
				assetSpaces = assetTypes[assetTypeName]
				
				if len(assetSpaces) > 0:
					assetSpaceName = assetSpaces[0][ProjectKeys.AssetSpace]

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
						item = QTreeWidgetItem(self.assetContainer_list,[name])
						make_child_TreeWidgetItem(data=new_collection[name] , item=item)

			self.assetContainer_list.sortItems(0, Qt.AscendingOrder)

	def filter_AssetContainer(self, text=str):
		print("Not Implemented!")
		# self.assetContainer_filter.setFilterFixedString(self.asset_search.text())
		return

	def set_project(self, project=ProjectMeta):
		self._project = project

	def assetSpace_ComboIndexChanged(self, index=int):
		item = self.assetContainer_list.currentItem()
		if item:
			assetSpaceName = self.sender().currentText()
			self.reload_assetWorkspaceList()

	def set_SceneDefaults(self):
		set_worldspace()
		set_defaultSceneSettings()

	def toggle_grids(self):
		if is_custom_grid():
			default_grid()
		else:
			show_grid()

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

class AssetSpaceCombo(QComboBox):
	def __init__(self):
		super(AssetSpaceCombo, self).__init__()
	def wheelEvent(self, event=QWheelEvent):
		return True
