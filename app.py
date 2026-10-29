"""Streamlit prototype views for the synthetic UOW Dubai study area."""

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
import streamlit as st


st.set_page_config(page_title="Urban Irrigation Twin", page_icon="💧", layout="wide")

NAVY = "#17354a"
BLUE = "#28759c"
PIPE = "#54798e"
GREEN = "#24a47f"
GOLD = "#e2a13a"


def draw_study_area() -> plt.Figure:
    """Draw an offline illustrative study radius and a zoomed network inset."""
    fig, (overview, inset) = plt.subplots(
        1, 2, figsize=(12, 6), gridspec_kw={"width_ratios": [1.25, 1]}
    )
    fig.patch.set_facecolor("#f7fafb")
    overview.set_facecolor("#eaf0e9")

    # Abstract blocks are decorative only and do not depict real streets or land use.
    blocks = [
        (-2.5, 1.8, 1.2, 0.45), (-0.9, 2.2, 1.5, 0.35), (1.0, 1.8, 1.2, 0.55),
        (-2.3, 0.7, 0.8, 0.6), (1.5, 0.5, 1.0, 0.7), (-1.8, -1.7, 1.2, 0.6),
        (0.8, -2.2, 1.4, 0.55), (-0.2, -2.6, 0.65, 0.45),
    ]
    for x, y, w, h in blocks:
        overview.add_patch(
            Rectangle((x, y), w, h, facecolor="#d8dfd3", edgecolor="#c5d0c6", lw=0.7)
        )
    overview.add_patch(Circle((0, 0), 3, facecolor="#6eb6ca", alpha=0.12, edgecolor=BLUE, lw=2.2))
    overview.scatter([0], [0], s=110, marker="s", color=NAVY, zorder=5, label="UOW Dubai reference")
    overview.annotate("UOW Dubai\n(reference point)", (0, 0), xytext=(0.25, 0.32), fontsize=9, color=NAVY)
    overview.set_title("3 km study-area context", color=NAVY, fontsize=13, weight="bold")
    overview.text(-2.85, -3.35, "Circle shows study radius; background is illustrative, not satellite imagery.", fontsize=8, color="#506775")
    overview.set_xlim(-3.55, 3.55)
    overview.set_ylim(-3.55, 3.55)
    overview.set_aspect("equal")
    overview.set_xlabel("Illustrative distance from reference point (km)", fontsize=8)
    overview.set_ylabel("Illustrative distance (km)", fontsize=8)
    overview.grid(alpha=0.15)

    draw_network(inset, show_measurements=False)
    inset.set_title("Hypothetical network (zoomed)", color=NAVY, fontsize=13, weight="bold")
    fig.suptitle("Offline study-area illustration", fontsize=16, color=NAVY, weight="bold")
    fig.text(
        0.5, 0.015,
        "All zones, connections and background shapes are illustrative; no actual UOW or city pipes are shown.",
        ha="center", fontsize=9, color="#8a4b13",
    )
    fig.tight_layout(rect=[0, 0.045, 1, 0.94])
    return fig


def draw_network(ax: plt.Axes, show_measurements: bool = True, fault_zone: str | None = None) -> None:
    """Draw the abstract source-manifold-three-zone pipe topology."""
    ax.set_facecolor("#fbfdfe")
    nodes = {
        "Source": (0.0, 0.0),
        "Manifold": (2.0, 0.0),
        "Zone A": (4.2, 1.45),
        "Zone B": (4.2, 0.0),
        "Zone C": (4.2, -1.45),
    }
    links = [("Source", "Manifold"), ("Manifold", "Zone A"), ("Manifold", "Zone B"), ("Manifold", "Zone C")]
    for start, end in links:
        x1, y1 = nodes[start]
        x2, y2 = nodes[end]
        ax.add_patch(FancyArrowPatch((x1 + 0.2, y1), (x2 - 0.2, y2), arrowstyle="-", lw=3, color=PIPE, zorder=1))
    for name, (x, y) in nodes.items():
        if name == "Source":
            color, marker = GOLD, "s"
        elif name == "Manifold":
            color, marker = NAVY, "o"
        else:
            is_fault = fault_zone == name
            color, marker = ("#c7473a" if is_fault else GREEN), "o"
        ax.scatter([x], [y], s=190 if name != "Source" else 150, color=color, marker=marker, edgecolor="white", linewidth=1.4, zorder=3)
        ax.annotate(name, (x, y), xytext=(0, 13 if name != "Zone C" else -22), textcoords="offset points", ha="center", fontsize=9, color=NAVY, weight="bold")

    if show_measurements:
        readings = {"Zone A": "12.0 L/min\n434.57 kPa", "Zone B": "13.2 L/min\n433.33 kPa", "Zone C": "10.8 L/min\n435.71 kPa"}
        for name in ("Zone A", "Zone B", "Zone C"):
            x, y = nodes[name]
            ax.text(x + 0.34, y, readings[name], va="center", fontsize=8, color="#314d5d")
    ax.text(0.0, -0.58, "Synthetic source", fontsize=8, ha="center", color="#80530e")
    ax.text(2.0, -0.58, "Distribution manifold", fontsize=8, ha="center", color="#506775")
    ax.set_xlim(-0.65, 6.0 if show_measurements else 5.0)
    ax.set_ylim(-2.05, 2.05)
    ax.set_aspect("equal")
    ax.axis("off")


st.title("Schedule-Aware Urban Irrigation Prototype")
st.caption("Simulation-only demonstration • UOW Dubai is a geographic reference, not the source of real network data")
st.warning("This screen is an illustrative diagram, not satellite imagery or a map of actual irrigation infrastructure.")

view = st.radio("Choose a view", ["Study area", "Pipeline view"], horizontal=True)

if view == "Study area":
    st.pyplot(draw_study_area(), use_container_width=True)
    st.caption("The circle is a 3 km context radius. The background shapes and network positions are illustrative and are not to scale.")
else:
    selected = st.selectbox("Highlight a hypothetical fault location", ["None", "Zone A", "Zone B", "Zone C"])
    fig, ax = plt.subplots(figsize=(11, 4.8))
    fig.patch.set_facecolor("#f7fafb")
    draw_network(ax, show_measurements=True, fault_zone=None if selected == "None" else selected)
    ax.set_title("Simulated pipeline topology and normal baseline readings", color=NAVY, fontsize=14, weight="bold", pad=16)
    st.pyplot(fig, use_container_width=True)
    st.caption("Red highlight is a visual example only. Pipe connections and measurements are simulated; no classifier is connected yet.")
