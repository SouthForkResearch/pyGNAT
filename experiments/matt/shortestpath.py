import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import *


STARTID = 2492
ENDID =253 #3850

# Load a shape file. We simplify to make things WAY faster
# and because we don't really care about the kinks in each segment
G = nx.read_shp('../../shapefiles/FullNetwork.shp', simplify=True)

# Not sure if this is the right way to go but it gets us here for now.
GG = G.to_undirected()



def findnodewithID(id):
    """
    One line helper function to find a node with a given ID
    :param id:
    :return:
    """
    return next(iter([e for e in G.edges_iter() if G.get_edge_data(*e)['OBJECTID'] == id]), None)


def summarizeAttrib(path_edges, GG, attrib):
    """
    Here's us summing all of the attrib ('Shape_Leng' in this case)
    :param path_edges:
    :param GG:
    :return:
    """
    x = []
    counter = 0
    for pe in path_edges:
        counter += GG.get_edge_data(*pe)[attrib]
        x.append(counter)
    y = [(t[0][1] + t[0][0]) for t in path_edges]
    return x, y

start = findnodewithID(STARTID)
end = findnodewithID(ENDID)


# Make a depth-first tree from the first headwater we find
shortestpath = nx.shortest_path(GG, source=start[0], target=end[0])
path_edges = zip(shortestpath, shortestpath[1:])



"""

    Now let's print some stuff out about this and draw some pretty graphs

"""

# This just helps us plot our geo graph. It's kind of ahack
pos = {v: v for k, v in enumerate(G.nodes())}


# We'll create a shapely line from this path and measure the length of it.
ls = LineString(shortestpath)
f, (ax1, ax2) = plt.subplots(1, 2)

ax1.set_aspect(1.0)
plt.sca(ax1)
plt.axis('off')
plt.rcParams["figure.figsize"] = (20,3)

# place a text box in upper left in axes coords
textstr = 'Edges: {0}\nNodes: {1}\nStartID: {2}\nEndID {3}\nPathDist: {4}'.format(len(G.nodes()), len(G.edges()), STARTID, ENDID, ls.length)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

nx.draw_networkx_edges(GG, pos, ax=ax1, edge_color='black', width=1)
nx.draw_networkx_edges(GG,pos, ax=ax1, edgelist=path_edges, edge_color='red', width=3)

# Now the second plot
px,py = summarizeAttrib(path_edges, GG, 'Shape_Leng')
plt.sca(ax2)
plt.plot(px, py)

plt.show()

