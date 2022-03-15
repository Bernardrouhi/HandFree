import os
import json

from PySide2.QtCore import (Signal, QObject)

import pipeline_handler
from pipeline_handler import Pipeline

PROJECT_EXTENSION = ".hfp"

class ProjectKeys():
	WorkDirectory = "Work_directory"
	PublishDirectory = "Publish_directory"
	Project = "Project"
	Version = "Version"
	AssetTypes = "AssetTypes"
	AssetSpace = "AssetSpace"
	WorkSpace = "Workspace"

class AssetSpaceKeys():
	Maya = "Maya"
	SusbtancePainter = "SubstancePainter"
	Empty = "Empty"

class ProjectMeta(QObject):
	'''Handle Hands Free Project file'''
	onWorkDirectoryUpdate = Signal()
	def __init__(self):
		QObject.__init__(self)
		self._data = self.PROJECT_METADATA()
		self._path = str(os.path.expanduser('~'))
		self._pm = Pipeline()
		self.init()

	def PROJECT_METADATA(self):
		'''Project default Metadata structure
		'''
		return {
			ProjectKeys.WorkDirectory:"",
			ProjectKeys.Project:"",
			ProjectKeys.AssetTypes:{},
			ProjectKeys.Version:"1.0"
		}.copy()

	def ASSETSPACE_METADATA(self):
		return {ProjectKeys.AssetSpace:"", ProjectKeys.WorkSpace:""}.copy()

	def init(self):
		'''Set environment variable if it's not set otherwise load the environment variable.
		'''
		# Project Name
		if self._pm.get_ProjectName():
			self.ProjectName = self._pm.get_ProjectName()
		else:
			self._pm.set_ProjectName(self._data[ProjectKeys.Project])


		# Work Directory
		if self._pm.get_WorkDirectory():
			self.WorkDirectory = self._pm.get_WorkDirectory()
		else:
			self._pm.set_WorkDirectory(self._data[ProjectKeys.WorkDirectory])

	def get_LastPath(self):
		'''Get last opened directory

			Return:
				(str): directory path.
		'''
		return self._path
	def set_LastPath(self, directory=str):
		'''Set last opened directory

			Return:
				(str): directory path.
		'''
		self._path = directory

	def get_ProjectName(self):
		'''Get the name of project

			Return: 
				(str): Name of the Project
		'''
		return self._pm.get_ProjectName()
	def set_ProjectName(self, project_name=str):
		'''update the project name

			Args:
				project_name (str): Name of the Project.
		
			Return: None
		'''
		self._data[ProjectKeys.Project] = project_name
		self._pm.set_ProjectName(project_name)

	def get_WorkDirectory(self):
		'''Get the WorkDirectory

			Return:
				(str): Path to project work directory.
		'''
		return self._pm.get_WorkDirectory()
	def set_WorkDirectory(self, work_directory=str):
		'''update the Work Directory

			Args:
				work_directory (str): Path to project work directory.
		
			Return: None
		'''
		self._data[ProjectKeys.WorkDirectory] = work_directory
		self._pm.set_WorkDirectory(work_directory)
		self.onWorkDirectoryUpdate.emit()

	def get_PublishDirectory(self):
		'''Get the Publish_directory

			Return:
				(str): Path to project work directory.
		'''
		return self._pm.get_PublishDirectory()
	def set_PublishDirectory(self, publish_directory=str):
		'''update the Work Directory

			Args:
				publish_directory (str): Path to project work directory.
		
			Return: None
		'''
		self._data[ProjectKeys.PublishDirectory] = publish_directory
		self._pm.set_PublishDirectory(publish_directory)

	def get_AssetTypesName(self):
		'''Get list of all the project AssetTypes'''
		return self._data[ProjectKeys.AssetTypes].keys()
	def get_AssetTypes(self):
		'''get the Project assetTypes'''
		return self._data[ProjectKeys.AssetTypes]
	def set_AssetTypes(self, assetTypeDict=dict):
		self._data[ProjectKeys.AssetTypes] = assetTypeDict
	def set_assetType(self, assetType=str, assetSpaceList=list):
		self._data[ProjectKeys.AssetTypes][assetType] = assetSpaceList

	def update_settings(self, project_name=str, work_directory=str):
		'''update all the settings.

			Args:
				project_name (str): Name of the Project.
				work_directory (str): Path to project work directory.
		
			Return: None
		'''
		self.set_ProjectName(project_name)
		self.set_WorkDirectory(work_directory)

	def load(self, ProjectFile=str):
		'''Load Hands Free Projet file

			Args:
			ProjectFile (str): Path to project file.
		
			Return: None
		'''
		if ProjectFile and ProjectFile.lower().endswith(PROJECT_EXTENSION):
			# update the latest path
			self._path = os.path.dirname(ProjectFile)
			with open(ProjectFile, 'r') as outfile:
				# Load project file
				if outfile:
					LoadedData = json.load(outfile)
					if ProjectKeys.Version in LoadedData and LoadedData[ProjectKeys.Version] == "1.0":
						if ProjectKeys.Project in LoadedData:
							self.set_ProjectName(project_name=LoadedData[ProjectKeys.Project])
						if ProjectKeys.WorkDirectory in LoadedData:
							self.set_WorkDirectory(work_directory=LoadedData[ProjectKeys.WorkDirectory])
						if ProjectKeys.AssetTypes in LoadedData:
							self.set_AssetTypes(assetTypeDict=LoadedData[ProjectKeys.AssetTypes])
						if ProjectKeys.PublishDirectory in LoadedData:
							self.set_PublishDirectory(publish_directory=LoadedData[ProjectKeys.PublishDirectory])

	def save(self, ProjectFile=str):
		'''Save Hands Free Projet file

			Args:
			ProjectFile (str): Path to project file.
		
			Return: None
		'''
		if ProjectFile:
			# add extension
			file_path = ProjectFile.split('.')[0]
			file_path += PROJECT_EXTENSION
			# update the latest path
			self._path = os.path.dirname(ProjectFile)
			# save project file
			with open(file_path, 'w') as outfile:
				json.dump(self._data, outfile, ensure_ascii=False, indent=4)

	def print_settings(self):
		'''
		'''
		print (self.get_WorkDirectory())
		print (self.get_ProjectName())
