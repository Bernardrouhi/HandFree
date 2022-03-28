import os, getpass, json, re, shutil
from PySide2.QtWidgets import (QAction, QFileDialog, QListWidget, QMenu, QSizePolicy,
						  QAbstractItemView, QTableWidget,QHeaderView, QHBoxLayout,
						  QTableWidgetItem, QComboBox, QDialog, QVBoxLayout, QLabel,
						  QLineEdit, QPushButton, QGroupBox, QTreeWidget, QTreeWidgetItem,
						  QFrame, QSplitter, QTreeView, QFileSystemModel, QGridLayout)
from PySide2.QtGui import (QRegExpValidator, QStandardItemModel)
from PySide2.QtCore import (Qt, QPoint, QRegExp, QItemSelection, QSortFilterProxyModel,
						  QDir, QModelIndex, Signal, QObject)

from ...core import projectMetadata, publishMetadata, pipeline_handler, mayaHelper
from .. import logViewerWidget
from . import copyDialog

reload(projectMetadata)
reload(publishMetadata)
reload(pipeline_handler)
reload(logViewerWidget)
reload(mayaHelper)
reload(copyDialog)

from ...core.projectMetadata import ProjectMeta, AssetSpaceKeys, ProjectKeys
from ...core.publishMetadata import PublishMeta, PublishLogKeys, PUBLISH_FILE
from ...core.pipeline_handler import Pipeline
from ...core.mayaHelper import reference_FileToScene,import_FileToScene
from ..logViewerWidget import LogViewerWidget
from .copyDialog import CopyProgressDialog

class PublishViewerDialog(QDialog):
	onWorkfileChanged = Signal()
	def __init__(self, parent=None, project=ProjectMeta):
		super(PublishViewerDialog, self).__init__(parent=parent)

		self._project = project

		self.setMinimumSize(100, 100)
		self.resize(900, 650)

		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(5,5,5,5)
		main_layout.setSpacing(5)

		top_frame = QFrame(self)
		top_frame.setFrameShape(QFrame.StyledPanel)

		bottom_frame = QFrame(self)
		bottom_frame.setFrameShape(QFrame.StyledPanel)

		right_frame = QFrame(self)
		right_frame.setFrameShape(QFrame.StyledPanel)

		container_splitter = QSplitter(Qt.Vertical)
		container_splitter.addWidget(top_frame)

		log_splitter = QSplitter(Qt.Vertical)
		log_splitter.addWidget(container_splitter)
		log_splitter.addWidget(bottom_frame)

		asset_splitter = QSplitter(Qt.Horizontal)
		asset_splitter.addWidget(log_splitter)
		asset_splitter.addWidget(right_frame)

		main_layout.addWidget(asset_splitter)

		# ------- Row -------
		# ----------------------------------------
		container_layout = QHBoxLayout()
		container_layout.setContentsMargins(0,0,0,0)
		container_layout.setSpacing(3)

		self.assetContainer_columns = ['AssetContainer']
		self.assetContainer_list = QTreeWidget()
		self.assetContainer_list.setExpandsOnDoubleClick(False)
		self.assetContainer_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.assetContainer_list.setHeaderLabels(self.assetContainer_columns)
		self.assetContainer_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.assetContainer_list.setContextMenuPolicy(Qt.CustomContextMenu)
		# self.assetContainer_list.customContextMenuRequested.connect(self.show_ContainerMenu)

		self.assetContainer_list.itemClicked.connect(self.container_selectionChanged)
		self.assetContainer_list.itemDoubleClicked.connect(self.toogle_container_expand)

		container_layout.addWidget(self.assetContainer_list)

		top_frame.setLayout(container_layout)

		# ------- Row -------
		# ----------------------------------------
		log_layout = QHBoxLayout()
		log_layout.setContentsMargins(0,0,0,0)
		log_layout.setSpacing(3)

		self.log_viewer = LogViewerWidget()

		log_layout.addWidget(self.log_viewer)

		bottom_frame.setLayout(log_layout)

		# ------- Row -------
		# ----------------------------------------
		asset_layout = QHBoxLayout()
		asset_layout.setContentsMargins(0,0,0,0)
		asset_layout.setSpacing(3)

		self.asset_list = QTreeView()
		self.asset_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.asset_list.setHeaderHidden(True)
		self.asset_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.asset_list.setContextMenuPolicy(Qt.CustomContextMenu)
		self.asset_list.customContextMenuRequested.connect(self.show_AssetMenu)

		self.asset_model = QStandardItemModel()

		fileTypes = ['.ma']
		self.asset_filter = HideFileTypesProxy(includes=fileTypes)
		self.asset_filter.setSourceModel(self.asset_model)

		asset_layout.addWidget(self.asset_list)

		right_frame.setLayout(asset_layout)

		# ------- Row -------
		# ----------------------------------------
		action_layout = QHBoxLayout()
		action_layout.setContentsMargins(0,0,0,0)
		action_layout.setSpacing(3)
		action_layout.setAlignment(Qt.AlignLeft)

		close_btn = QPushButton("Close")
		close_btn.clicked.connect(self.reject)

		action_layout.addWidget(close_btn)

		main_layout.addLayout(action_layout)

		self.setWindowTitle("Published Asset Viewer")
		self.reload_published()

	def reload_published(self):
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

		self.assetContainer_list.clear()

		# publish directory
		publishDir = os.path.normpath(self._project.get_PublishDirectory())

		# AssetTypes
		assetTypes = self._project.get_AssetTypes()
		for assetTypeName in assetTypes:
			assetTypeDir = os.path.normpath(os.path.join(publishDir,assetTypeName))
			
			assetSpaces = list()
			for assetDict in assetTypes[assetTypeName]:
				assetSpaces.append(assetDict[ProjectKeys.AssetSpace])

			item = QTreeWidgetItem(self.assetContainer_list,[assetTypeName])

			dir_collection = list()
			for root, dirs, files in os.walk(assetTypeDir):
				if PUBLISH_FILE in files and root.endswith(tuple(assetSpaces)):# any(x in assetSpaces for x in dirs):
					dir_collection.append(root.replace(assetTypeDir, "").strip(os.sep))
			
			# Convert list of path into dictionary of hierarchy
			hierarchy_dict = dirs_to_dict(list_dir=dir_collection)

			# Creating hierarchies in the widget
			make_child_TreeWidgetItem(data=hierarchy_dict,item=item)

			self.assetContainer_list.addTopLevelItem(item)
		self.assetContainer_list.sortItems(0, Qt.AscendingOrder)

	def show_ContainerMenu(self, point=QPoint):
		self.containerMenu = QMenu()

		selected = self.assetContainer_list.selectedItems()

		if len(selected) == 1:
			Create_action = QAction("Create new Asset", self)
			Create_action.setStatusTip('Allocate a new asset in publish folder.')
			Create_action.triggered.connect(self.create_new)
			self.containerMenu.addAction(Create_action)
			# shouldn't have child but parent
			if selected[0].childCount() <= 0 and selected[0].parent():
				log_actions = self.get_logs_actions()
				if log_actions:
					self.containerMenu.addSection("Logs")
					self.containerMenu.addActions(log_actions)

		self.containerMenu.addSeparator()

		structure_action = QAction("Copy Structure to Work directory", self)
		structure_action.setStatusTip('Copy the folder structure into workdirectory.')
		structure_action.triggered.connect(self.create_structure)
		self.containerMenu.addAction(structure_action)

		self.containerMenu.move(self.assetContainer_list.viewport().mapToGlobal(point))
		self.containerMenu.show()

	def get_logs_actions(self):
		item = self.assetContainer_list.currentItem()
		assetType = self.get_AssetType(item=item)
		assetSpaces = self._project.get_AssetSpaces(assetType=assetType)

		action_list = list()
		for assetSapce in assetSpaces:
			new_action = QAction("View {} Log".format(assetSapce), self)
			new_action.setStatusTip('View asset {} logs.'.format(assetSapce))
			new_action.triggered.connect(self.request_view_logs)
			new_action.setData(assetSapce)
			action_list.append(new_action)
		return action_list

	def show_AssetMenu(self, point=QPoint):
		self.assetMenu = QMenu()

		copy_action = QAction("Copy asset to workfile", self)
		copy_action.setStatusTip('Copy published asset into work folder.')
		copy_action.triggered.connect(self.copy_publish_to_workfile)
		self.assetMenu.addAction(copy_action)

		reference_action = QAction('Create Reference', self)
		reference_action.setStatusTip("Create Reference from published files.")
		reference_action.triggered.connect(self.create_reference)
		self.assetMenu.addAction(reference_action)

		import_action = QAction("Import to the scene", self)
		import_action.setStatusTip('Import the file into the scene.')
		import_action.triggered.connect(self.import_file)
		self.assetMenu.addAction(import_action)

		self.assetMenu.move(self.asset_list.viewport().mapToGlobal(point))
		self.assetMenu.show()

	def request_view_logs(self):
		publishDir = self._project.get_PublishDirectory()
		assetContainer_path = self.get_selected_ParentPath()
		# assetType = self.get_AssetType(item=self.assetContainer_list.currentItem())
		# assetSpaces = self._project.get_AssetSpaces(assetType=assetType)
		assetSpace = self.sender().data()
		file_path = os.path.normpath(os.path.join(publishDir,assetContainer_path,assetSpace))
		if os.path.exists(file_path) and PUBLISH_FILE in os.walk(file_path).next()[2]:
			publish_node = os.path.normpath(os.path.join(file_path,PUBLISH_FILE))
			self.log_viewer.load_log(meta=PublishMeta(meta_path=publish_node))

	def get_selected_ParentPath(self):
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

	def get_selected_ChildPaths(self):
		'''get list of select asset path'''
		def collect_paths(file_path=str(), path_list=list(), item=QTreeWidgetItem):
			if item.childCount() > 0:
				file_path = os.path.join(file_path,item.text(0))
				for child in range(item.childCount()):
					collect_paths(file_path=file_path, path_list=path_list,item=item.child(child))
				return path_list
			else:
				last_path = os.path.join(file_path,item.text(0))
				path_list.append(last_path)
				return path_list

		item = self.assetContainer_list.currentItem()
		if item.childCount() > 0:
			new_list = list()
			return collect_paths(file_path=str(), path_list=new_list, item=item)
		else:
			return item.text(0)
	
	def asset_selectionChanged(self, item=QTreeWidgetItem, column=int):
		if item.childCount() == 0:
			publishDir = self._project.get_PublishDirectory()
			assetContainer_path = self.get_selected_ParentPath()
			file_path = os.path.normpath(os.path.join(publishDir,assetContainer_path))
			if os.path.exists(file_path) and PUBLISH_FILE in os.walk(file_path).next()[2]:
				publish_node = os.path.normpath(os.path.join(file_path,PUBLISH_FILE))
				self.log_viewer.load_log(meta=PublishMeta(meta_path=publish_node))

	def get_AssetType(self, item=QTreeWidgetItem):
		if item.parent():
			return self.get_AssetType(item=item.parent())
		else:
			return item.text(0)

	def container_selectionChanged(self, item=QTreeWidgetItem, column=int):
		if item.childCount() == 0 and item.parent():
			publishDir = self._project.get_PublishDirectory()
			assetContainer_path = self.get_selected_ParentPath()
			file_path = os.path.normpath(os.path.join(publishDir,assetContainer_path))
			# assetType = self.get_AssetType(item=self.assetContainer_list.currentItem())
			# assetSpaces = self._project.get_AssetSpaces(assetType=assetType)

			publish_path = os.path.normpath(os.path.join(publishDir,assetContainer_path))
			# Load Assets
			if os.path.exists(publish_path):
				self.asset_model = QFileSystemModel()
				self.asset_model.setFilter(QDir.NoDotAndDotDot|QDir.AllDirs|QDir.Files) 
				self.asset_filter.setSourceModel(self.asset_model)
				self.asset_list.setModel(self.asset_filter)
				self.asset_list.setRootIndex(self.asset_filter.mapFromSource(self.asset_model.setRootPath(publish_path)))
				# self.asset_list.hideColumn(1)
				# self.asset_list.setColumnWidth(1, 10)
				self.asset_list.hideColumn(2)
				self.asset_list.hideColumn(3)
				self.asset_list.setHeaderHidden(False)
			# Load Logs
			if os.path.exists(publish_path) and PUBLISH_FILE in os.walk(publish_path).next()[2]:
				publish_node = os.path.normpath(os.path.join(publish_path,PUBLISH_FILE))
				self.log_viewer.load_log(meta=PublishMeta(meta_path=publish_node))
			
	def toogle_container_expand(self, item=QTreeWidgetItem, column=int):
		def expand_Children(item=QTreeWidgetItem, expand=bool):
			if item.childCount() > 0:
				item.setExpanded(expand)
				expand_Children(item=item.child(0), expand=expand)
			else:
				item.setExpanded(expand)

		if item.isExpanded():
			expand_Children(item=item, expand=False)
		else:
			expand_Children(item=item, expand=True)

	def create_new(self):
		workDir = self._project.get_WorkDirectory()
		publishDir = self._project.get_PublishDirectory()
		assetTypeDialog = NewAsset_Dialog(title = "New Asset Name")
		if assetTypeDialog.exec_() == QDialog.Accepted:
			assetContainer = assetTypeDialog.AssetContainer
			print(assetContainer)
			# assetTypeName = self.assetType_combo.currentText()
			# self.create_New_AssetContainer(assetContainer=assetContainer, assetTypeName=assetTypeName)
			# self.reload_assetContainerList()

	def create_structure(self):
		print (self.get_selected_ChildPaths())

	def copy_publish_to_workfile(self):
		publishDir = self._project.get_PublishDirectory()
		published_file = self.get_AssetPath()
		if published_file:
			workDir = self._project.get_WorkDirectory()
			assetContainer = self.get_selected_ParentPath()
			fileDir = os.path.join(workDir,assetContainer)
			
			if not os.path.exists(fileDir):
				os.makedirs(fileDir)

			fileName = self.get_AssetFileName()
			new_workfile = os.path.join(fileDir,"Published_{}".format(fileName))

			# shutil.copy(published_file, new_workfile)
			copyProgress = CopyProgressDialog(self,published_file,new_workfile)
			if copyProgress.exec_() == copyProgress.Accepted:
				self.onWorkfileChanged.emit()

	def get_AssetFileName(self):
		if self.asset_list.currentIndex().row() >= 0:
			index = self.asset_filter.mapToSource(self.asset_list.currentIndex())
			return self.asset_model.fileName(index)
		return None

	def get_AssetPath(self):
		if self.asset_list.currentIndex().row() >= 0:
			index = self.asset_filter.mapToSource(self.asset_list.currentIndex())
			return self.asset_model.filePath(index)
		return None

	def get_AssetName(self):
		item = self.assetContainer_list.currentItem()
		if item:
			return item.text(0)
		return None

	def create_reference(self):
		published_path = self.get_AssetPath()
		fileName = self.get_AssetFileName()
		if fileName:
			raw_name, extension = os.path.splitext(fileName)
			groupName = "{}_grp".format(raw_name)
			reference_FileToScene(file_path=published_path,group_name=groupName,namespace_name=raw_name)

	def import_file(self):
		published_path = self.get_AssetPath()
		fileName = self.get_AssetFileName()
		if fileName:
			raw_name, extension = os.path.splitext(fileName)
			import_FileToScene(file_path=published_path, namespace=raw_name)


class HideFileTypesProxy(QSortFilterProxyModel):
	def __init__(self, includes, *args, **kwargs):
		super(HideFileTypesProxy, self).__init__(*args, **kwargs)
		self._includes = includes[:]

	def filterAcceptsRow(self, source_row=int, source_parent=QModelIndex):
		idx = self.sourceModel().index(source_row, 0, source_parent)
		name = idx.data()

		for exc in self._includes:
			if "." not in name or name.endswith(exc):
				return True
			else:
				return False
		
		return True

class NewAsset_Dialog(QDialog):
	def __init__(self, title=str, parent=None):
		super(NewAsset_Dialog, self).__init__(parent=parent)

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