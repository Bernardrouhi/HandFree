import env_handler
reload(env_handler)
from env_handler import HandsFreeENV, get_Env, set_Env
from PySide2.QtCore import (Signal, QObject)

class Pipeline(object):
	def __init__(self):
		object.__init__(self)

	def get_ProjectName(self):
		'''Get the project name from environment variables.

			Return:
				(str): Name of project.
		'''
		return get_Env(HandsFreeENV.PROJECT_NAME)
	def set_ProjectName(self, project_name=str):
		'''Set the project name in environment variables.

			Args:
				project_name (str): Name of the project.
		'''
		set_Env(key_name=HandsFreeENV.PROJECT_NAME, value_name=project_name)
		return

	def get_AssetType(self):
		'''Get the asset type from environment variables.

			Return:
				(str): Name of Asset Type.
		'''
		return get_Env(HandsFreeENV.ASSET_TYPE)
	def set_AssetType(self, asset_type=str):
		'''Set the asset type in environment variables.

			Args:
				asset_type (str): Name of the Asse Type.
		'''
		set_Env(key_name=HandsFreeENV.ASSET_TYPE, value_name=asset_type)

	def get_AssetName(self):
		'''Get the asset name from environment variables.

			Return:
				(str): Name of the Asset.
		'''
		return get_Env(HandsFreeENV.ASSET_NAME)
	def set_AssetName(self, asset_name=str):
		'''Set the asset name in environment variables.

			Args:
				asset_name (str): Name of the Asset.
		'''
		set_Env(key_name=HandsFreeENV.ASSET_NAME, value_name=asset_name)

	def get_AssetSpace(self):
		'''Get the asset space from environment variables.

			Return:
				(str): Name of the AssetSpace.
		'''
		return get_Env(HandsFreeENV.ASSET_SPACE)
	def set_AssetSpace(self, asset_space=str):
		'''Set the asset space in environment variables.

			Args:
				asset_space (str): Name of the AssetSpace.
		'''
		set_Env(key_name=HandsFreeENV.ASSET_SPACE, value_name=asset_space)

	def get_AssetContainer(self):
		'''Get the asset container from environment variables.

			Return:
				(str): Name of the AssetContainer.
		'''
		return get_Env(HandsFreeENV.ASSET_CONTAINER)
	def set_AssetContainer(self, asset_container=str):
		'''Set the asset container in environment variables.

			Args:
				asset_container (str): Name of the AssetContainer.
		'''
		set_Env(key_name=HandsFreeENV.ASSET_CONTAINER, value_name=asset_container)

	def get_WorkDirectory(self):
		'''Get the work directory from environment variables.

			Return:
				(str): Path to work directory.
		'''
		return get_Env(HandsFreeENV.WORK_DIR)
	def set_WorkDirectory(self, directory=str):
		'''Set the work directory in environment variables.

			Args:
				directory (str): Path to work directory.
		'''
		set_Env(key_name=HandsFreeENV.WORK_DIR, value_name=directory)

	def get_PublishDirectory(self):
		'''Get the publish directory from environment variables.

			Return:
				(str): Path to publish directory.
		'''
		return get_Env(HandsFreeENV.PUBLISH_DIR)
	def set_PublishDirectory(self, directory=str):
		'''Set the publish directory in environment variables.

			Args:
				directory (str): Path to publish directory.
		'''
		set_Env(key_name=HandsFreeENV.PUBLISH_DIR, value_name=directory)
