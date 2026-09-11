"""AeroCrop.ai — Controller Layer"""
from .auth_controller import router as auth_router
from .history_controller import router as history_router
from .plot_controller import router as plot_router
from .predict_controller import router as predict_router
from .weather_controller import router as weather_router
from .mandi_controller import router as mandi_router

__all__ = [
    "auth_router",
    "history_router",
    "plot_router",
    "predict_router",
    "weather_router",
    "mandi_router",
]
