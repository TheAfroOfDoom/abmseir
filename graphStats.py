import networkx as nx
import matplotlib.pyplot as plt

n, k, d = 1500, 43, 3

# Read from file if exists
path = "WattsStrogatz_n{n}-k{k}-d{d}.edgelist".format(n = n, k = k, d = d)
g = []
g = nx.read_edgelist(path, nodetype = int)
print("Read graph from '%s' with %d vertices, %d edges." % (path, g.number_of_nodes(), g.number_of_edges()))

cc = nx.average_clustering(g)
print(cc)

nx.draw_circular(g, width = 0.08, node_size = 1)
plt.show()