
from PyQt5.QtGui import QPainter, QColor, QPen

import numpy as np


class Player:

	def __init__(self, jsonLogin):
		self.home    = jsonLogin['home']['idx']
		self.idx     = jsonLogin['idx']
		self.inGame  = jsonLogin['in_game']
		self.name    = jsonLogin['name']
		self.rating  = jsonLogin['rating']
		self.trains  = [train['idx'] for train in jsonLogin['trains']]

	def getAllIdx(self):

		return self.trains
