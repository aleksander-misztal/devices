"""Generates graph.png showing the LangGraph pipeline."""
from graph import graph

output = "graph.png"
png_data = graph.get_graph().draw_mermaid_png()
with open(output, "wb") as f:
    f.write(png_data)

print(f"Saved {output}")
