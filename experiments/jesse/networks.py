import networkx as nx

# testing variables
inShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Braids.shp'

# import shapefile as graph
G = nx.read_shp(inShp, simplify=False)
pos = {v: v for k, v in enumerate(G.nodes())}

# graph parameters
print G.number_of_nodes()
print G.number_of_edges()
print nx.degree(G)