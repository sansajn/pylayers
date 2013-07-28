# -*- coding: utf-8 -*-
# testy pre osmgraph_bidi_file.py

import sys, os

# import osmhraph modules
path = os.path.abspath(
	os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
	sys.path.insert(1, path)
del path

import osmgraph_bidi_file


def main():
	passed = 0
	failed = 0
	failed_tests = []
	tests = [test_read_header, test_read_nodes, test_read_vertices,
		test_read_edges]

	for test in tests:
		if test('data/romanova.bgrp'):
			passed += 1
		else:
			failed += 1
			failed_tests.append(test.__name__)

	if passed == len(tests):
		print 'all tests passed'
	else:
		print '%d tests failed' % (failed, )
		for test in failed_tests:
			print '  %s' % (test, )
		
	print 'done!'


def test_read_header(fname):
	grp = osmgraph_bidi_file.graph_file(fname)
	header = grp.read_header()

	if header['vertices'] != 170:
		return False

	if header['edges'] != 371:
		return False

	if header['bounds'] != ((481111316, 171071011), (481172491,	171162742)):
		return False

	if header['edge_table_idx'] != 0x570:
		return False

	if header['vertex_table_idx'] != 0x1ca0:
		return False

	print 'test_read_header done'
	return True

def test_read_nodes(fname):
	nodes = [0, 99, 169]
	expected = {0:(481144173, 171096828), 99:(481119139, 171122380), 
		169:(481171779, 171121477)}

	grp = osmgraph_bidi_file.graph_file(fname)

	for nidx in nodes:
		node = grp.read_node(nidx)
		if node != expected[nidx]:
			return False

	print 'test_read_nodes done'
	return True

def test_read_vertices(fname):
	vids = [0, 99, 169]
	expected = {0:0x570, 99:0x1298, 169:0x1c80}

	grp = osmgraph_bidi_file.graph_file(fname)
	header = grp.read_header()
	vtable = grp.read_vtable(header)

	for vid in vids:
		if vtable[vid] != expected[vid]:
			return False

	print 'test_read_vertices done'
	return True

def test_read_edges(fname):
	vids = [169, ]
	expected = {169:(4, (56, 0, 8, 24)), }

	grp = osmgraph_bidi_file.graph_file(fname)
	header = grp.read_header()
	vtable = grp.read_vtable(header)

	for vid in vids:
		edges = grp.read_edges(header, vtable, vid)
		if len(edges) != expected[vid][0]:
			return False
		if	edges[-1] != expected[vid][1]:
			return False

	print 'test_read_edges done'
	return True


if __name__ == '__main__':
	main()

