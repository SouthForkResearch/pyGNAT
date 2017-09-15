from qgis.core import *
import networkx as nx
import network as net

from test.utilities import get_qgis_app

QGIS_APP = get_qgis_app()
inSmallNetworkShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_SmallNetwork.shp'
inBraidsShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Braids.shp'
inDisconnectedNetworkShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Disconnected.shp'
inFlowDirectionShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Flow_Direction_small2.shp'
inDuplicatesShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\In\NHD_Duplicates.shp'
outShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out\test.shp'
outDir = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out'

#network_layer = QgsVectorLayer(inBraidsShp, 'inNetwork', 'ogr')
network_layer = QgsVectorLayer(inSmallNetworkShp, 'inNetwork', 'ogr')
#network_layer = QgsVectorLayer(inDisconnectedNetworkShp, 'inNetwork', 'ogr')
#network_layer = QgsVectorLayer(inFlowDirectionShp, 'inNetwork', 'ogr')
#network_layer = QgsVectorLayer(inDuplicatesShp, 'inNetwork', 'ogr')

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
edge_typed_G = theNetwork.merge_subgraphs(subnet_G,
                                    outflow_G,
                                    headwater_G,
                                    braid_complex_G,
                                    braid_simple_G)

# get node types
node_dict={}
type_list=[]
edge_dict = nx.get_edge_attributes(edge_typed_G, 'edge_type')
node_list = [n for n in edge_typed_G.nodes_iter()]
for node in node_list:
    node_pred = edge_typed_G.predecessors(node) # add predecessor node as first value in list for node key
    node_succ = edge_typed_G.successors(node) # add successor node(s) as second value(s) in list for node key
    node_dict[node]=[node_pred,node_succ] # add node as key to node_dict
for nk,nv in node_dict.items():
    for ek,ev in edge_dict.items():
        if nk in ek:
            type_list.append([nk,ev])
nx.set_node_attributes(edge_typed_G, 'node_type', None)
for nd in edge_typed_G.nodes_iter():
    type_subset = [n[1] for n in type_list if nd == n[0]]
    if 'braid' in type_subset and 'headwater' in type_subset:
        t = 'CB'
    elif 'braid' in type_subset and 'connector' in type_subset:
        t = 'CB'
    elif 'braid' in type_subset and 'outflow' in type_subset:
        t = 'CB'
    elif all(ts == 'braid' for ts in type_subset):
        t = 'BB'
    elif len(type_subset) == 2 and 'connector' in type_subset:
        t = 'CC'
    elif all(ts == 'connector' for ts in type_subset):
        t = 'TC'
    elif len(type_subset) == 1 and 'headwater' in type_subset:
        t = 'H'
    elif len(type_subset) == 1 and 'outflow' in type_subset:
        t = 'O'
    else:
        t = ''
    edge_typed_G.node[nd]['node_type'] = t


# calculate river kilometers
outflow_G = theNetwork.select_by_attribute(edge_typed_G, "edge_type", "outflow")
outflow_node = next(v for u, v, key, data in outflow_G.edges_iter(keys=True, data=True))
theNetwork.add_attribute(edge_typed_G, 'river_km', -9999)
for u,v,key,data in edge_typed_G.edges_iter(keys=True, data=True):
    path_len = nx.shortest_path_length(edge_typed_G,
                                       source=u,
                                       target=outflow_node,
                                       weight='_calc_len_')
    river_km = path_len/1000
    data['river_km'] = river_km

theNetwork._nx_to_shp(edge_typed_G, outDir)


# for u,v,key,d in theNetwork.G.edges_iter(data=True,keys=True):
#     print key, theNetwork.features.get(key)


# for e in G.edges_iter():
#     keys = G.get_edge_data(*e).keys()
#     # Loop through keys if more than one (for braids)
#     for k in keys:
#         data = G.get_edge_data(*e, key=k)
#         g = netgeometry(k, data)