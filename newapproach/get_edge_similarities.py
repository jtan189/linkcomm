#!/usr/bin/env python
# encoding: utf-8

# get_edge_similarities.py
# Joshua Tan
# Last Modified: 2013-12-16

# This file is based on:
# link_clustering.py
# Jim Bagrow, Yong-Yeol Ahn
# Last Modified: 2010-08-27

# Copyright 2008,2009,2010 James Bagrow, Yong-Yeol Ahn
# 
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os
from copy import copy
from operator import itemgetter
from heapq import heappush, heappop
from collections import defaultdict
from itertools import combinations, chain # requires python 2.6+
from optparse import OptionParser

def swap(a,b):
    if a > b:
        return b,a
    return a,b

def read_edgelist(filename, delimiter=None, nodetype=str):
    """reads two-column edgelist, returns dictionary
    mapping node -> set of neighbors and a list of edges
    """
    adj = defaultdict(set) # node to set of neighbors
    edges = set()
    for line in open(filename, 'U'):
        L = line.strip().split(delimiter)
        ni,nj = nodetype(L[0]),nodetype(L[1]) # other columns ignored
        if ni != nj: # skip any self-loops...
            edges.add( swap(ni,nj) )
            adj[ni].add(nj)
            adj[nj].add(ni) # since undirected
    return dict(adj), edges

def edge_similarities(adj):
    """Get all the edge similarities. Input dict maps nodes to sets of neighbors.
    Output is a list of decorated edge-pairs, (1-sim,eij,eik), ordered by similarity.
    """
    print "computing similarities..."
    i_adj = dict( (n,adj[n] | set([n])) for n in adj)  # node -> inclusive neighbors
    min_heap = [] # elements are (1-sim,eij,eik)
    for n in adj: # n is the shared node
        print("n: ", n)
        if len(adj[n]) > 1:
            for i,j in combinations(adj[n],2): # all unordered pairs of neighbors
                edge_pair = swap( swap(i,n),swap(j,n) )
                inc_ns_i,inc_ns_j = i_adj[i],i_adj[j] # inclusive neighbors
                S = 1.0 * len(inc_ns_i&inc_ns_j) / len(inc_ns_i|inc_ns_j) # Jacc similarity...

                i_index = int(i) - 1
                j_index = int(j) - 1
                #print("attrib i: ", i_index, "\n")
                #print("attrib j: ", j_index, "\n")
                both_have = 0
                either_has = 0
                for attr in range(0, len(ea[0])):
                    #print("attr: ", attr, "\n")
                    if ea[i_index][attr] == 1:
                        if ea[i_index][attr] == ea[j_index][attr]:
                            both_have = both_have + 1
                            either_has = either_has + 1
                        else:
                            either_has = either_has + 1
                    else:
                        if ea[i_index][attr] != ea[j_index][attr]:
                            either_has = either_has + 1
                if either_has != 0:
                    attr_sim = both_have / either_has
                else:
                    attri_sim = 0;

                #print("attrib similarity: ", attr_sim, "\n")

                alpha = 0.25
                S = (alpha * S) + ((1 - alpha) * attr_sim)

                heappush( min_heap, (1-S,edge_pair) )
    return [ heappop(min_heap) for i in xrange(len(min_heap)) ] # return ordered edge pairs


if __name__ == '__main__':
    # build option parser:
    class MyParser(OptionParser):
        def format_epilog(self, formatter):
            return self.epilog
    
    usage = "usage: python %prog [options] filename"
    description = """The link communities method of Ahn, Bagrow, and Lehmann, Nature, 2010:
    www.nature.com/nature/journal/v466/n7307/full/nature09182.html (doi:10.1038/nature09182)
    """
    epilog = """
    
Input:
  An edgelist file where each line represents an edge:
    node_i <delimiter> node_j <newline>
  if unweighted, or
    node_i <delimiter> node_j <delimiter> weight_ij <newline>
  if weighted.
    
Output: 
  Three text files with extensions .edge2comm.txt, .comm2edges.txt,
  and .comm2nodes.txt store the communities.
 
  edge2comm, an edge on each line followed by the community
  id (cid) of the edge's link comm:
    node_i <delimiter> node_j <delimiter> cid <newline>
  
  comm2edges, a list of edges representing one community per line:
    cid <delimiter> ni,nj <delimiter> nx,ny [...] <newline>

  comm2nodes, a list of nodes representing one community per line:
    cid <delimiter> ni <delimiter> nj [...] <newline>
  
  The output filename contains the threshold at which the dendrogram
  was cut, if applicable, or the threshold where the maximum
  partition density was found, and the value of the partition 
  density.
  
  If no threshold was given to cut the dendrogram, a file ending with
  `_thr_D.txt' is generated, containing the partition density as a
  function of clustering threshold.

  If the dendrogram option was given, two files are generated. One with
  `.cid2edge.txt' records the id of each edge and the other one with
  `.linkage.txt' stores the linkage structure of the hierarchical 
  clustering. In the linkage file, the edge in the first column is 
  merged with the one in the second at the similarity value in the 
  third column.
"""
    parser = MyParser(usage, description=description,epilog=epilog)
    parser.add_option("-d", "--delimiter", dest="delimiter", default=" ",
                      help="delimiter of input & output files [default: space]")
                    
    # parse options:
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    delimiter = options.delimiter
    if delimiter == '\\t':
        delimiter = '\t'
    
    print "# loading network from edgelist..."
    basename = os.path.splitext(args[0])[0]
    adj,edges = read_edgelist(args[0], delimiter=delimiter)
    print("edges", edges, "\n")
    print("adj", adj, "\n")

    print "# calculating edge similarities..."
    # edge_sim = edge_similarities(adj, edges)

    # # write edge similarity matrix to file
    # filename = "%s_edgesim.txt" % basename
    # f = open(filename,'w')
    # for s,D in list_D:
    #     print >>f, s, D
    # f.close()
    # print "# Edge similarity matrix written to %s" % filename
