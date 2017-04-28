import networkx as nx
import lib.network as net

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
    UG = DG.to_undirected()
    braid_G = nx.DiGraph()
    for edge in DG.edges(data=True):
        is_edge = get_edge_in_cycle(edge, UG)
        if is_edge == True:
            braid_G.add_edge(*edge)
    net.update_attribute(braid_G, attrb_field, "braid")
    return braid_G

#test
inBraidSimpleShp = r'C:\dev\pyGNAT\experiments\shapefiles\Braid_simple.shp'
outShp = r'C:\JL\Testing\pyGNAT\NetworkFeatures\Out\output_test.shp'

DG = nx.read_shp(inBraidSimpleShp, simplify=False)
attrb_field = "ReachType"
net.add_attribute(DG, attrb_field, "connector")

braid_G = get_braid_edges(DG, attrb_field)
nx.write_shp(braid_G, outShp)