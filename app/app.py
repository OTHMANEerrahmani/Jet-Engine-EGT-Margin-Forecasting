import reflex as rx
from app.states.forecast_state import ForecastState
from app.components.controls import control_panel_component
from app.components.status_display import (
    status_display_component,
)
from app.components.forecast_chart import (
    forecast_chart_component,
)


def index() -> rx.Component:
    return rx.el.div(
        rx.el.header(
            rx.el.h1(
                "Prévision de Marge EGT pour Moteurs à Réaction",
                class_name="text-3xl md:text-4xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-700 py-6",
            ),
            class_name="w-full bg-white shadow-sm mb-8",
        ),
        rx.el.main(
            control_panel_component(),
            status_display_component(),
            forecast_chart_component(),
            class_name="container mx-auto px-4 py-5 flex flex-col items-center",
        ),
        rx.el.footer(
            rx.el.p(
                "Application de prévision EGT - Développée avec Reflex",
                class_name="text-center text-sm text-gray-500 py-4",
            ),
            class_name="w-full bg-gray-50 mt-12",
        ),
        class_name="min-h-screen bg-gray-100 flex flex-col",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    stylesheets=[
        "https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css"
    ],
)
app.add_page(index, title="Prévision EGT")