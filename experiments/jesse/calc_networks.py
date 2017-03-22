import networkx as nx
import attributes as attrb
from sys import exit


def get_subgraphs(G):
    """
    Find all subgraphs that are disconnected
    """

    try:
        return list(nx.connected_component_subgraphs(GG))
    except:
        print "ERROR: Could not find subgraphs"
        exit(0)

def calc_network_id(graph_list):
    """
    Assign a unique identifier to the edges within each subgraph
    :param graph_list: list of subgraphs
    :return: new graph with network IDs added as attribute
    """

    attrb_field = "NetworkID"
    list_subgraphs = []
    try:
        subgraph_count = 1
        for SG in graph_list:
            network_id = "{0}{1:0>3}".format("net", subgraph_count)
            attrb.add_attribute(SG, attrb_field, network_id)
            list_subgraphs.append(SG)
            subgraph_count += 1
        union_subgraphs = nx.union_all(list_subgraphs)
        return union_subgraphs
    except:
        raise IndexError # not sure about this... will probably change later

inShp = r'C:\dev\pyGNAT\shapefiles\NHD_Disconnected.shp'
outShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out\subgraphs_netID.shp'
G = nx.read_shp(inShp, simplify=False)
GG = G.to_undirected()

# get list of sub-graphs
list_SG = get_subgraphs(GG)
# calculate a unique network ID for each
SG_networkID = calc_network_id(list_SG)

# write out to a shapefile
nx.write_shp(SG_networkID, outShp)