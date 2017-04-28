import unittest
import lib.network as net
import networkx as nx

inFullNetworkShp = r'C:\dev\pyGNAT\experiments\shapefiles\FullNetwork_sm.shp'
inDisconnectedShp = r'C:\dev\pyGNAT\experiments\shapefiles\NHD_Disconnected.shp'
inConnectedShp = r'C:\dev\pyGNAT\experiments\shapefiles\NHD_Braids.shp'
inBraidSimpleShp = r'C:\dev\pyGNAT\experiments\shapefiles\Braid_simple.shp'
outShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out\output_test.shp'


class NetworkTestCase(unittest.TestCase):
    """Tests for 'network.py' functions"""

    def test_get_subgraphs_disconnected(self):
        DG = nx.read_shp(inDisconnectedShp)
        UG = DG.to_undirected()
        list_SG = net.get_subgraphs(UG)
        self.assertTrue(len(list_SG) > 0)

    def test_get_subgraphs_connected(self):
        DG = nx.read_shp(inConnectedShp)
        UG = DG.to_undirected()
        list_SG = net.get_subgraphs(UG)
        self.assertTrue(len(list_SG) == 1)

    def test_get_subgraphs_directed_graph(self):
        DG = nx.read_shp(inDisconnectedShp)
        list_SG = net.get_subgraphs(DG)
        self.assertTrue(len(list_SG) == 0)

    def test_calc_network_id_multiple_networks(self):
        DG = nx.read_shp(inDisconnectedShp)
        UG = DG.to_undirected()
        list_SG = net.get_subgraphs(UG)
        union_SG = net.calc_network_id(list_SG)
        self.assertTrue(union_SG is not None)

    def test_calc_network_id_single_network(self):
        DG = nx.read_shp(inConnectedShp)
        UG = DG.to_undirected()
        list_SG = net.get_subgraphs(UG)
        union_SG = net.calc_network_id(list_SG)
        self.assertTrue(union_SG is not None)

    def test_add_attribute_with_name_and_value_new(self):
        a_name = "test_name"
        a_value = "test_value"
        DG = nx.read_shp(inFullNetworkShp)
        net.add_attribute(DG, a_name, a_value)
        test_dict = nx.get_edge_attributes(DG, a_name)
        self.assertTrue(any(test_dict))

    def test_add_attribute_with_name_and_value_exists(self):
        a_name = "test_name"
        a_value = "test_value"
        DG = nx.read_shp(inFullNetworkShp)
        net.add_attribute(DG, a_name, a_value)
        net.add_attribute(DG, a_name, a_value)
        # test_dict = nx.get_edge_attributes(DG, a_name)
        # self.assertTrue(any(test_dict))

    def test_update_attributes_with_name_and_value(self):
        a_name = "foo"
        a_value = "bar"
        u_value = "boo"
        DG = nx.read_shp(inFullNetworkShp)
        net.add_attribute(DG, a_name, a_value)
        net.update_attribute(DG, a_name, u_value)

    def test_get_graph_attributes_with_networkID(self):
        DG = nx.read_shp(inConnectedShp)
        UG = DG.to_undirected()
        list_SG = net.get_subgraphs(UG)
        union_SG = net.calc_network_id(list_SG)
        str_result_SG = net.get_graph_attributes(union_SG, "NetworkID")
        self.assertTrue(str_result_SG != "")

    def test_get_graph_attributes_without_networkID(self):
        DG = nx.read_shp(inConnectedShp)
        UG = DG.to_undirected()
        list_SG = net.get_subgraphs(UG)
        for SG in list_SG:
            str_result_SG = net.get_graph_attributes(SG, "NetworkID")
        self.assertTrue(str_result_SG == "")

    def test_get_graph_attributes_wrong_attribute(self):
        DG = nx.read_shp(inConnectedShp)
        UG = DG.to_undirected()
        list_SG = net.get_subgraphs(UG)
        for SG in list_SG:
            str_result_SG = net.get_graph_attributes(SG, "foo")
        self.assertTrue(str_result_SG == "")

    def test_select_by_attribute_existing_attributes(self):
        a_name = "foo"
        a_value = "bar"
        DG = nx.read_shp(inFullNetworkShp)
        net.add_attribute(DG, a_name, a_value)
        net.select_by_attribute(DG, a_name, a_value)
        test_dict = nx.get_edge_attributes(DG, a_name)
        self.assertTrue(any(test_dict))

    def test_select_by_attribute_no_attribute(self):
        a_name = "foo"
        a_value = "bar"
        DG = nx.read_shp(inFullNetworkShp)
        net.select_by_attribute(DG, a_name, a_value)
        test_dict = nx.get_edge_attributes(DG, a_name)
        self.assertFalse(any(test_dict))

    def test_get_outflow_edges_directed_graph(self):
        a_name = "ReachType"
        DG = nx.read_shp(inFullNetworkShp)
        outflow_G = net.get_outflow_edges(DG, a_name)
        self.assertTrue(outflow_G is not None)

    def test_get_outflow_edges_undirected_graph(self):
        a_name = "ReachType"
        DG = nx.read_shp(inFullNetworkShp)
        UG = DG.to_undirected()
        outflow_G = net.get_outflow_edges(UG, a_name)
        total_edges = nx.edges(outflow_G)
        self.assertTrue(len(total_edges) == 0)

    def test_get_headwater_edges_directed_graph(self):
        a_name = "ReachType"
        DG = nx.read_shp(inFullNetworkShp)
        headwater_G = net.get_headwater_edges(DG, a_name)
        self.assertTrue(headwater_G is not None)

    def test_get_headwater_edges_undirected_graph(self):
        a_name = "ReachType"
        DG = nx.read_shp(inFullNetworkShp)
        UG = DG.to_undirected()
        headwater_G = net.get_headwater_edges(UG, a_name)
        total_edges = nx.edges(headwater_G)
        self.assertTrue(len(total_edges) == 0)

    def test_get_braid_edges_directed_graph(self):
        a_name = "ReachType"
        DG = nx.read_shp(inBraidSimpleShp, simplify=False)
        net.add_attribute(DG, a_name, "connector")
        braid_G = net.get_braid_edges(DG, a_name)
        self.assertTrue(braid_G is not None)

    def test_get_braid_edges_undirected_graph(self):
        a_name = "ReachType"
        DG = nx.read_shp(inConnectedShp, simplify=False)
        net.add_attribute(DG, a_name, "connector")
        UG = DG.to_undirected()
        braid_G = net.get_braid_edges(UG, a_name)
        total_edges = nx.edges(braid_G)
        self.assertTrue(len(total_edges) == 0)

    def test_get_braid_edges_no_braids(self):
        a_name = "ReachType"
        DG = nx.read_shp(inDisconnectedShp, simplify=False)
        net.add_attribute(DG, a_name, "connector")
        braid_G = net.get_braid_edges(DG, a_name)
        total_edges = nx.edges(braid_G)
        self.assertTrue(len(total_edges) == 0)

    def test_merge_subgraphs_with_braids(self):
        a_name = "ReachType"
        DG = nx.read_shp(inFullNetworkShp, simplify=False)
        net.add_attribute(DG, a_name, "connector")
        outflow_G = net.get_outflow_edges(DG, a_name)
        headwater_G = net.get_headwater_edges(DG, a_name)
        braid_G = net.get_braid_edges(DG, a_name)
        final_G = net.merge_subgraphs(DG, outflow_G, headwater_G, braid_G)
        nx.write_shp(final_G, outShp)  # temporary for review
        self.assertTrue(final_G is not None)

    if __name__ == '__main__':
        unittest.main()