#author: Peter Barnes
#licence: GPLv3
#git: github.com/swanseamakerhub/rfid-register

import sys, mainwindow, time, logging
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from connect import *

GPIO.setwarnings(False)
reader = SimpleMFRC522()

class threadRead(QThread): #background thread that polls RFID reader for cards
	signal = pyqtSignal('PyQt_PyObject')

	def __init__(self):
		QThread.__init__(self)

	def __del__(self):
		self.wait()

	def run(self):
		while True: #runs thread continously
			try:
				id,text = reader.read()
			finally:
				print(id)
				self.signal.emit(id)

			self.sleep(0.1)

class MainWindow(QMainWindow, mainwindow.Ui_MainWindow):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self) # gets defined in the UI file
		self.shortcut_close = QShortcut(QKeySequence('Esc'), self) #press escape to close app
		self.shortcut_close.activated.connect(lambda x:app.quit())
		self.thread = threadRead()
		self.thread.signal.connect(self.getUser)

	def fillRegister(self,results):
		cursor2 = conn.cursor(mariadb.cursors.DictCursor)
		for row in results:
			now = datetime.now()
			timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
			cursor2.execute("INSERT INTO register(DateTime,UserID) VALUES (%s,%s);",(timestamp,row['UserID'],))
			conn.commit()
			print(cursor2._last_executed)
		cursor2.close()

	def getUser(self,id):
		cursor = conn.cursor(mariadb.cursors.DictCursor)
		cursor.execute("SELECT * FROM users WHERE TagID=%s;",(id,))
		results = cursor.fetchall()
		if(cursor.rowcount == 1):
			for row in results:
				welcomeMsg = "Welcome " + row['FirstName']
			self.lblStatus.setText(welcomeMsg)
			self.fillRegister(results)
		else:
			self.lblStatus.setText("User not found")
		cursor.close()

def main():
	# a new app instance
	app = QApplication(sys.argv)
	form = MainWindow()
	form.showFullScreen()
	form.thread.start()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
