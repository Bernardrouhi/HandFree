import os, subprocess, re, math
from PySide2.QtWidgets import (QAction, QFileDialog, QListWidget, QMenu, QSizePolicy,
						  QAbstractItemView, QTableWidget,QHeaderView, QHBoxLayout,
						  QTableWidgetItem, QComboBox, QDialog, QVBoxLayout, QLabel,
						  QLineEdit, QPushButton,QWidget, QProgressBar)
from PySide2.QtGui import (QRegExpValidator, QCloseEvent)
from PySide2.QtCore import (Qt, QPoint, QRegExp, QThread, Signal, QFile)


class CopyProgressDialog(QDialog):
	def __init__(self, parent=None, source=str, destination=str):
		super(CopyProgressDialog, self).__init__(parent)

		self._Source = source
		self._Destination = destination
		self._Sourcefile = QFile(self._Source)
		self._written = 0

		self.setMinimumSize(1, 1)
		self.resize(400, 50)

		# ------------- Main Layout --------------
		main_layout = QVBoxLayout(self)
		main_layout.setContentsMargins(5,5,5,5)
		main_layout.setSpacing(5)
		main_layout.setAlignment(Qt.AlignTop)
		self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

		# ------- Row -------
		# ----------------------------------------
		progress_layout = QHBoxLayout()
		progress_layout.setContentsMargins(0,0,0,0)
		progress_layout.setSpacing(3)
		progress_layout.setAlignment(Qt.AlignLeft)

		self.copyProgress = QProgressBar()
		self.copyProgress.setMinimum(0)
		# self.copyProgress.setMaximum(self._Sourcefile.size()/1024)
		self.copyProgress.setMaximum(100)
		self.copyProgress.setValue(0)

		progress_layout.addWidget(self.copyProgress)

		main_layout.addLayout(progress_layout)

		# ------- Row -------
		# ----------------------------------------
		size_layout = QHBoxLayout()
		size_layout.setContentsMargins(0,0,0,0)
		size_layout.setSpacing(3)
		size_layout.setAlignment(Qt.AlignLeft)

		self.total_size = QLabel(self.convert_size(self._Sourcefile.size()))
		self.saved_size = QLabel(self.convert_size(self._written))

		size_layout.addWidget(self.total_size)
		size_layout.addWidget(self.saved_size)

		main_layout.addLayout(size_layout)

		print (self._Sourcefile.size())


		self.setWindowTitle("Copying file...")
		self.copy()

	def convert_size(self, size_bytes):
		if size_bytes == 0:
			return "0Byte"
		size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
		i = int(math.floor(math.log(size_bytes, 1024)))
		p = math.pow(1024, i)
		s = round(size_bytes / p, 2)
		return "%s %s" % (s, size_name[i])

	def copy(self):
		self.copy_thread = CopyThread(parent=self, source=self._Source, destination=self._Destination)
		self.copy_thread.onPartDone.connect(self.update_progress)
		self.copy_thread.onCopyDone.connect(self.finished_copy)
		self.copy_thread.start()

	def update_progress(self, progress):
		self._written += progress
		self.copyProgress.setValue(progress * 100 / self._Sourcefile.size())
		self.saved_size.setText(self.convert_size(progress))

	def finished_copy(self, state):
		self.accept()

	def closeEvent(self, event=QCloseEvent):
		self.copy_thread.stop()

class CopyThread(QThread):

	onCopyDone = Signal(bool)
	onPartDone = Signal(int)

	def __init__(self, parent, source, destination):
		super(CopyThread, self).__init__(parent)
		self.source = source
		self.destination = destination

	def run(self):
		self.copy()
		self.onCopyDone.emit(True)

	def copy(self):
		source_size = os.stat(self.source).st_size
		copied = 0
		source = open(self.source, "rb")
		target = open(self.destination, "wb")

		blocksize = 1024*1024*2
		while True:
			chunk = source.read(blocksize)
			if not chunk:
				break
			target.write(chunk)
			copied += len(chunk)
			# self.onPartDone.emit(copied * 100 / source_size)
			self.onPartDone.emit(copied)

		source.close()
		target.close()

	def stop(self):
		self.terminate()