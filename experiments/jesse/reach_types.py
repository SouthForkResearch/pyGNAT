import networkx as nx
import attributes as attrb

# constants
ATTRB_TYPE = "ReachType"

# variables
inShp = r'C:\dev\pyGNAT\shapefiles\NHD_Braids.shp'
outShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out\reach_types.shp'
G = nx.read_shp(inShp, simplify=False)


attrb.add_attribute(G, ATTRB_TYPE, "connector") # add 'default' reach type

def get_outflow_edges(G):
    # create dictionary of nodes (keys) with total number of edges (value) that 'connect into' each node
    out_dict = G.out_degree()
    # find the outflow node (should have zero outgoing edges, right?)
    outflow_node = list(dict((k,v) for k,v in out_dict.iteritems() if v == 0))
    # get the edge that is connected to outflow node
    outflow_edge = G.in_edges(outflow_node, data=True)
    outflow_graph = nx.DiGraph(outflow_edge)
    # set reach_type attribute for outflow and headwater edges
    attrb.update_attribute(outflow_graph, ATTRB_TYPE, "outflow")
    return outflow_graph

def get_headwater_edges(G):
    # create dictionary of nodes (keys) with total number of edges (values) that 'connect out' of each node
    in_dict = G.in_degree()
    headwater_nodes = list(dict((k,v) for k,v in in_dict.iteritems() if v == 0))
    headwater_edges = G.out_edges(headwater_nodes, data=True)
    headwater_graph = nx.DiGraph(headwater_edges)
    attrb.update_attribute(headwater_graph, ATTRB_TYPE, "headwater")
    return headwater_graph

def merge_subgraphs(G, outflow_G, headwater_G):  # this needs to be refactored to handle a list of graphs
    # join all subgraphs back to main network graph
    G_outflow = nx.compose(G, outflow_G)
    G_headwater = nx.compose(G_outflow, headwater_G)
    return G_headwater


outflow_G = get_outflow_edges(G)
headwater_G = get_headwater_edges(G)
final_G = merge_subgraphs(G, outflow_G, headwater_G)

nx.write_shp(final_G, outShp)