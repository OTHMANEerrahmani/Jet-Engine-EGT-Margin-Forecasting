import reflex as rx
from app.states.forecast_state import ForecastState


def status_display_component() -> rx.Component:
    return rx.el.div(
        rx.cond(
            ForecastState.is_processing,
            rx.el.div(
                rx.spinner(
                    size="3", class_name="text-indigo-600"
                ),
                rx.el.p(
                    ForecastState.status_message,
                    class_name="ml-3 text-indigo-700 font-medium",
                ),
                class_name="flex items-center justify-center p-4 bg-indigo-50 rounded-lg text-sm mb-4",
            ),
            rx.el.div(
                rx.cond(
                    ForecastState.status_message,
                    rx.el.p(
                        ForecastState.status_message,
                        class_name=rx.cond(
                            ForecastState.error_message.is_truthy(),
                            "text-red-700 font-medium p-3 bg-red-50 rounded-lg text-sm",
                            "text-green-700 font-medium p-3 bg-green-50 rounded-lg text-sm",
                        ),
                    ),
                    rx.el.div(),
                ),
                class_name="mb-4",
            ),
        ),
        rx.cond(
            ForecastState.error_message,
            rx.el.div(
                rx.icon(
                    tag="flag_triangle_right",
                    class_name="w-5 h-5 text-red-500 mr-2",
                ),
                rx.el.p(
                    ForecastState.error_message,
                    class_name="text-red-700 font-medium",
                ),
                class_name="flex items-center p-4 bg-red-100 border border-red-300 rounded-lg text-sm mt-2",
            ),
            rx.el.div(),
        ),
        class_name="w-full max-w-2xl mx-auto text-center",
    )