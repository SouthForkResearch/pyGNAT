import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import *
import random
from sys import exit

def randomColour():
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())


# Load a shape file. We simplify to make things WAY faster
# and because we don't really care about the kinks in each segment
G = nx.read_shp('../../shapefiles/FullNetwork.shp', simplify=True)

# Not sure if this is the right way to go but it gets us here for now.
GG = G.to_undirected()



# Make a depth-first tree from the first headwater we find
try:
    """
    GET ALL THE SUBGRAPHS THAT ARE NOT CONNECTED
    """
    subgraphs = list(nx.connected_component_subgraphs(GG))
except:
    print "Could not find subgraphs"
    exit(0)





"""
    Now let's print some stuff out about this and draw some pretty graphs
"""

# This just helps us plot our geo graph. It's kind of ahack
pos = {v: v for k, v in enumerate(G.nodes())}
f, (ax) = plt.subplots(1)

ax.set_aspect(1.0)
plt.sca(ax)


# I want the biggest network to be black and big line thickness so let's find it.
for idx, SG in enumerate(subgraphs):
    if len(SG.nodes()) == max([len(x.nodes()) for x in subgraphs]):
        nx.draw_networkx_edges(SG, pos, ax=ax, edge_color='#000000', width=1, zorder=0)
    else:
        nx.draw_networkx_edges(SG, pos, ax=ax, edge_color=randomColour(), width=3, zorder=10)

plt.show()

