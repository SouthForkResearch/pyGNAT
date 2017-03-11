import networkx as nx

# testing variables
inShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Braids.shp'

# import shapefile as graph
G = nx.read_shp(inShp, simplify=False)

def add_attrb(G, attrb_name, attrb_value):
    for u, v, d in G.edges(data=True):
        G.add_edge(u, v, attrb_name=attrb_value)

    return
