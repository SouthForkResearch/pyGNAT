import networkx as nx


def update_attribute(G, attrb_name, attrb_value):
    dict = nx.get_edge_attributes(G, attrb_name)  # check if
    if len(dict) > 0:
        nx.set_edge_attributes(G, attrb_name, attrb_value)
    else:
        print "ERROR: Attribute not found"
        exit(0)
    return


def add_attribute(G, attrb_name, attrb_value):
    dict = nx.get_edge_attributes(G, attrb_name)
    if len(dict) == 0:
        nx.set_edge_attributes(G, attrb_name, attrb_value)
    else:
        print "ERROR: Attribute already exists"
        exit(0)
    return


def select_by_attribute(G, attrb_name, attrb_value):
    dict = nx.get_edge_attributes(G, attrb_name)  # check if
    if len(dict) > 0:
        return nx.Graph([(u, v, d) for u, v, d in G.edges(data=True) if d[attrb_name] != attrb_value])
    else:
        print "ERROR: Attribute not found"
        exit(0)
