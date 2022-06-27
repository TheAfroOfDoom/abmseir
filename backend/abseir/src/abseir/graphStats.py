import networkx as nx

# import matplotlib.pyplot as plt

n, k, d = 1500, 43, 3

# Read from file if exists
path = "graphs/wattsstrogatz_n{n}-k{k}-d{d}.edgelist".format(n=n, k=k, d=d)
g = []
g = nx.read_edgelist(path, nodetype=int)
print(
    "Read graph from '%s' with %d nodes, %d edges."
    % (path, g.number_of_nodes(), g.number_of_edges())
)

cc = nx.average_clustering(g)
print("Global Clustering Coefficient: ", cc)

nx.draw_circular(g, width=0.015, node_size=1)

# figmng = plt.get_current_fig_manager()
# figmng.resize(1080, 1080)

# plt.show()
