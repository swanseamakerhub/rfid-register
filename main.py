#author: Peter Barnes
#git: github.com/swanseamakerhub/rfid-register

import sys, mainwindow, time, logging
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence, QImage, QPalette, QBrush
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from connect import *
from threading import Timer

GPIO.setwarnings(False)
reader = SimpleMFRC522()

done = 0

class threadRead(QThread): #background thread that polls RFID reader for cards
	signal = pyqtSignal('PyQt_PyObject')

	def __init__(self):
		QThread.__init__(self)
	def __del__(self):
		self.wait()

	def run(self):
		global done
		while True: #runs thread continously
			print("starting thread")
			try:
				id,text = reader.read()
			finally:
				print(id)
				done = 0
				self.signal.emit(id)
				while (done == 0):
					pass

class MainWindow(QMainWindow, mainwindow.Ui_MainWindow):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setupUi(self) # gets defined in the UI file
		self.shortcut_close = QShortcut(QKeySequence('Esc'), self) #press escape to close app
		self.shortcut_close.activated.connect(lambda x:app.quit())
		self.thread = threadRead()
		self.thread.signal.connect(self.getUser)

		#graphics
		sImage = QImage("landing-page.png")
		palette = QPalette()
		palette.setBrush(QPalette.Window, QBrush(sImage))
		self.setPalette(palette)

	def waitForReset(self):
		#count to 3
		t = Timer(3.0, self.resetUI)
		t.start()

	def resetUI(self):
		global done
		sImage = QImage("landing-page.png")
		palette = QPalette()
		palette.setBrush(QPalette.Window, QBrush(sImage))
		self.setPalette(palette)
		self.lblStatus.setText("")
		done = 1 #flags the RFID reader to start reading again

	def fillRegister(self,results):
		cursor2 = conn.cursor(mariadb.cursors.DictCursor)
		for row in results:
			now = datetime.now()
			timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
			cursor2.execute("INSERT INTO register(DateTime,UserID) VALUES (%s,%s);",(timestamp,row['UserID'],))
			conn.commit()
			print(cursor2._last_executed)
		cursor2.close()

		self.waitForReset()

	def levelTextToID(self,levelText):
		switcher = {
			"Undergraduate": 1,
			"Postgraduate": 2,
			"Staff": 3,
			"Other": 4,
		}
		return switcher.get(levelText, "0")

	def courseTextToID(self,courseText):
		switcher = {
			"Aerospace Engineering": 1,
			"Chemical Engineering": 2,
			"Civil Engineering": 3,
			"Computer Science": 4,
			"Electrical and Electronic Engineering": 5,
			"Materials Engineering": 6,
			"Mathematics": 7,
			"Mechanical Engineering": 8,
			"Medical Engineering": 9,
			"EngD": 10,
			"PhD": 11,
			"Staff": 12,
			"Other": 13,
		}
		return switcher.get(courseText, "0")

	def enrollUser(self,results,id):
		firstName, okPressed = QInputDialog.getText(self, "Enrol User","Please enter your first name:", QLineEdit.Normal, "")
		lastName, okPressed = QInputDialog.getText(self, "Enrol User","Please enter your surname:", QLineEdit.Normal, "")
		studentNo, okPressed = QInputDialog.getInt(self, "Enrol User","Please enter your student number:", 0, 0, 9999999, 1)
		levelText = ("Undergraduate","Postgraduate","Staff", "Other")
		levelText, okPressed = QInputDialog.getItem(self, "Enrol User","Please select your level of study:", levelText, 0, False)
		levelID = self.levelTextToID(levelText)
		courseText = ("Aerospace Engineering", "Chemical Engineering", "Civil Engineering", "Computer Science", "Electrical and Electronic Engineering","Materials Engineering","Mathematics", "Mechanical Engineering", "Medical Engineering", "EngD", "PhD", "Staff", "Other")
		courseText, okPressed = QInputDialog.getItem(self, "Enrol User","Please select your discipline:", courseText, 0, False)
		courseID = self.courseTextToID(courseText)

		query = "INSERT INTO users (TagID,FirstName,LastName,StudentNo,LevelID,CourseID) VALUES ({},'{}','{}',{},{},{})".format(id,firstName,lastName,studentNo,levelID,courseID)

		cursor3 = conn.cursor(mariadb.cursors.DictCursor)
		cursor3.execute(query)
		conn.commit()
		print(cursor3._last_executed)
		cursor3.close()

		self.waitForReset()

	def getUser(self,id):

		sImage = QImage("background.png")
		palette = QPalette()
		palette.setBrush(QPalette.Window, QBrush(sImage))
		self.setPalette(palette)

		cursor = conn.cursor(mariadb.cursors.DictCursor)
		cursor.execute("SELECT UserID, FirstName FROM users WHERE TagID=%s;",(id,))
		results = cursor.fetchall()

		for row in results:
			welcomeMsg = "Welcome " + row['FirstName']

		if(cursor.rowcount == 1):
			self.lblStatus.setText(welcomeMsg)
			self.fillRegister(results)

		else:
			self.lblStatus.setText("User not found")
			self.enrollUser(results,id)
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
