import os
import shutil
from maya import cmds
from maya import mel
from maya import OpenMayaUI as omui
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QWidget, QMessageBox)
from shiboken2 import wrapInstance
from style_handler import current_file_path

class MayaAPIs():
	MAYA2020 = 20200100

def selectObjects(nodes=list):
	'''
	Select objects in maya.

	Parameters
	----------
	nodes: (list)
		List of object's name.
	'''
	cmds.select(nodes, add=True)

def clearSelection():
	'''
	Clear Maya selection.
	'''
	cmds.select(clear=True)

def getActiveItems():
	return cmds.ls(selection=True, long=False)

def runMel(cmd=str):
	'''
	Run mel commands.

	Parameters
	----------
	cmd: (str)
		Commands in Mel language.
	'''
	if cmd:
		mel.eval(cmd)

def mayaNamespace():
	'''
	Get list of Maya namespaces.

	Return
	------
	out: (list)
		List of Maya namespaces.
	'''
	cmds.namespace(setNamespace=':')
	return cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)

def runPython(cmd=str):
	'''
	Run python commands.

	Parameters
	----------
	cmd: (str)
		commands in Python language.
	'''
	if cmd:
		try:
			exec(cmd)
		except SyntaxError as err:
			dial = QMessageBox()
			dial.setText(str(err))
			dial.setWindowTitle("Caution!")
			dial.setIcon(QMessageBox.Warning)
			dial.addButton('Ok', QMessageBox.RejectRole)
			dial.exec_()
		except Exception as err:
			dial = QMessageBox()
			dial.setText(str(err))
			dial.setWindowTitle("Caution!")
			dial.setIcon(QMessageBox.Warning)
			dial.addButton('Ok', QMessageBox.RejectRole)
			dial.exec_()

def maya_version():
	'''
	Get current maya versions
	'''
	return cmds.about(version=True)

def warningMes(msg):
	'''
	Print out warning message.

	Parameters
	----------
	msg: (str)
		message to show on console.
	'''
	cmds.warning(msg)

def errorMes(msg):
	'''
	Print out error message.

	Parameters
	----------
	msg: (str)
		message to show on console.
	'''
	cmds.error(msg)

def get_MayaWindow():
	'''
	Get the maya window.
	'''
	mayaMainWindowPtr = omui.MQtUtil.mainWindow()
	return wrapInstance(long(mayaMainWindowPtr), QWidget)

def get_MayaPanel(panelName=str):
	# graphEdtrPtr = omui.MQtUtil.findLayout("graphEditor1Window|TearOffPanel|graphEditor1")
	graphEdtrPtr = omui.MQtUtil.findLayout(panelName)
	mayaParent = omui.MQtUtil.getParent(long(graphEdtrPtr))
	return wrapInstance(long(graphEdtrPtr), QWidget)

def maya_api_version():
	'''Get the maya API version.
	'''
	return int(cmds.about(api=True))

def dock_window(dialog_class):
	try:
		# if cmds.lsUI(dialog_class.CONTROL_NAME):
		cmds.deleteUI(dialog_class.CONTROL_NAME)
		logger.info('removed workspace {}'.format(dialog_class.CONTROL_NAME))

	except:
		pass

	# building the workspace control with maya.cmds
	main_control = cmds.workspaceControl(dialog_class.CONTROL_NAME, ttc=["AttributeEditor", -1],iw=300, mw=True, wp='preferred', label = dialog_class.DOCK_LABEL_NAME)
	
	control_widget = omui.MQtUtil.findControl(dialog_class.CONTROL_NAME)
	control_wrap = wrapInstance(long(control_widget), QWidget)
	
	# control_wrap is the widget of the docking window and now we can start working with it:
	control_wrap.setAttribute(Qt.WA_DeleteOnClose)
	win = dialog_class(control_wrap)
	
	# after maya is ready we should restore the window since it may not be visible
	cmds.evalDeferred(lambda *args: cmds.workspaceControl(main_control, e=True, rs=True))

	return win.run()

def create_WorkSpaceControl(controlName=str, controlLabel=str):
	control_widget = omui.MQtUtil.findControl(controlName)
	if not control_widget:
		cmds.workspaceControl(
					controlName, 
					tabToControl=["AttributeEditor", -1], 
					initialWidth=300, 
					minimumWidth=True, 
					widthProperty='preferred', 
					label=controlLabel)

def delete_WorkSpaceControl(controlName=str):
	control_widget = omui.MQtUtil.findControl(controlName)
	if control_widget:
		control_wrap = wrapInstance(long(control_widget), QWidget)
		# control_wrap.setParent(None)
		control_wrap.close()
		# control_wrap.deleteLater()
		print ("DELETE")

def get_MayaControl(controlName=str):
	control_widget = omui.MQtUtil.findControl(controlName)
	control_wrap = wrapInstance(long(control_widget), QWidget)
	control_wrap.setAttribute(Qt.WA_DeleteOnClose)
	return control_wrap

def restore_WorkSpaceControl(workSpaceControl):
	cmds.evalDeferred(lambda *args: cmds.workspaceControl(workSpaceControl, e=True, rs=True))

def open_scene(scene_path=str):
	cmds.file(scene_path, open=True, force=True)

def create_EmptyScene():
	cmds.file(new=True, force=True) 

def rename_Scene(name=str):
	cmds.file(rename=name)

def save_Scene():
	cmds.file(force=True, type='mayaAscii', save=True ) 

def set_MayaProject(directory=str):
	# cmds.workspace(directory, openWorkspace=True)
	# cmds.workspace( saveWorkspace=True )
	mel.eval('setProject "{}"'.format(directory.replace('\\', '/')))
	# print(cmds.workspace(query=True, directory=True ))

def get_workspaceName():
	return "workspace.mel"

def copy_workspace(destination=str):
	workspace_file = os.path.normpath(os.path.join(current_file_path(), "resources", get_workspaceName()))
	if os.path.isdir(destination):
		shutil.copy(workspace_file,destination)

def reference_FileToScene(file_path=str, namespace=str):
	cmds.file(file_path , reference=True, ignoreVersion = True, namespace = namespace)

def import_FileToScene(file_path=str, namespace=str):
	cmds.file(file_path , i=True, ignoreVersion = True, namespace = namespace)

def set_worldspace():
	cmds.upAxis( axis='z', rotateView=True )