import sys
sys.path.append('./..')
import cluster 

c = cluster.base_cluster()
c.insert(1)
c.insert(3)
c.insert(5)
c.insert(7)

print '[1 3 5 7] > ',
for e in c:
	print e, 

print 'cluster size: %d' % (len(c), )

