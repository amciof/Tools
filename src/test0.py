
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel, QTextEdit, QPushButton

from PyQt5.QtGui  import QIcon, QPainter, QColor, QBrush

from PyQt5.QtCore import Qt

import random


class CustomWidget(QWidget):

	def __init__(self, parent):
		QWidget.__init__(self, parent)

		self.setGeometry(0, 0, parent.size().width(), parent.size().height())

		self.login        = QTextEdit(self)
		#self.password     = QTextEdit(self)
		self.submitButton = QPushButton(self)

		self.submitButton.setGeometry(100, 300, 50, 50)
		self.submitButton.setText('Pingas')
		self.submitButton.clicked.connect(self.submit)

	def submit(self):
		print('submit')
		print(self.login.toPlainText())
		self.login.clear()

	def mousePressEvent(self, event):
		print('From custom widget')
		if event.button() == 1:
			self.hide()


class App(QMainWindow):

	def __init__(self, x0, y0, w, h):
		QMainWindow.__init__(self)

		self.setGeometry(x0, y0, w, h)

		self.widget = CustomWidget(self)

		self.show()

	def mousePressEvent(self, event):
		print('MainWindow')
		if event.button() == 1:
			self.widget.show()


app = QApplication(sys.argv)
ex  = App(200, 200, 1280, 720)
sys.exit(app.exec_())