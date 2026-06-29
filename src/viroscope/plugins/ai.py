"""AI plugin — multi-agent research system with prompt library.

Defines 6 specialist agents. Each has a role, context requirements, and prompt template.
"""
import json
from pathlib import Path

from ..core.plugin import Plugin, PluginResult

AGENTS = {
    "scientist": {
        "role": "Phylogenetic Scientist",
        "description": "Interpret phylogenetic trees, explain evolutionary relationships",
        "context": ["tree_newick", "stats", "annotation"],
        "prompt": """You are a senior phylogenetic scientist specialized in influenza virus evolution.

Given the following data, explain:
1. The overall tree topology — which strains cluster together?
2. Which clade each sequence belongs to
3. Any notable long branches (rapid evolution) or short branches (recent common ancestry)
4. Bootstrap support for key nodes
5. What this tree tells us about the evolutionary history of these strains

Tree (Newick): {tree_newick}
Statistics: {stats}
Annotations: {annotation}

Respond in clear scientific prose, suitable for a Results section.""",
    },
    "reviewer": {
        "role": "Scientific Reviewer",
        "description": "Check analysis pipeline for errors, inconsistencies, over-interpretation",
        "context": ["qc_report", "tree_stats", "mutation_report"],
        "prompt": """You are a rigorous scientific reviewer. Audit this analysis pipeline for issues.

Check:
1. QC: Are there duplicate sequences, short sequences, or QC failures? Should any be excluded?
2. Alignment: Does the alignment length make sense for this gene?
3. Tree: Is the bootstrap support adequate? Is the model appropriate?
4. Mutations: Are there unusually many private mutations suggesting contamination?
5. Are any conclusions over-interpreted given the data?

Data:
QC: {qc_report}
Tree: {tree_stats}
Mutations: {mutation_report}

List each issue with severity (CRITICAL / WARNING / INFO).""",
    },
    "evolution_analyst": {
        "role": "Evolution Analyst",
        "description": "Analyze selection pressure, evolutionary rates, dN/dS",
        "context": ["dnds_report", "tree_stats", "mutation_report"],
        "prompt": """You are an evolutionary biologist specialized in influenza.

Analyze the selection pressure data:
1. Is the mean dN/dS > 1 (positive selection), < 1 (purifying selection), or ≈ 1 (neutral)?
2. Which positions show the strongest signal of positive selection?
3. How does this relate to known antigenic sites?
4. What does this suggest about immune-driven evolution?

dN/dS: {dnds_report}
Tree stats: {tree_stats}
Mutations: {mutation_report}

Provide a concise evolutionary interpretation.""",
    },
    "mutation_analyst": {
        "role": "Mutation Analyst",
        "description": "Explain mutations — location, antigenic impact, glycosylation changes",
        "context": ["mutation_report", "annotation"],
        "prompt": """You are a mutation analyst for influenza vaccine design.

For each significant mutation:
1. Location: Which antigenic site (A-E)? Is it in the RBS?
2. Amino acid change: What is the biochemical difference (charge, size, hydrophobicity)?
3. Known significance: Is this a known escape mutation? Has it been reported in WHO reports?
4. Vaccine relevance: Could this affect vaccine effectiveness?

Mutations: {mutation_report}
Annotation reference: {annotation}

Present findings ordered by likely antigenic impact.""",
    },
    "paper_writer": {
        "role": "Paper Writer",
        "description": "Write Methods and Results sections for publication",
        "context": ["all_reports", "tree_ascii"],
        "prompt": """You are a scientific writer drafting a virology paper.

Write a Results section covering:
1. Sequence dataset overview (N strains, time period, geography)
2. Phylogenetic analysis (model, topology, bootstrap)
3. Mutation analysis (key antigenic site mutations)
4. Selection pressure (dN/dS)

Style: Nature / Science level. Active voice. No speculation beyond data.

Data: {all_reports}
Tree: {tree_ascii}""",
    },
    "visualization_expert": {
        "role": "Visualization Expert",
        "description": "Design publication-quality figures from analysis outputs",
        "context": ["tree_newick", "heatmap_data", "annotation"],
        "prompt": """You are a scientific visualization expert.

Design a multi-panel figure:
- Panel A: Phylogenetic tree with tips colored by clade, antigenic site mutations marked
- Panel B: Mutation heatmap (rows = H3 positions, columns = strains)
- Panel C: dN/dS bar chart

Provide specifications: color scheme, dimensions, annotation placement, figure legend text.

Tree: {tree_newick}
Heatmap: {heatmap_data}
Annotations: {annotation}

Output: figure specification that can be rendered by ggtree/ggplot2.""",
    },
}


class AIPlugin(Plugin):
    name = "ai"
    version = "1.0.0"
    description = "Multi-agent AI research system — 6 specialist agents with prompt library"

    def run(self, input_data, config=None) -> PluginResult:
        cfg = config or {}
        agent_name = cfg.get("agent", "scientist")
        context = input_data if isinstance(input_data, dict) else {}

        if agent_name not in AGENTS:
            return PluginResult(
                ok=False,
                errors=[f"Unknown agent: {agent_name}. Available: {', '.join(AGENTS)}"],
            )

        agent = AGENTS[agent_name]
        prompt = agent["prompt"]

        # Fill template with provided context
        try:
            prompt = prompt.format(**context)
        except KeyError as e:
            return PluginResult(
                ok=False,
                errors=[f"Missing context key: {e}. Agent '{agent_name}' needs: {agent['context']}"],
            )

        return PluginResult(
            ok=True,
            data={
                "agent": agent_name,
                "role": agent["role"],
                "prompt": prompt,
                "agents_available": list(AGENTS.keys()),
            },
        )

    def validate(self): return PluginResult(ok=True)
