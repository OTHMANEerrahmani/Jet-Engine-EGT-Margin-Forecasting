import reflex as rx
from app.states.forecast_state import ForecastState


def forecast_chart_component() -> rx.Component:
    return rx.el.div(
        rx.cond(
            ForecastState.show_chart
            & (
                ForecastState.forecast_chart_data.length()
                > 0
            ),
            rx.el.div(
                rx.el.h2(
                    "Prévision de la Marge EGT",
                    class_name="text-2xl font-semibold text-gray-800 mb-6 text-center",
                ),
                rx.recharts.line_chart(
                    rx.recharts.cartesian_grid(
                        stroke_dasharray="3 3",
                        stroke_opacity=0.3,
                    ),
                    rx.recharts.x_axis(
                        data_key="date",
                        name="Date",
                        angle=-30,
                        text_anchor="end",
                        height=70,
                    ),
                    rx.recharts.y_axis(
                        name="Marge EGT (°C)"
                    ),
                    rx.recharts.tooltip(),
                    rx.recharts.legend(
                        payload=[
                            {
                                "value": "Prévision EGT",
                                "type": "line",
                                "color": "#4f46e5",
                            }
                        ]
                    ),
                    rx.recharts.line(
                        data_key="EGT Margin Forecast (XGBoost)",
                        stroke="#4f46e5",
                        dot=False,
                        type="monotone",
                        name="Prévision EGT",
                    ),
                    rx.recharts.reference_area(
                        y1=0,
                        y2=20,
                        label=rx.recharts.label(
                            value="Zone à Risque (< 20°C)",
                            position="insideTopLeft",
                            fill="#ef4444",
                            font_size="10px",
                        ),
                        fill="#fee2e2",
                        stroke_opacity=0.3,
                        if_overflow="extendDomain",
                    ),
                    data=ForecastState.forecast_chart_data,
                    height=450,
                    margin={
                        "top": 5,
                        "right": 30,
                        "left": 20,
                        "bottom": 60,
                    },
                    class_name="bg-white p-6 rounded-xl shadow-lg",
                ),
                rx.el.button(
                    rx.icon(
                        tag="download", class_name="mr-2"
                    ),
                    "Télécharger les prévisions en Excel",
                    on_click=ForecastState.download_excel,
                    is_disabled=~ForecastState.can_download,
                    class_name="mt-8 px-6 py-3 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mx-auto",
                ),
                class_name="w-full max-w-4xl mx-auto p-4",
            ),
            rx.el.div(),
        ),
        class_name="w-full",
    )