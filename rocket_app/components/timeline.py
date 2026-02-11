from dash import html


def timeline_container():
    return html.Div(id="timeline", className="timeline")


def timeline_items(current_status):
    steps = [
        ("COUNTDOWN", "Countdown"),
        ("ASCENT", "Ascent"),
        ("COAST", "Coast"),
        ("APOGEE", "Apogee"),
        ("DESCENT", "Descent"),
        ("PARACHUTE", "Parachute"),
        ("LANDING", "Landing"),
    ]

    active_key = current_status if current_status in {k for k, _ in steps} else "COUNTDOWN"

    items = []
    for status_key, label in steps:
        class_name = "timeline-item active" if status_key == active_key else "timeline-item"
        items.append(
            html.Div(
                className=class_name,
                children=[
                    html.Div(className="timeline-dot"),
                    html.Div(label, className="timeline-label"),
                ],
            )
        )
    return items
