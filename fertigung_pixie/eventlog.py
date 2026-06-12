import pandas as pd
import numpy as np
import random

def generate_eventlog(n_orders=200, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    activities = {
        "Rohmaterial prüfen":      {"cost": 20,  "co2": 0.5,  "energy": 2,   "duration": 0.5},
        "Fräsen Maschine A":       {"cost": 150, "co2": 40.0, "energy": 80,  "duration": 2.0},
        "Fräsen Maschine B":       {"cost": 180, "co2": 20.0, "energy": 40,  "duration": 1.5},
        "Qualitätskontrolle":      {"cost": 30,  "co2": 1.0,  "energy": 3,   "duration": 0.5},
        "Lackieren Ofen":          {"cost": 200, "co2": 60.0, "energy": 120, "duration": 2.0},
        "Lackieren UV-Aushärtung": {"cost": 160, "co2": 10.0, "energy": 20,  "duration": 1.5},
        "Verpacken Standard":      {"cost": 40,  "co2": 5.0,  "energy": 8,   "duration": 0.5},
        "Verpacken Recycling":     {"cost": 50,  "co2": 1.0,  "energy": 5,   "duration": 0.5},
        "Versand Express":         {"cost": 250, "co2": 90.0, "energy": 0,   "duration": 0.5},
        "Versand Standard":        {"cost": 100, "co2": 30.0, "energy": 0,   "duration": 1.0},
    }

    paths = [
        ["Rohmaterial prüfen", "Fräsen Maschine A", "Qualitätskontrolle",
         "Lackieren Ofen", "Verpacken Standard", "Versand Express"],
        ["Rohmaterial prüfen", "Fräsen Maschine B", "Qualitätskontrolle",
         "Lackieren Ofen", "Verpacken Recycling", "Versand Standard"],
        ["Rohmaterial prüfen", "Fräsen Maschine B", "Qualitätskontrolle",
         "Lackieren UV-Aushärtung", "Verpacken Recycling", "Versand Standard"],
    ]

    rows = []
    for order_id in range(1, n_orders + 1):
        path = random.choices(paths, weights=[0.40, 0.35, 0.25])[0]
        t = pd.Timestamp("2024-01-01 06:00") + pd.Timedelta(hours=order_id * 0.1)
        for act in path:
            rows.append({
                "case_id":   f"O{order_id}",
                "activity":  act,
                "timestamp": t,
                "cost":      activities[act]["cost"]   + np.random.normal(0, 5),
                "co2":       max(0, activities[act]["co2"]    + np.random.normal(0, 1)),
                "energy":    max(0, activities[act]["energy"] + np.random.normal(0, 2)),
            })
            t += pd.Timedelta(hours=activities[act]["duration"])

    df = pd.DataFrame(rows)
    df.to_csv("data/eventlog.csv", index=False)
    print(f"Eventlog erstellt: {len(df)} Einträge, {n_orders} Aufträge")
    return df
