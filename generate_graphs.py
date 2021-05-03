# import networkx as nx
# from parse import *
# import random

# G = nx.complete_graph(30)

# for u,v in G.edges():
#     G.add_edge(u, v, 1)

# print(nx.info(G))

# path = "/Users/jenn3/Desktop/CS170/proj/samples/30_equal.in"
# write_input_file(G, path)

import networkx as nx
from parse import *
import random

g = nx.complete_graph(30)

#g.add_node(2)
#g.add_node(5)

#g.add_edge(2, 5)

#g.add_edge(4, 1)

#g.add_edge(1,2)

num = float(round(random.uniform(1.00,100.00),3))

for u,v in g.edges():
	g.add_edge(u,v, weight=num)

print(nx.info(g))


path = "/Users/jenn3/Desktop/CS170/proj/samples/30_equal.in"
write_input_file(g, path)