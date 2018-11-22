
from PyQt5.QtGui import QPainter, QColor, QPen

import numpy as np


class Player:

	##init
	def __init__(self, jsonLogin):
		self.home    = jsonLogin['home']['post_idx']
		self.idx     = jsonLogin['idx']
		self.inGame  = jsonLogin['in_game']
		self.name    = jsonLogin['name']
		self.rating  = jsonLogin['rating']
		#self.town
		self.trains  = [train['idx'] for train in jsonLogin['trains']]

	##Player logic
	#nothing here)
