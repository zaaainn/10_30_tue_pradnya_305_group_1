"""Streamlit prototype views for the synthetic UOW Dubai study area."""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from diagnosis import DEFAULT_MODEL_PATH, load_model
from evaluate_methods import evaluate_methods


st.set_page_config(page_title="Urban Irrigation Twin", page_icon="💧", layout="wide")

NAVY = "#17354a"
BLUE = "#28759c"
PIPE = "#54798e"
GREEN = "#24a47f"
GOLD = "#e2a13a"


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


def render_esri_satellite(api_key: str) -> None:
    """Embed Esri satellite imagery and clearly hypothetical network overlays."""
    key = json.dumps(api_key)
    html = f"""
    <!doctype html><html><head><meta charset="utf-8">
    <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@6.14.0/dist/maplibre-gl.css">
    <style>html,body,#map{{height:100%;width:100%;margin:0;font-family:Arial,sans-serif}}
    .notice{{position:absolute;z-index:2;left:12px;top:12px;max-width:360px;padding:10px 13px;
    background:#fff;border-radius:8px;box-shadow:0 2px 10px #0003;color:#17354a;font-size:13px;line-height:1.4}}
    .map-error{{display:none;position:absolute;z-index:3;right:12px;top:12px;max-width:360px;padding:10px 13px;
    background:#fff3cd;border-radius:8px;color:#604b00;font-size:13px;line-height:1.4}}</style>
    </head><body><div id="map"></div><div class="notice"><b>Satellite context only.</b><br>
    Green and blue lines show a hypothetical simulation network, not real UOW or city pipes.</div>
    <div id="map-error" class="map-error">Esri imagery could not be loaded. Check the ArcGIS access key and its Basemaps permission.</div>
    <script type="importmap">
      {{"imports":{{
        "maplibre-gl":"https://unpkg.com/maplibre-gl@6.14.0/dist/maplibre-gl.mjs",
        "@esri/maplibre-arcgis":"https://unpkg.com/@esri/maplibre-arcgis@1.3.1/dist/esm/maplibre-arcgis.min.js"
      }}}}
    </script>
    <script type="module">
      import * as maplibregl from "maplibre-gl";
      import * as maplibreArcGIS from "@esri/maplibre-arcgis";

      const accessToken = {key};
      const campus = [55.16267, 25.10143];
      const points = {{
        Source: [55.15990, 25.10143],
        Manifold: campus,
        "Zone A": [55.16267, 25.10368],
        "Zone B": [55.16544, 25.10143],
        "Zone C": [55.16267, 25.09918]
      }};
      const map = new maplibregl.Map({{
        container: "map", center: campus, zoom: 15,
        style: {{version: 8, sources: {{}}, layers: [{{id: "background", type: "background", paint: {{"background-color": "#17212b"}}}}]}}
      }});
      map.addControl(new maplibregl.NavigationControl(), "top-right");
      map.addControl(new maplibregl.FullscreenControl(), "top-right");
      map.on("error", () => {{ document.getElementById("map-error").style.display = "block"; }});
      const basemapStyle = maplibreArcGIS.BasemapStyle.applyStyle(map, {{style: "arcgis/imagery", token: accessToken}});
      basemapStyle.on("BasemapStyleError", () => {{ document.getElementById("map-error").style.display = "block"; }});

      function makeCircle(center, radiusMeters, steps = 96) {{
        const [longitude, latitude] = center;
        const earthRadius = 6378137;
        const lat1 = latitude * Math.PI / 180;
        const lon1 = longitude * Math.PI / 180;
        const angularDistance = radiusMeters / earthRadius;
        const coordinates = [];
        for (let i = 0; i <= steps; i++) {{
          const bearing = 2 * Math.PI * i / steps;
          const lat2 = Math.asin(Math.sin(lat1) * Math.cos(angularDistance) + Math.cos(lat1) * Math.sin(angularDistance) * Math.cos(bearing));
          const lon2 = lon1 + Math.atan2(Math.sin(bearing) * Math.sin(angularDistance) * Math.cos(lat1), Math.cos(angularDistance) - Math.sin(lat1) * Math.sin(lat2));
          coordinates.push([lon2 * 180 / Math.PI, lat2 * 180 / Math.PI]);
        }}
        return {{type: "Feature", properties: {{}}, geometry: {{type: "Polygon", coordinates: [coordinates]}}}};
      }}

      function addSimulationOverlays() {{
        map.addSource("study-radius", {{type: "geojson", data: makeCircle(campus, 3000)}});
        map.addLayer({{id: "study-radius-fill", type: "fill", source: "study-radius", paint: {{"fill-color": "#39a7e0", "fill-opacity": 0.06}}}});
        map.addLayer({{id: "study-radius-outline", type: "line", source: "study-radius", paint: {{"line-color": "#39a7e0", "line-width": 2, "line-opacity": 0.9}}}});

        const features = [
          {{type: "Feature", properties: {{kind: "feed"}}, geometry: {{type: "LineString", coordinates: [points.Source, points.Manifold]}}}},
          ...["Zone A", "Zone B", "Zone C"].map(name => ({{type: "Feature", properties: {{kind: "branch"}}, geometry: {{type: "LineString", coordinates: [points.Manifold, points[name]]}}}})),
          ...Object.entries(points).map(([name, coordinates]) => ({{type: "Feature", properties: {{name, kind: name === "Source" ? "source" : name === "Manifold" ? "manifold" : "zone"}}, geometry: {{type: "Point", coordinates}}}})),
          {{type: "Feature", properties: {{name: "UOW reference"}}, geometry: {{type: "Point", coordinates: campus}}}}
        ];
        map.addSource("hypothetical-network", {{type: "geojson", data: {{type: "FeatureCollection", features}}}});
        map.addLayer({{id: "network-lines", type: "line", source: "hypothetical-network", filter: ["==", ["geometry-type"], "LineString"], paint: {{"line-color": ["match", ["get", "kind"], "feed", "#28a6df", "#20c997"], "line-width": 5, "line-opacity": 0.95}}}});
        map.addLayer({{id: "network-points", type: "circle", source: "hypothetical-network", filter: ["==", ["geometry-type"], "Point"], paint: {{"circle-radius": ["match", ["get", "kind"], "manifold", 8, "source", 7, 7], "circle-color": ["match", ["get", "kind"], "source", "#e2a13a", "manifold", "#17354a", "#20c997"], "circle-stroke-color": "#ffffff", "circle-stroke-width": 2}}}});
        map.addLayer({{id: "network-labels", type: "symbol", source: "hypothetical-network", filter: ["==", ["geometry-type"], "Point"], layout: {{"text-field": ["get", "name"], "text-size": 13, "text-offset": [0, 1.4], "text-anchor": "top", "text-allow-overlap": true}}, paint: {{"text-color": "#ffffff", "text-halo-color": "#17354a", "text-halo-width": 1.5}}}});
      }}
      basemapStyle.on("BasemapStyleLoad", addSimulationOverlays);
    </script>
    </body></html>
    """
    components.html(html, height=650, scrolling=False)


st.title("Schedule-Aware Urban Irrigation Prototype")
st.caption("Three-zone irrigation fault-diagnosis prototype • synthetic network and readings")
st.info("Esri satellite imagery, when enabled, is geographic context only. Pipe locations and sensor readings are generated by the simulation, not taken from UOW infrastructure.")

view = st.radio("Choose a view", ["Study area", "Pipeline view", "Watering data", "Method comparison"], horizontal=True)

if view == "Study area":
    arcgis_api_key = os.environ.get("ARCGIS_API_KEY", "").strip()
    try:
        arcgis_api_key = arcgis_api_key or st.secrets.get("ARCGIS_API_KEY", "")
    except (KeyError, FileNotFoundError):
        pass
    if arcgis_api_key:
        render_esri_satellite(arcgis_api_key)
        st.caption("Satellite imagery is supplied by Esri ArcGIS. The 3 km circle and pipeline overlay are for study context; simulated pipe positions are illustrative and do not represent real infrastructure.")
    else:
        st.info("To show Esri satellite imagery, configure ARCGIS_API_KEY in .streamlit/secrets.toml. The offline illustration is shown until then.")
        st.pyplot(draw_study_area(), use_container_width=True)
        st.caption("The offline background shapes and network positions are illustrative and are not to scale.")
elif view == "Pipeline view":
    selected = st.selectbox("Highlight a hypothetical fault location", ["None", "Zone A", "Zone B", "Zone C"])
    fig, ax = plt.subplots(figsize=(11, 4.8))
    fig.patch.set_facecolor("#f7fafb")
    draw_network(ax, show_measurements=True, fault_zone=None if selected == "None" else selected)
    ax.set_title("Simulated pipeline topology and normal baseline readings", color=NAVY, fontsize=14, weight="bold", pad=16)
    st.pyplot(fig, use_container_width=True)
    st.caption("Red highlight is a visual example only. Pipe connections and measurements are simulated; diagnosis predictions are shown in the Method comparison view.")
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

        st.dataframe(displayed, use_container_width=True, hide_index=True, height=520)
        st.caption("For field definitions, see `DATA_DICTIONARY.md`. Keep rows with the same Scenario_ID together when splitting data for later model evaluation.")
        st.download_button(
            "Download filtered data as CSV",
            data=displayed.to_csv(index=False).encode("utf-8"),
            file_name="labeled_fault_scenarios.csv",
            mime="text/csv",
        )
else:
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
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        clog_rows = [
            {
                "Clog severity (test condition)": severity.title(),
                "Random Forest clog recall": f"{rf['clog_recall_by_severity'][severity] * 100:.1f}%",
                "Threshold clog recall": f"{threshold['clog_recall_by_severity'][severity] * 100:.1f}%",
            }
            for severity in ("mild", "moderate", "severe")
        ]
        st.markdown("**Clog recall by severity**")
        st.dataframe(pd.DataFrame(clog_rows), use_container_width=True, hide_index=True)

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
        st.dataframe(pd.DataFrame(class_rows), use_container_width=True, hide_index=True)

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
        st.dataframe(displayed[prediction_columns], use_container_width=True, hide_index=True, height=420)
        st.caption(metrics["response_time_note"])
