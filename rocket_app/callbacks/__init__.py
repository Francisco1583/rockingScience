from .analytics_editor import register as register_analytics_editor
from .analytics_overview import register as register_analytics_overview
from .launch_charts import register as register_launch_charts
from .predictive import register as register_predictive
from .rocket_3d import register as register_rocket_3d
from .telemetry import register as register_telemetry


def register_callbacks(app):
    register_telemetry(app)
    register_launch_charts(app)
    register_rocket_3d(app)
    register_analytics_overview(app)
    register_analytics_editor(app)
    register_predictive(app)


__all__ = ["register_callbacks"]
