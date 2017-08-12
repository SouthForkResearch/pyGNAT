from qgis.core import *
import networkx as nx
import network as net

from test.utilities import get_qgis_app

QGIS_APP = get_qgis_app()
inSmallNetworkShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_SmallNetwork.shp'
inBraidsShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Braids.shp'
inDisconnectedNetworkShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Disconnected.shp'
inFlowDirectionShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Flow_Direction_small2.shp'
outShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out\test.shp'
outDir = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out'

#network_layer = QgsVectorLayer(inBraidsShp, 'inNetwork', 'ogr')
#network_layer = QgsVectorLayer(inSmallNetworkShp, 'inNetwork', 'ogr')
#network_layer = QgsVectorLayer(inDisconnectedNetworkShp, 'inNetwork', 'ogr')
network_layer = QgsVectorLayer(inFlowDirectionShp, 'inNetwork', 'ogr')

theNetwork = net.Network(network_layer)
list_SG = theNetwork.get_subgraphs()
test_G = theNetwork.calc_network_id(list_SG)
subnet_G = theNetwork.select_by_attribute(test_G, "NetworkID", "net001")

source_node = theNetwork.find_node_with_ID(subnet_G, "_FID_", 2)
flow_error_G = theNetwork.flow_errors(subnet_G, source_node)

theNetwork.add_attribute(subnet_G, "edge_type", "connector")
outflow_G = theNetwork.get_outflow_edges(subnet_G, "edge_type", "outflow")
headwater_G = theNetwork.get_headwater_edges(subnet_G, "edge_type", "headwater")
braid_complex_G = theNetwork.get_complex_braids(subnet_G, "edge_type", "braid, complex")
braid_simple_G = theNetwork.get_simple_braids(subnet_G, "edge_type", "braid, simple")
edge_typed_G = theNetwork.merge_subgraphs(subnet_G,
                                    outflow_G,
                                    headwater_G,
                                    braid_complex_G,
                                    braid_simple_G)
theNetwork._nx_to_shp(edge_typed_G, outDir)



# subnet_ids = ["net001", "net002", "net003"]
# for id in subnet_ids:
#     subnet_G = theNetwork.select_by_attribute(test_G, "NetworkID", id)
#     theNetwork.add_attribute(subnet_G, "edge_type", "connector")
#     outflow_G = theNetwork.get_outflow_edges(subnet_G, "edge_type")


# for u,v,key,d in theNetwork.G.edges_iter(data=True,keys=True):
#     print key, theNetwork.features.get(key)


# for e in G.edges_iter():
#     keys = G.get_edge_data(*e).keys()
#     # Loop through keys if more than one (for braids)
#     for k in keys:
#         data = G.get_edge_data(*e, key=k)
#         g = netgeometry(k, data)