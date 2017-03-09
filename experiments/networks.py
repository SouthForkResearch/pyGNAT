import networkx as nx

# testing variables
inShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Braids_noZ.shp'

# import shapefile as graph
G = nx.read_shp(inShp, simplify=False)
pos = {v: v for k, v in enumerate(G.nodes())}

# graph parameters
print len(G.nodes())
print len(G.edges())