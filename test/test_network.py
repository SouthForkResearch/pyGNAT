import unittest
import lib.network as net

inFullNetworkShp = r'C:\dev\pyGNAT\experiments\shapefiles\FullNetwork.shp'
inDisconnectedShp = r'C:\dev\pyGNAT\experiments\shapefiles\NHD_Disconnected.shp'
inConnectedShp = r'C:\dev\pyGNAT\experiments\shapefile'

class NetworkTestCase(unittest.TestCase):
    """Tests for 'network.py'"""

    def test_init_network_with_line_shapefile(self):
        network_obj = net.Network(inFullNetworkShp)
        self.assertIsInstance(network_obj, net.Network)

    def test_init_network_with_no_input(self):
        network_obj = net.Network()
        self.assertTrue(network_obj.data_source != '')

    def test_get_subgraphs_disconnected(self):
        network_obj = net.Network(inDisconnectedShp, 'undirected' )
        network_obj.get_subgraphs()
        self.assertTrue(len(network_obj.list_SG) > 0)

    def test_get_subgraphs_connected(self):
        network_obj = net.Network(inConnectedShp, 'undirected')
        network_obj.get_subgraphs()
        self.assertTrue(len(network_obj.list_SG) == 0)

    def test_get_subgraphs_directed_graph(self):
        network_obj = net.Network(inDisconnectedShp)
        network_obj.get_subgraphs()
        self.assertTrue(len(network_obj.list_SG) == 0)

    def test_calc_network_id_multiple_networks(self):
        network_obj = net.Network(inFullNetworkShp, 'undirected')
        network_obj.get_subgraphs()
        union_SG = network_obj.calc_network_id()
        self.assertTrue(union_SG is not None)

if __name__ == '__main__':
    unittest.main()