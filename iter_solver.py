import networkx as nx
from parse import read_input_file, write_output_file
from utils import is_valid_solution, calculate_score
import sys
from os.path import basename, normpath
import glob
import random

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
    t = G.number_of_nodes() - 1

    H = G.copy()

    # find og min path
    og_length, og_path = nx.single_source_dijkstra(H, 0, t)

    #find best nodes to delete first
    d_vertices = []
    for i in range(c_num):
        # available_vertices = list(H.nodes)
        # available_vertices.remove(0)
        # available_vertices.remove(t)
        minLen = og_length
        d_vertex = None
        #iterate through each node except s and t
        # for j in available_vertices:
        for j in range(1, t):
            #for some reason i cant use the following line
            #j_edges = H.edges(j)
            if (H.has_node(j) and j not in d_vertices):
                F = H.copy()
                j_edges = F.edges(j)
                # print(j_edges)
                H.remove_node(j)
                #check that we can remove the node without disconnecting the graph
                if ((t in nx.algorithms.dag.descendants(H, 0)) and nx.is_connected(H)):
                    length, path = nx.single_source_dijkstra(H, 0, t)
                    if (length <= minLen):
                        minLen = length
                        d_vertex = j
                    #add node back since it might not be the most optimal
                H.add_node(j)
                H.add_edges_from(j_edges)
                # print(j_edges)

        #if theres a vertex to delete
        if d_vertex:
            H.remove_node(d_vertex)
            # available_vertices.remove(d_vertex)
            d_vertices.append(d_vertex)

    # find min path after deleting nodes
    no_nodes_length, no_nodes_path = nx.single_source_dijkstra(H, 0, t)

    # print("start edges")
    #find edges to delete
    d_edges = []
    for x in range(k_num):
        minLen = no_nodes_length
        d_edge = None
        #iterate through each edge
        for edge in H.edges:
            u, v = edge
            if ((u not in d_vertices) and (v not in d_vertices)):
                H.remove_edge(u, v)
                #check that we can remove the edge without disconnecting the graph
                if ((t in nx.algorithms.dag.descendants(H, 0)) and nx.is_connected(H)):
                    length, path = nx.single_source_dijkstra(H, 0, t)
                    #if better than previous option, update
                    if (length < minLen):
                        minLen = length
                        d_edge = edge
                #add edge back since it might not be the most optimal
                H.add_edge(u, v)

        #if theres an edge to delete
        if d_edge:
            u, v = d_edge
            H.remove_edge(u, v)
            d_edges.append(d_edge)

    return d_vertices, d_edges


def solve_noVertex(G):
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
    t = G.number_of_nodes() - 1

    H = G.copy()

    # find og min path
    og_length, og_path = nx.single_source_dijkstra(H, 0, t)

    #give up on vertices
    d_vertices = []
    # find min path after deleting nodes
    no_nodes_length, no_nodes_path = nx.single_source_dijkstra(H, 0, t)

    # print("start edges")
    #find edges to delete
    d_edges = []
    for x in range(k_num):
        minLen = no_nodes_length
        d_edge = None
        #iterate through each edge
        for edge in H.edges:
            u, v = edge
            if ((u not in d_vertices) and (v not in d_vertices)):
                H.remove_edge(u, v)
                #check that we can remove the edge without disconnecting the graph
                if ((t in nx.algorithms.dag.descendants(H, 0)) and nx.is_connected(H)):
                    length, path = nx.single_source_dijkstra(H, 0, t)
                    #if better than previous option, update
                    if (length < minLen):
                        minLen = length
                        d_edge = edge
                #add edge back since it might not be the most optimal
                H.add_edge(u, v)

        #if theres an edge to delete
        if d_edge:
            u, v = d_edge
            H.remove_edge(u, v)
            d_edges.append(d_edge)

    return d_vertices, d_edges

def solve_random(G):
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
    t = G.number_of_nodes() - 1

    H = G.copy()

    # find og min path
    og_length, og_path = nx.single_source_dijkstra(H, 0, t)

    #give up on vertices
    d_vertices = []
    vertex_count = 0
    while ((t in nx.algorithms.dag.descendants(H, 0)) and nx.is_connected(H) and (vertex_count < c_num)):
        remove = random.randint(1, t - 1)
        if (remove not in d_vertices):
            H.remove_node(remove)
            d_vertices.add(remove)
            vertex_count++

    d_edges = []
    edge_count = 0
    while ((t in nx.algorithms.dag.descendants(H, 0)) and nx.is_connected(H) and (edge_count < k_num)):
        remove = random.choice(H.edges)
        if (remove not in d_edges):
            H.remove_edge(remove)
            d_edges.add(remove)
            edge_count++

    return d_vertices, d_edges

# Here's an example of how to run your solver.

# Usage: python3 solver.py test.in

if __name__ == '__main__':
    assert len(sys.argv) == 2
    path = sys.argv[1]
    G = read_input_file(path)
    c, k = solve(G)
    assert is_valid_solution(G, c, k)
    score1 = calculate_score(G, c, k)
    
    c2, k2 = solve_noVertex(G)
    assert is_valid_solution(G, c2, k2)
    score2 = calculate_score(G, c2, k2)

    c3, k3 = solve_random(G)
    assert is_valid_solution(G, c3, k3)
    score3 = calculate_score(G, c3, k3)

    print("Shortest Path Difference (with vertex: {}".format(calculate_score(G, c, k)))
    print("Shortest Path Difference (without vertex: {}".format(calculate_score(G, c2, k2)))
    print("Shortest Path Difference (random: {}".format(calculate_score(G, c3, k3)))

    maxScore = max(score1, score2, score3)
    if (maxScore == score1):
        write_output_file(G, c, k, 'outputs/small-1.out')
    elif (maxScore == score2):
        write_output_file(G, c2, k2, 'outputs/small-1.out')
    else: 
        write_output_file(G, c3, k3, 'outputs/small-1.out')




# For testing a folder of inputs to create a folder of outputs, you can use glob (need to import it)
# if __name__ == '__main__':
#     inputs = glob.glob('inputs/*')
#     for input_path in inputs:
#         output_path = 'outputs/' + basename(normpath(input_path))[:-3] + '.out'
#         G = read_input_file(input_path)
#         c, k = solve(G)
#         assert is_valid_solution(G, c, k)
#         distance = calculate_score(G, c, k)
    
#         c2, k2 = solve_noVertex(G)
#         assert is_valid_solution(G, c2, k2)
#         score2 = calculate_score(G, c2, k2)

#         c3, k3 = solve_random(G)
#         assert is_valid_solution(G, c3, k3)
#         score3 = calculate_score(G, c3, k3)

#         maxScore = max(distance, score2, score3)
#         if (maxScore == distance):
#             write_output_file(G, c, k, output_path)
#         elif (maxScore == score2):
#             write_output_file(G, c2, k2, output_path)
#         else: 
#             write_output_file(G, c3, k3, output_path)
