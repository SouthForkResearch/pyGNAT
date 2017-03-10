import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import *

# testing variables
inShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Braids.shp'

# import shapefile as graph
G = nx.read_shp(inShp, simplify=False)


def filterOutCanals(G):
    # filter out canals (based on NHD FType)
    return nx.Graph([(u, v, d) for u, v, d in G.edges(data=True) if d['FType'] != 360])

SG = filterOutCanals(G)

# plot it
pos = {v: v for k, v in enumerate(G.nodes())}
f, (ax) = plt.subplots(1)

ax.set_aspect(1.0)
plt.sca(ax)

nx.draw_networkx_edges(G, pos, ax=ax, edge_color='red', width=1, zorder=10)
nx.draw_networkx_edges(SG, pos, ax=ax, edge_color='black', width=4, zorder=1)

plt.show()