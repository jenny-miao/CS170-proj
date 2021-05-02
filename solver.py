import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_score
import sys
from os.path import basename, normpath
import glob

import gurobipy as gp  
from gurobipy import GRB


def solve(G):
    """
    Args:
        G: networkx.Graph
    Returns:
        c: list of cities to remove
        k: list of edges to remove
    """
    #assign k and c parameters based on size of graph
    if (G.number_of_nodes <= 30):
    	k_num = 15
    	c_num = 1
    elif (G.number_of_nodes <= 50):
    	k_num = 50
    	c_num = 3
    else:
    	k_num = 100
    	c_num = 5

    # #returns a tuple (distance, path), where distance is the distance from source to target and path is a list representing the path from source to target.
    # distance, path = nx.single_source_dijkstra(G, 0, G.number_of_nodes() - 1)

    # #check s to t is still connected
    # assert G.number_of_nodes() - 1 in nx.algorithms.dag.descendants(G, 0)
    # assert nx.is_connected(G)

    m = gp.Model("help")
    edges = {}
    for (u,v) in G.edges():
    	edges[(u,v)] = m.addVars((u,v), vtype = GRB.BINARY, name = "edges")

    edge_keys = list(edges.keys())
    edge_vals = list(edges.values())
    # edges = m.addVars(G.edges(), vtype = GRB.BINARY, name = "edges")
    vertices = m.addVars(list(G.nodes()), vtype = GRB.BINARY, name = "vertices")

    m.addConstrs(sum(edges) >= G.number_of_edges() - k_num)
    m.addConstrs(sum(vertices) >= G.number_of_nodes() - c_num)

    #s and t cannot be deleted
    m.addConstrs(vertices[0] == 1)
    m.addConstrs(vertices[G.number_of_nodes - 1] == 1)
    
    #if a vertex is deleted, then its edges are deleted
    for i in range(G.number_of_nodes()):
    	for j in range(len(edge_vals)):
    		if (i in edge_keys[j]):
    			m.addConstrs((vertices[i] == 0) >> edges[edge_keys[j]] == 0)

    #need constraint for s and t connectivity (and overall graph connectivity?)

    m.setObjective(calculate_score(G, c_num, k_num), GRB.MAXIMIZE)

    # m.optimize()
    # pass


# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

# if __name__ == '__main__':
    # assert len(sys.argv) == 2
    # path = sys.argv[1]
    # G = read_input_file(path)
    # c, k = solve(G)
    # assert is_valid_solution(G, c, k)
    # print("Shortest Path Difference: {}".format(calculate_score(G, c, k)))
    # write_output_file(G, c, k, 'outputs/small-1.out')


# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
if __name__ == '__main__':
    inputs = glob.glob('inputs/*')
    for input_path in inputs:
        output_path = 'outputs/' + basename(normpath(input_path))[:-3] + '.out'
        G = read_input_file(input_path)
        c, k = solve(G)
        assert is_valid_solution(G, c, k)
        distance = calculate_score(G, c, k)
        write_output_file(G, c, k, output_path)
