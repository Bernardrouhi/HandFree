import os

class HandFreeENV():
	WORK_DIR = 'HF_WORK_DIR'
	PUBLISH_DIR = 'HF_PUBLISH_DIR'
	PROJECT_NAME = 'HF_PROJECT_NAME'
	ASSET_NAME = 'HF_ASSET_NAME'
	ASSET_TYPE = 'HF_ASSET_TYPE'
	ASSET_SPACE = 'HF_ASSET_SPACE'
	ASSET_CONTAINER = 'HF_ASSET_CONTAINER'
	HFP_FILE = 'HFP_FILE'
	DYNAMIC_ROOT = 'DYNAMIC_ROOT'

def is_Env(key=str):
	'''Check if Key exists in environment variables.

		Args:
			key (str): Name of environment variable.

		Return:
			(boolean): True if exists, otherwise False.
	'''
	return True if key in os.environ else False

def get_Env(key_name=str):
	'''Get from environment variables.

		Args:
			key_name (str): Name of the environment variable.

		Return:
			(str): Value of the environment variable.
	'''
	return os.getenv(key_name, "")

def set_Env(key_name=str, value_name=str):
	'''Register a new key and value into environment variables.

		Args:
			key_name (str): Name to register in environment variable.
			value_name (str): Value to store in the Name.
		
		Return: None
	'''
	os.environ[key_name] = value_name

def del_Env(key_name=str):
	'''Delete from environment variables.

		Args:
			key_name (str): Name of environment variable.

		Return: None
	'''
	if is_Env(key_name):
		del os.environ[key_name]

def check_hfp_file(projectfile=str()):
	_projectfile = str()
	if projectfile:
		_projectfile = os.path.normpath(projectfile)
		if os.path.isfile(_projectfile) and _projectfile.lower().endswith(".hfp"):
			set_Env(key_name=HandFreeENV.HFP_FILE,value_name=_projectfile)
			print ("-----Loaded hfp from File Path-----")
			return _projectfile
	return ""

def check_hfp_env():
	result = get_Env(key_name=HandFreeENV.HFP_FILE)
	if result:
		_projectfile = os.path.normpath(result)
		if os.path.isfile(_projectfile) and _projectfile.lower().endswith(".hfp"):
			_projectfile = os.path.normpath(result)
			print ("-----Loaded hfp from Environment Variable-----")
			return _projectfile
	else:
		set_Env(key_name=HandFreeENV.HFP_FILE, value_name="")
	return ""