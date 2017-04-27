#   Name:           Network
#   Description:    Main library of functions for building network topologies.
#   Authors:        Jesse Langdon, jesse@southforkresearch.org
#                   Matt Reimer, matt@northarrowresearch.com
#   Created:        4/6/2017
#   Revised:        4/27/2017


import networkx as nx

def get_subgraphs(G):
    """
    Find all subgraphs that are disconnected.
    :param self: graph must be undirected to use this method.
    """
    try:
        list_SG = list(nx.connected_component_subgraphs(G))
        return list_SG
    except:
        print "ERROR: Could not find subgraphs"
        list_SG = []
        return list_SG


def calc_network_id(list_SG):
    """
    Assign a unique identifier to the edges within each subgraph
    :param self.graph_list: list of subgraphs
    :return: new graph with network IDs added as attribute
    """
    attrb_field = "NetworkID"
    try:
        subgraph_count = 1
        for SG in list_SG:
            network_id = "{0}{1:0>3}".format("net", subgraph_count)
            add_attribute(SG, attrb_field, network_id)
            subgraph_count += 1
        union_SG = nx.union_all(list_SG)
        return union_SG
    except:
       raise IndexError  # not sure about this... will probably change later


def get_graph_attributes(G, attrb_name):
    str_total_edges = G.size()
    edge_dict = nx.get_edge_attributes(G, attrb_name)
    if len(edge_dict) > 0:
        networks = set(val for val in edge_dict.values())
        for network in networks:
            str_summary = "Network ID: {0} - Total number of edges: {1}".format(network, str_total_edges)
        return str_summary
    else:
        str_summary = ""
        print "ERROR: Network ID attribute not found"
        return str_summary


def update_attribute(G, attrb_name, attrb_value):
    """
    Update existing attribute with new values
    :param attrb_name: name of the attribute to be updated
    :param attrb_value: new attribute value
    """
    dict = nx.get_edge_attributes(G, attrb_name)
    try:
        if len(dict) > 0:
            nx.set_edge_attributes(G, attrb_name, attrb_value)
        else:
            print "ERROR: Attribute type does not exist in the network"
    except:
        print "ERROR: Missing an input parameter"
    return


def add_attribute(G, attrb_name, attrb_value):
    """
    Add a new attribute to a graph.
    :param attrb_name: name of the attribute to be added
    :param attrb_value: new attribute value
    """
    dict = nx.get_edge_attributes(G, attrb_name)
    if len(dict) == 0:
        nx.set_edge_attributes(G, attrb_name, attrb_value)
    else:
        print "ERROR: Attribute already exists"
    return


def select_by_attribute(G, attrb_name, attrb_value):
    """
    Select all edges within a graph based on the user-supplied attribute value
    :param attrb_name: name of the attribute that will be used for the selection
    :param attrb_value: attribute value to select by
    """
    dict = nx.get_edge_attributes(G, attrb_name)
    if len(dict) > 0:
        nx.Graph([(u, v, d) for u, v, d in G.edges(data=True) if d[attrb_name] != attrb_value])
    else:
        print "ERROR: Attribute not found"


def get_outflow_edges(G, attrb_field):
    """
    Create graph with the outflow edge attributed
    :param attrb_type: name of the attribute field
    :return outflow_G: graph with new headwater attribute
    """
    if nx.is_directed(G):
        out_dict = G.out_degree()
        # find the outflow node (should have zero outgoing edges, right?)
        outflow_node = list(dict((k, v) for k, v in out_dict.iteritems() if v == 0))
        # get the edge that is connected to outflow node
        outflow_edge = G.in_edges(outflow_node, data=True)
        outflow_G = nx.DiGraph(outflow_edge)
        # set reach_type attribute for outflow and headwater edges
        update_attribute(outflow_G, attrb_field, "outflow")
        return outflow_G
    else:
        print "ERROR: Graph is not directed."
        outflow_G = nx.null_graph()
        return outflow_G


def get_headwater_edges(G, attrb_field):
    """
    Create graph with the headwater edges attributed
    :param attrb_field: name of the attribute field
    :return headwater_G: graph with new attribute
    """
    if nx.is_directed(G):
        in_dict = G.in_degree()
        headwater_nodes = list(dict((k, v) for k, v in in_dict.iteritems() if v == 0))
        headwater_edges = G.out_edges(headwater_nodes, data=True)
        headwater_G = nx.DiGraph(headwater_edges)
        update_attribute(G, attrb_field, "headwater")
        return headwater_G
    else:
        print "ERROR: Graph is not directed."
        headwater_G = nx.null_graph()
        return headwater_G


def get_braid_edges(G, attrb_field):
    """
    Create graph with the braid edges attributed
    :param attrb_field: name of the attribute field
    :return braid_G: graph with new attribute
    """
    if nx.is_directed(G):
        UG = G.to_undirected()
        print "Number of edges in undirected graph: " + str(UG.number_of_edges())
        braid_G = nx.DiGraph()
        print "Finding cycles in undirected graph..."
        list_cycles = nx.cycle_basis(UG)
        if len(list_cycles) == 0:
            print "ERROR: no braids found!"
            braid_G = nx.null_graph()
            return braid_G
        else:
            print "Total number of potential braids: " + str(len(list_cycles))
            for cycles in list_cycles:
                #cycle_edges = zip(cycles, cycles[1:] + cycles[:1])
                for u, v, d in G.edges(nbunch=cycles, data=True):
                    braid_G.add_edge(u, v, d)
            update_attribute(braid_G, attrb_field, "braid")
            return braid_G
    else:
        print "ERROR: Graph is not directed."
        braid_G = nx.null_graph()
        return braid_G


def merge_subgraphs(G, outflow_G, headwater_G, braid_G):
    """
    Join all subgraphs with the main graph
    :param list_G: list of subgraphs with reach type attribute added
    :return G_compose: final graph output with all reach type attributes included
    """

    # unfortunately this didn't work correctly
    # SG = list_G.pop(0)
    # compose_G = nx.compose(G, SG)
    # if len(list_G) > 0:
    #     merge_subgraphs(compose_G, list_G)

    # this is not ideal, but the fancy recursion didn't work
    G1 = nx.compose(G, outflow_G)
    G2 = nx.compose(G1, headwater_G)
    compose_G = nx.compose(G2, braid_G)

    return compose_G