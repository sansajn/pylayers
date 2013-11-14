# -*- coding: utf-8 -*-
# Prečíta graf vygenerovaný programom 'osm/graph/simple_graph'.
import struct

class graph_file:
	def __init__(self, fname):
		self._fgraph = open(fname, 'rb')

	def __del__(self):
		self._fgraph.close()

	def read_header(self):
		self._fgraph.seek(0)
		d = self._fgraph.read(32)
		unpacked = struct.unpack('<IIiiiiII', d)
		return {
			'vertices': unpacked[0],
			'edges': unpacked[1],
			'bounds': ((unpacked[2], unpacked[3]), (unpacked[4], unpacked[5])),
			'edge_idx': unpacked[6],
			'itable_idx': unpacked[7]
		}

	def read_itable(self, header):
		'Precita incidencnu tabulku (adjacency list).'
		n_verts = header['vertices']
		self._fgraph.seek(header['itable_idx'])
		d = self._fgraph.read(4*n_verts)
		itable = struct.unpack('<%dI' % n_verts, d)
		return itable

	def read_edges(self, header, itable, idx):
		if itable[idx] == 0xffffffff:
			return []

		next_offset = self._next_valid(itable, idx)
		edges_size = next_offset - itable[idx]
		if next_offset == 0xffffffff:
			edges_size = header['itable_idx'] - itable[idx]

		self._fgraph.seek(itable[idx])
		d = self._fgraph.read(edges_size)

		edges = []
		n_edges = edges_size/9
		for i in range(0, n_edges):
			e = struct.unpack('iib', d[9*i:9*i+9])
			edges.append(e)

		return edges

	def read_vertex(self, idx):
		self._fgraph.seek(32+8*idx)
		d = self._fgraph.read(8)
		return struct.unpack('ii', d)

	def _next_valid(self, itable, idx):
		while idx < len(itable)-1:
			idx += 1
			if itable[idx] != 0xffffffff:
				return itable[idx]
		return 0xffffffff
