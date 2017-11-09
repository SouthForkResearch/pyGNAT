from qgis.core import *
import networkx as nx
import network as net
import time

from test.utilities import get_qgis_app

QGIS_APP = get_qgis_app()
inSmallNetworkShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_SmallNetwork.shp'
inMedNetworkShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_MedNetwork.shp'
inBraidsShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Braids.shp'
inDisconnectedNetworkShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Disconnected.shp'
inFlowDirectionShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Flow_Direction_small2.shp'
inDuplicatesShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Duplicates.shp'
outShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out\test.shp'
outDir = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out'

# timing
t0 = time.time()

#network_layer = QgsVectorLayer(inBraidsShp, 'inNetwork', 'ogr')
#network_layer = QgsVectorLayer(inMedNetworkShp, 'inNetwork', 'ogr')
#network_layer = QgsVectorLayer(inDisconnectedNetworkShp, 'inNetwork', 'ogr')
#network_layer = QgsVectorLayer(inFlowDirectionShp, 'inNetwork', 'ogr')
#network_layer = QgsVectorLayer(inDuplicatesShp, 'inNetwork', 'ogr')
network_layer = QgsVectorLayer(inSmallNetworkShp, 'inNetwork', 'ogr')

theNetwork = net.Network(network_layer)
list_SG = theNetwork.get_subgraphs()
id_G = theNetwork.calc_network_id(list_SG)
subnet_G = theNetwork.select_by_attribute(id_G, "NetworkID", "net001")

# dupes_G = theNetwork.error_dup(subnet_G)
# source_node = theNetwork.find_node_with_ID(subnet_G, "_FID_", 2)
# flow_error_G = theNetwork.error_flow(subnet_G, source_node)

theNetwork.add_attribute(subnet_G, "edge_type", "connector")
outflow_G = theNetwork.get_outflow_edges(subnet_G, "edge_type", "outflow")
headwater_G = theNetwork.get_headwater_edges(subnet_G, "edge_type", "headwater")
braid_complex_G = theNetwork.get_complex_braids(subnet_G, "edge_type", "braid")
braid_simple_G = theNetwork.get_simple_braids(subnet_G, "edge_type", "braid")
gnat_G = theNetwork.merge_subgraphs(subnet_G,
                                    outflow_G,
                                    headwater_G,
                                    braid_complex_G,
                                    braid_simple_G)

# set node types
theNetwork.set_node_types()

# calculate river kilometers
outflow_G = theNetwork.select_by_attribute(gnat_G, "edge_type", "outflow")
outflow_node = next(v for u, v, key, data in outflow_G.edges_iter(keys=True, data=True))
theNetwork.add_attribute(gnat_G, 'river_km', -9999)
for u,v,key,data in gnat_G.edges_iter(keys=True, data=True):
    path_len = nx.shortest_path_length(gnat_G,
                                       source=u,
                                       target=outflow_node,
                                       weight='_calc_len_')
    river_km = path_len/1000
    data['river_km'] = river_km

theNetwork.streamorder()
theNetwork._nx_to_shp(gnat_G, outDir)


# # stream order
# processed_G = nx.MultiDiGraph()
# theNetwork.add_attribute(gnat_G, 'stream_order', '-9999')
# i = 1

# headwater_G = theNetwork.get_headwater_edges(gnat_G, "edge_type", "headwater")
# for u,v,k,d in gnat_G.edges_iter(data=True, keys=True):
#     if headwater_G.has_edge(u, v, key=k):
#         gnat_G.add_edge(u,v,key=k, stream_order=i)
#         processed_G.add_edge(u,v,key=k)
#
# del u, v, k, d
#
# prev_sel_G = theNetwork.select_by_attribute(theNetwork.gnat_G, "stream_order", i)
# for u,v,k,d in gnat_G.edges_iter(data=True, keys=True):
#     if prev_sel_G.has_edge(u, v, key=k):
#         out_edges = gnat_G.out_edges(v, data=True, keys=True)
#         for e in out_edges:
#             if gnat_G.node[e[1]]['node_type'] == 'TC' or gnat_G.node[e[1]]['node_type'] == 'CB':
#                 gnat_G.edge[e[0]][e[1]][e[2]]['stream_order'] = i+1
#             else:
#                 gnat_G.edge[e[0]][e[1]][e[2]]['stream_order'] = i
# next_sel_G = theNetwork.select_by_attribute(theNetwork.gnat_G, "stream_order", i + 1)
# i += 1

print time.time() - t0, "seconds (wall time)" #print time elapsed in "seconds wall time"