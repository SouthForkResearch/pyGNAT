import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import *
from sys import exit
import random

def randomColour():
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())


# Load a shape file. Note that simplify is FALSE here. This is important
# If you simplify
G = nx.read_shp('../../shapefiles/NHD_Braids.shp', simplify=False)

# Not sure if this is the right way to go but it gets us here for now.
GG = G.to_undirected()

cycles = []
try:
    cycles = nx.cycle_basis(GG)
    # just get the list of biConn with length > 1
except:
    print "no biconnected segments found"
    exit(0)



"""

    Now let's print some stuff out about this and draw some pretty graphs

"""

# This just helps us plot our geo graph. It's kind of ahack
pos = {v: v for k, v in enumerate(G.nodes())}


# We'll create a shapely line from this path and measure the length of it.
# ls = LineString(shortestpath)
f, (ax1, ax2) = plt.subplots(1, 2)

ax1.set_aspect(1.0)
plt.sca(ax1)
plt.axis('off')
plt.rcParams["figure.figsize"] = (20,3)

# place a text box in upper left in axes coords
# textstr = 'Edges: {0}\nNodes: {1}\nStartID: {2}\nEndID {3}\nPathDist: {4}'.format(len(G.nodes()), len(G.edges()), STARTID, ENDID, ls.length)
# props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
# ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=14,
#         verticalalignment='top', bbox=props)

nx.draw_networkx_edges(GG, pos, ax=ax1, edge_color='black', width=1)
for idx, cycle in enumerate(cycles):
    cycle.append(cycle[0])
    ls = LineString(cycle)
    x, y = ls.xy
    ax1.plot(x, y, color=randomColour(), linewidth=3, solid_capstyle='round', label="Cycle: ".format(idx))

plt.show()
