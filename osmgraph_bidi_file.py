# -*- coding: utf-8 -*-
# Podpora pre čítanie obojsmerného grafu vygenerovaného programom
# 'osmut/graph/graph_bidi_dijkstra'.
import struct

class graph_file:
	EDGE_SIZE = 8
	
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
			'edge_table_idx': unpacked[6],
			'vertex_table_idx': unpacked[7]
		}

	def read_vtable(self, header):
		'Precita tabulku vrcholou grafu (adjacency list).'
		n_verts = header['vertices']
		self._fgraph.seek(header['vertex_table_idx'])
		d = self._fgraph.read(4*n_verts)
		vtable = struct.unpack('<%dI' % n_verts, d)
		return vtable

	def read_edges(self, header, vtable, idx):
		'Prečíta a vráti incidenčné hrany vrchola \c idx.'
		if vtable[idx] == 0xffffffff:
			return []

		edges_size = self._adjacent_edges_size(header, vtable, idx)
		
		self._fgraph.seek(vtable[idx])
		d = self._fgraph.read(edges_size)

		edges = []
		n_edges = edges_size/8  # 8 means for graph_file.EDGE_SIZE
		for i in range(0, n_edges):
			unpacked = struct.unpack('II', d[8*i:8*i+8])
			e = (
				unpacked[0],  # target
				unpacked[1] & (2**2-1),  # direction
				(unpacked[1] >> 2) & (2**6-1),  # type
				(unpacked[1] >> 8) & (2**24-1)  # distance
			)
			edges.append(e)

		return edges
	
	def num_edges(self, header, vtable, vid):
		'Vrati pocet hran vrchola \c vid.'
		return self._adjacent_edges_size(header, vtable, vid)/EDGE_SIZE

	def read_node(self, idx):
		self._fgraph.seek(32+8*idx)
		d = self._fgraph.read(8)
		return struct.unpack('ii', d)
	
	def _adjacent_edges_size(self, header, vtable, vid):
		next_v_offset = self._next_valid(vtable, vid)
		edges_size = next_v_offset - vtable[vid]
		if next_v_offset == 0xffffffff:
			edges_size = header['vertex_table_idx'] - vtable[vid]
		return edges_size

	def _next_valid(self, vtable, idx):
		while idx < len(vtable)-1:
			idx += 1
			if vtable[idx] != 0xffffffff:
				return vtable[idx]
		return 0xffffffff
