import networkx as nx
import matplotlib.pyplot as plt
from sys import exit


# Load up a simplified shape file and find the outflow from any
# arbitrary given point
G = nx.read_shp('../../shapefiles/FullNetwork.shp', simplify=True)

def findnodewithID(id):
    """
    One line helper function to find a node with a given ID
    :param id:
    :return:
    """
    return next(iter([e for e in G.edges_iter() if G.get_edge_data(*e)['OBJECTID'] == id]), None)

# Get the first node (which I totally arbitrarily chose on the map)
startnode = findnodewithID(19624)

try:
    dfsEdges = list(nx.dfs_edges(G, startnode[0]))
    # just get the list of biConn with length > 1
except:
    print "no biconnected segments found"
    exit(0)

red_edges = dfsEdges
black_edges = [edge for edge in G.edges() if edge not in red_edges]


"""

    Now let's print some stuff out about this and draw some pretty graphs

"""

# This just helps us plot our geo graph. It's kind of ahack
pos = {v: v for k, v in enumerate(G.nodes())}
f, (ax) = plt.subplots(1)
ax.set_aspect(1.0)
plt.axis('off')
plt.sca(ax)

nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='r', arrows=True)
nx.draw_networkx_edges(G, pos, edgelist=black_edges, arrows=False)

ax.set_aspect(1.0)
plt.sca(ax)
plt.show()

