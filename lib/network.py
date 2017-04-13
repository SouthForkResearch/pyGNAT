#   Name:           Network
#   Description:    Primary class for building network topologies.
#   Authors:        Jesse Langdon, jesse@southforkresearch.org
#                   Matt Reimer, matt@northarrowresearch.com
#   Created:        4/6/2017
#   Revised:        4/13/2017


import networkx as nx

class Network():

    def __init__(self, inShp='', directed='true'):
        """Default is to create an directed graph, but an undirected
        graph is required to use some methods."""
        try:
            self.data_source = "inShp"
            if directed == 'true':
                self.G = nx.read_shp(inShp)
            else:
                temp_G = nx.read_shp(inShp)
                self.G = temp_G.to_undirected()
        except Exception as e:
            print "Cannot instantiate object. Input shapefile data source required."
            pass


    def get_subgraphs(self):
        """
        Find all subgraphs that are disconnected.
        :param self: graph must be undirected to use this method.
        """
        try:
            self.list_SG = list(nx.connected_component_subgraphs(self.G))
            return self.list_SG
        except:
            print "ERROR: Could not find subgraphs"
            exit(0)


    def calc_network_id(self):
        """
        Assign a unique identifier to the edges within each subgraph
        :param self.graph_list: list of subgraphs
        :return: new graph with network IDs added as attribute
        """
        attrb_field = "NetworkID"
        try:
            subgraph_count = 1
            for SG in self.list_SG:
                network_id = "{0}{1:0>3}".format("net", subgraph_count)
                self.G.add_attribute(SG, attrb_field, network_id)
                subgraph_count += 1
            union_SG = nx.union_all(self.list_SG)
            return union_SG
        except:
            raise IndexError  # not sure about this... will probably change later


    def get_graph_attributes(self, attrb_name):
        str_total_edges = self.G.size()
        edge_dict = nx.get_edge_attributes(self.G, attrb_name)
        if len(edge_dict) > 0:
            networks = set(val for val in edge_dict.values())
        else:
            print "ERROR: Attribute not found"
            exit(0)
        # format into string for printing
        for network in networks:
            str_summary = "Network ID: {0} - Total number of edges: {1}".format(network, str_total_edges)
        return str_summary


    def update_attribute(self, attrb_name, attrb_value):
        """
        Update existing attribute with new values
        :param attrb_name: name of the attribute to be updated
        :param attrb_value: new attribute value
        """
        dict = nx.get_edge_attributes(self.G, attrb_name)
        if len(dict) > 0:
            nx.set_edge_attributes(self.G, attrb_name, attrb_value)
        else:
            print "ERROR: Attribute not found"
            exit(0)
        return


    def add_attribute(self, attrb_name, attrb_value):
        """
        Add a new attribute to a graph.
        :param attrb_name: name of the attribute to be added
        :param attrb_value: new attribute value
        """
        dict = nx.get_edge_attributes(self.G, attrb_name)
        if len(dict) == 0:
            nx.set_edge_attributes(self.G, attrb_name, attrb_value)
        else:
            print "ERROR: Attribute already exists"
            exit(0)
        return


    def select_by_attribute(self, attrb_name, attrb_value):
        """
        Select all edges within a graph based on the user-supplied attribute value
        :param attrb_name: name of the attribute that will be used for the selection
        :param attrb_value: attribute value to select by
        """
        dict = nx.get_edge_attributes(self.G, attrb_name)
        if len(dict) > 0:
            nx.Graph([(u, v, d) for u, v, d in self.G.edges(data=True) if d[attrb_name] != attrb_value])
        else:
            print "ERROR: Attribute not found"
            exit(0)


    def get_outflow_edges(self, attrb_field):
        """
        Create graph
        :param attrb_type:
        """
        out_dict = self.G.out_degree()
        # find the outflow node (should have zero outgoing edges, right?)
        outflow_node = list(dict((k, v) for k, v in out_dict.iteritems() if v == 0))
        # get the edge that is connected to outflow node
        outflow_edge = self.G.in_edges(outflow_node, data=True)
        outflow_G = nx.DiGraph(outflow_edge)
        # set reach_type attribute for outflow and headwater edges
        self.update_attribute(attrb_field, "outflow")
        return outflow_G


    def get_headwater_edges(self, attrb_field):
        """
        Create graph with the headwater edges attributed
        :param attrb_field: name of the attribute field
        :return headwater_G: graph with new attribute
        """
        in_dict = self.G.in_degree()
        headwater_nodes = list(dict((k, v) for k, v in in_dict.iteritems() if v == 0))
        headwater_edges = self.G.out_edges(headwater_nodes, data=True)
        headwater_G = nx.DiGraph(headwater_edges)
        self.update_attribute(attrb_field, "headwater")
        return headwater_G


    def get_braid_edges(self, attrb_field):
        """
        Create graph with the braid edges attributed
        :param attrb_field: name of the attribute field
        :return headwater_G: graph with new attribute
        """
        UG = self.G.to_undirected()
        print "Number of edges in undirected graph: " + str(UG.number_of_edges())
        braid_G = nx.DiGraph()
        try:
            print "Finding cycles in undirected graph..."
            list_cycles = nx.cycle_basis(UG)
            print "Total number of potential braids: " + len(list_cycles)
        except:
            print "ERROR: no biconnected segments found"
            exit(0)
        for cycles in list_cycles:
            cycle_edges = zip(cycles, cycles[1:] + cycles[:1])
            print len(cycle_edges)
            for u, v, d in self.G.edges(nbunch=cycles, data=True):
                braid_G.add_edge(u, v, d)
        self.update_attribute(braid_G, attrb_field, "braid")
        return braid_G


    def merge_subgraphs(self, list_G):  # this needs to be refactored to handle a list of graphs
        """
        Join all subgraphs with the main graph
        :param list_G: list of subgraphs with reach type attribute added
        :return G_compose: final graph output with all reach type attributes included
        """
        list_G.insert(0, self.G)
        G_compose = nx.compose_all(list_G)
        return G_compose