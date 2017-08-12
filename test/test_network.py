import unittest

import os
from os import *
from qgis.core import QgsVectorLayer
from utilities import get_qgis_app
import network as net
import networkx as nx

QGIS_APP = get_qgis_app()

inFullNetworkShp = r'C:\JL\Testing\pyGNAT\issue29\In\FullNetwork.shp'
inSmallNetworkShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_SmallNetwork.shp'
inSmallNetworkNoBraidsShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_SmallNetwork_nobraids.shp'
inDisconnectedShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Disconnected.shp'
inConnectedShp = r'C:\JL\Testing\pyGNAT\issue29\In\NHD_Braids.shp'
inBraidSimpleShp = r'C:\JL\Testing\pyGNAT\issue29\In\Braid_simple.shp'
inFlowDirShp = r'C:\JL\Testing\pyGNAT\issue29\In\NHD_Flow_Direction.shp'
outDir = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out'


class NetworkTestCase(unittest.TestCase):
    """Tests for 'network.py' functions"""

    def test_shp_to_nx_as_multidigraph(self):
        network_layer = QgsVectorLayer(inSmallNetworkShp, 'inNetwork', 'ogr')
        theNetwork = net.Network(network_layer, outDir)
        self.assertTrue(theNetwork.G is not None)

    def test_nx_to_shp(self):
        network_layer = QgsVectorLayer(inSmallNetworkShp, 'inNetwork', 'ogr')
        theNetwork = net.Network(network_layer, outDir)
        # FIXME create a new graph and export
        outShp = "{0}\\{1}".format(outDir, "network_lines.shp")
        self.assertTrue(os.path.exists(outShp))


    # def test_get_subgraphs_disconnected(self):
    #     DG = nx.read_shp(inDisconnectedShp)
    #     UG = DG.to_undirected()
    #     list_SG = net.get_subgraphs(UG)
    #     self.assertTrue(len(list_SG) > 0)
    #
    # def test_get_subgraphs_connected(self):
    #     DG = nx.read_shp(inConnectedShp)
    #     UG = DG.to_undirected()
    #     list_SG = net.get_subgraphs(UG)
    #     self.assertTrue(len(list_SG) == 1)
    #
    # def test_get_subgraphs_directed_graph(self):
    #     DG = nx.read_shp(inDisconnectedShp)
    #     list_SG = net.get_subgraphs(DG)
    #     self.assertTrue(len(list_SG) == 0)
    #
    # def test_calc_network_id_multiple_networks(self):
    #     DG = nx.read_shp(inDisconnectedShp)
    #     UG = DG.to_undirected()
    #     list_SG = net.get_subgraphs(UG)
    #     union_SG = net.calc_network_id(list_SG)
    #     self.assertTrue(union_SG is not None)
    #
    # def test_calc_network_id_single_network(self):
    #     DG = nx.read_shp(inConnectedShp)
    #     UG = DG.to_undirected()
    #     list_SG = net.get_subgraphs(UG)
    #     union_SG = net.calc_network_id(list_SG)
    #     self.assertTrue(union_SG is not None)
    #
    # def test_add_attribute_with_name_and_value_new(self):
    #     a_name = "test_name"
    #     a_value = "test_value"
    #     DG = nx.read_shp(inSmallNetworkShp)
    #     net.add_attribute(DG, a_name, a_value)
    #     test_dict = nx.get_edge_attributes(DG, a_name)
    #     self.assertTrue(any(test_dict))
    #
    # def test_add_attribute_with_name_and_value_exists(self):
    #     a_name = "test_name"
    #     a_value = "test_value"
    #     DG = nx.read_shp(inSmallNetworkShp)
    #     net.add_attribute(DG, a_name, a_value)
    #     net.add_attribute(DG, a_name, a_value)
    #     # test_dict = nx.get_edge_attributes(DG, a_name)
    #     # self.assertTrue(any(test_dict))
    #
    # def test_update_attributes_with_name_and_value(self):
    #     a_name = "foo"
    #     a_value = "bar"
    #     u_value = "boo"
    #     DG = nx.read_shp(inSmallNetworkShp)
    #     net.add_attribute(DG, a_name, a_value)
    #     net.update_attribute(DG, a_name, u_value)
    #
    # def test_get_graph_attributes_with_networkID(self):
    #     DG = nx.read_shp(inConnectedShp)
    #     UG = DG.to_undirected()
    #     list_SG = net.get_subgraphs(UG)
    #     union_SG = net.calc_network_id(list_SG)
    #     str_result_SG = net.get_graph_attributes(union_SG, "NetworkID")
    #     self.assertTrue(str_result_SG != "")
    #
    # def test_get_graph_attributes_without_networkID(self):
    #     DG = nx.read_shp(inConnectedShp)
    #     UG = DG.to_undirected()
    #     list_SG = net.get_subgraphs(UG)
    #     for SG in list_SG:
    #         str_result_SG = net.get_graph_attributes(SG, "NetworkID")
    #     self.assertTrue(str_result_SG == "")
    #
    # def test_get_graph_attributes_wrong_attribute(self):
    #     DG = nx.read_shp(inConnectedShp)
    #     UG = DG.to_undirected()
    #     list_SG = net.get_subgraphs(UG)
    #     for SG in list_SG:
    #         str_result_SG = net.get_graph_attributes(SG, "foo")
    #     self.assertTrue(str_result_SG == "")
    #
    # def test_select_by_attribute_existing_attributes(self):
    #     a_name = "foo"
    #     a_value = "bar"
    #     DG = nx.read_shp(inSmallNetworkShp)
    #     net.add_attribute(DG, a_name, a_value)
    #     net.select_by_attribute(DG, a_name, a_value)
    #     test_dict = nx.get_edge_attributes(DG, a_name)
    #     self.assertTrue(any(test_dict))
    #
    # def test_select_by_attribute_no_attribute(self):
    #     a_name = "foo"
    #     a_value = "bar"
    #     DG = nx.read_shp(inSmallNetworkShp)
    #     net.select_by_attribute(DG, a_name, a_value)
    #     test_dict = nx.get_edge_attributes(DG, a_name)
    #     self.assertFalse(any(test_dict))
    #
    # def test_get_outflow_edges_directed_graph(self):
    #     a_name = "ReachType"
    #     DG = nx.read_shp(inSmallNetworkShp)
    #     outflow_G = net.get_outflow_edges(DG, a_name)
    #     self.assertTrue(outflow_G is not None)
    #
    # def test_get_outflow_edges_undirected_graph(self):
    #     a_name = "ReachType"
    #     DG = nx.read_shp(inSmallNetworkShp)
    #     UG = DG.to_undirected()
    #     outflow_G = net.get_outflow_edges(UG, a_name)
    #     total_edges = nx.edges(outflow_G)
    #     self.assertTrue(len(total_edges) == 0)
    #
    # def test_get_headwater_edges_directed_graph(self):
    #     a_name = "ReachType"
    #     DG = nx.read_shp(inSmallNetworkShp)
    #     headwater_G = net.get_headwater_edges(DG, a_name)
    #     self.assertTrue(headwater_G is not None)
    #
    # def test_get_headwater_edges_undirected_graph(self):
    #     a_name = "ReachType"
    #     DG = nx.read_shp(inSmallNetworkShp)
    #     UG = DG.to_undirected()
    #     headwater_G = net.get_headwater_edges(UG, a_name)
    #     total_edges = nx.edges(headwater_G)
    #     self.assertTrue(len(total_edges) == 0)
    #
    # def test_get_braid_edges_directed_graph(self):
    #     a_name = "ReachType"
    #     DG = nx.read_shp(inSmallNetworkShp, simplify=True)
    #     net.add_attribute(DG, a_name, "connector")
    #     braid_G = net.get_braid_edges(DG, a_name)
    #     self.assertTrue(braid_G is not None)
    #
    # def test_get_braid_edges_undirected_graph(self):
    #     a_name = "ReachType"
    #     DG = nx.read_shp(inConnectedShp, simplify=False)
    #     net.add_attribute(DG, a_name, "connector")
    #     UG = DG.to_undirected()
    #     braid_G = net.get_braid_edges(UG, a_name)
    #     total_edges = nx.edges(braid_G)
    #     self.assertTrue(len(total_edges) == 0)
    #
    # def test_get_braid_edges_no_braids(self):
    #     a_name = "ReachType"
    #     DG = nx.read_shp(inDisconnectedShp, simplify=False)
    #     net.add_attribute(DG, a_name, "connector")
    #     braid_G = net.get_braid_edges(DG, a_name)
    #     total_edges = nx.edges(braid_G)
    #     self.assertTrue(len(total_edges) == 0)
    #
    # def test_merge_subgraphs_with_braids(self):
    #     a_name = "ReachType"
    #     DG = net.import_shp(inSmallNetworkShp)
    #     net.add_attribute(DG, a_name, "connector")
    #     outflow_G = net.get_outflow_edges(DG, a_name)
    #     headwater_G = net.get_headwater_edges(DG, a_name)
    #     braid_G = net.get_braid_edges(DG, a_name)
    #     final_G = net.merge_subgraphs(DG, outflow_G, headwater_G, braid_G)
    #     net.export_shp(final_G, inSmallNetworkShp, outShp)
    #     self.assertTrue(final_G is not None)
    #
    def test_merge_subgraphs_with_no_braids(self):
        a_name = "ReachType"
        DG = nx.read_shp(inSmallNetworkNoBraidsShp, simplify=False)
        net.add_attribute(DG, a_name, "connector")
        outflow_G = net.get_outflow_edges(DG, a_name)
        headwater_G = net.get_headwater_edges(DG, a_name)
        braid_G = net.get_braid_edges(DG, a_name)
        final_G = net.merge_subgraphs(DG, outflow_G, headwater_G, braid_G)
        net.export_shp(final_G, inSmallNetworkShp, outShp)  # temporary for review
        self.assertTrue(final_G is not None)
    #
    # def test_error_flow_dir(self):
    #     DG = nx.read_shp(inFlowDirShp, simplify=True)
    #     nodeID = net.findnodewithID(DG, 2695)
    #     error_G = net.flow_errors(DG, nodeID[1])
    #     nx.write_shp(error_G, outShp)
    #     error_only_G = net.select_by_attribute(error_G, "error_flow", 1)
    #     self.assertTrue(error_only_G is not None)
    #
    # def test_get_unique_attributes(self):
    #     DG = net.import_shp(inDisconnectedShp)
    #     dict_attrb = nx.get_edge_attributes(DG, "NetworkID")
    #     if len(dict_attrb) > 0:
    #         network_id_list = net.get_unique_attrb(dict_attrb)
    #     self.assertGreater(network_id_list, 0)
    #

    if __name__ == '__main__':
        unittest.main()