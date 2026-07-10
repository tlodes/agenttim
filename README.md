# AgentTim

Evaluations-Framework zum Vergleich von **Single-Agent-** und **Multi-Agent-Architekturen**
bei der Werkzeugnutzung (Tool Calling / Function Calling) auf den Benchmarks
**BFCL Multi-Turn** und **MCPAgentBench**.

Das Projekt untersucht, wie sich unterschiedliche Agenten-Topologien – ein einzelner
ReAct-Agent gegenüber Orchestrator-, Router- und Swarm-Architekturen – hinsichtlich
Werkzeug-Korrektheit, Zustands-Genauigkeit, Token-Kosten und Latenz verhalten.

## Überblick

Agenten werden über [LangGraph](https://github.com/langchain-ai/langgraph) /
[LangChain](https://github.com/langchain-ai/langchain) gebaut, greifen über
[MCP](https://modelcontextprotocol.io/) (Model Context Protocol) auf Werkzeuge zu
und werden mit [DeepEval](https://github.com/confident-ai/deepeval) sowie eigenen
Metriken evaluiert. Als LLM-Backend dient Azure OpenAI (bzw. OpenRouter).

## Architekturen

| Typ | Beschreibung |
|-----|--------------|
| **Single-Agent** | Ein einzelner ReAct-Agent mit Zugriff auf alle Werkzeuge (`singleagent/`) |
| **Orchestrator** | Zentraler Orchestrator delegiert an domänenspezifische Sub-Agenten (`multiagents/*Orchestrator`) |
| **Router** | Router leitet Anfragen an den passenden Spezial-Agenten weiter (`multiagents/*Router`) |
| **Swarm** | Agenten übergeben (Handoff) Aufgaben dezentral untereinander (`multiagents/*Swarm`) |

Jede Architektur existiert in einer Variante für **BFCL** und für **MCPAgentBench**.

## Projektstruktur

```
agenttim/
├── agents/            # Basisklassen: BaseEvalAgent, StatefulEvalAgent, StatelessSubAgent
├── singleagent/       # Single-Agent-Implementierungen (bfcl, mcpagentbench)
├── multiagents/       # Orchestrator-, Router- und Swarm-Architekturen je Benchmark
├── mcpservers/        # MCP-Server, die Benchmark-Werkzeuge bereitstellen (mcpbfcl, mcpagentbench)
├── bfcl/              # BFCL-Domänen-Konfiguration, State-Manager, Tool-Factory + Funktionsquellen
├── chromadb/          # Vektor-Store-Setup (z. B. juristische Beispiel-Daten)
├── config/            # Settings (pydantic-settings) und Secret-Management
├── services/          # LLM-Service, DeepEval-Model-Adapter
└── evaluation/        # Evaluations-Harness, Metriken, Skripte, Dashboard und Ergebnisse
    ├── eval_utils/        # Metriken (Tool-Correctness, State-Match, Effizienz, Tokens …)
    ├── evaluationscripts/ # Runner: evaluate_bfcl_multiturn.py, evaluate_mcpagentbench.py, run_all.py
    ├── dashboard/         # Streamlit-Dashboard zur Ergebnisauswertung
    └── plots/             # Generierte Abbildungen und LaTeX-Tabellen
```

## Voraussetzungen

- Python **3.13**
- [Poetry](https://python-poetry.org/) für das Dependency-Management
- Zugang zu Azure OpenAI oder OpenRouter

## Installation

```bash
cd evaluation
poetry install
```

## Konfiguration

Die Einstellungen werden über Umgebungsvariablen bzw. eine `.env`-Datei geladen
(siehe `config/settings.py`):

```env
SERVICE_NAME=AgentTim
AZURE_OPENAI_API_VERSION=2025-03-01-preview
AZURE_OPENAI_MODEL=gpt-5.4-mini
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_API_KEY=...
MCP_BENCH_BASE_URL=http://localhost:9000
MCP_BFCL_BASE_URL=http://localhost:9100
```

## Nutzung

MCP-Server starten (stellen die Benchmark-Werkzeuge bereit), dann die Evaluation ausführen:

```bash
# Alle Benchmarks
python evaluationscripts/run_all.py --benchmark all

# Nur MCPAgentBench, Multi-Agent
python evaluationscripts/run_all.py --benchmark mcpagentbench --agent multi

# BFCL mit ausgewählten Modi
python evaluationscripts/run_all.py --jwt-token "eyJ..." --benchmark bfcl --modes st-1t st-mt
```

Auswertungs-Dashboard:

```bash
streamlit run dashboard/streamlit_eval.py
```

## Evaluations-Dimensionen

- **Modi**: `st-1t` (single-turn), `st-mt` / `mt-mt` (multi-turn)
- **Metriken**: Tool-Correctness, Argument-Correctness, State-Match / Final-State,
  Klärungsfragen, Effizienz, Token-Verbrauch und Latenz

## Lizenz

Noch nicht festgelegt.
