import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import *
from sys import exit
import random


# Load a shape file. Note that simplify is FALSE here. This is important
# If you simplify the read_shp will clean up all the duplicate points
# and you'll lose your braids
G = nx.read_shp('../../shapefiles/NHD_Braids.shp', simplify=False)

# Not sure if this is the right way to go but it gets us here for now.
GG = G.to_undirected()

cycles = []
try:
    # Get all the cycles in this network
    cycles = nx.cycle_basis(GG)
except:
    print "no biconnected segments found"
    exit(0)



"""

    Now let's print some stuff out about this and draw some pretty graphs

"""
# We'll create a shapely line from this path and measure the length of it.
pos = {v: v for k, v in enumerate(G.nodes())}
f, (ax) = plt.subplots(1)
ax.set_aspect(1.0)
plt.axis('off')
plt.sca(ax)

def randomColour():
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())

nx.draw_networkx_edges(GG, pos, ax=ax, edge_color='black', width=1)
for idx, cycle in enumerate(cycles):
    cycle.append(cycle[0])
    ls = LineString(cycle)
    x, y = ls.xy
    ax.plot(x, y, color=randomColour(), linewidth=3, solid_capstyle='round', label="Cycle: ".format(idx))

plt.show()
