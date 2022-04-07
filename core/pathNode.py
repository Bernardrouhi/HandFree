import os, json
class PathNode(object):
	def __init__(self, relative_path=str()):
		'''{AssetType}/{AssetContainer}{AssetName}/{AssetSpace}'''
		self._assetType = str()
		self._assetContainer = str()
		self._assetName = str()
		self._assetWorkspace = str()

		pathSections = relative_path.split(os.sep)
		if len(pathSections) >= 3:
			self._assetType = pathSections[0]
			self._assetContainer = pathSections[1:-1]
			self._assetName = pathSections[-2]
			self._assetWorkspace = pathSections[-1]

	def AssetType(self):
		return self._assetType

	def isValid(self):
		return True if self.AssetType() and self.AssetWorkspace() and self.AssetName() and self.AssetContainer() else False

	def AssetName(self):
		return self._assetName

	def AssetWorkspace(self):
		return self._assetWorkspace

	def AssetContainer(self):
		return os.path.join(*self._assetContainer)

	def __str__(self):
		return json.dumps({ "AssetType":self.AssetType(),
							"AssetContainer":self.AssetContainer(),
							"AssetName":self.AssetName(),
							"AssetWorkspace":self.AssetWorkspace()}, indent=4)