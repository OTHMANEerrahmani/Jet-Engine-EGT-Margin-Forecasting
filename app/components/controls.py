import reflex as rx
from app.states.forecast_state import ForecastState
from app.components.file_uploader import (
    file_uploader_component,
)


def control_panel_component() -> rx.Component:
    return rx.el.div(
        file_uploader_component(),
        rx.el.button(
            "Lancer la prévision",
            on_click=ForecastState.run_forecast,
            is_disabled=ForecastState.is_processing
            | (ForecastState.uploaded_file_name == ""),
            class_name="mt-6 px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed",
        ),
        class_name="p-6 bg-white rounded-xl shadow-lg w-full max-w-2xl mx-auto mb-8",
    )