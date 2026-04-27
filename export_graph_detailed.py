"""Generates graph_detailed.png — annotated pipeline diagram."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(14, 20))
ax.set_xlim(0, 14)
ax.set_ylim(0, 20)
ax.axis("off")
fig.patch.set_facecolor("#f8f9fa")

# ── colours ──────────────────────────────────────────────────────────────────
C_NODE   = "#dce8ff"   # node background
C_BORDER = "#4a6fa5"   # node border
C_SUB    = "#f0f4ff"   # sub-item background
C_LLM    = "#ffe8d6"   # LLM call highlight
C_COND   = "#e8f5e9"   # conditional / routing
C_START  = "#d0d0f8"   # start/end


def box(ax, x, y, w, h, label, sublabels=(), color=C_NODE, fontsize=10):
    """Draw a rounded box with an optional title and sub-labels."""
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.08",
                          linewidth=1.5,
                          edgecolor=C_BORDER,
                          facecolor=color)
    ax.add_patch(rect)
    if sublabels:
        ax.text(x + w / 2, y + h - 0.22, label,
                ha="center", va="top", fontsize=fontsize,
                fontweight="bold", color="#1a2a4a")
        step = (h - 0.38) / max(len(sublabels), 1)
        for i, sub in enumerate(sublabels):
            ax.text(x + 0.18, y + h - 0.42 - i * step, sub,
                    ha="left", va="top", fontsize=8.5, color="#2c3e50",
                    fontfamily="monospace")
    else:
        ax.text(x + w / 2, y + h / 2, label,
                ha="center", va="center", fontsize=fontsize,
                fontweight="bold", color="#1a2a4a")


def arrow(ax, x1, y1, x2, y2, label="", color="#4a6fa5"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.12, my, label, fontsize=8, color=color, va="center")


def dashed_arrow(ax, x1, y1, x2, y2, label="", color="#4a6fa5"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5,
                                linestyle="dashed"))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.12, my, label, fontsize=8, color=color, va="center",
                style="italic")


# ── layout constants ──────────────────────────────────────────────────────────
W = 5.5   # node width
WS = 13   # canvas width reference
CX = 7    # center x

# ── __start__ ────────────────────────────────────────────────────────────────
box(ax, CX - 1.2, 19.2, 2.4, 0.55, "__start__", color=C_START, fontsize=9)

# ── extract ──────────────────────────────────────────────────────────────────
EX = CX - W / 2; EY = 17.5; EH = 1.5
box(ax, EX, EY, W, EH, "extract", color=C_NODE, sublabels=[
    "LLM (gpt-4o-mini)",
    "→ devices[]: {brand, model, type}",
    "   brand tylko gdy słowo padło dosłownie",
    "   model = pełna nazwa z pytania",
])

# ── extract_specs ─────────────────────────────────────────────────────────────
SX = 0.5; SY = 14.8; SH = 2.4
box(ax, SX, SY, W, SH, "extract_specs", color=C_LLM, sublabels=[
    "LLM (gpt-4o-mini)",
    "→ category, brand, price_max_pln",
    "   ram_gb (eq) / ram_min_gb (gte)",
    "   storage_gb (eq) / storage_min_gb (gte)",
    "   screen_min_inch, screen_type",
    "   refresh_rate_min_hz, connectivity_5g",
    "   sort_by, sort_order, limit",
])

# ── name_search ───────────────────────────────────────────────────────────────
NX = 8.0; NY = 14.8; NH = 2.4
box(ax, NX, NY, W, NH, "name_search", color=C_NODE, sublabels=[
    "pool: category filter (jeśli podana)",
    "per extracted device:",
    "  1. exact match (normalize)",
    "  2. token overlap ≥60% + liczby OK",
    "  3. fuzzy token_sort_ratio ≥82",
    "→ candidates[]: {clipper_id, name, matched_by}",
])

# ── filter_search ─────────────────────────────────────────────────────────────
FSX = 0.5; FSY = 11.6; FSH = 2.9
box(ax, FSX, FSY, W, FSH, "filter_search", color=C_NODE, sublabels=[
    "guard: brand OR spec filters",
    "       OR (category + brand/specs/sort)",
    "pre-filter: category → brand",
    "spec filters (eq / gte / lte):",
    "  battery_mah, camera_mpx, ram_gb",
    "  storage_gb, screen_inch, screen_type",
    "  refresh_rate_hz, price_pln, 5G, GPS",
    "sort: sort_by + sort_order (nulls last)",
    "→ filter_devices[]: clipper_id[]",
])

# ── aggregate ─────────────────────────────────────────────────────────────────
AGX = CX - W / 2; AGY = 9.0; AGH = 2.3
box(ax, AGX, AGY, W, AGH, "aggregate", color=C_LLM, sublabels=[
    "union: name_ids + filter_ids (order preserved)",
    "if name_ids ≤ MAX_CANDIDATES & specific model:",
    "  LLM picker → exact generation match",
    "  filter_ids dołączone tylko z innej kategorii",
    "re-sort wg sort_by (nulls last)",
    "limit tylko gdy sort_by present",
    "→ devices[]: clipper_id[]",
])

# ── route ─────────────────────────────────────────────────────────────────────
RY = 8.1
ax.text(CX, RY - 0.1, "route: len(devices) ≤ 10?",
        ha="center", va="top", fontsize=8.5, color="#555",
        style="italic")

# ── responder_normal ──────────────────────────────────────────────────────────
RNX = 0.5; RNY = 5.8; RNH = 1.9
box(ax, RNX, RNY, W, RNH, "responder_normal  (≤10)", color=C_COND, sublabels=[
    "LLM (gpt-4o-mini)",
    "kontekst: pytanie + pełne teksty urządzeń",
    "→ swobodna odpowiedź tekstowa",
    "mode = 'normal'",
])

# ── responder_heavy ───────────────────────────────────────────────────────────
RHX = 8.0; RHY = 5.8; RHH = 1.9
box(ax, RHX, RHY, W, RHH, "responder_heavy  (>10)", color=C_COND, sublabels=[
    "LLM (gpt-4o-mini)",
    "kontekst: pytanie + filtry + total_found",
    "→ krótkie intro (bez listy urządzeń)",
    "mode = 'heavy' + card_devices[]",
])

# ── __end__ ───────────────────────────────────────────────────────────────────
box(ax, CX - 1.2, 5.0, 2.4, 0.55, "__end__", color=C_START, fontsize=9)

# ── arrows ────────────────────────────────────────────────────────────────────
# start → extract
arrow(ax, CX, 19.2, CX, 17.5 + EH)

# extract → extract_specs (diagonal left)
arrow(ax, EX, EY + EH / 2, SX + W, SY + SH / 2)
# extract → name_search (diagonal right)
arrow(ax, EX + W, EY + EH / 2, NX, NY + NH / 2)

# extract_specs → filter_search
arrow(ax, SX + W / 2, SY, SX + W / 2, FSY + FSH)

# name_search → aggregate (diagonal left)
arrow(ax, NX, NY + NH / 2, AGX + W, AGY + AGH / 2)
# filter_search → aggregate (diagonal right)
arrow(ax, FSX + W, FSY + FSH / 2, AGX, AGY + AGH / 2)

# aggregate → responder_normal (dashed, left)
dashed_arrow(ax, AGX, AGY + AGH / 2, RNX + W, RNY + RNH / 2, label="normal")
# aggregate → responder_heavy (dashed, right)
dashed_arrow(ax, AGX + W, AGY + AGH / 2, RHX, RHY + RNH / 2, label="heavy")

# responder_normal → end
arrow(ax, RNX + W / 2, RNY, CX - 0.6, 5.55)
# responder_heavy → end
arrow(ax, RHX + W / 2, RHY, CX + 0.6, 5.55)

# ── legend ────────────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(facecolor=C_NODE,  edgecolor=C_BORDER, label="retrieval / logic"),
    mpatches.Patch(facecolor=C_LLM,   edgecolor=C_BORDER, label="LLM call"),
    mpatches.Patch(facecolor=C_COND,  edgecolor=C_BORDER, label="responder (conditional)"),
    mpatches.Patch(facecolor=C_START, edgecolor=C_BORDER, label="start / end"),
]
ax.legend(handles=legend_items, loc="lower right", fontsize=8,
          framealpha=0.9, edgecolor=C_BORDER)

ax.set_title("Device RAG Pipeline — szczegółowy graf", fontsize=13,
             fontweight="bold", color="#1a2a4a", pad=8)

plt.tight_layout()
plt.savefig("graph_detailed.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("Saved graph_detailed.png")
