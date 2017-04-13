import unittest
import lib.network as net

inFullNetworkShp = r'C:\dev\pyGNAT\experiments\shapefiles\FullNetwork.shp'

class NetworkTestCase(unittest.TestCase):
    """Tests for 'network.py'"""

    def test_init_network_with_line_shapefile(self):
        network_obj = net.Network(inFullNetworkShp)
        self.assertIsInstance(network_obj, net.Network)

    def test_init_network_with_no_input(self):
        network_obj = net.Network()
        self.assertTrue(network_obj.data_source != '')


if __name__ == '__main__':
    unittest.main()