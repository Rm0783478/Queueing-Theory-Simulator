"""
All plotly chart functions.
Each function accepts simulation output dicts and returns a plotly figure.
"""

import plotly.graph.objects as go
import plotly.express as px
import numpy as np 

# Shared color palette
COLOR_SIM  = "#378ADD"   # blue (simulated)
COLOR_THEO = "#D85A30"   # coral (theoretical)
COLOR_FILL = "rgba(55,138,221,0.12)"

# Shared layout defaults
def _base_layout() -> dict:
    return dict(
        height = 320,
        margin = dict(t = 50, b = 50, l = 50, r = 30),
        plot_bgcolor = "white",
        paper_bgcolor = "white",
        font = dict(family = "Arial", size = 12, color = "#1A1A1A"),
        xaxis = dict(showgrid = True, gridcolor = "#F1EFE8"),
        yaxis = dict(showgrid = True, gridcolor = "#F1EFE8"),
    )

# Queue length over time

def queue_length_chart(queue_log: list) -> go.Figure:
    """Generates line chart of queue length over simulated time."""
    if not queue_log:
        return go.Figure()

    times  = [t for t, _ in queue_log]
    lengths = [q for _, q in queue_log]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x = times, y = lengths,
        mode = "lines",
        line = dict(color = COLOR_SIM, width = 1.5),
        fill = "tozeroy",
        fillcolor = COLOR_FILL,
        name = "Queue length",
    ))
    fig.update_layout(
        title = "Queue length over time",
        x_axis_title = "Simulated time",
        y_axis_title = "Customers in queue",
        **_base_layout(),
    )
    return fig

# Wait time histogram

def wait_time_histogram(wait_times: list, theoretical_wq: float = None) -> go.Figure:
    """Histogram of individual customer wait times with optional theoretical mean line."""
    if not wait_times:
        return go.Figure()
    
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x = wait_times,
        nbinsx = 40,
        marker_color = COLOR_SIM,
        opacity = 0.8,
        name = "Observed wait times",
    ))

    if theoretical_wq is not None and theoretical_wq != float("inf"):
        fig.add_vline(
            x = theoretical_wq,
            line_dash = "dash",
            line_color = COLOR_THEO,
            annotation_text = f"Theoretical Wq = {theoretical_wq:.2f}",
            annotation_position = "top right",
        )
    
    sim_mean = float(np.mean(wait_times))
    fig.add_vline(
        x = sim_mean,
        line_dash = "dot",
        line_color = COLOR_SIM,
        annotation_test = f"Simulated mean = {sim_mean:.2f}",
        annotation_position = "top left",
    )

    fig.update_layout(
        title = "Wait Time Distribution",
        x_axis_title = "Wait Time",
        y_axis_title = "Count",
        **_base_layout(),
    )

    return fig

# Sever utilization gauge

def utilization_gauge(rho_sim: float, rho_theo: float = None) -> go.Figure:
    """Generates gauge chart showing server utilization"""
    fig = go.Figure(go.Indicator(
        mode = "gauge + number + delta",
        value = round(rho_sim * 100, 1),
        delta = {
            "reference": round(rho_theo * 100, 1) if rho_theo else None,
            "suffix": "%",
        } if rho_theo else {},
        number = {"suffix": "%"},
        title = {"text": "Server Utilization (ρ)"},
        gauge = {
            "axis": {"range": [0, 100], "ticksuffix": "%"},
            "bar": {"color": COLOR_SIM},
            "steps": [
                {"range": [0, 70], "color": "#EAF3DE"}, # green (healthy)
                {"range": [70, 90], "color": "#FAEEDA"}, # amber (caution)
                {"range": [90, 100], "color": "#FCEBEB"}, # red (overloaded)
            ],
            "threshold": {
                "line": {"color": COLOR_THEO, "width": 2},
                "thickness": 0.75,
                "value": round(rho_theo * 100, 1) if rho_theo else 0, 
            },
        },
    ))
        
    fig.update_layout(height = 280, margin = dict(t = 60, b = 20, l = 30, r = 30))
    return fig

# Sensitivity analysis

def sensitivity_chart(param_name: str, param_values: list, wq_values: list, rho_values: list) -> go.Figure:
    """
    Generates dual-axis chart sweeping a parameter (lambda or k) and showing
    how Wq and rho respond. This is THE chart of interest.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = param_values,
        y = wq_values,
        mode ="lines + markers",
        name = "Mean wait (Wq)",
        line = dict (color = COLOR_SIM, width = 2),
        y_axis = "y1",
    ))

    fig.add_trace(go.Scatter(
        x = param_values,
        y = [r * 100 for r in rho_values],
        mode = "lines + markers",
        name = "Utilization ρ (%)",
        line = dict(color = COLOR_THEO, width = 2, dash = "dash"),
        y_axis = "y2",
    ))

    # Marks the instability boundary at rho = 1
    fig.add_hline(
        y = 100, 
        line_dash = "dot",
        line_color = "#E24B4A",
        annotation_text = "System unstable (ρ = 1)",
        y_ref = "y2",
    )

    fig.update_layout(
        title = f"Sensitivity: Wq and ρ vs. {param_name}",
        x_axis_title = param_name,
        y_axis = dict(title = "Mean Wait Time (Wq)", color = COLOR_SIM),
        y_axis_2 = dict (
            title = "Utilization ρ (%)",
            color = COLOR_THEO,
            overlaying = "y",
            side = "right",
            range = [0, 110],
        ),
        legend = dict(x = 0.01, y = 0.99),
        **_base_layout(),
    )
    
    return fig
