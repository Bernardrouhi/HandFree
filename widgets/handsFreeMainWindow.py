import webbrowser
from PySide2.QtWidgets import (QMainWindow, QDockWidget, QWidget, QAction, 
						  QMenuBar,QFileDialog, QTabWidget, QMenu, QDialog)
from PySide2.QtCore import Qt

import projectLoaderWidget
import projectInfoWidget
import dialogs.projectSetupDialog
from ..core import projectMetadata

reload(projectLoaderWidget)
reload(projectInfoWidget)
reload(dialogs.projectSetupDialog)
reload(projectMetadata)

from projectLoaderWidget import AssetLoaderWidget
from projectInfoWidget import ProjectInfo
from dialogs.projectSetupDialog import ProjectSetupDialog
from dialogs.exportAssetsDialog import ExportDialog
from ..core.projectMetadata import ProjectMeta

class HandsFreeMainWindow(QMainWindow):
	def __init__(self, parent=None, projectfile=str(), edit=bool(False)):
		super(HandsFreeMainWindow, self).__init__(parent)
		self._parent = parent
		self._edit = edit
		self._project = ProjectMeta()
		self._project.load(ProjectFile=projectfile)

		self.setWindowTitle('HandsFreeMainWindow')

		self.setMinimumHeight(1)
		self.setMinimumWidth(1)

		# self.setContextMenuPolicy(Qt.PreventContextMenu)

		self.setTabPosition(Qt.LeftDockWidgetArea, QTabWidget.East)

		# Project Info Tab
		self.projectInfo = ProjectInfo()

		self.infoDock = QDockWidget(" Project Info ", self)
		self.infoDock.setObjectName('Project Info')
		self.infoDock.setFeatures(QDockWidget.DockWidgetClosable|QDockWidget.DockWidgetMovable)
		self.infoDock.setWidget(self.projectInfo)
		# self.infoDock.setTitleBarWidget(QWidget(self.infoDock))
		self.addDockWidget(Qt.LeftDockWidgetArea, self.infoDock)
		self.infoDock.setVisible(True)

		# Asset Loader Tab
		self.assetLoader = AssetLoaderWidget(edit=edit, project=self._project)
		self.assetDock = QDockWidget(" Asset Loader ", self)
		self.assetDock.setObjectName('Asset Loader')
		self.assetDock.setFeatures(QDockWidget.DockWidgetClosable|QDockWidget.DockWidgetMovable)
		self.assetDock.setWidget(self.assetLoader)
		# self.assetDock.setTitleBarWidget(QWidget(self.assetDock))
		self.addDockWidget(Qt.LeftDockWidgetArea, self.assetDock)
		self.assetDock.setVisible(True)

		# Signals
		self._project.onWorkDirectoryUpdate.connect(self.assetLoader.reload_assetTypes)
		self.assetLoader.onUpdate.connect(self.projectInfo.update_information)
		# Menu
		self.setMenuBar(self.create_menu())

	def create_menu(self):
		window_menu = QMenuBar(self)

		if self._edit:
			# Setup Menu
			setup_menu = window_menu.addMenu("&Setup")

			setup_action = QAction("&Setup Project", self)
			setup_action.setStatusTip('Edit the project settings.')
			setup_action.triggered.connect(self.setup_project)
			setup_menu.addAction(setup_action)

			load_action = QAction("&Load Project", self)
			load_action.setStatusTip('Load hfp file.')
			load_action.triggered.connect(self.load_project)
			setup_menu.addAction(load_action)

			save_action = QAction("&Save Project", self)
			save_action.setStatusTip('Save hfp file.')
			save_action.triggered.connect(self.save_project)
			setup_menu.addAction(save_action)

		# Tool Menu
		tool_menu = window_menu.addMenu("&Tool")

		export_action = QAction("&Export", self)
		export_action.setStatusTip('Batch export assets.')
		export_action.triggered.connect(self.export_asset)
		tool_menu.addAction(export_action)

		import_action = QAction("&Import", self)
		import_action.setStatusTip('Batch import assets.')
		import_action.triggered.connect(self.import_asset)
		tool_menu.addAction(import_action)

		# About menu
		about_menu = window_menu.addMenu("&About")
		wiki_action = QAction("&About HandsFree...", self)
		wiki_action.setStatusTip('Open Wiki page for documentation.')
		wiki_action.triggered.connect(self.wiki_open)
		about_menu.addAction(wiki_action)

		return window_menu

	def wiki_open(self):
		print ("Wiki is not ready yet.")
		# webbrowser.open_new_tab('https://github.com/Bernardrouhi/HandsFree/wiki')

	def setup_project(self):
		'''Setup project Dialog and update Environment varaiables'''
		projectDialog = ProjectSetupDialog(
					ProjectName=self._project.get_ProjectName(),
					WorkDirectory=self._project.get_WorkDirectory(),
					PublishDirectory=self._project.get_PublishDirectory(),
					AssetTypes=self._project.get_AssetTypes().copy()
		)
		if projectDialog.exec_() == QDialog.Accepted:
			self._project.set_ProjectName(projectDialog.get_ProjectName())
			self._project.set_AssetTypes(projectDialog.get_AssetTypes())
			self._project.set_WorkDirectory(projectDialog.get_WorkDirectory())
			self._project.set_PublishDirectory(projectDialog.get_PublishDirectory())
			print ("Project Settings are stored.")

	def save_project(self):
		'''Save project HFP file'''
		newPath, okPressed = QFileDialog.getSaveFileName(self, 'Save Project File', self._project.get_LastPath(), "Hand Free Project (*.hfp)")
		if newPath:
			self._project.save(ProjectFile=newPath)

	def load_project(self):
		file_path, okPressed = QFileDialog.getOpenFileName(self, 'Open Project File', self._project.get_LastPath(),"Hand Free Project (*.hfp)")
		if file_path:
			self._project.load(ProjectFile=file_path)

	def export_asset(self):
		export_Dialog = ExportDialog(project=self._project)

		if export_Dialog.exec_() == QDialog.Accepted:
			print("OKAY")

	def import_asset(self):
		pass
