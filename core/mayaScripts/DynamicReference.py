import sys
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds

def run():
	# get scene file
	file_path = sys.argv[1]

	# Open Scene
	cmds.file(file_path, open=True)

	#-------------- Script --------------

	DynamicVariable = "$DYNAMIC_ROOT"
	publish_dir = os.environ["HF_PUBLISH_DIR"]
	Work_dir = os.environ["HF_WORK_DIR"]
	os.environ["DYNAMIC_ROOT"] = publish_dir

	references = cmds.ls(references=True)
	for each in references:
		name = os.path.normpath(cmds.referenceQuery(each, filename=True))
		newName = name.replace(os.path.normpath(publish_dir),DynamicVariable)
		newName = newName.replace(os.path.normpath(Work_dir),DynamicVariable)
		cmds.file(newName, loadReference=each)

	#------------------------------------

	# Save Scene
	cmds.file(save=True, force=True)

run()
maya.standalone.uninitialize()