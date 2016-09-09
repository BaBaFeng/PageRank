# -*- coding: utf8 -*-

import re
import csv
import operator
import networkx as networkx


class Parse():

    def __init__(self, filename, isDirected=None):
        self.filename = filename
        self.isDirected = isDirected

        self.parse()

        self.gdata

    def parse(self):
        reader = csv.reader(open(self.filename, 'r'), delimiter=',')
        self.data = [row for row in reader]

        print("Reading and parsing the data into memory...")
        if self.isDirected:
            self.parse_directed()
        else:
            self.parse_undirected()

    def parse_undirected(self):
        G = networkx.Graph()
        nodes = set([row[0] for row in self.data])
        edges = [(row[0], row[2]) for row in self.data]

        num_nodes = len(nodes)
        rank = 1 / float(num_nodes)
        G.add_nodes_from(nodes, rank=rank)
        G.add_edges_from(edges)
        self.gdata = G

        return G

    def parse_directed(self):
        DG = networkx.DiGraph()

        for i, row in enumerate(self.data):
            node_a = self.format_key(row[0])
            node_b = self.format_key(row[2])
            val_a = self.digits(row[1])
            val_b = self.digits(row[3])

            DG.add_edge(node_a, node_b)
            if val_a >= val_b:
                DG.add_path([node_a, node_b])
            else:
                DG.add_path([node_b, node_a])

        self.gdata = DG

        return DG

    def digits(self, val):
        return int(re.sub("\D", "", val))

    def format_key(self, key):
        key = key.strip()
        if key.startswith('"') and key.endswith('"'):
            key = key[1:-1]
        return key


class PageRank:

    def __init__(self, graph, directed=None):
        self.graph = graph
        self.V = len(self.graph)
        self.d = 0.85
        self.directed = directed
        self.ranks = dict()

    def rank(self):
        for key, node in self.graph.nodes(data=True):
            if self.directed:
                self.ranks[key] = 1 / float(self.V)
            else:
                self.ranks[key] = node.get('rank')

        for _ in range(10):
            for key, node in self.graph.nodes(data=True):
                rank_sum = 0
                if self.directed:
                    neighbors = self.graph.out_edges(key)
                    for n in neighbors:
                        outlinks = len(self.graph.out_edges(n[1]))
                        if outlinks > 0:
                            rank_sum += (1 / float(outlinks)) * self.ranks[n[1]]
                else:
                    neighbors = self.graph[key]
                    for n in neighbors:
                        if self.ranks[n] is not None:
                            outlinks = len(self.graph.neighbors(n))
                            rank_sum += (1 / float(outlinks)) * self.ranks[n]

                # actual page rank compution
                self.ranks[key] = ((1 - float(self.d)) * (1 / float(self.V))) + self.d * rank_sum


if __name__ == '__main__':
    graph = Parse("polblogs.csv").gdata
    p = PageRank(graph)
    p.rank()
    sorted_r = sorted(p.ranks.items(), key=operator.itemgetter(1), reverse=True)
    for tup in sorted_r:
        print('{0:8} {1} {2:10}'.format(str(tup[0]), ":", tup[1]))
