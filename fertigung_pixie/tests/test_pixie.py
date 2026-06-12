"""
pytest-Tests für den PIXIE-Algorithmus.
Ausführen: pytest tests/ -v
"""
import pytest
import networkx as nx
from pixie import pixie


# ---------------------------------------------------------------------------
# Hilfsfunktion: einfacher Graph mit zwei Alternativen ab "start"
# ---------------------------------------------------------------------------
def two_choice_graph(weight_uv=10, weight_ofen=10):
    """
    start → UV-Aushärtung  (günstig, wenig CO₂, wenig Energie)
    start → Ofen           (teuer,   viel CO₂,  viel Energie)
    Gleiche Frequenz (weight), damit nur die Zielkriterien entscheiden.
    """
    G = nx.DiGraph()
    G.add_edge("start", "UV-Aushärtung", weight=weight_uv,
               co2=10.0, cost=160.0, energy=20.0)
    G.add_edge("start", "Ofen",          weight=weight_ofen,
               co2=60.0, cost=200.0, energy=120.0)
    return G


# ---------------------------------------------------------------------------
# Grundlegende Funktionstests
# ---------------------------------------------------------------------------
class TestPixieBasic:
    def test_returns_dict(self):
        G = two_choice_graph()
        result = pixie(G, "start", 0.25, 0.25, 0.25, 0.25)
        assert isinstance(result, dict)

    def test_only_successors_visited(self):
        G = two_choice_graph()
        result = pixie(G, "start", 0.25, 0.25, 0.25, 0.25)
        assert all(k in ("UV-Aushärtung", "Ofen") for k in result)

    def test_sorted_descending(self):
        G = two_choice_graph()
        result = pixie(G, "start", 0.25, 0.25, 0.25, 0.25)
        counts = list(result.values())
        assert counts == sorted(counts, reverse=True)

    def test_no_successor_returns_empty(self):
        G = nx.DiGraph()
        G.add_node("alone")
        result = pixie(G, "alone", 0.25, 0.25, 0.25, 0.25, n_steps=100)
        assert result == {}


# ---------------------------------------------------------------------------
# Szenario-Tests: Empfehlung hängt vom Gewicht ab
# ---------------------------------------------------------------------------
class TestPixieSzenarien:
    def test_nachhaltigkeit_bevorzugt_uv(self):
        """Hohe CO₂-Gewichtung → UV-Aushärtung (weniger CO₂) soll gewinnen."""
        G = two_choice_graph()
        result = pixie(G, "start", alpha=0.1, beta=0.1, gamma=0.6, delta=0.2,
                       n_steps=3000)
        top = list(result.keys())[0]
        assert top == "UV-Aushärtung", (
            f"Nachhaltigkeitsszenario: erwartet UV-Aushärtung, bekam {top}"
        )

    def test_kostenszenario_bevorzugt_uv(self):
        """Hohe Kostengewichtung → UV-Aushärtung (160 € < 200 €) soll gewinnen."""
        G = two_choice_graph()
        result = pixie(G, "start", alpha=0.1, beta=0.7, gamma=0.1, delta=0.1,
                       n_steps=3000)
        top = list(result.keys())[0]
        assert top == "UV-Aushärtung", (
            f"Kostenszenario: erwartet UV-Aushärtung, bekam {top}"
        )

    def test_frequenz_bevorzugt_haeufigeren_pfad(self):
        """Hohe Frequenzgewichtung → häufigerer Pfad (Ofen, weight=90) soll gewinnen."""
        G = two_choice_graph(weight_uv=10, weight_ofen=90)
        result = pixie(G, "start", alpha=0.9, beta=0.03, gamma=0.04, delta=0.03,
                       n_steps=3000)
        top = list(result.keys())[0]
        assert top == "Ofen", (
            f"Frequenzszenario: erwartet Ofen (häufiger), bekam {top}"
        )

    def test_alle_gleich_beide_im_ergebnis(self):
        """Ausgeglichene Gewichte und gleiche Frequenz → beide Knoten erscheinen."""
        G = two_choice_graph()
        result = pixie(G, "start", 0.25, 0.25, 0.25, 0.25, n_steps=5000)
        assert len(result) == 2, "Beide Nachfolger sollen besucht werden"


# ---------------------------------------------------------------------------
# Integrations-Test: läuft auf dem echten Produktionsgraphen
# ---------------------------------------------------------------------------
class TestPixieIntegration:
    @pytest.fixture(scope="class")
    def graph(self):
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        from eventlog import generate_eventlog
        from graph import build_graph
        df = generate_eventlog(n_orders=200)
        return build_graph(df)

    def test_nachhaltigkeit_empfiehlt_uv(self, graph):
        result = pixie(graph, "Qualitätskontrolle",
                       alpha=0.1, beta=0.1, gamma=0.6, delta=0.2,
                       n_steps=3000)
        top = list(result.keys())[0]
        assert top == "Lackieren UV-Aushärtung", (
            f"Nachhaltigkeitsszenario (Produktionsgraph): bekam {top}"
        )

    def test_kostenszenario_empfiehlt_uv(self, graph):
        result = pixie(graph, "Qualitätskontrolle",
                       alpha=0.1, beta=0.7, gamma=0.1, delta=0.1,
                       n_steps=3000)
        top = list(result.keys())[0]
        assert top == "Lackieren UV-Aushärtung", (
            f"Kostenszenario (Produktionsgraph): bekam {top}"
        )

    def test_result_not_empty(self, graph):
        result = pixie(graph, "Rohmaterial prüfen",
                       0.25, 0.25, 0.25, 0.25, n_steps=500)
        assert len(result) > 0
