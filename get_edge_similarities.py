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
import numpy as np
from collections import defaultdict
from itertools import combinations # requires python 2.6+
from optparse import OptionParser

def swap(a,b):
    if a > b:
        return b,a
    return a,b

def swap_reverse((a, b)):
    if int(a) < int(b):
        return b,a
    return a,b

def read_edgelist(filename, delimiter=None, nodetype=str):
    """reads two-column edgelist, returns dictionary
    mapping node -> set of neighbors and a list of edges
    """
    adj = defaultdict(set) # node to set of neighbors
    edges = set()
    edge_index_map = {}
    ind = 0
    for line in open(filename, 'U'):
        L = line.strip().split(delimiter)
        ni,nj = nodetype(L[0]),nodetype(L[1]) # other columns ignored
        if ni != nj: # skip any self-loops...
            edges.add( swap(ni,nj) )
            adj[ni].add(nj)
            adj[nj].add(ni) # since undirected

        if int(ni) > int(nj):
            edge_index_map[(ni,nj)] = ind
        else:
            edge_index_map[(nj,ni)] = ind
        ind = ind + 1

    if verbose:
        print "edge_index_map:\n", edge_index_map        

    return dict(adj), edges, edge_index_map

def edge_similarities(adj, ea, eim):
    """Get all the edge similarities. Input dict maps nodes to sets of neighbors.
    Output is an edge distance matrix, where (eij,eik) entries correspond to (1-sim).
    """
    #num_edges = len(set([e for (e, _) in ea]) | set([e for (_, e) in ea]))
    num_edges = len(ea)
    esim = np.zeros((num_edges, num_edges))

    i_adj = dict((n, adj[n] | set([n])) for n in adj)  # node -> inclusive neighbors

    for n in adj: # n is the shared node

        if verbose:
            print "shared node: ", n

        if len(adj[n]) > 1:
            for i,j in combinations(adj[n],2): # all unordered pairs of neighbors

                edge_pair = swap( swap(i,n),swap(j,n) )
                inc_ns_i,inc_ns_j = i_adj[i],i_adj[j] # inclusive neighbors

                # compute Jaccard similarity coefficient
                sim = 1.0 * len(inc_ns_i & inc_ns_j) / len(inc_ns_i | inc_ns_j) 

                if verbose:
                    print "i: ", i
                    print "j: ", j
                    print "edge pair: ", edge_pair
                    print "inc_ns_i: ", inc_ns_i
                    print "inc_ns_j: ", inc_ns_j
                    print "sim: ", sim, " (dist: ", 1 - sim, ")"

                # populate upper triangle of matrix
                ei_index = eim[swap_reverse(swap_reverse(edge_pair[0]))]
                ej_index = eim[swap_reverse(swap_reverse(edge_pair[1]))]
             
                if verbose:
                    print "ei_index: ", ei_index
                    print "ej_index: ", ej_index
   
                if ei_index > ej_index:
                    esim[ei_index, ej_index] = 1-sim
                else:
                    esim[ej_index, ei_index] = 1-sim

    if verbose:
        print
    return esim

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
    An unweighted edgelist file where each line represents an edge:
    node_i <delimiter> node_j <newline>
    
Output: 
    A text file containing the edge distance matrix.
"""
    parser = MyParser(usage, description=description, epilog=epilog)
    parser.add_option("-d", "--delimiter", dest="delimiter", default=" ",
                      help="delimiter of input & output files [default: space]")
    parser.add_option("-o", "--output", dest="output", default=None,
                      help="name to use for output file")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                      help="display verbose messages")
    parser.add_option("-w", action="store_true", dest="very_verbose", default=False,
                      help="display very verbose messages")
                    
    # parse options:
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("incorrect number of arguments")
    delimiter = options.delimiter
    if delimiter == '\\t':
        delimiter = '\t'
    verbose = options.verbose
    very_verbose = options.very_verbose
    
    print "# loading network from edgelist..."
    basename = os.path.splitext(args[0])[0]
    adj,edges, edge_index_map = read_edgelist(args[0], delimiter=delimiter)
    
    if very_verbose:
        verbose = True
        print "num edges: ", len(edges)
        print "edges: ", edges
        print "adj: ", adj, "\n"
        print "edge index map: ", edge_index_map, "\n"

    print "# calculating edge similarities..."
    edge_sim = edge_similarities(adj, edges, edge_index_map)

    # write edge similarity matrix to file
    print "# writing Jacccard distance matrix to file..."

    if options.output:
        filename = options.output
    else:
        filename = "%s_edgedist.txt" % basename

    np.savetxt(filename, edge_sim, fmt='%-7.5f')
    print "# Edge distance matrix written to %s" % filename
