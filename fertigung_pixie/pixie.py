import random
from collections import defaultdict

def normalize(values: dict) -> dict:
    if not values:
        return {}
    min_v = min(values.values())
    max_v = max(values.values())
    if max_v == min_v:
        return {k: 1.0 for k in values}
    return {k: (v - min_v) / (max_v - min_v) for k, v in values.items()}

def pixie(G, start_node, alpha, beta, gamma, delta,
          n_steps=1000, restart_prob=0.5):
    """
    alpha : Gewicht für historische Häufigkeit (höher = bevorzuge häufige Pfade)
    beta  : Gewicht für niedrige Kosten
    gamma : Gewicht für niedrigen CO₂-Ausstoß
    delta : Gewicht für niedrigen Energieverbrauch
    """
    edges = list(G.edges(data=True))
    co2_norm    = normalize({(u,v): d["co2"]    for u,v,d in edges})
    cost_norm   = normalize({(u,v): d["cost"]   for u,v,d in edges})
    energy_norm = normalize({(u,v): d["energy"] for u,v,d in edges})

    visit_counts = defaultdict(int)
    current = start_node

    for _ in range(n_steps):
        if random.random() < restart_prob:
            current = start_node
            continue

        neighbors = list(G.successors(current))
        if not neighbors:
            current = start_node
            continue

        # Frequenz lokal unter den Nachbarn normalisieren
        freq_local = normalize({nb: G[current][nb]["weight"] for nb in neighbors})

        weights = []
        for nb in neighbors:
            score = (alpha * freq_local[nb]
                   + beta  * (1 - cost_norm.get((current, nb),   0))
                   + gamma * (1 - co2_norm.get((current, nb),    0))
                   + delta * (1 - energy_norm.get((current, nb), 0)))
            weights.append(max(0.001, score))

        total = sum(weights)
        probs   = [w / total for w in weights]
        current = random.choices(neighbors, weights=probs, k=1)[0]
        visit_counts[current] += 1

    return dict(sorted(visit_counts.items(), key=lambda x: x[1], reverse=True))
