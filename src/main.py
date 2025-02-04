import osmnx as ox


if __name__ == "__main__":
    G = ox.graph_from_place(
        "Capital Region of Denmark", network_type="drive_service", simplify=True
    )
    fig, ax = ox.plot.plot_graph(G, node_size=0, edge_linewidth=0.5, figsize=(10, 10))
