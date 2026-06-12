import os
import matplotlib.pyplot as plt
from eventlog import generate_eventlog
from graph    import build_graph
from pixie    import pixie

# --- Setup ---
os.makedirs("data", exist_ok=True)

# --- 1. Eventlog generieren ---
df = generate_eventlog(n_orders=200)
print(df.head(6))

# --- 2. Graph aufbauen ---
G = build_graph(df)

# --- 3. Szenarien testen ---
start = "Qualitätskontrolle"
szenarien = {
    "Produktionsleiter (schnell)":  (0.6, 0.2, 0.1, 0.1),
    "Controller (kostenoptimiert)": (0.2, 0.6, 0.1, 0.1),
    "Nachhaltigkeitsbeauftragter":  (0.1, 0.1, 0.6, 0.2),
}

print(f"\nStartknoten: {start}\n" + "-"*50)
for name, (a, b, g, d) in szenarien.items():
    result  = pixie(G, start, a, b, g, d)
    top     = list(result.keys())[0]
    besuche = list(result.values())[0]
    co2     = G[start][top]["co2"]
    cost    = G[start][top]["cost"]
    energy  = G[start][top]["energy"]
    print(f"Szenario:    {name}")
    print(f"Empfehlung:  {top}  ({besuche}/1000 Besuche)")
    print(f"CO2:         {co2:.1f} kg  |  Kosten: {cost:.0f} €  |  Energie: {energy:.0f} kWh")
    print("-"*50)

# --- 4. Trade-off visualisieren ---
gammas   = [i/10 for i in range(0, 11)]
co2_res  = []
cost_res = []

for g in gammas:
    rest   = (1 - g) / 3
    result = pixie(G, start, rest, rest, g, rest)
    top    = list(result.keys())[0]
    co2_res.append(G[start][top]["co2"])
    cost_res.append(G[start][top]["cost"])

fig, ax1 = plt.subplots(figsize=(8, 4))
ax2 = ax1.twinx()
ax1.plot(gammas, co2_res,  "g-o", label="CO₂ (kg)")
ax2.plot(gammas, cost_res, "b-s", label="Kosten (€)")
ax1.set_xlabel("CO₂-Gewicht γ")
ax1.set_ylabel("CO₂ der Empfehlung (kg)", color="g")
ax2.set_ylabel("Kosten der Empfehlung (€)",  color="b")
ax1.set_title("Trade-off: CO₂-Gewicht γ vs. Emissionen & Kosten")
fig.legend(loc="upper right")
plt.tight_layout()
plt.savefig("data/tradeoff.png", dpi=150)
plt.show()
print("\nPlot gespeichert: data/tradeoff.png")
