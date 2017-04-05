import networkx as nx
import attributes as attrb

# constants
ATTRB_FLOW = "check_flow"

# variables
inShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Flow_Direction_small.shp'
startnode = (-1548545.770992536097765, 795909.187834305688739)
G = nx.read_shp(inShp, simplify=False)

def check_flow_dir(G, startnode):
    RG = nx.DiGraph.reverse(G, copy=True)
    attrb.add_attribute(RG, ATTRB_FLOW, "downstream") # add 'default' reach type

    # Get the first node (which I totally arbitrarily chose on the map)
    successor_dict = nx.dfs_successors(RG, startnode)

    RG_edges = RG.edges(data=True)
    upstream_edges = []
    for e in RG_edges:
        if e[0] not in successor_dict.keys():
            upstream_edges.append(e)

    # add new "flow_dir" attribute, based on bad_edges list
    upstream_graph = nx.DiGraph(upstream_edges)
    # set reach_type attribute for outflow and headwater edges
    attrb.update_attribute(upstream_graph, ATTRB_FLOW, "upstream")
    compose_G = nx.compose(RG, upstream_graph)
    return compose_G

final_G = check_flow_dir(G, startnode)