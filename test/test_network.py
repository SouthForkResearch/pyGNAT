import unittest
import lib.network as net
import networkx as nx

inFullNetworkShp = r'C:\dev\pyGNAT\experiments\shapefiles\FullNetwork_sm.shp'
inDisconnectedShp = r'C:\dev\pyGNAT\experiments\shapefiles\NHD_Disconnected.shp'
inConnectedShp = r'C:\dev\pyGNAT\experiments\shapefiles\NHD_Braids.shp'

class NetworkTestCase(unittest.TestCase):
    """Tests for 'network.py'"""

    def test_init_network_with_line_shapefile(self):
        net_obj = net.Network(inFullNetworkShp)
        self.assertIsInstance(net_obj, net.Network)

    def test_init_network_with_no_input(self):
        net_obj = net.Network()
        self.assertTrue(net_obj.data_source != '')

    def test_get_subgraphs_disconnected(self):
        net_obj = net.Network(inDisconnectedShp, 'undirected' )
        net_obj.get_subgraphs()
        self.assertTrue(len(net_obj.list_SG) > 0)

    def test_get_subgraphs_connected(self):
        net_obj = net.Network(inConnectedShp, 'undirected')
        net_obj.get_subgraphs()
        self.assertTrue(len(net_obj.list_SG) == 1)

    def test_get_subgraphs_directed_graph(self):
        net_obj = net.Network(inDisconnectedShp)
        net_obj.get_subgraphs()
        self.assertTrue(len(net_obj.list_SG) == 0)

    def test_calc_network_id_multiple_networks(self):
        net_obj = net.Network(inFullNetworkShp, 'undirected')
        net_obj.get_subgraphs()
        union_SG = net_obj.calc_network_id()
        self.assertTrue(union_SG is not None)

    def test_calc_network_id_single_network(self):
        net_obj = net.Network(inConnectedShp, 'undirected')
        net_obj.get_subgraphs()
        union_SG = net_obj.calc_network_id()
        self.assertTrue(union_SG is not None)

    def test_add_attribute_with_name_and_value_new(self):
        a_name = "test_name"
        a_value = "test_value"
        net_obj = net.Network(inFullNetworkShp, 'directed')
        net_obj.add_attribute(net_obj.G, a_name, a_value)
        test_dict = nx.get_edge_attributes(net_obj.G, a_name)
        self.assertTrue(any(test_dict))

    def test_add_attribute_with_name_and_value_exists(self):
        a_name = "test_name"
        a_value = "test_value"
        net_obj = net.Network(inFullNetworkShp, 'directed')
        net_obj.add_attribute(net_obj.G, a_name, a_value)
        net_obj.add_attribute(net_obj.G, a_name, a_value)
        # test_dict = nx.get_edge_attributes(net_obj.G, a_name)
        # self.assertTrue(any(test_dict))

    def test_update_attributes_with_name_and_value(self):
        a_name = "foo"
        a_value = "bar"
        u_value = "boo"
        net_obj = net.Network(inFullNetworkShp, 'directed')
        net_obj.add_attribute(net_obj.G, a_name, a_value)
        net_obj.update_attribute(net_obj.G, a_name, u_value)

    # def get_graph_attributes_with_networkID(self):
    #     net_obj = net.Network(inConnectedShp, 'undirected')
    #     net_obj.get_subgraphs()
    #     for SG in net_obj.list_SG:
    #         str_result_SG = net_obj.get_graph_attributes(SG, "NetworkID")
    #     self.assertTrue(str_result_SG != "")
    #
    # def get_graph_attributes_without_networkID(self):
    #     net_obj = net.Network(inConnectedShp, 'undirected')
    #     for SG in net_obj.list_SG:
    #         str_result_SG = net_obj.get_graph_attributes(SG, "NetworkID")
    #     self.assertTrue(str_result_SG == "")
    #
    # def get_graph_attributes_wrong_attribute(self):
    #     net_obj = net.Network(inConnectedShp, 'undirected')
    #     net_obj.get_subgraphs()
    #     for SG in net_obj.list_SGL:
    #         str_result_SG = net_obj.get_graph_attributes(SG, "foo")
    #     self.assertTrue(str_result_SG == "")


if __name__ == '__main__':
    unittest.main()