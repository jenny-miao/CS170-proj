import networkx as nx
from parse import *
import random

g = nx.complete_graph(100)

#g.add_node(2)
#g.add_node(5)

#g.add_edge(2, 5)

#g.add_edge(4, 1)

#g.add_edge(1,2)

for u,v in g.edges():
    g.add_edge(u,v, weight=float(round(random.uniform(1.00,100.00),3)))

print(nx.info(g))

path = "/Users/reyclydevillasenor/Desktop/100.in"
write_input_file(g, path)
