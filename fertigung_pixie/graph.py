import networkx as nx
import numpy as np
from collections import defaultdict

def build_graph(df):
    transitions = defaultdict(lambda: {
        "count": 0, "co2": [], "cost": [], "energy": []
    })

    for case_id, group in df.groupby("case_id"):
        group = group.sort_values("timestamp").reset_index(drop=True)
        for i in range(len(group) - 1):
            src = group.loc[i,   "activity"]
            tgt = group.loc[i+1, "activity"]
            transitions[(src, tgt)]["count"]  += 1
            transitions[(src, tgt)]["co2"].append(group.loc[i+1, "co2"])
            transitions[(src, tgt)]["cost"].append(group.loc[i+1, "cost"])
            transitions[(src, tgt)]["energy"].append(group.loc[i+1, "energy"])

    G = nx.DiGraph()
    for (src, tgt), data in transitions.items():
        G.add_edge(src, tgt,
            weight = data["count"],
            co2    = np.mean(data["co2"]),
            cost   = np.mean(data["cost"]),
            energy = np.mean(data["energy"]),
        )

    print(f"Graph aufgebaut: {G.number_of_nodes()} Knoten, {G.number_of_edges()} Kanten")
    return G
