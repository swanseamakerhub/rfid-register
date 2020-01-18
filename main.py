import sys

#Qt Prereqs
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import pyqtSlot

# This is our window from QtCreator
import mainwindow

# RC522 Imports
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
import time
import logging

# RC522 Setup
logging.disable(logging.CRITICAL)
GPIO.setwarnings(False)
reader = SimpleMFRC522()

class MainWindow(QMainWindow, mainwindow.Ui_MainWindow):
	# access variables inside of the UI's file
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self) # gets defined in the UI file

		self.shortcut_close = QShortcut(QKeySequence('Esc'), self)
		self.shortcut_close.activated.connect(lambda x:app.quit())

		self.btnEnable.clicked.connect(self.on_click)

	def rfRead(self):
		try:
			id,text = reader.read()
	        	#print(id)
			if(id==811913388378):
				print("Welcome Peter")
			if(id==320200448433):
				print("Welcome Fred")
				self.lblStatus.setText("Welcome Fred")
		finally:
			time.sleep(0.01)

	@pyqtSlot()
	def on_click(self):
		self.rfRead()


def main():
 	# a new app instance
	app = QApplication(sys.argv)
	form = MainWindow()
	form.showFullScreen()
	sys.exit(app.exec_())

if __name__ == "__main__":
 main()
