#!/usr/bin/env python
#
#       filename
#
#       Copyright 2010 John Tyree <johntyree@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


from random import randrange, randint
import itertools as it
import igraph as ig
import sys
import subprocess

def vertexlist(g):
    l = set(it.chain.from_iterable(g.get_edgelist()))
    return sorted(list(l))

def colorgraph(g, c):
    g.es["color"] = list(it.repeat(c, g.ecount()))
    g.vs["color"] = list(it.repeat(c, g.vcount()))
    return g

def get_eattrs(g):
    attrs = dict(zip(g1.get_edgelist(), repeat(dict)))
    for x in g.es:
        attrs[x.tuple].update(x.attributes())
    return attrs

def get_vattrs(g):
    vertexindex = sorted([x.index for x in g.vs])
    attrs = dict(zip(g1.get_edgelist(), repeat(dict)))
    for x in g.vs:
        attrs[x.index].update(x.attributes())
    return attrs

def repeat(f):
    while 1: yield f()

def deep_update(d1,d2):
    for (k,v) in d2.items():
        print (k,v)
        if '__iter__' in dir(v):
            if not '__iter__' in dir(d1[k]):
                d1[k] = {}
            d1[k] = deep_update(d1[k],v)
        else:
            d1[k] = v
    return d1

def apply_attrs(g, eattrs, vattrs):
    for e in g.es:
        for k,v in eattrs.get(e.tuple).items(): e[k] = v
    for vertex in g.vs:
        for k,v in vattrs.get(vertex.index).items(): vertex[k] = v
    return g.simplify()

def overlay_attrs(g1,g2):
    '''Lay g2 over g1, overwriting information as necessary.
    Return only the eattr and vattr dicts.'''
    eattrs = deep_update(get_eattrs(g1), get_eattrs(g2))
    vattrs = deep_update(get_vattrs(g1), get_vattrs(g2))
    return (eattrs, vattrs)

def overlay(g1,g2):
    def repeat(f):
        while 1: yield f()
    edgetuples = set(it.chain(g1.get_edgelist(),g2.get_edgelist()))
    vertexindex = sorted(set([x.index for x in it.chain(g1.vs,g2.vs)]))
    eattrs = dict(zip(edgetuples, repeat(dict)))
    vattrs = dict(zip(vertexindex, repeat(dict)))
    for x in it.chain(g1.es, g2.es):
        eattrs[x.tuple].update(x.attributes())
        #print eattrs
    for x in it.chain(g1.vs, g2.vs):
        vattrs[x.index].update(x.attributes())
    g3 = g1.union(g2).simplify()
    for e in g3.es:
        for k,v in eattrs.get(e.tuple).items(): e[k] = v
    for vertex in g3.vs:
        for k,v in vattrs.get(vertex.index).items(): vertex[k] = v
    return g3.simplify()


def read_comm2edges(fin):
    '''Read in the linkcomm output and build community edgelist.
       Return [(len, edgelist)]'''
    ## index 0 is a tmp var
    topk = list(it.repeat(0, 5+1))
    g = ig.Graph()
    comm = []
    for i in fin.readlines():
        c = i.strip().split()
        el = [tuple(map(int, x.split(','))) for x in c[1:]]
        comm.append((len(el), el))
    return comm

def p(graph):
    #
    #print("pagerank", graph.pagerank())
    ## Looks like per-edge attributes aren't working?
    ig.plot(graph, layout=graph.layout('kk'),
            target='graph.png', vertex_label="",
            edge_width=0.3)
    #ig.plot(graph, layout=graph.layout('grid_fr'),
    #        target='graph.png', vertex_label="", edge_width=0.3)
    #ig.plot(graph, layout=graph.layout('kamada_kawai'), target='graph.png')
    subprocess.Popen(['feh', 'graph.png'])

def test():
    colors = dict(enumerate(("blue", "green", "orange", "purple", "black", "pink")))
    graph = ig.Graph.Full(9)
    graph2 = ig.Graph.Full(7)
    graph.es['color'] = ['green'] * graph.ecount()
    graph.es['thickness'] = [2.5] * graph.ecount()
    graph.vs['color'] = ['green'] * graph.vcount()
    graph2.es['color'] = ['blue'] * graph2.ecount()
    graph2.vs['color'] = ['blue'] * graph2.vcount()
    g = overlay(graph,graph2)
    #g.es['color'] = [color_dict[comm] for comm in g.cs['comm']]
    p(g)
    #graph.write_edgelist(sys.stdout)

def visualize(fin, d, k=5):
    comm = sorted(read_comm2edges(fin), reverse=True)
    el = sorted(reduce(lambda x,y: (x[0], x[1]+y[1]), comm)[1])
    #comm = sorted([(4,[(1,2),(0,3),(0,4)]), (1, [(2,3)])], reverse=True)
    colors = it.cycle(("blue", "green", "orange", "red", "pink", "black"))
    graph = ig.Graph(edges = el)#, edge_attrs = {'color': list(it.repeat("red", len(el))), 'edge_width': list(it.repeat(1, len(el))), })
    graph.es['name'] = [None] * graph.ecount()
    graph.vs['label'] = d
    for c in reversed(comm[:k]):
        color = colors.next()
        el = graph.es([i for i,x in enumerate(graph.es) if x.tuple in c[1]])
        vl = graph.vs(set([item for sublist in el for item in sublist.tuple]))
        #el['color'] = [c] * len(el)
        vl['color'] = [color] * len(vl)
        el['edge_width'] = [3] * len(el)

    # Remove nodes that are not connected
    l = enumerate(graph.outdegree())
    unconnecteds = [x for x,_ in filter(lambda x: x[1] == 0,l)]
    graph.delete_vertices(unconnecteds)
    return graph

def main():
    #graph = visualize(sys.stdin, 5)
    #graph = visualize(open('cpp/karate_maxS0.333333_maxD0.284758.comm2edges.txt') , 5)
    #graph = visualize(open('cpp/lesmis_maxS0.333333_maxD0.574285.comm2edges.txt') , 1)
    d = []
    with open(sys.argv[2]) as f:
        for line in f:
            tok = line.split()
            d.append(tok[1])

    graph = visualize(open(sys.argv[1]), d, 3)
    p(graph)
    #test()
    #ig.plot(graph, layout=graph.layout_fruchterman_reingold())
    #graph.write_edgelist(sys.stdout)
    return 0

if __name__ == '__main__': main()
