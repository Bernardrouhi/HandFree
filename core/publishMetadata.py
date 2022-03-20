import os
import json
from datetime import datetime #timezone

from PySide2.QtCore import (Signal, QObject)

PUBLISH_EXTENSION = ".hfpub"
PUBLISH_NAME = "Asset"
PUBLISH_FILE = "Asset.hfpub"

class PublishLogKeys():
	VERSION = "Version"
	USER = "User"
	WORKFILES = "WorkFiles"
	PUBLISHFILES = "PublishFiles"
	RECORD = "Record"
	APP = "Application"
	DESCRIPTION = "Description"

class PublishFileKeys():
	FILE_VERSION = "Hands Free Version"
	ASSET_TYPE = "AssetType"
	ASSET_CONTAINER = "AssetContainer"
	ASSET_SPACE = "AssetSpace"
	ASSET_NAME = "AssetName"
	LOGS = "Logs"

class PublishMeta(QObject):
	'''Handle Hands Free Publish file'''
	def __init__(self, meta_path=str()):
		QObject.__init__(self)
		self._publish = self.PUBLISH_METADATA()
		if os.path.exists(meta_path):
			self.load(directory=meta_path)

	def PUBLISH_METADATA(self):
		'''File Metadata structure
		'''
		return {
			PublishFileKeys.FILE_VERSION:"1.0",
			PublishFileKeys.ASSET_TYPE:str(),
			PublishFileKeys.ASSET_CONTAINER:str(),
			PublishFileKeys.ASSET_SPACE:str(),
			PublishFileKeys.ASSET_NAME:str(),
			PublishFileKeys.LOGS:list()
		}.copy()

	def LOG_METADATA(self):
		'''Node Metadata structure
		'''
		return {
			PublishLogKeys.VERSION: int(1),
			PublishLogKeys.USER: str(),
			PublishLogKeys.WORKFILES: list(),
			PublishLogKeys.PUBLISHFILES: list(),
			PublishLogKeys.RECORD: str(),
			PublishLogKeys.APP:str(),
			PublishLogKeys.DESCRIPTION:str()
		}.copy()

	def set_AssetType(self, assetType=str):
		self._publish[PublishFileKeys.ASSET_TYPE] = assetType
	def get_AssetType(self):
		return self._publish[PublishFileKeys.ASSET_TYPE]

	def set_AssetContainer(self, assetContainer=str):
		self._publish[PublishFileKeys.ASSET_CONTAINER] = assetContainer
	def get_AssetContainer(self):
		return self._publish[PublishFileKeys.ASSET_CONTAINER]

	def set_AssetSpace(self, assetSpace=str):
		self._publish[PublishFileKeys.ASSET_SPACE] = assetSpace
	def get_AssetSpace(self):
		return self._publish[PublishFileKeys.ASSET_SPACE]

	def set_AssetName(self, assetName=str):
		self._publish[PublishFileKeys.ASSET_NAME] = assetName
	def get_AssetName(self):
		return self._publish[PublishFileKeys.ASSET_NAME]

	def set_PublishNode(self, assetType=str, assetContainer=str, assetSpace=str, assetName=str):
		self.set_AssetType(assetType=assetType)
		self.set_AssetContainer(assetContainer=assetContainer)
		self.set_AssetSpace(assetSpace=assetSpace)
		self.set_AssetName(assetName=assetName)

	def create_new_log(self, username=str, workfiles=list, publishfiles=list, app=str, description=str):
		newRecord = self.LOG_METADATA()
		nextVersion = self.get_version() + 1
		newRecord[PublishLogKeys.VERSION] = nextVersion
		newRecord[PublishLogKeys.USER] = username
		newRecord[PublishLogKeys.WORKFILES] = workfiles
		newRecord[PublishLogKeys.PUBLISHFILES] = publishfiles
		# newRecord[PublishLogKeys.RECORD] = str(datetime.now(timezone.utc).timestamp())
		newRecord[PublishLogKeys.RECORD] = str(datetime.now())
		newRecord[PublishLogKeys.APP] = app
		newRecord[PublishLogKeys.DESCRIPTION] = description
		self._publish[PublishFileKeys.LOGS].append(newRecord)
		return newRecord

	def get_version(self):
		return len(self._publish[PublishFileKeys.LOGS])

	def get_logs(self):
		return self._publish[PublishFileKeys.LOGS]

	def get_date(self, record=str):
		# return datetime.fromtimestamp(record, timezone.utc).date()
		return datetime.utcfromtimestamp(record).date()
	def get_time(self, record=str):
		# return datetime.fromtimestamp(record, timezone.utc).time()
		return datetime.utcfromtimestamp(record).time()

	def save(self, directory=str):
		'''Save Hands Free publish file

			Args:
			directory (str): Path to publish file.
		
			Return: None
		'''
		if directory:
			if os.path.isfile(directory):
				directory = os.path.dirname(directory)
			directory = os.path.normpath(directory)
			# add extension
			file_path = os.path.join(directory,PUBLISH_FILE)
			# save project file
			with open(file_path, 'w') as outfile:
				json.dump(self._publish, outfile, ensure_ascii=False)

	def load(self, directory=str):
		if directory:
			if os.path.isfile(directory):
				directory = os.path.dirname(directory)
			# add extension
			file_path = os.path.join(directory,PUBLISH_FILE)
			if os.path.exists(file_path):
				with open(file_path, 'r') as outfile:
					LoadedData = json.load(outfile)
					if PublishFileKeys.FILE_VERSION in LoadedData and LoadedData[PublishFileKeys.FILE_VERSION] == "1.0":
						if PublishFileKeys.LOGS in LoadedData:
							self._publish[PublishFileKeys.LOGS] = LoadedData[PublishFileKeys.LOGS]
						if PublishFileKeys.ASSET_TYPE in LoadedData:
							self.set_AssetType(assetType=LoadedData[PublishFileKeys.ASSET_TYPE])
						if PublishFileKeys.ASSET_CONTAINER in LoadedData:
							self.set_AssetContainer(assetContainer=LoadedData[PublishFileKeys.ASSET_CONTAINER])
						if PublishFileKeys.ASSET_SPACE in LoadedData:
							self.set_AssetSpace(assetSpace=LoadedData[PublishFileKeys.ASSET_SPACE])
						if PublishFileKeys.ASSET_NAME in LoadedData:
							self.set_AssetName(assetName=LoadedData[PublishFileKeys.ASSET_NAME])
						
