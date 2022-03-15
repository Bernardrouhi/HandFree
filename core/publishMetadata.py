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
	WORKFILE = "WorkFile"
	ASSETNAME = "AssetName"
	RECORD = "Record"
	APP = "Application"
	DESCRIPTION = "Description"

class PublishFileKeys():
	FILE_VERSION = "Hands Free Version"
	LOGS = "Logs"

class PublishMeta(QObject):
	'''Handle Hands Free Publish file'''
	def __init__(self):
		QObject.__init__(self)
		self._publish = self.PUBLISH_METADATA()

	def PUBLISH_METADATA(self):
		'''File Metadata structure
		'''
		return {
			PublishFileKeys.FILE_VERSION:"1.0",
			PublishFileKeys.LOGS:list()
		}.copy()

	def LOG_METADATA(self):
		'''Node Metadata structure
		'''
		return {
			PublishLogKeys.VERSION: int(1),
			PublishLogKeys.USER: str(),
			PublishLogKeys.WORKFILE: str(),
			PublishLogKeys.ASSETNAME: str(),
			PublishLogKeys.RECORD: str(),
			PublishLogKeys.APP:str(),
			PublishLogKeys.DESCRIPTION:str()
		}.copy()

	def create_new_log(self, username=str, workfile=str, assetName=str, app=str, description=str):
		newRecord = self.LOG_METADATA()
		nextVersion = self.get_version() + 1
		newRecord[PublishLogKeys.VERSION] = nextVersion
		newRecord[PublishLogKeys.USER] = username
		newRecord[PublishLogKeys.WORKFILE] = workfile
		newRecord[PublishLogKeys.ASSETNAME] = assetName
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
