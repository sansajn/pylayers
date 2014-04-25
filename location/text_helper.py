# -*- coding: utf-8 -*-
__author__ = 'Adam Hlavatovič'

def scanf(s, delim, typelst):
	return [f(c) for c,f in zip(s.split(delim), typelst)]

def textread(fname, delim, typelst):
	'''\example rows = textread('test.txt', ',', [int, float, float])'''
	rows = []
	f = open(fname, 'r')
	for ln in f:
		rows.append(scanf(ln, delim, typelst))
	f.close()
	return rows
