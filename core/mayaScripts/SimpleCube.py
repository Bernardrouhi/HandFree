import sys
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds

# try:
def run():
	# get scene file
	file_path = sys.argv[1]

	# Open Scene
	cmds.file(file_path, open=True)

	#-------------- Script --------------

	cmds.polyCube( d=10, h=10 , w=10)
	cmds.polyCube( d=10, h=10 , w=10)
	cmds.polyCube( d=10, h=10 , w=10)
	cmds.polyCube( d=10, h=10 , w=10)
	cmds.polyCube( d=10, h=10 , w=10)

	#------------------------------------

	# Save Scene
	cmds.file(save=True, force=True)

run()
maya.standalone.uninitialize()
# except Exception as e:
# 	sys.stdout.write(1)