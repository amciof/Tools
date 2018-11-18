
from .MapElements import Road, Town, Market, Storage

import networkx as nx
import json


class Map:

	##init section
	def __init__(self, jsonLogin, jsonMap):
		pass

	#graph init
	def __getGraphLayout(self, jsonGraph):
		MAGIC_CONST = 5

		graph = nx.Graph()

		for point in jsonGraph['points']:
			graph.add_node(point['idx'])

		for edge in jsonGraph['lines']:
			u, v = edge['points']
			graph.add_edge(u, v)

		pos = nx.spring_layout(graph, iterations = MAGIC_CONST * len(jsonGraph['points']))

		return pos

	def __getGraphRepresentation(self, jsonGraph):

		vertexes = jsonGraph['points']
		edges    = jsonGraph['lines']

		bases = {vertex['idx'] : None for vertex in vertexes}
		roads = {vertex['idx'] : {}   for vertex in vertexes}
		for edge in edges.values():
			idx, length, uv = edge
			u, v = uv

			self.roads[u][v] = length
			self.roads[v][u] = length

		return bases, roads


	##state
	def setBaseColor(idx, color):
		pass