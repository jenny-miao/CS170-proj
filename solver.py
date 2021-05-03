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
    # FOR ALL VERTEX AND EDGE VARIABLES IN LP 1 MEANS WE KEEP 0 MEANS WE DELETE

    m = gp.Model("help")
    # We keep track of vertex variables and edge variables corresponding for edges adjacent to every v
    edges = {v: [] for v in G.nodes()}
    vertices = {}
    allEdges = []

    # Need to keep track of flow variables for constraint for connectivity
    s = G.nodes()[0]
    t = G.nodes()[G.number_of_nodes - 1]
    flowTo = {v : [] for v in G.nodes()}
    flowFrom = {v : [] for v in G.nodes()}

    for (u,v) in G.edges:
        # Create edgeVars - these will be the edges what we delete/keep
        edgeVar = m.addVar(vtype = GRB.BINARY, name = "e_" + str(u) + "," + str(v))
        edges[u].append(edgeVar)
        edges[v].append(edgeVar)
        allEdges.append(edgeVar)

        flowVar1 = m.addVar(vtype = GRB.INTEGER, ub = 1, lb = -1, name = "f_" + str(u) + "," + str(v))
        flowVar2 = m.addVar(vtype = GRB.INTEGER, ub = 1, lb = -1, name = "f_" + str(v) + "," + str(u))
        m.addConstr(flowVar1 == -flowVar2)
        m.addConstr(flowVar1 <= edgeVar)
        m.addConstr(-flowVar1 <= edgeVar)

        flowTo[v].append(flowVar1)
        flowFrom[u].append(flowVar1)
        flowTo[u].append(flowVar2)
        flowFrom[v].append(flowVar2)
    
    for v in G.nodes:
        vertices[v] = m.addVar(vtype = GRB.BINARY, name = "n_" + str(v))
        # This constraint ensures if one vertex removed then adjacent edges must also be not used
        m.addConstr(len(edges[v]) * vertices[v] >= gp.quicksum(edges[v]), "if " + str(v) + " removed then so must adjacent edges")
        if v == s:
            m.addConstr(gp.quicksum(flowTo[v]) - gp.quicksum(flowFrom[v]) == 1) 
        elif v == t:
            m.addConstr(gp.quicksum(flowTo[v]) - gp.quicksum(flowFrom[v]) == -1) 
        else:
            m.addConstr(gp.quicksum(flowTo[v]) - gp.quicksum(flowFrom[v]) == 0) 
        
    #s and t cannot be deleted
    m.addConstr(vertices[0] == 1, "s not deleted")
    m.addConstr(vertices[G.number_of_nodes() - 1] == 1, "t not deleted")

    # Constraint that makes sure we only delete k edges
    # THIS IS AN APPROXIMATION SINCE WE FORCE ADJACENT EDGES TO BE DELETED IF WE REMOVE NODE SO THIS LIMITS THE NUMBER WE CAN REMOVE
    # OUR SOL WONT BE OPTIMAL WHICH JUST MEANS A LOWER SCORE, MAYBE COME UP WITH ANOTHER CONSTRAINT TO SOMEHOW ACCOUNT FOR THE EDGES THAT ARE ALSO CONNECTED TO NODE WE DISCONNECT
    m.addConstr(gp.quicksum(allEdges) >= G.number_of_edges() - k_num, "only k edges removed")

    # Constraint that makes sure we only delete c vertices
    m.addConstr(gp.quicksum(vertices.values()) >= G.number_of_nodes() - c_num, "only c vertices removed")

    
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
