import time
from datetime import datetime
import networkx as nx
import attributes as attrb

start_time = time.time()
today=datetime.now()
print "Start time: " + str(today)

# constants
ATTRB_FIELD = "ReachType" # name of the new attribute field in the output shapefile

# variables
inShp = r'C:\dev\pyGNAT\experiments\shapefiles\FullNetwork.shp'
outShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out\reach_types.shp'
print 'Reading shapefile...'
G = nx.read_shp(inShp, simplify=False)


attrb.add_attribute(G, ATTRB_FIELD, "connector") # add 'default' reach type

def findnodewithID(id):
    """
    One line helper function to find a node with a given ID
    :param id:
    :return:
    """
    return next(iter([e for e in G.edges_iter() if G.get_edge_data(*e)['OBJECTID'] == id]), None)


def get_outflow_edges(G):
    # create dictionary of nodes (keys) with total number of edges (value) that 'connect into' each node
    out_dict = G.out_degree()
    # find the outflow node (should have zero outgoing edges, right?)
    outflow_node = list(dict((k,v) for k,v in out_dict.iteritems() if v == 0))
    # get the edge that is connected to outflow node
    outflow_edge = G.in_edges(outflow_node, data=True)
    outflow_graph = nx.DiGraph(outflow_edge)
    # set reach_type attribute for outflow and headwater edges
    attrb.update_attribute(outflow_graph, ATTRB_FIELD, "outflow")
    return outflow_graph


def get_headwater_edges(G):
    # create dictionary of nodes (keys) with total number of edges (values) that 'connect out' of each node
    in_dict = G.in_degree()
    headwater_nodes = list(dict((k,v) for k,v in in_dict.iteritems() if v == 0))
    headwater_edges = G.out_edges(headwater_nodes, data=True)
    headwater_graph = nx.DiGraph(headwater_edges)
    attrb.update_attribute(headwater_graph, ATTRB_FIELD, "headwater")
    return headwater_graph


def get_braid_edges(G):
    print "Converting directed to undirected graph..."
    UG = G.to_undirected()
    print "Number of edges in undirected graph: " + str(UG.number_of_edges())
    braid_G = nx.DiGraph()
    try:
        print "Finding cycles in undirected graph..."
        list_cycles = nx.cycle_basis(UG)
        print len(list_cycles)
    except:
        print "ERROR: no biconnected segments found"
        exit(0)
    for cycles in list_cycles:
        cycle_edges = zip(cycles, cycles[1:] + cycles[:1])
        print len(cycle_edges)
        for u,v,d in G.edges(nbunch=cycles, data=True):
            if (u,v) in cycle_edges or (v,u) in cycle_edges:
                braid_G.add_edge(u,v,d)
                attrb.update_attribute(braid_G, ATTRB_FIELD, "braid")
                print "{0},{1} added to braid_G".format(u,v)
    return braid_G


def merge_subgraphs(G, outflow_G, headwater_G, braid_G):  # this needs to be refactored to handle a list of graphs
    # join all subgraphs back to main network graph
    G_outflow = nx.compose(G, outflow_G)
    G_headwater = nx.compose(G_outflow, headwater_G)
    G_braid = nx.compose(G_headwater, braid_G)
    return G_braid


print "Find outflow edges..."
outflow_G = get_outflow_edges(G)
print "Find headwater edges..."
headwater_G = get_headwater_edges(G)
print "Find braid edges..."
braid_G = get_braid_edges(G)
print "Create final network graph..."
final_G = merge_subgraphs(G, outflow_G, headwater_G, braid_G)
print "Write network to shapefile..."
nx.write_shp(final_G, outShp)

end_time = time.time()
print "Total processing time: " + str(end_time - start_time)