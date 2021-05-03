import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_score
import sys
from os.path import basename, normpath
import glob

from gurobipy import *
import gurobipy as gp

def solve(G):
    """
    Args:
        G: networkx.Graph
    Returns:
        c: list of cities to remove
        k: list of edges to remove
    """
    #assign k and c parameters based on size of graph
    if (G.number_of_nodes() <= 30):
    	k_num = 15
    	c_num = 1
    elif (G.number_of_nodes() <= 50):
    	k_num = 50
    	c_num = 3
    else:
    	k_num = 100
    	c_num = 5

    #check s to t is still connected
    #assert G.number_of_nodes() - 1 in nx.algorithms.dag.descendants(G, 0)

    m = gp.Model("help")

    #we create edge dict of (e, i) where e represents edge (u,v) and i=0, or 1, representing if we delete it or not.
    edges = {}
    for (u,v) in G.edges():
    	edges[(u,v)] = m.addVar(vtype = GRB.BINARY, name = "edges")

    edge_keys = list(edges.keys())
    edge_vals = list(edges.values())

    #we make a dict of vertices (v, i), where v is a vertex in G, and i represents if its deleted or not.
    vertices = {}
    for v in G.nodes():
        vertices[v] = m.addVar(vtype = GRB.BINARY, name = "vertices")

    #s and t cannot be deleted
    m.addConstr(vertices[0] == 1)
    m.addConstr(vertices[G.number_of_nodes() - 1] == 1)
    
    m.update()
    print(vertices[0])
    
    #if a vertex is deleted, then its edges are deleted
    #for i in range(G.number_of_nodes()):
    #	for j in range(len(edge_vals)):
    #		if (i in edge_keys[j]):
    #			m.addConstr((vertices[i] == 0) >> edges[edge_keys[j]] == 0)

    m.update()

    edgelen=0
    for e,i in edges:
        if i==1:
            edgelen +=1

    m.addConstr(edgelen >= G.number_of_edges() - k_num)
    m.addConstr(sum(vertices.values()) >= G.number_of_nodes() - c_num)

    m.update()
   
    #need constraint for s and t connectivity (and overall graph connectivity?)

    d_edges = [e for e, i in edges if i==0] 

    d_vertices = []
    for v in range(G.number_of_nodes()):
    	if vertices[v] == 0:
    		d_vertices.add(v)

    d_vertices = [v for v, i in vertices if i==0]

    m.setObjective(calculate_score(G, d_vertices, d_edges), GRB.MAXIMIZE)
    m.optimize()

    pass


# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

if __name__ == '__main__':
    assert len(sys.argv) == 2
    path = sys.argv[1]
    G = read_input_file(path)
    c, k = solve(G)
    assert is_valid_solution(G, c, k)
    print("Shortest Path Difference: {}".format(calculate_score(G, c, k)))
    write_output_file(G, c, k, 'outputs/small-1.out')


# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
# if __name__ == '__main__':
#     inputs = glob.glob('inputs/*')
#     for input_path in inputs:
#         output_path = 'outputs/' + basename(normpath(input_path))[:-3] + '.out'
#         G = read_input_file(input_path)
#         c, k = solve(G)
#         assert is_valid_solution(G, c, k)
#         distance = calculate_score(G, c, k)
#         write_output_file(G, c, k, output_path)
