import networkx as nx
import matplotlib.pyplot as plt
import attributes as a

# testing variables
inShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Braids.shp'
outShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out\NHD_Braids_attrib.shp'
# import shapefile as graph
G = nx.read_shp(inShp, simplify=False)


# attributes.py

# update an existing attribute
a.update_attribute(G, "GNAT", "Gummy Bear")
# add a new attribute
a.add_attribute(G, "NEW_FIELD", "-99999")
# filter graph by an attribute
SG = a.select_by_attribute(G, "GNIS_Name", "Lostine River")

nx.write_shp(SG, outShp)

# plot it
pos = {v: v for k, v in enumerate(G.nodes())}
f, (ax) = plt.subplots(1)

ax.set_aspect(1.0)
plt.sca(ax)

nx.draw_networkx_edges(G, pos, ax=ax, edge_color='red', width=1, zorder=10)
nx.draw_networkx_edges(SG, pos, ax=ax, edge_color='black', width=4, zorder=1)

plt.show()
