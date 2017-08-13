#   Name:           Network
#   Description:    Main class used for building and manipulating
#                   network topologies.
#   Authors:        Jesse Langdon, jesse@southforkresearch.org
#                   Matt Reimer, matt@northarrowresearch.com
#   Created:        4/6/2017
#   Revised:        7/26/2017

import os.path
import ogr
from qgis.core import *
import networkx as nx


class Network():

    def __init__(self, in_network_lyr, msgcallback=None):
        """
        Main class for processing stream networks in GNAT.
        """

        self.msgcallback = msgcallback
        self.id_field = "_FID_"
        self.features = {}
        self.cols = []

        # get QgsCoordinateReferenceSystem from QgsVectorLayer
        self.crs = in_network_lyr.crs()
        self.epsg = self.crs.authid()

        # Convert QgsVectorLayer to NX MultiDiGraph
        self._shp_to_nx(in_network_lyr, simplify=True)

    def _shp_to_nx(self, in_network_lyr, simplify=True, geom_attrs=True):
        """
        THIS IS a re-purposed version of read_shp from nx
        :param shapelayer:
        :param simplify:
        :param geom_attrs:
        :return:
        """
        self.G = nx.MultiDiGraph()

        for f in in_network_lyr.getFeatures():

            flddata = f.attributes()
            # change NULL values to None, so that OGR can export graphs to shapefiles at a later time.
            for n,i in enumerate(flddata):
                if i==NULL:
                    flddata[n]=None
            fields = [str(fi.name()) for fi in f.fields()]

            geo = f.geometry()
            # We don't care about M or Z
            geo.geometry().dropMValue()
            geo.geometry().dropZValue()

            attributes = dict(zip(fields, flddata))
            # Add a new _FID_ field
            fid = int(f.id())
            attributes[self.id_field] = fid
            attributes['_calc_len_'] = geo.length()

            # Note:  Using layer level geometry type
            if geo.wkbType() in (QgsWKBTypes.LineString, QgsWKBTypes.MultiLineString):
                for edge in self.edges_from_line(geo, attributes, simplify, geom_attrs):
                    e1, e2, attr = edge
                    self.features[fid] = attr
                    self.G.add_edge(tuple(e1), tuple(e2), key=attr[self.id_field], attr_dict=attr)
                self.cols = self.features[self.features.keys()[0]].keys()
            else:
                raise ImportError("GeometryType {} not supported. For now we only support LineString types.".
                                  format(QgsWKBTypes.displayString(int(geo.wkbType()))))

    def _nx_to_shp(self, G, out_dir):
        """
        This is a re-purposing of the NetworkX write_shp module with some minor changes.
        :param G: networkx directional graph
        :param outdir: directory where output shapefiles will be written
        """

        # easier to debug in python if ogr throws exceptions
        ogr.UseExceptions()

        # set spatial reference for output shapefile
        srs = ogr.osr.SpatialReference()
        srs.ImportFromEPSG(int(self.epsg[5:]))

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
        shpdir = drv.CreateDataSource("{0}".format(out_dir))
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
        fields = {}  # storage for field names and their data types
        attributes = {}  # storage for attribute data (indexed by field names)

        # Conversion dict between python and ogr types
        OGRTypes = {int: ogr.OFTInteger, str: ogr.OFTString, float: ogr.OFTReal}

        # Edge loop
        for u,v,k,data in G.edges_iter(data=True,keys=True):
            g = netgeometry(k, data)
            # Loop through attribute data in edges
            for f_key, f_data in data.items():
                # Reject spatial data not required for attribute table
                if (f_key != 'Json' and f_key != 'Wkt' and f_key != 'Wkb'
                and f_key != 'ShpName'):
                    # For all edges check/add field and data type to fields dict
                    if f_key not in fields:
                        # Field not in previous edges so add to dict
                        if type(f_data) in OGRTypes:
                            fields[f_key] = OGRTypes[type(f_data)]
                        else:
                            # Data type not supported, default to string (char 80)
                            fields[f_key] = ogr.OFTString
                        newfield = ogr.FieldDefn(f_key, fields[f_key])
                        edges.CreateField(newfield)
                        # Store the data from new field to dict for CreateLayer()
                        attributes[f_key] = f_data
                    else:
                        # Field already exists, add data to dict for CreateLayer()
                        attributes[f_key] = f_data
            # Create the feature with geometry, passing new attribute data
            create_feature(g, edges, attributes)
        nodes, edges = None, None
        return

    def edges_from_line(self, geom, attrs, simplify=True, geom_attrs=True):
        """
        This is repurposed from the shape helper here:
        https://github.com/networkx/networkx/blob/master/networkx/readwrite/nx_shp.py
        :return:
        """
        if geom.wkbType() == QgsWKBTypes.LineString:
            pline = geom.asPolyline()
            if simplify:
                edge_attrs = attrs.copy()
                # DEBUGGING
                edge_attrs["Wkt"] = geom.exportToWkt()
                if geom_attrs:
                    edge_attrs["Wkb"] = geom.asWkb()
                    edge_attrs["Wkt"] = geom.exportToWkt()
                    edge_attrs["Json"] = geom.exportToGeoJSON()
                yield (pline[0], pline[-1], edge_attrs)
            else:
                for i in range(0, len(pline) - 1):
                    pt1 = pline[i]
                    pt2 = pline[i + 1]
                    edge_attrs = attrs.copy()
                    if geom_attrs:
                        segment = ogr.Geometry(ogr.wkbLineString)
                        segment.AddPoint_2D(pt1[0], pt1[1])
                        segment.AddPoint_2D(pt2[0], pt2[1])
                        edge_attrs["Wkb"] = segment.asWkb()
                        edge_attrs["Wkt"] = segment.exportToWkt()
                        edge_attrs["Json"] = segment.exportToGeoJSON()
                        del segment
                    yield (pt1, pt2, edge_attrs)

        # TODO: MULTILINESTRING MIGHT NOT WORK
        elif geom.wkbType() == QgsWKBTypes.MultiLineString:
            for i in range(geom.GetGeometryCount()):
                geom_i = geom.GetGeometryRef(i)
                for edge in self.edges_from_line(geom_i, attrs, simplify, geom_attrs):
                    yield edge

    def get_subgraphs(self):
        """
        Find all subgraphs that are disconnected.
        :param self: graph must be undirected to use this method.
        """
        try:
            list_SG = list(nx.weakly_connected_component_subgraphs(self.G, copy=True))
            return list_SG
        except:
            print "ERROR: Could not find subgraphs"
            list_SG = []
            return list_SG

    def calc_network_id(self, list_SG):
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
                self.add_attribute(SG, attrb_field, network_id)
                subgraph_count += 1
            union_SG = nx.union_all(list_SG)
            return union_SG
        except:
           raise IndexError  # not sure about this... will probably change later

    def get_graph_attributes(self, G, attrb_name):
        total_edges = G.number_of_edges()
        edge_dict = nx.get_edge_attributes(G, attrb_name)
        if len(edge_dict) > 0:
            list_summary = []
            list_summary.append("Total number of edges in network: {0}".format(total_edges))
            networks = sorted(set(val for val in edge_dict.values()))
            for network in networks:
                select_G = self.select_by_attribute(G, attrb_name, network)
                select_edges = [(u,v,k,d) for u,v,k,d in select_G.edges(data=True, keys=True)]
                select_edges_len = len(select_edges)
                list_summary.append("Network ID: {0} - Total number of edges: {1}".format(network, select_edges_len))
            return list_summary
        else:
            list_summary = []
            print "ERROR: Network ID attribute not found"
            return list_summary

    def add_attribute(self, G, attrb_name, attrb_value):
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

    def select_by_attribute(self, G, attrb_name, attrb_value):
        """
        Select all edges within a multigraph based on the user-supplied attribute value
        :param attrb_name: name of the attribute that will be used for the selection
        :param attrb_value: attribute value to select by
        """
        select_G = nx.MultiDiGraph()
        for u,v,k,d in G.edges_iter(data=True,keys=True):
            if d[attrb_name]==attrb_value:
                keys = G.get_edge_data(u,v).keys()
                # Loop through keys if more than one (for braids)
                for ky in keys:
                    data = G.get_edge_data(u,v, key=ky)
                    select_G.add_edge(u,v,ky,data)
        return select_G
        # else:
        #     print "ERROR: Attribute not found"
        #     select_G = nx.null_graph()
        #     return select_G

    def update_attribute(self, G, attrb_name, attrb_value):
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

    def get_outflow_edges(self, G, attrb_field, attrb_name):
        """
        Create graph with the outflow edge attributed
        :param attrb_type: name of the attribute field
        :return outflow_G: graph with new headwater attribute
        """
        if nx.is_directed(G):
            # find the outflow node (should have zero outgoing edges, right?)
            list_nodes = [n for n in G.nodes_iter()]
            list_successors = []
            for node in list_nodes:
                list_successors.append(tuple((node, len(G.edges(node)))))
            for i in list_successors:
                if i[1] == 0:
                    # get the edge that is connected to outflow node
                    outflow_edge = G.in_edges(i[0], data=True, keys=True)
                    outflow_G = nx.MultiDiGraph(outflow_edge)
            # set reach_type attribute for outflow and headwater edges
            self.update_attribute(outflow_G, attrb_field, attrb_name)
            return outflow_G
        else:
            print "ERROR: Graph is not directed."
            outflow_G = nx.null_graph()
            return outflow_G

    def get_headwater_edges(self, G, attrb_field, attrb_name):
        """
        Create graph with the headwater edges attributed
        :param attrb_field: name of the attribute field
        :return headwater_G: graph with new attribute
        """
        if nx.is_directed(G):
            RG = nx.reverse(G, copy=True)
            list_nodes = [n for n in RG.nodes_iter()]
            list_successors = []
            for node in list_nodes:
                list_successors.append(tuple((node, len(RG.edges(node)))))
            headwater_G = nx.MultiDiGraph()
            for i in list_successors:
                if i[1] == 0:
                    headwater_edge = RG.in_edges(i[0], data=True, keys=True)
                    headwater_G.add_edge(*(headwater_edge.pop()))
            headwater_RG = nx.reverse(headwater_G, copy=True)
            self.update_attribute(headwater_RG, attrb_field, attrb_name)
            return headwater_RG
        else:
            print "ERROR: Graph is not directed."
            headwater_G = nx.null_graph()
            return headwater_G

    def get_complex_braids(self, G, attrb_field, attrb_name):
        """
        Create graph with the complex braid edges attributed
        :param attrb_field: name of the attribute field
        :return braid_G: graph with new attribute
        """
        if nx.is_directed(G):
            UG = nx.Graph(G)
            braid_G = nx.MultiDiGraph()
            for edge in G.edges(data=True, keys=True):
                is_edge = self.get_edge_in_cycle(edge, UG)
                if is_edge == True:
                    braid_G.add_edge(*edge)
            self.update_attribute(braid_G, attrb_field, attrb_name)
            return braid_G
        else:
            print "ERROR: Graph is not directed."
            braid_complex_G = nx.null_graph()
            return braid_complex_G

    def get_simple_braids(self, G, attrb_field, attrb_name):
        """
        Create graph with the simple braid edges attributed
        :param attrb_field: name of the attribute field
        :return braid_G: graph with new attribute
        """
        braid_simple_G = nx.MultiDiGraph()
        parallel_edges = []
        for e in G.edges_iter():
            keys = G.get_edge_data(*e).keys()
            if keys not in parallel_edges:
                if len(keys) == 2:
                    for k in keys:
                        data = G.get_edge_data(*e, key=k)
                        braid_simple_G.add_edge(e[0], e[1], key=k, attr_dict=data)
            parallel_edges.append(keys)
        self.update_attribute(braid_simple_G, attrb_field, attrb_name)
        return braid_simple_G

    def get_edge_in_cycle(self, edge, G):
        u, v, key, d = edge
        list_cycles = nx.cycle_basis(G)
        cycle_edges = [zip(nodes,(nodes[1:]+nodes[:1])) for nodes in list_cycles]
        found = False
        for cycle in cycle_edges:
            if (u, v) in cycle or (v, u) in cycle:
                found = True
        return found

    def merge_subgraphs(self, G, outflow_G, headwater_G, braid_complex_G, braid_simple_G):
        """
        Join all subgraphs with the main graph
        :param list_G: list of subgraphs with reach type attribute added
        :return G_compose: final graph output with all reach type attributes included
        """
        G1 = nx.compose(G, outflow_G)
        G2 = nx.compose(G1, headwater_G)
        if braid_complex_G is not None:
            G3 = nx.compose(G2, braid_complex_G)
        if braid_simple_G is not None:
            self.edge_typed_G = nx.compose(G3, braid_simple_G)
        if braid_complex_G is None or braid_simple_G is None:
            self.edge_typed_G = G2
        return self.edge_typed_G

    def find_node_with_ID(self, G, id_field, id_value):
        """
        Helper function to find a node with a given ID field and value
        :param G: MultiDiGraph
        :param id: OBJECTID value
        :return: single edge
        """
        return next(iter([e for e in G.edges_iter(data=True,keys=True) if G.get_edge_data(*e)[id_field] == id_value]), None)

    def get_unique_attrb(self, dict):
        unique_attrbs = sorted(set(dict.values()))
        return unique_attrbs

    def error_flow(self, G, src_node, ud=None):
        """Returns the first edges that do not conform to the flow direction
        implicit in defined source node.
        G: target digraph
        src: source nodes
        ud: undirected graph (faster iteration with setdirection)
        """
        RG = nx.reverse(G, copy=True)
        flipped_G = nx.MultiDiGraph()
        upstream_list = []
        gnodes = list(nx.dfs_preorder_nodes(RG, src_node[1]))
        if not ud:
            ud = RG.to_undirected()
        connected = RG.edges(nx.dfs_tree(ud, src_node[1]).nodes(), data=True, keys=True)

        for edge in connected:
            start = edge[0]
            end = edge[1]
            if end in gnodes and start not in gnodes:
                upstream_list.append(edge)

        # add new "error_flow" attribute to graph
        self.add_attribute(RG, "error_flow", "0")  # add 'default' value
        for u,v,key,d in RG.edges_iter(keys=True,data=True):
            if (u,v,key,d) in upstream_list:
                flipped_G.add_edge(u,v,key,d)
        if flipped_G is not None:
            self.update_attribute(flipped_G, "error_flow", "1")
        nx.reverse(RG)
        upstream_G = nx.compose(RG, flipped_G)
        return upstream_G

    def error_dup(self, G):
        """Returns parallel edges with identical lengths
        G: target digraph
        return: multidigraph with new error_dup attribute field
        """
        self.add_attribute(G, 'error_dupe', 0)
        duplicates_G = nx.MultiDiGraph()
        for e in G.edges_iter():
            keys = G.get_edge_data(*e).keys()
            if len(keys) == 2:
                length_list = []
                for k in keys:
                    data = G.get_edge_data(*e, key=k)
                    length_list.append((e[0],e[1],k,data))
                if length_list[0][3]['_calc_len_'] == length_list[1][3]['_calc_len_']:
                    for i in length_list:
                        duplicates_G.add_edge(i[0],i[1],i[2],i[3])
        self.update_attributes(duplicates_G, 'error_dupe', 1)
        dupes_G = nx.compose()
        return dupes_G


# TODO
def get_node_types(G, id, attrb_field, attrb_value):
    ### pseudo-code ###
    # reverse direction of network
    reverse_G = G.reverse(copy=True)
    # start at outflow node
    outflow_node = findnodewithID(reverse_G, id)
    # add NODE_TYPE = 'outflow'
    add_attribute(reverse_G, "NodeType", "outflow")
    # iterate through nodes up network

    # for each node:
        # get list of connected edges (or nodes) using "neighbor" function
        # and degree for each node
        # need a detailed series of conditional statements:
            # if braid and connector in neighbor list:
                # node_type = "braid-to-connector"
            # elif only braids in neighbor list:
                # node_type = "braid-to-braid"
            # elif only connectors and degree > 2:
                # node_type = 'tributary confluence"
            # elif two or more outflows in neighbor list:
                # node_type = 'outflow'
            # elif two or more headwaters in neighbor list:
                # node_type = 'headwater'
    return