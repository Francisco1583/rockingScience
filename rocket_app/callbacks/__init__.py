from .analytics import register as register_analytics
from .radar import register as register_radar
from .telemetry import register as register_telemetry


def register_callbacks(app):
    register_telemetry(app)
    register_radar(app)
    register_analytics(app)


__all__ = ["register_callbacks"]
