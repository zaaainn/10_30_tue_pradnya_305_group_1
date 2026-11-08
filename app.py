"""Streamlit prototype views for the synthetic UOW Dubai study area."""

from diagnosis import predict_records
from schedule_aware_threshold import predict_thresholds
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import patheffects
from matplotlib.lines import Line2D
from PIL import Image
import numpy as np
import pandas as pd
import streamlit as st

from diagnosis import DEFAULT_MODEL_PATH, load_model
from evaluate_methods import evaluate_methods
import ui_theme
from ui_theme import show_table


st.set_page_config(page_title="Urban Irrigation Twin", page_icon="💧", layout="wide")

ui_theme.inject_css()
T = ui_theme.tokens()  # colours for the diagrams, matching the selected theme


@st.cache_data(show_spinner=False)
def cached_method_comparison(
    dataset_path: str,
    model_path: str,
    dataset_modified: float,
    model_modified: float,
) -> tuple[pd.DataFrame, dict]:
    """Cache shared holdout predictions and metrics for the dashboard session."""
    data = pd.read_csv(dataset_path)
    model_bundle = load_model(model_path)
    return evaluate_methods(data, model_bundle)


def draw_context_map(reading: pd.Series, highlighted_zone: str | None = None) -> plt.Figure:
    """Show the supplied Dubai map as context with a clearly hypothetical network overlay."""
    image_path = Path(__file__).parent / "assets" / "uow_dubai_context.png"
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    fig, ax = plt.subplots(figsize=(12, 7.4))
    fig.patch.set_facecolor(T["plot_face"])
    ax.imshow(image, extent=(0, width, height, 0), zorder=0)

    # These normalized points are a visual illustration only, not surveyed pipe coordinates.
    points = {
        "Source": (.31, .57), "Manifold": (.43, .57),
        "Zone A": (.55, .34), "Zone B": (.64, .57), "Zone C": (.55, .78),
    }
    coords = {name: (x * width, y * height) for name, (x, y) in points.items()}
    links = [("Source", "Manifold"), ("Manifold", "Zone A"), ("Manifold", "Zone B"), ("Manifold", "Zone C")]
    for start, end in links:
        x1, y1 = coords[start]
        x2, y2 = coords[end]
        ax.plot([x1, x2], [y1, y2], color="#071525", linewidth=9, alpha=.86, solid_capstyle="round", zorder=2)
        ax.plot([x1, x2], [y1, y2], color=T["chart_high"], linewidth=4.2, alpha=.98, solid_capstyle="round", zorder=3)

    def add_node(name: str, color: str, marker: str = "o", size: int = 250) -> None:
        x, y = coords[name]
        ax.scatter([x], [y], s=size + 115, marker=marker, color="#081321", edgecolor="white", linewidth=2, zorder=4)
        ax.scatter([x], [y], s=size, marker=marker, color=color, edgecolor="white", linewidth=1.5, zorder=5)

    add_node("Source", T["source"], marker="s", size=210)
    add_node("Manifold", T["node"], size=260)
    for zone in ("Zone A", "Zone B", "Zone C"):
        add_node(zone, T["fault"] if zone == highlighted_zone else T["zone"], size=270)

    text_effect = [patheffects.withStroke(linewidth=3.2, foreground="#071321", alpha=.95)]
    labels = {
        "Source": ("Synthetic source", -14, 34, "right"),
        "Manifold": ("Distribution manifold", 0, 37, "center"),
        "Zone A": ("Zone A", 0, -32, "center"),
        "Zone B": ("Zone B", 0, -32, "center"),
        "Zone C": ("Zone C", 0, 34, "center"),
    }
    for name, (label, dx, dy, align) in labels.items():
        x, y = coords[name]
        ax.annotate(label, (x, y), xytext=(dx, dy), textcoords="offset points", ha=align, va="center",
                    color="white", fontsize=10.5, weight="bold", zorder=7, path_effects=text_effect,
                    bbox=dict(boxstyle="round,pad=.3", facecolor="#101c2b", edgecolor="#d7e4f4", alpha=.94))

    for zone in ("Zone A", "Zone B", "Zone C"):
        key = zone.replace(" ", "")
        flow = float(reading[f"Flow_{key}_L_min"])
        pressure = float(reading[f"Pressure_{key}_kPa"])
        x, y = coords[zone]
        offset = (43, -5) if zone == "Zone A" else ((38, 2) if zone == "Zone B" else (38, 8))
        label = f"{flow:.1f} L/min  ·  {pressure:.1f} kPa"
        ax.annotate(label, (x, y), xytext=offset, textcoords="offset points", ha="left", va="center",
                    color="white", fontsize=8.1, weight="bold", zorder=7, path_effects=text_effect,
                    bbox=dict(boxstyle="round,pad=.32", facecolor="#101c2b", edgecolor="#d7e4f4", alpha=.94))

    ax.text(.018 * width, .035 * height, "SIMULATED NETWORK · NOT REAL CAMPUS PIPES", color="white", fontsize=10,
            weight="bold", va="top", zorder=8,
            bbox=dict(boxstyle="round,pad=.62", facecolor="#101c2b", edgecolor="white", alpha=.94))
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")
    fig.tight_layout(pad=0)
    return fig


def draw_confusion_matrix(predictions: pd.DataFrame, method_column: str, title: str) -> plt.Figure:
    """Render an actual-versus-predicted class heatmap for one method."""
    labels = ["normal", "leak", "clog"]
    predicted_labels = labels + (["unknown_fault"] if (predictions[method_column] == "unknown_fault").any() else [])
    matrix = pd.crosstab(predictions["Condition"], predictions[method_column]).reindex(
        index=labels, columns=predicted_labels, fill_value=0
    )
    cmap = LinearSegmentedColormap.from_list("diagnosis", [T["chart_low"], T["chart_high"]])
    fig, ax = plt.subplots(figsize=(5.3, 3.7))
    fig.patch.set_facecolor(T["plot_face"])
    ax.set_facecolor(T["plot_face"])
    ax.imshow(matrix.to_numpy(), cmap=cmap, vmin=0, vmax=max(1, int(matrix.to_numpy().max())))
    shown_predictions = ["Other / unknown" if label == "unknown_fault" else label.title() for label in predicted_labels]
    ax.set_xticks(range(len(predicted_labels)), shown_predictions)
    ax.set_yticks(range(len(labels)), [label.title() for label in labels])
    ax.set_xlabel("Predicted condition", color=T["plot_muted"], labelpad=8)
    ax.set_ylabel("Actual condition", color=T["plot_muted"], labelpad=8)
    ax.set_title(title, color=T["plot_text"], fontsize=12, weight="bold", loc="left", pad=12)
    ax.tick_params(colors=T["plot_muted"], length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    for row in range(len(labels)):
        for col in range(len(predicted_labels)):
            value = int(matrix.iloc[row, col])
            text_color = T["plot_face"] if value > matrix.to_numpy().max() * .55 else T["plot_text"]
            ax.text(col, row, str(value), ha="center", va="center", color=text_color, fontsize=11, weight="bold")
    fig.tight_layout(pad=1.25)
    return fig


def draw_comparison_chart(metrics: dict) -> plt.Figure:
    """Compare the main performance and risk measures as paired bars."""
    rf, threshold = metrics["random_forest"], metrics["schedule_aware_threshold"]
    labels = ["Accuracy", "Macro F1", "Location", "Missed faults", "False warnings"]
    rf_values = [rf["accuracy"], rf["macro_f1"], rf["fault_location_accuracy"], rf["missed_fault_rate"], rf["false_alert_rate"]]
    threshold_values = [threshold["accuracy"], threshold["macro_f1"], threshold["fault_location_accuracy"], threshold["missed_fault_rate"], threshold["false_alert_rate"]]
    positions = list(range(len(labels)))
    width = .34
    fig, ax = plt.subplots(figsize=(10.2, 4.1))
    fig.patch.set_facecolor(T["plot_face"])
    ax.set_facecolor(T["plot_face"])
    ax.bar([p - width / 2 for p in positions], rf_values, width, color=T["chart_high"], label="Random Forest", zorder=3)
    ax.bar([p + width / 2 for p in positions], threshold_values, width, color=T["chart_cyan"], label="Schedule-aware threshold", zorder=3)
    ax.set_ylim(0, 1.12)
    ax.set_yticks([0, .25, .5, .75, 1], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_xticks(positions, labels)
    ax.set_title("Diagnosis quality and alert risk", color=T["plot_text"], fontsize=12, weight="bold", loc="left", pad=12)
    ax.grid(axis="y", color=T["grid"], linewidth=.8, zorder=0)
    ax.tick_params(colors=T["plot_muted"], length=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(T["grid"])
    legend = ax.legend(frameon=False, ncol=2, loc="upper right")
    for label in legend.get_texts():
        label.set_color(T["plot_muted"])
    for x, value in zip([p - width / 2 for p in positions], rf_values):
        ax.text(x, value + .025, f"{value:.0%}", ha="center", va="bottom", fontsize=8, color=T["plot_text"])
    for x, value in zip([p + width / 2 for p in positions], threshold_values):
        ax.text(x, value + .025, f"{value:.0%}", ha="center", va="bottom", fontsize=8, color=T["plot_text"])
    fig.tight_layout(pad=1.25)
    return fig


def draw_clog_severity_chart(metrics: dict) -> plt.Figure:
    """Show how clog recall changes from mild to severe obstruction."""
    rf = metrics["random_forest"]["clog_recall_by_severity"]
    threshold = metrics["schedule_aware_threshold"]["clog_recall_by_severity"]
    labels = ["Mild", "Moderate", "Severe"]
    rf_values = [rf[key.lower()] for key in labels]
    threshold_values = [threshold[key.lower()] for key in labels]
    positions = list(range(len(labels)))
    width = .32
    fig, ax = plt.subplots(figsize=(6.3, 3.8))
    fig.patch.set_facecolor(T["plot_face"])
    ax.set_facecolor(T["plot_face"])
    ax.bar([p - width / 2 for p in positions], rf_values, width, color=T["chart_high"], label="Random Forest", zorder=3)
    ax.bar([p + width / 2 for p in positions], threshold_values, width, color=T["chart_cyan"], label="Schedule-aware threshold", zorder=3)
    ax.set_ylim(0, 1.13)
    ax.set_yticks([0, .25, .5, .75, 1], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_xticks(positions, labels)
    ax.set_title("Clog recall by severity", color=T["plot_text"], fontsize=12, weight="bold", loc="left", pad=12)
    ax.grid(axis="y", color=T["grid"], linewidth=.8, zorder=0)
    ax.tick_params(colors=T["plot_muted"], length=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(T["grid"])
    legend = ax.legend(frameon=False, fontsize=8, loc="upper left")
    for label in legend.get_texts():
        label.set_color(T["plot_muted"])
    for x, value in zip([p - width / 2 for p in positions], rf_values):
        ax.text(x, value + .025, f"{value:.0%}", ha="center", va="bottom", fontsize=8, color=T["plot_text"])
    for x, value in zip([p + width / 2 for p in positions], threshold_values):
        ax.text(x, value + .025, f"{value:.0%}", ha="center", va="bottom", fontsize=8, color=T["plot_text"])
    fig.tight_layout(pad=1.25)
    return fig


def draw_class_precision_recall_chart(metrics: dict) -> plt.Figure:
    """Compare Random Forest precision and recall with the threshold baseline by class."""
    rf = metrics["random_forest"]["per_class"]
    threshold = metrics["schedule_aware_threshold"]["per_class"]
    classes = ["normal", "leak", "clog"]
    labels = ["Normal", "Leak", "Clog"]
    series = [
        ("RF precision", [rf[name]["precision"] for name in classes], T["chart_high"]),
        ("RF recall", [rf[name]["recall"] for name in classes], T["chart_cyan"]),
        ("Threshold precision", [threshold[name]["precision"] for name in classes], T["pipe"]),
        ("Threshold recall", [threshold[name]["recall"] for name in classes], T["source"]),
    ]
    positions = np.arange(len(classes))
    width = .19
    fig, ax = plt.subplots(figsize=(9.2, 3.8))
    fig.patch.set_facecolor(T["plot_face"])
    ax.set_facecolor(T["plot_face"])
    for index, (label, values, color) in enumerate(series):
        offset = (index - 1.5) * width
        bars = ax.bar(positions + offset, values, width, color=color, label=label, zorder=3)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + .025, f"{value:.0%}",
                    ha="center", va="bottom", fontsize=7, color=T["plot_text"])
    ax.set_ylim(0, 1.15)
    ax.set_yticks([0, .25, .5, .75, 1], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_xticks(positions, labels)
    ax.set_title("Precision and recall by condition", color=T["plot_text"], fontsize=12, weight="bold", loc="left", pad=12)
    ax.grid(axis="y", color=T["grid"], linewidth=.8, zorder=0)
    ax.tick_params(colors=T["plot_muted"], length=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(T["grid"])
    legend = ax.legend(frameon=False, ncol=2, loc="upper right", fontsize=8)
    for item in legend.get_texts():
        item.set_color(T["plot_muted"])
    fig.tight_layout(pad=1.25)
    return fig


def draw_processing_time_chart(metrics: dict) -> plt.Figure:
    """Show backend prediction time per test record for both methods."""
    rf_time = metrics["random_forest"]["processing_ms_per_record"]
    threshold_time = metrics["schedule_aware_threshold"]["processing_ms_per_record"]
    values = [rf_time, threshold_time]
    labels = ["Random Forest", "Schedule-aware\nthreshold"]
    fig, ax = plt.subplots(figsize=(5.2, 3.3))
    fig.patch.set_facecolor(T["plot_face"])
    ax.set_facecolor(T["plot_face"])
    bars = ax.bar(labels, values, color=[T["chart_high"], T["chart_cyan"]], width=.5, zorder=3)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + max(values + [1]) * .035,
                f"{value:.3f} ms", ha="center", va="bottom", fontsize=9, color=T["plot_text"])
    ax.set_ylim(0, max(values + [1]) * 1.22)
    ax.set_ylabel("Milliseconds per record", color=T["plot_muted"], fontsize=8)
    ax.set_title("Backend prediction time", color=T["plot_text"], fontsize=12, weight="bold", loc="left", pad=12)
    ax.grid(axis="y", color=T["grid"], linewidth=.8, zorder=0)
    ax.tick_params(colors=T["plot_muted"], length=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(T["grid"])
    fig.tight_layout(pad=1.25)
    return fig


def draw_sensor_deviations(
    observed: pd.Series,
    expected: pd.Series,
    model_location: str,
    threshold_location: str,
) -> plt.Figure:
    """Plot observed-minus-normal pressure and flow by zone for one diagnosis result."""
    zones = ["Zone A", "Zone B", "Zone C"]
    zone_keys = {zone: zone.replace(" ", "") for zone in zones}
    flow_deltas = [
        float(observed[f"Flow_{zone_keys[zone]}_L_min"] - expected[f"Flow_{zone_keys[zone]}_L_min"])
        for zone in zones
    ]
    pressure_deltas = [
        float(observed[f"Pressure_{zone_keys[zone]}_kPa"] - expected[f"Pressure_{zone_keys[zone]}_kPa"])
        for zone in zones
    ]

    # Make the ML diagnosis the primary visual signal; show the baseline as a discreet marker.
    colors = [T["chart_high"] if zone == model_location else T["pipe"] for zone in zones]
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8))
    fig.patch.set_facecolor(T["plot_face"])
    categories = [
        (axes[0], flow_deltas, "Flow change by zone", "Change from expected flow (L/min)"),
        (axes[1], pressure_deltas, "Pressure change by zone", "Change from expected pressure (kPa)"),
    ]
    for ax, values, title, xlabel in categories:
        ax.set_facecolor(T["plot_face"])
        positions = [2, 1, 0]
        bars = ax.barh(positions, values, color=colors, height=.5, zorder=3)
        ax.axvline(0, color=T["plot_muted"], linewidth=1, alpha=.8, zorder=2)
        if threshold_location in zones:
            threshold_y = positions[zones.index(threshold_location)]
            ax.scatter([0], [threshold_y], marker="D", s=48, color=T["chart_cyan"],
                       edgecolor=T["plot_face"], linewidth=1.1, zorder=5)
        largest = max([abs(value) for value in values] + [.1])
        limit = largest * 1.42
        ax.set_xlim(-limit, limit)
        ax.set_yticks(positions, zones)
        ax.set_xlabel(xlabel, color=T["plot_muted"], fontsize=8)
        ax.set_title(title, color=T["plot_text"], fontsize=11, weight="bold", loc="left", pad=10)
        ax.grid(axis="x", color=T["grid"], linewidth=.8, zorder=0)
        ax.tick_params(colors=T["plot_muted"], length=0, labelsize=9)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(T["grid"])
        for bar, value in zip(bars, values):
            offset = limit * .025 * (1 if value >= 0 else -1)
            ax.text(
                value + offset,
                bar.get_y() + bar.get_height() / 2,
                f"{value:+.2f}",
                ha="left" if value >= 0 else "right",
                va="center",
                fontsize=8,
                color=T["plot_text"],
            )

    handles = [
        Patch(facecolor=T["chart_high"], label="Random Forest prediction"),
        Patch(facecolor=T["pipe"], label="Other zones"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor=T["chart_cyan"],
               markeredgecolor=T["plot_face"], markersize=7, label="Threshold prediction"),
    ]
    legend = fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=8)
    for label in legend.get_texts():
        label.set_color(T["plot_muted"])
    fig.tight_layout(rect=(0, .1, 1, 1), pad=1.25)
    return fig


view = ui_theme.sidebar_nav(default="Study area")
ui_theme.top_bar(page=view)

page_slug = view.lower().replace(" ", "-")
with st.container(key=f"page-content-{page_slug}"):
    st.markdown('<div class="workspace-eyebrow">URBAN WATER · SIMULATION WORKSPACE</div>', unsafe_allow_html=True)
    st.title({"Study area": "Study area", "Pipeline view": "Pipeline overview", "Watering data": "Watering data", "Method comparison": "Method comparison", "Live Diagnosis": "Live diagnosis"}.get(view, "Irrigation fault diagnosis"))
    st.caption("Three-zone irrigation fault-diagnosis prototype • synthetic network and readings")
    st.info("The study area, zones and pipe connections are illustrative. Pipe locations and sensor readings are generated by the simulation, not taken from UOW infrastructure.")

    if view == "Study area":
        data_path = Path(__file__).parent / "outputs" / "labeled_fault_scenarios.csv"
        if not data_path.exists():
            st.error("The labeled scenario CSV is missing. Run generate_labeled_dataset.py to create it.")
        else:
            dataset = pd.read_csv(data_path)
            normal = dataset[dataset["Condition"] == "normal"]
            map_c1, map_c2 = st.columns(2)
            schedule = map_c1.selectbox("Baseline watering schedule", sorted(normal["Schedule"].unique()), key="map_schedule")
            hours = sorted(normal.loc[normal["Schedule"] == schedule, "Hour"].unique())
            hour = map_c2.selectbox("Hour", hours, format_func=lambda value: f"Hour {value}", key="map_hour")
            baseline = normal.loc[(normal["Schedule"] == schedule) & (normal["Hour"] == hour)].iloc[0]
            st.pyplot(draw_context_map(baseline), use_container_width=True)
            st.caption("The supplied map is geographic context only. The overlaid source, manifold, zones, pipe connections and displayed readings are simulated, illustrative and not surveyed or to scale.")

    elif view == "Pipeline view":
        data_path = Path(__file__).parent / "outputs" / "labeled_fault_scenarios.csv"
        if not data_path.exists():
            st.error("The labeled scenario CSV is missing. Run generate_labeled_dataset.py to create it.")
        else:
            dataset = pd.read_csv(data_path)
            controls = st.columns(4)
            schedule = controls[0].selectbox("Schedule", sorted(dataset["Schedule"].unique()), key="pipe_schedule")
            condition = controls[1].selectbox("Condition", ["normal", "leak", "clog"], key="pipe_condition")
            if condition == "normal":
                severity, location = "none", "none"
                controls[2].selectbox("Severity", ["Not applicable"], disabled=True, key="pipe_severity_normal")
                controls[3].selectbox("Fault zone", ["No fault"], disabled=True, key="pipe_location_normal")
            else:
                severity = controls[2].selectbox("Severity", ["mild", "moderate", "severe"], key="pipe_severity")
                location = controls[3].selectbox("Fault zone", ["Zone A", "Zone B", "Zone C"], key="pipe_location")
            scenario = dataset.loc[
                (dataset["Schedule"] == schedule)
                & (dataset["Condition"] == condition)
                & (dataset["Severity"] == severity)
                & (dataset["Fault_Location"] == location)
            ]
            hours = sorted(scenario["Hour"].unique())
            hour = st.select_slider("Simulation hour", options=hours, value=hours[0], format_func=lambda value: f"Hour {value}")
            reading = scenario.loc[scenario["Hour"] == hour].iloc[0]
            st.markdown(f"**{schedule.title()} schedule · {condition.title()} · {str(severity).title()} · {location.title()} · Hour {hour}**")
            st.pyplot(draw_context_map(reading, highlighted_zone=location if condition != "normal" else None), use_container_width=True)
            st.caption("Map labels and readings are linked to the selected simulated scenario. The geographic image is context only; pipe geometry and locations are illustrative, not real campus infrastructure.")
    elif view == "Watering data":
        data_path = Path(__file__).parent / "outputs" / "labeled_fault_scenarios.csv"
        st.subheader("Labeled irrigation scenario dataset")
        st.caption("WNTR-generated hydraulic readings across normal operation, leaks, and clogs.")
        if not data_path.exists():
            st.error("The labeled scenario CSV is missing. Run generate_labeled_dataset.py to create it.")
        else:
            dataset = pd.read_csv(data_path)
            f1, f2, f3 = st.columns(3)
            selected_schedule = f1.selectbox("Schedule", ["All", *sorted(dataset["Schedule"].unique())])
            selected_condition = f2.selectbox("Condition", ["All", *sorted(dataset["Condition"].unique())])
            selected_location = f3.selectbox("Fault location", ["All", *sorted(dataset["Fault_Location"].unique())])

            displayed = dataset.copy()
            if selected_schedule != "All":
                displayed = displayed[displayed["Schedule"] == selected_schedule]
            if selected_condition != "All":
                displayed = displayed[displayed["Condition"] == selected_condition]
            if selected_location != "All":
                displayed = displayed[displayed["Fault_Location"] == selected_location]

            c1, c2, c3 = st.columns(3)
            c1.metric("Scenario-hour records", len(displayed))
            c2.metric("Scenario configurations", displayed["Scenario_ID"].nunique())
            c3.metric("Schedules", displayed["Schedule"].nunique())

            show_table(displayed, use_container_width=True, hide_index=True, height=520)
            st.caption("For field definitions, see `DATA_DICTIONARY.md`. Keep rows with the same Scenario_ID together when splitting data for later model evaluation.")
            st.download_button(
                "Download filtered data as CSV",
                data=displayed.to_csv(index=False).encode("utf-8"),
                file_name="labeled_fault_scenarios.csv",
                mime="text/csv",
            )
    elif view == "Method comparison":
        dataset_path = Path(__file__).parent / "outputs" / "labeled_fault_scenarios.csv"
        model_path = Path(DEFAULT_MODEL_PATH)
        st.subheader("Random Forest vs schedule-aware threshold")
        st.caption("Both methods are compared on the same held-out night-schedule records.")
        if not dataset_path.exists() or not model_path.exists():
            st.error("The scenario dataset or saved Random Forest model is missing. Generate the dataset and run train_model.py first.")
        else:
            with st.spinner("Loading model and preparing the held-out comparison…"):
                predictions, metrics = cached_method_comparison(
                    str(dataset_path),
                    str(model_path),
                    dataset_path.stat().st_mtime,
                    model_path.stat().st_mtime,
                )

            st.info(
                f"Test set: {metrics['test_rows']} night-schedule records from "
                f"{metrics['test_scenario_configurations']} scenario configurations. "
                "The Random Forest was trained on morning and afternoon profiles."
            )

            rf = metrics["random_forest"]
            threshold = metrics["schedule_aware_threshold"]
            with st.container(key="results-panel"):
                st.markdown("#### Performance overview")
                st.caption("Random Forest is the primary method; the schedule-aware threshold is the benchmark. All charts use predictions from the same held-out night-schedule records. Lower is better for missed faults and false warnings.")
                st.pyplot(draw_comparison_chart(metrics), use_container_width=True)

                chart_col1, chart_col2 = st.columns([1.2, 1])
                with chart_col1:
                    st.pyplot(draw_clog_severity_chart(metrics), use_container_width=True)
                with chart_col2:
                    st.pyplot(draw_processing_time_chart(metrics), use_container_width=True)

                st.pyplot(draw_class_precision_recall_chart(metrics), use_container_width=True)

                st.markdown("#### Random Forest summary")
                rf_metric1, rf_metric2, rf_metric3 = st.columns(3)
                rf_metric1.metric("Macro F1", f"{rf['macro_f1']:.1%}", help="Unweighted average F1 across normal, leak and clog classes.")
                rf_metric2.metric("Fault-location accuracy", f"{rf['fault_location_accuracy']:.1%}")
                rf_metric3.metric("Missed-fault rate", f"{rf['missed_fault_rate']:.1%}")

                st.markdown("#### Where each method gets the diagnosis right")
                st.caption("Each cell shows the number of records in that actual-versus-predicted class. The diagonal cells are correct predictions.")
                matrix_col1, matrix_col2 = st.columns(2)
                with matrix_col1:
                    st.pyplot(draw_confusion_matrix(predictions, "Predicted_Condition", "Random Forest"), use_container_width=True)
                with matrix_col2:
                    st.pyplot(draw_confusion_matrix(predictions, "Threshold_Condition", "Schedule-aware threshold"), use_container_width=True)

            st.markdown("#### Exact evaluation measures")
            metric_rows = [
                ("Condition accuracy", "accuracy", "percent"),
                ("Condition macro F1", "macro_f1", "percent"),
                ("Fault-location accuracy", "fault_location_accuracy", "percent"),
                ("Missed-fault rate", "missed_fault_rate", "percent"),
                ("False-alert rate", "false_alert_rate", "percent"),
                ("Mean processing time per record", "processing_ms_per_record", "milliseconds"),
            ]
            table_rows = []
            for label, key, unit in metric_rows:
                if unit == "percent":
                    rf_value, threshold_value = f"{rf[key] * 100:.1f}%", f"{threshold[key] * 100:.1f}%"
                else:
                    rf_value, threshold_value = f"{rf[key]:.3f} ms", f"{threshold[key]:.3f} ms"
                table_rows.append({"Measure": label, "Random Forest": rf_value, "Schedule-aware threshold": threshold_value})
            show_table(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

            class_rows = []
            for method_name, result in (("Random Forest", rf), ("Schedule-aware threshold", threshold)):
                for condition, scores in result["per_class"].items():
                    class_rows.append(
                        {
                            "Method": method_name,
                            "Condition": condition,
                            "Precision": f"{scores['precision'] * 100:.1f}%",
                            "Recall": f"{scores['recall'] * 100:.1f}%",
                        }
                    )
            st.markdown("**Precision and recall by condition**")
            show_table(pd.DataFrame(class_rows), use_container_width=True, hide_index=True)

            st.markdown("**Held-out scenario predictions**")
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            condition_filter = filter_col1.selectbox("Actual condition", ["All", *sorted(predictions["Condition"].unique())])
            severity_filter = filter_col2.selectbox("Fault severity", ["All", *sorted(predictions["Severity"].unique())])
            location_filter = filter_col3.selectbox("Actual location", ["All", *sorted(predictions["Fault_Location"].unique())])
            displayed = predictions.copy()
            if condition_filter != "All":
                displayed = displayed[displayed["Condition"] == condition_filter]
            if severity_filter != "All":
                displayed = displayed[displayed["Severity"] == severity_filter]
            if location_filter != "All":
                displayed = displayed[displayed["Fault_Location"] == location_filter]
            prediction_columns = [
                "Scenario_ID", "Hour", "Condition", "Severity", "Fault_Location",
                "Predicted_Condition", "Predicted_Fault_Location", "Threshold_Alert",
                "Threshold_Condition", "Threshold_Location",
            ]
            show_table(displayed[prediction_columns], use_container_width=True, hide_index=True, height=420)
            st.caption(metrics["response_time_note"])

    elif view == "Live Diagnosis":

        st.subheader("Live Fault Diagnosis")

        dataset_path = Path(__file__).parent / "outputs" / "labeled_fault_scenarios.csv"

        if not dataset_path.exists():

            st.error("Dataset not found.")

        else:

            data = pd.read_csv(dataset_path)

            selected_scenario = st.selectbox(
                "Select Scenario",
                sorted(data["Scenario_ID"].unique())
            )

            scenario_data = data[
                data["Scenario_ID"] == selected_scenario
            ]

            selected_hour = st.selectbox(
                "Simulation hour",
                sorted(scenario_data["Hour"].unique()),
                format_func=lambda hour: f"Hour {hour}",
            )
            selected_reading = scenario_data[scenario_data["Hour"] == selected_hour].copy()

            st.markdown("### Sensor Readings")

            sensor_cols = [
                "Pressure_ZoneA_kPa",
                "Pressure_ZoneB_kPa",
                "Pressure_ZoneC_kPa",
                "Flow_ZoneA_L_min",
                "Flow_ZoneB_L_min",
                "Flow_ZoneC_L_min",
            ]

            show_table(
                selected_reading[sensor_cols],
                use_container_width=True
            )

            if st.button("Run Diagnosis"):

                ml_result = predict_records(
                    selected_reading
                )

                threshold_result = predict_thresholds(
                    selected_reading,
                    baseline_data=data
                )

                ml_condition = ml_result[
                    "Predicted_Condition"
                ].iloc[0]

                ml_location = ml_result[
                    "Predicted_Fault_Location"
                ].iloc[0]

                threshold_condition = threshold_result[
                    "Threshold_Condition"
                ].iloc[0]

                threshold_location = threshold_result[
                    "Threshold_Location"
                ].iloc[0]

                fault_alert = ml_condition != "normal" or bool(threshold_result["Threshold_Alert"].iloc[0])
                notification_title = "Simulated fault alert" if fault_alert else "Normal simulation result"
                notification_detail = (
                    f"{selected_scenario}, hour {selected_hour}. Random Forest: {ml_condition} at {ml_location}; "
                    f"threshold: {threshold_condition} at {threshold_location}."
                )
                ui_theme.add_notification(
                    notification_title,
                    notification_detail,
                    kind="alert" if fault_alert else "info",
                )

                with st.container(key="diagnosis-results"):
                    st.markdown("### Diagnosis results")
                    st.caption(f"Simulated result · {selected_scenario} · hour {selected_hour}")
                    reading = selected_reading.iloc[0]
                    baseline_match = data.loc[
                        (data["Condition"] == "normal")
                        & (data["Schedule"] == reading["Schedule"])
                        & (data["Hour"] == reading["Hour"])
                    ]
                    if not baseline_match.empty:
                        st.markdown("#### Sensor changes from the matching normal baseline")
                        st.caption("Bars show observed minus expected pressure and flow for this schedule and hour. Colors identify each method’s suspected zone.")
                        st.pyplot(
                            draw_sensor_deviations(
                                reading,
                                baseline_match.iloc[0],
                                ml_location,
                                threshold_location,
                            ),
                            use_container_width=True,
                        )

                    col1, col2 = st.columns([1.15, .85])

                    with col1:
                        with st.container(key="rf-diagnosis-card"):
                            st.markdown("**Random Forest classifier · primary diagnosis**")
                            st.metric("Predicted condition", ml_condition.title())
                            st.metric("Suspected location", ml_location)

                    with col2:
                        with st.container(key="threshold-diagnosis-card"):
                            st.markdown("**Schedule-aware threshold · baseline**")
                            st.metric("Predicted condition", threshold_condition.replace("_", " ").title())
                            st.metric("Suspected location", threshold_location)

                    comparison = pd.DataFrame(
                        {
                            "Method": ["Random Forest", "Schedule-aware threshold"],
                            "Condition": [ml_condition, threshold_condition],
                            "Location": [ml_location, threshold_location],
                        }
                    )
                    show_table(comparison, hide_index=True, use_container_width=True)
