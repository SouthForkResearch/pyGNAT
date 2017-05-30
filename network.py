#   Name:           Network
#   Description:    Main library of functions for building network topologies.
#   Authors:        Jesse Langdon, jesse@southforkresearch.org
#                   Matt Reimer, matt@northarrowresearch.com
#   Created:        4/6/2017
#   Revised:        5/5/2017

import os.path
import networkx as nx


def import_shp(file_path):
    if os.path.isfile(file_path) and file_path.endswith(".shp"):
        DG = nx.read_shp(file_path)
        return DG
    else:
        print "ERROR: Could not convert to networkx graph, not a shapefile"
        DG = nx.Graph()
        return DG

# FIXME need to finish implementing this
# def export_shp(G, folder_path):
#     if G is not None:
#         nx.write_shp(G, folder_path)
#     else:
#         print "ERROR: Could not write to shapefile, graph is empty"
#     return

def export_shp(G, inshp, outdir):
    """
    This is a re-purposing of the NetworkX write_shp module with some minor changes.
    :param G: networkx directional graph 
    :param outdir: directory where output shapefiles will be written
    """
    try:
        from osgeo import ogr
    except ImportError:
        raise ImportError("write_shp requires OGR: http://www.gdal.org/")
    # easier to debug in python if ogr throws exceptions
    ogr.UseExceptions()

    def get_input_srs(inshp):
        in_driver = ogr.GetDriverByName('ESRI Shapefile')
        in_src = in_driver.Open(inshp, 0)
        in_lyr = in_src.GetLayer()
        in_srs = in_lyr.GetSpatialRef()
        return in_srs

    def netgeometry(key, data):
        if 'Wkb' in data:
            geom = ogr.CreateGeometryFromWkb(data['Wkb'])
        elif 'Wkt' in data:
            geom = ogr.CreateGeometryFromWkt(data['Wkt'])
        elif type(key[0]).__name__ == 'tuple':  # edge keys are packed tuples
            geom = ogr.Geometry(ogr.wkbLineString)
            _from, _to = key[0], key[1]
            try:
                geom.SetPoint(0, *_from)
                geom.SetPoint(1, *_to)
            except TypeError:
                # assume user used tuple of int and choked ogr
                _ffrom = [float(x) for x in _from]
                _fto = [float(x) for x in _to]
                geom.SetPoint(0, *_ffrom)
                geom.SetPoint(1, *_fto)
        else:
            geom = ogr.Geometry(ogr.wkbPoint)
            try:
                geom.SetPoint(0, *key)
            except TypeError:
                # assume user used tuple of int and choked ogr
                fkey = [float(x) for x in key]
                geom.SetPoint(0, *fkey)

        return geom

    # Create_feature with new optional attributes arg (should be dict type)
    def create_feature(geometry, lyr, attributes=None):
        feature = ogr.Feature(lyr.GetLayerDefn())
        feature.SetGeometry(g)
        if attributes != None:
            # Loop through attributes, assigning data to each field
            for field, data in attributes.items():
                feature.SetField(field, data)
        lyr.CreateFeature(feature)
        feature.Destroy()

    node_name = "network_nodes"
    edge_name = "network_lines"
    drv = ogr.GetDriverByName("ESRI Shapefile")
    shpdir = drv.CreateDataSource(outdir)
    srs = get_input_srs(inshp)
    try:
        shpdir.DeleteLayer(node_name)
    except:
        pass
    nodes = shpdir.CreateLayer(node_name, srs, ogr.wkbPoint)
    for n in G:
        data = G.node[n]
        g = netgeometry(n, data)
        create_feature(g, nodes)
        try:
            shpdir.DeleteLayer(edge_name)
        except:
            pass
    edges = shpdir.CreateLayer(edge_name, srs, ogr.wkbLineString)

    # New edge attribute write support merged into edge loop
    fields = {}      # storage for field names and their data types
    attributes = {}  # storage for attribute data (indexed by field names)

    # Conversion dict between python and ogr types
    OGRTypes = {int: ogr.OFTInteger, str: ogr.OFTString, float: ogr.OFTReal}

    # Edge loop
    for e in G.edges(data=True):
        data = G.get_edge_data(*e)
        g = netgeometry(e, data)
        # Loop through attribute data in edges
        for key, data in e[2].items():
            # Reject spatial data not required for attribute table
            if (key != 'Json' and key != 'Wkt' and key != 'Wkb'
                and key != 'ShpName'):
                  # For all edges check/add field and data type to fields dict
                    if key not in fields:
                  # Field not in previous edges so add to dict
                        if type(data) in OGRTypes:
                            fields[key] = OGRTypes[type(data)]
                        else:
                            # Data type not supported, default to string (char 80)
                            fields[key] = ogr.OFTString
                        # Create the new field
                        newfield = ogr.FieldDefn(key, fields[key])
                        edges.CreateField(newfield)
                        # Store the data from new field to dict for CreateLayer()
                        attributes[key] = data
                    else:
                     # Field already exists, add data to dict for CreateLayer()
                        attributes[key] = data
        # Create the feature with, passing new attribute data
        create_feature(g, edges, attributes)

    nodes, edges = None, None


def get_subgraphs(G):
    """
    Find all subgraphs that are disconnected.
    :param self: graph must be undirected to use this method.
    """
    try:
        UG = G.to_undirected()
        list_SG = list(nx.connected_component_subgraphs(UG))
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
    if nx.is_directed(G):
        DG = G
    else:
        DG = G.to_directed()
    total_edges = G.number_of_edges()
    edge_dict = nx.get_edge_attributes(DG, attrb_name)
    if len(edge_dict) > 0:
        list_summary=[]
        list_summary.append("Total number of edges in network: {0}".format(total_edges))
        networks = sorted(set(val for val in edge_dict.values()))
        for network in networks:
            select_G = select_by_attribute(DG, "NetworkID", network)
            select_total_edges = select_G.number_of_edges()
            list_summary.append("Network ID: {0} - Total number of edges: {1}".format(network, select_total_edges))
        del DG
        return list_summary
    else:
        list_summary = []
        print "ERROR: Network ID attribute not found"
        return list_summary


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
        select_G = nx.Graph([(u, v, d) for u, v, d in G.edges(data=True) if d[attrb_name] == attrb_value])
        return select_G
    else:
        print "ERROR: Attribute not found"
        select_G = nx.null_graph()
        return select_G


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
        update_attribute(headwater_G, attrb_field, "headwater")
        return headwater_G
    else:
        print "ERROR: Graph is not directed."
        headwater_G = nx.null_graph()
        return headwater_G


def get_edge_in_cycle(edge, G):
    u, v, d = edge
    list_cycles = nx.cycle_basis(G)
    cycle_edges = [zip(nodes,(nodes[1:]+nodes[:1])) for nodes in list_cycles]
    found = False
    for cycle in cycle_edges:
        if (u, v) in cycle or (v, u) in cycle:
            found = True
    return found


def get_braid_edges(DG, a_name):
    """
    Create graph with the braid edges attributed
    :param attrb_field: name of the attribute field
    :return braid_G: graph with new attribute
    """
    if nx.is_directed(DG):
        UG = DG.to_undirected()
        braid_G = nx.DiGraph()
        for edge in DG.edges(data=True):
            is_edge = get_edge_in_cycle(edge, UG)
            if is_edge == True:
                braid_G.add_edge(*edge)
        update_attribute(braid_G, a_name, "braid")
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
